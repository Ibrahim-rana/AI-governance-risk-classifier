"""
FastAPI router for PDF report generation and download.
"""

import re
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from ..services.report_generator import generate_report, export_pdf_bytes
from .assessment import _assessments

router = APIRouter()


class GeneratePdfRequest(BaseModel):
    assessment_id: str


def _sanitize_filename(name: str) -> str:
    """Convert a string into a safe filename component."""
    # Replace spaces/special chars with underscores, keep only alphanumerics and underscores
    sanitized = re.sub(r"[^\w\s-]", "", name)
    sanitized = re.sub(r"[\s-]+", "_", sanitized)
    return sanitized.strip("_").lower()[:60]


@router.post("/generate-pdf")
async def generate_pdf_report(request: GeneratePdfRequest):
    """
    Generate and download a PDF compliance report for a completed assessment.
    
    Returns the PDF as a downloadable file with a descriptive filename:
    ai_governance_report_<use_case_title>_<date>.pdf
    """
    # Look up the assessment
    assessment = _assessments.get(request.assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail=f"Assessment '{request.assessment_id}' not found. "
                   f"Assessments are stored in memory and may be lost on server restart."
        )

    try:
        # Generate the report structure from the classification result
        report = generate_report(assessment)

        # Generate PDF bytes
        pdf_bytes = export_pdf_bytes(report)

        # Build a descriptive filename
        title_part = _sanitize_filename(assessment.use_case_title)
        date_part = datetime.now().strftime("%Y%m%d")
        filename = f"ai_governance_report_{title_part}_{date_part}.pdf"

        # Return as a downloadable PDF
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
