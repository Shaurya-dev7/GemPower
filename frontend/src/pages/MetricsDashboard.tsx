import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { Activity, Zap, Clock, ShieldCheck } from 'lucide-react';
import { API_URL } from '../config/api';

export const MetricsDashboard = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/metrics`);
        setMetrics(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) return (
    <div className="panel" style={{ display: 'flex', flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
        <Activity size={48} color="var(--accent)" />
      </motion.div>
    </div>
  );
  
  if (!metrics || metrics.error) return <div className="panel" style={{flex: 1}}>{metrics?.error || "Failed to load"}</div>;

  const { system_metrics, reliability_report, cost_analysis, avg_stage_timings, is_test_mode } = metrics;

  const formatLatency = (sec: number | undefined) => {
    if (sec === undefined) return '0 ms';
    if (is_test_mode || sec === 0 || (sec < 0.001 && sec > 0)) return '< 1 ms';
    if (sec < 1) return `${(sec * 1000).toFixed(2)} ms`;
    return `${sec.toFixed(2)} s`;
  };

  const tokens = cost_analysis?.avg_tokens_per_request;
  const isEstimated = is_test_mode || (tokens !== undefined && tokens < 1 && tokens > 0);
  const tokenDisplay = tokens !== undefined ? `${Math.round(tokens)}${isEstimated ? ' (Est.)' : ''}` : '0';

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0, transition: { duration: 0.3 } }
  };

  return (
    <motion.div 
      style={{ display: 'flex', flexDirection: 'column', gap: '2rem', flex: 1 }}
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
        <Activity size={32} color="var(--accent)" />
        <h2 style={{ margin: 0 }} className="gradient-text">Telemetry & Insights</h2>
      </div>

      <motion.div className="panel" variants={itemVariants}>
        <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Zap size={20} color="var(--accent)"/> System Overview
        </h3>
        <div className="metrics-grid">
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Total Success Rate</h4>
            <div className="value">{Math.round(system_metrics?.total_success_rate || 0)}%</div>
          </motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Determinism Score</h4>
            <div className="value">{Math.round(system_metrics?.determinism_score || 0)}%</div>
          </motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Avg Latency</h4>
            <div className="value">{formatLatency(system_metrics?.avg_pipeline_latency)}</div>
          </motion.div>
        </div>
      </motion.div>

      <motion.div className="panel" variants={itemVariants}>
        <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ShieldCheck size={20} color="var(--success)"/> Reliability & Cost
        </h3>
        <div className="metrics-grid">
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Validation Accuracy</h4>
            <div className="value" style={{ color: 'var(--accent)' }}>
              {Math.round(reliability_report?.validation_accuracy || 0)}%
            </div>
          </motion.div>
          <motion.div className="metric-card" whileHover={{ scale: 1.02 }}>
            <h4>Avg Tokens / Request</h4>
            <div className="value" style={{ color: 'var(--accent)', fontSize: isEstimated ? '2rem' : 'inherit' }}>
              {tokenDisplay}
            </div>
          </motion.div>
        </div>
      </motion.div>

      <motion.div className="panel" variants={itemVariants} style={{ marginBottom: '2rem' }}>
        <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Clock size={20} color="var(--warning)"/> Pipeline Stage Timings
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {[
            { label: 'Intent Extraction', value: avg_stage_timings?.intent_ms },
            { label: 'Architecture Planner', value: avg_stage_timings?.architecture_ms },
            { label: 'Schema Generator', value: avg_stage_timings?.schema_ms },
            { label: 'Global Validation', value: avg_stage_timings?.validation_ms },
            { label: 'Runtime Engine', value: avg_stage_timings?.runtime_ms },
          ].map((stage, idx) => (
            <motion.div 
              key={idx}
              style={{ background: 'var(--bg-dark)', padding: '1rem', borderRadius: '4px', border: '1px solid var(--border)', borderLeft: '4px solid var(--border)' }}
              whileHover={{ y: -2, borderLeftColor: 'var(--accent)' }}
            >
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px' }}>{stage.label}</div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 'bold', fontSize: '1.2rem' }}>{stage.value?.toFixed(1) || '0.0'} ms</div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};
