import Badge, { ScorePill } from './Badge';
import { LEAD_STATUSES } from '../utils/constants';

export default function LeadCard({ lead, onClick, onMove }) {
  const isHot = lead.ai_classification === 'Hot';
  return (
    <div
      className={`group rounded-xl border p-3 text-left transition hover:-translate-y-0.5 hover:shadow-card ${
        isHot
          ? 'border-hot-border bg-gradient-to-br from-hot-soft via-white to-white'
          : 'border-slate-200 bg-white'
      }`}
    >
      <button type="button" className="w-full text-left" onClick={() => onClick?.(lead)}>
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate font-semibold text-ink-900">{lead.full_name}</p>
            <p className="truncate text-xs text-ink-500">{lead.company}</p>
          </div>
          <ScorePill score={lead.ai_score} classification={lead.ai_classification} />
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {lead.ai_classification && <Badge tone={lead.ai_classification}>{lead.ai_classification}</Badge>}
          {lead.priority && <Badge tone={lead.priority} size="sm">{lead.priority}</Badge>}
        </div>
        {lead.requirement && <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-ink-600">{lead.requirement}</p>}
        {lead.next_action && (
          <p className="mt-2 rounded-lg bg-slate-50 px-2 py-1.5 text-[11px] leading-snug text-ink-500">
            Next: {lead.next_action}
          </p>
        )}
      </button>
      {onMove && (
        <div className="mt-3 border-t border-slate-100 pt-2">
          <label className="section-label mb-1 block">Move stage</label>
          <select
            className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2 py-1.5 text-xs outline-none focus:border-brand-500"
            value={lead.status}
            onChange={(e) => onMove(lead, e.target.value)}
            onClick={(e) => e.stopPropagation()}
          >
            {LEAD_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
