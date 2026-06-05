import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, FileCode, CheckCircle, AlertTriangle, Box, ShieldCheck, Zap, Settings2 } from 'lucide-react';

export const PipelineResults = () => {
  const [activeTab, setActiveTab] = useState('intent');
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const raw = localStorage.getItem('compile_results');
    if (raw) setData(JSON.parse(raw));
  }, []);

  if (!data) {
    return (
      <motion.div className="panel" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <AlertTriangle size={48} color="var(--warning)" style={{ margin: '0 auto 1rem auto' }} />
          <h3>No data available</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Please ignite the compilation from the Builder first.</p>
        </div>
      </motion.div>
    );
  }

  const { stages } = data;

  const renderSummaryHeader = () => {
    const confidence = stages?.intent?.confidence || 0;
    const valScore = stages?.validation?.score || 0;
    const modulesCount = stages?.architecture?.modules?.length || 0;
    const entitiesCount = stages?.architecture?.entities?.length || 0;
    const apiEndpointsCount = stages?.schemas?.api?.length || 0;

    return (
      <div className="metrics-grid" style={{ marginBottom: '2rem' }}>
        <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
          <h4><Zap size={16} color="var(--accent)" /> Confidence</h4>
          <div className="value">{(confidence * 100).toFixed(0)}%</div>
        </motion.div>
        <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
          <h4><ShieldCheck size={16} color="var(--accent)" /> Validation Score</h4>
          <div className="value">{valScore}/100</div>
        </motion.div>
        <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
          <h4><Box size={16} color="var(--accent)" /> Modules</h4>
          <div className="value">{modulesCount}</div>
        </motion.div>
        <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
          <h4><Database size={16} color="var(--accent)" /> Entities</h4>
          <div className="value">{entitiesCount}</div>
        </motion.div>
        <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
          <h4><FileCode size={16} color="var(--accent)" /> API Endpoints</h4>
          <div className="value">{apiEndpointsCount}</div>
        </motion.div>
      </div>
    );
  };

  const renderArchitecture = () => {
    const arch = stages?.architecture;
    if (!arch) return null;
    
    const sectionStyle = { padding: '0.75rem', background: 'var(--bg-dark)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', border: '1px solid var(--border)', marginBottom: '0.5rem' };
    
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <details>
          <summary style={sectionStyle}>▶ Modules ({arch.modules?.length || 0})</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(arch.modules, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ Entities ({arch.entities?.length || 0})</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(arch.entities, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ User Flows ({arch.user_flows?.length || 0})</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(arch.user_flows, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ Permissions ({arch.permissions?.length || 0})</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(arch.permissions, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ System Components ({arch.system_components?.length || 0})</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(arch.system_components, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ Raw JSON</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(arch, null, 2)}</pre></div>
        </details>
      </motion.div>
    );
  };

  const renderSchemas = () => {
    const schemas = stages?.schemas;
    if (!schemas) return null;
    const tables = schemas.database?.length || 0;
    const endpoints = schemas.api?.length || 0;
    const pages = schemas.ui?.length || 0;
    
    let forms = 0;
    schemas.ui?.forEach((p: any) => {
      p.components?.forEach((c: any) => {
        if (c.type === 'form') forms++;
      });
    });

    const sectionStyle = { padding: '0.75rem', background: 'var(--bg-dark)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', border: '1px solid var(--border)', marginBottom: '0.5rem' };

    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="metrics-grid">
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}><h4>Tables</h4><div className="value">{tables}</div></motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}><h4>API Endpoints</h4><div className="value">{endpoints}</div></motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}><h4>Forms</h4><div className="value">{forms}</div></motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}><h4>Pages</h4><div className="value">{pages}</div></motion.div>
        </div>
        <details>
          <summary style={sectionStyle}>▶ Raw JSON</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(schemas, null, 2)}</pre></div>
        </details>
      </motion.div>
    );
  };

  const renderValidation = () => {
    const val = stages?.validation;
    if (!val) return null;
    
    const sectionStyle = { padding: '0.75rem', background: 'var(--bg-dark)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', border: '1px solid var(--border)', marginBottom: '0.5rem' };
    
    return (
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div className="metrics-grid">
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Validation Score</h4>
            <div className="value">{val.score}/100</div>
          </motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Status</h4>
            <div className="value" style={{ color: val.is_valid ? 'var(--success)' : 'var(--error)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {val.is_valid ? <CheckCircle size={32} /> : <AlertTriangle size={32} />}
              {val.is_valid ? 'PASS' : 'FAIL'}
            </div>
          </motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Errors</h4>
            <div className="value" style={{ color: val.errors?.length ? 'var(--error)' : 'inherit'}}>{val.errors?.length || 0}</div>
          </motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Warnings</h4>
            <div className="value" style={{ color: val.warnings?.length ? 'var(--warning)' : 'inherit'}}>{val.warnings?.length || 0}</div>
          </motion.div>
        </div>
        <details>
          <summary style={sectionStyle}>▶ Raw JSON</summary>
          <div style={{ padding: '0.5rem 0' }}><pre>{JSON.stringify(val, null, 2)}</pre></div>
        </details>
      </motion.div>
    );
  };

  return (
    <div className="panel" style={{ flex: 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <Settings2 size={32} color="var(--accent)" />
        <h2 style={{ margin: 0 }} className="gradient-text">Architectural Blueprint</h2>
      </div>
      
      {renderSummaryHeader()}

      <div className="tabs">
        <button className={`tab ${activeTab === 'intent' ? 'active' : ''}`} onClick={() => setActiveTab('intent')}>Intent Extraction</button>
        <button className={`tab ${activeTab === 'architecture' ? 'active' : ''}`} onClick={() => setActiveTab('architecture')}>Architecture</button>
        <button className={`tab ${activeTab === 'schemas' ? 'active' : ''}`} onClick={() => setActiveTab('schemas')}>Schemas</button>
        <button className={`tab ${activeTab === 'validation' ? 'active' : ''}`} onClick={() => setActiveTab('validation')}>Validation</button>
      </div>

      <div className="tab-content" style={{ position: 'relative' }}>
        <AnimatePresence mode="wait">
          {activeTab === 'intent' && (
            <motion.div key="intent" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
              <pre>{JSON.stringify(stages?.intent, null, 2)}</pre>
            </motion.div>
          )}
          {activeTab === 'architecture' && (
            <motion.div key="architecture" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
              {renderArchitecture()}
            </motion.div>
          )}
          {activeTab === 'schemas' && (
            <motion.div key="schemas" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
              {renderSchemas()}
            </motion.div>
          )}
          {activeTab === 'validation' && (
            <motion.div key="validation" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
              {renderValidation()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
