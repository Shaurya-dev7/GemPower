import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Play, LayoutTemplate, AlertTriangle } from 'lucide-react';
import { API_URL } from '../config/api';

export const RuntimePreview = () => {
  const [hasPreview, setHasPreview] = useState<boolean | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/runtime-preview`)
      .then(res => setHasPreview(res.ok))
      .catch(() => setHasPreview(false));
  }, []);

  return (
    <div className="panel" style={{ flex: 1, padding: '2rem', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <Play size={32} color="var(--accent)" />
        <h2 style={{ margin: 0 }} className="gradient-text">Runtime Preview</h2>
      </div>
      
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '1.1rem' }}>
        This isolated environment renders the generated application from your most recent compilation request.
      </p>
      
      <motion.div 
        className="iframe-container" 
        style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        {hasPreview === null ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', justifyContent: 'center', height: '100%' }}>
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }}>
              <LayoutTemplate size={48} color="var(--accent)" />
            </motion.div>
            <span style={{ fontSize: '1.2rem' }}>Initializing sandbox environment...</span>
          </div>
        ) : hasPreview ? (
          <iframe 
            src={`${API_URL}/runtime-preview`} 
            title="Runtime Preview" 
            style={{ width: '100%', flex: 1, border: 'none', display: 'block' }} 
          />
        ) : (
          <div style={{ 
            padding: '4rem', 
            textAlign: 'center', 
            color: 'var(--text-secondary)', 
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            background: 'var(--bg-dark)'
          }}>
            <AlertTriangle size={64} color="var(--warning)" style={{ marginBottom: '1.5rem' }} />
            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>No runtime generated yet</h3>
            <p style={{ fontSize: '1.1rem' }}>Please ignite the compilation from the Builder first.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};
