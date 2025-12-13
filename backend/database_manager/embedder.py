import os
from typing import List, Iterable, Optional
from sentence_transformers import SentenceTransformer


class EmbeddingsGenerator:
    def __init__(self, model_name: Optional[str] = "all-MiniLM-L6-v2", dim: Optional[int] = None):
        self.model_name = model_name
        self.dim = int(dim or os.getenv("EMBEDDING_DIM", 384))
        self.embedding_model = SentenceTransformer(self.model_name)

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        texts = list(texts)
        if len(texts) == 0:
            return []

        embeddings = self.embedding_model.encode(texts, show_progress_bar=False, convert_to_numpy=False)
        return [list(map(float, v)) for v in embeddings]
