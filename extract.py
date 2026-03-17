"""
extract.py – Fragenkatalog gegen ChromaDB stellen & Passagen extrahieren.

Usage:
    python extract.py --collection quant_trading \
                      --catalog catalog/questions.md \
                      --output output/raw_extractions/
"""

import argparse
import os
import re
import sys
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "intfloat/multilingual-e5-base"
TOP_K = 10
MIN_SCORE = 0.70
SCORE_STRONG = 0.75
MAX_CHUNKS_PER_SOURCE = 2


# ---------------------------------------------------------------------------
# Fragenkatalog einlesen
# ---------------------------------------------------------------------------

def parse_questions(catalog_path: str) -> list[dict]:
    """
    Liest Fragen aus einem Markdown-Katalog.
    Unterstützt zwei Formate:
      Format A (einfach):   - Frage als Bullet Point
      Format B (RAG-opt.):  **query:** "Frage als langer Text"
    Abschnitte werden über ## Heading erkannt.
    """
    questions = []
    current_section = "Allgemein"

    _query_line = re.compile(r'^\*\*query:\*\*\s*"?(.+?)"?\s*$')

    with open(catalog_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            # Abschnitts-Header (## aber nicht ###)
            if re.match(r"^## [^#]", line):
                current_section = line[3:].strip()
            elif line.startswith("# "):
                current_section = line[2:].strip()
            # Format B: **query:** "..."
            elif m := _query_line.match(line):
                question = m.group(1).strip()
                if question:
                    questions.append({"section": current_section, "question": question})
            # Format A: - Frage oder * Frage
            elif re.match(r"^[-*]\s+.+", line):
                question = re.sub(r"^[-*]\s+", "", line).strip()
                if question:
                    questions.append({"section": current_section, "question": question})

    return questions


# ---------------------------------------------------------------------------
# Extraktion
# ---------------------------------------------------------------------------

def extract(collection_name: str, catalog_path: str, output_dir: str, top_k: int, min_score: float = 0.0):
    # Modell laden
    print(f"Lade Embedding-Modell '{MODEL_NAME}' ...")
    model = SentenceTransformer(MODEL_NAME)

    # ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        print(f"[FEHLER] Collection '{collection_name}' nicht gefunden.", file=sys.stderr)
        print("Bitte zuerst ingest.py ausführen.", file=sys.stderr)
        sys.exit(1)

    # Fragen laden
    questions = parse_questions(catalog_path)
    if not questions:
        print("[FEHLER] Keine Fragen im Katalog gefunden.", file=sys.stderr)
        sys.exit(1)

    print(f"{len(questions)} Fragen geladen aus '{catalog_path}'")
    print(f"Collection: '{collection_name}' ({collection.count()} Chunks)")
    print(f"Min-Score: >= {min_score} | Max pro Quelle: {MAX_CHUNKS_PER_SOURCE}")
    print()

    os.makedirs(output_dir, exist_ok=True)

    # Zeitstempel für diesen Lauf
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{collection_name}_{run_ts}.md")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"# Extraktion: {collection_name}\n")
        out.write(f"Katalog: `{catalog_path}`  \n")
        out.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
        out.write(f"Top-K: {top_k}  \n\n---\n\n")

        current_section = None

        for i, item in enumerate(questions, 1):
            # Abschnitts-Header schreiben wenn neu
            if item["section"] != current_section:
                current_section = item["section"]
                out.write(f"## {current_section}\n\n")

            question = item["question"]
            print(f"[{i}/{len(questions)}] {question}")

            # Query-Embedding (nomic asymmetrisches Retrieval: query prefix)
            query_embedding = model.encode(
                f"query: {question}",
                normalize_embeddings=True,
            ).tolist()

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count()),
                include=["documents", "metadatas", "distances"],
            )

            out.write(f"### Frage {i}: {question}\n\n")

            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            if not docs:
                out.write("_Keine Passagen gefunden._\n\n")
                continue

            written = 0
            source_counts: dict[str, int] = {}
            for rank, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
                similarity = round(1 - dist, 4)
                if similarity < min_score:
                    continue
                source = meta.get("source", "unbekannt")
                if source_counts.get(source, 0) >= MAX_CHUNKS_PER_SOURCE:
                    continue
                source_counts[source] = source_counts.get(source, 0) + 1
                chunk_idx = meta.get("chunk_index", "?")

                written += 1
                if similarity >= SCORE_STRONG:
                    score_label = "STARK"
                else:
                    score_label = "AUSREICHEND"
                out.write(f"**Passage {written}** | Quelle: `{source}` | Chunk #{chunk_idx} | Score: {similarity} [{score_label}]\n\n")
                out.write(f"> {doc.strip()}\n\n")

            if written == 0:
                out.write(f"_KEIN AUSREICHENDER MATCH — alle {len(docs)} Kandidaten unter Score {min_score}. Wissenslücke in der Bibliothek oder Frage zu spezifisch._\n\n")

            out.write("---\n\n")

    print(f"\nFertig. Extraktion gespeichert: {output_file}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ChromaDB → Extraktion per Fragenkatalog")
    parser.add_argument("--collection", required=True,
                        help="Name der ChromaDB-Collection")
    parser.add_argument("--catalog", required=True,
                        help="Pfad zur questions.md Datei")
    parser.add_argument("--output", default="output/raw_extractions/",
                        help="Ausgabeverzeichnis (default: output/raw_extractions/)")
    parser.add_argument("--top-k", type=int, default=TOP_K,
                        help=f"Anzahl Kandidaten die abgerufen werden (default: {TOP_K})")
    parser.add_argument("--min-score", type=float, default=MIN_SCORE,
                        help=f"Minimaler Similarity-Score – unter diesem Wert = kein Match (default: {MIN_SCORE})")
    args = parser.parse_args()

    if not os.path.isfile(args.catalog):
        print(f"[FEHLER] Katalog nicht gefunden: {args.catalog}", file=sys.stderr)
        sys.exit(1)

    extract(args.collection, args.catalog, args.output, args.top_k, args.min_score)


if __name__ == "__main__":
    main()
