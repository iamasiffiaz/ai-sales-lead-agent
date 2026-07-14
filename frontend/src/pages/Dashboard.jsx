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
import StatCard from '../components/StatCard';
import ChartCard from '../components/ChartCard';
import LoadingSpinner from '../components/LoadingSpinner';
import Badge from '../components/Badge';
import Button from '../components/Button';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';

const COLORS = ['#DC2626', '#D97706', '#64748B', '#059669', '#0B1220', '#F59E0B'];

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = () => {
    setLoading(true);
    setError('');
    api
      .get('/api/analytics/dashboard')
      .then((res) => setData(res.data))
      .catch((err) => {
        setError(err.message);
        toast(err.message, 'error');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard..." />;
  if (error || !data) {
    return (
      <EmptyState
        icon="chart"
        title="Dashboard unavailable"
        description={error || 'Could not load analytics. Start the API and run seed.py.'}
        actionLabel="Retry"
        onAction={load}
      />
    );
  }

  const classData = [
    { name: 'Hot', value: data.hot_leads },
    { name: 'Warm', value: data.warm_leads },
    { name: 'Cold', value: data.cold_leads },
  ];

  return (
    <div className="space-y-6 animate-rise">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="page-header">
          <p className="section-label">Sales command center</p>
          <h2 className="page-title">Pipeline health at a glance</h2>
          <p className="page-subtitle">Live totals, classification mix, and AI next moves.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/app/follow-ups">
            <Button variant="outline">Follow-ups due ({data.follow_ups_due})</Button>
          </Link>
          <Link to="/app/leads">
            <Button variant="outline">Manage leads</Button>
          </Link>
          <Link to="/app/recommendations">
            <Button>AI insights</Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total leads" value={data.total_leads} accent="ink" />
        <StatCard label="Hot leads" value={data.hot_leads} accent="hot" hint="Score 75–100 · contact first" />
        <StatCard label="Warm leads" value={data.warm_leads} accent="warm" hint="Score 45–74 · nurture" />
        <StatCard label="Cold leads" value={data.cold_leads} accent="cold" hint="Score 1–44 · low touch" />
        <StatCard label="Average score" value={data.average_score} accent="brand" />
        <StatCard label="Follow-ups due" value={data.follow_ups_due} accent="warm" />
        <StatCard label="Emails generated" value={data.emails_generated} accent="brand" />
        <StatCard label="Won / Lost" value={`${data.won_count} / ${data.lost_count}`} accent="ink" />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Conversion pipeline" subtitle="Leads by stage">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.pipeline_chart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="status" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#059669" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Lead sources" subtitle="Where opportunities come from">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.source_breakdown} dataKey="count" nameKey="source" outerRadius={90} label>
                {data.source_breakdown.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ChartCard title="Classification mix" subtitle="Hot vs Warm vs Cold">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={classData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {classData.map((entry, i) => (
                  <Cell key={entry.name} fill={COLORS[i]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="surface-card p-5">
          <div className="flex items-center justify-between gap-2">
            <div>
              <h3 className="font-display text-lg font-semibold">Recent AI recommendations</h3>
              <p className="text-sm text-ink-500">What to prioritize this week</p>
            </div>
            <Link to="/app/recommendations">
              <Button size="sm" variant="ghost">
                View all
              </Button>
            </Link>
          </div>
          <div className="mt-4 space-y-3">
            {data.recent_recommendations?.length ? (
              data.recent_recommendations.map((rec) => (
                <div key={rec.id} className="rounded-xl border border-slate-100 bg-slate-50/80 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-semibold text-ink-900">{rec.title}</p>
                    <Badge tone={rec.priority}>{rec.priority}</Badge>
                  </div>
                  <p className="mt-1 text-xs text-ink-500">{rec.category}</p>
                  <p className="mt-2 text-sm leading-relaxed text-ink-600">{rec.content}</p>
                </div>
              ))
            ) : (
              <EmptyState
                title="No recommendations yet"
                description="Generate AI insights from your current book of business."
                actionLabel="Open AI Insights"
                onAction={() => {
                  window.location.href = '/app/recommendations';
                }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
