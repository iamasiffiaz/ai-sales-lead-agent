export default function StatCard({ label, value, hint, accent = 'brand' }) {
  const accents = {
    brand: 'from-brand-600 to-brand-800',
    hot: 'from-red-500 to-red-700',
    warm: 'from-amber-500 to-amber-700',
    cold: 'from-slate-500 to-slate-700',
    ink: 'from-ink-800 to-ink-950',
  };
  return (
    <div className="surface-card relative overflow-hidden p-5 transition hover:-translate-y-0.5 hover:shadow-soft">
      <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${accents[accent]}`} />
      <p className="section-label">{label}</p>
      <p className="mt-2 font-display text-3xl font-bold tracking-tight text-ink-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-ink-500">{hint}</p>}
    </div>
  );
}
