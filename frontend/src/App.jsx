import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, AlertTriangle, CheckCircle2, Database } from 'lucide-react';
import './styles.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [quality, setQuality] = useState([]);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/metrics/reliability`).then((response) => response.json()),
      fetch(`${API_URL}/quality/summary`).then((response) => response.json()),
    ]).then(([nextMetrics, nextQuality]) => {
      setMetrics(nextMetrics);
      setQuality(nextQuality);
    }).catch(() => {
      setMetrics({ successful_runs: 0, failed_runs: 0, rows_loaded: 0, rows_rejected: 0, success_rate: 0 });
    });
  }, []);

  return (
    <main className="shell">
      <section className="topbar">
        <div>
          <h1>ETL Reliability Console</h1>
          <p>Airflow orchestration, data quality and recovery telemetry.</p>
        </div>
        <Activity aria-hidden="true" />
      </section>

      <section className="metrics">
        <Metric icon={<CheckCircle2 />} label="Success rate" value={`${Math.round((metrics?.success_rate || 0) * 100)}%`} />
        <Metric icon={<Database />} label="Rows loaded" value={metrics?.rows_loaded ?? 0} />
        <Metric icon={<AlertTriangle />} label="Rows rejected" value={metrics?.rows_rejected ?? 0} />
      </section>

      <section className="panel">
        <h2>Latest quality checks</h2>
        <div className="table">
          {quality.length === 0 ? <p>No quality results yet.</p> : quality.map((row, index) => (
            <div className="row" key={`${row.rule_name}-${index}`}>
              <span>{row.rule_name}</span>
              <strong className={row.status === 'pass' ? 'pass' : 'fail'}>{row.status}</strong>
              <span>{row.failed_count} failures</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <article className="metric">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

createRoot(document.getElementById('root')).render(<App />);
