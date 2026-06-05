import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { PromptInput } from './pages/PromptInput';
import { PipelineResults } from './pages/PipelineResults';
import { RuntimePreview } from './pages/RuntimePreview';
import { MetricsDashboard } from './pages/MetricsDashboard';
import { Sparkles, TerminalSquare, Activity, Settings2 } from 'lucide-react';
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
            <TerminalSquare size={18} /> Builder
          </div>
        </Link>
        <Link to="/results" className={location.pathname === '/results' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Settings2 size={18} /> Architecture
          </div>
        </Link>
        <Link to="/preview" className={location.pathname === '/preview' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Sparkles size={18} /> Preview
          </div>
        </Link>
        <Link to="/metrics" className={location.pathname === '/metrics' ? 'active' : ''}>
          <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Activity size={18} /> Metrics
          </div>
        </Link>
      </div>
    </nav>
  );
};

const AnimatedRoutes = () => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
            <PromptInput />
          </motion.div>
        } />
        <Route path="/results" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
            <PipelineResults />
          </motion.div>
        } />
        <Route path="/preview" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
            <RuntimePreview />
          </motion.div>
        } />
        <Route path="/metrics" element={
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}>
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
      <Navigation />
      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <AnimatedRoutes />
      </div>
    </Router>
  );
}

export default App;
