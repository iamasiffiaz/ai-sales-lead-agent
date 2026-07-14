import { Routes, Route } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Leads from './pages/Leads';
import LeadDetails from './pages/LeadDetails';
import ImportLeads from './pages/ImportLeads';
import Pipeline from './pages/Pipeline';
import Emails from './pages/Emails';
import FollowUps from './pages/FollowUps';
import Analytics from './pages/Analytics';
import Recommendations from './pages/Recommendations';
import Settings from './pages/Settings';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/app" element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="leads" element={<Leads />} />
        <Route path="leads/:id" element={<LeadDetails />} />
        <Route path="import" element={<ImportLeads />} />
        <Route path="pipeline" element={<Pipeline />} />
        <Route path="emails" element={<Emails />} />
        <Route path="follow-ups" element={<FollowUps />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
