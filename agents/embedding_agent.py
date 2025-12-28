from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
from config import settings


class EmbeddingAgent:
    """
    Agent responsible for generating embeddings for text chunks.
    Uses local sentence-transformers models (Hugging Face).
    """

    def __init__(self):
        # Always use local embeddings (Hugging Face)
        print(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self.model_name = settings.embedding_model

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for all chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Chunks with added 'embedding' field
        """
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self._embed_with_local(texts)

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding

        return chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        return self._embed_with_local([query])[0]

    def _embed_with_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local sentence-transformers model."""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.model.get_sentence_embedding_dimension()
