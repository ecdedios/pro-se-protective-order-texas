# Data Indexing Plan — Azure AI Search

Companion doc to `dv-protective-order-agent-architecture.md`, detailing how the RAG corpus is built and maintained.

---

## 1. Source Documents

| Source | Scope | Notes |
|---|---|---|
| TX Family Code Title 4 (Protective Orders) | Statewide | Public statute text |
| County-specific filing procedures | Pilot counties only (2–3 for v1) | Filing location, fees, required copies, hours |
| TX Application for Protective Order — official instructions | Statewide | Explains how to complete the standard form |

v1 deliberately limits county coverage rather than attempting all 254 counties — depth and accuracy over breadth.

---

## 2. Chunking Strategy

Chunking is content-aware, not fixed-token-window, because legal text loses meaning if split mid-requirement.

- **Statute** — chunk by section/subsection (e.g., §85.001, §85.002). Each chunk is a complete legal unit.
- **County rules** — chunk by procedural step (where to file, fees, what to bring, hours). Naturally short and atomic.
- **Form instructions** — chunk by the form field/section they explain.

---

## 3. Index Schema

| Field | Type | Purpose |
|---|---|---|
| `content` | string | Raw chunk text |
| `content_vector` | vector | Embedding for semantic search |
| `source_type` | string | `statute` / `county_rule` / `form_instruction` |
| `county` | string (nullable) | Null = statewide; populated for county-specific rules |
| `citation` | string | e.g. "Tex. Fam. Code §85.001" — enables the agent to show its grounding |
| `last_verified_date` | date | Drives staleness checks and re-index scheduling |

`citation` is the most important field — it's what separates a grounded answer from a confident-sounding guess.

The runnable index definition is in [`rag-index-schema.json`](./rag-index-schema.json) — ready to submit via the Azure Portal's "Add index (JSON)" option or the Search SDK. It adds a required `id` key field and vector/semantic search configuration not shown in the table above:
- Vector profile assumes `text-embedding-3-small` (1536 dimensions) — update to 3072 if using `-large`
- HNSW algorithm with cosine similarity, defaults tuned for a corpus in the hundreds-to-low-thousands of chunks range
- Semantic configuration uses `citation` as the title field so re-ranked results surface a recognizable label (e.g. "Tex. Fam. Code §85.001"), not a raw chunk ID

---

## 4. Retrieval Approach

- **Hybrid search** (vector + keyword), not pure semantic — legal text has exact terms (specific code sections, defined terms) where keyword match outperforms embedding similarity alone
- **County filter** — applied when the survivor's county is known and covered; falls back to statewide-only chunks otherwise
- **Semantic re-ranking** — precision is prioritized over recall; a wrong grounded citation is worse than surfacing fewer, more relevant chunks

---

## 5. Freshness & Maintenance

- `last_verified_date` tracked per chunk
- Scheduled re-indexing job (not one-time load) — statutes and county procedures change, and a stale legal citation is a real risk to a survivor relying on it, not just a data-quality issue
- Recommended cadence: quarterly re-verification pass minimum, plus ad hoc re-index on known statute amendments

---

## 6. Open Questions for Implementation

- Embedding model choice (Azure OpenAI `text-embedding-3-small` vs `-large` — cost/quality tradeoff)
- Whether county coverage expands post-v1 and how that scales the re-verification workload
- Process for flagging/handling a detected statute change (manual review vs automated diff alert)
