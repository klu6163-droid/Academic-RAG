"""
Embedding engine using sentence-transformers.
Computes and caches embeddings for the evidence corpus.
"""

import json
from pathlib import Path

import numpy as np


class EmbeddingEngine:
    def __init__(self, config):
        self.model_name = config.embedding.model
        self.dimension = config.embedding.dimension
        self.batch_size = config.embedding.batch_size
        self.cache_dir = Path(config.embedding.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._embeddings: np.ndarray | None = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            try:
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception:
                self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str], show_progress: bool = False) -> np.ndarray:
        """Encode texts to normalized embeddings."""
        model = self._get_model()
        return model.encode(texts, show_progress_bar=show_progress, normalize_embeddings=True, batch_size=self.batch_size)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query."""
        model = self._get_model()
        return model.encode([query], normalize_embeddings=True)

    def load_or_compute(self, texts: list[str], cache_key: str = "evidence") -> np.ndarray:
        """Load cached embeddings or compute and cache."""
        cache_path = self.cache_dir / f"{cache_key}_embeddings.npy"

        if cache_path.exists():
            emb = np.load(str(cache_path))
            if emb.shape[0] == len(texts) and emb.shape[1] == self.dimension:
                self._embeddings = emb
                return emb

        emb = self.encode(texts, show_progress=True)
        np.save(str(cache_path), emb)
        self._embeddings = emb
        return emb

    @property
    def embeddings(self) -> np.ndarray | None:
        return self._embeddings
