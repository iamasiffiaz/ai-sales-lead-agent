import { Link } from 'react-router-dom';
import Button from '../components/Button';
import { BRAND } from '../utils/constants';

const features = [
  {
    title: 'AI lead scoring',
    body: 'Hybrid rules + AI reasoning scores every prospect 1–100 with Hot / Warm / Cold classification.',
  },
  {
    title: 'Personalized outreach',
    body: 'Generate first-touch, follow-up, proposal, re-engagement, and meeting emails in one click.',
  },
  {
    title: 'CRM pipeline',
    body: 'Kanban stages from New to Won keep ownership clear while AI suggests next actions.',
  },
  {
    title: 'CSV import & analytics',
    body: 'Import campaign lists, auto-qualify rows, and track source, industry, and conversion trends.',
  },
];

const useCases = [
  { title: 'Startups', body: 'Qualify inbound demos fast without hiring a full SDR pod on day one.' },
  { title: 'Agencies', body: 'Run multi-client pipelines with consistent scoring and follow-up cadence.' },
  { title: 'Sales teams', body: 'Focus calendar time on Hot leads and automate the rest of the book.' },
  { title: 'B2B companies', body: 'Turn form fills, webinars, and LinkedIn replies into prioritized opportunities.' },
];

const plans = [
  {
    name: 'Starter',
    price: '$49',
    desc: 'Solo founders & early GTM',
    items: ['Up to 500 leads', 'AI scoring', 'Email drafts', 'CSV import'],
  },
  {
    name: 'Growth',
    price: '$149',
    desc: 'Sales teams scaling inbound',
    items: ['Unlimited scoring', 'Pipeline board', 'Follow-up reminders', 'Analytics'],
    featured: true,
  },
  {
    name: 'Operator',
    price: '$399',
    desc: 'Agencies & multi-brand ops',
    items: ['Multi-ICP settings', 'Bulk qualify', 'Priority support', 'API access'],
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 text-ink-900">
      <header className="absolute inset-x-0 top-0 z-20">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
          <p className="font-display text-xl font-bold text-white">{BRAND.name}</p>
          <div className="flex items-center gap-3">
            <a href="#features" className="hidden text-sm text-white/80 hover:text-white sm:inline">
              Features
            </a>
            <a href="#pricing" className="hidden text-sm text-white/80 hover:text-white sm:inline">
              Pricing
            </a>
            <Link to="/app">
              <Button size="sm" variant="accent">
                Open dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="relative min-h-[100svh] overflow-hidden bg-hero-grid text-white">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          }}
        />
        <div className="relative mx-auto flex min-h-[100svh] max-w-6xl flex-col justify-end px-5 pb-16 pt-28 sm:justify-center sm:pb-24">
          <p className="font-display text-5xl font-bold leading-[1.05] tracking-tight text-white sm:text-7xl md:text-8xl">
            {BRAND.name}
          </p>
          <h1 className="mt-5 max-w-2xl text-xl font-medium text-emerald-50/95 sm:text-2xl">
            Score the right leads. Draft the right email. Move the pipeline faster.
          </h1>
          <p className="mt-4 max-w-xl text-sm text-slate-300 sm:text-base">
            An AI sales assistant for startups and B2B teams — qualify opportunities, prioritize Hot
            prospects, and keep follow-ups from slipping.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/app">
              <Button size="lg">Launch live demo</Button>
            </Link>
            <a href="#value">
              <Button size="lg" variant="outline" className="border-white/30 bg-white/10 text-white hover:bg-white/20">
                See how it works
              </Button>
            </a>
          </div>
        </div>
        <div className="pointer-events-none absolute -right-10 bottom-10 hidden h-72 w-72 rounded-full bg-brand-500/20 blur-3xl md:block" />
        <div className="pointer-events-none absolute left-1/3 top-24 hidden h-40 w-40 rounded-full bg-accent-400/20 blur-3xl md:block" />
      </section>

      <section id="value" className="mx-auto max-w-6xl px-5 py-20">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-brand-700">Business value</p>
        <h2 className="mt-3 max-w-3xl font-display text-3xl font-semibold text-ink-900 sm:text-4xl">
          Stop wasting hours on leads that will not buy.
        </h2>
        <p className="mt-4 max-w-3xl text-ink-600">
          AI Sales & Lead Qualification Agent helps startups and sales teams prioritize the right leads,
          reduce manual qualification work, generate personalized outreach, and manage follow-ups from one
          dashboard. It improves sales productivity by helping teams focus on high-intent prospects and move
          faster through the pipeline.
        </p>
      </section>

      <section id="features" className="border-y border-slate-200 bg-white py-20">
        <div className="mx-auto max-w-6xl px-5">
          <h2 className="font-display text-3xl font-semibold">Built for modern GTM teams</h2>
          <p className="mt-2 max-w-2xl text-ink-600">
            From scoring to outreach to pipeline — one operating system for qualification work.
          </p>
          <div className="mt-10 grid gap-8 md:grid-cols-2">
            {features.map((f, i) => (
              <div
                key={f.title}
                className="group border-l-2 border-brand-500 pl-5 transition hover:border-accent-500"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <h3 className="font-display text-xl font-semibold text-ink-900">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-600">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-20">
        <h2 className="font-display text-3xl font-semibold">Who it is for</h2>
        <p className="mt-2 text-ink-600">One workflow that adapts across GTM motions.</p>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {useCases.map((u) => (
            <div key={u.title} className="rounded-2xl bg-ink-950 p-5 text-white">
              <h3 className="font-display text-lg font-semibold text-emerald-300">{u.title}</h3>
              <p className="mt-2 text-sm text-slate-300">{u.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="pricing" className="bg-gradient-to-b from-slate-100 to-slate-50 py-20">
        <div className="mx-auto max-w-6xl px-5">
          <h2 className="font-display text-3xl font-semibold">Simple pricing</h2>
          <p className="mt-2 text-ink-600">Portfolio demo pricing — production ready architecture.</p>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl border p-6 ${
                  plan.featured
                    ? 'border-brand-600 bg-ink-950 text-white shadow-soft'
                    : 'border-slate-200 bg-white'
                }`}
              >
                <p className="text-sm font-semibold uppercase tracking-wide opacity-70">{plan.name}</p>
                <p className="mt-2 font-display text-4xl font-bold">
                  {plan.price}
                  <span className="text-base font-medium opacity-70">/mo</span>
                </p>
                <p className={`mt-1 text-sm ${plan.featured ? 'text-slate-300' : 'text-ink-500'}`}>{plan.desc}</p>
                <ul className="mt-5 space-y-2 text-sm">
                  {plan.items.map((item) => (
                    <li key={item} className="flex gap-2">
                      <span className={plan.featured ? 'text-brand-400' : 'text-brand-600'}>✓</span>
                      {item}
                    </li>
                  ))}
                </ul>
                <Link to="/app" className="mt-6 block">
                  <Button className="w-full" variant={plan.featured ? 'primary' : 'outline'}>
                    Start free demo
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-20">
        <div className="overflow-hidden rounded-3xl bg-hero-grid px-8 py-12 text-white">
          <h2 className="font-display text-3xl font-semibold sm:text-4xl">Ready to qualify smarter?</h2>
          <p className="mt-3 max-w-xl text-slate-300">
            Open the live dashboard with seeded Hot, Warm, and Cold leads — score, draft emails, and move
            deals across the pipeline.
          </p>
          <Link to="/app" className="mt-6 inline-block">
            <Button size="lg" variant="accent">
              Enter QualifyAI
            </Button>
          </Link>
        </div>
      </section>

      <footer className="border-t border-slate-200 py-8 text-center text-xs text-ink-500">
        Portfolio-ready AI sales OS · FastAPI · React · LLM APIs
      </footer>
    </div>
  );
}
