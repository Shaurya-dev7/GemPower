import { useState, useEffect } from 'react';

export const RuntimePreview = () => {
  const [hasPreview, setHasPreview] = useState<boolean | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/runtime-preview')
      .then(res => setHasPreview(res.ok))
      .catch(() => setHasPreview(false));
  }, []);

  return (
    <div className="panel" style={{ height: '80vh', padding: '1rem', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ marginBottom: '1rem' }}>Runtime Preview</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
        This iframe renders the generated application from your most recent compile request.
      </p>
      
      <div className="iframe-container" style={{ flexGrow: 1 }}>
        {hasPreview === null ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading preview...</div>
        ) : hasPreview ? (
          <iframe 
            src="http://localhost:8000/runtime-preview" 
            title="Runtime Preview" 
            style={{ width: '100%', height: '100%', border: 'none', borderRadius: '8px' }} 
          />
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)', border: '1px dashed var(--border)', borderRadius: '8px' }}>
            <h3>No runtime generated yet.</h3>
            <p>Run a compile first.</p>
          </div>
        )}
      </div>
    </div>
  );
};
