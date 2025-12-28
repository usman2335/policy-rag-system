# UniPolicyQA

A RAG-powered Legal & Policy Question Answering Assistant for University Documents

## Project Overview

UniPolicyQA is an intelligent system that helps students and staff navigate university policies by providing accurate, citation-backed answers to natural language questions. The system uses Retrieval-Augmented Generation (RAG) with Google Gemini AI and Hugging Face embeddings to deliver reliable policy information.

## Features

- **Document Upload**: Support for PDF and DOCX documents with OCR for scanned files
- **Intelligent Q&A**: Natural language question answering with citation-backed responses
- **Policy Checking**: Automatic detection of ambiguity, contradictions, and legal advice
- **Confidence Scoring**: Each answer includes a confidence score based on multiple factors
- **Citation Tracking**: All answers include references to source documents and page numbers
- **User Feedback**: Built-in feedback mechanism to improve system performance
- **Modern UI**: Clean, responsive React frontend with Tailwind CSS

## Tech Stack

### Backend
- **Framework**: FastAPI
- **LLM**: Google Gemini 1.5 Flash (Free tier)
- **Embeddings**: Sentence Transformers (Hugging Face)
- **Vector Database**: ChromaDB
- **Document Processing**: PyMuPDF, PDFPlumber, python-docx
- **OCR**: Tesseract

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

## Project Structure

```
nlp_proj/
├── agents/                      # Agent implementations
│   ├── __init__.py
│   ├── ingestion_agent.py       # Document processing
│   ├── chunker_agent.py         # Text chunking
│   ├── embedding_agent.py       # Embedding generation
│   ├── vector_db_agent.py       # Vector database operations
│   ├── retriever_agent.py       # Document retrieval
│   ├── answer_generator_agent.py # Answer generation
│   └── policy_checker_agent.py  # Policy compliance checking
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── data/                        # Data storage (created at runtime)
│   ├── uploads/                 # Uploaded documents
│   ├── chroma_db/               # Vector database
│   └── logs/                    # Feedback logs
├── main.py                      # FastAPI application
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose setup
└── README.md                    # This file
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Tesseract OCR (for scanned documents)
- Google API Key (Gemini)

### Option 1: Local Setup

#### Backend Setup

1. **Install Python dependencies**:
```bash
cd c:\Users\munib\Desktop\nlp_proj
pip install -r requirements.txt
```

2. **Install Tesseract OCR** (for Windows):
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add to PATH

3. **Configure environment**:
   - The `.env` file is already created with your Google API key
   - Verify settings in `.env` file

4. **Run the backend**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

#### Frontend Setup

1. **Install Node dependencies**:
```bash
cd frontend
npm install
```

2. **Run the frontend**:
```bash
npm run dev
```

The UI will be available at `http://localhost:5173`

### Option 2: Docker Setup

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

This will start both backend and frontend services.

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Usage

### 1. Upload Documents

1. Navigate to the "Upload Documents" tab
2. Click to select a PDF or DOCX file
3. Click "Upload Document"
4. Wait for processing to complete

### 2. Ask Questions

1. Go to the "Ask Question" tab
2. Type your question about university policies
3. Click "Get Answer"
4. Review the answer with:
   - Main answer text
   - Confidence score
   - Citations from source documents
   - Warnings (if any)
   - Recommendations
   - Related follow-up questions

### 3. Provide Feedback

- Click 👍 "Helpful" or 👎 "Not Helpful" to improve the system
- Feedback is logged for analysis

## API Endpoints

### Core Endpoints

- `POST /upload` - Upload a document
- `POST /query` - Ask a question
- `POST /feedback` - Submit feedback
- `GET /documents` - List uploaded documents
- `DELETE /documents/{document_id}` - Delete a document
- `GET /stats` - Get system statistics
- `GET /health` - Health check

### Example API Usage

```python
import requests

# Upload a document
with open('policy.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', files={'file': f})
    print(response.json())

# Ask a question
response = requests.post('http://localhost:8000/query', json={
    'query': 'What is the attendance policy?'
})
print(response.json())
```

## Agent Architecture

### 1. Ingestion Agent
- Extracts text from PDF/DOCX files
- Performs OCR on scanned documents
- Normalizes text and extracts metadata

### 2. Chunker Agent
- Splits documents into overlapping chunks
- Maintains metadata (filename, page, etc.)
- Configurable chunk size and overlap

### 3. Embedding Agent
- Uses Sentence Transformers (Hugging Face)
- Model: `all-MiniLM-L6-v2`
- Generates 384-dimensional embeddings

### 4. Vector DB Agent
- ChromaDB for persistent storage
- Cosine similarity search
- Metadata filtering support

### 5. Retriever Agent
- Semantic search using embeddings
- Configurable top-K retrieval
- Context formatting for LLM

### 6. Answer Generator Agent
- Uses Google Gemini 1.5 Flash
- Citation-aware prompting
- Follow-up question generation

### 7. Policy Checker Agent
- Ambiguity detection
- Modal verb analysis
- Contradiction checking
- Legal advice detection
- Confidence scoring

## Configuration

Key configuration options in `.env`:

```bash
# Google API
GOOGLE_API_KEY=your_key_here

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM Configuration
LLM_MODEL=gemini-1.5-flash
LLM_TEMPERATURE=0.1
MAX_TOKENS=2000

# Retrieval
TOP_K_CHUNKS=7
CHUNK_SIZE=512
CHUNK_OVERLAP=128
```

## Evaluation Metrics

The system tracks:

- **Accuracy**: Ground-truth answer matching
- **Citation Precision**: % of answers with supporting citations
- **Hallucination Rate**: % of unsupported facts
- **User Satisfaction**: Feedback ratings
- **Latency**: Average response time

## Troubleshooting

### Backend Issues

1. **Import errors**: Ensure all packages are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Tesseract not found**: Install Tesseract and add to PATH

3. **Google API errors**: Verify your API key in `.env`

4. **ChromaDB errors**: Delete `data/chroma_db` and restart

### Frontend Issues

1. **Port already in use**: Change port in `vite.config.js`

2. **API connection failed**: Ensure backend is running on port 8000

3. **Build errors**: Delete `node_modules` and reinstall
   ```bash
   rm -rf node_modules
   npm install
   ```

## Future Enhancements

- [ ] Multi-language support
- [ ] Advanced re-ranking with cross-encoders
- [ ] Fine-tuning on university-specific data
- [ ] Admin dashboard for analytics
- [ ] Role-based access control
- [ ] Integration with university SSO
- [ ] Mobile app
- [ ] Slack/Teams integration

## Team

- 21i-0447 Usman Afzal
- 21i-0847 Babar Shaheen
- 21i-0848 Muhammad Ahmed
- 21i-0520 Munib Akhtar

## License

This project is for educational purposes.

## Acknowledgments

- Google Gemini AI for LLM capabilities
- Hugging Face for embedding models
- ChromaDB for vector storage
- FastAPI and React communities
