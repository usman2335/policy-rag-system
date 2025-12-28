from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np
from config import settings
import json


class VectorDBAgent:
    """
    Agent responsible for managing the vector database.
    Supports ChromaDB for persistent storage.
    """

    def __init__(self, collection_name: str = "university_policies"):
        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.vector_db_path,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add chunks with embeddings to the vector database.

        Args:
            chunks: List of chunk dictionaries with 'embedding' field
        """
        if not chunks:
            return

        ids = [f"{chunk['document_id']}_{chunk['chunk_id']}" for chunk in chunks]
        embeddings = [chunk['embedding'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]

        # Prepare metadata (ChromaDB doesn't support nested dicts)
        metadatas = []
        for chunk in chunks:
            metadata = {
                'filename': chunk['filename'],
                'page_number': chunk['page_number'],
                'document_type': chunk['document_type'],
                'chunk_id': chunk['chunk_id'],
                'document_id': chunk['document_id'],
                'token_count': chunk['token_count'],
                'char_count': chunk['char_count']
            }
            metadatas.append(metadata)

        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

    def query(
        self,
        query_embedding: List[float],
        top_k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query the vector database for similar chunks.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of matching chunks with metadata and similarity scores
        """
        if top_k is None:
            top_k = settings.top_k_chunks

        where_filter = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )

        # Format results
        chunks = []
        for i in range(len(results['ids'][0])):
            chunk = {
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            chunks.append(chunk)

        return chunks

    def delete_document(self, document_id: str) -> None:
        """
        Delete all chunks from a specific document.

        Args:
            document_id: Document ID to delete
        """
        self.collection.delete(
            where={"document_id": document_id}
        )

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'total_chunks': count
        }

    def list_documents(self) -> List[Dict]:
        """List all unique documents in the collection."""
        # Get all items (limited to metadata)
        results = self.collection.get()

        # Extract unique documents
        documents = {}
        for metadata in results['metadatas']:
            doc_id = metadata['document_id']
            if doc_id not in documents:
                documents[doc_id] = {
                    'document_id': doc_id,
                    'filename': metadata['filename'],
                    'document_type': metadata['document_type'],
                    'chunk_count': 1
                }
            else:
                documents[doc_id]['chunk_count'] += 1

        return list(documents.values())

    def clear_collection(self) -> None:
        """Clear all data from the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
