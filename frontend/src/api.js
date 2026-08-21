const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function analyzeResume(resumeFile, jobDescription) {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  if (jobDescription && jobDescription.trim()) {
    formData.append('job_description', jobDescription);
  }

  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred.' }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}