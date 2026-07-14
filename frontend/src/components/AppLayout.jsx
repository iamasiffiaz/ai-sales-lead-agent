import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { NAV_ITEMS } from '../utils/constants';

const titles = Object.fromEntries(NAV_ITEMS.map((n) => [n.to, n.label]));

export default function AppLayout() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const match = Object.keys(titles)
    .sort((a, b) => b.length - a.length)
    .find((path) => location.pathname === path || (path !== '/app' && location.pathname.startsWith(path)));
  const title = titles[match] || 'Dashboard';

  return (
    <div className="flex min-h-screen bg-app-mesh">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar title={title} subtitle="AI Sales & Lead Qualification Agent" onMenu={() => setOpen(true)} />
        <main className="flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
