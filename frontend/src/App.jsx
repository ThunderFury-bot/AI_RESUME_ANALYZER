import { useState } from 'react';
import UploadForm from './components/UploadForm';
import ResultsView from './components/ResultsView';
import { analyzeResume } from './api';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (resumeFile, jobDescription) => {
    setLoading(true);
    setError('');
    setResults(null);
    try {
      const data = await analyzeResume(resumeFile, jobDescription);
      setResults(data);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>AI-Powered Resume Analyzer</h1>
      <p className="subtitle">Upload your resume and get instant AI-powered feedback.</p>

      <UploadForm onAnalyze={handleAnalyze} loading={loading} />

      {loading && <p className="loading">Analyzing your resume, please wait...</p>}
      {error && <p className="error-banner">{error}</p>}

      <ResultsView results={results} />
    </div>
  );
}