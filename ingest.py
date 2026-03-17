"""
ingest.py – PDFs einlesen, chunken & in ChromaDB vektorisieren.

Usage:
    python ingest.py --source sources/buch.pdf --collection quant_trading
    python ingest.py --source sources/*.pdf --collection quant_trading
"""

import argparse
import glob
import hashlib
import os
import re
import sys

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CHUNK_SIZE = 900        # Zeichen (nicht Token) – größer = vollständigere Passagen
CHUNK_OVERLAP = 200     # ~22% Overlap – verhindert Absatz-Splits
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
MODEL_NAME = "intfloat/multilingual-e5-base"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Überschriften die eine Bibliographie einleiten
_BIBLIO_HEADERS = re.compile(
    r"^\s*(references|literatur(verzeichnis)?|bibliography|bibliographie"
    r"|quellen(verzeichnis)?|literatur\s*&\s*quellen|works\s+cited)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Seiten-Header: TOC, Vorwort, Inhaltsverzeichnis
_FRONT_MATTER_HEADERS = re.compile(
    r"^\s*(contents|table\s+of\s+contents|inhaltsverzeichnis|inhalt"
    r"|foreword|vorwort|preface|acknowledgements?|danksagung"
    r"|about\s+the\s+author|list\s+of\s+(figures|tables|abbreviations))\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# TOC-Zeile: endet mit Seitenzahl, hat Punkt-Leader oder kurze Einträge + Zahl
_TOC_LINE = re.compile(
    r"(\.{3,}\s*\d+\s*$"          # Dot leader: "Kapitel 1 ..... 23"
    r"|\s{2,}\d{1,4}\s*$"          # Trailing page number mit Whitespace
    r"|^\s*\d+\s*$)"               # Zeile ist nur eine Zahl
)

# Citation-Pattern: "[1]", "(Author, 2020)", "doi:", typische Literaturzeilen
_CITATION_LINE = re.compile(
    r"(\[\d+\]|doi:\s*10\.\d{4}|\(\w[\w\s]+,\s*\d{4}\)|^\s*\d{1,3}\.\s+\w)"
)


def is_bibliography_page(text: str) -> bool:
    """Gibt True zurück wenn die Seite eine Bibliographie-Überschrift enthält."""
    return bool(_BIBLIO_HEADERS.search(text))


def is_front_matter_page(text: str) -> bool:
    """Gibt True zurück wenn die Seite ein TOC, Vorwort oder Inhaltsverzeichnis ist."""
    return bool(_FRONT_MATTER_HEADERS.search(text))


def is_noise_chunk(text: str) -> bool:
    """Filtert TOC-Chunks, Index-Seiten und Seitenzahlen-Listen."""
    if len(text) < 150:
        return True

    # Zu viele Ziffern → Seitenzahlen-Liste oder Index
    digit_ratio = sum(c.isdigit() for c in text) / len(text)
    if digit_ratio > 0.4:
        return True

    # TOC-Muster: viele Zeilen enden mit Seitenzahlen
    lines = [l for l in text.splitlines() if l.strip()]
    if lines:
        toc_hits = sum(1 for l in lines if _TOC_LINE.search(l))
        if (toc_hits / len(lines)) >= 0.4:
            return True

    return False


def is_citation_heavy(chunk: str, threshold: float = 0.5) -> bool:
    """Gibt True zurück wenn mehr als threshold der Zeilen Citation-Patterns sind."""
    lines = [l for l in chunk.splitlines() if l.strip()]
    if not lines:
        return False
    hits = sum(1 for l in lines if _CITATION_LINE.search(l))
    return (hits / len(lines)) >= threshold


def load_pdf(path: str) -> str:
    """
    Extrahiert Text aus einem PDF – stoppt beim ersten Bibliographie-Abschnitt.
    Gibt den bereinigten Text zurück.
    """
    try:
        reader = PdfReader(path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if is_bibliography_page(text):
                print(f"  [FILTER] Bibliographie erkannt auf Seite {i+1} – Rest wird übersprungen")
                break
            if is_front_matter_page(text):
                print(f"  [FILTER] Front-Matter übersprungen (Seite {i+1})")
                continue
            pages.append(text)
        return "\n".join(pages)
    except Exception as e:
        print(f"  [FEHLER] Kann {path} nicht lesen: {e}", file=sys.stderr)
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Teilt Text in überlappende Chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


def stable_id(source: str, index: int) -> str:
    """Deterministischer Chunk-ID aus Dateiname + Index."""
    raw = f"{os.path.basename(source)}::{index}"
    return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def ingest(sources: list[str], collection_name: str, chunk_size: int, overlap: int):
    # Embedding-Modell laden
    print(f"Lade Embedding-Modell '{MODEL_NAME}' ...")
    model = SentenceTransformer(MODEL_NAME)

    # ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    total_chunks = 0

    for source in sources:
        if not os.path.isfile(source):
            print(f"  [SKIP] Datei nicht gefunden: {source}", file=sys.stderr)
            continue

        print(f"\nVerarbeite: {source}")
        text = load_pdf(source)
        if not text:
            continue

        chunks_raw = chunk_text(text, chunk_size, overlap)
        chunks = [c for c in chunks_raw if not is_citation_heavy(c) and not is_noise_chunk(c)]
        skipped = len(chunks_raw) - len(chunks)
        if skipped:
            print(f"  {skipped} Noise-Chunks gefiltert (TOC/Index/Bibliographie)")
        print(f"  {len(chunks)} Chunks nach Filter")

        # Embeddings berechnen
        print(f"  Vektorisiere ...")
        # multilingual-e5 erwartet ein Prefix für asymmetrisches Retrieval
        prefixed = [f"passage: {c}" for c in chunks]
        embeddings = model.encode(prefixed, show_progress_bar=True, normalize_embeddings=True)

        # In ChromaDB speichern (in Batches um Memory zu schonen)
        ids = [stable_id(source, i) for i in range(len(chunks))]
        metadatas = [{"source": os.path.basename(source), "chunk_index": i} for i in range(len(chunks))]

        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            collection.upsert(
                ids=ids[i:i+batch_size],
                documents=chunks[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size].tolist(),
                metadatas=metadatas[i:i+batch_size],
            )

        total_chunks += len(chunks)
        print(f"  ✓ {len(chunks)} Chunks gespeichert in Collection '{collection_name}'")

    print(f"\nFertig. {total_chunks} Chunks total in '{collection_name}'.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PDF → ChromaDB Ingestion")
    parser.add_argument("--source", required=True, nargs="+",
                        help="PDF-Datei(en) oder Glob-Muster (z.B. sources/*.pdf)")
    parser.add_argument("--collection", required=True,
                        help="Name der ChromaDB-Collection")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE,
                        help=f"Chunk-Größe in Zeichen (default: {CHUNK_SIZE})")
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP,
                        help=f"Overlap in Zeichen (default: {CHUNK_OVERLAP})")
    args = parser.parse_args()

    # Glob-Muster auflösen
    resolved = []
    for pattern in args.source:
        matches = glob.glob(pattern)
        if matches:
            resolved.extend(matches)
        else:
            resolved.append(pattern)  # wird später als "nicht gefunden" behandelt

    ingest(resolved, args.collection, args.chunk_size, args.overlap)


if __name__ == "__main__":
    main()
