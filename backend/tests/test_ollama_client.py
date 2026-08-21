"""
Tests for ollama_client.py — verifies prompt construction and
error handling when Ollama is unreachable or returns bad data,
using mocking so these tests don't require Ollama to actually be running.
"""

import pytest
from unittest.mock import patch, Mock
import requests

from app.ollama_client import build_prompt, analyze_resume, OllamaError


def test_build_prompt_includes_resume_text():
    """The prompt should always include the resume text verbatim."""
    prompt = build_prompt("Experienced Python developer", None)
    assert "Experienced Python developer" in prompt


def test_build_prompt_includes_job_description_when_provided():
    """When a job description is given, it should appear in the prompt."""
    prompt = build_prompt("My resume text", "Looking for a Python developer")
    assert "Looking for a Python developer" in prompt
    assert "compare the resume against this job description" in prompt


def test_build_prompt_handles_missing_job_description():
    """When no job description is given, the prompt should say so instead of crashing."""
    prompt = build_prompt("My resume text", None)
    assert "No job description was provided" in prompt


@patch("app.ollama_client.requests.post")
def test_analyze_resume_connection_error_raises_ollama_error(mock_post):
    """If Ollama can't be reached, analyze_resume should raise a clear OllamaError."""
    mock_post.side_effect = requests.exceptions.ConnectionError()
    with pytest.raises(OllamaError, match="Could not connect to Ollama"):
        analyze_resume("resume text", None)


@patch("app.ollama_client.requests.post")
def test_analyze_resume_timeout_raises_ollama_error(mock_post):
    """If Ollama times out, analyze_resume should raise a clear OllamaError."""
    mock_post.side_effect = requests.exceptions.Timeout()
    with pytest.raises(OllamaError, match="took too long to respond"):
        analyze_resume("resume text", None)


@patch("app.ollama_client.requests.post")
def test_analyze_resume_valid_response_returns_parsed_dict(mock_post):
    """A well-formed Ollama response should be parsed and returned as a dict."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": (
            '{"overall_score": 80, "ats_compatibility": "Good", '
            '"missing_skills": [], "strengths": [], "weaknesses": [], "suggestions": []}'
        )
    }
    mock_post.return_value = mock_response

    result = analyze_resume("resume text", None)
    assert result["overall_score"] == 80
    assert result["ats_compatibility"] == "Good"


@patch("app.ollama_client.requests.post")
def test_analyze_resume_missing_fields_raises_ollama_error(mock_post):
    """If the LLM response is missing required fields, an OllamaError should be raised."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"overall_score": 80}'  # missing other required fields
    }
    mock_post.return_value = mock_response

    with pytest.raises(OllamaError, match="missing required fields"):
        analyze_resume("resume text", None)