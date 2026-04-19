"""
Classification chain using LangChain.
Orchestrates: retrieval -> classification -> structured output parsing.
Falls back to a rule-based mock classifier when no LLM API key is available.
"""

import os
import json
import re
from typing import Optional
from dotenv import load_dotenv

from ..models.schemas import UseCaseInput, ClassificationResult, RetrievedSource
from ..retrieval.search import search_with_enhanced_query
from ..taxonomy.loader import get_taxonomy_summary, match_input_flags, match_description_flags, get_high_risk_domains
from ..prompts.classify_prompt import SYSTEM_PROMPT, USER_PROMPT, BASELINE_PROMPT

load_dotenv()


def _get_llm():
    """Get LLM instance if API key is available."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-openai-api-key-here":
        return None
    try:
        from langchain_openai import ChatOpenAI
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(
            model=model,
            temperature=0.1,
            api_key=api_key
        )
    except Exception as e:
        print(f"Failed to initialize LLM: {e}")
        return None


def _parse_llm_response(response_text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks."""
    text = response_text.strip()
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        text = json_match.group(1).strip()
    
    brace_start = text.find('{')
    brace_end = text.rfind('}')
    if brace_start != -1 and brace_end != -1:
        text = text[brace_start:brace_end + 1]
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _format_retrieved_context(sources: list) -> str:
    """Format retrieved sources into context string for the prompt."""
    if not sources:
        return "No regulatory documents have been ingested yet. Classification will be based on general knowledge of the taxonomy."
    
    parts = []
    for i, source in enumerate(sources):
        parts.append(f"[Source {i+1}] Document: {source.document}")
        
        # Prefer the structured legal_anchor over the raw article_or_section label
        anchor = getattr(source, "legal_anchor", None) or source.article_or_section
        parts.append(f"  Legal anchor: {anchor}")
        
        # Exact PDF page reference
        pn = source.page_number
        pn_end = getattr(source, "page_number_end", None)
        if pn is not None:
            if pn_end and pn_end != pn:
                parts.append(f"  Page: pp. {pn}–{pn_end}")
            else:
                parts.append(f"  Page: p. {pn}")
        else:
            parts.append("  Page: unknown")
        
        # Citation confidence
        conf = getattr(source, "citation_confidence", None)
        if conf:
            parts.append(f"  Citation confidence: {conf}")
        
        parts.append(f"  Relevance: {source.relevance_score}")
        parts.append(f"  Excerpt: {source.excerpt}")
        parts.append("")
    return "\n".join(parts)



def _rule_based_classify(use_case: UseCaseInput, sources: list) -> dict:
    """Rule-based fallback classifier when no LLM is available."""
    high_risk_domains = get_high_risk_domains()
    domain_lower = use_case.domain.lower() if use_case.domain else ""
    desc_lower = use_case.description.lower()
    title_lower = use_case.title.lower()
    combined = f"{title_lower} {desc_lower} {domain_lower}"
    
    prohibited_keywords = ["social scoring", "mass surveillance", "subliminal manipulation",
                           "exploit vulnerabilities", "untargeted scraping facial"]
    high_risk_keywords = ["recruitment", "hiring", "employment", "education", "law enforcement",
                          "police", "border control", "immigration", "critical infrastructure",
                          "healthcare", "medical", "diagnosis", "credit scor", "insurance",
                          "biometric", "public services", "exam proctoring", "facial recognition"]
    
    risk_classification = "Minimal Risk"
    confidence = 0.65
    
    for kw in prohibited_keywords:
        if kw in combined:
            risk_classification = "Prohibited / Unacceptable Risk"
            confidence = 0.75
            break
    
    if risk_classification == "Minimal Risk":
        for kw in high_risk_keywords:
            if kw in combined:
                risk_classification = "High Risk"
                confidence = 0.72 + (0.01 * len(kw)) # Add variance based on match length
                break
    
    if risk_classification == "Minimal Risk":
        for d in high_risk_domains:
            if d.lower() in combined:
                risk_classification = "High Risk"
                confidence = 0.68
                break
    
    if risk_classification == "Minimal Risk" and (use_case.impacts_rights or use_case.automated_decisions):
        risk_classification = "Limited Risk"
        confidence = 0.60 + (0.05 if use_case.impacts_rights else 0) + (0.05 if use_case.automated_decisions else 0)
    
    # match_input_flags now returns Dict[str, str] (flag -> reason)
    flags: dict = match_input_flags(
        use_case.personal_data, use_case.sensitive_data,
        use_case.automated_decisions, use_case.impacts_rights
    )
    # Also merge in description-based keyword flags
    flags.update(match_description_flags(use_case.description, use_case.title))

    # Additional implied flags from checkboxes (with explicit reasons + article refs)
    if use_case.impacts_rights and "Fairness / Bias Concern" not in flags:
        flags["Fairness / Bias Concern"] = 'Triggered by: "Impacts Rights or Opportunities" checkbox [EU AI Act Art. 10 (Data Governance)]'
    if use_case.automated_decisions and "Transparency Concern" not in flags:
        flags["Transparency Concern"] = 'Triggered by: "Automated Decision-Making" checkbox [EU AI Act Art. 50]'

    source_refs = []
    if sources:
        source_refs = [f"{s.document} ({s.article_or_section})" for s in sources[:3]]

    rationale_parts = [f"This AI system ({use_case.title}) has been classified as {risk_classification}."]
    if domain_lower:
        rationale_parts.append(f"Operating in the {use_case.domain} domain.")
    if use_case.personal_data:
        rationale_parts.append("It processes personal data, triggering GDPR obligations.")
    if use_case.impacts_rights:
        rationale_parts.append("It may impact fundamental rights, opportunities, or legal status of individuals.")
    if source_refs:
        rationale_parts.append(f"Relevant regulatory references: {'; '.join(source_refs)}.")
    else:
        rationale_parts.append("Note: No regulatory documents ingested - classification based on rule-based analysis only.")

    recommendations = []
    if use_case.personal_data:
        recommendations.append("Document the lawful basis for processing personal data under GDPR Article 6")
    if use_case.sensitive_data:
        recommendations.append("Conduct a Data Protection Impact Assessment (DPIA) per GDPR Article 35")
    if use_case.automated_decisions:
        recommendations.append("Implement human oversight mechanisms and appeal pathways")
    if use_case.impacts_rights:
        recommendations.append("Conduct a fundamental rights impact assessment")
    if "Fairness / Bias Concern" in flags:
        recommendations.append("Perform a bias and fairness assessment on training data and model outputs")
    if risk_classification == "High Risk":
        recommendations.append("Ensure compliance with EU AI Act high-risk system requirements (Articles 9-15)")
    if not recommendations:
        recommendations.append("Document the AI system's intended purpose and risk assessment")
        recommendations.append("Maintain transparency about AI usage with affected persons")

    return {
        "risk_classification": risk_classification,
        "compliance_flags": list(flags.keys()),
        "flag_details": flags,
        "summary_rationale": " ".join(rationale_parts),
        "recommendations": recommendations[:5],
        "confidence_score": round(confidence, 2)
    }


from ..engine.rules import evaluate_rules
from ..engine.checklist import build_gap_repository


def _annotate_sources(sources: list, use_case: UseCaseInput) -> list:
    """
    Deterministically annotate each RetrievedSource with a `trigger_reason`
    that explains *exactly* which user input (text phrase or checkbox)
    caused this regulatory excerpt to be relevant.

    Sources that cannot be mapped to a concrete trigger are dropped so
    that the frontend only displays citations with clear traceability.
    """
    if not sources:
        return []

    desc_lower = use_case.description.lower()
    title_lower = use_case.title.lower()
    combined = f"{title_lower} {desc_lower}"

    # ── keyword buckets mapped to the regulation articles they match ──
    _ARTICLE_KEYWORD_MAP = {
        "Article 5": {
            "keywords": ["social scoring", "mass surveillance", "subliminal manipulation",
                         "exploit vulnerabilities", "untargeted scraping"],
            "label": "prohibited practice",
        },
        "Article 6": {
            "keywords": ["high-risk", "high risk", "annex iii", "safety component"],
            "label": "high-risk classification criteria",
        },
        "Article 9": {
            "keywords": ["risk management", "lifecycle", "risk assessment"],
            "label": "risk management obligation",
        },
        "Article 10": {
            "keywords": ["training data", "data governance", "data quality", "data set",
                         "bias", "representativeness"],
            "label": "data governance obligation",
        },
        "Article 11": {
            "keywords": ["technical documentation", "annex iv"],
            "label": "technical documentation obligation",
        },
        "Article 14": {
            "keywords": ["human oversight", "human-in-the-loop", "human intervention",
                         "overriding", "override"],
            "label": "human oversight obligation",
        },
        "Article 50": {
            "keywords": ["transparency", "inform", "disclosure", "chatbot", "deepfake",
                         "synthetic", "generated content"],
            "label": "transparency obligation",
        },
        "Annex III": {
            "keywords": ["biometric", "critical infrastructure", "education", "employment",
                         "law enforcement", "border", "migration", "justice",
                         "healthcare", "medical", "credit", "insurance"],
            "label": "high-risk use-case area",
        },
    }

    # checkbox → human description
    _CHECKBOX_TRIGGERS = []
    if use_case.personal_data:
        _CHECKBOX_TRIGGERS.append(("personal data", '"Processes Personal Data" checkbox'))
    if use_case.sensitive_data:
        _CHECKBOX_TRIGGERS.append(("sensitive data", '"Processes Sensitive Data" checkbox'))
    if use_case.automated_decisions:
        _CHECKBOX_TRIGGERS.append(("automated decision", '"Automated Decision-Making" checkbox'))
    if use_case.impacts_rights:
        _CHECKBOX_TRIGGERS.append(("fundamental right", '"Impacts Rights or Opportunities" checkbox'))
        _CHECKBOX_TRIGGERS.append(("impact", '"Impacts Rights or Opportunities" checkbox'))
    if use_case.is_safety_component:
        _CHECKBOX_TRIGGERS.append(("safety component", '"Safety Component" checkbox'))

    # domain → text probe
    domain_lower = (use_case.domain or "").lower()

    annotated = []
    for source in sources:
        excerpt_lower = source.excerpt.lower()
        anchor = (source.legal_anchor or source.article_or_section or "").strip()
        reasons = []

        # 1. Match by article anchor → specific user input
        for art, info in _ARTICLE_KEYWORD_MAP.items():
            # Does this source's anchor reference this article?
            if art.lower() in anchor.lower() or art.lower().replace(" ", "") in anchor.lower().replace(" ", ""):
                # Find the specific user text that triggers this article
                for kw in info["keywords"]:
                    if kw in combined:
                        # Extract a short surrounding snippet
                        idx = combined.index(kw)
                        snippet = combined[max(0, idx - 15): idx + len(kw) + 15].strip()
                        reasons.append(
                            f'{art} ({info["label"]}) — triggered by text in description: "…{snippet}…"'
                        )
                        break
                # Also check checkbox triggers
                if not reasons:
                    for kw, label in _CHECKBOX_TRIGGERS:
                        if kw in excerpt_lower:
                            reasons.append(
                                f'{art} ({info["label"]}) — triggered by {label}'
                            )
                            break
                # Domain match for Annex III
                if not reasons and art == "Annex III" and domain_lower:
                    for kw in info["keywords"]:
                        if kw in domain_lower:
                            reasons.append(
                                f'{art} ({info["label"]}) — triggered by selected domain: "{use_case.domain}"'
                            )
                            break

        # 2. If anchor didn't match, try matching excerpt keywords against user input
        if not reasons:
            for art, info in _ARTICLE_KEYWORD_MAP.items():
                for kw in info["keywords"]:
                    if kw in excerpt_lower and kw in combined:
                        idx = combined.index(kw)
                        snippet = combined[max(0, idx - 15): idx + len(kw) + 15].strip()
                        reasons.append(
                            f'{art} ({info["label"]}) — excerpt mentions "{kw}" which matches description text: "…{snippet}…"'
                        )
                        break
                if reasons:
                    break

        # 3. Checkbox-based match: excerpt mentions a checkbox concept
        if not reasons:
            for kw, label in _CHECKBOX_TRIGGERS:
                if kw in excerpt_lower:
                    reasons.append(
                        f"Relevant to {label} — excerpt discusses: \"{kw}\""
                    )
                    break

        # 4. Domain match as last resort
        if not reasons and domain_lower:
            if domain_lower in excerpt_lower:
                reasons.append(
                    f'Relevant to selected domain "{use_case.domain}" — excerpt mentions this domain'
                )

        # Only keep sources where we found a concrete reason
        if reasons:
            source.trigger_reason = reasons[0]  # primary reason
            # Ensure article number is always visible
            if not anchor or anchor in ("Unknown Section", "Full Document", ""):
                # Try to extract article from the reason itself
                for art in _ARTICLE_KEYWORD_MAP:
                    if art.lower() in reasons[0].lower():
                        source.legal_anchor = art
                        break
            annotated.append(source)

    return annotated


def classify_use_case(use_case: UseCaseInput, use_rag: bool = True) -> ClassificationResult:
    """
    Main classification function.
    Retrieves relevant regulatory text and classifies the use case.
    
    Args:
        use_case: The AI use case to classify
        use_rag: Whether to use RAG retrieval (False for baseline comparison)
    
    Returns:
        ClassificationResult with full classification details
    """
    sources = []
    if use_rag:
        sources = search_with_enhanced_query(
            use_case_title=use_case.title,
            use_case_description=use_case.description,
            domain=use_case.domain,
            personal_data=use_case.personal_data,
            automated_decisions=use_case.automated_decisions,
            impacts_rights=use_case.impacts_rights,
            n_results=8
        )
        # Annotate and filter: only keep sources with a clear trigger reason
        sources = _annotate_sources(sources, use_case)

    # --- Build flag details from all deterministic sources ---
    # 1a. Checkbox-based flags -> dict {flag_name: reason}
    checkbox_flag_details = match_input_flags(
        use_case.personal_data, use_case.sensitive_data,
        use_case.automated_decisions, use_case.impacts_rights
    )
    # 1b. Description keyword-based flags -> dict {flag_name: reason}
    description_flag_details = match_description_flags(use_case.description, use_case.title)

    # Merge: checkbox flags take precedence; description adds extras
    merged_flag_details = {**description_flag_details, **checkbox_flag_details}

    # 2. Deterministic Rules Engine
    rules_result = evaluate_rules(use_case)
    risk_classification = rules_result["risk_classification"]
    risk_reasoning = rules_result["risk_reasoning"]
    obligations = rules_result["obligations"]
    required_evidence = rules_result["evidence_checklist"]

    # 3. Checklist Engine
    gap_result = build_gap_repository(required_evidence, sources)
    evidence_checklist = gap_result["evidence_checklist"]
    gaps = gap_result["gaps"]

    # Input flags list (just the names, for backwards compat)
    input_flag_names = list(merged_flag_details.keys())

    llm = _get_llm()

    if llm is not None:
        try:
            retrieved_context = _format_retrieved_context(sources) if use_rag else "No retrieval used - classify based on your knowledge."

            # Format obligations for prompt
            obs_str = "\\n".join([f"- {o.article_ref}: {o.description} (Needs: {o.evidence_needed})" for o in obligations])
            if not obs_str:
                obs_str = "None"

            if use_rag:
                system_msg = SYSTEM_PROMPT.format(
                    risk_classification=risk_classification,
                    obligations=obs_str,
                    retrieved_context=retrieved_context,
                    input_flags=", ".join(input_flag_names) if input_flag_names else "None"
                )
                user_msg = USER_PROMPT.format(
                    title=use_case.title,
                    description=use_case.description,
                    domain=use_case.domain or "Not specified",
                    user_type=use_case.user_type or "Not specified",
                    deployment_context=use_case.deployment_context or "Not specified",
                    ai_technique=use_case.ai_technique or "Not specified",
                    human_oversight_level=use_case.human_oversight_level or "Not specified",
                    affected_group_size=use_case.affected_group_size or "Not specified",
                    is_safety_component="Yes" if use_case.is_safety_component else "No",
                    personal_data="Yes" if use_case.personal_data else "No",
                    sensitive_data="Yes" if use_case.sensitive_data else "No",
                    automated_decisions="Yes" if use_case.automated_decisions else "No",
                    impacts_rights="Yes" if use_case.impacts_rights else "No"
                )
                from langchain_core.messages import SystemMessage, HumanMessage
                messages = [SystemMessage(content=system_msg), HumanMessage(content=user_msg)]
            else:
                prompt = BASELINE_PROMPT.format(
                    title=use_case.title,
                    description=use_case.description,
                    domain=use_case.domain or "Not specified",
                    personal_data="Yes" if use_case.personal_data else "No",
                    automated_decisions="Yes" if use_case.automated_decisions else "No",
                    impacts_rights="Yes" if use_case.impacts_rights else "No"
                )
                from langchain_core.messages import HumanMessage
                messages = [HumanMessage(content=prompt)]

            response = llm.invoke(messages)
            parsed = _parse_llm_response(response.content)

            if parsed:
                # Merge LLM-detected flags — only accept those with a
                # specific trigger reason (never generic fallback text)
                llm_flags = parsed.get("compliance_flags", [])
                llm_flag_details = parsed.get("flag_details", {})

                from ..taxonomy.loader import _flag_article_map
                art_map = _flag_article_map()

                for flag in llm_flags:
                    if flag not in merged_flag_details:
                        reason = llm_flag_details.get(flag)
                        # Skip flags where LLM didn't provide a concrete reason
                        if not reason:
                            continue
                        # Append article reference if not already in the reason
                        article = art_map.get(flag, "")
                        if article and article not in reason:
                            reason = f"{reason} [{article}]"
                        merged_flag_details[flag] = reason

                # Final filter: only keep flags that have concrete details
                all_flag_names = [f for f in merged_flag_details if merged_flag_details[f]]

                # Process citation details
                citation_details = parsed.get("citation_details", {})
                if use_rag and sources:
                    for i, source in enumerate(sources):
                        source_key = f"[Source {i+1}]"
                        if source_key in citation_details:
                            source.trigger_reason = citation_details[source_key]

                return ClassificationResult(
                    use_case_title=use_case.title,
                    risk_classification=risk_classification,  # deterministic
                    risk_reasoning=risk_reasoning,
                    obligations=obligations,
                    evidence_checklist=evidence_checklist,
                    gaps=gaps,
                    compliance_flags=all_flag_names,
                    flag_details=merged_flag_details,
                    summary_rationale=parsed.get("summary_rationale", ""),
                    retrieved_sources=sources if use_rag else [],
                    recommendations=parsed.get("recommendations", []),
                    confidence_score=parsed.get("confidence_score", 0.5),
                    input_data=use_case
                )
        except Exception as e:
            print(f"LLM classification failed: {e}")

    # Fallback to pure rule-based if LLM fails or is absent
    return ClassificationResult(
        use_case_title=use_case.title,
        risk_classification=risk_classification,
        risk_reasoning=risk_reasoning,
        obligations=obligations,
        evidence_checklist=evidence_checklist,
        gaps=gaps,
        compliance_flags=input_flag_names,
        flag_details=merged_flag_details,
        summary_rationale="Deterministic rule engine applied. LLM rationale generation skipped or failed.",
        retrieved_sources=sources if use_rag else [],
        recommendations=["Follow obligations listed in the checklist."],
        confidence_score=0.8,
        input_data=use_case
    )

