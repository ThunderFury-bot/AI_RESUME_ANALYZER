from pydantic import BaseModel
from typing import List

class AnalysisResult(BaseModel):
    overall_score: int
    ats_compatibility: str
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]

class ErrorResponse(BaseModel):
    error: str
    detail: str