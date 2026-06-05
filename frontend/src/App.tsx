import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { PromptInput } from './pages/PromptInput';
import { PipelineResults } from './pages/PipelineResults';
import { RuntimePreview } from './pages/RuntimePreview';
import { MetricsDashboard } from './pages/MetricsDashboard';
import { Sparkles, TerminalSquare, Activity, Settings2, Github, BookOpen } from 'lucide-react';
import './index.css';

const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="navbar">
      <div className="logo">
        <Sparkles size={24} color="var(--accent)" />
        GemPower
      </div>
      <div className="nav-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <TerminalSquare size={16} /> Builder
          </div>
        </Link>
        <Link to="/results" className={location.pathname === '/results' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Settings2 size={16} /> Architecture
          </div>
        </Link>
        <Link to="/preview" className={location.pathname === '/preview' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Sparkles size={16} /> Preview
          </div>
        </Link>
        <Link to="/metrics" className={location.pathname === '/metrics' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Activity size={16} /> Metrics
          </div>
        </Link>
      </div>
      <div className="nav-actions">
        <a href="https://github.com/Shaurya-dev7/GemPower" target="_blank" rel="noopener noreferrer" className="icon-link">
          <Github size={20} />
        </a>
        <a href="#" className="icon-link">
          <BookOpen size={20} />
        </a>
      </div>
    </nav>
  );
};

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-logo">
          <Sparkles size={20} color="var(--accent)" />
          <span>GemPower AI Compiler</span>
        </div>
        <div className="footer-links">
          <a href="#">Documentation</a>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
        </div>
        <div className="footer-copyright">
          &copy; {new Date().getFullYear()} GemPower. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

const AnimatedRoutes = () => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <PromptInput />
          </motion.div>
        } />
        <Route path="/results" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <PipelineResults />
          </motion.div>
        } />
        <Route path="/preview" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <RuntimePreview />
          </motion.div>
        } />
        <Route path="/metrics" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <MetricsDashboard />
          </motion.div>
        } />
      </Routes>
    </AnimatePresence>
  );
};

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Navigation />
        <div className="container">
          <AnimatedRoutes />
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
