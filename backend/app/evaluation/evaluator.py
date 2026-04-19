"""
Evaluation pipeline for the AI risk classifier.
Runs classification on a labeled dataset and computes metrics,
including a baseline comparison without RAG.
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

from ..models.schemas import (
    UseCaseInput, 
    EvaluationRow, 
    EvaluationMetrics,
    EvaluationResult,
    ClassificationResult
)
from ..chains.classifier import classify_use_case


def load_dataset() -> List[EvaluationRow]:
    """Load the default evaluation dataset."""
    data_dir = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
    dataset_path = os.path.join(os.path.abspath(data_dir), "datasets", "evaluation_dataset.json")
    
    if not os.path.exists(dataset_path):
        return []
    
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [EvaluationRow(**row) for row in data]
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return []


def _compute_metrics(expected: List[EvaluationRow], results: List[ClassificationResult], 
                     is_rag: bool = True) -> EvaluationMetrics:
    """Compute performance metrics comparing expected to actual results."""
    if not expected or not results or len(expected) != len(results):
        return EvaluationMetrics()
    
    correct_category = 0
    total_expected_flags = 0
    total_predicted_flags = 0
    correct_flags = 0
    
    hallucination_count = 0
    total_cases = len(expected)
    
    for exp, res in zip(expected, results):
        if exp.expected_risk_category == res.risk_classification:
            correct_category += 1
        
        exp_flags = set(exp.expected_concern_flags)
        res_flags = set(res.compliance_flags)
        
        total_expected_flags += len(exp_flags)
        total_predicted_flags += len(res_flags)
        correct_flags += len(exp_flags.intersection(res_flags))
        
        if is_rag and "Article" in res.summary_rationale:
            # Simple heuristic for hallucination: citing articles when no sources retrieved
            if not res.retrieved_sources:
                hallucination_count += 1
            else:
                cited_articles = [s.article_or_section for s in res.retrieved_sources]
                # If they explicitly mention an article not in sources, potential hallucination
                # (Simple check for this prototype)
    
    accuracy = correct_category / total_cases if total_cases > 0 else 0
    
    precision = correct_flags / total_predicted_flags if total_predicted_flags > 0 else 0
    recall = correct_flags / total_expected_flags if total_expected_flags > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    retrieval_precision = 0.0
    citation_correctness = 0.0
    if is_rag:
        cases_with_sources = sum(1 for r in results if r.retrieved_sources)
        retrieval_precision = cases_with_sources / total_cases if total_cases > 0 else 0
        
        # Calculate citation correctness: does the cited passage support the obligation claimed?
        cases_with_correct_citations = 0
        cases_with_obligations = 0
        
        for res in results:
            if not res.obligations:
                continue
            cases_with_obligations += 1
            
            # Get the set of articles required by the rules engine
            required_article_refs = set(o.article_ref.lower() for o in res.obligations)
            
            # Get the set of articles actually retrieved by RAG
            retrieved_anchors = []
            for source in res.retrieved_sources:
                if source.legal_anchor:
                    retrieved_anchors.append(source.legal_anchor.lower())
                elif source.article_or_section:
                    retrieved_anchors.append(source.article_or_section.lower())
                    
            retrieved_anchors_set = set(retrieved_anchors)
            
            # A citation is correct if at least one of the retrieved anchors maps to ONE of the required obligations
            # Or if we want strict correctness: if all retrieved anchors are mapped to obligations.
            # Reviewer asked: "does the cited passage support the obligation you claim"
            # Let's check how many of the triggered obligations are actually backed up by a retrieved source
            backed_up_obligations = 0
            for req in required_article_refs:
                if any(req in r_anchor for r_anchor in retrieved_anchors_set):
                    backed_up_obligations += 1
            
            if len(required_article_refs) > 0 and backed_up_obligations > 0:
                cases_with_correct_citations += 1
                
        if cases_with_obligations > 0:
            citation_correctness = cases_with_correct_citations / cases_with_obligations
            
    return EvaluationMetrics(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        retrieval_precision=retrieval_precision,
        citation_correctness=citation_correctness,
        hallucination_count=hallucination_count,
        total_cases=total_cases
    )


def run_evaluation(dataset: List[EvaluationRow] = None, run_baseline: bool = True) -> EvaluationResult:
    """
    Run evaluation on a dataset, optionally comparing RAG to a baseline.
    """
    if dataset is None:
        dataset = load_dataset()
    
    if not dataset:
        raise ValueError("No dataset found or provided for evaluation.")
    
    rag_results = []
    baseline_results = []
    per_case_results = []
    
    for idx, row in enumerate(dataset):
        use_case = UseCaseInput(
            title=row.title,
            description=row.description,
            domain=row.domain,
            personal_data=row.personal_data,
            sensitive_data=row.sensitive_data,
            automated_decisions=row.automated_decisions,
            impacts_rights=row.impacts_rights,
            deployment_context="",
            ai_technique="",
            human_oversight_level="",
            affected_group_size="",
            is_safety_component=False
        )
        
        rag_res = classify_use_case(use_case, use_rag=True)
        rag_results.append(rag_res)
        
        case_result = {
            "id": row.use_case_id,
            "title": row.title,
            "expected_category": row.expected_risk_category,
            "rag_category": rag_res.risk_classification,
            "expected_flags": row.expected_concern_flags,
            "rag_flags": rag_res.compliance_flags,
            "rag_confidence": rag_res.confidence_score,
            "sources_count": len(rag_res.retrieved_sources)
        }
        
        if run_baseline:
            base_res = classify_use_case(use_case, use_rag=False)
            baseline_results.append(base_res)
            case_result["baseline_category"] = base_res.risk_classification
            case_result["baseline_flags"] = base_res.compliance_flags
        
        per_case_results.append(case_result)
    
    rag_metrics = _compute_metrics(dataset, rag_results, is_rag=True)
    baseline_metrics = None
    if run_baseline:
        baseline_metrics = _compute_metrics(dataset, baseline_results, is_rag=False)
        
    summary = f"Evaluated {len(dataset)} cases. RAG Accuracy: {rag_metrics.accuracy:.1%}. "
    if run_baseline:
        summary += f"Baseline Accuracy: {baseline_metrics.accuracy:.1%}."
        
    return EvaluationResult(
        rag_metrics=rag_metrics,
        baseline_metrics=baseline_metrics,
        per_case_results=per_case_results,
        summary=summary
    )
