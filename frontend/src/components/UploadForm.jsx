import { useState } from 'react';

export default function UploadForm({ onAnalyze, loading }) {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [fileError, setFileError] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFileError('');
    if (file && file.type !== 'application/pdf') {
      setFileError('Please select a PDF file.');
      setResumeFile(null);
      return;
    }
    setResumeFile(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!resumeFile) {
      setFileError('Please select a resume PDF before analyzing.');
      return;
    }
    onAnalyze(resumeFile, jobDescription);
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <div className="field">
        <label>Resume (PDF) *</label>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        {fileError && <p className="error-text">{fileError}</p>}
      </div>

      <div className="field">
        <label>Job Description (optional)</label>
        <textarea
          rows={6}
          placeholder="Paste the job description here..."
          value={jobDescription}
          onChange={(e) => setJobDescription(e.target.value)}
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Resume'}
      </button>
    </form>
  );
}