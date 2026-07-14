export const LEAD_STATUSES = [
  'New',
  'Contacted',
  'Qualified',
  'Proposal Sent',
  'Won',
  'Lost',
];

export const CLASSIFICATIONS = ['Hot', 'Warm', 'Cold'];
export const PRIORITIES = ['Low', 'Medium', 'High'];

export const EMAIL_TYPES = [
  'First Outreach',
  'Follow-up',
  'Proposal Follow-up',
  'Re-engagement',
  'Meeting Request',
];

export const LEAD_SOURCES = [
  'Inbound Demo',
  'Website Form',
  'LinkedIn',
  'Referral',
  'Cold Email',
  'Outbound',
  'Webinar',
  'Ads',
  'Event',
  'Partner',
  'Content Download',
];

export const NAV_ITEMS = [
  { to: '/app', label: 'Dashboard', end: true },
  { to: '/app/leads', label: 'Leads' },
  { to: '/app/pipeline', label: 'Pipeline' },
  { to: '/app/emails', label: 'Emails' },
  { to: '/app/follow-ups', label: 'Follow-ups' },
  { to: '/app/import', label: 'Import CSV' },
  { to: '/app/analytics', label: 'Analytics' },
  { to: '/app/recommendations', label: 'AI Insights' },
  { to: '/app/settings', label: 'Settings' },
];

export const BRAND = {
  name: 'QualifyAI',
  tagline: 'AI Sales & Lead Qualification Agent',
};
