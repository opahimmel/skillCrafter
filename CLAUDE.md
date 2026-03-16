# Skill Crafting System
## nomic-embed-text + ChromaDB · Local RAG Pipeline

---

## Was dieses System tut

Dieses System verwandelt rohe Wissensquellen (PDFs, Bücher, Papers) in einen **präzisen, destillierten Skill** – ohne Cloud, ohne API-Kosten, ohne dass Daten deinen Mac verlassen.

Das Ziel ist kein Chatbot. Das Ziel ist **Skill Crafting**:
> Expertenwissen aus Quellen extrahieren → kuratieren → in eine Denkarchitektur überführen.

---

## Architektur

```
Wissensquellen (PDFs)
        ↓
[INGEST]
nomic-embed-text wandelt Text in Vektoren um
ChromaDB speichert die Vektoren lokal
        ↓
[EXTRACT]
Fragenkatalog wird gegen ChromaDB gestellt
Rohe Passagen aus den Quellen kommen zurück
        ↓
[CURATE]
Du bewertest: relevant / nicht relevant
        ↓
[CRAFT]
Kuratiertes Wissen → SKILL.md
```

**Kein LLM im Extraktionsprozess.** Die Rohpassagen kommen direkt aus den Quellen – ungefärbt, uninterpretiert.

---

## Setup

### 1. Voraussetzungen

```bash
# Python environment
python3 -m venv .venv
source .venv/bin/activate

# Dependencies
pip install chromadb nomic sentence-transformers pypdf langchain langchain-community
```

### 2. Projektstruktur

```
skill-crafting/
├── CLAUDE.md               ← diese Datei
├── ingest.py               ← PDFs einlesen & vektorisieren
├── extract.py              ← Fragen stellen & Passagen abrufen
├── catalog/
│   └── questions.md        ← Fragenkatalog (du pflegst das)
├── sources/
│   └── *.pdf               ← deine Bücher & Papers
├── chroma_db/              ← lokale Vektordatenbank (auto-generiert)
└── output/
    ├── raw_extractions/    ← rohe Passagen pro Frage
    ├── curated/            ← was du als relevant markiert hast
    └── skills/             ← fertige SKILL.md Dateien
```

---

## Workflow

### Phase 1 – INGEST: Quellen einlesen

```bash
python ingest.py --source sources/buch.pdf --collection quant_trading
```

Was passiert:
- PDF wird in Chunks aufgeteilt (512 Token, 64 Token Overlap)
- nomic-embed-text vektorisiert jeden Chunk
- ChromaDB speichert alles lokal in `chroma_db/`

**Tipp:** Jedes Skill-Projekt bekommt eine eigene Collection in ChromaDB.

---

### Phase 2 – EXTRACT: Fragen stellen

```bash
python extract.py --collection quant_trading --catalog catalog/questions.md --output output/raw_extractions/
```

Was passiert:
- Jede Frage aus dem Katalog wird gegen ChromaDB gestellt
- Die top 5 relevantesten Passagen werden zurückgegeben
- Kein LLM – nur rohe Textstellen aus deinen Quellen
- Alles wird als Markdown in `output/raw_extractions/` gespeichert

---

### Phase 3 – CURATE: Du entscheidest

Öffne die Extraktionen in `output/raw_extractions/`.

Für jede Passage entscheidest du:
- ✅ Relevant → kopieren nach `output/curated/`
- ❌ Nicht relevant → ignorieren
- ⚠️ Teilweise relevant → manuell kürzen & kopieren

**Du bist der Filter. Das ist dein Edge.**

---

### Phase 4 – CRAFT: Skill bauen

Aus dem kuratierten Wissen baust du die SKILL.md.

Ein exzellenter Skill besteht aus:

```markdown
## Mental Model
Wie denkt ein Experte auf diesem Gebiet?

## Decision Framework
Welche Fragen stellt er sich – und in welcher Reihenfolge?

## Core Patterns
Bewährte Lösungswege für bekannte Probleme.

## Hard Constraints
Was macht er NIE? (genauso wichtig wie was er tut)

## Verification
Wie prüft er sein eigenes Ergebnis?
```

Ein Skill ist kein Glossar. Ein Skill ist eine **Denkarchitektur**.

---

## Der Fragenkatalog

Der Fragenkatalog ist das Herzstück des Systems.
**Schlechte Fragen → schlechte Extraktionen → schlechter Skill.**

### Anatomie einer guten Frage

| Schlechte Frage | Gute Frage |
|---|---|
| Was ist eine Trading Strategie? | Unter welchen Marktbedingungen versagt Mean Reversion? |
| Was ist Risiko? | Wie berechnet man Position Sizing bei asymmetrischem Risiko? |
| Was ist Backtest? | Welche Fehler führen zu Overfitting im Backtest? |

### Fragentypen für jeden Skill:

```markdown
## Grundlagen
- Was sind die 3-5 fundamentalen Prinzipien dieses Gebiets?
- Welche Konzepte werden am häufigsten missverstanden?

## Entscheidungslogik
- Wann tut ein Experte X und wann tut er Y?
- Welche Faktoren sind entscheidend für [Kernentscheidung]?

## Fehler & Grenzen
- Was sind die häufigsten Anfängerfehler?
- Wann funktioniert dieser Ansatz NICHT?

## Verifikation
- Wie prüft ein Experte ob sein Ergebnis korrekt ist?
- Was sind Warnsignale dass etwas falsch läuft?

## Implementierung
- Wie geht man von Theorie zu Praxis?
- Welche konkreten Schritte folgen aufeinander?
```

---

## Skill Versionierung

Ein Skill ist kein Endprodukt – er wächst mit deiner Erfahrung.

```
skill_v0.1.md   ← reines Buchwissen
skill_v0.4.md   ← erste eigene Erfahrungen integriert
skill_v1.0.md   ← battle-tested, dein echter Edge
```

**Regel:** Jedes Mal wenn du etwas in der Praxis lernst das die Bücher nicht hatten → in den Skill.

---

## Neues Skill-Projekt starten

```bash
# 1. Neue Collection anlegen
python ingest.py --source sources/*.pdf --collection [projekt_name]

# 2. Fragenkatalog erstellen
cp catalog/questions_template.md catalog/[projekt_name]_questions.md
# → Fragen anpassen

# 3. Extrahieren
python extract.py --collection [projekt_name] --catalog catalog/[projekt_name]_questions.md

# 4. Kuratieren & Skill bauen
# → output/skills/[projekt_name]_skill.md
```

---

## Laufende Projekte

| Skill | Collection | Status |
|---|---|---|
| quant_expert | quant_trading | 🔄 in Arbeit |

---

## Philosophie

> Du musst die Bücher nicht verstehen. Du musst nur entscheiden was wahr ist.
> Die KI liest – du kuratierst – der Skill denkt.
