# UniPolicyQA - Installation Instructions

## What You Need

Your complete RAG-powered University Policy QA system is now ready! All services used are **100% FREE**:

### Free Services Used
- ✅ **Google Gemini AI** (models/gemma-3-1b-it) - FREE
- ✅ **Hugging Face Sentence Transformers** (all-MiniLM-L6-v2) - FREE
- ✅ **ChromaDB** - FREE & Open Source
- ✅ **FastAPI** - FREE & Open Source
- ✅ **React + Vite** - FREE & Open Source

## Quick Installation (Windows)

### Step 1: Install Python Dependencies

```bash
cd c:\Users\munib\Desktop\nlp_proj
pip install -r requirements.txt
```

**Expected time**: 5-10 minutes

### Step 2: Install Tesseract OCR (for scanned PDFs)

1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

### Step 3: Start Backend

```bash
python main.py
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Install Frontend (New Terminal)

```bash
cd frontend
npm install
```

### Step 5: Start Frontend

```bash
npm run dev
```

**Expected output**:
```
➜  Local:   http://localhost:5173/
```

### Step 6: Open in Browser

Visit: `http://localhost:5173`

## Verification

### 1. Check Backend Health
Visit: `http://localhost:8000/health`

Should return:
```json
{
  "status": "healthy",
  "vector_db": {...}
}
```

### 2. Test Upload
1. Go to "Upload Documents" tab
2. Select a PDF file
3. Click "Upload Document"
4. Wait for success message

### 3. Test Query
1. Go to "Ask Question" tab
2. Type: "What are the main topics in this document?"
3. Click "Get Answer"
4. Review the citation-backed answer

## System Architecture

```
User Browser (React UI)
    ↓
FastAPI Backend
    ↓
┌────────────────────────────────┐
│  Document Ingestion Agent      │ → PDF/DOCX Processing
│  (PyMuPDF + Tesseract OCR)     │
└────────────────────────────────┘
    ↓
┌────────────────────────────────┐
│  Chunker Agent                 │ → Text Chunking
│  (LangChain RecursiveTextSplitter) │
└────────────────────────────────┘
    ↓
┌────────────────────────────────┐
│  Embedding Agent               │ → Hugging Face
│  (sentence-transformers)       │   (all-MiniLM-L6-v2)
└────────────────────────────────┘
    ↓
┌────────────────────────────────┐
│  Vector DB Agent               │ → ChromaDB
│  (ChromaDB)                    │   (Local Storage)
└────────────────────────────────┘
    ↓
Query Time:
┌────────────────────────────────┐
│  Retriever Agent               │ → Semantic Search
└────────────────────────────────┘
    ↓
┌────────────────────────────────┐
│  Answer Generator              │ → Google Gemini
│  (models/gemma-3-1b-it)        │   (FREE)
└────────────────────────────────┘
    ↓
┌────────────────────────────────┐
│  Policy Checker Agent          │ → Quality Check
└────────────────────────────────┘
```

## Configuration

All settings are in [.env](.env):

```bash
# Your Google API Key (already configured)
GOOGLE_API_KEY=AIzaSyCuZJn1t2PXTEHIcDaChSupXxMRkt2LvB8

# Model (FREE Google Gemini model)
LLM_MODEL=models/gemma-3-1b-it

# Embeddings (FREE Hugging Face)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector DB (FREE & Local)
VECTOR_DB_PATH=./data/chroma_db
```

## Troubleshooting

### Problem: "Module not found"
**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Problem: "Tesseract not found"
**Solution**: Install Tesseract and add to PATH
```bash
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

### Problem: Backend won't start
**Solution**: Check if port 8000 is available
```bash
netstat -ano | findstr :8000
```

### Problem: Google API errors
**Solution**: Your key is configured. Check quota at:
https://console.cloud.google.com/

### Problem: ChromaDB errors
**Solution**: Clear database
```bash
rmdir /s /q data\chroma_db
```

## Cost Analysis

| Component | Service | Cost |
|-----------|---------|------|
| LLM | Google Gemini (gemma-3-1b-it) | **FREE** |
| Embeddings | Hugging Face (local) | **FREE** |
| Vector DB | ChromaDB (local) | **FREE** |
| Backend | FastAPI (self-hosted) | **FREE** |
| Frontend | React (self-hosted) | **FREE** |
| **TOTAL** | | **$0.00** |

## Performance

- **First Query**: ~5-10 seconds (loading models)
- **Subsequent Queries**: ~2-3 seconds
- **Document Upload**: ~30-60 seconds per PDF
- **Embedding Generation**: ~2-3 seconds per document

## API Endpoints

### Core Operations
- `POST /upload` - Upload document
- `POST /query` - Ask question
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document
- `POST /feedback` - Submit feedback
- `GET /health` - Health check
- `GET /stats` - System statistics

### Example cURL Commands

```bash
# Health Check
curl http://localhost:8000/health

# Upload Document
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the attendance policy?"}'
```

## Features

### 1. Document Upload & Processing
- PDF and DOCX support
- OCR for scanned documents
- Automatic text extraction
- Metadata preservation

### 2. Intelligent Question Answering
- Natural language queries
- Citation-backed answers
- Confidence scoring
- Source attribution

### 3. Policy Checking
- Ambiguity detection
- Contradiction checking
- Legal advice flagging
- Modal verb analysis

### 4. User Interface
- Clean, modern design
- Document management
- Query history
- Feedback mechanism

## Development

### Run Backend in Dev Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run Frontend in Dev Mode
```bash
cd frontend
npm run dev
```

Hot reload is enabled for both!

## Production Deployment (Optional)

### Using Docker
```bash
docker-compose up --build
```

This starts both backend and frontend in containers.

## Project Files

```
nlp_proj/
├── agents/                  # All agent implementations
│   ├── ingestion_agent.py
│   ├── chunker_agent.py
│   ├── embedding_agent.py
│   ├── vector_db_agent.py
│   ├── retriever_agent.py
│   ├── answer_generator_agent.py
│   └── policy_checker_agent.py
├── frontend/                # React UI
│   ├── src/App.jsx
│   └── package.json
├── main.py                  # FastAPI backend
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── .env                     # Your settings
├── README.md                # Full documentation
└── SETUP_GUIDE.md           # Quick start guide
```

## Next Steps

1. **Upload Documents**: Add your university policy PDFs
2. **Test Queries**: Ask questions about policies
3. **Review Answers**: Check citations and confidence
4. **Provide Feedback**: Help improve the system
5. **Customize**: Adjust settings in `.env`

## Support

- Check [README.md](README.md) for full documentation
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for troubleshooting
- All code is well-commented

## Team

- 21i-0447 Usman Afzal
- 21i-0847 Babar Shaheen
- 21i-0848 Muhammad Ahmed
- 21i-0520 Munib Akhtar

---

**Remember**: Everything is FREE! No hidden costs, no API limits to worry about. Your Google API key is already configured and the Gemini model is completely free to use.

Happy coding! 🚀
