# Compliance Risk Assessment: Automated Resume Screening Tool

*Generated: 2026-04-19T18:26:26.724340*

---

## Disclaimer

> This is a compliance risk assessment for decision-support purposes only. It does not constitute legal advice.

---

## Use Case Summary

**AI System:** Automated Resume Screening Tool
**Description:** An AI system that uses machine learning to automatically screen and rank job applicants based on their resumes. The system processes personal data including work history, education, and demographic information. It makes automated decisions about which candidates advance to interviews with no human review.
**Domain:** Employment
**Personal Data:** Yes
**Sensitive Data:** Yes
**Automated Decisions:** Yes
**Impacts Rights:** Yes

## Risk Classification

**Classification:** High Risk

**Confidence Score:** 85%

## Compliance Concerns

- ⚠️ Human Oversight Concern
- ⚠️ Privacy Concern
- ⚠️ Fairness / Bias Concern

## Explanation

The Automated Resume Screening Tool is classified as high risk due to its use in employment decisions, which directly affects individuals' rights and opportunities. According to Article 1, AI systems used for recruitment and selection of natural persons are considered high-risk, necessitating compliance with Articles 9, 10, 11, and 14 regarding risk management, data governance, technical documentation, and human oversight. Compliance concerns identified: Human Oversight Concern, Privacy Concern, Fairness / Bias Concern. Classification confidence: 85%

## Supporting Evidence

### [source_1] eu_ai_act_excerpts.txt — Article 1 (Page 1)

> 4. Employment, workers management and access to self-employment: AI systems intended to be used for the recruitment or selection of natural persons, for making decisions affecting terms of work-related relationships, promotion or termination of work-related contractual relationships, for task alloca...

**Why this applies:** The AI system is intended for recruitment or selection of natural persons, which is explicitly mentioned in the description.

*Relevance Score: 0.68*

### [source_2] EU_AI_ACT_2024.pdf — Article 6 (Page 127)

> will receive or will be able to access, in the context of or within educational and vocational training institutions
at all levels;
(d) AI systems intended to be used for monitoring and detecting prohibited behaviour of students during tests in the
context of or within educational and vocational tra...

**Why this applies:** Annex III (high-risk use-case area) — excerpt mentions "education" which matches description text: "…work history, education, and demograph…"

*Relevance Score: 0.61*

### [source_4] EU_AI_ACT_2024.pdf — Page 17 (Page 17)

> assessment of personality traits and characteristics or the past criminal behaviour of natural persons or groups, for
profiling in the course of detection, investigation or prosecution of criminal offences. AI systems specifically
intended to be used for administrative proceedings by tax and customs...

**Why this applies:** Article 50 (transparency obligation) — excerpt mentions "inform" which matches description text: "…nd demographic information. it makes…"

*Relevance Score: 0.60*

### [source_5] eu_ai_act_excerpts.txt — Article 1 (Page 1)

> 3. Education and vocational training: AI systems intended to be used to determine access to or admission to educational and vocational training institutions; to evaluate learning outcomes; to assess the appropriate level of education for an individual; to monitor and detect prohibited behaviour of s...

**Why this applies:** The system processes personal data and makes automated decisions affecting employment, aligning with the high-risk classification criteria.

*Relevance Score: 0.58*

### [source_7] EU_AI_ACT_2024.pdf — Page 14 (Page 14)

> be understood to be an AI system that does not have an impact on the substance, and thereby the outcome, of
decision-making, whether human or automated. An AI system that does not materially influence the outcome of
decision-making could include situations in which one or more of the following condi...

**Why this applies:** Relevant to "Impacts Rights or Opportunities" checkbox — excerpt discusses: "impact"

*Relevance Score: 0.56*

### [source_8] EU_AI_ACT_2024.pdf — Article 6 (Page 127)

> 3. Education and vocational training:
(a) AI systems intended to be used to determine access or admission or to assign natural persons to educational and
vocational training institutions at all levels;
(b) AI systems intended to be used to evaluate learning outcomes, including when those outcomes ar...

**Why this applies:** Annex III (high-risk use-case area) — excerpt mentions "education" which matches description text: "…work history, education, and demograph…"

*Relevance Score: 0.55*

## Citations

- [source_1] eu_ai_act_excerpts.txt, Article 1, Page 1
- [source_2] EU_AI_ACT_2024.pdf, Article 6, Page 127
- [source_4] EU_AI_ACT_2024.pdf, Page 17, Page 17
- [source_5] eu_ai_act_excerpts.txt, Article 1, Page 1
- [source_7] EU_AI_ACT_2024.pdf, Page 14, Page 14
- [source_8] EU_AI_ACT_2024.pdf, Article 6, Page 127

## Recommended Mitigations

1. Establish and document a comprehensive Risk Management System (RMS) covering the entire lifecycle of the AI system as per Article 9.
2. Develop a Data Governance Policy and conduct a Quality Assessment Report to ensure compliance with Article 10.
3. Prepare comprehensive Technical Documentation in accordance with Annex IV before placing the system on the market, as required by Article 11.
4. Implement human oversight measures, including human-in-the-loop operational guidelines and evidence of user interface/user experience considerations, to comply with Article 14.
5. Conduct regular audits to assess the fairness and bias in the AI system's decision-making process.

## Legal Obligations

- **Article 9**: Establish, implement, document and maintain a risk management system.
  *Evidence Needed*: Documented Risk Management System (RMS) covering the entire lifecycle.
- **Article 10**: Data and data governance requirements.
  *Evidence Needed*: Data Governance Policy and Quality Assessment Report.
- **Article 11**: Technical documentation must be drawn up before the system is placed on the market.
  *Evidence Needed*: Comprehensive Technical Documentation as per Annex IV.
- **Article 14**: Human oversight measures.
  *Evidence Needed*: Human-in-the-loop operational guidelines and UI/UX evidence.

## Evidence Checklist & Gap Repository

| Item | Reference | Status |
| --- | --- | --- |
| Risk Management System documentation | Article 9 | ❌ GAP |
| Data Quality Assessment Report | Article 10 | ❌ GAP |
| Technical Documentation (Annex IV) | Article 11 | ❌ GAP |
| Human Oversight Operational Guidelines | Article 14 | ❌ GAP |

---

*Assessment ID: ad748a33-bebc-428f-a158-9dd518cc0649*
*Report ID: 58d6520a-76f7-4e38-a2f4-8cc817ed44a5*