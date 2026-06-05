import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { Sparkles, ArrowRight } from 'lucide-react';
import heroBg from '../assets/hero_bg_black.png';

export const PromptInput = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCompile = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/api/compile', { prompt });
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
    <div style={{ position: 'relative', width: '100%', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      {/* Abstract Background Image behind the main panel */}
      <div 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `url(${heroBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.3,
          zIndex: -1,
          borderRadius: '4px',
          maskImage: 'linear-gradient(to bottom, black 50%, transparent 100%)',
          WebkitMaskImage: 'linear-gradient(to bottom, black 50%, transparent 100%)'
        }}
      />
      
      <motion.div 
        className="panel" 
        style={{ maxWidth: '900px', width: '100%', margin: 'auto', textAlign: 'center', position: 'relative', background: 'rgba(24, 24, 27, 0.8)', backdropFilter: 'blur(10px)' }}
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <motion.div
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.4 }}
        >
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
            <div style={{ background: 'var(--bg-dark)', padding: '1rem', borderRadius: '4px', border: '2px solid var(--accent)', boxShadow: '4px 4px 0px 0px var(--accent)' }}>
              <Sparkles size={48} color="var(--accent)" />
            </div>
          </div>
          <h1 className="gradient-text" style={{ marginBottom: '1.5rem', fontSize: '3.5rem', fontWeight: 800 }}>
            Forge Your Vision
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '3rem', fontSize: '1.25rem', maxWidth: '700px', margin: '0 auto 3rem auto', lineHeight: 1.6 }}>
            The ultimate AI-driven compiler. Describe your application in natural language, and watch as GemPower scaffolds architecture, databases, APIs, and runtime UI instantaneously.
          </p>
        </motion.div>
        
        <motion.div 
          className="textarea-wrapper"
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
        >
          <textarea 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="I want to build a..."
            style={{ fontSize: '1.2rem', padding: '2rem' }}
          />
        </motion.div>
        
        <motion.button 
          className="btn-primary" 
          onClick={handleCompile}
          disabled={loading}
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          style={{ alignSelf: 'center', fontSize: '1.25rem', padding: '1.25rem 3rem' }}
        >
          {loading ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
              <Sparkles size={24} />
            </motion.div>
          ) : (
            <Sparkles size={24} />
          )}
          {loading ? 'Synthesizing Architecture...' : 'Ignite Compilation'}
          {!loading && <ArrowRight size={24} />}
        </motion.button>
      </motion.div>
    </div>
  );
};
