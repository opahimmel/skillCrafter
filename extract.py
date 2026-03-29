"""
extract.py – Fragenkatalog gegen ChromaDB stellen & Passagen extrahieren.

Usage:
    python extract.py --collection quant_trading \
                      --catalog catalog/questions.md \
                      --output output/raw_extractions/

    # Kompaktes Format für den Craft Loop (weniger Tokens):
    python extract.py --collection quant_trading \
                      --catalog catalog/questions.md \
                      --output output/raw_extractions/ \
                      --compact
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

import chromadb
from sentence_transformers import CrossEncoder, SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "intfloat/multilingual-e5-base"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TOP_K = 10
RERANK_TOP_N = 5
MIN_SCORE = 0.70
SCORE_STRONG = 0.75


# ---------------------------------------------------------------------------
# Fragenkatalog einlesen
# ---------------------------------------------------------------------------

def parse_questions(catalog_path: str) -> list[dict]:
    """
    Liest Probes aus einem Markdown-Katalog.
    Unterstützt drei Formate:
      Format A (einfach):     - Frage als Bullet Point
      Format B (RAG-opt.):    **query:** "Frage als langer Text"
      Format C (Multi-Probe): - FRAGE: ... / - STATEMENT: ... / - KEYWORDS: ...
    Abschnitte werden über ## Heading erkannt.
    """
    questions = []
    current_section = "Allgemein"

    _query_line = re.compile(r'^\*\*query:\*\*\s*"?(.+?)"?\s*$')
    _probe_line = re.compile(r'^-\s+(FRAGE|STATEMENT|KEYWORDS):\s*(.+)$')

    with open(catalog_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            # Abschnitts-Header (## aber nicht ###)
            if re.match(r"^## [^#]", line):
                current_section = line[3:].strip()
            elif line.startswith("# "):
                current_section = line[2:].strip()
            # Format C: Multi-Probe (FRAGE/STATEMENT/KEYWORDS)
            elif m := _probe_line.match(line):
                probe_type = m.group(1)
                probe_text = m.group(2).strip()
                if probe_text:
                    questions.append({
                        "section": current_section,
                        "question": probe_text,
                        "probe_type": probe_type,
                    })
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

def extract(collection_name: str, catalog_path: str, output_dir: str, top_k: int,
            min_score: float = 0.0, compact: bool = False):
    # Modelle laden
    print(f"Lade Embedding-Modell '{MODEL_NAME}' ...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Lade Reranker '{RERANK_MODEL}' ...")
    reranker = CrossEncoder(RERANK_MODEL)

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
    print(f"Retrieval: Top-{top_k} → Rerank → Top-{RERANK_TOP_N} | Min-Score: >= {min_score}")
    if compact:
        print("Modus: KOMPAKT (für Craft Loop)")
    print()

    os.makedirs(output_dir, exist_ok=True)

    # Zeitstempel für diesen Lauf
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"{collection_name}_{run_ts}.md")

    # Im Kompakt-Modus: JSON-Sidecar mit Chunk-IDs für Duplikat-Check
    all_passages = []  # für JSON-Sidecar

    with open(output_file, "w", encoding="utf-8") as out:
        if compact:
            out.write(f"# {collection_name} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        else:
            out.write(f"# Extraktion: {collection_name}\n")
            out.write(f"Katalog: `{catalog_path}`  \n")
            out.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n")
            out.write(f"Top-K: {top_k}  \n\n---\n\n")

        current_section = None

        for i, item in enumerate(questions, 1):
            # Abschnitts-Header schreiben wenn neu
            if not compact and item["section"] != current_section:
                current_section = item["section"]
                out.write(f"## {current_section}\n\n")

            question = item["question"]
            print(f"[{i}/{len(questions)}] {question}")

            # Query-Embedding (multilingual-e5 asymmetrisches Retrieval: query prefix)
            query_embedding = model.encode(
                f"query: {question}",
                normalize_embeddings=True,
            ).tolist()

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count()),
                include=["documents", "metadatas", "distances"],
            )

            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            if compact:
                out.write(f"## Q{i}: {question}\n")
            else:
                out.write(f"### Frage {i}: {question}\n\n")

            if not docs:
                if compact:
                    out.write("KEINE TREFFER\n\n")
                else:
                    out.write("_Keine Passagen gefunden._\n\n")
                continue

            # Pre-filter: nur Kandidaten über min_score
            candidates = []
            for doc, meta, dist in zip(docs, metas, distances):
                similarity = round(1 - dist, 4)
                if similarity >= min_score:
                    candidates.append({"doc": doc, "meta": meta, "similarity": similarity})

            if not candidates:
                if compact:
                    out.write(f"KEIN MATCH (alle unter {min_score})\n\n")
                else:
                    out.write(f"_KEIN AUSREICHENDER MATCH — alle {len(docs)} Kandidaten unter Score {min_score}. Wissenslücke in der Bibliothek oder Frage zu spezifisch._\n\n")
                continue

            # Reranking: Cross-Encoder bewertet Query+Passage gemeinsam
            pairs = [[question, c["doc"]] for c in candidates]
            rerank_scores = reranker.predict(pairs)
            for idx, c in enumerate(candidates):
                c["rerank_score"] = float(rerank_scores[idx])
            candidates.sort(key=lambda c: c["rerank_score"], reverse=True)
            candidates = candidates[:RERANK_TOP_N]

            written = 0
            for c in candidates:
                source = c["meta"].get("source", "unbekannt")
                chunk_idx = c["meta"].get("chunk_index", "?")
                chunk_id = f"{source}:{chunk_idx}"
                written += 1

                # Für JSON-Sidecar sammeln
                all_passages.append({
                    "chunk_id": chunk_id,
                    "question_idx": i,
                    "question": question,
                    "similarity": c["similarity"],
                    "rerank_score": c["rerank_score"],
                    "source": source,
                    "chunk_index": chunk_idx,
                })

                if compact:
                    out.write(f"[{chunk_id}|cos={c['similarity']}|rr={c['rerank_score']:.3f}] ")
                    out.write(f"{c['doc'].strip()}\n\n")
                else:
                    score_label = "STARK" if c["similarity"] >= SCORE_STRONG else "AUSREICHEND"
                    out.write(f"**Passage {written}** | Quelle: `{source}` | Chunk #{chunk_idx} | Cosine: {c['similarity']} [{score_label}] | Rerank: {c['rerank_score']:.3f}\n\n")
                    out.write(f"> {c['doc'].strip()}\n\n")

            if not compact:
                out.write("---\n\n")

    # JSON-Sidecar speichern (für programmatischen Duplikat-Check)
    if compact:
        sidecar_file = output_file.replace(".md", ".json")
        with open(sidecar_file, "w", encoding="utf-8") as f:
            json.dump({
                "collection": collection_name,
                "timestamp": run_ts,
                "total_passages": len(all_passages),
                "passages": all_passages,
            }, f, indent=2, ensure_ascii=False)
        print(f"Sidecar gespeichert: {sidecar_file}")

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
    parser.add_argument("--compact", action="store_true",
                        help="Kompaktes Output-Format für den Craft Loop (weniger Tokens, JSON-Sidecar)")
    args = parser.parse_args()

    if not os.path.isfile(args.catalog):
        print(f"[FEHLER] Katalog nicht gefunden: {args.catalog}", file=sys.stderr)
        sys.exit(1)

    extract(args.collection, args.catalog, args.output, args.top_k, args.min_score, args.compact)


if __name__ == "__main__":
    main()
