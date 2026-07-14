import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import Button from '../components/Button';
import Input from '../components/Input';
import Select from '../components/Select';
import Textarea from '../components/Textarea';
import Badge, { ScorePill } from '../components/Badge';
import Table from '../components/Table';
import Modal from '../components/Modal';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { toast } from '../components/ToastProvider';
import { CLASSIFICATIONS, LEAD_SOURCES, LEAD_STATUSES, PRIORITIES } from '../utils/constants';
import { formatDate } from '../utils/formatDate';

const emptyForm = {
  full_name: '',
  company: '',
  email: '',
  phone: '',
  job_title: '',
  industry: '',
  company_size: '',
  budget: '',
  requirement: '',
  lead_source: 'Website Form',
  website: '',
  linkedin_url: '',
  notes: '',
  status: 'New',
  priority: 'Medium',
};

export default function Leads() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    q: '',
    status: '',
    classification: '',
    lead_source: '',
    industry: '',
    sort_by: 'ai_score',
    sort_dir: 'desc',
  });
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [bulkLoading, setBulkLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '' && v != null)
      );
      const res = await api.get('/api/leads', { params: { ...params, page_size: 100 } });
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const created = await api.post('/api/leads', form);
      await api.post(`/api/qualification/score/${created.data.id}`);
      toast('Lead created and scored');
      setOpen(false);
      setForm(emptyForm);
      load();
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (id) => {
    if (!window.confirm('Delete this lead permanently?')) return;
    try {
      await api.delete(`/api/leads/${id}`);
      toast('Lead deleted');
      load();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const bulkScore = async () => {
    setBulkLoading(true);
    try {
      const res = await api.post('/api/qualification/bulk-score');
      toast(`Scored ${res.data.scored} leads`);
      load();
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setBulkLoading(false);
    }
  };

  const exportCsv = () => {
    window.open(`${api.defaults.baseURL}/api/leads/export-csv`, '_blank');
  };

  const columns = [
    {
      key: 'full_name',
      label: 'Lead',
      render: (row) => (
        <div>
          <Link to={`/app/leads/${row.id}`} className="font-semibold text-brand-700 hover:underline">
            {row.full_name}
          </Link>
          <p className="text-xs text-ink-500">{row.company}</p>
        </div>
      ),
    },
    { key: 'email', label: 'Email' },
    { key: 'industry', label: 'Industry', render: (r) => r.industry || '—' },
    { key: 'lead_source', label: 'Source', render: (r) => r.lead_source || '—' },
    {
      key: 'ai_score',
      label: 'Score',
      render: (r) => <ScorePill score={r.ai_score} classification={r.ai_classification} />,
    },
    {
      key: 'ai_classification',
      label: 'Class',
      render: (r) => (r.ai_classification ? <Badge tone={r.ai_classification}>{r.ai_classification}</Badge> : '—'),
    },
    {
      key: 'status',
      label: 'Status',
      render: (r) => <Badge>{r.status}</Badge>,
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (r) => formatDate(r.created_at),
    },
    {
      key: 'actions',
      label: '',
      render: (r) => (
        <div className="flex gap-2">
          <Link to={`/app/leads/${r.id}`}>
            <Button size="sm" variant="outline">
              Open
            </Button>
          </Link>
          <Button size="sm" variant="ghost" onClick={() => onDelete(r.id)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold">Lead management</h2>
          <p className="text-sm text-ink-500">{total} leads in CRM</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={exportCsv}>
            Export CSV
          </Button>
          <Button variant="secondary" loading={bulkLoading} onClick={bulkScore}>
            Bulk AI score
          </Button>
          <Button onClick={() => setOpen(true)}>New lead</Button>
        </div>
      </div>

      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-card md:grid-cols-3 xl:grid-cols-7">
        <Input
          label="Search"
          placeholder="Name, company, email..."
          value={filters.q}
          onChange={(e) => setFilters({ ...filters, q: e.target.value })}
        />
        <Select label="Status" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All</option>
          {LEAD_STATUSES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </Select>
        <Select
          label="Classification"
          value={filters.classification}
          onChange={(e) => setFilters({ ...filters, classification: e.target.value })}
        >
          <option value="">All</option>
          {CLASSIFICATIONS.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </Select>
        <Select
          label="Source"
          value={filters.lead_source}
          onChange={(e) => setFilters({ ...filters, lead_source: e.target.value })}
        >
          <option value="">All</option>
          {LEAD_SOURCES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </Select>
        <Input
          label="Industry"
          placeholder="e.g. SaaS"
          value={filters.industry}
          onChange={(e) => setFilters({ ...filters, industry: e.target.value })}
        />
        <Select
          label="Sort by"
          value={`${filters.sort_by}:${filters.sort_dir}`}
          onChange={(e) => {
            const [sort_by, sort_dir] = e.target.value.split(':');
            setFilters({ ...filters, sort_by, sort_dir });
          }}
        >
          <option value="ai_score:desc">Score · high → low</option>
          <option value="ai_score:asc">Score · low → high</option>
          <option value="created_at:desc">Newest first</option>
          <option value="created_at:asc">Oldest first</option>
          <option value="full_name:asc">Name A–Z</option>
          <option value="company:asc">Company A–Z</option>
        </Select>
        <div className="flex items-end">
          <Button className="w-full" variant="outline" onClick={load}>
            Apply filters
          </Button>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-2 shadow-soft">
        {loading ? (
          <LoadingSpinner />
        ) : items.length === 0 ? (
          <EmptyState title="No leads found" description="Create a lead or import a CSV to get started." actionLabel="New lead" onAction={() => setOpen(true)} />
        ) : (
          <Table columns={columns} rows={items} />
        )}
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title="Create lead" wide>
        <form className="grid gap-3 sm:grid-cols-2" onSubmit={onCreate}>
          <Input label="Full name" required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <Input label="Company" required value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
          <Input label="Email" required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Input label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          <Input label="Job title" value={form.job_title} onChange={(e) => setForm({ ...form, job_title: e.target.value })} />
          <Input label="Industry" value={form.industry} onChange={(e) => setForm({ ...form, industry: e.target.value })} />
          <Input label="Company size" value={form.company_size} onChange={(e) => setForm({ ...form, company_size: e.target.value })} />
          <Input label="Budget" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} />
          <Select label="Lead source" value={form.lead_source} onChange={(e) => setForm({ ...form, lead_source: e.target.value })}>
            {LEAD_SOURCES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </Select>
          <Select label="Status" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            {LEAD_STATUSES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </Select>
          <Select label="Priority" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
            {PRIORITIES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </Select>
          <Input label="Website" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} />
          <Input className="sm:col-span-2" label="LinkedIn URL" value={form.linkedin_url} onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })} />
          <Textarea className="sm:col-span-2" label="Requirement" value={form.requirement} onChange={(e) => setForm({ ...form, requirement: e.target.value })} />
          <Textarea className="sm:col-span-2" label="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <div className="sm:col-span-2 flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={saving}>
              Create & score
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
