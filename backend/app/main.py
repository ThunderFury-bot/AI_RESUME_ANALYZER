"""
main.py

FastAPI application entry point for the AI-Powered Resume Analyzer backend.
Exposes a REST API with two endpoints:
    GET  /health   - simple liveness check
    POST /analyze  - accepts a resume PDF (+ optional job description)
                     and returns an AI-generated analysis
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.pdf_extraction import extract_text_from_pdf, PDFExtractionError
from app.ollama_client import analyze_resume, OllamaError

app = FastAPI(title="AI-Powered Resume Analyzer API")

# Allow the frontend (running on a different origin/port) to call this API.
# Wildcard origins are acceptable here since this is a local development
# / demo project with no authentication or sensitive data involved.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_MB = 10


@app.get("/health")
def health_check():
    """
    Simple liveness check endpoint.

    Returns:
        dict: {"status": "ok"} if the backend process is running.
    """
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
):
    """
    Analyze an uploaded resume PDF, optionally against a job description.

    Validates the uploaded file, extracts its text content, sends it to
    the local Ollama LLM for analysis, and returns the structured result.

    Args:
        resume (UploadFile): The uploaded resume file. Must be a PDF.
        job_description (str, optional): Plain text job description used
            to tailor the analysis. If omitted, the resume is evaluated
            generally against common ATS/resume best practices.

    Returns:
        dict: The AI-generated analysis containing overall_score,
            ats_compatibility, missing_skills, strengths, weaknesses,
            and suggestions.

    Raises:
        HTTPException(400): If the file isn't a PDF, is empty, or exceeds
            the maximum allowed size, or if text extraction fails.
        HTTPException(503): If Ollama is unreachable, times out, the
            model is missing, or the AI response is invalid.
    """
    # --- File type validation ---
    if resume.content_type != "application/pdf" and not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted for the resume.")

    file_bytes = await resume.read()

    # --- Empty file validation ---
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    # --- File size validation ---
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.")

    # --- Text extraction ---
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # --- AI analysis via Ollama ---
    try:
        result = analyze_resume(resume_text, job_description)
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return result