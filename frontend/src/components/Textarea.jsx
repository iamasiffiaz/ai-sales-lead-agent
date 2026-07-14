export default function Textarea({ label, className = '', rows = 4, ...props }) {
  return (
    <label className={`block ${className}`}>
      {label && <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-ink-500">{label}</span>}
      <textarea
        rows={rows}
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-ink-900 outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        {...props}
      />
    </label>
  );
}
