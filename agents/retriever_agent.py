from typing import List, Dict, Optional
from agents.embedding_agent import EmbeddingAgent
from agents.vector_db_agent import VectorDBAgent
from config import settings


class RetrieverAgent:
    """
    Agent responsible for retrieving relevant chunks for a given query.
    Combines embedding generation and vector database querying.
    """

    def __init__(self):
        self.embedding_agent = EmbeddingAgent()
        self.vector_db_agent = VectorDBAgent()

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_by_document: Optional[str] = None,
        filter_by_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User's question
            top_k: Number of chunks to retrieve
            filter_by_document: Optional filename filter
            filter_by_type: Optional document type filter

        Returns:
            List of relevant chunks with metadata
        """
        if top_k is None:
            top_k = settings.top_k_chunks

        # Generate query embedding
        query_embedding = self.embedding_agent.embed_query(query)

        # Prepare metadata filter
        filter_metadata = {}
        if filter_by_document:
            filter_metadata['filename'] = filter_by_document
        if filter_by_type:
            filter_metadata['document_type'] = filter_by_type

        # Query vector database
        chunks = self.vector_db_agent.query(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata if filter_metadata else None
        )

        # Post-process chunks
        for chunk in chunks:
            chunk['similarity_score'] = 1 - chunk['distance']  # Convert distance to similarity

        return chunks

    def rerank_chunks(self, chunks: List[Dict], query: str) -> List[Dict]:
        """
        Optional: Re-rank retrieved chunks for better relevance.
        This is a simple implementation that could be enhanced with
        a cross-encoder model.

        Args:
            chunks: Retrieved chunks
            query: Original query

        Returns:
            Re-ranked chunks
        """
        # For now, just return chunks as-is (already ranked by similarity)
        # In a full implementation, you could use a cross-encoder here
        return chunks

    def format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into a context string for the LLM.

        Args:
            chunks: Retrieved chunks

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, chunk in enumerate(chunks, start=1):
            metadata = chunk['metadata']
            context_part = f"""[DOC: {metadata['filename']} | page: {metadata['page_number']} | paragraph: {metadata['chunk_id']}]
{chunk['text']}
"""
            context_parts.append(context_part)

        return "\n".join(context_parts)

    def get_citations(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract citation information from chunks.

        Args:
            chunks: Retrieved chunks

        Returns:
            List of citation dictionaries
        """
        citations = []

        for chunk in chunks:
            metadata = chunk['metadata']
            citation = {
                'filename': metadata['filename'],
                'page_number': metadata['page_number'],
                'chunk_id': metadata['chunk_id'],
                'text_snippet': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            }
            citations.append(citation)

        return citations
