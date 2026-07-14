import { useEffect, useState } from 'react';
import api from '../api/client';
import Button from '../components/Button';
import Input from '../components/Input';
import Textarea from '../components/Textarea';
import LoadingSpinner from '../components/LoadingSpinner';
import { toast } from '../components/ToastProvider';

export default function Settings() {
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .get('/api/settings')
      .then((res) => setForm(res.data))
      .catch((err) => toast(err.message, 'error'))
      .finally(() => setLoading(false));
  }, []);

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.put('/api/settings', {
        business_name: form.business_name,
        target_industry: form.target_industry,
        ideal_customer_profile: form.ideal_customer_profile,
        minimum_budget_preference: form.minimum_budget_preference,
        default_follow_up_interval_days: Number(form.default_follow_up_interval_days),
        ai_provider: form.ai_provider,
        api_key_placeholder: form.api_key_placeholder,
        email_signature: form.email_signature,
      });
      setForm(res.data);
      toast('Settings saved');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !form) return <LoadingSpinner />;

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      <div>
        <h2 className="font-display text-2xl font-semibold">Settings</h2>
        <p className="text-sm text-ink-500">Tune ICP, AI provider placeholders, and email defaults.</p>
      </div>

      <form onSubmit={save} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
        <Input
          label="Business name"
          value={form.business_name}
          onChange={(e) => setForm({ ...form, business_name: e.target.value })}
        />
        <Input
          label="Target industry"
          value={form.target_industry}
          onChange={(e) => setForm({ ...form, target_industry: e.target.value })}
        />
        <Textarea
          label="Ideal customer profile"
          rows={4}
          value={form.ideal_customer_profile}
          onChange={(e) => setForm({ ...form, ideal_customer_profile: e.target.value })}
        />
        <Input
          label="Minimum budget preference"
          value={form.minimum_budget_preference}
          onChange={(e) => setForm({ ...form, minimum_budget_preference: e.target.value })}
        />
        <Input
          label="Default follow-up interval (days)"
          type="number"
          min="1"
          value={form.default_follow_up_interval_days}
          onChange={(e) => setForm({ ...form, default_follow_up_interval_days: e.target.value })}
        />
        <Input
          label="AI provider"
          value={form.ai_provider}
          onChange={(e) => setForm({ ...form, ai_provider: e.target.value })}
        />
        <Input
          label="API key placeholder"
          type="password"
          placeholder="Stored for UI only — use OPENAI_API_KEY in backend env"
          value={form.api_key_placeholder || ''}
          onChange={(e) => setForm({ ...form, api_key_placeholder: e.target.value })}
        />
        <Textarea
          label="Email signature"
          rows={4}
          value={form.email_signature}
          onChange={(e) => setForm({ ...form, email_signature: e.target.value })}
        />
        <div className="flex justify-end">
          <Button type="submit" loading={saving}>
            Save settings
          </Button>
        </div>
      </form>

      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-ink-600">
        <p className="font-semibold text-ink-800">JWT-ready auth</p>
        <p className="mt-1">
          Demo user seeded as <code>demo@qualifyai.dev</code> / <code>demo1234</code>. Auth routes live at{' '}
          <code>/api/auth/register</code> and <code>/api/auth/login</code> for production wiring.
        </p>
      </div>
    </div>
  );
}
