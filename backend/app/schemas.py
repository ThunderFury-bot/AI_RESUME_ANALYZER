"""
schemas.py

Pydantic models defining the shape of API responses. Used for
documentation purposes and optional response validation.
"""

from pydantic import BaseModel
from typing import List


class AnalysisResult(BaseModel):
    """
    The structured result of a resume analysis, as returned by the
    /analyze endpoint.

    Attributes:
        overall_score: Integer score from 0-100 representing overall
            resume quality/fit.
        ats_compatibility: A short paragraph assessing how well the
            resume would parse through an Applicant Tracking System.
        missing_skills: Skills or keywords the resume lacks, relative
            to general best practices or the provided job description.
        strengths: Notable positive aspects of the resume.
        weaknesses: Notable weak points in the resume.
        suggestions: Concrete, actionable suggestions for improvement.
    """
    overall_score: int
    ats_compatibility: str
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class ErrorResponse(BaseModel):
    """
    Standard error response shape (for documentation reference —
    FastAPI's HTTPException already produces a compatible structure).
    """
    error: str
    detail: str