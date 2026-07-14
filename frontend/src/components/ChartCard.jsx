export default function ChartCard({ title, subtitle, children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-slate-200 bg-white p-5 shadow-soft ${className}`}>
      <div className="mb-4">
        <h3 className="font-display text-lg font-semibold text-ink-900">{title}</h3>
        {subtitle && <p className="text-sm text-ink-500">{subtitle}</p>}
      </div>
      <div className="h-64 w-full">{children}</div>
    </div>
  );
}
