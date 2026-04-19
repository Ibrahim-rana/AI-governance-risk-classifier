"""
Citation formatter for EU AI Act regulatory references.

Given a retrieved chunk (text + metadata from ChromaDB), this module
produces a fully structured citation object conforming to the output
format required by the assessment pipeline:

    Source: EU AI Act
    Legal anchor: Article 6, paragraph 1
    Page: 47              (or "pp. 47–48" for cross-page chunks)
    Support text: "..."
    Confidence: high / medium / low

Confidence rules
----------------
- high   : relevance_score ≥ 0.75  AND exact page recorded in ChromaDB metadata
- medium : relevance_score 0.50–0.74, OR page was inherited from a broad section
- low    : relevance_score < 0.50, OR no page recorded, OR missing legal anchor
"""

from __future__ import annotations

from typing import Optional


# ── Confidence thresholds ──────────────────────────────────────────────────

_HIGH_THRESHOLD = 0.75
_MEDIUM_THRESHOLD = 0.50


# ── Page string helpers ────────────────────────────────────────────────────

def format_page_ref(
    page_number: Optional[int],
    page_number_end: Optional[int] = None,
) -> str:
    """
    Return a human-readable page reference.

    Examples:
        format_page_ref(47)        → "p. 47"
        format_page_ref(47, 48)    → "pp. 47–48"
        format_page_ref(None)      → "page unknown"
    """
    if page_number is None:
        return "page unknown"
    if page_number_end is not None and page_number_end != page_number:
        return f"pp. {page_number}–{page_number_end}"
    return f"p. {page_number}"


# ── Confidence computation ─────────────────────────────────────────────────

def compute_citation_confidence(
    relevance_score: float,
    page_number: Optional[int],
    legal_anchor: Optional[str],
    page_is_exact: bool = True,
) -> str:
    """
    Compute confidence level for a citation.

    Parameters
    ----------
    relevance_score : float
        Cosine-based relevance score in [0, 1].
    page_number : int | None
        Recorded PDF page number (None = unknown).
    legal_anchor : str | None
        Detected Article / Recital / Annex reference (None = none found).
    page_is_exact : bool
        True if the page number was recorded at the chunk level (new pipeline).
        False if it was inherited from a broad section (legacy data).

    Returns
    -------
    "high" | "medium" | "low"
    """
    if page_number is None:
        return "low"

    if not page_is_exact:
        # Page was estimated / inherited — cap at medium
        if relevance_score >= _HIGH_THRESHOLD and legal_anchor:
            return "medium"
        return "low"

    if relevance_score >= _HIGH_THRESHOLD and legal_anchor:
        return "high"

    if relevance_score >= _MEDIUM_THRESHOLD:
        return "medium"

    return "low"


# ── Formatted citation string ──────────────────────────────────────────────

def build_formatted_citation(
    *,
    document: str,
    legal_anchor: Optional[str],
    anchor_type: Optional[str],
    page_number: Optional[int],
    page_number_end: Optional[int],
    excerpt: str,
    confidence: str,
) -> str:
    """
    Produce the canonical multi-line citation string.

    Output example::

        Source: EU AI Act
        Legal anchor: Article 6
        Page: p. 47
        Support text: "High-risk AI systems … shall comply with …"
        Confidence: high
    """
    lines = [f"Source: {document}"]

    if legal_anchor:
        anchor_label = (anchor_type or "").capitalize() if anchor_type else ""
        lines.append(f"Legal anchor: {legal_anchor}")
    else:
        lines.append("Legal anchor: not identified")

    lines.append(f"Page: {format_page_ref(page_number, page_number_end)}")

    # Truncate excerpt for display (max 300 chars)
    short_excerpt = excerpt.strip()
    if len(short_excerpt) > 300:
        short_excerpt = short_excerpt[:297] + "…"
    lines.append(f'Support text: "{short_excerpt}"')

    lines.append(f"Confidence: {confidence}")

    return "\n".join(lines)


# ── Main enrichment entry point ────────────────────────────────────────────

def enrich_source(
    *,
    document: str,
    article_or_section: str,
    excerpt: str,
    relevance_score: float,
    page_number: Optional[int],
    page_number_end: Optional[int] = None,
    legal_anchor: Optional[str] = None,
    anchor_type: Optional[str] = None,
    page_is_exact: bool = True,
) -> dict:
    """
    Given raw retrieved-chunk data, return an enrichment dict with:
        - legal_anchor
        - anchor_type
        - page_number_end
        - citation_confidence
        - formatted_citation

    Merge the returned dict into RetrievedSource fields.
    """
    # Fall back to article_or_section from metadata if no explicit anchor
    effective_anchor = legal_anchor or (
        article_or_section if article_or_section not in ("", "Unknown Section", "Full Document") else None
    )

    # Determine anchor_type from article_or_section if not explicit
    effective_anchor_type = anchor_type
    if not effective_anchor_type and effective_anchor:
        lower = effective_anchor.lower()
        if lower.startswith("article"):
            effective_anchor_type = "article"
        elif lower.startswith("recital"):
            effective_anchor_type = "recital"
        elif lower.startswith("annex"):
            effective_anchor_type = "annex"

    confidence = compute_citation_confidence(
        relevance_score=relevance_score,
        page_number=page_number,
        legal_anchor=effective_anchor,
        page_is_exact=page_is_exact,
    )

    formatted = build_formatted_citation(
        document=document,
        legal_anchor=effective_anchor,
        anchor_type=effective_anchor_type,
        page_number=page_number,
        page_number_end=page_number_end,
        excerpt=excerpt,
        confidence=confidence,
    )

    return {
        "legal_anchor": effective_anchor,
        "anchor_type": effective_anchor_type,
        "page_number_end": page_number_end,
        "citation_confidence": confidence,
        "formatted_citation": formatted,
    }
