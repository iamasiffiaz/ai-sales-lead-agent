const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = path.resolve(__dirname, '../../docs/screenshots');
fs.mkdirSync(OUT, { recursive: true });

const BASE = process.env.APP_URL || 'http://127.0.0.1:5174';

const shots = [
  { name: 'landing.png', url: `${BASE}/`, full: true },
  { name: 'dashboard.png', url: `${BASE}/app`, full: false },
  { name: 'leads.png', url: `${BASE}/app/leads`, full: false },
  { name: 'pipeline.png', url: `${BASE}/app/pipeline`, full: false },
  { name: 'analytics.png', url: `${BASE}/app/analytics`, full: false },
  { name: 'recommendations.png', url: `${BASE}/app/recommendations`, full: false },
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  for (const shot of shots) {
    await page.goto(shot.url, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(1500);
    const file = path.join(OUT, shot.name);
    await page.screenshot({ path: file, fullPage: shot.full });
    console.log('saved', shot.name);
  }

  await page.goto(`${BASE}/app/leads`, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1000);
  const link = page.locator('a[href^="/app/leads/"]').first();
  if (await link.count()) {
    await link.click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(OUT, 'lead-details.png'), fullPage: false });
    console.log('saved lead-details.png');
  } else {
    console.log('skip lead-details — no lead links found');
  }

  await browser.close();
  console.log('done');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
