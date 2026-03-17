# skillCrafter

A local pipeline to extract text passages from PDFs via semantic search. Built on `multilingual-e5-base` (sentence-transformers) and ChromaDB.

---

## What it does

1. **Ingest:** PDFs werden in Chunks aufgeteilt, per Embedding-Modell vektorisiert und in ChromaDB gespeichert.
2. **Extract:** Ein Fragenkatalog wird gegen die ChromaDB gestellt. Pro Frage kommen die n ähnlichsten Textpassagen zurück — direkt aus dem PDF, kein LLM.
3. **Curate:** Du entscheidest welche Passagen relevant sind.
4. **Craft:** Aus den kuratierten Passagen baust du ein Skill-Dokument.

Die Qualität der Extraktion hängt fast ausschließlich von der Qualität der Fragen ab.

---

## Tech Stack

| Komponente | Technologie |
|---|---|
| Embedding-Modell | `intfloat/multilingual-e5-base` (lokal via sentence-transformers) |
| Vektordatenbank | ChromaDB (PersistentClient, lokal) |
| PDF-Parsing | pypdf |
| Python | 3.12 |

**Warum multilingual-e5-base:** Das Modell unterstützt Cross-Lingual-Retrieval. Queries auf Deutsch gegen englische Quellen verlieren mit englisch-optimierten Modellen (z.B. nomic-embed-text) typisch 15–20% Similarity-Score. e5-base schließt diesen Gap.

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

## Frageformat — der entscheidende Teil

ChromaDB findet Passagen über Cosine-Similarity zwischen Query-Embedding und Dokument-Embedding. Was zurückkommt ist der Text der dem Embedding der Frage am nächsten liegt — nicht der Text der die Frage inhaltlich beantwortet.

Das bedeutet: vage Fragen liefern thematisch ähnliche aber inhaltlich nutzlose Passagen. Präzise, keyword-dichte Fragen liefern die richtigen Chunks.

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

Das YAML-Block wird nicht für die Suche verwendet — er dient als Dokumentation und erleichtert die spätere Kuration.

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

Scores unter dem Threshold bedeuten nicht zwingend einen Fehler im System — oft fehlt das relevante Material einfach in der Bibliothek.

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
