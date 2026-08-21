from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.pdf_extraction import extract_text_from_pdf, PDFExtractionError
from app.ollama_client import analyze_resume, OllamaError

app = FastAPI(title="AI-Powered Resume Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_MB = 10

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
):
    # Validate file type
    if resume.content_type != "application/pdf" and not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted for the resume.")

    # Read file bytes
    file_bytes = await resume.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.")

    # Extract text
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except PDFExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Analyze with Ollama
    try:
        result = analyze_resume(resume_text, job_description)
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return result