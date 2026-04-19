"""
Taxonomy loader utility.
Loads the risk taxonomy configuration from YAML and provides
helper functions for category matching.
"""

import os
import yaml
from typing import List, Dict, Any


_TAXONOMY_CACHE = None


def get_taxonomy_path() -> str:
    """Get the path to the risk taxonomy YAML file."""
    return os.path.join(os.path.dirname(__file__), "risk_taxonomy.yaml")


def load_taxonomy() -> Dict[str, Any]:
    """Load and cache the risk taxonomy configuration."""
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is None:
        with open(get_taxonomy_path(), "r", encoding="utf-8") as f:
            _TAXONOMY_CACHE = yaml.safe_load(f)
    return _TAXONOMY_CACHE


def reload_taxonomy() -> Dict[str, Any]:
    """Force reload taxonomy from disk."""
    global _TAXONOMY_CACHE
    _TAXONOMY_CACHE = None
    return load_taxonomy()


def get_risk_categories() -> List[Dict[str, Any]]:
    """Get all risk categories from taxonomy."""
    taxonomy = load_taxonomy()
    return taxonomy.get("categories", [])


def get_concern_flags() -> List[Dict[str, Any]]:
    """Get all concern flag definitions."""
    taxonomy = load_taxonomy()
    return taxonomy.get("concern_flags", [])


def get_high_risk_domains() -> List[str]:
    """Get list of domains considered high-risk."""
    taxonomy = load_taxonomy()
    return taxonomy.get("domains_high_risk", [])


def get_taxonomy_summary() -> str:
    """Get a formatted summary of the taxonomy for use in prompts."""
    categories = get_risk_categories()
    concerns = get_concern_flags()
    
    lines = ["## Risk Classification Categories\n"]
    for cat in categories:
        lines.append(f"### {cat['name']} (Severity: {cat['severity']})")
        lines.append(f"{cat['description']}")
        lines.append("Triggers:")
        for t in cat.get("triggers", []):
            lines.append(f"  - {t}")
        lines.append("")
    
    lines.append("\n## Compliance Concern Flags\n")
    for flag in concerns:
        lines.append(f"### {flag['name']}")
        lines.append("Triggers:")
        for t in flag.get("triggers", []):
            lines.append(f"  - {t}")
        lines.append("")
    
    return "\n".join(lines)


def _flag_article_map() -> Dict[str, str]:
    """Map each concern flag to its primary EU AI Act / GDPR article."""
    return {
        "Privacy Concern": "GDPR Art. 5-6, EU AI Act Art. 10",
        "Fairness / Bias Concern": "EU AI Act Art. 10 (Data Governance)",
        "Transparency Concern": "EU AI Act Art. 50",
        "Human Oversight Concern": "EU AI Act Art. 14",
        "Data Governance Concern": "EU AI Act Art. 10",
    }


def match_input_flags(personal_data: bool, sensitive_data: bool,
                      automated_decisions: bool, impacts_rights: bool) -> Dict[str, str]:
    """
    Match concern flags based on structured input fields.
    Returns a dict mapping each triggered flag name to the specific checkbox
    that triggered it, including the EU AI Act article reference.
    """
    matched: Dict[str, str] = {}
    concerns = get_concern_flags()
    art_map = _flag_article_map()

    checkbox_labels = {
        "personal_data": "\"Processes Personal Data\" checkbox",
        "sensitive_data": "\"Processes Sensitive Data\" checkbox",
        "automated_decisions": "\"Automated Decision-Making\" checkbox",
        "impacts_rights": "\"Impacts Rights or Opportunities\" checkbox",
    }

    for concern in concerns:
        input_fields = concern.get("input_fields", [])
        for field in input_fields:
            if {"personal_data": personal_data, "sensitive_data": sensitive_data,
                "automated_decisions": automated_decisions, "impacts_rights": impacts_rights}.get(field, False):
                article = art_map.get(concern["name"], "")
                article_suffix = f" [{article}]" if article else ""
                matched[concern["name"]] = (
                    f"Triggered by: {checkbox_labels.get(field, field)}{article_suffix}"
                )
                break

    return matched


def match_description_flags(description: str, title: str) -> Dict[str, str]:
    """
    Match additional concern flags from free-text description/title keywords.
    Returns a dict mapping each triggered flag name to the triggering phrase,
    including the EU AI Act article reference.
    """
    combined = f"{title} {description}".lower()
    extra: Dict[str, str] = {}
    art_map = _flag_article_map()

    _FLAG_KEYWORDS = {
        "Fairness / Bias Concern": ["bias", "discriminat", "fairness", "protected group"],
        "Transparency Concern": ["opaque", "black box", "no explanation", "not informed"],
        "Human Oversight Concern": ["no human", "fully automated", "no appeal", "no review"],
        "Data Governance Concern": ["training data", "data quality", "data provenance"],
    }

    for flag_name, keywords in _FLAG_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                idx = combined.index(kw)
                snippet = combined[max(0, idx - 10): idx + len(kw) + 10].strip()
                article = art_map.get(flag_name, "")
                article_suffix = f" [{article}]" if article else ""
                extra[flag_name] = (
                    f'Triggered by text in description: "…{snippet}…"{article_suffix}'
                )
                break

    return extra
