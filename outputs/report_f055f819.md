# Compliance Risk Assessment: Clearview AI — Facial Recognition & Biometric Identification Platform

*Generated: 2026-04-19T18:38:18.902694*

---

## Disclaimer

> This is a compliance risk assessment for decision-support purposes only. It does not constitute legal advice.

---

## Use Case Summary

**AI System:** Clearview AI — Facial Recognition & Biometric Identification Platform
**Description:** Clearview AI is a commercial AI-powered facial recognition platform founded in 2017 and headquartered in New York, USA. The system operates by autonomously scraping billions of publicly available images from the open internet — including social media platforms (Facebook, Instagram, LinkedIn, Twitter), news websites, mugshot databases, online videos, and other publicly indexed web pages — without the knowledge or consent of the individuals depicted.

The core AI engine converts each scraped facial image into a unique numerical biometric hash (a mathematical representation of facial geometry) using deep learning convolutional neural networks. These hashes are indexed into a proprietary database that, as of 2024, contains over 50 billion facial images sourced from individuals worldwide, including EU citizens and minors.

The platform offers a reverse-image search service: a client (typically a law enforcement officer, intelligence analyst, or private investigator) uploads an unknown face — sourced from CCTV footage, a photograph, or a video frame — and the system matches it against its database to return the identity of the individual, along with associated metadata such as image source URLs, geolocation tags, social media profiles, and contextual information linked to the original images.

The system operates with no user consent mechanism, no opt-out facility for data subjects, no transparency notices to individuals whose data is stored, and no legal basis for collection or processing under EU law. It has been commercially deployed for use by thousands of law enforcement agencies primarily in the United States, as well as private sector clients globally.
**Domain:** Law Enforcement
**Personal Data:** Yes
**Sensitive Data:** Yes
**Automated Decisions:** Yes
**Impacts Rights:** Yes

## Risk Classification

**Classification:** High Risk

**Confidence Score:** 85%

## Compliance Concerns

- ⚠️ Privacy Concern
- ⚠️ Fairness / Bias Concern
- ⚠️ Human Oversight Concern
- ⚠️ Lack of user consent mechanism
- ⚠️ No transparency notices to individuals
- ⚠️ No legal basis for data collection or processing

## Explanation

The Clearview AI platform is classified as high risk due to its use of facial recognition and biometric identification, which involves processing sensitive personal data without consent or legal basis, violating Article 9 and Article 10 of the EU AI Act. The system's operation raises significant privacy and fairness concerns, necessitating a comprehensive risk management system and human oversight measures as outlined in Articles 9, 10, 11, and 14. Compliance concerns identified: Privacy Concern, Fairness / Bias Concern, Human Oversight Concern, Lack of user consent mechanism, No transparency notices to individuals, No legal basis for data collection or processing. Classification confidence: 85%

## Supporting Evidence

### [source_2] EU_AI_ACT_2024.pdf — Article 71 (Page 82)

> used for biometric categorisation and emotion recognition, which are permitted by law to detect, prevent or investigate
criminal offences, subject to appropriate safeguards for the rights and freedoms of third parties, and in accordance with
Union law.
4. Deployers of an AI system that generates or ...

**Why this applies:** The use of AI systems that create or expand facial recognition databases through the untargeted scraping of facial images from the internet or CCTV footage should be prohibited because that practice adds to the feeling of mass surveillance and can lead to gross violations of fundamental rights, including the right to privacy.

*Relevance Score: 0.65*

### [source_3] EU_AI_ACT_2024.pdf — Article 9 (Page 69)

> such post-remote biometric identification systems.
This paragraph is without prejudice to Article 9 of Regulation (EU) 2016/679 and Article 10 of Directive (EU) 2016/680
for the processing of biometric data.
Regardless of the purpose or deployer, each use of such high-risk AI systems shall be docume...

**Why this applies:** Annex III (high-risk use-case area) — excerpt mentions "biometric" which matches description text: "…recognition & biometric identification…"

*Relevance Score: 0.60*

### [source_4] EU_AI_ACT_2024.pdf — Article 16 (Page 12)

> example on the basis of known trafficking routes.
(43) The placing on the market, the putting into service for that specific purpose, or the use of AI systems that create or
expand facial recognition databases through the untargeted scraping of facial images from the internet or CCTV
footage, should...

**Why this applies:** Relevant to "Impacts Rights or Opportunities" checkbox — excerpt discusses: "fundamental right"

*Relevance Score: 0.57*

### [source_5] EU_AI_ACT_2024.pdf — Page 5 (Page 5)

> product on him or herself and help the consumer to make a purchase decision. Filters used on online social network
services which categorise facial or body features to allow users to add or modify pictures or videos could also be
considered to be ancillary feature as such filter cannot be used witho...

**Why this applies:** Annex III (high-risk use-case area) — excerpt mentions "biometric" which matches description text: "…recognition & biometric identification…"

*Relevance Score: 0.57*

### [source_6] EU_AI_ACT_2024.pdf — Article 9 (Page 69)

> EN
OJ L, 12.7.2024
In no case shall such high-risk AI system for post-remote biometric identification be used for law enforcement purposes in
an untargeted way, without any link to a criminal offence, a criminal proceeding, a genuine and present or genuine and
foreseeable threat of a criminal offenc...

**Why this applies:** In no case shall such high-risk AI system for post-remote biometric identification be used for law enforcement purposes in an untargeted way, without any link to a criminal offence.

*Relevance Score: 0.57*

### [source_7] EU_AI_ACT_2024.pdf — Page 9 (Page 9)

> prohibition should not affect lawful evaluation practices of natural persons that are carried out for a specific purpose
in accordance with Union and national law.
(32) The use of AI systems for ‘real-time’ remote biometric identification of natural persons in publicly accessible spaces
for the purp...

**Why this applies:** The use of AI systems for ‘real-time’ remote biometric identification of natural persons in publicly accessible spaces for the purpose of law enforcement is particularly intrusive to the rights and freedoms of the concerned persons.

*Relevance Score: 0.56*

### [source_8] EU_AI_ACT_2024.pdf — Article 114 (Page 2)

> enforcement and of the use of AI systems of biometric categorisation for the purpose of law enforcement, it is
appropriate to base this Regulation, in so far as those specific rules are concerned, on Article 16 TFEU. In light of
those specific rules and the recourse to Article 16 TFEU, it is appropr...

**Why this applies:** Annex III (high-risk use-case area) — excerpt mentions "biometric" which matches description text: "…recognition & biometric identification…"

*Relevance Score: 0.56*

## Citations

- [source_2] EU_AI_ACT_2024.pdf, Article 71, Page 82
- [source_3] EU_AI_ACT_2024.pdf, Article 9, Page 69
- [source_4] EU_AI_ACT_2024.pdf, Article 16, Page 12
- [source_5] EU_AI_ACT_2024.pdf, Page 5, Page 5
- [source_6] EU_AI_ACT_2024.pdf, Article 9, Page 69
- [source_7] EU_AI_ACT_2024.pdf, Page 9, Page 9
- [source_8] EU_AI_ACT_2024.pdf, Article 114, Page 2

## Recommended Mitigations

1. Establish and document a comprehensive Risk Management System (RMS) covering the entire lifecycle of the AI system as required by Article 9.
2. Develop and implement a Data Governance Policy and conduct a Quality Assessment Report to ensure compliance with data governance requirements under Article 10.
3. Prepare comprehensive Technical Documentation in accordance with Annex IV before placing the system on the market, as mandated by Article 11.
4. Implement human oversight measures, including human-in-the-loop operational guidelines and evidence of user interface/user experience (UI/UX) considerations, to comply with Article 14.

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

*Assessment ID: f055f819-b9ec-4805-a574-e2b8d6321d34*
*Report ID: 8a2f77c5-78aa-48b5-9977-d7906cbeee0d*