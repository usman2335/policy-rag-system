from typing import List, Dict
from langchain_text_splitters.character import RecursiveCharacterTextSplitter


class ChunkerAgent:
    """
    Agent responsible for splitting document text into chunks
    with metadata preservation.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 128):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    def chunk_document(self, document_data: Dict) -> List[Dict]:
        """
        Split document into chunks with metadata.

        Args:
            document_data: Document data from IngestionAgent

        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        chunk_id = 0

        for page in document_data['pages']:
            page_chunks = self._chunk_text(
                text=page['text'],
                page_number=page['page_number'],
                filename=document_data['filename'],
                document_type=document_data['document_type']
            )

            for chunk in page_chunks:
                chunk['chunk_id'] = chunk_id
                chunk['document_id'] = self._generate_document_id(document_data['filename'])
                chunks.append(chunk)
                chunk_id += 1

        return chunks

    def _chunk_text(self, text: str, page_number: int, filename: str, document_type: str) -> List[Dict]:
        """Split text into overlapping chunks."""
        text_chunks = self.text_splitter.split_text(text)
        chunks = []

        for i, chunk_text in enumerate(text_chunks):
            # Create chunk metadata
            chunk_data = {
                'text': chunk_text,
                'page_number': page_number,
                'filename': filename,
                'document_type': document_type,
                'token_count': len(chunk_text.split()),  # Approximate token count
                'char_count': len(chunk_text),
                'start_token': i * (self.chunk_size - self.chunk_overlap),
                'end_token': i * (self.chunk_size - self.chunk_overlap) + len(chunk_text.split())
            }

            chunks.append(chunk_data)

        return chunks

    def _generate_document_id(self, filename: str) -> str:
        """Generate a unique document ID from filename."""
        import hashlib
        return hashlib.md5(filename.encode()).hexdigest()[:16]

    def get_chunk_statistics(self, chunks: List[Dict]) -> Dict:
        """Get statistics about chunks."""
        if not chunks:
            return {}

        total_chunks = len(chunks)
        total_tokens = sum(c['token_count'] for c in chunks)
        total_chars = sum(c['char_count'] for c in chunks)

        return {
            'total_chunks': total_chunks,
            'total_tokens': total_tokens,
            'total_chars': total_chars,
            'avg_tokens_per_chunk': total_tokens / total_chunks,
            'avg_chars_per_chunk': total_chars / total_chunks
        }
