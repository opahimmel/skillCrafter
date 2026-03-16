"""
curate.py – Interaktives CLI zum Kuratieren von Extraktionen.

Öffnet jede Passage aus einer Extraktion und lässt dich entscheiden:
  y  → relevant, nach output/curated/ kopieren
  n  → nicht relevant, überspringen
  e  → editieren (öffnet $EDITOR)
  q  → beenden

Usage:
    python curate.py --input output/raw_extractions/quant_trading_20240101_120000.md
    python curate.py --input output/raw_extractions/quant_trading_20240101_120000.md \
                     --output output/curated/
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime


# ---------------------------------------------------------------------------
# Parser: Markdown-Extraktion einlesen
# ---------------------------------------------------------------------------

def parse_extractions(md_path: str) -> list[dict]:
    """
    Liest eine von extract.py erzeugte Markdown-Datei ein.
    Gibt Liste von {"section": str, "question": str, "passages": [str]} zurück.
    """
    entries = []
    current_section = ""
    current_question = ""
    current_passages = []
    buffer = []

    def flush():
        if current_question and buffer:
            entries.append({
                "section": current_section,
                "question": current_question,
                "passages": list(buffer),
            })
            buffer.clear()

    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("## ") and not line.startswith("### "):
            current_section = line[3:].strip()
        elif line.startswith("### Frage "):
            flush()
            current_question = re.sub(r"^### Frage \d+: ", "", line).strip()
        elif line.startswith("**Passage"):
            # Sammle Passage-Block bis zur nächsten Passage oder ---
            passage_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith("**Passage") and lines[i].rstrip() != "---":
                passage_lines.append(lines[i].rstrip())
                i += 1
            buffer.append("\n".join(passage_lines))
            continue
        i += 1

    flush()
    return entries


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def show_passage(section: str, question: str, passage: str, idx: int, total: int):
    clear()
    print(f"{BOLD}{'─'*70}{RESET}")
    print(f"{CYAN}Abschnitt:{RESET} {section}")
    print(f"{YELLOW}Frage:{RESET} {question}")
    print(f"{BOLD}{'─'*70}{RESET}")
    print()
    print(passage)
    print()
    print(f"{BOLD}{'─'*70}{RESET}")
    print(f"Passage {idx} von {total}")
    print(f"  {GREEN}y{RESET} = relevant    {RED}n{RESET} = skip    e = editieren    q = beenden")
    print(f"{BOLD}{'─'*70}{RESET}")


# ---------------------------------------------------------------------------
# Curate
# ---------------------------------------------------------------------------

def curate(input_path: str, output_dir: str):
    entries = parse_extractions(input_path)

    if not entries:
        print("[FEHLER] Keine Passagen gefunden. Ist die Datei korrekt?", file=sys.stderr)
        sys.exit(1)

    # Alle Passagen flach auflisten
    all_passages = []
    for entry in entries:
        for p in entry["passages"]:
            all_passages.append({
                "section": entry["section"],
                "question": entry["question"],
                "passage": p,
            })

    os.makedirs(output_dir, exist_ok=True)
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_file = os.path.join(output_dir, f"{base}_curated_{run_ts}.md")

    curated = []
    total = len(all_passages)

    for i, item in enumerate(all_passages, 1):
        show_passage(item["section"], item["question"], item["passage"], i, total)

        while True:
            try:
                choice = input("> ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                choice = "q"

            if choice == "y":
                curated.append(item)
                print(f"{GREEN}✓ Gespeichert{RESET}")
                break
            elif choice == "n":
                print(f"{RED}✗ Übersprungen{RESET}")
                break
            elif choice == "e":
                # In $EDITOR öffnen
                editor = os.environ.get("EDITOR", "nano")
                with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
                    tmp.write(item["passage"])
                    tmp_path = tmp.name
                subprocess.call([editor, tmp_path])
                with open(tmp_path, encoding="utf-8") as tmp:
                    item["passage"] = tmp.read().strip()
                os.unlink(tmp_path)
                curated.append(item)
                print(f"{GREEN}✓ Editiert & gespeichert{RESET}")
                break
            elif choice == "q":
                print("\nBeenden. Bisherige Auswahl wird gespeichert.")
                goto_save = True
                break
            else:
                print("y / n / e / q")
        else:
            continue

        if choice == "q":
            break

    # Speichern
    if curated:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(f"# Kuratierte Passagen\n")
            out.write(f"Quelle: `{input_path}`  \n")
            out.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
            out.write(f"Gespeichert: {len(curated)} von {total} Passagen  \n\n---\n\n")

            current_section = None
            for item in curated:
                if item["section"] != current_section:
                    current_section = item["section"]
                    out.write(f"## {current_section}\n\n")
                out.write(f"**Frage:** {item['question']}\n\n")
                out.write(f"{item['passage']}\n\n---\n\n")

        clear()
        print(f"\n{GREEN}Fertig.{RESET} {len(curated)} Passagen gespeichert in:")
        print(f"  {output_file}")
    else:
        clear()
        print("\nKeine Passagen ausgewählt.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Interaktives Kurations-Tool")
    parser.add_argument("--input", required=True,
                        help="Extraktions-Markdown aus output/raw_extractions/")
    parser.add_argument("--output", default="output/curated/",
                        help="Ausgabeverzeichnis (default: output/curated/)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[FEHLER] Datei nicht gefunden: {args.input}", file=sys.stderr)
        sys.exit(1)

    curate(args.input, args.output)


if __name__ == "__main__":
    main()
