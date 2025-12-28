from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime
import json

from config import settings
from agents.ingestion_agent import IngestionAgent
from agents.chunker_agent import ChunkerAgent
from agents.embedding_agent import EmbeddingAgent
from agents.vector_db_agent import VectorDBAgent
from agents.retriever_agent import RetrieverAgent
from agents.answer_generator_agent import AnswerGeneratorAgent
from agents.policy_checker_agent import PolicyCheckerAgent

# Initialize FastAPI app
app = FastAPI(
    title="UniPolicyQA",
    description="RAG-powered Legal & Policy Question Answering Assistant for University Documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
ingestion_agent = IngestionAgent()
chunker_agent = ChunkerAgent(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)
embedding_agent = EmbeddingAgent()
vector_db_agent = VectorDBAgent()
retriever_agent = RetrieverAgent()
answer_generator_agent = AnswerGeneratorAgent()
policy_checker_agent = PolicyCheckerAgent()

# Store for tracking upload jobs
upload_jobs = {}


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    filter_by_document: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    citations: List[dict]
    confidence_score: float
    warnings: List[str]
    recommendations: List[str]
    followup_questions: Optional[List[str]] = None
    metadata: dict


class FeedbackRequest(BaseModel):
    query: str
    answer: str
    is_correct: bool
    comment: Optional[str] = None


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "UniPolicyQA API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = vector_db_agent.get_collection_stats()
        return {
            "status": "healthy",
            "vector_db": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a document (PDF or DOCX) for processing.
    The document will be processed in the background.
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.docx', '.doc']:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF and DOCX files are allowed."
        )

    # Save uploaded file
    file_path = os.path.join(settings.upload_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create job ID
    job_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"

    # Add processing task to background
    background_tasks.add_task(process_document, job_id, file_path)

    upload_jobs[job_id] = {
        "status": "processing",
        "filename": file.filename,
        "started_at": datetime.now().isoformat()
    }

    return {
        "message": "File uploaded successfully",
        "job_id": job_id,
        "filename": file.filename,
        "status": "processing"
    }


async def process_document(job_id: str, file_path: str):
    """Background task to process uploaded document."""
    try:
        # Step 1: Ingest document
        document_data = ingestion_agent.process_document(file_path)

        # Step 2: Chunk document
        chunks = chunker_agent.chunk_document(document_data)

        # Step 3: Generate embeddings
        chunks_with_embeddings = embedding_agent.embed_chunks(chunks)

        # Step 4: Store in vector database
        vector_db_agent.add_chunks(chunks_with_embeddings)

        # Update job status
        upload_jobs[job_id] = {
            "status": "completed",
            "filename": os.path.basename(file_path),
            "chunks_created": len(chunks),
            "completed_at": datetime.now().isoformat()
        }

        # Log feedback
        log_feedback({
            "type": "document_upload",
            "job_id": job_id,
            "filename": os.path.basename(file_path),
            "chunks": len(chunks),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        upload_jobs[job_id] = {
            "status": "failed",
            "filename": os.path.basename(file_path),
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }


@app.get("/upload/{job_id}")
async def get_upload_status(job_id: str):
    """Get the status of an upload job."""
    if job_id not in upload_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return upload_jobs[job_id]


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the document collection with a natural language question.
    Returns an answer with citations and confidence score.
    """
    try:
        # Step 1: Retrieve relevant chunks
        chunks = retriever_agent.retrieve(
            query=request.query,
            top_k=request.top_k,
            filter_by_document=request.filter_by_document
        )

        if not chunks:
            return QueryResponse(
                answer="I don't have any information to answer this question. Please upload relevant policy documents first.",
                citations=[],
                confidence_score=0.0,
                warnings=["No relevant documents found"],
                recommendations=["Upload university policy documents to get started"],
                metadata={"chunks_retrieved": 0}
            )

        # Step 2: Format context and get citations
        context = retriever_agent.format_context(chunks)
        citations = retriever_agent.get_citations(chunks)

        # Step 3: Generate answer
        answer_result = answer_generator_agent.generate_answer(
            query=request.query,
            context=context,
            citations=citations
        )

        # Step 4: Check policy compliance
        policy_check = policy_checker_agent.check_policy(
            answer=answer_result['answer'],
            retrieved_chunks=chunks,
            query=request.query
        )

        # Step 5: Generate follow-up questions (optional)
        followup_questions = answer_generator_agent.generate_followup_questions(
            query=request.query,
            answer=answer_result['answer']
        )

        # Log query
        log_feedback({
            "type": "query",
            "query": request.query,
            "answer": answer_result['answer'],
            "confidence": policy_check['confidence_score'],
            "chunks_used": len(chunks),
            "timestamp": datetime.now().isoformat()
        })

        return QueryResponse(
            answer=answer_result['answer'],
            citations=answer_result['citations'],
            confidence_score=policy_check['confidence_score'],
            warnings=policy_check['warnings'],
            recommendations=policy_check['recommendations'],
            followup_questions=followup_questions,
            metadata={
                "chunks_retrieved": len(chunks),
                "tokens_used": answer_result.get('tokens_used', 0),
                "model": answer_result.get('model', 'unknown'),
                "policy_checks": {
                    "ambiguity": policy_check['ambiguity_check'],
                    "modal_verbs": policy_check['modal_verb_analysis'],
                    "contradictions": policy_check['contradiction_check'],
                    "legal_advice": policy_check['legal_advice_check']
                }
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on a query response."""
    try:
        log_feedback({
            "type": "user_feedback",
            "query": feedback.query,
            "answer": feedback.answer,
            "is_correct": feedback.is_correct,
            "comment": feedback.comment,
            "timestamp": datetime.now().isoformat()
        })

        return {"message": "Feedback submitted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@app.get("/documents")
async def list_documents():
    """List all uploaded documents in the vector database."""
    try:
        documents = vector_db_agent.list_documents()
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the vector database and file system."""
    try:
        # Get document info before deleting
        documents = vector_db_agent.list_documents()
        doc_to_delete = next((d for d in documents if d['document_id'] == document_id), None)

        # Delete from vector database
        vector_db_agent.delete_document(document_id)

        # Delete physical file if it exists
        if doc_to_delete:
            file_path = os.path.join(settings.upload_dir, doc_to_delete['filename'])
            if os.path.exists(file_path):
                os.remove(file_path)

        return {
            "message": f"Document deleted successfully",
            "document_id": document_id,
            "filename": doc_to_delete['filename'] if doc_to_delete else "unknown"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """Get system statistics."""
    try:
        stats = vector_db_agent.get_collection_stats()

        # Get upload jobs stats
        completed_jobs = sum(1 for job in upload_jobs.values() if job['status'] == 'completed')
        failed_jobs = sum(1 for job in upload_jobs.values() if job['status'] == 'failed')
        processing_jobs = sum(1 for job in upload_jobs.values() if job['status'] == 'processing')

        return {
            "vector_db": stats,
            "upload_jobs": {
                "total": len(upload_jobs),
                "completed": completed_jobs,
                "failed": failed_jobs,
                "processing": processing_jobs
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


def log_feedback(data: dict):
    """Log feedback and audit trail to file."""
    log_file = os.path.join("./data/logs", "feedback.jsonl")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a") as f:
        f.write(json.dumps(data) + "\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
