// Generates dist/sitemap.xml from the built pages' canonicals.
// Run automatically during `astro build` (integration in astro.config.mjs).
// Rules (kept from the hand-maintained file):
//   - noindex pages (404, admin) are excluded
//   - galerie/<slug> detail pages: changefreq never, priority 0.5
//   - listing/section pages: changefreq monthly, priority 0.7-1.0
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { join, relative } from 'node:path';

const SITE = 'https://michalgazda.github.io/annamatejska.pl/';

function walk(dir, acc = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(p, acc);
    else if (e.name === 'index.html') acc.push(p);
  }
  return acc;
}

function entry(loc, changefreq, priority) {
  return `  <url><loc>${loc}</loc><changefreq>${changefreq}</changefreq><priority>${priority}</priority></url>`;
}

export function generateSitemap({ dist = 'dist' } = {}) {
  const pages = walk(dist);
  const urls = [];
  for (const p of pages) {
    const rel = relative(dist, p).split('\\').join('/');
    const dir = rel.slice(0, -'index.html'.length);
    const html = readFileSync(p, 'utf8');
    if (/name="robots" content="noindex/.test(html)) continue;
    const loc = SITE + dir;
    const isGalleryDetail = /^galerie\/[^/]+\/$/.test(dir);
    const isHome = dir === '';
    urls.push(
      isHome ? entry(loc, 'monthly', '1.0')
      : isGalleryDetail ? entry(loc, 'never', '0.5')
      : entry(loc, 'monthly', '0.7')
    );
  }
  urls.sort((a, b) => a.localeCompare(b));
  const xml =
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls.join('\n') + '\n' +
    '</urlset>\n';
  writeFileSync(join(dist, 'sitemap.xml'), xml);
  return urls.length;
}
