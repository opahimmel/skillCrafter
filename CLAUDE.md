# Skill Crafting System

> Expertenwissen aus Quellen extrahieren → automatisch kuratieren → in eine Denkarchitektur überführen.

Lokal. Kein Cloud-LLM im Extraktionsprozess. Passagen kommen ungefärbt aus ChromaDB.

---

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install chromadb nomic sentence-transformers pypdf langchain langchain-community
```

---

## Architektur & Modell-Protokoll

```
PHASE 0 — Interview + Spannungsfeld          → Opus (Gespräch mit User)
PHASE 1-3 — Craft Loop (Runs 1-3)            → Haiku als Dirigent (/model haiku)
PHASE SYNTHESIZE — Skill bauen                → Opus (/model opus)
```

**Modell-Wechsel ist explizit.** User wechselt mit `/model haiku` vor dem Loop
und `/model opus` vor Interview und Synthesize.

```
DIRIGENT (Haiku — liest Dateien, ruft Scripts, schreibt Ergebnisse)
    │
    ├── QUICK-FILTER AGENT (Haiku — Passagen lesen & SKIP/KANDIDAT)
    │
    ├── SCORER AGENTS (Sonnet — Excellence-Bewertung, parallel)
    │     Kein CLAUDE.md, kein insight.md, kein run_log
    │
    ├── QUESTION AGENT (Haiku — Fragenkatalog generieren)
    │
    └── DUPLIKAT-CHECK (Python via chunk_index.json — 0 Tokens)
```

**Opus nur für Denkarbeit (Interview, Spannungsfeld, Synthesize).** Sonnet nur für Excellence-Scoring. Alles andere Haiku — inklusive Dirigent.

---

## Trigger

- **"craft loop starten für [name]"** → Vollständiger Loop (Runs 1-5)
- **"skill bauen für [name]"** → SYNTHESIZE-Phase (Voraussetzung: `insight.md` existiert)

---

## Neuen Skill anlegen

```bash
python craft_init.py --skill [name]
# → Dann PDFs in skills/[name]/sources/ ablegen
```

---

## Craft Loop

### Phase 0 — Bootstrap (nur Run 1)

Wenn `iterations_completed == 0`:

#### Schritt 0a — Interview (Pflicht)

4 Fragen, sequentiell. Jede Antwort baut auf der vorherigen auf.

1. *"Was soll jemand mit diesem Skill entscheiden können — was ist die Kernentscheidung?"*
2. *"Aus welcher Rolle heraus? Creator (baut), Owner (entscheidet) oder Broker (vermittelt)?"*
3. *"Was weißt du bereits — was wäre trivial für dich?"*
4. *"Wo vermutest du die größte Unsicherheit — was könnte dich überraschen?"*

#### Schritt 0b ��� Spannungsfeld ableiten

Aus den Interview-Antworten das **Spannungsfeld** definieren und in `craftplan.md` speichern:

```markdown
## Spannungsfeld

**Kernentscheidung:** [aus Frage 1]
**Primärrolle:** [Creator|Owner|Broker]
**Trivial-Grenze:** [aus Frage 3 — was NICHT gesucht werden soll]
**Unsicherheit:** [aus Frage 4 — wo die Spannung liegt]
```

Das Spannungsfeld ist der Rahmen für alle Runs. Es bestimmt nicht *was* gefunden wird, sondern *aus welchen Richtungen* gesucht wird.

#### Schritt 0c — Multi-Probe Katalog generieren

Aus dem Spannungsfeld generiert der Haiku-Agent den ersten Katalog. **Entscheidend:** Die drei Probe-Typen kommen aus verschiedenen Richtungen des Spannungsfelds.

```
Du generierst einen Multi-Probe Katalog für RAG-Extraktion.

SPANNUNGSFELD:
  Kernentscheidung: [...]
  Primärrolle: [...]
  Trivial-Grenze: [...]
  Unsicherheit: [...]

Generiere 8 Probe-Sets. Jedes Set hat 3 Probes die aus VERSCHIEDENEN
Richtungen des Spannungsfelds kommen:

  FRAGE    — sucht Unbekanntes, failure-framed, aus Richtung der Unsicherheit
  STATEMENT — formuliert eine Hypothese die bestätigt oder widerlegt werden soll,
              aus der GEGENRICHTUNG der Primärrolle
              (Rolle=Owner → Statement aus Creator-Perspektive, etc.)
  KEYWORDS  — Fachterminologie die ein Experte der ANDEREN Rollen nutzen würde,
              nicht die Begriffe die der User schon kennt (Trivial-Grenze)

REGELN:
- Jedes Set deckt eine EIGENE Region im Embedding-Space ab
- FRAGE, STATEMENT und KEYWORDS desselben Sets zeigen in verschiedene Richtungen
- Keine Überlappung mit Trivial-Grenze
- Qualität > Quantität. Kein Padding.

FORMAT:
## SET-01: [Thema]
- FRAGE: [...]
- STATEMENT: [...]
- KEYWORDS: [...]
```

Agent mit `model: "haiku"`. Ergebnis als `questions.md` speichern.

#### Schritt 0d — Ingest

```bash
source .venv/bin/activate && python ingest.py --source skills/[name]/sources/*.pdf --collection [name]
```

**Ingest nur einmal.** ChromaDB wird nicht neu befüllt.

---

### Schritt 1 — Extraktion

```bash
source .venv/bin/activate && python extract.py \
  --collection [name] \
  --catalog skills/[name]/questions.md \
  --output skills/[name]/extractions/ \
  --compact
```

`--compact` erzeugt: Markdown (~40% kleiner) + JSON-Sidecar mit Chunk-IDs.

### Schritt 2 — Duplikate filtern (Python, 0 Tokens)

```bash
source .venv/bin/activate && python -c "
from chunk_index import ChunkIndex
import json, sys, glob
idx = ChunkIndex('skills/[name]/chunk_index.json')
sidecars = sorted(glob.glob('skills/[name]/extractions/*.json'))
if not sidecars:
    print('KEINE SIDECAR GEFUNDEN', file=sys.stderr); sys.exit(1)
new = idx.filter_new(sidecars[-1])
print(f'{len(new)} neue Passagen (von {json.load(open(sidecars[-1]))[\"total_passages\"]} total)')
for p in new:
    print(f'  {p[\"chunk_id\"]} (sim={p[\"similarity\"]})')
"
```

Nur als "neu" gemeldete Chunks werden weiterverarbeitet.

### Schritt 3 — Zwei-Pass Excellence-Scoring

**Pass 1 — Quick-Filter (Haiku-Agent):**
Liest alle neuen Passagen. Pro Passage: **SKIP** (trivial/Lehrbuch/Definition) oder **KANDIDAT**.
Ziel: ~40-50% eliminieren. Agent mit `model: "haiku"`.

**Pass 2 — Full-Score (Sonnet-Agents, parallel):**
KANDIDAT-Passagen in Batches (5-10 pro Agent) an Sonnet-Agents.

Scorer-Prompt:

```
Bewerte jede Passage gegen diese 5 Kriterien. Antworte NUR im geforderten Format.

KRITERIEN:
1. MECHANISMUS — Erklärt WIE/WARUM, nicht nur DASS. ✓ wenn Kausalität oder Prozess.
2. NICHT-TRIVIAL — Praktiker wüsste das nicht aus dem Gedächtnis. ✓ wenn Schwellenwerte, Interaktionseffekte, Gegenintuitives.
3. HEBEL — Verändert eine Entscheidung konkret. ✓ wenn "weiß ich das, handle ich anders".
4. KOMPRESSION — Zusammenfassung verliert Information. ✓ wenn jedes Wort trägt.
5. QUELLENSPEZIFISCH — Eigene Erkenntnis des Autors. ✓ wenn eigene Messung/Experiment/Schlussfolgerung.

PASSAGEN:
[nummeriert]

FORMAT (eine Zeile pro Passage):
[Nr]|[Score]/5|[✓✗✓✓✗]|[1 Satz Begründung]
```

Agent mit `model: "sonnet"`.

### Schritt 4 — Insights speichern

Nur **Score ≥ 3/5** → `insight.md`. Bei 2/5: in `run_log.md` als "Kandidat" notieren.

Format:

```markdown
## INSIGHT-[NN]

**Score:** [X]/5 — [✓/✗ pro Kriterium]
**Quelle:** `[filename]` | Chunk #[n] | Similarity: [score]
**Gefunden:** Run [n] | Frage: *"[question text]"*

> [originale Passage, unverändert]

**Warum exzellent:** [1 Satz]

---
```

Chunk-Index aktualisieren:
```python
from chunk_index import ChunkIndex
idx = ChunkIndex("skills/[name]/chunk_index.json")
idx.add("buch.pdf:34", insight_number=5, score=4, run=1)
idx.save()
```

### Schritt 5 — Run-Kritik

In `run_log.md`:

```markdown
## Run [N] — [Datum]

**Fragen:** [n] | **Passagen:** [n] | **Neue:** [n] | **Insights:** [n]

### Treffer
[1 Zeile pro erfolgreiche Frage]

### Lücken
[1 Zeile pro 0-Treffer-Frage]

### Hypothesen Run [N+1]
[2-4 konkrete Vermutungen]
```

### Schritt 6 — Multi-Probe Katalog generieren (Haiku-Agent)

Input: Spannungsfeld aus craftplan.md, Run-Kritik, bisherige Insight-Themen, Run-Nummer.

```
Du generierst einen Multi-Probe Katalog für RAG-Extraktion.

SPANNUNGSFELD:
  Kernentscheidung: [...]
  Primärrolle: [...]
  Trivial-Grenze: [...]
  Unsicherheit: [...]

RUN: [N+1] von [max]
BISHERIGE INSIGHTS (Themen): [Liste]
LETZTER RUN: [Kritik]

STRATEGIE:
- Run 2 — SCHARF: 5 Probe-Sets, gezielt Lücken + Gegenrichtung bisheriger Treffer
- Run 3 — FINAL: 3 Probe-Sets, nur noch offene Spannungen, maximale Präzision

Pro Probe-Set 3 Probes aus VERSCHIEDENEN Richtungen:
  FRAGE    — sucht Unbekanntes, failure-framed, aus Richtung der Unsicherheit
  STATEMENT — Hypothese aus der GEGENRICHTUNG der Primärrolle
  KEYWORDS  — Fachterminologie der ANDEREN Rollen, nicht Trivial-Grenze

REGELN:
- Jedes Set = eigene Region im Embedding-Space
- FRAGE, STATEMENT und KEYWORDS zeigen in verschiedene Richtungen
- Keine Überlappung mit Trivial-Grenze oder bereits gefundenen Insights
- Qualität > Quantität. Kein Padding.

FORMAT:
## SET-01: [Thema]
- FRAGE: [...]
- STATEMENT: [...]
- KEYWORDS: [...]
```

Agent mit `model: "haiku"`. Ergebnis als `questions.md` speichern.

### Schritt 7 — craftplan.md aktualisieren

`iterations_completed` um 1 erhöhen.

### Schritt 8 — Loop-Entscheidung

**3 Runs total. Kein Padding, kein "noch ein Run sicherheitshalber".**

```
Run 1 — BREIT (sequentiell, braucht Interview-Input)
  8 Probe-Sets × 3 = 24 Probes
  Alle Ecken des Spannungsfelds abtasten
  → "Was gibt es hier?"

Run 2+3 — PARALLEL (nach Run 1 genug Orientierung)
  Haiku-Agent generiert beide Kataloge in einem Call:
    Run 2 — SCHARF: 5 Sets × 3 = 15 Probes (Lücken + Gegenrichtung)
    Run 3 — FINAL:  3 Sets × 3 = 9 Probes (offene Spannungen)
  Extraktion + Scoring jeweils unabhängig
  Insights in insight.md mergen (Orchestrator, sequentiell)
  Finale Run-Kritik für beide Runs
```

Nach Run 3 → **Loop-Abschluss-Evaluation**.

---

## Loop-Abschluss-Evaluation

Datenanalyse, kein Reasoning. Der Dirigent (Haiku) prüft:

1. **Yield-Trend:** `count(insights_run_N)` vs. vorherige Runs → steigend/fallend/null?
2. **Zero-Hit-Probes:** Wie viele Probes hatten 0 Treffer? (aus run_log)
3. **Neue Chunks:** Anteil neuer vs. bekannter Chunks (aus chunk_index)

Entscheidungslogik:
- Yield = 0 in letztem Run UND Zero-Hit-Probes < 2 → `STOP`
- Yield > 0 UND noch Runs übrig → `WEITER`
- Im Zweifel: `STOP`. Kein "noch ein Run sicherheitshalber".

---

## Excellence-Kriterien

Score ≥ 3/5 → `insight.md`. Im Zweifel eher inkludieren.

| # | Kriterium | ✓ wenn |
|---|---|---|
| 1 | **Mechanismus** | Erklärt WIE/WARUM, nicht nur DASS |
| 2 | **Nicht-trivial** | Praktiker wüsste es nicht aus dem Gedächtnis |
| 3 | **Hebel** | "Weiß ich das, handle ich anders" |
| 4 | **Kompressionsverlust** | Zusammenfassung verliert Information |
| 5 | **Quellenspezifisch** | Eigene Erkenntnis des Autors, kein Lehrbuch |

---

## Fragen-Qualität

| Schlecht | Gut |
|---|---|
| Was ist eine Trading Strategie? | Unter welchen Marktbedingungen versagt Mean Reversion? |
| Was ist Risiko? | Wie berechnet man Position Sizing bei asymmetrischem Risiko? |
| Was ist Backtest? | Welche Fehler führen zu Overfitting im Backtest? |

Gute Fragen decken ab: Entscheidungslogik, Fehler & Grenzen, Verifikation, Implementierung.

---

## Phase SYNTHESIZE — Skill bauen

Trigger: **"skill bauen für [name]"**. Voraussetzung: `insight.md` existiert.

### Schritt 1 — Cluster-Analyse

Insights nach Entscheidungskontext gruppieren (nicht nach Run).
Cluster mit mind. 5 Insights dem User präsentieren:
```
Cluster A — [Name]: [N] Insights — [1-Satz Beschreibung]
Cluster B — [Name]: [N] Insights — [1-Satz Beschreibung]
```

### Schritt 2 — Gegenfragen (Pflicht)

1. *"Wer benutzt diesen Skill in welchem Kontext?"*
2. *"Welchen Cluster als Skill ausarbeiten — oder alle separat?"*
3. *"Wann soll Claude diesen Skill automatisch aktivieren? 2-3 Situationen."*

### Schritt 3 — SKILL.md bauen

```markdown
---
name: [skill-name]
description: >
  [Was der Skill tut + Trigger-Phrasen]
---

# [Skill Name]

## Mental Model
## Decision Framework
## Core Patterns
## Hard Constraints
## Verification
## Referenzen
Lies `references/insights.md` für vollständige Quell-Passagen.
```

Regeln: ≤500 Zeilen, imperativ, Mechanismen erklären, destillieren statt kopieren.

---

## Datei-Konventionen

```
skills/[name]/
  sources/           ← PDFs (user befüllt)
  extractions/       ← *.md + *.json pro Run
  questions.md       ← aktueller Fragenkatalog (wird überschrieben)
  insight.md         ← akkumulierte Excellence-Chunks (nur ergänzen)
  chunk_index.json   ← Duplikat-Index (nie manuell editieren)
  run_log.md         ← Kritik pro Run
  craftplan.md       ← Konfiguration & Status
  SKILL.md           ← fertiger Skill (≤500 Zeilen)
  references/
    insights.md      ← Kopie von insight.md
```

---

## Token-Budget

**3 Runs total: 48 Probes (24 + 15 + 9)**

| Komponente | Modell | Kosten-Klasse |
|---|---|---|
| Interview + Spannungsfeld | Opus | einmalig, ~2-3k |
| Dirigent (Loop-Steuerung) | **Haiku** | ~1-2k/Run |
| Quick-Filter | Haiku (Agent) | ~800/Run |
| Excellence-Scoring | Sonnet (Agent) | ~500 × N Batches |
| Probe-Generierung | Haiku (Agent) | ~800/Run |
| Duplikat-Check | Python | 0 |
| Reranking | lokal (cross-encoder) | 0 |
| Loop-Evaluation | Haiku (Dirigent) | ~200/Run |
| Synthesize (Skill bauen) | Opus | einmalig, ~5-10k |

**Modell-Wechsel-Protokoll:**
1. Opus → Interview + Spannungsfeld
2. `/model haiku` → Craft Loop (Runs 1-3)
3. `/model opus` → Synthesize
