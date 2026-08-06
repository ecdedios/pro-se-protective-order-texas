# TX Pro Se Protective Order Agent — Architecture Doc

## 1. Purpose & Positioning

An Azure-native AI agent that guides domestic violence survivors in Texas through preparing a pro se application for a protective order — intake, legal-procedure guidance (grounded in statute, not model memory), form completion, and connection to local resources.

**Portfolio goal:** demonstrate senior-level, end-to-end Azure AI engineering — RAG grounding, responsible-AI guardrails on a sensitive domain, secure handling of survivor data, and defensible architectural tradeoffs (including what was *left out* and why).

---

## 2. System Overview

```
Survivor
   │
   ▼
[Intake UI] ──(Container Apps)
   │  guided, trauma-informed Q&A
   ▼
[Agent Orchestrator] ──(Azure OpenAI)
   │  classifies case type, decides next question,
   │  requests grounded facts, never freelances legal advice
   ▼
[RAG Retrieval] ──(Azure AI Search)
   │  indexed: TX Family Code Title 4, county filing rules,
   │  official form instructions
   ▼
[Form Completion] ──(Document Intelligence, scoped to
   │                  parsing survivor-uploaded supporting docs
   │                  e.g. police reports — not the blank form itself)
   ▼
[Filled PDF + Filing Instructions + Local Resources
   + Hearing Prep Guide + Chronology Worksheet]
   │
   ▼
Survivor downloads / prints / takes to courthouse

Cross-cutting: Key Vault (secrets, encryption keys) · Fabric (de-identified usage analytics)
```

No Service Bus / Logic Apps in v1 — call chain is synchronous. See §6 for when that would change.

---

## 3. Component Breakdown

### 3.1 Intake (Azure Container Apps)
- Hosts the chat/form frontend and backend API
- Session-based, not persisted chat logs — only structured intake fields are stored
- Trauma-informed question design: no re-traumatizing phrasing, ability to pause/exit safely (quick-exit button, no browser history trace)

### 3.2 Agent Orchestrator (Azure OpenAI)
- Tool-calling agent: decides what info is missing, what to ask next, when intake is complete
- Classifies case type (family violence / dating violence / stalking) — determines which TX form and statute apply
- **Guardrail:** system prompt + retrieval constraint — agent answers procedural questions ("where do I file," "what happens next") only from retrieved sources; explicitly declines to give legal advice or predict case outcomes; surfaces a legal aid hotline for anything outside procedural scope

### 3.3 RAG Grounding (Azure AI Search)
- Index: TX Family Code Title 4 (Protective Orders), county-specific filing procedures, official form instructions
- Every procedural claim is retrieval-grounded and citable back to source — this is the centerpiece for demonstrating RAG competency
- Chunking strategy: statute sections + county rules indexed separately, retrieved and merged per query

### 3.4 Form Completion (Azure Document Intelligence)
- **Scoped use:** parsing survivor-uploaded supporting documents (e.g., a police report, prior order) to extract relevant facts/dates
- The blank TX Application for Protective Order itself uses a fixed field map (hardcoded), since it's a single known template — not a Document Intelligence use case
- Output: fields merged from intake + extracted doc facts → filled PDF

### 3.5 Security (Azure Key Vault)
- Auth to Azure OpenAI, AI Search, and Document Intelligence uses **managed identity** (`DefaultAzureCredential`) — Container Apps' system-assigned identity is granted access directly to each resource, so no API keys are issued or stored for those services in normal operation
- Key Vault holds what managed identity *can't* replace: encryption keys for any stored survivor PII, and any local-dev-only fallback API keys (never used in deployed environments)
- No secrets in code/config; local development uses `.env` (git-ignored) with the same variable names Key Vault would resolve in production

### 3.6 Analytics (Microsoft Fabric)
- Aggregated, de-identified metrics only: completion rate, drop-off point, most-requested county
- No individual survivor data enters this layer

### 3.7 Hearing Preparation
- **Generic "what to expect at your hearing" guide** — retrieval-grounded from official court self-help materials (same RAG pattern as §3.3), selected by case classification (family violence / dating violence / stalking). Not personalized, not case-specific content generation.
- **Chronology/organizing worksheet** — survivor enters their own account in their own words; the agent helps sequence it chronologically and flags standard elements a judge typically needs to hear (date, relationship, specific acts, reason for fear of future harm). The agent structures the survivor's input — it does not write or generate their testimony.
- **Deliberately excluded:** a personalized script for the agent to write on the survivor's behalf. This crosses from procedural support into content that resembles legal advice/case strategy (unauthorized-practice-of-law exposure), risks reading as coached testimony in court, and carries meaningful hallucination risk with no attorney-review step in the design. See design-decision note below.

> **Design decision worth calling out in interviews:** the marginal utility of a fully personalized script over the guide+worksheet combination is small for most users (the real barrier is fear/unfamiliarity with process, not literally lacking words), while the liability and courtroom-credibility risk increases sharply. This tradeoff — recognizing where "helpful" tips into "reckless" in a sensitive domain — is intentional and is a stronger signal of judgment than shipping the riskier feature.

---

## 4. Data & Privacy Design

- Minimize retention: intake data persists only long enough to generate the form, then purged (configurable TTL)
- No PII in application logs
- Encryption at rest (Key Vault-managed keys) and in transit
- Service-to-service auth via managed identity rather than long-lived API keys — reduces credential-leak surface, no keys to rotate/revoke for the core Azure services
- Clear survivor-facing statement of what is/isn't stored, and for how long
- This section matters as much to the portfolio story as the AI components — it signals product judgment, not just API usage

## 5. Responsible AI Guardrails

- Retrieval-grounded answers only for procedural/legal-process questions
- Explicit scope boundary: procedural guidance, not legal advice or outcome prediction
- Escalation path to legal aid / DV hotline surfaced for anything outside scope
- No case-outcome prediction, no advice on responding to alleged abuser

## 6. Deferred: Async / Event-Driven (v2 consideration)

Not included in v1 — current volume/latency doesn't justify it. Would revisit if:
- Traffic becomes spiky (e.g., a shelter network mass-shares the tool)
- A slow step is added (large-document Document Intelligence processing, human review queue)
- Retry/resilience on form-gen failure becomes a real requirement

If triggered: Service Bus decouples form-gen/notification from the request path; Logic Apps handles resource-lookup/notification integration.

**Stretch goal — Infrastructure as Code:** v1 provisioning is manual (Azure Portal), which is appropriate for initial setup and validation. Once the manual setup works end-to-end, codifying it in Bicep or Terraform is a natural v1.5 step — it's a strong signal for senior-level roles and de-risks re-provisioning/teardown. Deliberately sequenced *after* manual setup rather than first, since proving the design works is more valuable early than automating a design that might still change.

## 8. What You Need to Stand This Up

**Azure resources**
- Azure OpenAI resource (GPT-4o-class model deployment for the agent) — quota/access approval often required
- Azure AI Search (Basic tier to start; needs a vector-capable tier for embeddings)
- Azure Document Intelligence resource (prebuilt-document, or custom model later)
- Azure Container Apps environment + Container Registry
- Azure Key Vault
- Microsoft Fabric workspace (defer until analytics phase)
- Resource group / subscription with OpenAI quota

**Data to source**
- TX Family Code Title 4 text (public, Texas statutes site)
- TX Application for Protective Order PDF + instructions (Texas courts / OAG site)
- County-specific filing rules — pick 2–3 counties for v1, not all 254

**Dev tooling**
- Python + `azure-identity`, `openai`, `azure-search-documents`, `azure-ai-documentintelligence` SDKs
- Docker, Azure CLI (`az containerapp` extension)

**Before building**
- Legal review pass on scope and disclaimers — even for a portfolio project, this is worth taking seriously and documenting

---

## Appendix: Recruiter-Facing README Notes

Highlight in the public repo:
- Why RAG (not just "used a vector DB") — grounding claims to reduce hallucination risk in a legal-adjacent domain
- Why Document Intelligence was scoped down rather than used everywhere — shows judgment, not checkbox-collecting
- Why async was deferred — same reason
- Privacy/data-minimization design as a first-class concern, not an afterthought
- Include an architecture diagram and a short "tradeoffs considered" section — this is what differentiates a portfolio project from a tutorial clone
