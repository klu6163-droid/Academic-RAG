"""
FAISS-based vector store for dense retrieval.
"""

from pathlib import Path

import numpy as np


class FAISSVectorStore:
    def __init__(self, config):
        self.index_type = config.vector_store.index_type
        self.index_dir = Path(config.vector_store.index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.dimension = config.embedding.dimension
        self._index = None
        self._ids: list[int] = []

    def build(self, embeddings: np.ndarray):
        """Build FAISS index from embeddings."""
        import faiss

        n, d = embeddings.shape
        self.dimension = d

        if self.index_type == "flat_ip":
            # Inner product (cosine similarity for normalized vectors)
            index = faiss.IndexFlatIP(d)
        elif self.index_type == "flat_l2":
            index = faiss.IndexFlatL2(d)
        else:
            index = faiss.IndexFlatIP(d)

        index.add(embeddings.astype(np.float32))
        self._index = index
        self._ids = list(range(n))
        return index

    def save(self, name: str = "evidence"):
        """Save index to disk."""
        if self._index is None:
            return
        import faiss
        path = self.index_dir / f"{name}.index"
        faiss.write_index(self._index, str(path))

    def load(self, name: str = "evidence", num_vectors: int = 0) -> bool:
        """Load index from disk. Returns True if successful."""
        import faiss
        path = self.index_dir / f"{name}.index"
        if not path.exists():
            return False
        index = faiss.read_index(str(path))
        if num_vectors and index.ntotal != num_vectors:
            return False
        self._index = index
        self._ids = list(range(self._index.ntotal))
        return True

    def search(self, query_embedding: np.ndarray, top_k: int = 20) -> list[tuple[int, float]]:
        """Search index and return (index, score) pairs."""
        if self._index is None:
            return []

        q = query_embedding.reshape(1, -1).astype(np.float32)
        scores, indices = self._index.search(q, min(top_k, self._index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                results.append((int(idx), float(score)))
        return results

    @property
    def is_ready(self) -> bool:
        return self._index is not None

    @property
    def num_vectors(self) -> int:
        return self._index.ntotal if self._index else 0
