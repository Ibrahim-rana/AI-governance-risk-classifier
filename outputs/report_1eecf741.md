# Compliance Risk Assessment: Clearview AI — Facial Recognition & Biometric Identification Platform

*Generated: 2026-04-19T17:41:24.587337*

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
System classification
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

## Explanation

The Clearview AI platform is classified as high risk due to its use of facial recognition technology that processes personal and sensitive data without user consent, violating fundamental rights under EU law. Article 9 mandates a documented risk management system, while Article 10 emphasizes data governance requirements, both of which are critical given the platform's extensive data collection practices and lack of transparency. Compliance concerns identified: Privacy Concern, Fairness / Bias Concern, Human Oversight Concern. Classification confidence: 85%

## Supporting Evidence

### [source_1] EU_AI_ACT_2024.pdf — Article 4 (Page 51)

> based solely on the profiling of a natural person or on assessing their personality traits and characteristics; this
prohibition shall not apply to AI systems used to support the human assessment of the involvement of a person in
a criminal activity, which is already based on objective and verifiabl...

**Why this applies:** The system's operation of scraping images without consent violates the prohibition on profiling based solely on personal data.

*Relevance Score: 0.65*

### [source_2] EU_AI_ACT_2024.pdf — Article 71 (Page 82)

> used for biometric categorisation and emotion recognition, which are permitted by law to detect, prevent or investigate
criminal offences, subject to appropriate safeguards for the rights and freedoms of third parties, and in accordance with
Union law.
4. Deployers of an AI system that generates or ...

**Why this applies:** The use of biometric categorization for law enforcement without appropriate safeguards raises concerns about rights and freedoms.

*Relevance Score: 0.65*

### [source_3] EU_AI_ACT_2024.pdf — Article 9 (Page 69)

> such post-remote biometric identification systems.
This paragraph is without prejudice to Article 9 of Regulation (EU) 2016/679 and Article 10 of Directive (EU) 2016/680
for the processing of biometric data.
Regardless of the purpose or deployer, each use of such high-risk AI systems shall be docume...

**Why this applies:** The lack of documentation for high-risk AI systems as required by Article 9 is evident in the system's deployment.

*Relevance Score: 0.60*

### [source_4] EU_AI_ACT_2024.pdf — Article 16 (Page 12)

> example on the basis of known trafficking routes.
(43) The placing on the market, the putting into service for that specific purpose, or the use of AI systems that create or
expand facial recognition databases through the untargeted scraping of facial images from the internet or CCTV
footage, should...

**Why this applies:** The practice of untargeted scraping of facial images contributes to mass surveillance and potential violations of privacy rights.

*Relevance Score: 0.57*

### [source_5] EU_AI_ACT_2024.pdf — Page 5 (Page 5)

> product on him or herself and help the consumer to make a purchase decision. Filters used on online social network
services which categorise facial or body features to allow users to add or modify pictures or videos could also be
considered to be ancillary feature as such filter cannot be used witho...

*Relevance Score: 0.57*

### [source_6] EU_AI_ACT_2024.pdf — Article 9 (Page 69)

> EN
OJ L, 12.7.2024
In no case shall such high-risk AI system for post-remote biometric identification be used for law enforcement purposes in
an untargeted way, without any link to a criminal offence, a criminal proceeding, a genuine and present or genuine and
foreseeable threat of a criminal offenc...

**Why this applies:** The system's use for law enforcement purposes without a link to specific criminal offenses violates the stipulations of Article 6.

*Relevance Score: 0.57*

### [source_7] EU_AI_ACT_2024.pdf — Page 9 (Page 9)

> prohibition should not affect lawful evaluation practices of natural persons that are carried out for a specific purpose
in accordance with Union and national law.
(32) The use of AI systems for ‘real-time’ remote biometric identification of natural persons in publicly accessible spaces
for the purp...

*Relevance Score: 0.56*

### [source_8] EU_AI_ACT_2024.pdf — Article 114 (Page 2)

> enforcement and of the use of AI systems of biometric categorisation for the purpose of law enforcement, it is
appropriate to base this Regulation, in so far as those specific rules are concerned, on Article 16 TFEU. In light of
those specific rules and the recourse to Article 16 TFEU, it is appropr...

*Relevance Score: 0.56*

## Citations

- [source_1] EU_AI_ACT_2024.pdf, Article 4, Page 51
- [source_2] EU_AI_ACT_2024.pdf, Article 71, Page 82
- [source_3] EU_AI_ACT_2024.pdf, Article 9, Page 69
- [source_4] EU_AI_ACT_2024.pdf, Article 16, Page 12
- [source_5] EU_AI_ACT_2024.pdf, Page 5, Page 5
- [source_6] EU_AI_ACT_2024.pdf, Article 9, Page 69
- [source_7] EU_AI_ACT_2024.pdf, Page 9, Page 9
- [source_8] EU_AI_ACT_2024.pdf, Article 114, Page 2

## Recommended Mitigations

1. Establish and implement a documented Risk Management System (RMS) covering the entire lifecycle of the AI system as required by Article 9.
2. Develop a Data Governance Policy and conduct a Quality Assessment Report to ensure compliance with Article 10.
3. Prepare comprehensive Technical Documentation in accordance with Annex IV before placing the system on the market, as mandated by Article 11.
4. Implement human oversight measures, including Human-in-the-loop operational guidelines and UI/UX evidence, to comply with Article 14.
5. Ensure transparency notices are provided to individuals whose data is processed and establish an opt-out facility to respect user rights.

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

*Assessment ID: 1eecf741-fb99-4bbe-9f20-2169ed2a6ec2*
*Report ID: 1a4160f6-75f0-4070-bf00-8a4ba47d0bd6*