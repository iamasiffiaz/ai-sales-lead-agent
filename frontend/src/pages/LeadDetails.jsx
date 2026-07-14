import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';
import Badge, { ScorePill } from '../components/Badge';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import Textarea from '../components/Textarea';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';
import { EMAIL_TYPES, LEAD_SOURCES, LEAD_STATUSES, PRIORITIES } from '../utils/constants';
import { formatDate, formatDateTime } from '../utils/formatDate';

export default function LeadDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [emailType, setEmailType] = useState('First Outreach');
  const [generating, setGenerating] = useState(false);
  const [emails, setEmails] = useState([]);
  const [editingEmail, setEditingEmail] = useState(null);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [leadRes, emailRes] = await Promise.all([
        api.get(`/api/leads/${id}`),
        api.get('/api/emails', { params: { lead_id: id } }),
      ]);
      setLead(leadRes.data);
      setEmails(emailRes.data);
    } catch (err) {
      setError(err.message);
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const save = async () => {
    setSaving(true);
    try {
      const res = await api.put(`/api/leads/${id}`, lead);
      setLead(res.data);
      toast('Lead updated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const score = async () => {
    setScoring(true);
    try {
      await api.post(`/api/qualification/score/${id}`);
      toast('AI qualification complete');
      load();
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setScoring(false);
    }
  };

  const generateEmail = async () => {
    setGenerating(true);
    try {
      const res = await api.post(`/api/emails/generate/${id}`, { email_type: emailType });
      toast('Email draft generated');
      setEditingEmail(res.data);
      load();
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setGenerating(false);
    }
  };

  const saveEmail = async () => {
    if (!editingEmail) return;
    try {
      await api.put(`/api/emails/${editingEmail.id}`, {
        subject: editingEmail.subject,
        body: editingEmail.body,
      });
      toast('Draft saved');
      setEditingEmail(null);
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const setFollowUp = async () => {
    if (!lead.next_follow_up_date) {
      toast('Pick a follow-up date first', 'error');
      return;
    }
    try {
      await api.post('/api/followups', {
        lead_id: Number(id),
        due_date: lead.next_follow_up_date,
        notes: `Follow up with ${lead.full_name}`,
      });
      await api.put(`/api/leads/${id}`, { next_follow_up_date: lead.next_follow_up_date });
      toast('Follow-up scheduled');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  if (loading) return <LoadingSpinner label="Loading lead..." />;
  if (error || !lead) {
    return (
      <EmptyState
        title="Lead not found"
        description={error || 'This record may have been deleted.'}
        actionLabel="Back to leads"
        onAction={() => navigate('/app/leads')}
      />
    );
  }

  const q = lead.qualification;
  let factors = null;
  try {
    factors = q?.scoring_factors ? JSON.parse(q.scoring_factors) : null;
  } catch {
    factors = null;
  }

  return (
    <div className="space-y-4 animate-rise">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link to="/app/leads" className="text-sm font-medium text-brand-700 hover:underline">
            ← Back to leads
          </Link>
          <h2 className="mt-1 font-display text-2xl font-semibold sm:text-3xl">{lead.full_name}</h2>
          <p className="text-ink-500">
            {lead.job_title ? `${lead.job_title} · ` : ''}
            {lead.company}
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <ScorePill score={lead.ai_score} classification={lead.ai_classification} />
            {lead.ai_classification && <Badge tone={lead.ai_classification}>{lead.ai_classification}</Badge>}
            <Badge tone={lead.status}>{lead.status}</Badge>
            <Badge tone={lead.priority}>{lead.priority}</Badge>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" loading={scoring} onClick={score}>
            Run AI score
          </Button>
          <Button loading={saving} onClick={save}>
            Save changes
          </Button>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <div className="surface-card grid gap-3 p-5 sm:grid-cols-2">
            <Input label="Full name" value={lead.full_name || ''} onChange={(e) => setLead({ ...lead, full_name: e.target.value })} />
            <Input label="Company" value={lead.company || ''} onChange={(e) => setLead({ ...lead, company: e.target.value })} />
            <Input label="Email" value={lead.email || ''} onChange={(e) => setLead({ ...lead, email: e.target.value })} />
            <Input label="Phone" value={lead.phone || ''} onChange={(e) => setLead({ ...lead, phone: e.target.value })} />
            <Input label="Job title" value={lead.job_title || ''} onChange={(e) => setLead({ ...lead, job_title: e.target.value })} />
            <Input label="Industry" value={lead.industry || ''} onChange={(e) => setLead({ ...lead, industry: e.target.value })} />
            <Input label="Company size" value={lead.company_size || ''} onChange={(e) => setLead({ ...lead, company_size: e.target.value })} />
            <Input label="Budget" value={lead.budget || ''} onChange={(e) => setLead({ ...lead, budget: e.target.value })} />
            <Select label="Status" value={lead.status} onChange={(e) => setLead({ ...lead, status: e.target.value })}>
              {LEAD_STATUSES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </Select>
            <Select label="Priority" value={lead.priority} onChange={(e) => setLead({ ...lead, priority: e.target.value })}>
              {PRIORITIES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </Select>
            <Select label="Lead source" value={lead.lead_source || ''} onChange={(e) => setLead({ ...lead, lead_source: e.target.value })}>
              <option value="">—</option>
              {LEAD_SOURCES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </Select>
            <Input label="Next follow-up" type="date" value={lead.next_follow_up_date || ''} onChange={(e) => setLead({ ...lead, next_follow_up_date: e.target.value })} />
            <Input className="sm:col-span-2" label="Website" value={lead.website || ''} onChange={(e) => setLead({ ...lead, website: e.target.value })} />
            <Input className="sm:col-span-2" label="LinkedIn" value={lead.linkedin_url || ''} onChange={(e) => setLead({ ...lead, linkedin_url: e.target.value })} />
            <Textarea className="sm:col-span-2" label="Requirement" value={lead.requirement || ''} onChange={(e) => setLead({ ...lead, requirement: e.target.value })} />
            <Textarea className="sm:col-span-2" label="Notes" value={lead.notes || ''} onChange={(e) => setLead({ ...lead, notes: e.target.value })} />
            <div className="sm:col-span-2">
              <Button variant="outline" onClick={setFollowUp}>
                Schedule follow-up from date
              </Button>
            </div>
          </div>

          <div className="surface-card p-5">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <h3 className="font-display text-lg font-semibold">AI email drafts</h3>
                <p className="text-sm text-ink-500">Personalized from name, company, industry, budget, and requirement</p>
              </div>
              <div className="flex gap-2">
                <Select value={emailType} onChange={(e) => setEmailType(e.target.value)}>
                  {EMAIL_TYPES.map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </Select>
                <Button loading={generating} onClick={generateEmail}>
                  Generate
                </Button>
              </div>
            </div>

            {editingEmail && (
              <div className="mt-4 rounded-xl border border-brand-200 bg-brand-50/40 p-4">
                <p className="section-label text-brand-700">Editing draft</p>
                <Input
                  className="mt-2"
                  label="Subject"
                  value={editingEmail.subject}
                  onChange={(e) => setEditingEmail({ ...editingEmail, subject: e.target.value })}
                />
                <Textarea
                  className="mt-3"
                  label="Body"
                  rows={10}
                  value={editingEmail.body}
                  onChange={(e) => setEditingEmail({ ...editingEmail, body: e.target.value })}
                />
                <div className="mt-3 flex flex-wrap gap-2">
                  <Button onClick={saveEmail}>Save draft</Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      navigator.clipboard.writeText(`${editingEmail.subject}\n\n${editingEmail.body}`);
                      toast('Copied to clipboard');
                    }}
                  >
                    Copy
                  </Button>
                  <Button variant="ghost" onClick={() => setEditingEmail(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            <div className="mt-4 space-y-3">
              {emails.length === 0 && !editingEmail ? (
                <EmptyState
                  icon="mail"
                  title="No drafts yet"
                  description="Generate a personalized first outreach or follow-up email."
                  actionLabel="Generate first outreach"
                  onAction={() => {
                    setEmailType('First Outreach');
                    generateEmail();
                  }}
                />
              ) : (
                emails.map((email) => (
                  <div key={email.id} className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <p className="font-semibold">{email.subject}</p>
                        <p className="text-xs text-ink-500">
                          {email.email_type} · {formatDateTime(email.created_at)}
                        </p>
                      </div>
                      <Badge tone={email.status}>{email.status}</Badge>
                    </div>
                    <pre className="mt-3 whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink-700">{email.body}</pre>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Button size="sm" variant="outline" onClick={() => setEditingEmail(email)}>
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
                          toast('Marked as sent');
                          load();
                        }}
                      >
                        Mark sent
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div
            className={`surface-card p-5 ${
              lead.ai_classification === 'Hot' ? 'ring-1 ring-hot/20' : ''
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <h3 className="font-display text-lg font-semibold">AI qualification</h3>
              {lead.ai_classification && <Badge tone={lead.ai_classification}>{lead.ai_classification}</Badge>}
            </div>
            {q ? (
              <div className="mt-4 space-y-3 text-sm">
                <div className="grid grid-cols-3 gap-2">
                  {[
                    ['Intent', q.buyer_intent],
                    ['Budget', q.budget_fit],
                    ['Urgency', q.urgency_level],
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg bg-slate-50 px-2 py-2 text-center">
                      <p className="text-[10px] font-semibold uppercase tracking-wide text-ink-400">{label}</p>
                      <p className="mt-0.5 font-semibold text-ink-800">{value}</p>
                    </div>
                  ))}
                </div>
                <div className="rounded-xl border border-brand-100 bg-brand-50/50 p-3">
                  <p className="section-label text-brand-700">Suggested next action</p>
                  <p className="mt-1 text-ink-800">{q.suggested_next_action}</p>
                </div>
                <p><span className="font-semibold">Reason:</span> {q.reason}</p>
                <p><span className="font-semibold">Approach:</span> {q.recommended_approach}</p>
                <p><span className="font-semibold">Risks:</span> {q.risk_factors}</p>
                <p><span className="font-semibold">Personalization:</span> {q.personalization_notes}</p>
                {factors && (
                  <div>
                    <p className="section-label mb-2">Score factors</p>
                    <div className="space-y-1.5">
                      {Object.entries(factors).map(([key, val]) => (
                        <div key={key} className="flex items-start justify-between gap-2 rounded-lg bg-slate-50 px-2 py-1.5">
                          <div>
                            <p className="text-xs font-semibold capitalize text-ink-700">{key.replace(/_/g, ' ')}</p>
                            <p className="text-[11px] text-ink-500">{val.reason}</p>
                          </div>
                          <span className="text-xs font-bold text-ink-800">+{val.points}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <EmptyState
                title="Not scored yet"
                description="Run AI score to get classification, risks, and next actions."
                actionLabel="Run AI score"
                onAction={score}
              />
            )}
          </div>
          <div className="surface-card space-y-2 p-5 text-sm">
            <p><span className="font-semibold">Created:</span> {formatDate(lead.created_at)}</p>
            <p><span className="font-semibold">Last contacted:</span> {formatDateTime(lead.last_contacted_at)}</p>
            <p><span className="font-semibold">Next follow-up:</span> {formatDate(lead.next_follow_up_date)}</p>
            <p><span className="font-semibold">Next action:</span> {lead.next_action || '—'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
