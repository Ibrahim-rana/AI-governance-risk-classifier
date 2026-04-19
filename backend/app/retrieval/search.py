"""
RAG retrieval search module — page-aware edition.

Queries the ChromaDB vector store to find relevant regulatory chunks
for a given AI use case description, then enriches each hit with a
fully structured citation (legal anchor, exact PDF page, confidence).
"""

from typing import List, Dict, Optional
from ..models.schemas import RetrievedSource
from .ingestion import get_collection, get_collection_stats
from .citation import enrich_source


def search_regulations(
    query: str,
    n_results: int = 8,
    document_filter: Optional[str] = None,
) -> List[RetrievedSource]:
    """
    Search the vector store for relevant regulatory chunks.

    Each returned RetrievedSource carries:
        - page_number        : exact PDF page from new pipeline  (or best-effort from old)
        - page_number_end    : for cross-page chunks
        - legal_anchor       : Article / Recital / Annex detected on that page
        - anchor_type        : "article" | "recital" | "annex" | "none"
        - citation_confidence: "high" | "medium" | "low"
        - formatted_citation : multi-line citation string

    Args:
        query: The search query (typically a use case description).
        n_results: Number of results to return.
        document_filter: Optional filter to a specific document name.

    Returns:
        List of enriched RetrievedSource objects, sorted by relevance.
    """
    stats = get_collection_stats()
    if stats.get("total_chunks", 0) == 0:
        return []

    collection = get_collection()

    where_filter = None
    if document_filter:
        where_filter = {"document": document_filter}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, stats["total_chunks"]),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        print(f"[search] Query error: {e}")
        return []

    sources: List[RetrievedSource] = []

    if results and results.get("documents") and results["documents"][0]:
        for i, doc_text in enumerate(results["documents"][0]):
            metadata: Dict = (
                results["metadatas"][0][i] if results.get("metadatas") else {}
            )
            distance: float = (
                results["distances"][0][i] if results.get("distances") else 1.0
            )

            # Cosine distance → similarity score in [0, 1]
            relevance_score = max(0.0, 1.0 - (distance / 2.0))

            # Pull page fields from metadata
            page_number: Optional[int] = metadata.get("page_number")
            page_number_end: Optional[int] = metadata.get("page_number_end", page_number)
            legal_anchor: Optional[str] = metadata.get("legal_anchor")
            anchor_type: Optional[str] = metadata.get("anchor_type")
            article_or_section: str = metadata.get("article_or_section", "Unknown Section")

            # Was the page number recorded exactly (new pipeline) or estimated (old)?
            page_is_exact = metadata.get("page_exact", "false") == "true"

            # Sanitise: if page number is 1 and page_exact is not set it could be
            # a legacy chunk — lower confidence automatically via page_is_exact flag
            if page_number == 1 and not page_is_exact:
                page_is_exact = False

            excerpt = doc_text[:500] if len(doc_text) > 500 else doc_text

            # Build enriched citation data
            enrichment = enrich_source(
                document=metadata.get("document", "EU AI Act"),
                article_or_section=article_or_section,
                excerpt=excerpt,
                relevance_score=relevance_score,
                page_number=page_number,
                page_number_end=page_number_end,
                legal_anchor=legal_anchor if legal_anchor not in (None, "None", "") else None,
                anchor_type=anchor_type if anchor_type not in (None, "none", "") else None,
                page_is_exact=page_is_exact,
            )

            source = RetrievedSource(
                document=metadata.get("document", "EU AI Act"),
                article_or_section=article_or_section,
                excerpt=excerpt,
                citation_id=f"source_{i + 1}",
                page_number=page_number,
                page_number_end=enrichment["page_number_end"],
                legal_anchor=enrichment["legal_anchor"],
                anchor_type=enrichment["anchor_type"],
                relevance_score=round(relevance_score, 3),
                citation_confidence=enrichment["citation_confidence"],
                formatted_citation=enrichment["formatted_citation"],
            )
            sources.append(source)

    sources.sort(key=lambda s: s.relevance_score, reverse=True)
    return sources


def search_with_enhanced_query(
    use_case_title: str,
    use_case_description: str,
    domain: str = "",
    personal_data: bool = False,
    automated_decisions: bool = False,
    impacts_rights: bool = False,
    n_results: int = 8,
) -> List[RetrievedSource]:
    """
    Search with an enhanced query built from structured use case inputs.
    Combines multiple aspects of the use case into a comprehensive query.
    """
    query_parts = [
        f"AI system: {use_case_title}",
        use_case_description,
    ]

    if domain:
        query_parts.append(f"Domain: {domain}")

    if personal_data:
        query_parts.append("processes personal data, data protection requirements")

    if automated_decisions:
        query_parts.append("automated decision-making, profiling, human oversight")

    if impacts_rights:
        query_parts.append(
            "impacts fundamental rights, opportunities, access, safety, legal status"
        )

    enhanced_query = ". ".join(query_parts)
    return search_regulations(enhanced_query, n_results=n_results)


def get_all_document_names() -> List[str]:
    """Get list of all unique document names in the collection."""
    stats = get_collection_stats()
    if stats.get("total_chunks", 0) == 0:
        return []

    collection = get_collection()
    try:
        all_data = collection.get(include=["metadatas"])
        docs: set = set()
        if all_data and all_data.get("metadatas"):
            for meta in all_data["metadatas"]:
                if meta.get("document"):
                    docs.add(meta["document"])
        return sorted(list(docs))
    except Exception:
        return []
