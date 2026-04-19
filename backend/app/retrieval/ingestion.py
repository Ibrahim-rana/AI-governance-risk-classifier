"""
Document ingestion pipeline — page-aware edition.

ARCHITECTURE CHANGE (v2)
-------------------------
Old pipeline (broken):
    PDF → merge all pages → detect_article_sections → chunk_text
    Problem: chunks inherit only the section START page, not their actual page.

New pipeline (v2):
    PDF → [page 1 text] [page 2 text] … [page N text]
               ↓ per page
    detect_legal_anchors(page_text)
    chunk_text(page_text)           ← chunks stay WITHIN one page
    every chunk.metadata["page_number"] = that page's page number  ← exact

Cross-page chunks are eliminated by design: we chunk WITHIN each page,
so every chunk is always 100% inside one PDF page.

Stores to ChromaDB with metadata:
    - page_number       : int   (1-indexed, matches PDF viewer)
    - page_number_end   : int   (same as page_number; reserved for future cross-page)
    - legal_anchor      : str   (first Article / Recital / Annex on the page)
    - anchor_type       : str   ("article" | "recital" | "annex" | "none")
    - article_or_section: str   (kept for backwards compat with search layer)
    - document          : str
    - source_file       : str
    - chunk_index       : int
    - ingested_at       : str
    - page_exact        : str   ("true") — flags that page number is exact
"""

import os
import re
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings          # noqa: F401 (kept for compat)
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    SPLITTER_AVAILABLE = True
except ImportError:
    SPLITTER_AVAILABLE = False

# PDF extraction — prefer pdfplumber, fall back to PyPDF2
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

from .page_index import detect_legal_anchors, primary_anchor


# ── Global state ─────────────────────────────────────────────────────────────

_chroma_client = None
_collection = None

CHROMA_PERSIST_DIR = os.environ.get(
    "CHROMA_PERSIST_DIR",
    os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db"),
)
COLLECTION_NAME = "regulatory_documents"

# Minimum readable text length per page (shorter = likely scanned image)
MIN_PAGE_TEXT_LEN = 30


# ── ChromaDB helpers ──────────────────────────────────────────────────────────

def get_chroma_client():
    """Get or create ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "chromadb is not installed. Install with: pip install chromadb"
            )
        persist_dir = os.path.abspath(CHROMA_PERSIST_DIR)
        os.makedirs(persist_dir, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
    return _chroma_client


def get_collection():
    """Get or create the regulatory documents collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Regulatory and policy document chunks"},
        )
    return _collection


def reset_collection():
    """Delete and recreate the collection (required after pipeline change)."""
    global _collection
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _collection = None
    return get_collection()


# ── PDF / text extraction ─────────────────────────────────────────────────────

def _extract_pages_pdfplumber(filepath: str) -> List[Dict]:
    """Extract text page-by-page using pdfplumber (preferred, more accurate)."""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({"page_number": i + 1, "text": text})
    return pages


def _extract_pages_pypdf2(filepath: str) -> List[Dict]:
    """Fallback: extract text page-by-page using PyPDF2."""
    reader = PdfReader(filepath)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"page_number": i + 1, "text": text})
    return pages


def extract_text_from_pdf(filepath: str) -> List[Dict]:
    """
    Extract text from a PDF, page by page.
    Returns List[{"page_number": int, "text": str}].
    """
    if PDFPLUMBER_AVAILABLE:
        return _extract_pages_pdfplumber(filepath)
    if PYPDF2_AVAILABLE:
        return _extract_pages_pypdf2(filepath)
    raise ImportError(
        "No PDF library available. Install pdfplumber: pip install pdfplumber"
    )


def extract_text_from_file(filepath: str) -> List[Dict]:
    """Extract text from a file (PDF or plain text)."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return [{"page_number": 1, "text": f.read()}]


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 600, chunk_overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks (within a single page)."""
    if SPLITTER_AVAILABLE:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)
    # Fallback: simple sliding window
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def generate_chunk_id(document: str, chunk_index: int, content: str) -> str:
    """Generate deterministic ID for a chunk."""
    hash_input = f"{document}:{chunk_index}:{content[:100]}"
    return hashlib.md5(hash_input.encode()).hexdigest()


# ── Core ingestion logic ──────────────────────────────────────────────────────

def ingest_file(filepath: str, document_name: Optional[str] = None) -> Dict:
    """
    Ingest a single file into the vector store using page-first chunking.

    Algorithm
    ---------
    1. Extract text page-by-page.
    2. For each readable page:
       a. Detect legal anchors (Article N, Recital N, Annex …).
       b. Split page text into chunks (all chunks stay within the page).
       c. Assign page_number directly from the page — no estimation.
    3. Upsert all chunks to ChromaDB with exact page metadata.
    """
    if document_name is None:
        document_name = os.path.basename(filepath)

    pages_data = extract_text_from_file(filepath)

    if not pages_data or not any(p["text"].strip() for p in pages_data):
        return {
            "filename": document_name,
            "status": "error",
            "message": "Empty file or no extractable text",
            "chunk_count": 0,
        }

    collection = get_collection()
    total_chunks = 0
    skipped_pages = 0

    for page in pages_data:
        page_number = page["page_number"]
        page_text = page["text"]

        # Skip unreadable pages (scanned images, blank pages)
        if len(page_text.strip()) < MIN_PAGE_TEXT_LEN:
            skipped_pages += 1
            continue

        # Detect legal anchors on this page
        anchors = detect_legal_anchors(page_text)
        p_anchor = primary_anchor(anchors)

        legal_anchor_ref = p_anchor["ref"] if p_anchor else "None"
        anchor_type_str = p_anchor["anchor_type"] if p_anchor else "none"

        # For backwards compat: build a human-readable section label
        article_or_section = legal_anchor_ref if legal_anchor_ref != "None" else f"Page {page_number}"

        # Split this page into chunks — all chunks stay within this page
        chunks = chunk_text(page_text)

        for chunk_content in chunks:
            if not chunk_content.strip():
                continue

            chunk_id = generate_chunk_id(document_name, total_chunks, chunk_content)

            collection.upsert(
                ids=[chunk_id],
                documents=[chunk_content],
                metadatas=[{
                    "document": document_name,
                    "source_file": os.path.basename(filepath),
                    # ── Page tracking (exact, from PDF layout) ──
                    "page_number": page_number,
                    "page_number_end": page_number,   # same page always (no cross-page)
                    "page_exact": "true",             # flag: not estimated
                    # ── Legal anchor ──
                    "legal_anchor": legal_anchor_ref,
                    "anchor_type": anchor_type_str,
                    "article_or_section": article_or_section,   # backwards compat
                    # ── Bookkeeping ──
                    "chunk_index": total_chunks,
                    "ingested_at": datetime.now().isoformat(),
                }],
            )
            total_chunks += 1

    return {
        "filename": document_name,
        "status": "ingested",
        "chunk_count": total_chunks,
        "page_count": len(pages_data),
        "skipped_pages": skipped_pages,
        "file_size": os.path.getsize(filepath),
    }


def ingest_directory(directory: str) -> List[Dict]:
    """Ingest all supported files in a directory."""
    results = []
    supported_extensions = {".txt", ".pdf", ".md"}

    if not os.path.isdir(directory):
        return results

    for filename in os.listdir(directory):
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported_extensions:
            filepath = os.path.join(directory, filename)
            try:
                result = ingest_file(filepath)
                results.append(result)
            except Exception as e:
                results.append({
                    "filename": filename,
                    "status": "error",
                    "message": str(e),
                    "chunk_count": 0,
                })

    return results


def ingest_default_documents() -> List[Dict]:
    """Ingest the default regulatory documents from the data directory."""
    data_dir = os.environ.get(
        "DATA_DIR",
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"),
    )
    regulations_dir = os.path.join(os.path.abspath(data_dir), "regulations")
    return ingest_directory(regulations_dir)


def get_collection_stats() -> Dict:
    """Get statistics about the current collection."""
    try:
        collection = get_collection()
        count = collection.count()
        return {
            "total_chunks": count,
            "collection_name": COLLECTION_NAME,
            "persist_dir": os.path.abspath(CHROMA_PERSIST_DIR),
        }
    except Exception as e:
        return {
            "total_chunks": 0,
            "collection_name": COLLECTION_NAME,
            "error": str(e),
        }


# ── Legacy compatibility shim (not used in v2, kept for external callers) ─────

def detect_article_sections(pages_data: List[Dict]) -> List[Dict]:
    """
    DEPRECATED — kept only for external callers that may still reference this.

    The new pipeline does not use this function. Page-first chunking in
    ingest_file() replaces section detection entirely.
    """
    import warnings
    warnings.warn(
        "detect_article_sections() is deprecated. "
        "Use ingest_file() which performs page-first chunking.",
        DeprecationWarning,
        stacklevel=2,
    )
    full_text = ""
    char_to_page = []
    for page in pages_data:
        start_idx = len(full_text)
        full_text += page["text"] + "\n\n"
        end_idx = len(full_text)
        char_to_page.extend([page["page_number"]] * (end_idx - start_idx))

    pattern = r"(Article\s+\d+[a-z]?\s*[-–—]\s*[^\n]+)"
    matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        page_num = char_to_page[start] if start < len(char_to_page) else 1
        sections.append({
            "article_or_section": match.group(1).strip(),
            "text": full_text[start:end].strip(),
            "page_number": page_num,
        })
    if not sections:
        sections.append({
            "article_or_section": "Full Document",
            "text": full_text,
            "page_number": pages_data[0]["page_number"] if pages_data else 1,
        })
    return sections
