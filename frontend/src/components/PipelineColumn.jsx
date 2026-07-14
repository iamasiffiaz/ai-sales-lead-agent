import LeadCard from './LeadCard';

const stageAccents = {
  New: 'border-t-sky-500',
  Contacted: 'border-t-indigo-500',
  Qualified: 'border-t-violet-500',
  'Proposal Sent': 'border-t-fuchsia-500',
  Won: 'border-t-brand-500',
  Lost: 'border-t-slate-400',
};

export default function PipelineColumn({ status, leads, onLeadClick, onMove }) {
  const scored = leads.filter((l) => l.ai_score != null);
  const avg =
    scored.length > 0
      ? Math.round(scored.reduce((sum, l) => sum + l.ai_score, 0) / scored.length)
      : null;

  return (
    <div
      className={`flex min-w-[280px] flex-1 flex-col rounded-2xl border border-slate-200 border-t-4 bg-slate-50/90 ${
        stageAccents[status] || 'border-t-slate-300'
      }`}
    >
      <div className="flex items-center justify-between gap-2 px-3 py-3">
        <div>
          <h3 className="text-sm font-bold text-ink-800">{status}</h3>
          {avg != null && !Number.isNaN(avg) && (
            <p className="text-[11px] text-ink-400">Avg score {avg || '—'}</p>
          )}
        </div>
        <span className="rounded-full bg-white px-2.5 py-0.5 text-xs font-semibold text-ink-600 shadow-sm">
          {leads.length}
        </span>
      </div>
      <div className="flex max-h-[70vh] flex-1 flex-col gap-2.5 overflow-y-auto px-3 pb-3 scrollbar-thin">
        {leads.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 px-3 py-8 text-center text-xs text-ink-400">
            No leads in this stage
          </div>
        )}
        {leads.map((lead) => (
          <LeadCard key={lead.id} lead={lead} onClick={onLeadClick} onMove={onMove} />
        ))}
      </div>
    </div>
  );
}
