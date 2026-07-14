import Button from './Button';

export default function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon = 'inbox',
}) {
  const icons = {
    inbox: (
      <path d="M4 7h16M4 12h10M4 17h7" strokeLinecap="round" />
    ),
    chart: (
      <>
        <path d="M4 19V9M10 19V5M16 19v-7M22 19H2" strokeLinecap="round" />
      </>
    ),
    mail: (
      <path d="M4 6h16v12H4V6zm0 0l8 7 8-7" strokeLinecap="round" strokeLinejoin="round" />
    ),
    search: (
      <>
        <circle cx="11" cy="11" r="6" />
        <path d="M20 20l-3.5-3.5" strokeLinecap="round" />
      </>
    ),
  };

  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-gradient-to-b from-white to-slate-50/80 px-6 py-14 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-700 shadow-sm">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
          {icons[icon] || icons.inbox}
        </svg>
      </div>
      <h3 className="font-display text-xl font-semibold text-ink-900">{title}</h3>
      {description && <p className="mt-2 max-w-md text-sm leading-relaxed text-ink-500">{description}</p>}
      {actionLabel && onAction && (
        <Button className="mt-5" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
