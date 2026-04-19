#!/usr/bin/env python3
"""
reingest.py — Page-aware re-ingestion script for the EU AI Act.

Run this script once after the page-aware pipeline upgrade to:
  1. Delete the existing ChromaDB collection (which has wrong page numbers).
  2. Rebuild the page-level JSON index from the canonical PDF.
  3. Re-ingest all regulatory documents using the new page-first chunking.
  4. Print a verification summary.

Usage:
    cd backend
    python reingest.py

Options:
    --rebuild-index   Force-rebuild the page index even if the cache exists
    --verify          Run a page-number smoke test after ingestion
    --reset-db        Reset the ChromaDB collection before ingesting (default: True)
    --no-reset-db     Skip DB reset (add chunks on top of existing ones)
"""

import argparse
import os
import sys

# Allow running from the backend directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

from app.retrieval.page_index import build_page_index, CANONICAL_PDF, CACHE_FILE
from app.retrieval.ingestion import (
    reset_collection,
    ingest_default_documents,
    get_collection_stats,
)
from app.retrieval.search import search_regulations


# ── Verification smoke test ───────────────────────────────────────────────────

# Known passages and their expected page ranges in the official EU AI Act 2024 PDF
# (OJ 2024/1689, PDF from EUR-Lex — adjust if using a different edition)
SMOKE_TESTS = [
    {
        "query": "prohibited artificial intelligence practices social scoring",
        "expected_article": "Article 5",
        "expected_page_min": 40,
        "expected_page_max": 60,
        "description": "Article 5 — Prohibited AI practices",
    },
    {
        "query": "high-risk AI systems classification",
        "expected_article": "Article 6",
        "expected_page_min": 55,
        "expected_page_max": 80,
        "description": "Article 6 — Classification of high-risk AI systems",
    },
    {
        "query": "transparency obligations providers users AI systems",
        "expected_article": "Article 50",
        "expected_page_min": 100,
        "expected_page_max": 160,
        "description": "Article 50 — Transparency obligations",
    },
]


def run_smoke_tests() -> None:
    print("\n" + "=" * 70)
    print("VERIFICATION — Page number smoke tests")
    print("=" * 70)

    passed = 0
    failed = 0

    for test in SMOKE_TESTS:
        sources = search_regulations(test["query"], n_results=5)
        if not sources:
            print(f"  ✗  {test['description']}")
            print(f"     → No results returned")
            failed += 1
            continue

        best = sources[0]
        pn = best.page_number

        # Check page number is in expected range
        in_range = (
            pn is not None
            and test["expected_page_min"] <= pn <= test["expected_page_max"]
        )
        confidence = best.citation_confidence or "unknown"
        anchor = best.legal_anchor or best.article_or_section

        status = "✓" if in_range else "✗"
        if in_range:
            passed += 1
        else:
            failed += 1

        print(f"\n  {status}  {test['description']}")
        print(f"     Query        : {test['query'][:60]}…")
        print(f"     Best match   : {anchor}")
        print(f"     Page returned: {pn}   (expected: {test['expected_page_min']}–{test['expected_page_max']})")
        print(f"     Confidence   : {confidence}")
        print(f"     Relevance    : {best.relevance_score:.3f}")
        if not in_range and pn is not None:
            print(f"     ⚠  Page {pn} is outside the expected range — verify manually in the PDF")
        if pn == 1 and confidence in ("low", None):
            print(f"     ⚠  Page 1 with low confidence — this chunk may be from the old pipeline")

    print(f"\n  Results: {passed} passed, {failed} failed out of {len(SMOKE_TESTS)} tests")
    print("=" * 70)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Re-ingest EU AI Act with page-aware pipeline")
    parser.add_argument("--rebuild-index", action="store_true",
                        help="Force-rebuild the page index cache")
    parser.add_argument("--verify", action="store_true",
                        help="Run page-number smoke tests after ingestion")
    parser.add_argument("--no-reset-db", action="store_true",
                        help="Do NOT reset the ChromaDB collection before ingesting")
    args = parser.parse_args()

    reset_db = not args.no_reset_db

    print("=" * 70)
    print("EU AI Act — Page-Aware Re-Ingestion")
    print("=" * 70)

    # ── Step 1: Check canonical PDF ──────────────────────────────────────────
    pdf_path = CANONICAL_PDF
    if not os.path.exists(pdf_path):
        print(f"\n  ERROR: Canonical PDF not found at:\n         {pdf_path}")
        print("\n  Please place the official EU AI Act PDF at that path and retry.")
        print("  Download from: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689")
        sys.exit(1)

    pdf_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"\n  Canonical PDF : {pdf_path}")
    print(f"  File size     : {pdf_size_mb:.1f} MB")
    print(
        "\n  ⚠  Page numbers in citations will refer to THIS specific PDF file.\n"
        "     If you replace the PDF with a different edition, re-run this script."
    )

    # ── Step 2: Build page index ─────────────────────────────────────────────
    print(f"\n[1/3] Building page-level index …")
    if args.rebuild_index or not os.path.exists(CACHE_FILE):
        index = build_page_index(pdf_path=pdf_path, force_rebuild=True)
    else:
        print(f"  Page index cache found: {CACHE_FILE}")
        print("  (Use --rebuild-index to force a fresh build)")
        from app.retrieval.page_index import load_page_index
        index = load_page_index()

    readable_pages = sum(1 for p in index if p.get("readable", True))
    print(f"  Total pages   : {len(index)}")
    print(f"  Readable pages: {readable_pages}")
    print(f"  Cache file    : {CACHE_FILE}")

    # ── Step 3: Reset ChromaDB ───────────────────────────────────────────────
    if reset_db:
        print(f"\n[2/3] Resetting ChromaDB collection …")
        reset_collection()
        print("  Collection reset ✓")
    else:
        print(f"\n[2/3] Skipping DB reset (--no-reset-db)")

    # ── Step 4: Ingest documents ─────────────────────────────────────────────
    print(f"\n[3/3] Ingesting regulatory documents …")
    results = ingest_default_documents()

    for r in results:
        if r["status"] == "ingested":
            print(
                f"  ✓  {r['filename']}"
                f"  |  {r.get('page_count', '?')} pages"
                f"  |  {r['chunk_count']} chunks"
                f"  |  {r.get('skipped_pages', 0)} skipped pages"
            )
        else:
            print(f"  ✗  {r['filename']}  →  {r.get('message', 'error')}")

    stats = get_collection_stats()
    print(f"\n  Total chunks in DB: {stats['total_chunks']}")

    # ── Step 5: Optional verification ───────────────────────────────────────
    if args.verify:
        run_smoke_tests()
    else:
        print("\n  Tip: Run with --verify to check page numbers against known passages.")

    print("\nDone. The classifier will now return exact PDF page numbers in citations.")


if __name__ == "__main__":
    main()
