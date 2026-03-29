"""
chunk_index.py – Duplikat-Check für den Craft Loop ohne LLM-Tokens.

Verwaltet eine chunk_index.json pro Skill die trackt welche Chunks
bereits als Insights gespeichert wurden.

Usage:
    from chunk_index import ChunkIndex

    idx = ChunkIndex("skills/mein_skill/chunk_index.json")
    if not idx.is_known("buch.pdf:34"):
        # → neuer Chunk, bewerten lassen
        idx.add("buch.pdf:34", insight_number=5, score=4)
    idx.save()
"""

import json
import os


class ChunkIndex:
    """Schneller O(1) Duplikat-Check via JSON-Datei."""

    def __init__(self, path: str):
        self.path = path
        self._data: dict[str, dict] = {}
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                self._data = json.load(f)

    def is_known(self, chunk_id: str) -> bool:
        return chunk_id in self._data

    def add(self, chunk_id: str, insight_number: int, score: int, run: int = 0):
        self._data[chunk_id] = {
            "insight": insight_number,
            "score": score,
            "run": run,
        }

    def next_insight_number(self) -> int:
        if not self._data:
            return 1
        return max(entry["insight"] for entry in self._data.values()) + 1

    def count(self) -> int:
        return len(self._data)

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def filter_new(self, extraction_json_path: str) -> list[dict]:
        """
        Liest eine Extraction-Sidecar-JSON und gibt nur Passagen zurück
        deren chunk_id noch nicht im Index ist.

        Returns: Liste von Passage-Dicts (chunk_id, question, similarity, etc.)
        """
        with open(extraction_json_path, encoding="utf-8") as f:
            data = json.load(f)

        seen_in_batch = set()
        new_passages = []
        for p in data["passages"]:
            cid = p["chunk_id"]
            if cid not in self._data and cid not in seen_in_batch:
                seen_in_batch.add(cid)
                new_passages.append(p)

        return new_passages
