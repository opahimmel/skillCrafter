# skillCrafter

A local pipeline to extract text passages from PDFs via semantic search and distill them into a usable skill document. Built on `multilingual-e5-base` (sentence-transformers) and ChromaDB. No cloud, no API costs.

---

## What it does

The pipeline has two distinct phases:

**Phase 1 — Extraction (Claude Code orchestrated)**

Claude Code runs this phase autonomously. Its role is central: it generates the questions, evaluates the results, and decides what to ask next.

1. **Ingest:** PDFs are split into chunks, embedded with `multilingual-e5-base`, and stored in a local ChromaDB collection. Runs once per skill.
2. **Question generation:** Claude Code writes the question catalog for each iteration — starting broad, then narrowing based on what previous runs found and what they missed. No questions are generated to fill a count; only as many as there are genuine new angles.
3. **Extract:** The question catalog is run against ChromaDB via `extract.py`. Per question, the n most similar passages are returned — directly from the source, no LLM involved in retrieval.
4. **Evaluate:** Claude Code reads every returned passage and scores it against 5 excellence criteria (see below). Only passages that meet ≥3/5 are kept.
5. **Accumulate:** Passing passages are written to `insight.md` with score, source, and a note on why the passage qualifies.
6. **Critique:** Claude Code writes a per-run critique to `run_log.md` — which questions worked, which didn't, what was missed, and what hypotheses to test next.

This loop runs for N iterations. After the final iteration Claude Code evaluates whether the sources are exhausted or further runs would still yield new excellence.

**Phase 2 — Skill Crafting (Claude Code)**

Once `insight.md` is saturated, Claude Code reads the accumulated passages and builds a `SKILL.md` — a structured, imperative decision document that can be loaded into Claude as a skill.

Claude Code asks 3 questions before building:
- Who is the user of this skill and in what context?
- Which thematic cluster of insights to use (or all)?
- When should Claude activate this skill automatically?

The answers determine the YAML trigger in the frontmatter, the workflow structure, and the imperative framing of the content.

---

## The 5 Excellence Criteria

A passage is kept only if it meets ≥3 of 5:

1. **Mechanism** — explains HOW or WHY something works, not just THAT it does
2. **Non-trivial** — a competent practitioner would not know this from memory
3. **Leverage** — knowing this changes a decision, a design, or an action
4. **Compression loss** — summarizing the passage loses relevant information
5. **Source-specific** — this is the author's own finding, not generic textbook material

---

## Claude Code Integration

Claude Code acts as the orchestrator for both phases.

**Trigger phrases:**

```
craft loop starten für <skill_name>   → runs the full extraction loop
skill bauen für <skill_name>          → builds SKILL.md from insight.md
```

The craft loop is fully autonomous. Claude Code:
- Runs `extract.py` per iteration
- Reads the extraction output and scores each passage
- Writes passing passages to `insight.md`
- Writes a critique to `run_log.md` (what worked, what didn't, what to ask next)
- Rewrites `questions.md` for the next iteration
- After the final iteration: evaluates yield trend and recommends STOP or CONTINUE

The behavior is defined in `CLAUDE.md`.

**What Claude Code does NOT do:**
- It does not invent or paraphrase passages. All content in `insight.md` is verbatim from the sources.
- It does not run ingest more than once per skill.
- It does not generate questions to hit a target count — only as many as there are genuine new angles.

---

## Tech Stack

| Component | Technology |
|---|---|
| Embedding model | `intfloat/multilingual-e5-base` (local via sentence-transformers) |
| Vector database | ChromaDB (PersistentClient, local) |
| PDF parsing | pypdf |
| Orchestrator | Claude Code (reads CLAUDE.md for loop behavior) |
| Python | 3.12 |

**Why multilingual-e5-base:** Supports cross-lingual retrieval. German queries against English sources lose 15–20% similarity score with English-only models (e.g. nomic-embed-text). e5-base closes this gap.

Prefix schema: `query: <question>` for retrieval, `passage: <text>` for ingest.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

First run downloads `multilingual-e5-base` (~1.1GB) from HuggingFace.

---

## Usage

**Step 1 — Initialize the skill**
```bash
python craft_init.py --skill [name]
```

**Step 2 — Add your PDFs**
```
skills/[name]/sources/*.pdf
```

**Step 3 — Start Claude Code, then say:**
```
craft loop starten für [name]
```
Claude Code asks once for a one-sentence skill description, then runs the extraction loop autonomously through N iterations. Each iteration it generates questions, retrieves passages, scores them, and updates `insight.md` with the passages that pass the excellence filter.

**Step 4 — Build the skill**
```
skill bauen für [name]
```
Claude Code clusters the collected insights, asks 3 questions about the intended use, and writes `SKILL.md` — ready to be placed in `~/.claude/skills/`.

---

## Question Format

ChromaDB finds passages via cosine similarity between query embedding and document embedding. The returned text is what is closest to the query in embedding space — not what answers the question semantically.

Vague questions return thematically similar but informationally useless passages. Precise, keyword-dense questions return the right chunks.

**Simple format:**
```markdown
- When does approach X fail despite correct inputs?
- What does an expert in X know that beginners consistently get wrong?
```

**RAG-optimized format** (higher retrieval scores, recommended):
```markdown
### Q01
**query:** "Keyword-dense, self-contained question without pronouns — all concepts named explicitly..."
```

Full guide: [QUESTION_CRAFTING.md](QUESTION_CRAFTING.md)

---

## CLI

```bash
python skill.py new <name>
python skill.py ingest <name>
python skill.py ingest <name> --file book.pdf
python skill.py extract <name>
python skill.py extract <name> --min-score 0.70
python skill.py extract <name> --top-k 10
python skill.py curate <name>
python skill.py list
python skill.py delete <name>
```

---

## Score Interpretation

| Score | Label | Meaning |
|---|---|---|
| ≥ 0.75 | STARK | Use passage directly |
| 0.70–0.74 | AUSREICHEND | Review before using |
| < 0.70 | — | Not returned — insufficient match |

Scores below threshold do not indicate a system error. The relevant content may simply not be in the source material.

---

## Ingest Filters

Noise is removed automatically during ingest:

- Bibliography sections (parsing stops at first References header)
- Front matter: TOC, preface, table of contents
- Chunks with >40% lines ending in page numbers
- Chunks under 150 characters or with >40% digits
- Chunks with >50% citation-pattern lines

---

## Project Structure

```
skillCrafter/
├── CLAUDE.md           ← loop behavior and skill crafting instructions for Claude Code
├── skill.py
├── ingest.py
├── extract.py
├── curate.py
├── requirements.txt
└── skills/
    └── <skill_name>/
        ├── sources/        ← PDFs (not in git)
        ├── extractions/    ← timestamped extraction files (not in git)
        ├── questions.md    ← current question catalog (overwritten each run)
        ├── insight.md      ← accumulated excellence passages (append-only)
        ├── run_log.md      ← per-run critique and hypotheses
        ├── craftplan.md    ← status and configuration
        ├── SKILL.md        ← finished skill document
        └── references/
            └── insights.md ← copy of insight.md for SKILL.md reference
```

---

## License

MIT
