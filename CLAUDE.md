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

---

---

# CRAFT LOOP — Claude Code Autonomous Pipeline

## Zweck

Das System läuft jetzt in einem neuen Modus. Das Ziel ist nicht mehr `skill.md`.
Das Ziel ist `insight.md`: eine kuratierte Sammlung von Excellence-Chunks aus den Quellen.

**Claude Code ist der Orchestrator.** Kein manueller Schritt außer: PDFs ablegen + Trigger.

---

## Trigger

Wenn der User sagt: **"craft loop starten für [name]"** (oder äquivalent), führt Claude Code den vollständigen Loop für den Skill `[name]` aus.

Wenn der User sagt: **"skill bauen für [name]"** (oder äquivalent), startet Claude Code die SYNTHESIZE-Phase für den Skill `[name]` — Cluster-Analyse, Gegenfragen, SKILL.md schreiben. Voraussetzung: `insight.md` muss existieren.

---

## Init-Prüfung

Vor dem ersten Run prüfen:

```bash
ls skills/[name]/
```

Falls `craftplan.md` fehlt → Fehler: "Skill nicht initialisiert. Führe zuerst aus: `python craft_init.py --skill [name]`"

Falls `sources/` leer ist → Fehler: "Keine PDFs gefunden. Bitte PDFs in `skills/[name]/sources/` ablegen."

---

## Phase 0 — Bootstrap (nur Run 1)

**Wenn `iterations_completed == 0`:**

1. Frage den User: *"Beschreibe den Skill in einem Satz. Was soll ein Experte auf diesem Gebiet wissen?"*
2. Speichere die Beschreibung in `craftplan.md` (Feld `description`)
3. Generiere die ersten Fragen (siehe "Fragen-Strategie Run 1" unten)
4. Führe Ingest aus:
   ```bash
   source .venv/bin/activate && python ingest.py --source skills/[name]/sources/*.pdf --collection [name]
   ```

**Ingest nur einmal.** Bei allen folgenden Runs wird ChromaDB nicht neu befüllt.

---

## Der Loop (Runs 1–N)

Für jeden Run folgt Claude Code exakt dieser Sequenz:

### Schritt 1 — Extraktion ausführen

```bash
source .venv/bin/activate && python extract.py \
  --collection [name] \
  --catalog skills/[name]/questions.md \
  --output skills/[name]/extractions/
```

### Schritt 2 — Extraktion analysieren

Claude liest die neue Extraktions-Datei vollständig.
Für jede Passage: Excellence-Bewertung gegen die 5 Kriterien (siehe unten).

### Schritt 3 — Excellence-Chunks in insight.md speichern

Nur Passagen die **mindestens 3 von 5** Excellence-Kriterien erfüllen werden gespeichert.
Bereits in `insight.md` enthaltene Passagen (gleicher Chunk-ID oder nahezu identischer Text) werden übersprungen.

Format eines Insights:

```markdown
## INSIGHT-[NN]

**Score:** [X]/5 — [✓/✗ Mechanismus] [✓/✗ Nicht-trivial] [✓/✗ Hebel] [✓/✗ Kompressionsverlust] [✓/✗ Quellenspezifisch]
**Quelle:** `[filename]` | Chunk #[n] | Similarity: [score]
**Gefunden:** Run [n] | Frage: *"[question text]"*

> [originale Passage, unverändert]

**Warum exzellent:** [1-2 Sätze — was genau an dieser Passage Excellence-Level ist]

---
```

### Schritt 4 — Run kritisieren

Claude schreibt einen Kritik-Block in `run_log.md`:

```markdown
## Run [N] — [Datum]

**Fragen:** [Anzahl]
**Passagen gefunden (STARK):** [Anzahl]
**Als Exzellenz bewertet:** [Anzahl]
**Neue Insights in insight.md:** [Anzahl]

### Was funktioniert hat
[Welche Fragen haben exzellente Passagen gefunden? Warum?]

### Was nicht funktioniert hat
[Welche Fragen hatten 0 STARK-Matches oder nur banale Treffer? Warum?]

### Wissenslücken erkannt
[Was wäre noch zu fischen, das in diesem Run nicht auftauchte?]

### Hypothesen für Run [N+1]
[Konkrete Vermutungen: "Wenn ich Frage X so formuliere, treffe ich Passagen aus Bereich Y"]

---
```

### Schritt 5 — Fragen für den nächsten Run verbessern

Claude überschreibt `skills/[name]/questions.md` mit dem neuen Fragenkatalog.
Dabei:
- Fragen die 0 STARK-Matches hatten: komplett reformulieren oder durch neue ersetzen
- Fragen die gute Matches hatten aber noch Tiefe lassen: Folge-Fragen generieren (spezifischer, tiefer)
- Neue Bereiche erschließen die in den Passagen angedeutet wurden aber noch nicht direkt abgefragt wurden
- Generiere so viele Fragen wie es echte, orthogonale Proben gibt — nicht mehr. Jede Frage muss eine Region des Embedding-Space adressieren, die keine andere Frage desselben Runs abdeckt. Wenn nach N Fragen kein genuiner neuer Winkel mehr existiert: stop. Qualität schlägt Quantität. Richtwert: Run 1 ~15-20, Run 2+ ~8-15, Lückenschluss ~5-10. Niemals auffüllen um eine Zielzahl zu erreichen.

### Schritt 6 — craftplan.md aktualisieren

`iterations_completed` um 1 erhöhen. Status aktualisieren.

### Schritt 7 — Loop-Entscheidung

Wenn `iterations_completed < max_iterations`:
→ Weiter mit Schritt 1 (nächster Run)

Wenn `iterations_completed == max_iterations`:
→ **Loop-Abschluss-Evaluation** (siehe unten)

---

## Loop-Abschluss-Evaluation

**Wichtig — falscher Frame vermeiden:**
Die Frage ist NICHT "Haben wir alles abgedeckt?" und NICHT "Haben wir die einfachen Treffer geborgen?"
Die einzige Frage ist: **Gibt es noch Excellence in den Quellen, die durch präzisere Fragen erreichbar wäre?**
Coverage ist kein Ziel. Yield ist kein Ziel. Das einzige Ziel ist Excellence-Dichte in `insight.md`.
Ein Chunk mit Score 5/5 kann in Run 6 gefunden werden genauso wie in Run 1 — die Frage ist nur ob die bisherigen Fragen dorthin gezeigt haben.

Nach dem letzten Run bewertet Claude:

1. **Yield-Trend:** Wurden in den letzten 2 Runs noch neue Insights gefunden, oder sinkt der Ertrag gegen 0?
2. **Excellence-Lücken:** Gibt es noch klar identifizierbare Bereiche in den Quellen, aus denen noch keine Excellence-Chunks extrahiert wurden?
3. **Fragen-Potenzial:** Gibt es noch Fragen-Winkel die nicht versucht wurden — spezifischer, tiefer, aus anderem Blickwinkel?

Claude gibt eine Empfehlung:
- `STOP — Excellence-Potenzial der Quellen ist ausgeschöpft` → kein weiterer Run nötig
- `WEITER — [X] weitere Runs empfohlen wegen [Begründung]` → user entscheidet

---

## Excellence-Kriterien (die 5 Filter)

Ein Chunk wird als Exzellenz eingestuft wenn er **mindestens 3 von 5** erfüllt:

### 1. Mechanismus trägt ✓
Der Chunk erklärt **WIE oder WARUM** etwas funktioniert — nicht nur DASS es funktioniert.
*Negativ-Beispiel:* "Mean reversion strategies often fail in trending markets." (DASS)
*Positiv-Beispiel:* "Mean reversion fails when noise trading risk σu is large because the price-trigger mechanism can no longer distinguish conservative from aggressive behavior..." (WARUM + Mechanismus)

### 2. Nicht-trivial ✓
Ein kompetenter Praktiker würde das **nicht aus dem Gedächtnis wissen**.
Faustregeln, Daumenregeln, Basiswissen = nicht-trivial NICHT erfüllt.
Quantifizierte Schwellenwerte, Interaktionseffekte, Gegenintuitives = erfüllt.

### 3. Hebel ✓
Das Wissen **verändert eine Entscheidung, ein Design, eine Handlung** konkret.
Frage: "Wenn ich das weiß, handle ich anders?" → Ja = erfüllt.

### 4. Kompressionsverlust ✓
Beim Zusammenfassen geht relevante Information verloren. **Die Originalformulierung zählt.**
Kann man den Chunk auf einen Satz reduzieren ohne Verlust? → Nein = erfüllt.
Ist der Chunk bereits komprimiert und jedes Wort trägt? → erfüllt.

### 5. Quellenspezifisch ✓
Das ist die **eigene Erkenntnis des Autors** — nicht generisches Lehrbuchmaterial.
Eigene Messung, eigenes Experiment, eigene Schlussfolgerung = erfüllt.
Standarddefinition oder -erklärung = nicht erfüllt.

---

## Fragen-Strategie nach Run-Nummer

### Run 1 — Explorativ ("ins Blaue")
Ausgangspunkt: nur die ein-Satz Skill-Beschreibung des Users.
**Strategie:** Breite Abdeckung. Viele verschiedene Winkel. Richtwert: 15-20 Fragen.
Nicht optimieren — erkunden. Das Ziel ist herauszufinden WAS in den PDFs steckt.
Format: B-type (failure-framed) + F-type (finding-direct), kein YAML-Overhead nötig.

Beispiel für ein unbekanntes Thema (Skill: "Wie Experten in X entscheiden"):
- "When does X fail despite correct inputs?"
- "What do experts in X know that beginners consistently get wrong?"
- "Under what conditions does X produce counterintuitive results?"
- "Is [central assumption of X] true in edge cases?"

### Run 2 — Fokus auf Lücken
Basierend auf Run-1-Ergebnis: Fragen zu Bereichen die auftauchten aber noch Tiefe lassen.
Fragen zu Bereichen die komplett fehlten (keine STARK-Matches) anders formulieren.
Spezifischer werden: statt "how does X work" → "at what threshold does X break"
Richtwert: 8-15 Fragen — nur echte Hypothesen, kein Padding.

### Run 3–4 — Tiefenfischen
Gezielt in die Bereiche wo Run-1-2 Excellence-Chunks gefunden hat.
Follow-up-Fragen zu den gefundenen Insights: Was ist die Grenze dieses Mechanismus?
Gegenbeispiele suchen: "Does X hold when Y is reversed?"
Richtwert: 8-15 Fragen.

### Run 5 — Lückenschluss
Bekannte Wissenslücken aus `run_log.md` direkt adressieren.
Sehr spezifische Fragen zu den letzten verbleibenden Hypothesen.
Richtwert: 5-10 Fragen. Wenn nur 4 echte Lücken bekannt sind: 4-8 Proben, nicht mehr.

---

## Phase SYNTHESIZE — Skill bauen aus insight.md

Wird ausgelöst wenn der User sagt: **"skill bauen für [name]"** (oder äquivalent).

Voraussetzung: `insight.md` existiert und enthält Einträge.

---

### Schritt 1 — Cluster-Analyse

Claude liest `insight.md` vollständig und gruppiert die Insights nach Entscheidungskontext — nicht nach Run-Nummer.
Ziel: herausfinden wie viele distinkte Skills das Material trägt, und welche Cluster stark genug sind (mind. 5 Insights pro Cluster).

Claude präsentiert dem User die gefundenen Cluster als kurze Liste:
```
Cluster A — [Name]: [N] Insights — [1-Satz Beschreibung was dieser Skill kann]
Cluster B — [Name]: [N] Insights — [1-Satz Beschreibung]
...
```

---

### Schritt 2 — Gegenfragen an den User (Pflicht, nicht überspringen)

Claude stellt **genau diese 3 Fragen** und wartet auf Antwort:

**Frage 1 — Nutzer des Skills:**
*"Wer benutzt diesen Skill in welchem Kontext? Beispiele: jemand der einen Algorithmus von Grund auf baut / jemand der einen bestehenden Algorithmus auditiert / jemand der eine Deployment-Entscheidung trifft / jemand der Forschungsliteratur bewertet. Das bestimmt den Workflow und den Trigger."*

**Frage 2 — Welcher Cluster:**
*"Ich habe [N] Cluster gefunden (siehe oben). Welchen Cluster soll ich als erstes zu einem Skill ausarbeiten — oder soll ich alle als separate Skills bauen?"*

**Frage 3 — Trigger-Kontext:**
*"Wann soll Claude diesen Skill automatisch aktivieren? Beschreibe 2-3 typische Situationen oder Phrasen bei denen der Skill greifen soll."*

---

### Schritt 3 — SKILL.md bauen

Mit den Antworten des Users baut Claude die SKILL.md nach diesem Schema:

**Struktur:**
```markdown
---
name: [skill-name]
description: >
  [Was der Skill tut + Trigger-Phrasen aus Frage 3, etwas "pushy" formuliert]
---

# [Skill Name]

[1-2 Sätze was dieser Skill leistet]

## Mental Model
[Wie denkt ein Experte auf diesem Gebiet? — destilliert aus den Insights, nicht kopiert]

## Decision Framework
[Welche Fragen stellt er sich — und in welcher Reihenfolge?]
[Imperativ: "Prüfe zuerst X. Wenn X, dann Y. Wenn nicht, dann Z."]

## Core Patterns
[3-7 bewährte Muster aus den Insights — jedes in 2-4 Sätzen, imperativ]

## Hard Constraints
[Was macht ein Experte NIE — direkt aus den Failure-Mode-Insights]

## Verification
[Wie prüft er sein Ergebnis — aus den Validation-Insights]

## Referenzen
Lies `references/insights.md` für vollständige Quell-Passagen.
```

**Regeln beim Schreiben:**
- ≤500 Zeilen — wenn mehr nötig: Hierarchie einführen und auf Reference-Files zeigen
- Ausschließlich imperative Sprache: "Prüfe", "Verwende", "Vermeide" — nie "man sollte"
- Kein akademisches Passiv — der Skill spricht den Nutzer direkt an
- Mechanismen erklären, nicht nur benennen: "X versagt weil Y" statt "X kann versagen"
- Insights nicht kopieren — destillieren: aus 5 ähnlichen Insights eine klare Regel ableiten

**Referenz-File anlegen:**
`insight.md` wird verlinkt als `skills/[name]/references/insights.md` (oder Symlink/Kopie).
Die SKILL.md bleibt schlank, die Originalpassagen bleiben zugänglich.

---

### Schritt 4 — craftplan.md aktualisieren

```yaml
status: skill_built
skill_file: skills/[name]/SKILL.md
skill_clusters: [A, B, ...]  # welche gebaut wurden
```

---

## Datei-Konventionen

```
skills/[name]/
  sources/           ← PDFs (user befüllt)
  extractions/       ← timestamped Extraktions-MDs (auto)
  questions.md       ← aktueller Fragenkatalog (wird überschrieben)
  insight.md         ← akkumulierte Excellence-Chunks (wird ergänzt, nie gelöscht)
  run_log.md         ← Kritik & Verbesserungs-Notizen pro Run (wird ergänzt)
  craftplan.md       ← Konfiguration & Status (wird aktualisiert)
  SKILL.md           ← fertiger Skill (≤500 Zeilen)
  references/
    insights.md      ← Pointer/Kopie von insight.md für SKILL.md-Referenzen
```

`insight.md` wird nur **ergänzt**, nie überschrieben.
`questions.md` wird bei jedem Run **überschrieben** mit der neuen Version.
`run_log.md` wird bei jedem Run **ergänzt**.
`SKILL.md` wird bei jedem Skill-Build **überschrieben**.

---

## Wichtig

**Passagen kommen ungefärbt aus ChromaDB.** Claude interpretiert und bewertet, aber erfindet nichts.
Die Excellence-Bewertung ist subjektiv — im Zweifel eher inkludieren als exkludieren.
Bei 2/5 Score: in `run_log.md` als "Kandidat" notieren, nicht in `insight.md`.
