import { useEffect, useState } from 'react';
import api from '../api/client';
import Button from '../components/Button';
import Badge from '../components/Badge';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';

export default function Recommendations() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/recommendations');
      setItems(res.data);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const generate = async () => {
    setGenerating(true);
    try {
      const res = await api.post('/api/recommendations/generate');
      setItems(res.data);
      toast('Fresh AI recommendations ready');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold">AI sales recommendations</h2>
          <p className="text-sm text-ink-500">
            Who to contact first, where the pipeline leaks, and which industries win.
          </p>
        </div>
        <Button loading={generating} onClick={generate}>
          Regenerate insights
        </Button>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : items.length === 0 ? (
        <EmptyState
          title="No recommendations yet"
          description="Generate insights from your current book of leads."
          actionLabel="Generate now"
          onAction={generate}
        />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {items.map((rec) => (
            <div
              key={rec.id}
              className={`rounded-2xl border bg-white p-5 shadow-soft ${
                rec.priority === 'High' ? 'border-brand-300' : 'border-slate-200'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">{rec.category}</p>
                  <h3 className="mt-1 font-display text-xl font-semibold text-ink-900">{rec.title}</h3>
                </div>
                <Badge tone={rec.priority}>{rec.priority}</Badge>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-ink-600">{rec.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
