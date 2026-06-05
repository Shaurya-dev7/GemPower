import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export const PromptInput = () => {
  const [prompt, setPrompt] = useState('Build a CRM with contacts and subscriptions');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCompile = async () => {
    setLoading(true);
    try {
      // Hit the FastAPI backend
      const res = await axios.post('http://localhost:8000/api/compile', { prompt });
      // Store the result in localStorage for simplicity across components
      localStorage.setItem('compile_results', JSON.stringify(res.data));
      navigate('/results');
    } catch (err) {
      console.error(err);
      alert('Failed to compile. Check backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel" style={{ maxWidth: '800px', margin: '4rem auto', textAlign: 'center' }}>
      <h1 style={{ marginBottom: '1rem', fontSize: '2.5rem' }}>Describe your application</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        The Antigravity Compiler will parse your intent, build the architecture, generate DB/API schemas, validate constraints, and scaffold the runtime.
      </p>
      
      <div className="textarea-wrapper">
        <textarea 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="I want to build a..."
        />
      </div>
      
      <button 
        className="btn-primary" 
        onClick={handleCompile}
        disabled={loading}
      >
        {loading ? 'Compiling Application...' : 'Compile Application 🚀'}
      </button>
    </div>
  );
};
