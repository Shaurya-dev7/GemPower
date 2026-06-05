import { useState, useEffect } from 'react';
import axios from 'axios';

export const MetricsDashboard = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/metrics');
        setMetrics(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) return <div className="panel">Loading metrics...</div>;
  if (!metrics || metrics.error) return <div className="panel">{metrics?.error || "Failed to load"}</div>;

  const { system_metrics, reliability_report, cost_analysis, avg_stage_timings, is_test_mode } = metrics;

  const formatLatency = (sec: number | undefined) => {
    if (sec === undefined) return '0 ms';
    if (is_test_mode || sec === 0 || (sec < 0.001 && sec > 0)) return '< 1 ms';
    if (sec < 1) return `${(sec * 1000).toFixed(2)} ms`;
    return `${sec.toFixed(2)} s`;
  };

  const tokens = cost_analysis?.avg_tokens_per_request;
  const isEstimated = is_test_mode || (tokens !== undefined && tokens < 1 && tokens > 0);
  const tokenDisplay = tokens !== undefined ? `${Math.round(tokens)}${isEstimated ? ' (Estimated)' : ''}` : '0';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="panel">
        <h2 style={{ marginBottom: '1.5rem' }}>System Overview</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>Total Success Rate</h4>
            <div className="value">{Math.round(system_metrics?.total_success_rate || 0)}%</div>
          </div>
          <div className="metric-card">
            <h4>Determinism Score</h4>
            <div className="value">{Math.round(system_metrics?.determinism_score || 0)}%</div>
          </div>
          <div className="metric-card">
            <h4>Avg Latency</h4>
            <div className="value">{formatLatency(system_metrics?.avg_pipeline_latency)}</div>
          </div>
        </div>
      </div>

      <div className="panel">
        <h2 style={{ marginBottom: '1.5rem' }}>Reliability & Cost</h2>
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>Validation Accuracy</h4>
            <div className="value" style={{ background: 'linear-gradient(135deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text' }}>
              {Math.round(reliability_report?.validation_accuracy || 0)}%
            </div>
          </div>
          <div className="metric-card">
            <h4>Avg Tokens / Request</h4>
            <div className="value" style={{ background: 'linear-gradient(135deg, #a78bfa, #f472b6)', WebkitBackgroundClip: 'text', fontSize: isEstimated ? '1.5rem' : 'inherit' }}>
              {tokenDisplay}
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <h2 style={{ marginBottom: '1.5rem' }}>Pipeline Stage Timings</h2>
        <ul style={{ listStyle: 'none', color: 'var(--text-secondary)' }}>
          <li>Intent Extraction: {avg_stage_timings?.intent_ms?.toFixed(1)} ms</li>
          <li>Architecture Planner: {avg_stage_timings?.architecture_ms?.toFixed(1)} ms</li>
          <li>Schema Generator: {avg_stage_timings?.schema_ms?.toFixed(1)} ms</li>
          <li>Global Validation: {avg_stage_timings?.validation_ms?.toFixed(1)} ms</li>
          <li>Runtime Engine: {avg_stage_timings?.runtime_ms?.toFixed(1)} ms</li>
        </ul>
      </div>
    </div>
  );
};
