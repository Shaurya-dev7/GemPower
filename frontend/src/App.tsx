import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { PromptInput } from './pages/PromptInput';
import { PipelineResults } from './pages/PipelineResults';
import { RuntimePreview } from './pages/RuntimePreview';
import { MetricsDashboard } from './pages/MetricsDashboard';
import './index.css';

const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="navbar">
      <div className="logo">Antigravity Compiler</div>
      <div className="nav-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Prompt Input</Link>
        <Link to="/results" className={location.pathname === '/results' ? 'active' : ''}>Pipeline Results</Link>
        <Link to="/preview" className={location.pathname === '/preview' ? 'active' : ''}>Runtime Preview</Link>
        <Link to="/metrics" className={location.pathname === '/metrics' ? 'active' : ''}>Metrics Dashboard</Link>
      </div>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <Navigation />
      <div className="container">
        <Routes>
          <Route path="/" element={<PromptInput />} />
          <Route path="/results" element={<PipelineResults />} />
          <Route path="/preview" element={<RuntimePreview />} />
          <Route path="/metrics" element={<MetricsDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
