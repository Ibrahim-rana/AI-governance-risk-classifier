"""
Deterministic rules engine for AI risk classification.
Evaluates structured input against the YAML taxonomy to produce a 
guaranteed deterministic risk level and mapping of required obligations.
"""

from typing import Dict, Any, List
from ..models.schemas import UseCaseInput, ObligationItem, EvidenceChecklistItem
from ..taxonomy.loader import load_taxonomy


def evaluate_rules(use_case: UseCaseInput) -> Dict[str, Any]:
    """
    Evaluates the use case against the deterministic rules taxonomy.
    Takes structured inputs and outputs a fixed risk category, a list of obligations,
    required evidence items, and a risk_reasoning string explaining the trigger.
    """
    taxonomy = load_taxonomy()
    categories = taxonomy.get("categories", [])
    high_risk_domains = taxonomy.get("domains_high_risk", [])

    # Defaults
    assigned_category = None
    obligations = []
    evidence_checklist = []
    risk_reasoning = ""

    # 1. Prohibited Risk Check
    prohibited_keywords = [
        "social scoring", "mass surveillance", "subliminal manipulation", "exploit vulnerabilities"
    ]
    for kw in prohibited_keywords:
        source = None
        if kw in use_case.description.lower():
            source = f"description (contains prohibited phrase: \"{kw}\")"
        elif kw in use_case.title.lower():
            source = f"system title (contains prohibited phrase: \"{kw}\")"
        if source:
            assigned_category = _get_category_by_level("prohibited", categories)
            risk_reasoning = (
                f"Classified as **Prohibited / Unacceptable Risk** because the {source}. "
                "This directly maps to a practice prohibited under EU AI Act Article 5."
            )
            break

    # 2. High Risk Check
    if not assigned_category:
        matched_domain = next(
            (d for d in high_risk_domains if d.lower() == use_case.domain.lower()), None
        )
        is_hr_technique = use_case.ai_technique.lower() == "biometrics"
        is_safety = use_case.is_safety_component

        if matched_domain:
            assigned_category = _get_category_by_level("high", categories)
            risk_reasoning = (
                f"Classified as **High Risk** because the selected domain is \"{use_case.domain}\", "
                "which appears in the EU AI Act Annex III list of high-risk application areas."
            )
        elif is_hr_technique:
            assigned_category = _get_category_by_level("high", categories)
            risk_reasoning = (
                "Classified as **High Risk** because the selected AI technique is \"Biometric Recognition\", "
                "which is categorized as high-risk under EU AI Act Annex III."
            )
        elif is_safety:
            assigned_category = _get_category_by_level("high", categories)
            risk_reasoning = (
                "Classified as **High Risk** because the \"Safety Component\" checkbox was selected, "
                "indicating this AI system is a safety component of a regulated product (EU AI Act Annex I)."
            )

    # 3. Limited Risk Check
    if not assigned_category:
        is_customer_facing = "customer-facing" in use_case.deployment_context.lower()
        is_genai = use_case.ai_technique.lower() in ["llm/genai", "generative ai"]

        if is_customer_facing:
            assigned_category = _get_category_by_level("limited", categories)
            risk_reasoning = (
                "Classified as **Limited Risk** because the deployment context is \"Customer-facing\", "
                "triggering transparency obligations under EU AI Act Article 50."
            )
        elif is_genai:
            assigned_category = _get_category_by_level("limited", categories)
            risk_reasoning = (
                "Classified as **Limited Risk** because the selected AI technique is \"LLM / Generative AI\", "
                "which carries transparency obligations under EU AI Act Article 50."
            )
        elif use_case.automated_decisions:
            assigned_category = _get_category_by_level("limited", categories)
            risk_reasoning = (
                "Classified as **Limited Risk** because the \"Automated Decision-Making\" checkbox was selected, "
                "indicating decisions without meaningful human intervention, triggering Article 50 obligations."
            )

    # 4. Minimal Risk Fallback
    if not assigned_category:
        assigned_category = _get_category_by_level("minimal", categories)
        risk_reasoning = (
            "Classified as **Minimal Risk** because no prohibited keywords were found in the description or title, "
            "the selected domain is not in the EU AI Act high-risk list, the AI technique is not biometric, "
            "and none of the high-risk checkbox conditions were met."
        )

    # Build Output
    if assigned_category:
        for obs in assigned_category.get("obligations", []):
            obligations.append(ObligationItem(**obs))

        for ev in assigned_category.get("evidence_checklist", []):
            evidence_checklist.append(EvidenceChecklistItem(
                item=ev["item"],
                status="required",
                article_ref=ev["article_ref"]
            ))

    return {
        "risk_classification": assigned_category["name"] if assigned_category else "Unknown",
        "risk_reasoning": risk_reasoning,
        "obligations": obligations,
        "evidence_checklist": evidence_checklist,
    }


def _get_category_by_level(level: str, categories: List[Dict]) -> Dict:
    for cat in categories:
        if cat.get("level") == level:
            return cat
    return None
