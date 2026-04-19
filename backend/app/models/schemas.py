"""
Pydantic models for the AI Governance Risk Classifier.
Defines input/output schemas for use case assessment, classification results,
report generation, and evaluation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class UseCaseInput(BaseModel):
    """Input schema for an AI use case to be assessed."""
    title: str = Field(..., description="Title of the AI system")
    description: str = Field(..., description="Free-text description of the AI use case")
    domain: str = Field(default="", description="Intended domain or industry (e.g., healthcare, finance)")
    user_type: str = Field(default="", description="Type of users affected (e.g., employees, public, patients)")
    personal_data: bool = Field(default=False, description="Whether personal data is used")
    sensitive_data: bool = Field(default=False, description="Whether sensitive/special category personal data is used")
    automated_decisions: bool = Field(default=False, description="Whether automated decision-making is involved")
    impacts_rights: bool = Field(default=False, description="Whether output impacts people's rights, opportunities, access, safety, or legal status")
    # ── New Structured Intake Fields ──
    deployment_context: str = Field(default="", description="Context of deployment: internal tool, customer-facing, public-sector")
    ai_technique: str = Field(default="", description="Core AI technique used: ML classification, LLM/GenAI, computer vision, biometrics, other")
    human_oversight_level: str = Field(default="", description="Level of human oversight: full automation, human-in-the-loop, human review after")
    affected_group_size: str = Field(default="", description="Approximate size of the affected group: < 100, 100-10k, > 10k")
    is_safety_component: bool = Field(default=False, description="Whether the AI system is a safety component of a product")


class ObligationItem(BaseModel):
    """A specific legal obligation triggered by the use case."""
    article_ref: str = Field(..., description="Article or Annex reference")
    description: str = Field(..., description="Description of the obligation")
    evidence_needed: str = Field(..., description="What must be shown to prove compliance")


class EvidenceChecklistItem(BaseModel):
    """A requirement line item for the evidence checklist."""
    item: str = Field(..., description="The evidence artifact or requirement")
    status: str = Field(..., description="Status: 'present', 'gap', or 'required'")
    article_ref: str = Field(..., description="Reference to the regulation source")


class GapItem(BaseModel):
    """A missing evidence item."""
    item: str = Field(..., description="The missing evidence artifact")
    reason: str = Field(..., description="Why this is required")
    article_ref: str = Field(..., description="Reference to the regulation source")


class RetrievedSource(BaseModel):
    """A single retrieved regulatory source with citation."""
    document: str = Field(..., description="Name of the source document")
    article_or_section: str = Field(..., description="Article or section reference (backwards-compat label)")
    excerpt: str = Field(..., description="Text excerpt from the regulation")
    citation_id: str = Field(..., description="Unique citation identifier")
    # ── Page tracking (exact, from PDF layout — never estimated) ────────────
    page_number: Optional[int] = Field(default=None, description="PDF page number where this chunk starts (matches PDF viewer)")
    page_number_end: Optional[int] = Field(default=None, description="PDF page number where this chunk ends (only differs from page_number for cross-page chunks)")
    # ── Legal anchor ────────────────────────────────────────────────────────
    legal_anchor: Optional[str] = Field(default=None, description="Most specific legal reference on the page (e.g. 'Article 6', 'Recital 47', 'Annex III')")
    anchor_type: Optional[str] = Field(default=None, description="Type of anchor: 'article' | 'recital' | 'annex' | 'paragraph' | 'none'")
    # ── Citation quality ────────────────────────────────────────────────────
    relevance_score: float = Field(default=0.0, description="Relevance score from vector retrieval")
    citation_confidence: Optional[str] = Field(default=None, description="Citation confidence: 'high' | 'medium' | 'low'")
    formatted_citation: Optional[str] = Field(default=None, description="Pre-formatted citation string ready for display")
    # ── Explainability ──────────────────────────────────────────────────────
    trigger_reason: Optional[str] = Field(default=None, description="Explanation of which text or checkbox caused this source to be relevant")


class ClassificationResult(BaseModel):
    """Output schema for a risk classification result."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique assessment ID")
    use_case_title: str = Field(..., description="Title of the assessed AI use case")
    risk_classification: str = Field(..., description="Primary risk classification level")
    risk_reasoning: str = Field(default="", description="Explanation of which input (text or checkbox) caused the risk classification")
    compliance_flags: List[str] = Field(default_factory=list, description="List of compliance concern flags")
    flag_details: Dict[str, str] = Field(default_factory=dict, description="Maps each flag to the specific input text or checkbox that triggered it")
    summary_rationale: str = Field(..., description="Short rationale for the classification")
    retrieved_sources: List[RetrievedSource] = Field(default_factory=list, description="Retrieved regulatory sources")
    recommendations: List[str] = Field(default_factory=list, description="Recommended next steps")
    obligations: List[ObligationItem] = Field(default_factory=list, description="Specific EU AI Act obligations")
    evidence_checklist: List[EvidenceChecklistItem] = Field(default_factory=list, description="Required evidence and status")
    gaps: List[GapItem] = Field(default_factory=list, description="Missing evidence/gaps identified")
    confidence_score: float = Field(default=0.0, description="Confidence score (0-1)")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Assessment timestamp")
    input_data: Optional[UseCaseInput] = Field(default=None, description="Original input data")


class ReportOutput(BaseModel):
    """Audit-ready report structure."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assessment_id: str
    title: str
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    use_case_summary: str
    classification: str
    compliance_concerns: List[str]
    explanation: str
    evidence: List[RetrievedSource]
    citations: List[str]
    recommended_mitigations: List[str]
    obligations: List[ObligationItem] = Field(default_factory=list)
    evidence_checklist: List[EvidenceChecklistItem] = Field(default_factory=list)
    gaps: List[GapItem] = Field(default_factory=list)
    confidence_score: float
    disclaimer: str = "This is a compliance risk assessment for decision-support purposes only. It does not constitute legal advice."


class DocumentInfo(BaseModel):
    """Information about an ingested regulatory document."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    document_type: str = "regulation"
    status: str = "pending"  # pending, ingesting, ingested, error
    chunk_count: int = 0
    file_size: int = 0
    ingested_at: Optional[str] = None


class EvaluationRow(BaseModel):
    """A single row in the evaluation dataset."""
    use_case_id: str
    title: str
    description: str
    domain: str = ""
    personal_data: bool = False
    sensitive_data: bool = False
    automated_decisions: bool = False
    impacts_rights: bool = False
    expected_risk_category: str
    expected_concern_flags: List[str] = Field(default_factory=list)
    notes: str = ""


class EvaluationMetrics(BaseModel):
    """Evaluation metrics for the classifier."""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    retrieval_precision: float = 0.0
    citation_correctness: float = 0.0
    hallucination_count: int = 0
    total_cases: int = 0


class EvaluationResult(BaseModel):
    """Full evaluation results including comparison."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    rag_metrics: EvaluationMetrics
    baseline_metrics: Optional[EvaluationMetrics] = None
    per_case_results: List[dict] = Field(default_factory=list)
    summary: str = ""
