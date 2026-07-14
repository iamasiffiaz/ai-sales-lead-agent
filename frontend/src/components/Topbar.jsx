import { Link } from 'react-router-dom';
import Button from './Button';

export default function Topbar({ title, subtitle, onMenu }) {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur">
      <div className="flex items-center justify-between gap-3 px-4 py-3 lg:px-6">
        <div className="flex items-center gap-3">
          <button
            className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-sm lg:hidden"
            onClick={onMenu}
          >
            Menu
          </button>
          <div>
            <h1 className="font-display text-xl font-semibold text-ink-900">{title}</h1>
            {subtitle && <p className="text-xs text-ink-500">{subtitle}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/">
            <Button variant="ghost" size="sm">
              Landing
            </Button>
          </Link>
          <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 sm:flex">
            <span className="h-2 w-2 rounded-full bg-brand-500" />
            <span className="text-xs font-medium text-ink-600">Demo · Alex Morgan</span>
          </div>
        </div>
      </div>
    </header>
  );
}
