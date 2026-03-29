"""
craft_init.py – Neuen Skill initialisieren.

Erstellt die Ordnerstruktur und Konfigurationsdateien für einen neuen Craft Loop.

Usage:
    python craft_init.py --skill mein_skill
    python craft_init.py --skill mein_skill --description "Was der Experte auf diesem Gebiet weiß"
    python craft_init.py --skill mein_skill --max-iterations 7
"""

import argparse
import os
import sys
from datetime import datetime


def init_skill(name: str, description: str = "", max_iterations: int = 3):
    base = os.path.join("skills", name)

    if os.path.exists(base):
        print(f"[FEHLER] Skill '{name}' existiert bereits unter: {base}", file=sys.stderr)
        print("Benutze einen neuen Namen oder lösche den existierenden Ordner.", file=sys.stderr)
        sys.exit(1)

    # Ordner anlegen
    for folder in ["sources", "extractions"]:
        os.makedirs(os.path.join(base, folder), exist_ok=True)
        print(f"  ✓ {os.path.join(base, folder)}/")

    today = datetime.now().strftime("%Y-%m-%d")

    # craftplan.md
    craftplan_content = f"""---
skill: {name}
description: "{description}"
collection: {name}
iterations_completed: 0
max_iterations: {max_iterations}
status: awaiting_sources
created: {today}
---

# Craft Plan: {name}

## Skill-Beschreibung
{description if description else "[Noch nicht definiert — wird im Interview gesetzt]"}

## Spannungsfeld
<!-- Wird durch das Interview in Phase 0 befüllt -->

**Kernentscheidung:** [Was soll mit diesem Skill entschieden werden?]
**Primärrolle:** [Creator|Owner|Broker]
**Trivial-Grenze:** [Was ist bekannt und soll NICHT gesucht werden]
**Unsicherheit:** [Wo liegt die größte Wissenslücke / was könnte überraschen]

## Status
- Iterationen abgeschlossen: 0 / {max_iterations}
- Nächster Schritt: PDFs in `skills/{name}/sources/` ablegen, dann Claude starten

## Notizen
<!-- Eigene Notizen zum Projekt hier -->
"""

    # insight.md
    insight_content = f"""# Insights: {name}

> {description if description else "[Skill-Beschreibung folgt beim ersten Run]"}

*Erstellt: {today} — 0 Insights*

---

<!-- Insights werden automatisch durch den Craft Loop eingefügt -->
<!-- Format: INSIGHT-XX mit Score, Quelle, Run-Nummer und Begründung -->
"""

    # run_log.md
    run_log_content = f"""# Run Log: {name}

---

<!-- Jeder Run dokumentiert: Fragen-Version, Ergebnisse, Kritik, Verbesserungen -->
<!-- Wird automatisch durch den Craft Loop befüllt -->
"""

    # questions.md (leer, wird beim ersten Run generiert)
    questions_content = f"""# {name} — Question Catalog
# Collection: {name}
# Version: 1.0 — Initial (wird generiert)
#
---

<!-- Fragen werden beim ersten Run von Claude generiert -->
<!-- Format: B-type (failure-framed) + F-type (finding-direct) -->
"""

    files = {
        os.path.join(base, "craftplan.md"): craftplan_content,
        os.path.join(base, "insight.md"): insight_content,
        os.path.join(base, "run_log.md"): run_log_content,
        os.path.join(base, "questions.md"): questions_content,
    }

    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {path}")

    print(f"""
╔══════════════════════════════════════════════════════╗
║  Skill '{name}' initialisiert
║
║  1. PDFs ablegen in:
║     skills/{name}/sources/
║
║  2. Claude starten und sagen:
║     "craft loop starten für {name}"
╚══════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(description="Neuen Skill für den Craft Loop initialisieren")
    parser.add_argument("--skill", required=True,
                        help="Name des Skills (wird als Ordner- und Collection-Name verwendet)")
    parser.add_argument("--description", default="",
                        help="Ein-Satz Skill-Beschreibung (kann auch später beim ersten Run angegeben werden)")
    parser.add_argument("--max-iterations", type=int, default=5,
                        help=f"Maximale Anzahl Runs (default: 3)")
    args = parser.parse_args()

    init_skill(args.skill, args.description, args.max_iterations)


if __name__ == "__main__":
    main()
