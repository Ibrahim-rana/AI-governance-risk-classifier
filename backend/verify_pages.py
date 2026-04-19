"""
Quick page-number verification script.
Queries the ChromaDB for known EU AI Act passages and prints their citations.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

from app.retrieval.search import search_regulations
from app.retrieval.ingestion import get_collection_stats

stats = get_collection_stats()
print(f"\nCollection stats: {stats['total_chunks']} total chunks\n")

queries = [
    "prohibited AI practices social scoring",
    "high-risk AI systems classification conformity assessment",
    "transparency obligations chatbot AI generated content",
]

for q in queries:
    print(f"Query: {q}")
    results = search_regulations(q, n_results=3)
    if not results:
        print("  No results\n")
        continue
    for r in results:
        pn = r.page_number
        pn_end = r.page_number_end
        anchor = r.legal_anchor or r.article_or_section
        conf = r.citation_confidence or "N/A"
        score = r.relevance_score
        page_str = f"pp. {pn}–{pn_end}" if pn_end and pn_end != pn else f"p. {pn}" if pn else "unknown"
        print(f"  [{conf.upper()}] {anchor} | {page_str} | score={score:.3f}")
        if r.formatted_citation:
            for line in r.formatted_citation.split("\n"):
                print(f"    {line}")
        print()
    print()
