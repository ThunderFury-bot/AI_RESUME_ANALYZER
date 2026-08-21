import requests
import json
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_TIMEOUT = 120  # seconds - local LLMs can be slow on CPU

class OllamaError(Exception):
    pass

def build_prompt(resume_text: str, job_description: str | None) -> str:
    jd_section = ""
    if job_description and job_description.strip():
        jd_section = f"""
Job Description to compare against:
\"\"\"
{job_description.strip()}
\"\"\"

When evaluating missing skills and ATS compatibility, specifically compare the resume against this job description.
"""
    else:
        jd_section = "\nNo job description was provided. Evaluate the resume generally for ATS best practices and common industry standards."

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
        raw_output = response.json()["response"]
    except (KeyError, json.JSONDecodeError):
        raise OllamaError("Ollama returned an unexpected response format.")

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        raise OllamaError("The AI model returned invalid JSON. Try again.")

    required_keys = {"overall_score", "ats_compatibility", "missing_skills", "strengths", "weaknesses", "suggestions"}
    if not required_keys.issubset(parsed.keys()):
        raise OllamaError("The AI model response is missing required fields.")

    return parsed