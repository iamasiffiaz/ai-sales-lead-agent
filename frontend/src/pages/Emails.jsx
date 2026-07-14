import { useEffect, useState } from 'react';
import api from '../api/client';
import Button from '../components/Button';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import Badge from '../components/Badge';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import Modal from '../components/Modal';
import { toast } from '../components/ToastProvider';
import { formatDateTime } from '../utils/formatDate';

export default function Emails() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/emails');
      setEmails(res.data);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const save = async () => {
    try {
      await api.put(`/api/emails/${editing.id}`, {
        subject: editing.subject,
        body: editing.body,
        status: editing.status,
      });
      toast('Draft saved');
      setEditing(null);
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="font-display text-2xl font-semibold">Email drafts</h2>
        <p className="text-sm text-ink-500">Edit, copy, and mark outreach as sent.</p>
      </div>

      {emails.length === 0 ? (
        <EmptyState
          icon="mail"
          title="No email drafts"
          description="Open a lead and generate a personalized email to get started."
          actionLabel="Go to leads"
          onAction={() => {
            window.location.href = '/app/leads';
          }}
        />
      ) : (
        <div className="grid gap-3 lg:grid-cols-2">
          {emails.map((email) => (
            <div key={email.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="font-semibold text-ink-900">{email.subject}</p>
                  <p className="text-xs text-ink-500">
                    {email.lead_name} · {email.lead_company} · {email.email_type}
                  </p>
                </div>
                <Badge tone={email.status}>{email.status}</Badge>
              </div>
              <p className="mt-3 line-clamp-4 whitespace-pre-wrap text-sm text-ink-600">{email.body}</p>
              <p className="mt-2 text-xs text-ink-400">{formatDateTime(email.created_at)}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button size="sm" variant="outline" onClick={() => setEditing(email)}>
                  Edit
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    navigator.clipboard.writeText(`${email.subject}\n\n${email.body}`);
                    toast('Copied');
                  }}
                >
                  Copy
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={async () => {
                    await api.put(`/api/emails/${email.id}`, { status: 'Sent' });
                    toast('Marked sent');
                    load();
                  }}
                >
                  Mark sent
                </Button>
                <Button
                  size="sm"
                  variant="danger"
                  onClick={async () => {
                    await api.delete(`/api/emails/${email.id}`);
                    toast('Deleted');
                    load();
                  }}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={!!editing} onClose={() => setEditing(null)} title="Edit email draft" wide>
        {editing && (
          <div className="space-y-3">
            <Input
              label="Subject"
              value={editing.subject}
              onChange={(e) => setEditing({ ...editing, subject: e.target.value })}
            />
            <Textarea
              label="Body"
              rows={12}
              value={editing.body}
              onChange={(e) => setEditing({ ...editing, body: e.target.value })}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setEditing(null)}>
                Cancel
              </Button>
              <Button onClick={save}>Save draft</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
