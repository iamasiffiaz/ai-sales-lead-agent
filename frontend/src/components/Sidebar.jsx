import { NavLink } from 'react-router-dom';
import { BRAND, NAV_ITEMS } from '../utils/constants';

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && <button className="fixed inset-0 z-30 bg-ink-950/40 lg:hidden" onClick={onClose} aria-label="Close menu" />}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-white/10 bg-ink-950 text-white transition-transform lg:static lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="border-b border-white/10 px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 font-display text-sm font-bold shadow-soft">
              Q
            </div>
            <div>
              <p className="font-display text-xl font-bold tracking-tight text-white">{BRAND.name}</p>
              <p className="text-[11px] text-emerald-200/80">Lead qualification OS</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={onClose}
              className={({ isActive }) =>
                `block rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-white/10 p-4">
          <p className="text-xs font-medium text-slate-300">Demo workspace</p>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-500">
            FastAPI · React · Postgres-ready · LLM scoring
          </p>
        </div>
      </aside>
    </>
  );
}
