import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import api from '../api/client';
import ChartCard from '../components/ChartCard';
import LoadingSpinner from '../components/LoadingSpinner';
import Badge from '../components/Badge';
import StatCard from '../components/StatCard';
import Table from '../components/Table';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';

const COLORS = ['#DC2626', '#D97706', '#64748B', '#059669', '#0B1220', '#F59E0B', '#047857'];

export default function Analytics() {
  const [data, setData] = useState(null);
  const [pipeline, setPipeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    Promise.all([api.get('/api/analytics/leads'), api.get('/api/analytics/pipeline')])
      .then(([leadsRes, pipeRes]) => {
        setData(leadsRes.data);
        setPipeline(pipeRes.data);
      })
      .catch((err) => {
        setError(err.message);
        toast(err.message, 'error');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingSpinner label="Loading analytics..." />;
  if (error || !data) {
    return (
      <EmptyState
        icon="chart"
        title="Analytics unavailable"
        description={error || 'Could not load analytics data.'}
        actionLabel="Retry"
        onAction={load}
      />
    );
  }

  const columns = [
    {
      key: 'full_name',
      label: 'Lead',
      render: (r) => (
        <Link to={`/app/leads/${r.id}`} className="font-semibold text-brand-700 hover:underline">
          {r.full_name}
        </Link>
      ),
    },
    { key: 'company', label: 'Company' },
    {
      key: 'ai_score',
      label: 'Score',
      render: (r) => <span className="font-bold">{r.ai_score}</span>,
    },
    {
      key: 'ai_classification',
      label: 'Class',
      render: (r) => <Badge tone={r.ai_classification}>{r.ai_classification}</Badge>,
    },
    { key: 'industry', label: 'Industry' },
    { key: 'status', label: 'Status' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-semibold">Analytics</h2>
        <p className="text-sm text-ink-500">Performance across classification, source, status, and industry.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Follow-up completion"
          value={`${data.follow_up_completion_rate}%`}
          accent="brand"
        />
        <StatCard label="Won" value={data.won_lost_summary.won} accent="brand" />
        <StatCard label="Lost" value={data.won_lost_summary.lost} accent="cold" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Leads by classification">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.by_classification} dataKey="value" nameKey="name" outerRadius={90} label>
                {data.by_classification.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Leads by source">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.by_source}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#047857" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Leads by status">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.by_status}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#0B1220" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Average score by industry">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.avg_score_by_industry}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="industry" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="average_score" fill="#D97706" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {pipeline && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
          <h3 className="font-display text-lg font-semibold">Stage conversion snapshot</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {pipeline.conversion_rates.map((c) => (
              <div key={`${c.from}-${c.to}`} className="rounded-lg border border-slate-200 px-3 py-2 text-sm">
                {c.from} → {c.to}: <strong>{c.rate}%</strong>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h3 className="mb-3 font-display text-lg font-semibold">Top high-value leads</h3>
        <Table columns={columns} rows={data.top_high_value_leads} />
      </div>
    </div>
  );
}
