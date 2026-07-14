import { useState } from 'react';
import api from '../api/client';
import Button from '../components/Button';
import Badge from '../components/Badge';
import { toast } from '../components/ToastProvider';

const SAMPLE = `name,company,email,phone,job_title,industry,company_size,budget,requirement,lead_source,website,linkedin_url,notes
Jordan Blake,Acme Robotics,jordan@acmerobotics.com,+1-555-0100,VP Sales,Manufacturing,51-200,$28000,Need AI qualification for channel partners this quarter,Website Form,https://acmerobotics.com,https://linkedin.com/in/jordanblake,Inbound demo request
Taylor Singh,NovaApps,taylor@novaapps.io,+1-555-0101,Founder,SaaS,11-50,$15000,Score product-led growth inbound quickly,LinkedIn,https://novaapps.io,,Warm reply on LinkedIn`;

export default function ImportLeads() {
  const [file, setFile] = useState(null);
  const [runAi, setRunAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);

  const onUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      toast('Choose a CSV file first', 'error');
      return;
    }
    setLoading(true);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await api.post(`/api/leads/import-csv?run_ai=${runAi}`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setSummary(res.data);
      toast(`Imported ${res.data.successful} leads`);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const downloadSample = () => {
    const blob = new Blob([SAMPLE], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_leads.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h2 className="font-display text-2xl font-semibold">CSV import</h2>
        <p className="text-sm text-ink-500">
          Upload campaign or CRM exports. We save leads and optionally run AI qualification on each row.
        </p>
      </div>

      <form onSubmit={onUpload} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
        <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center hover:border-brand-400">
          <p className="font-semibold text-ink-800">{file ? file.name : 'Drop or choose a .csv file'}</p>
          <p className="mt-1 text-xs text-ink-500">
            Columns: name, company, email, phone, job_title, industry, company_size, budget, requirement,
            lead_source, website, linkedin_url, notes
          </p>
          <input
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>

        <label className="mt-4 flex items-center gap-2 text-sm text-ink-700">
          <input type="checkbox" checked={runAi} onChange={(e) => setRunAi(e.target.checked)} />
          Run AI qualification after import
        </label>

        <div className="mt-5 flex flex-wrap gap-2">
          <Button type="submit" loading={loading}>
            Upload & import
          </Button>
          <Button type="button" variant="outline" onClick={downloadSample}>
            Download sample CSV
          </Button>
        </div>
      </form>

      {summary && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h3 className="font-display text-lg font-semibold">Import summary</h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-4">
            <div className="rounded-xl bg-slate-50 p-3">
              <p className="text-xs text-ink-500">Total rows</p>
              <p className="text-2xl font-bold">{summary.total_rows}</p>
            </div>
            <div className="rounded-xl bg-brand-50 p-3">
              <p className="text-xs text-ink-500">Successful</p>
              <p className="text-2xl font-bold text-brand-700">{summary.successful}</p>
            </div>
            <div className="rounded-xl bg-red-50 p-3">
              <p className="text-xs text-ink-500">Failed</p>
              <p className="text-2xl font-bold text-red-700">{summary.failed}</p>
            </div>
            <div className="rounded-xl bg-amber-50 p-3">
              <p className="text-xs text-ink-500">Duplicates</p>
              <p className="text-2xl font-bold text-amber-700">{summary.duplicates}</p>
            </div>
          </div>
          {summary.errors?.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-sm font-semibold">Row issues</p>
              {summary.errors.slice(0, 10).map((err, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  <Badge>Row {err.row}</Badge>
                  <span className="text-ink-600">{err.error}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
