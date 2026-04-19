"""
FastAPI router for AI use case assessment.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime
import json
import os

from ..models.schemas import UseCaseInput, ClassificationResult, ReportOutput
from ..chains.classifier import classify_use_case
from ..services.report_generator import generate_report, save_report


router = APIRouter()

# In-memory storage for demo purposes
# In a real app, this would be a database
_assessments = {}
_reports = {}

def get_outputs_dir():
    outputs_dir = os.environ.get("OUTPUTS_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "outputs"))
    os.makedirs(outputs_dir, exist_ok=True)
    return os.path.abspath(outputs_dir)


@router.post("/assess", response_model=ClassificationResult)
async def assess_use_case(use_case: UseCaseInput, background_tasks: BackgroundTasks):
    """
    Assess an AI use case and return risk classification.
    """
    try:
        # Run classification pipeline
        result = classify_use_case(use_case)
        
        # Store result
        _assessments[result.id] = result
        
        # Generate report in background
        report = generate_report(result)
        _reports[report.id] = report
        
        outputs_dir = get_outputs_dir()
        background_tasks.add_task(save_report, report, outputs_dir, ["json", "markdown", "pdf"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/assessments", response_model=List[Dict[str, Any]])
async def list_assessments():
    """List all past assessments."""
    return [
        {
            "id": a.id,
            "title": a.use_case_title,
            "classification": a.risk_classification,
            "timestamp": a.timestamp,
            "confidence": a.confidence_score
        }
        for a in sorted(_assessments.values(), key=lambda x: x.timestamp, reverse=True)
    ]


@router.get("/assessments/{assessment_id}", response_model=ClassificationResult)
async def get_assessment(assessment_id: str):
    """Get a specific assessment by ID."""
    if assessment_id not in _assessments:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return _assessments[assessment_id]
