import { useState, useEffect } from 'react';

export const PipelineResults = () => {
  const [activeTab, setActiveTab] = useState('intent');
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const raw = localStorage.getItem('compile_results');
    if (raw) setData(JSON.parse(raw));
  }, []);

  if (!data) {
    return <div className="panel">No data available. Please run a prompt first.</div>;
  }

  const { stages } = data;

  const renderSummaryHeader = () => {
    const confidence = stages?.intent?.confidence || 0;
    const valScore = stages?.validation?.score || 0;
    const modulesCount = stages?.architecture?.modules?.length || 0;
    const entitiesCount = stages?.architecture?.entities?.length || 0;
    const apiEndpointsCount = stages?.schemas?.api?.length || 0;
    const pagesCount = stages?.schemas?.ui?.length || 0;

    return (
      <div className="metrics-grid" style={{ marginBottom: '2rem' }}>
        <div className="metric-card">
          <h4>Confidence</h4>
          <div className="value">{(confidence * 100).toFixed(0)}%</div>
        </div>
        <div className="metric-card">
          <h4>Validation Score</h4>
          <div className="value">{valScore}/100</div>
        </div>
        <div className="metric-card">
          <h4>Modules</h4>
          <div className="value">{modulesCount}</div>
        </div>
        <div className="metric-card">
          <h4>Entities</h4>
          <div className="value">{entitiesCount}</div>
        </div>
        <div className="metric-card">
          <h4>API Endpoints</h4>
          <div className="value">{apiEndpointsCount}</div>
        </div>
        <div className="metric-card">
          <h4>Pages</h4>
          <div className="value">{pagesCount}</div>
        </div>
      </div>
    );
  };

  const renderArchitecture = () => {
    const arch = stages?.architecture;
    if (!arch) return null;
    
    const sectionStyle = { padding: '0.5rem', background: 'var(--bg-secondary)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' };
    
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <details>
          <summary style={sectionStyle}>▶ Modules ({arch.modules?.length || 0})</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(arch.modules, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ Entities ({arch.entities?.length || 0})</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(arch.entities, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ User Flows ({arch.user_flows?.length || 0})</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(arch.user_flows, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ Permissions ({arch.permissions?.length || 0})</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(arch.permissions, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ System Components ({arch.system_components?.length || 0})</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(arch.system_components, null, 2)}</pre></div>
        </details>
        <details>
          <summary style={sectionStyle}>▶ Raw JSON</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(arch, null, 2)}</pre></div>
        </details>
      </div>
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

    const sectionStyle = { padding: '0.5rem', background: 'var(--bg-secondary)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' };

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="metrics-grid">
          <div className="metric-card"><h4>Tables</h4><div className="value">{tables}</div></div>
          <div className="metric-card"><h4>API Endpoints</h4><div className="value">{endpoints}</div></div>
          <div className="metric-card"><h4>Forms</h4><div className="value">{forms}</div></div>
          <div className="metric-card"><h4>Pages</h4><div className="value">{pages}</div></div>
        </div>
        <details>
          <summary style={sectionStyle}>▶ Raw JSON</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(schemas, null, 2)}</pre></div>
        </details>
      </div>
    );
  };

  const renderValidation = () => {
    const val = stages?.validation;
    if (!val) return null;
    
    const sectionStyle = { padding: '0.5rem', background: 'var(--bg-secondary)', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' };
    
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>Validation Score</h4>
            <div className="value">{val.score}/100</div>
          </div>
          <div className="metric-card">
            <h4>Status</h4>
            <div className="value" style={{ color: val.is_valid ? '#4ade80' : '#f87171' }}>
              {val.is_valid ? 'PASS' : 'FAIL'}
            </div>
          </div>
          <div className="metric-card">
            <h4>Errors</h4>
            <div className="value">{val.errors?.length || 0}</div>
          </div>
          <div className="metric-card">
            <h4>Warnings</h4>
            <div className="value">{val.warnings?.length || 0}</div>
          </div>
        </div>
        <details>
          <summary style={sectionStyle}>▶ Raw JSON</summary>
          <div style={{ marginTop: '0.5rem' }}><pre>{JSON.stringify(val, null, 2)}</pre></div>
        </details>
      </div>
    );
  };

  return (
    <div className="panel">
      <h2 style={{ marginBottom: '1.5rem' }}>Pipeline Results</h2>
      
      {renderSummaryHeader()}

      <div className="tabs">
        <button className={`tab ${activeTab === 'intent' ? 'active' : ''}`} onClick={() => setActiveTab('intent')}>Intent Extraction</button>
        <button className={`tab ${activeTab === 'architecture' ? 'active' : ''}`} onClick={() => setActiveTab('architecture')}>Architecture</button>
        <button className={`tab ${activeTab === 'schemas' ? 'active' : ''}`} onClick={() => setActiveTab('schemas')}>Schemas</button>
        <button className={`tab ${activeTab === 'validation' ? 'active' : ''}`} onClick={() => setActiveTab('validation')}>Validation</button>
      </div>

      <div className="tab-content">
        {activeTab === 'intent' && <pre>{JSON.stringify(stages?.intent, null, 2)}</pre>}
        {activeTab === 'architecture' && renderArchitecture()}
        {activeTab === 'schemas' && renderSchemas()}
        {activeTab === 'validation' && renderValidation()}
      </div>
    </div>
  );
};
