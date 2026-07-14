import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import PipelineColumn from '../components/PipelineColumn';
import LoadingSpinner from '../components/LoadingSpinner';
import Modal from '../components/Modal';
import Badge, { ScorePill } from '../components/Badge';
import Button from '../components/Button';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';

export default function Pipeline() {
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/pipeline');
      setColumns(res.data.columns);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onMove = async (lead, status) => {
    try {
      await api.put(`/api/pipeline/move-lead/${lead.id}`, { status });
      toast(`Moved ${lead.full_name} → ${status}`);
      if (selected?.id === lead.id) setSelected({ ...lead, status });
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  if (loading) return <LoadingSpinner label="Loading pipeline..." />;

  const total = columns.reduce((sum, c) => sum + c.leads.length, 0);

  return (
    <div className="space-y-4 animate-rise">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="page-header">
          <h2 className="page-title">Sales pipeline</h2>
          <p className="page-subtitle">
            {total} leads across stages. Use “Move stage” on each card to update status.
          </p>
        </div>
        <Button variant="outline" onClick={load}>
          Refresh
        </Button>
      </div>

      {total === 0 ? (
        <EmptyState
          title="Pipeline is empty"
          description="Create or import leads to populate your Kanban stages."
          actionLabel="Go to leads"
          onAction={() => navigate('/app/leads')}
        />
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-2">
          {columns.map((col) => (
            <PipelineColumn
              key={col.status}
              status={col.status}
              leads={col.leads}
              onLeadClick={setSelected}
              onMove={onMove}
            />
          ))}
        </div>
      )}

      <Modal open={!!selected} onClose={() => setSelected(null)} title={selected?.full_name || 'Lead'} wide>
        {selected && (
          <div className="space-y-4 text-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-ink-500">
                  {selected.job_title || 'Contact'} · {selected.company}
                </p>
                <p className="mt-1 text-ink-600">{selected.email}</p>
              </div>
              <ScorePill score={selected.ai_score} classification={selected.ai_classification} />
            </div>
            <div className="flex flex-wrap gap-2">
              {selected.ai_classification && (
                <Badge tone={selected.ai_classification}>{selected.ai_classification}</Badge>
              )}
              <Badge tone={selected.status}>{selected.status}</Badge>
              {selected.priority && <Badge tone={selected.priority}>{selected.priority}</Badge>}
            </div>
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="section-label">Requirement</p>
              <p className="mt-1 text-ink-700">{selected.requirement || 'No requirement listed.'}</p>
            </div>
            {selected.next_action && (
              <div className="rounded-xl border border-brand-100 bg-brand-50/60 p-3">
                <p className="section-label text-brand-700">Suggested next action</p>
                <p className="mt-1 text-ink-800">{selected.next_action}</p>
              </div>
            )}
            <div className="flex flex-wrap gap-2 pt-1">
              <Button onClick={() => navigate(`/app/leads/${selected.id}`)}>Open full record</Button>
              <Button
                variant="outline"
                onClick={() => navigate(`/app/leads/${selected.id}`)}
              >
                Generate email
              </Button>
              <Button variant="ghost" onClick={() => setSelected(null)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
