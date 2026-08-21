"""
ollama_client.py

Handles communication with the locally hosted Ollama LLM service.
Builds a structured prompt from the resume (and optional job description),
sends it to Ollama's REST API, and validates the returned JSON analysis.
"""

import requests
import json
import os

# Ollama connection settings — overridable via environment variables so the
# same code works both locally (host.docker.internal isn't needed) and
# inside Docker (where the backend must reach Ollama on the host machine)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_TIMEOUT = 120  # seconds — local LLMs can be slow on CPU-only machines


class OllamaError(Exception):
    """
    Raised when Ollama cannot be reached, times out, returns an error
    status, or produces a response that isn't valid/expected JSON.

    Used to give the API layer a single, clean exception type to catch
    and turn into a meaningful HTTP error for the frontend.
    """
    pass


def build_prompt(resume_text: str, job_description: str | None) -> str:
    """
    Construct the prompt sent to the LLM, instructing it to return a
    strict JSON object with the six required analysis fields.

    Args:
        resume_text (str): The extracted text content of the resume.
        job_description (str | None): Optional job description text used
            to tailor the missing-skills and ATS compatibility analysis.
            If None or empty, the model is instructed to evaluate the
            resume generally instead of against a specific job.

    Returns:
        str: The fully assembled prompt string ready to send to Ollama.
    """
    if job_description and job_description.strip():
        jd_section = f"""
Job Description to compare against:
\"\"\"
{job_description.strip()}
\"\"\"

When evaluating missing skills and ATS compatibility, specifically compare the resume against this job description.
"""
    else:
        jd_section = (
            "\nNo job description was provided. Evaluate the resume generally "
            "for ATS best practices and common industry standards."
        )

    # The prompt explicitly requests a fixed JSON shape so the response
    # can be parsed reliably and rendered consistently on the frontend
    prompt = f"""You are an expert resume reviewer and ATS (Applicant Tracking System) specialist.

Analyze the following resume and respond with ONLY a valid JSON object, no extra text, no markdown formatting, no code fences. The JSON must have exactly this structure:

{{
  "overall_score": <integer 0-100>,
  "ats_compatibility": "<short paragraph assessing ATS compatibility>",
  "missing_skills": ["skill1", "skill2", ...],
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "suggestions": ["suggestion1", "suggestion2", ...]
}}

Resume text:
\"\"\"
{resume_text}
\"\"\"
{jd_section}

Respond with ONLY the JSON object. Do not include any explanation before or after it.
"""
    return prompt


def analyze_resume(resume_text: str, job_description: str | None) -> dict:
    """
    Send the resume (and optional job description) to the local Ollama
    model and return the parsed, validated analysis.

    Args:
        resume_text (str): The extracted text content of the resume.
        job_description (str | None): Optional job description text.

    Returns:
        dict: A dictionary containing exactly the six expected keys:
            overall_score, ats_compatibility, missing_skills, strengths,
            weaknesses, suggestions.

    Raises:
        OllamaError: If Ollama cannot be reached, times out, returns a
            non-200 status, the requested model is missing, or the
            response is not valid JSON / is missing required fields.
    """
    prompt = build_prompt(resume_text, job_description)

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=OLLAMA_TIMEOUT,
        )
    except requests.exceptions.ConnectionError:
        raise OllamaError(
            "Could not connect to Ollama. Make sure Ollama is running on the host machine."
        )
    except requests.exceptions.Timeout:
        raise OllamaError(
            "Ollama took too long to respond. The model may be overloaded or the input too large."
        )

    if response.status_code == 404:
        raise OllamaError(
            f"Model '{OLLAMA_MODEL}' not found. Run 'ollama pull {OLLAMA_MODEL}' on the host."
        )
    if response.status_code != 200:
        raise OllamaError(f"Ollama returned an unexpected error (status {response.status_code}).")

    try:
        # Ollama wraps the model's actual text output inside a "response" key
        raw_output = response.json()["response"]
    except (KeyError, json.JSONDecodeError):
        raise OllamaError("Ollama returned an unexpected response format.")

    try:
        # The model was instructed to return pure JSON — parse it directly
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        raise OllamaError("The AI model returned invalid JSON. Try again.")

    # Defensive check: make sure the model actually included every field
    # we asked for, even though it was instructed to. LLM output isn't
    # 100% guaranteed to follow instructions exactly every time.
    required_keys = {
        "overall_score", "ats_compatibility", "missing_skills",
        "strengths", "weaknesses", "suggestions"
    }
    if not required_keys.issubset(parsed.keys()):
        raise OllamaError("The AI model response is missing required fields.")

    return parsed