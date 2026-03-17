# skillCrafter

A local pipeline to extract text passages from PDFs via semantic search. Built on `multilingual-e5-base` (sentence-transformers) and ChromaDB.

---

## What it does

1. **Ingest:** PDFs are split into chunks, vectorized using an embedding model, and stored in ChromaDB.

2. **Extract:** A questionnaire is analyzed against ChromaDB. For each question, the n most similar text passages are returned—directly from the PDF.

The quality of the extraction depends almost exclusively on the quality of the questions and the source pdf.

---

## Tech Stack

| Komponente | Technologie |
|---|---|
| Embedding-Modell | `intfloat/multilingual-e5-base` (lokal via sentence-transformers) |
| Vektordatenbank | ChromaDB (PersistentClient, lokal) |
| PDF-Parsing | pypdf |
| Python | 3.12 |


Prefix-Schema: `query: <frage>` beim Retrieval, `passage: <text>` beim Ingest.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Erster Start lädt `multilingual-e5-base` (~1.1GB) von HuggingFace.

---

## Quickstart

```bash
python skill.py new my_skill
cp /path/to/book.pdf skills/my_skill/sources/
# questions.md befüllen (siehe unten)
python skill.py ingest my_skill
python skill.py extract my_skill
python skill.py curate my_skill
```

---

## Question Format — the Crucial Part

ChromaDB retrieves passages based on cosine similarity between the query embedding and the document embedding. What it returns is the text that is closest to the embedding of the question — not necessarily the text that actually answers the question.

This means: vague questions yield topically similar but substantively useless passages. Precise, keyword-dense questions yield the correct chunks.

**Einfaches Format:**
```markdown
- Was sind die Kernprinzipien von X?
- Wann versagt dieser Ansatz?
```

**RAG-optimiertes Format** (höhere Retrieval-Scores, empfohlen):
```markdown
## Abschnitt

### Q01
**query:** "Keyword-dichte, selbstständige Frage ohne Pronomen — alle Konzepte explizit benannt..."
```

```yaml
id: Q01
category: risk
concept_anchor: stop_loss_noise_calibration
keywords:
  - Stop Loss Kalibrierung
  - ATR-basierter Stop
  - Bid-Ask Rauschen
```



Vollständige Anleitung: [QUESTION_CRAFTING.md](QUESTION_CRAFTING.md)

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

## Score-Interpretation

| Score | Label | Bedeutung |
|---|---|---|
| ≥ 0.75 | STARK | Passage direkt verwenden |
| 0.70–0.74 | AUSREICHEND | Passage prüfen |
| < 0.70 | — | Wird nicht ausgegeben — kein ausreichender Match |



---

## Ingest-Filter

Noise wird automatisch beim Ingest entfernt:

- Bibliographie-Abschnitte (Parsing stoppt beim ersten References-Header)
- Front-Matter: TOC, Vorwort, Inhaltsverzeichnis
- Chunks mit >40% Zeilen die auf Seitenzahlen enden
- Chunks unter 150 Zeichen oder mit >40% Ziffern
- Chunks mit >50% Citation-Pattern-Zeilen

---

## Projektstruktur

```
skillCrafter/
├── skill.py
├── ingest.py
├── extract.py
├── curate.py
├── requirements.txt
└── skills/
    └── <skill_name>/
        ├── questions.md    ← ins Git
        ├── skill.md        ← ins Git
        ├── sources/        ← PDFs, nicht im Git
        ├── extractions/    ← nicht im Git
        └── curated/        ← nicht im Git
```

---

## License

MIT
