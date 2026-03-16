"""
skill.py – Zentrales CLI für das Skill Crafting System.

Jeder Skill bekommt einen eigenen Ordner unter skills/<name>/ und eine
eigene ChromaDB-Collection.

Befehle:
    python skill.py new <name>          Neuen Skill anlegen
    python skill.py ingest <name>       PDFs aus skills/<name>/sources/ einlesen
    python skill.py extract <name>      Extraktion starten
    python skill.py curate <name>       Interaktiv kuratieren (letzten Extraction-Run)
    python skill.py list                Alle Skills + Status anzeigen
    python skill.py delete <name>       Collection + Ordner löschen (mit Bestätigung)
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
PYTHON = sys.executable

QUESTIONS_TEMPLATE = """\
# Fragenkatalog: {name}
<!-- Ersetze die Beispielfragen mit deinen eigenen. -->
<!-- Fragen als Bullet Points (- oder *), Abschnitte mit ## -->

## Grundlagen

- Was sind die fundamentalen Prinzipien dieses Gebiets?
- Welche Konzepte werden am häufigsten missverstanden?
- Was unterscheidet Anfänger von Experten hier?

## Entscheidungslogik

- Wann tut ein Experte X statt Y?
- Welche Faktoren sind für die Kernentscheidung entscheidend?

## Fehler & Grenzen

- Was sind die häufigsten Anfängerfehler?
- Wann funktioniert dieser Ansatz nicht?

## Verifikation

- Wie prüft ein Experte ob sein Ergebnis korrekt ist?
- Was sind Warnsignale dass etwas falsch läuft?

## Implementierung

- Wie geht man von Theorie zu Praxis?
- Welche konkreten Schritte folgen aufeinander?
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def skill_dir(name: str) -> str:
    return os.path.join(SKILLS_DIR, name)


def skill_exists(name: str) -> bool:
    return os.path.isdir(skill_dir(name))


def require_skill(name: str):
    if not skill_exists(name):
        print(f"[FEHLER] Skill '{name}' nicht gefunden. Mit 'new' anlegen.", file=sys.stderr)
        sys.exit(1)


def latest_extraction(name: str) -> str | None:
    pattern = os.path.join(skill_dir(name), "extractions", f"{name}_*.md")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


def run(cmd: list[str]):
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# Befehle
# ---------------------------------------------------------------------------

def cmd_new(name: str):
    d = skill_dir(name)
    if skill_exists(name):
        print(f"[INFO] Skill '{name}' existiert bereits unter {d}")
        return

    for sub in ["sources", "extractions", "curated"]:
        os.makedirs(os.path.join(d, sub), exist_ok=True)

    questions_path = os.path.join(d, "questions.md")
    with open(questions_path, "w", encoding="utf-8") as f:
        f.write(QUESTIONS_TEMPLATE.format(name=name))

    skill_md = os.path.join(d, "skill.md")
    with open(skill_md, "w", encoding="utf-8") as f:
        f.write(f"# Skill: {name}\n\n")
        f.write("## Mental Model\n\n_noch leer_\n\n")
        f.write("## Decision Framework\n\n_noch leer_\n\n")
        f.write("## Core Patterns\n\n_noch leer_\n\n")
        f.write("## Hard Constraints\n\n_noch leer_\n\n")
        f.write("## Verification\n\n_noch leer_\n\n")

    print(f"✓ Skill '{name}' angelegt unter {d}")
    print(f"\nNächste Schritte:")
    print(f"  1. PDFs nach skills/{name}/sources/ kopieren")
    print(f"  2. Fragen in skills/{name}/questions.md schreiben")
    print(f"  3. python skill.py ingest {name}")
    print(f"  4. python skill.py extract {name}")
    print(f"  5. python skill.py curate {name}")


def cmd_ingest(name: str, chunk_size: int, overlap: int, file: str = None):
    require_skill(name)
    sources_dir = os.path.join(skill_dir(name), "sources")

    if file:
        # Einzelne Datei – Pfad relativ zu sources/ oder absolut
        if not os.path.isabs(file):
            file = os.path.join(sources_dir, file)
        if not os.path.isfile(file):
            print(f"[FEHLER] Datei nicht gefunden: {file}", file=sys.stderr)
            sys.exit(1)
        pdfs = [file]
    else:
        pdfs = glob.glob(os.path.join(sources_dir, "*.pdf"))
        if not pdfs:
            print(f"[FEHLER] Keine PDFs in skills/{name}/sources/ gefunden.", file=sys.stderr)
            sys.exit(1)

    print(f"Ingest: {len(pdfs)} PDF(s) → Collection '{name}'")
    run([
        PYTHON, "ingest.py",
        "--source", *pdfs,
        "--collection", name,
        "--chunk-size", str(chunk_size),
        "--overlap", str(overlap),
    ])


def cmd_extract(name: str, top_k: int, min_score: float):
    require_skill(name)
    catalog = os.path.join(skill_dir(name), "questions.md")
    output_dir = os.path.join(skill_dir(name), "extractions")

    if not os.path.isfile(catalog):
        print(f"[FEHLER] Kein questions.md in skills/{name}/", file=sys.stderr)
        sys.exit(1)

    cmd = [
        PYTHON, "extract.py",
        "--collection", name,
        "--catalog", catalog,
        "--output", output_dir,
        "--top-k", str(top_k),
    ]
    if min_score > 0:
        cmd += ["--min-score", str(min_score)]

    run(cmd)


def cmd_curate(name: str):
    require_skill(name)
    extraction = latest_extraction(name)

    if not extraction:
        print(f"[FEHLER] Keine Extraktion gefunden. Erst 'extract {name}' ausführen.", file=sys.stderr)
        sys.exit(1)

    curated_dir = os.path.join(skill_dir(name), "curated")
    print(f"Kuratiere: {extraction}")
    run([PYTHON, "curate.py", "--input", extraction, "--output", curated_dir])


def cmd_list():
    if not os.path.isdir(SKILLS_DIR):
        print("Noch keine Skills angelegt.")
        return

    skills = sorted(
        s for s in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, s)) and not s.startswith(".")
    )
    if not skills:
        print("Noch keine Skills angelegt.")
        return

    # ChromaDB collections prüfen
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collections = {c.name for c in client.list_collections()}
    except Exception:
        collections = set()

    print(f"{'Skill':<25} {'Collection':<12} {'PDFs':<6} {'Extractions':<14} {'Curated'}")
    print("─" * 75)
    for name in skills:
        d = skill_dir(name)
        pdfs = len(glob.glob(os.path.join(d, "sources", "*.pdf")))
        extractions = len(glob.glob(os.path.join(d, "extractions", "*.md")))
        curated = len(glob.glob(os.path.join(d, "curated", "*.md")))
        db = "✓" if name in collections else "–"
        print(f"{name:<25} {db:<12} {pdfs:<6} {extractions:<14} {curated}")


def cmd_delete(name: str):
    require_skill(name)
    print(f"[WARNUNG] Löscht Collection '{name}' aus ChromaDB und den Ordner skills/{name}/")
    confirm = input("Sicher? (ja/nein): ").strip().lower()
    if confirm != "ja":
        print("Abgebrochen.")
        return

    # ChromaDB Collection löschen
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        client.delete_collection(name)
        print(f"  ✓ Collection '{name}' gelöscht")
    except Exception as e:
        print(f"  [INFO] Collection nicht gefunden oder bereits gelöscht: {e}")

    # Ordner löschen
    shutil.rmtree(skill_dir(name))
    print(f"  ✓ Ordner skills/{name}/ gelöscht")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Skill Crafting System – zentrales CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # new
    p_new = sub.add_parser("new", help="Neuen Skill anlegen")
    p_new.add_argument("name")

    # ingest
    p_ingest = sub.add_parser("ingest", help="PDFs einlesen")
    p_ingest.add_argument("name")
    p_ingest.add_argument("--file", default=None,
                          help="Einzelnes PDF aus sources/ (ohne Pfad, nur Dateiname)")
    p_ingest.add_argument("--chunk-size", type=int, default=512)
    p_ingest.add_argument("--overlap", type=int, default=128)

    # extract
    p_extract = sub.add_parser("extract", help="Extraktion starten")
    p_extract.add_argument("name")
    p_extract.add_argument("--top-k", type=int, default=5)
    p_extract.add_argument("--min-score", type=float, default=0.0)

    # curate
    p_curate = sub.add_parser("curate", help="Letzte Extraktion kuratieren")
    p_curate.add_argument("name")

    # list
    sub.add_parser("list", help="Alle Skills anzeigen")

    # delete
    p_delete = sub.add_parser("delete", help="Skill löschen")
    p_delete.add_argument("name")

    args = parser.parse_args()

    if args.cmd == "new":
        cmd_new(args.name)
    elif args.cmd == "ingest":
        cmd_ingest(args.name, args.chunk_size, args.overlap, args.file)
    elif args.cmd == "extract":
        cmd_extract(args.name, args.top_k, args.min_score)
    elif args.cmd == "curate":
        cmd_curate(args.name)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "delete":
        cmd_delete(args.name)


if __name__ == "__main__":
    main()
