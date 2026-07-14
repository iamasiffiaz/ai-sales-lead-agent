import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import Select from '../components/Select';
import Modal from '../components/Modal';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';
import { formatDate, relativeDue } from '../utils/formatDate';

export default function FollowUps() {
  const [items, setItems] = useState([]);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ lead_id: '', due_date: '', notes: '' });

  const load = async () => {
    setLoading(true);
    try {
      const params =
        filter === 'upcoming' ? { upcoming: true } : filter === 'overdue' ? { overdue: true } : {};
      const [fu, leadRes] = await Promise.all([
        api.get('/api/followups', { params }),
        api.get('/api/leads', { params: { page_size: 100, sort_by: 'ai_score', sort_dir: 'desc' } }),
      ]);
      setItems(fu.data);
      setLeads(leadRes.data.items);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  const create = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/followups', {
        lead_id: Number(form.lead_id),
        due_date: form.due_date,
        notes: form.notes,
      });
      toast('Follow-up created');
      setOpen(false);
      setForm({ lead_id: '', due_date: '', notes: '' });
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const complete = async (id) => {
    try {
      await api.put(`/api/followups/${id}`, { status: 'Completed' });
      toast('Marked completed');
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const generateFollowupEmail = async (item) => {
    try {
      await api.post(`/api/emails/generate/${item.lead_id}`, { email_type: 'Follow-up' });
      toast('Follow-up email drafted');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold">Follow-up reminders</h2>
          <p className="text-sm text-ink-500">Never lose track of Warm and Hot conversations.</p>
        </div>
        <Button onClick={() => setOpen(true)}>New follow-up</Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {[
          ['all', 'All'],
          ['upcoming', 'Upcoming'],
          ['overdue', 'Overdue'],
        ].map(([value, label]) => (
          <Button
            key={value}
            size="sm"
            variant={filter === value ? 'primary' : 'outline'}
            onClick={() => setFilter(value)}
          >
            {label}
          </Button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : items.length === 0 ? (
        <EmptyState title="No follow-ups" description="Schedule a reminder from a lead or create one here." />
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className={`rounded-2xl border bg-white p-4 shadow-soft ${
                item.status === 'Overdue' ? 'border-red-200' : 'border-slate-200'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <Link to={`/app/leads/${item.lead_id}`} className="font-semibold text-brand-700 hover:underline">
                    {item.lead_name}
                  </Link>
                  <p className="text-sm text-ink-500">{item.lead_company}</p>
                  <p className="mt-2 text-sm text-ink-700">{item.notes}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge tone={item.status}>{item.status}</Badge>
                    {item.lead_classification && (
                      <Badge tone={item.lead_classification}>{item.lead_classification}</Badge>
                    )}
                    {item.lead_score != null && <Badge>Score {item.lead_score}</Badge>}
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{formatDate(item.due_date)}</p>
                  <p className="text-xs text-ink-500">{relativeDue(item.due_date)}</p>
                  <div className="mt-3 flex flex-wrap justify-end gap-2">
                    {item.status !== 'Completed' && (
                      <Button size="sm" onClick={() => complete(item.id)}>
                        Complete
                      </Button>
                    )}
                    <Button size="sm" variant="outline" onClick={() => generateFollowupEmail(item)}>
                      AI follow-up email
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={async () => {
                        await api.delete(`/api/followups/${item.id}`);
                        toast('Deleted');
                        load();
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Schedule follow-up">
        <form className="space-y-3" onSubmit={create}>
          <Select
            label="Lead"
            required
            value={form.lead_id}
            onChange={(e) => setForm({ ...form, lead_id: e.target.value })}
          >
            <option value="">Select lead</option>
            {leads.map((l) => (
              <option key={l.id} value={l.id}>
                {l.full_name} — {l.company}
              </option>
            ))}
          </Select>
          <Input
            label="Due date"
            type="date"
            required
            value={form.due_date}
            onChange={(e) => setForm({ ...form, due_date: e.target.value })}
          />
          <Textarea
            label="Notes"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Save</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
