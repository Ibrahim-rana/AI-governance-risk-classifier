"""
Page-level index for the EU AI Act.

Parses the canonical EU AI Act PDF page-by-page and stores a JSON index at:
    backend/page_index_cache/eu_ai_act_page_index.json

Each entry:
    {
        "page_number": int,          # 1-indexed, matches PDF viewer
        "text": str,                 # full extracted text for this page
        "char_start": int,           # offset into concatenated document
        "char_end": int,             # end offset into concatenated document
        "legal_anchors": [           # all Article / Recital / Annex refs on page
            {"ref": "Article 6", "anchor_type": "article"},
            ...
        ]
    }

Usage:
    from app.retrieval.page_index import build_page_index, load_page_index
    index = build_page_index()         # build and cache
    index = load_page_index()          # load from cache (auto-builds if missing)
"""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Optional

# ── PDF extraction ──────────────────────────────────────────────────────────

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


# ── Paths ───────────────────────────────────────────────────────────────────

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.abspath(os.path.join(_BACKEND_ROOT, "..", "data")),
)

CANONICAL_PDF = os.path.join(_DATA_DIR, "regulations", "EU_AI_ACT_2024.pdf")
CACHE_DIR = os.path.join(_BACKEND_ROOT, "page_index_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "eu_ai_act_page_index.json")


# ── Legal anchor detection ──────────────────────────────────────────────────

# Patterns ordered from most-specific to least-specific
_ANCHOR_PATTERNS: List[tuple[str, str]] = [
    # Annex (Roman numerals I–XV)
    (r"\bAnnex\s+(?:I{1,3}|IV|V{1,2}I{0,3}|IX|X{1,2}(?:I{1,3}|IV|V)?|XV?)\b", "annex"),
    # Article with optional letter suffix (Article 6a)
    (r"\bArticle\s+\d{1,3}[a-z]?\b", "article"),
    # Recital
    (r"\bRecital\s+\d{1,3}\b", "recital"),
    # Paragraph/Point — secondary anchors only
    (r"\bparagraph\s+\d{1,2}\b", "paragraph"),
    (r"\bpoint\s+\([a-z]\)\b", "point"),
]

_COMPILED_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), anchor_type)
    for pattern, anchor_type in _ANCHOR_PATTERNS
]


def detect_legal_anchors(text: str) -> List[Dict[str, str]]:
    """
    Return all legal anchors (Article, Recital, Annex …) found in *text*.
    Results are deduplicated and ordered by position of first occurrence.
    """
    seen: set[str] = set()
    anchors: List[Dict[str, str]] = []

    for pattern, anchor_type in _COMPILED_PATTERNS:
        for m in pattern.finditer(text):
            ref = re.sub(r"\s+", " ", m.group(0)).strip()
            if ref not in seen:
                seen.add(ref)
                anchors.append({"ref": ref, "anchor_type": anchor_type})

    # Sort by position of first occurrence so Article comes before Recital etc.
    positions: Dict[str, int] = {}
    for pattern, _ in _COMPILED_PATTERNS:
        for m in pattern.finditer(text):
            ref = re.sub(r"\s+", " ", m.group(0)).strip()
            if ref not in positions:
                positions[ref] = m.start()

    anchors.sort(key=lambda a: positions.get(a["ref"], 0))
    return anchors


def primary_anchor(anchors: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """Return the most specific anchor: article > annex > recital > paragraph."""
    priority = {"article": 0, "annex": 1, "recital": 2, "paragraph": 3, "point": 4}
    if not anchors:
        return None
    return min(anchors, key=lambda a: priority.get(a["anchor_type"], 99))


# ── PDF text extraction ─────────────────────────────────────────────────────

def _extract_pages_pdfplumber(filepath: str) -> List[Dict]:
    """Extract text page-by-page using pdfplumber (preferred)."""
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


def extract_pages(filepath: str) -> List[Dict]:
    """Extract pages using pdfplumber if available, else PyPDF2."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PDF not found: {filepath}")
    if PDFPLUMBER_AVAILABLE:
        return _extract_pages_pdfplumber(filepath)
    if PYPDF2_AVAILABLE:
        return _extract_pages_pypdf2(filepath)
    raise ImportError(
        "No PDF library available. Install pdfplumber: pip install pdfplumber"
    )


# ── Index build / load ──────────────────────────────────────────────────────

def build_page_index(
    pdf_path: str = CANONICAL_PDF,
    force_rebuild: bool = False,
) -> List[Dict]:
    """
    Build the page-level index from *pdf_path* and cache it as JSON.

    Each entry in the returned list:
        {
            "page_number": int,
            "text": str,
            "char_start": int,
            "char_end": int,
            "legal_anchors": [{ref, anchor_type}, ...],
            "primary_anchor": {ref, anchor_type} | None,
        }
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    if not force_rebuild and os.path.exists(CACHE_FILE):
        return load_page_index()

    print(f"[page_index] Building page index from: {pdf_path}")
    raw_pages = extract_pages(pdf_path)
    print(f"[page_index] Extracted {len(raw_pages)} pages")

    index: List[Dict] = []
    cursor = 0  # character offset in the concatenated document string

    for raw in raw_pages:
        text = raw["text"]
        char_start = cursor
        char_end = cursor + len(text)
        cursor = char_end + 1  # +1 for the page separator '\n'

        anchors = detect_legal_anchors(text)
        p_anchor = primary_anchor(anchors)

        # Skip pages with effectively no text (scanned image pages)
        if len(text.strip()) < 30:
            index.append({
                "page_number": raw["page_number"],
                "text": text,
                "char_start": char_start,
                "char_end": char_end,
                "legal_anchors": [],
                "primary_anchor": None,
                "readable": False,
            })
        else:
            index.append({
                "page_number": raw["page_number"],
                "text": text,
                "char_start": char_start,
                "char_end": char_end,
                "legal_anchors": anchors,
                "primary_anchor": p_anchor,
                "readable": True,
            })

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"[page_index] Cached {len(index)} pages → {CACHE_FILE}")
    return index


def load_page_index(auto_build: bool = True) -> List[Dict]:
    """Load the cached page index, building it if missing."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    if auto_build:
        return build_page_index()
    raise FileNotFoundError(
        f"Page index cache not found: {CACHE_FILE}\n"
        "Run build_page_index() or reingest.py first."
    )


# ── Lookup helpers ──────────────────────────────────────────────────────────

def find_pages_for_text(
    needle: str,
    index: Optional[List[Dict]] = None,
    max_results: int = 3,
) -> List[Dict]:
    """
    Search the page index for pages containing *needle* (case-insensitive).
    Returns at most *max_results* page entries.
    """
    if index is None:
        index = load_page_index()
    needle_lower = needle.lower()
    results = []
    for page in index:
        if needle_lower in page["text"].lower():
            results.append(page)
            if len(results) >= max_results:
                break
    return results


def get_page_by_number(
    page_number: int,
    index: Optional[List[Dict]] = None,
) -> Optional[Dict]:
    """Return the index entry for a specific page number."""
    if index is None:
        index = load_page_index()
    for page in index:
        if page["page_number"] == page_number:
            return page
    return None
