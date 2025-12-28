# UniPolicyQA - Quick Setup Guide

## Prerequisites Installation

### 1. Install Python 3.10+
Download from: https://www.python.org/downloads/

### 2. Install Node.js 18+
Download from: https://nodejs.org/

### 3. Install Tesseract OCR (Windows)
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. Add to PATH:
   - Default location: `C:\Program Files\Tesseract-OCR`
   - Add to System Environment Variables

### 4. Get Google API Key
Your current key is already configured in `.env`:
```
YOUR_API_KEY_HERE
```

## Quick Start (Recommended)

### Step 1: Install Backend Dependencies
```bash
cd c:\Users\munib\Desktop\nlp_proj
pip install -r requirements.txt
```

Wait for installation to complete (may take 5-10 minutes for first time).

### Step 2: Start Backend Server
```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Install Frontend Dependencies (New Terminal)
```bash
cd c:\Users\munib\Desktop\nlp_proj\frontend
npm install
```

### Step 4: Start Frontend Server
```bash
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### Step 5: Open Application
Open your browser and go to: `http://localhost:5173`

## Testing the Application

### 1. Upload a Test Document
1. Click "Upload Documents" tab
2. Select a PDF or DOCX file (e.g., student handbook)
3. Click "Upload Document"
4. Wait for "Document uploaded successfully"

### 2. Ask a Question
1. Click "Ask Question" tab
2. Type a question like: "What is the attendance policy?"
3. Click "Get Answer"
4. Review the answer with citations

## Common Issues & Solutions

### Issue 1: "Module not found" errors
**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt --upgrade
```

### Issue 2: Tesseract not found
**Solution**: Add Tesseract to PATH
```bash
# Windows
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

### Issue 3: Port 8000 already in use
**Solution**: Kill the process or change port in `.env`
```bash
# Windows - Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: Google API errors
**Solution**: Check your API key
- Verify key in `.env` file
- Check quota at: https://console.cloud.google.com/

### Issue 5: ChromaDB errors
**Solution**: Clear database and restart
```bash
# Delete the database folder
rmdir /s /q data\chroma_db
# Restart backend
python main.py
```

### Issue 6: Frontend can't connect to backend
**Solution**: Check CORS settings
- Verify backend is running on port 8000
- Check `CORS_ORIGINS` in `.env`

## Verifying Installation

### Check Backend
Visit: `http://localhost:8000/health`

Expected response:
```json
{
  "status": "healthy",
  "vector_db": {...},
  "timestamp": "..."
}
```

### Check Frontend
Visit: `http://localhost:5173`

You should see the UniPolicyQA interface.

## API Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/upload -F "file=@document.pdf"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is the attendance policy?\"}"
```

## Alternative: Docker Setup

If you have Docker installed:

```bash
# Build and run
docker-compose up --build

# Stop
docker-compose down
```

## Performance Tips

1. **First Load**: The first query will be slow (loading embedding model)
2. **Embedding Model**: Downloads ~80MB on first run
3. **Document Processing**: Large PDFs may take 1-2 minutes to process
4. **Query Speed**: Typical query takes 2-5 seconds

## Development Mode

### Auto-reload Backend (with uvicorn)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Hot Reload
Already enabled with `npm run dev`

## Project Structure Check

Verify all files are present:
```
nlp_proj/
├── agents/
│   ├── ingestion_agent.py
│   ├── chunker_agent.py
│   ├── embedding_agent.py
│   ├── vector_db_agent.py
│   ├── retriever_agent.py
│   ├── answer_generator_agent.py
│   └── policy_checker_agent.py
├── frontend/
│   └── src/
│       └── App.jsx
├── main.py
├── config.py
├── requirements.txt
└── .env
```

## Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all prerequisites are installed
3. Check the `.env` file configuration
4. Review the troubleshooting section in README.md

## Next Steps

1. Upload your university policy documents
2. Test with sample questions
3. Review the answer quality and citations
4. Provide feedback to improve the system
5. Customize the prompt templates in agent files

## Contact

For project-specific questions, contact the team members listed in README.md.

Good luck with your project! 🚀
