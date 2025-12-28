import os
from typing import Dict, List, Optional
import fitz  # PyMuPDF
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from datetime import datetime


class IngestionAgent:
    """
    Agent responsible for extracting text from documents (PDF, DOCX)
    with OCR support for scanned documents.
    """

    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc']

    def process_document(self, file_path: str) -> Dict:
        """
        Process a document and extract text with metadata.

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary containing extracted text, metadata, and page information
        """
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.pdf':
            return self._process_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._process_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def _process_pdf(self, file_path: str) -> Dict:
        """Extract text from PDF with fallback to OCR for scanned pages."""
        document_data = {
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'upload_date': datetime.now().isoformat(),
            'document_type': 'pdf',
            'pages': []
        }

        try:
            # Try PyMuPDF first for digital PDFs
            doc = fitz.open(file_path)

            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()

                # If text extraction yields very little, try OCR
                if len(text.strip()) < 50:
                    text = self._ocr_pdf_page(file_path, page_num - 1)

                # Normalize text
                text = self._normalize_text(text)

                page_data = {
                    'page_number': page_num,
                    'text': text,
                    'char_count': len(text)
                }

                document_data['pages'].append(page_data)

            doc.close()

        except Exception as e:
            print(f"PyMuPDF failed, trying pdfplumber: {e}")
            # Fallback to pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""

                    if len(text.strip()) < 50:
                        text = self._ocr_pdf_page(file_path, page_num - 1)

                    text = self._normalize_text(text)

                    page_data = {
                        'page_number': page_num,
                        'text': text,
                        'char_count': len(text)
                    }

                    document_data['pages'].append(page_data)

        return document_data

    def _process_docx(self, file_path: str) -> Dict:
        """Extract text from DOCX files."""
        document_data = {
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'upload_date': datetime.now().isoformat(),
            'document_type': 'docx',
            'pages': []
        }

        doc = Document(file_path)
        full_text = []

        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)

        # Treat entire document as one "page" for DOCX
        text = '\n'.join(full_text)
        text = self._normalize_text(text)

        page_data = {
            'page_number': 1,
            'text': text,
            'char_count': len(text)
        }

        document_data['pages'].append(page_data)

        return document_data

    def _ocr_pdf_page(self, file_path: str, page_num: int) -> str:
        """Perform OCR on a PDF page."""
        try:
            doc = fitz.open(file_path)
            page = doc[page_num]

            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Perform OCR
            text = pytesseract.image_to_string(img)
            doc.close()

            return text
        except Exception as e:
            print(f"OCR failed for page {page_num}: {e}")
            return ""

    def _normalize_text(self, text: str) -> str:
        """Normalize extracted text."""
        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Fix common hyphenation issues
        text = text.replace('- ', '')

        # Normalize unicode characters
        text = text.encode('ascii', 'ignore').decode('ascii')

        return text

    def extract_headings(self, text: str) -> List[Dict]:
        """
        Extract potential section headings from text.
        Simple heuristic-based approach.
        """
        headings = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            # Heuristic: short lines, all caps, or numbered sections
            if line and (
                len(line) < 100 and
                (line.isupper() or
                 any(line.startswith(f"{num}.") for num in range(1, 20)))
            ):
                headings.append({
                    'line_number': i,
                    'heading': line
                })

        return headings
