# skillCrafter

**Transform books and papers into precise, reusable expert knowledge — entirely offline.**

skillCrafter is a local RAG pipeline that extracts knowledge from PDF sources, lets you curate the results, and builds structured skill documents. No cloud. No LLM. No API costs. Your data never leaves your machine.

---

## Why

Reading a book doesn't mean you've captured its knowledge. Most insights are buried across hundreds of pages, mixed with context you don't need.

skillCrafter solves this by turning the extraction process into a system:

1. You define **what you want to know** (question catalog)
2. The system finds **where the answer lives** in your sources (vector search)
3. You decide **what's worth keeping** (manual curation)
4. The result is a **Skill** — a structured thinking architecture you can actually use

The goal isn't a chatbot. The goal is **distilled expert knowledge**, in your own words, built from primary sources.

---

## What it's good for

- Extracting actionable knowledge from dense technical books
- Building domain expertise from research papers
- Creating reference documents for specialized fields (finance, medicine, law, engineering)
- Sharing curated knowledge structures with teammates
- Building a personal knowledge system that grows over time

---

## How it works

```
PDFs (books, papers)
      ↓
[INGEST]
nomic-embed-text converts text chunks into vectors
ChromaDB stores everything locally
      ↓
[EXTRACT]
Your question catalog is run against ChromaDB
Raw passages from your sources come back
No LLM — only direct text matches
      ↓
[CURATE]
You review each passage: keep / skip / edit
      ↓
[CRAFT]
Curated knowledge → SKILL.md
```

---

## Tech Stack

| Component | Technology | Why |
|---|---|---|
| Embeddings | `nomic-ai/nomic-embed-text-v1.5` | State-of-the-art open model, runs fully local |
| Vector DB | ChromaDB (PersistentClient) | Local, no server required, excellent Python API |
| PDF parsing | pypdf | Lightweight, no external dependencies |
| ML runtime | sentence-transformers | Direct model access, no account needed |
| Language | Python 3.12 | |

**No cloud services. No API keys. No data leaves your machine.**

---

## Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/skillCrafter.git
cd skillCrafter

# 2. Python environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt
```

First run will download the `nomic-embed-text-v1.5` model (~270MB) from HuggingFace automatically.

---

## Quickstart

```bash
# Create a new skill project
python skill.py new my_skill

# Add your PDFs
cp /path/to/book.pdf skills/my_skill/sources/

# Write your questions in skills/my_skill/questions.md
# (see Question Format below)

# Run the pipeline
python skill.py ingest my_skill       # PDF → ChromaDB
python skill.py extract my_skill      # questions → passages
python skill.py curate my_skill       # review: y / n / e

# Check all your skills
python skill.py list
```

---

## Question Format

Questions are plain Markdown. Two formats are supported:

**Simple:**
```markdown
- What are the core principles of X?
- When does this approach fail?
- What mistakes do beginners make?
```

**RAG-optimized** (better retrieval scores — recommended for technical domains):
```markdown
## Section Name

### Q01
**query:** "Keyword-dense, self-contained question with explicit concept names and no ambiguous pronouns..."
```

Good questions = good extractions. Vague questions return vague passages.

---

## Skill Structure

A finished Skill is not a glossary. It's a thinking architecture:

```markdown
## Mental Model
How does an expert think about this domain?

## Decision Framework
What questions do they ask — and in what order?

## Core Patterns
Proven approaches to known problems.

## Hard Constraints
What do they NEVER do? (as important as what they do)

## Verification
How do they check their own work?
```

---

## CLI Reference

```bash
python skill.py new <name>                          # create skill
python skill.py ingest <name>                       # ingest all PDFs in sources/
python skill.py ingest <name> --file book.pdf       # ingest single PDF
python skill.py extract <name>                      # run extraction
python skill.py extract <name> --min-score 0.60     # with similarity threshold
python skill.py extract <name> --top-k 8            # more passages per question
python skill.py curate <name>                       # curate last extraction
python skill.py list                                # overview of all skills
python skill.py delete <name>                       # delete skill + collection
```

---

## Filters

skillCrafter automatically removes noise from ingested PDFs:

- **Bibliography filter** — stops parsing at reference sections
- **Front-matter filter** — skips table of contents, preface, foreword pages
- **TOC chunk filter** — removes chunks where >40% of lines end with page numbers
- **Noise filter** — removes chunks under 150 characters or with >40% digits
- **Citation density filter** — removes chunks dominated by citation patterns
- **Source balancing** — limits results to max 2 chunks per source per question (prevents large books from dominating)

---

## Project Structure

```
skillCrafter/
├── skill.py              ← main CLI entry point
├── ingest.py             ← PDF ingestion pipeline
├── extract.py            ← question-based extraction
├── curate.py             ← interactive curation tool
├── requirements.txt
└── skills/
    └── <skill_name>/
        ├── questions.md  ← your question catalog
        ├── skill.md      ← finished skill document
        ├── sources/      ← place PDFs here (not tracked by git)
        ├── extractions/  ← raw extraction output (not tracked)
        └── curated/      ← curated passages (not tracked)
```

---

## License

MIT
