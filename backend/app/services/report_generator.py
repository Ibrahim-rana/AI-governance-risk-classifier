"""
Report generation service.
Generates audit-ready reports in Markdown, JSON, and PDF formats.
"""

import os
import json
from typing import Optional
from datetime import datetime

from ..models.schemas import ClassificationResult, ReportOutput


def generate_report(result: ClassificationResult) -> ReportOutput:
    """Generate a structured report from a classification result."""
    citations = []
    for source in result.retrieved_sources:
        page_info = f", Page {source.page_number}" if source.page_number else ""
        citations.append(f"[{source.citation_id}] {source.document}, {source.article_or_section}{page_info}")
    
    explanation_parts = [result.summary_rationale]
    if result.compliance_flags:
        explanation_parts.append(f"Compliance concerns identified: {', '.join(result.compliance_flags)}.")
    explanation_parts.append(f"Classification confidence: {result.confidence_score:.0%}")
    
    return ReportOutput(
        assessment_id=result.id,
        title=f"Compliance Risk Assessment: {result.use_case_title}",
        use_case_summary=_build_use_case_summary(result),
        classification=result.risk_classification,
        compliance_concerns=result.compliance_flags,
        explanation=" ".join(explanation_parts),
        evidence=result.retrieved_sources,
        citations=citations,
        recommended_mitigations=result.recommendations,
        obligations=result.obligations,
        evidence_checklist=result.evidence_checklist,
        gaps=result.gaps,
        confidence_score=result.confidence_score
    )


def _build_use_case_summary(result: ClassificationResult) -> str:
    """Build a summary of the use case from the classification result."""
    parts = [f"**AI System:** {result.use_case_title}"]
    if result.input_data:
        if result.input_data.description:
            parts.append(f"**Description:** {result.input_data.description}")
        if result.input_data.domain:
            parts.append(f"**Domain:** {result.input_data.domain}")
        if result.input_data.user_type:
            parts.append(f"**Users Affected:** {result.input_data.user_type}")
        parts.append(f"**Personal Data:** {'Yes' if result.input_data.personal_data else 'No'}")
        parts.append(f"**Sensitive Data:** {'Yes' if result.input_data.sensitive_data else 'No'}")
        parts.append(f"**Automated Decisions:** {'Yes' if result.input_data.automated_decisions else 'No'}")
        parts.append(f"**Impacts Rights:** {'Yes' if result.input_data.impacts_rights else 'No'}")
    return "\n".join(parts)


def export_markdown(report: ReportOutput) -> str:
    """Export report as Markdown string."""
    lines = [
        f"# {report.title}",
        "",
        f"*Generated: {report.generated_at}*",
        "",
        "---",
        "",
        "## Disclaimer",
        "",
        f"> {report.disclaimer}",
        "",
        "---",
        "",
        "## Use Case Summary",
        "",
        report.use_case_summary,
        "",
        "## Risk Classification",
        "",
        f"**Classification:** {report.classification}",
        "",
        f"**Confidence Score:** {report.confidence_score:.0%}",
        "",
        "## Compliance Concerns",
        "",
    ]
    
    for concern in report.compliance_concerns:
        lines.append(f"- ⚠️ {concern}")
    lines.append("")
    
    lines.extend([
        "## Explanation",
        "",
        report.explanation,
        "",
        "## Supporting Evidence",
        "",
    ])
    
    for source in report.evidence:
        page_info = f" (Page {source.page_number})" if source.page_number else ""
        lines.append(f"### [{source.citation_id}] {source.document} — {source.article_or_section}{page_info}")
        lines.append("")
        lines.append(f"> {source.excerpt[:300]}...")
        lines.append("")
        if getattr(source, "trigger_reason", None):
            lines.append(f"**Why this applies:** {source.trigger_reason}")
            lines.append("")
        lines.append(f"*Relevance Score: {source.relevance_score:.2f}*")
        lines.append("")
    
    if not report.evidence:
        lines.append("*No regulatory documents were retrieved for this assessment.*")
        lines.append("")
    
    lines.extend([
        "## Citations",
        "",
    ])
    for citation in report.citations:
        lines.append(f"- {citation}")
    lines.append("")
    
    lines.extend([
        "## Recommended Mitigations",
        "",
    ])
    for i, rec in enumerate(report.recommended_mitigations, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")
    
    lines.extend([
        "## Legal Obligations",
        "",
    ])
    for obs in report.obligations:
        lines.append(f"- **{obs.article_ref}**: {obs.description}")
        lines.append(f"  *Evidence Needed*: {obs.evidence_needed}")
    lines.append("")
    
    lines.extend([
        "## Evidence Checklist & Gap Repository",
        "",
        "| Item | Reference | Status |",
        "| --- | --- | --- |"
    ])
    for item in report.evidence_checklist:
        icon = "✅" if item.status == "present" else "❌ GAP"
        lines.append(f"| {item.item} | {item.article_ref} | {icon} |")
    lines.append("")
    
    lines.extend([
        "---",
        "",
        f"*Assessment ID: {report.assessment_id}*",
        f"*Report ID: {report.id}*",
    ])
    
    return "\n".join(lines)


def export_json(report: ReportOutput) -> str:
    """Export report as JSON string."""
    return report.model_dump_json(indent=2)


def _escape_xml(text: str) -> str:
    """Escape special XML/HTML characters for ReportLab Paragraph elements."""
    if not text:
        return ""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _get_risk_color(classification: str) -> tuple:
    """Return (background_hex, text_hex) based on risk classification."""
    if "Prohibited" in (classification or ""):
        return ("#FEE2E2", "#991B1B")  # Red
    if "High" in (classification or ""):
        return ("#FFF7ED", "#9A3412")  # Orange
    if "Limited" in (classification or ""):
        return ("#FEFCE8", "#854D0E")  # Yellow
    return ("#F0FDF4", "#166534")       # Green


def _build_audit_readiness_summary(report: ReportOutput) -> str:
    """Generate a short audit-readiness summary paragraph."""
    concern_count = len(report.compliance_concerns)
    evidence_count = len(report.evidence)
    rec_count = len(report.recommended_mitigations)

    risk_word = report.classification.split()[0] if report.classification else "Undetermined"

    if concern_count == 0:
        posture = "No specific compliance concerns were identified."
    elif concern_count <= 2:
        posture = f"{concern_count} compliance concern(s) were flagged for review."
    else:
        posture = f"Multiple compliance concerns ({concern_count}) were identified, indicating significant regulatory exposure."

    return (
        f"This assessment classified the AI system as '{report.classification}' "
        f"with a confidence score of {report.confidence_score:.0%}. "
        f"{posture} "
        f"The analysis drew upon {evidence_count} retrieved regulatory source(s) and produced "
        f"{rec_count} actionable recommendation(s). "
        f"Organizations deploying this system should review all flagged concerns and implement "
        f"the recommended mitigations before proceeding to production deployment."
    )


def export_pdf_bytes(report: ReportOutput) -> bytes:
    """
    Export report as a professional, audit-ready PDF.
    Includes all required sections: title, use case, date/time,
    risk classification, confidence, compliance flags, rationale,
    regulatory citations, actionable insights, audit-readiness
    summary, and footer disclaimer.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.lib.colors import HexColor, Color
        from reportlab.lib.units import inch, mm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        import io

        buffer = io.BytesIO()
        page_w, page_h = A4

        # ----- Page number callback -----
        def _add_page_number(canvas, doc):
            canvas.saveState()
            # Footer line
            canvas.setStrokeColor(HexColor("#CBD5E1"))
            canvas.setLineWidth(0.5)
            canvas.line(50, 45, page_w - 50, 45)
            # Footer text
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(HexColor("#94A3B8"))
            canvas.drawString(
                50, 30,
                "This is a compliance decision-support report and does not constitute formal legal advice."
            )
            canvas.drawRightString(page_w - 50, 30, f"Page {doc.page}")
            canvas.restoreState()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=50,
            bottomMargin=60,
            leftMargin=50,
            rightMargin=50,
        )

        # ========== STYLES ==========
        styles = getSampleStyleSheet()

        s_report_title = ParagraphStyle(
            "ReportTitle", parent=styles["Title"],
            fontSize=20, leading=24, spaceAfter=4,
            textColor=HexColor("#0F172A"),
            alignment=TA_CENTER,
        )
        s_subtitle = ParagraphStyle(
            "Subtitle", parent=styles["Normal"],
            fontSize=10, leading=14, spaceAfter=16,
            textColor=HexColor("#64748B"),
            alignment=TA_CENTER,
        )
        s_section = ParagraphStyle(
            "SectionHeading", parent=styles["Heading2"],
            fontSize=14, leading=18, spaceBefore=18, spaceAfter=8,
            textColor=HexColor("#1E293B"),
            borderPadding=(0, 0, 4, 0),
        )
        s_subsection = ParagraphStyle(
            "SubSection", parent=styles["Heading3"],
            fontSize=11, leading=15, spaceBefore=10, spaceAfter=4,
            textColor=HexColor("#334155"),
        )
        s_body = ParagraphStyle(
            "BodyText2", parent=styles["Normal"],
            fontSize=10, leading=14, spaceAfter=6,
            textColor=HexColor("#334155"),
            alignment=TA_JUSTIFY,
        )
        s_label = ParagraphStyle(
            "Label", parent=styles["Normal"],
            fontSize=10, leading=14, spaceAfter=2,
            textColor=HexColor("#64748B"),
        )
        s_value = ParagraphStyle(
            "Value", parent=styles["Normal"],
            fontSize=10, leading=14, spaceAfter=6,
            textColor=HexColor("#0F172A"),
        )
        s_bullet = ParagraphStyle(
            "BulletItem", parent=styles["Normal"],
            fontSize=10, leading=14, spaceAfter=4,
            textColor=HexColor("#334155"),
            leftIndent=16, bulletIndent=4,
        )
        s_numbered = ParagraphStyle(
            "NumberedItem", parent=styles["Normal"],
            fontSize=10, leading=14, spaceAfter=5,
            textColor=HexColor("#334155"),
            leftIndent=20, bulletIndent=4,
        )
        s_excerpt = ParagraphStyle(
            "Excerpt", parent=styles["Normal"],
            fontSize=9, leading=13, spaceAfter=4,
            textColor=HexColor("#475569"),
            leftIndent=12, rightIndent=12,
            borderPadding=(6, 6, 6, 6),
            backColor=HexColor("#F8FAFC"),
        )
        s_small = ParagraphStyle(
            "SmallGrey", parent=styles["Normal"],
            fontSize=8, leading=11, spaceAfter=2,
            textColor=HexColor("#94A3B8"),
        )
        s_disclaimer = ParagraphStyle(
            "Disclaimer", parent=styles["Normal"],
            fontSize=8, leading=11, spaceAfter=12,
            textColor=HexColor("#94A3B8"),
            alignment=TA_CENTER,
        )
        s_badge = ParagraphStyle(
            "Badge", parent=styles["Normal"],
            fontSize=13, leading=18, spaceAfter=4,
            alignment=TA_CENTER,
        )

        elements = []

        # ========== HEADER ==========
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("AI Governance Risk Classifier", s_disclaimer))
        elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#CBD5E1"), spaceAfter=12))
        elements.append(Paragraph(_escape_xml(report.title), s_report_title))

        gen_dt = report.generated_at
        try:
            dt_obj = datetime.fromisoformat(gen_dt)
            gen_dt = dt_obj.strftime("%B %d, %Y at %I:%M %p")
        except Exception:
            pass
        elements.append(Paragraph(f"Generated: {gen_dt}", s_subtitle))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=6))

        # ========== RISK CLASSIFICATION BADGE ==========
        bg_hex, txt_hex = _get_risk_color(report.classification)
        risk_data = [
            [
                Paragraph(
                    f'<font color="{txt_hex}"><b>{_escape_xml(report.classification)}</b></font>',
                    s_badge,
                ),
            ],
            [
                Paragraph(
                    f'<font color="{txt_hex}">Confidence: {report.confidence_score:.0%}</font>',
                    s_small,
                ),
            ],
        ]
        risk_table = Table(risk_data, colWidths=[page_w - 100])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor(bg_hex)),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        elements.append(risk_table)
        elements.append(Spacer(1, 14))

        # ========== USE CASE SUMMARY ==========
        elements.append(Paragraph("1. Use Case Summary", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        for line in report.use_case_summary.split("\n"):
            clean = line.replace("**", "").strip()
            if clean:
                if ":" in clean:
                    label, val = clean.split(":", 1)
                    elements.append(Paragraph(
                        f'<font color="#64748B">{_escape_xml(label.strip())}:</font> '
                        f'<font color="#0F172A"><b>{_escape_xml(val.strip())}</b></font>',
                        s_body,
                    ))
                else:
                    elements.append(Paragraph(_escape_xml(clean), s_body))

        # ========== COMPLIANCE FLAGS ==========
        elements.append(Paragraph("2. Compliance Flags", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        if report.compliance_concerns:
            for concern in report.compliance_concerns:
                elements.append(Paragraph(
                    f'<bullet>&bull;</bullet> <font color="#DC2626"><b>{_escape_xml(concern)}</b></font>',
                    s_bullet,
                ))
        else:
            elements.append(Paragraph(
                '<i>No specific compliance concerns were flagged.</i>', s_body
            ))

        # ========== SUMMARY RATIONALE ==========
        elements.append(Paragraph("3. Summary Rationale", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        elements.append(Paragraph(_escape_xml(report.explanation), s_body))

        # ========== REGULATORY CITATIONS & EVIDENCE ==========
        elements.append(Paragraph("4. Retrieved Regulatory Citations", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        if report.evidence:
            for idx, source in enumerate(report.evidence, 1):
                page_info = f"  |  Page {source.page_number}" if source.page_number else ""
                elements.append(Paragraph(
                    f'<b>[{_escape_xml(source.citation_id)}] {_escape_xml(source.document)}</b>'
                    f' &mdash; {_escape_xml(source.article_or_section)}'
                    f'{_escape_xml(page_info)}',
                    s_subsection,
                ))
                excerpt_text = source.excerpt[:400]
                elements.append(Paragraph(
                    f'<i>&ldquo;{_escape_xml(excerpt_text)}&rdquo;</i>',
                    s_excerpt,
                ))
                trigger = getattr(source, 'trigger_reason', None)
                if trigger:
                    elements.append(Paragraph(
                        f'<font color="#DC2626"><b>Why this applies:</b></font> {_escape_xml(trigger)}',
                        s_body,
                    ))
                elements.append(Paragraph(
                    f'Relevance Score: {source.relevance_score:.2f}',
                    s_small,
                ))
                elements.append(Spacer(1, 6))
        else:
            elements.append(Paragraph(
                '<i>No regulatory documents were retrieved for this assessment. '
                'Analysis was based on general taxonomy rules.</i>',
                s_body,
            ))

        # ========== ACTIONABLE INSIGHTS / RECOMMENDED NEXT STEPS ==========
        elements.append(Paragraph("5. Actionable Insights / Recommended Next Steps", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        if report.recommended_mitigations:
            for i, rec in enumerate(report.recommended_mitigations, 1):
                elements.append(Paragraph(
                    f'<b>{i}.</b>  {_escape_xml(rec)}',
                    s_numbered,
                ))
        else:
            elements.append(Paragraph(
                '<i>No specific recommendations generated.</i>', s_body
            ))

        # ========== OBLIGATIONS & EVIDENCE CHECKLIST ==========
        elements.append(Paragraph("6. Required Evidence Checklist & Gap Repository", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        
        if report.evidence_checklist:
            for item in report.evidence_checklist:
                status_color = "#16A34A" if item.status == "present" else "#DC2626"
                status_text = "PRESENT" if item.status == "present" else "GAP"
                elements.append(Paragraph(
                    f'<b>{_escape_xml(item.article_ref)}:</b> {_escape_xml(item.item)} '
                    f'<font color="{status_color}"><b>[{status_text}]</b></font>',
                    s_bullet,
                ))
        else:
            elements.append(Paragraph('<i>No specific evidence items required for this risk tier.</i>', s_body))
        
        # ========== AUDIT-READINESS SUMMARY ==========
        elements.append(Paragraph("7. Audit-Readiness Summary", s_section))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#E2E8F0"), spaceAfter=8))
        audit_summary = _build_audit_readiness_summary(report)
        # Render inside a light table for visual emphasis
        audit_data = [[Paragraph(_escape_xml(audit_summary), s_body)]]
        audit_table = Table(audit_data, colWidths=[page_w - 120])
        audit_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F0F9FF")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            ("LINEBELOW", (0, 0), (-1, -1), 0, HexColor("#F0F9FF")),
            ("BOX", (0, 0), (-1, -1), 0.5, HexColor("#BAE6FD")),
        ]))
        elements.append(audit_table)

        # ========== FOOTER SECTION ==========
        elements.append(Spacer(1, 24))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#CBD5E1"), spaceAfter=8))
        elements.append(Paragraph(
            f'Assessment ID: {report.assessment_id}  &nbsp;&nbsp;|&nbsp;&nbsp;  Report ID: {report.id}',
            s_small,
        ))
        elements.append(Paragraph(
            '<b>Disclaimer:</b> ' + _escape_xml(report.disclaimer),
            s_disclaimer,
        ))

        # ========== BUILD PDF ==========
        doc.build(elements, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
        return buffer.getvalue()

    except ImportError:
        # Fallback: return markdown as plain text PDF
        md = export_markdown(report)
        return md.encode("utf-8")


def save_report(report: ReportOutput, output_dir: str, formats: list = None) -> dict:
    """Save report to files in specified formats."""
    if formats is None:
        formats = ["json", "markdown"]
    
    os.makedirs(output_dir, exist_ok=True)
    saved = {}
    base_name = f"report_{report.assessment_id[:8]}"
    
    if "json" in formats:
        path = os.path.join(output_dir, f"{base_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(export_json(report))
        saved["json"] = path
    
    if "markdown" in formats:
        path = os.path.join(output_dir, f"{base_name}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(export_markdown(report))
        saved["markdown"] = path
    
    if "pdf" in formats:
        path = os.path.join(output_dir, f"{base_name}.pdf")
        pdf_bytes = export_pdf_bytes(report)
        with open(path, "wb") as f:
            f.write(pdf_bytes)
        saved["pdf"] = path
    
    return saved
