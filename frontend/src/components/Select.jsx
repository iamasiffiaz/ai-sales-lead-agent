export default function Select({ label, children, className = '', ...props }) {
  return (
    <label className={`block ${className}`}>
      {label && <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-ink-500">{label}</span>}
      <select
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-ink-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        {...props}
      >
        {children}
      </select>
    </label>
  );
}
