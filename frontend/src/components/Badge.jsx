const styles = {
  Hot: 'bg-hot-soft text-hot border-hot-border ring-1 ring-hot/10',
  Warm: 'bg-warm-soft text-warm border-warm-border ring-1 ring-warm/10',
  Cold: 'bg-cold-soft text-cold border-cold-border ring-1 ring-cold/10',
  High: 'bg-brand-50 text-brand-700 border-brand-200',
  Medium: 'bg-slate-50 text-ink-700 border-slate-200',
  Low: 'bg-white text-ink-500 border-slate-200',
  Won: 'bg-brand-50 text-brand-700 border-brand-200',
  Lost: 'bg-slate-100 text-slate-600 border-slate-200',
  Draft: 'bg-slate-50 text-ink-600 border-slate-200',
  Sent: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Pending: 'bg-amber-50 text-amber-700 border-amber-200',
  Overdue: 'bg-red-50 text-red-700 border-red-200',
  Completed: 'bg-brand-50 text-brand-700 border-brand-200',
  New: 'bg-sky-50 text-sky-700 border-sky-200',
  Contacted: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  Qualified: 'bg-violet-50 text-violet-700 border-violet-200',
  'Proposal Sent': 'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200',
};

export default function Badge({ children, tone, className = '', size = 'md' }) {
  const key = tone || children;
  const color = styles[key] || 'bg-slate-50 text-ink-700 border-slate-200';
  const sizing = size === 'sm' ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs';
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border font-semibold ${sizing} ${color} ${className}`}
    >
      {(key === 'Hot' || key === 'Warm' || key === 'Cold') && (
        <span
          className={`h-1.5 w-1.5 rounded-full ${
            key === 'Hot' ? 'bg-hot' : key === 'Warm' ? 'bg-warm' : 'bg-cold'
          }`}
        />
      )}
      {children}
    </span>
  );
}

export function ScorePill({ score, classification }) {
  if (score == null) return <span className="text-ink-400">—</span>;
  const ring =
    classification === 'Hot'
      ? 'bg-ink-900 text-white ring-hot/30'
      : classification === 'Warm'
        ? 'bg-ink-800 text-white ring-warm/30'
        : 'bg-slate-600 text-white ring-cold/20';
  return (
    <span className={`inline-flex min-w-[2.25rem] items-center justify-center rounded-md px-2 py-0.5 text-xs font-bold ring-2 ${ring}`}>
      {score}
    </span>
  );
}
