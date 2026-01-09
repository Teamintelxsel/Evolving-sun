# Dual Certification Roadmap: SOC 2 Type II + ISO 27001

> **Investment Required**: $30K-$150K | **Timeline**: 6-12 months | **Expected ROI**: 18 months

---

## Executive Summary

This roadmap outlines the path to achieving **SOC 2 Type II** and **ISO 27001** certifications, which are table stakes for enterprise AI platforms in 2025. Additionally, we prepare for **ISO 42001** (AI Management System) and **EU AI Act** compliance.

---

## 🎯 SOC 2 Type II Certification

### Overview
- **Purpose**: Trust Service Criteria compliance (Security, Availability, Processing Integrity, Confidentiality, Privacy)
- **Timeline**: 6-12 months
- **Investment**: $30K-$100K
- **Auditor**: Big 4 or recognized CPA firm (e.g., Deloitte, PwC, EY, KPMG)

### Timeline & Milestones

#### Month 1-2: Gap Analysis & Scoping
- [ ] **Week 1-2**: Select SOC 2 auditor
  - Request proposals from 3+ certified auditors
  - Compare costs and timelines
  - Sign engagement letter
- [ ] **Week 3-4**: Conduct readiness assessment
  - Document current controls
  - Identify gaps against TSC
  - Prioritize remediation efforts
- [ ] **Week 5-6**: Define scope
  - Determine which trust service criteria to include
  - Map in-scope systems and processes
  - Document system boundaries
- [ ] **Week 7-8**: Create remediation plan
  - Assign owners to each gap
  - Set deadlines
  - Allocate resources

**Deliverables**:
- Gap analysis report
- SOC 2 scope document
- Remediation project plan

---

#### Month 3-4: Control Implementation (General)
- [ ] **Security (Required)**
  - [ ] Access control policies (RBAC, MFA)
  - [ ] Network security (firewalls, IDS/IPS)
  - [ ] Encryption (at rest: AES-256, in transit: TLS 1.3)
  - [ ] Vulnerability management (quarterly scans, patch SLA)
  - [ ] Incident response plan
  - [ ] Security awareness training
  
- [ ] **Availability (Recommended)**
  - [ ] 99.9% uptime SLA
  - [ ] Redundant infrastructure
  - [ ] Backup and disaster recovery (RPO: 1 hour, RTO: 4 hours)
  - [ ] Capacity planning
  - [ ] Performance monitoring
  
- [ ] **Processing Integrity (Optional)**
  - [ ] Data validation controls
  - [ ] Error handling and logging
  - [ ] Quality assurance processes
  - [ ] Change management procedures
  
- [ ] **Confidentiality (Recommended for AI)**
  - [ ] Data classification policy
  - [ ] Confidential data handling procedures
  - [ ] NDA management
  - [ ] Secure disposal of confidential data
  
- [ ] **Privacy (If handling PII)**
  - [ ] Privacy policy
  - [ ] Consent management
  - [ ] Data subject rights (access, deletion)
  - [ ] Privacy by design

**Deliverables**:
- Documented control procedures
- Control evidence collection process
- Policies and standards library

---

#### Month 5-6: AI-Specific Controls
- [ ] **Model Governance**
  - [ ] Model development lifecycle policy
  - [ ] Model approval and deployment process
  - [ ] Model performance monitoring
  - [ ] Model rollback procedures
  - [ ] Model versioning and registry
  
- [ ] **Training Data Provenance**
  - [ ] Data lineage tracking
  - [ ] Data quality validation
  - [ ] Bias detection and mitigation
  - [ ] Data retention and deletion
  - [ ] Data source verification
  
- [ ] **API Security**
  - [ ] API authentication (OAuth 2.0, JWT)
  - [ ] Rate limiting and throttling
  - [ ] Input validation and sanitization
  - [ ] API audit logging
  - [ ] API versioning and deprecation
  
- [ ] **Agent Security**
  - [ ] Zero-trust architecture implementation
  - [ ] Agent identity verification (DID/VC)
  - [ ] Just-in-time privileged access
  - [ ] Behavioral monitoring and anomaly detection
  - [ ] Multi-agent collusion prevention

**Deliverables**:
- AI governance framework document
- Model management procedures
- API security standards

---

#### Month 7-9: Pre-Audit Readiness
- [ ] **Control Testing**
  - [ ] Internal control testing (sample 25+ instances per control)
  - [ ] Document test results
  - [ ] Remediate failed tests
  - [ ] Re-test until pass rate ≥95%
  
- [ ] **Evidence Collection**
  - [ ] Automate evidence collection where possible
  - [ ] Centralize evidence repository
  - [ ] Organize by control objective
  - [ ] Validate completeness
  
- [ ] **Documentation Review**
  - [ ] Ensure all policies are approved and dated
  - [ ] Verify procedures match actual practices
  - [ ] Update organizational charts
  - [ ] Review vendor contracts for SOC 2 clauses
  
- [ ] **Readiness Assessment**
  - [ ] Internal audit or external pre-assessment
  - [ ] Address findings
  - [ ] Management review and sign-off

**Deliverables**:
- Control test results
- Evidence package (organized)
- Readiness assessment report

---

#### Month 10-12: Type II Audit (12-Month Observation Period)
- [ ] **Kickoff (Month 10)**
  - [ ] Audit planning meeting
  - [ ] Provide system description
  - [ ] Schedule fieldwork
  
- [ ] **Fieldwork (Month 10-11)**
  - [ ] Auditor tests control design
  - [ ] Auditor tests control operating effectiveness
  - [ ] Respond to auditor requests
  - [ ] Provide evidence on demand
  
- [ ] **Remediation (Month 11)**
  - [ ] Address auditor findings
  - [ ] Implement corrective actions
  - [ ] Re-test if needed
  
- [ ] **Reporting (Month 12)**
  - [ ] Receive draft SOC 2 report
  - [ ] Management response to exceptions
  - [ ] Receive final SOC 2 Type II report
  - [ ] Publish to customers (gated access)

**Deliverables**:
- SOC 2 Type II Report
- Management assertion letter
- Customer-facing SOC 2 summary

---

## 🌍 ISO 27001 Certification

### Overview
- **Purpose**: International standard for Information Security Management System (ISMS)
- **Timeline**: 6-12 months
- **Investment**: $50K-$150K
- **Certification Body**: Accredited by national body (e.g., ANAB, UKAS)

### Timeline & Milestones

#### Month 1-2: ISMS Design & Risk Assessment
- [ ] **Week 1-2**: Leadership commitment
  - [ ] Appoint Information Security Manager
  - [ ] Define ISMS scope
  - [ ] Allocate budget and resources
  
- [ ] **Week 3-4**: Context of the organization
  - [ ] Identify internal/external issues
  - [ ] Identify interested parties (customers, regulators, employees)
  - [ ] Determine ISMS scope boundaries
  
- [ ] **Week 5-6**: Information security policy
  - [ ] Draft top-level security policy
  - [ ] Management review and approval
  - [ ] Communicate to organization
  
- [ ] **Week 7-8**: Risk assessment
  - [ ] Asset inventory (hardware, software, data, people)
  - [ ] Threat and vulnerability identification
  - [ ] Risk analysis (likelihood × impact)
  - [ ] Risk evaluation (risk appetite)
  - [ ] Risk treatment plan (accept, mitigate, transfer, avoid)

**Deliverables**:
- ISMS scope statement
- Information security policy
- Risk assessment report
- Risk treatment plan

---

#### Month 3-4: AI-Specific ISMS Controls
- [ ] **AI Data Residency**
  - [ ] Map data flows (training, inference, storage)
  - [ ] Ensure compliance with data localization laws (GDPR, etc.)
  - [ ] Implement data sovereignty controls
  - [ ] Document cross-border data transfers
  
- [ ] **Model Lifecycle Management**
  - [ ] Model development controls (secure coding, peer review)
  - [ ] Model validation and testing
  - [ ] Model deployment approval process
  - [ ] Model monitoring and maintenance
  - [ ] Model decommissioning
  
- [ ] **Vendor Integration Security**
  - [ ] Vendor risk assessment (OpenAI, Anthropic, Google, Meta)
  - [ ] Vendor contracts with security SLAs
  - [ ] Vendor access controls
  - [ ] Vendor audit rights
  - [ ] Vendor incident notification

**Deliverables**:
- AI data flow diagrams
- Model lifecycle procedures
- Vendor security requirements

---

#### Month 5-6: Control Implementation (ISO 27001:2022 Annex A)
- [ ] **Organizational Controls (A.5)**
  - [ ] Security policies
  - [ ] Roles and responsibilities
  - [ ] Segregation of duties
  - [ ] Management responsibilities
  
- [ ] **People Controls (A.6)**
  - [ ] Screening procedures
  - [ ] Terms of employment (security clauses)
  - [ ] Security awareness training
  - [ ] Disciplinary process
  
- [ ] **Physical Controls (A.7)**
  - [ ] Secure areas (data center access)
  - [ ] Physical entry controls
  - [ ] Equipment security
  - [ ] Secure disposal
  
- [ ] **Technological Controls (A.8)**
  - [ ] User access management
  - [ ] Privileged access rights
  - [ ] Information access restriction
  - [ ] Cryptography
  - [ ] Secure development lifecycle
  - [ ] Vulnerability management
  - [ ] Logging and monitoring
  - [ ] Backup
  - [ ] Malware protection
  - [ ] Network security
  - [ ] Web filtering

**Deliverables**:
- 93 Annex A controls implemented
- Statement of Applicability (SoA)
- Control implementation evidence

---

#### Month 7-9: Internal Audits & Management Review
- [ ] **Internal Audit Program**
  - [ ] Develop internal audit plan
  - [ ] Train internal auditors
  - [ ] Conduct internal audits (sample all areas)
  - [ ] Document findings and nonconformities
  - [ ] Corrective action plans
  - [ ] Verify corrective actions
  
- [ ] **Management Review**
  - [ ] Review ISMS performance
  - [ ] Review risk assessment results
  - [ ] Review internal audit findings
  - [ ] Review incident reports
  - [ ] Identify improvement opportunities
  - [ ] Management decisions and actions

**Deliverables**:
- Internal audit reports
- Corrective action register
- Management review minutes

---

#### Month 10-12: Certification Audit
- [ ] **Stage 1 Audit (Documentation Review)**
  - [ ] Provide ISMS documentation to auditor
  - [ ] Auditor reviews for completeness
  - [ ] Address stage 1 findings
  
- [ ] **Stage 2 Audit (On-Site Assessment)**
  - [ ] Auditor tests control implementation
  - [ ] Auditor interviews staff
  - [ ] Auditor reviews evidence
  - [ ] Address nonconformities
  
- [ ] **Certification Decision**
  - [ ] Receive audit report
  - [ ] Resolve any minor nonconformities
  - [ ] Certification body issues ISO 27001 certificate
  - [ ] Publish certificate (website, LinkedIn)

**Deliverables**:
- ISO 27001 certificate (3-year validity)
- Certification audit report
- Public certificate announcement

---

## 🤖 ISO 42001 Preparation (AI Management System)

### Overview
- **Purpose**: First international standard for AI management systems
- **Status**: Published October 2023, early adoption phase
- **Timeline**: 6-12 months (after ISO 27001)
- **Investment**: $30K-$75K

### Key Requirements
- [ ] **AI Governance Framework**
  - [ ] AI ethics policy
  - [ ] AI risk management
  - [ ] AI accountability and oversight
  - [ ] AI performance metrics
  
- [ ] **Model Cards and Transparency**
  - [ ] Model card for each AI model
    - Intended use
    - Training data description
    - Performance metrics
    - Limitations and biases
    - Ethical considerations
  - [ ] Algorithmic transparency documentation
  - [ ] Explainability mechanisms
  
- [ ] **Stakeholder Management**
  - [ ] Identify AI stakeholders
  - [ ] Stakeholder engagement plan
  - [ ] Feedback mechanisms
  - [ ] Dispute resolution

**Deliverables**:
- AI management system documentation
- Model cards library
- ISO 42001 readiness assessment

---

## 🇪🇺 EU AI Act Compliance (by August 2026)

### Overview
- **Purpose**: Regulatory compliance for AI systems in EU market
- **Deadline**: August 2, 2026 (full application)
- **Risk Level**: High-risk AI (autonomous agents with significant impact)

### Compliance Requirements
- [ ] **High-Risk AI Conformity Assessment**
  - [ ] Classify AI system risk level
  - [ ] Conduct conformity assessment
  - [ ] Third-party audit (if required)
  - [ ] CE marking (if required)
  - [ ] Registration in EU database
  
- [ ] **Transparency Requirements**
  - [ ] Inform users they're interacting with AI
  - [ ] Provide AI system information
  - [ ] Disclose AI-generated content
  - [ ] Right to explanation
  
- [ ] **Human Oversight Mechanisms**
  - [ ] Human-in-the-loop controls
  - [ ] Override capabilities
  - [ ] Stop functionality
  - [ ] Human review of high-stakes decisions
  
- [ ] **Data Governance**
  - [ ] Training data quality requirements
  - [ ] Bias detection and mitigation
  - [ ] Data lineage documentation
  - [ ] GDPR alignment
  
- [ ] **Technical Documentation**
  - [ ] System design and architecture
  - [ ] Risk assessment
  - [ ] Testing and validation results
  - [ ] Monitoring and logging

**Deliverables**:
- EU AI Act compliance report
- High-risk AI system registration
- Technical documentation package

---

## 📊 Certification Roadmap Gantt Chart

```
Month | SOC 2 Type II           | ISO 27001              | ISO 42001 | EU AI Act
------|-------------------------|------------------------|-----------|----------
1     | Gap Analysis            | ISMS Design            |           |
2     | Scoping                 | Risk Assessment        |           |
3     | Control Implement (Gen) | AI Controls            |           |
4     | Control Implement (Gen) | AI Controls            |           |
5     | AI Controls             | Annex A Controls       |           |
6     | AI Controls             | Annex A Controls       |           |
7     | Pre-Audit Readiness     | Internal Audits        |           |
8     | Pre-Audit Readiness     | Internal Audits        |           |
9     | Pre-Audit Readiness     | Management Review      |           |
10    | Type II Audit Start     | Stage 1 Audit          | Prep      | Prep
11    | Fieldwork               | Stage 2 Audit          | Prep      | Prep
12    | Reporting               | Certification          | Prep      | Prep
13-18 | Surveillance (annual)   | Surveillance (annual)  | Implement | Implement
19-24 |                         |                        | Certify   | Compliance
```

---

## 💰 Budget Breakdown

### SOC 2 Type II: $30K-$100K
- Auditor fees: $20K-$60K
- Consulting (optional): $10K-$30K
- Tools (GRC platform): $5K-$10K/year
- Internal labor: 500-1000 hours

### ISO 27001: $50K-$150K
- Certification body fees: $15K-$40K
- Consulting (optional): $20K-$60K
- Implementation: $15K-$50K
- Internal labor: 800-1500 hours

### ISO 42001: $30K-$75K
- Certification fees: $10K-$25K
- Consulting: $10K-$30K
- Implementation: $10K-$20K
- Internal labor: 400-800 hours

### EU AI Act: $20K-$50K
- Legal counsel: $10K-$25K
- Technical assessment: $5K-$15K
- Implementation: $5K-$10K
- Internal labor: 300-600 hours

**Total Investment**: $130K-$375K over 24 months

---

## 📈 Return on Investment (ROI)

### Direct Benefits
- **Revenue Increase**: 30-50% from enterprise customers requiring certifications
- **Deal Velocity**: 40% faster sales cycles (certification removes blocker)
- **Contract Size**: 25% larger deals with certified vendors
- **Win Rate**: 20% improvement in competitive situations

### Indirect Benefits
- **Brand Trust**: Industry recognition
- **Competitive Moat**: Barrier to entry for competitors
- **Operational Excellence**: Improved security and processes
- **Regulatory Preparedness**: Avoid fines and delays

### ROI Timeline
- **Month 6**: First enterprise deals with certification requirement
- **Month 12**: $25K MRR from certification-requiring customers
- **Month 18**: Break-even on certification investment
- **Month 24**: 3x return on investment

---

## 🎯 Success Metrics

### Certification Metrics
- [ ] SOC 2 Type II report received (Month 12)
- [ ] ISO 27001 certificate issued (Month 12)
- [ ] Zero critical findings in audits
- [ ] ISO 42001 certification (Month 24)
- [ ] EU AI Act compliance (Month 24)

### Business Metrics
- [ ] 50% of enterprise deals require SOC 2
- [ ] 30% of deals require ISO 27001
- [ ] 10% contract value increase with certifications
- [ ] 2+ compliance-based competitive wins per quarter

### Operational Metrics
- [ ] 99.9% uptime achieved
- [ ] <15 minute incident response time
- [ ] 100% employee security training completion
- [ ] Zero security incidents during audit period

---

## 📚 Resources & Tools

### GRC Platforms (recommended)
- **Vanta**: $3K-$10K/year, automated SOC 2/ISO 27001
- **Drata**: $2K-$8K/year, continuous compliance
- **Secureframe**: $2K-$8K/year, compliance automation
- **Manual**: $0, spreadsheets and docs (not recommended)

### Recommended Auditors
- **SOC 2**: Big 4 (Deloitte, PwC, EY, KPMG) or Richey May, A-LIGN
- **ISO 27001**: BSI, SGS, TÜV, NQA, A-LIGN

### Training Resources
- ISACA: Certified Information Security Manager (CISM)
- (ISC)²: Certified Information Systems Security Professional (CISSP)
- ISO 27001 Lead Implementer course

---

**Last Updated**: January 2025
**Owner**: Chief Information Security Officer (CISO)
**Review Frequency**: Quarterly
