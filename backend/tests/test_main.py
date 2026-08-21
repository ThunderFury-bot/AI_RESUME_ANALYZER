"""
Tests for main.py — verifies the /health and /analyze API endpoints,
including validation and error-handling behavior, using FastAPI's
TestClient so these tests run without needing Docker or a live server.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok():
    """GET /health should always return a 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_non_pdf_file():
    """Uploading a non-PDF file should return a 400 error."""
    response = client.post(
        "/analyze",
        files={"resume": ("resume.txt", b"just some text", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF files" in response.json()["detail"]


def test_analyze_rejects_empty_file():
    """Uploading an empty file should return a 400 error."""
    response = client.post(
        "/analyze",
        files={"resume": ("resume.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_analyze_requires_resume_field():
    """Submitting without a resume file at all should fail validation."""
    response = client.post("/analyze", data={"job_description": "some job"})
    assert response.status_code == 422  # FastAPI's built-in validation error


@patch("app.main.analyze_resume")
@patch("app.main.extract_text_from_pdf")
def test_analyze_success_returns_analysis(mock_extract, mock_analyze):
    """
    A valid PDF upload should return the analysis JSON from Ollama.
    Both PDF extraction and the Ollama call are mocked so this test
    doesn't depend on a real PDF file or a running Ollama instance.
    """
    mock_extract.return_value = "John Doe, Software Engineer"
    mock_analyze.return_value = {
        "overall_score": 85,
        "ats_compatibility": "Strong match",
        "missing_skills": [],
        "strengths": ["Clear formatting"],
        "weaknesses": [],
        "suggestions": [],
    }

    response = client.post(
        "/analyze",
        files={"resume": ("resume.pdf", b"%PDF-1.4 fake pdf bytes", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["overall_score"] == 85