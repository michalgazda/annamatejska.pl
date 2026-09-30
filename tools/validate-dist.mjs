// Validator for dist/ output — run after `npm run build`.
// Usage: node tools/validate-dist.mjs   (exit 1 on any failure)
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, relative, posix } from 'node:path';

const DIST = join(process.cwd(), 'dist');
const errors = [];

function fail(msg) { errors.push(msg); }

// ---- collect all html pages ----
function walk(dir, acc = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walk(p, acc);
    else if (e.name.endsWith('.html')) acc.push(p);
  }
  return acc;
}
const pages = walk(DIST);
if (pages.length === 0) fail('dist/ has no HTML pages');

// ---- collect all files that exist under dist (for link/src resolution) ----
function walkFiles(dir, acc = []) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) walkFiles(p, acc);
    else acc.push(p);
  }
  return acc;
}
const allFiles = walkFiles(DIST);
const distFileSet = new Set(allFiles.map(f => relative(DIST, f).split('\\').join('/')));
// GH Pages directory URLs: /x/y resolves to x/y/index.html.
// Site-absolute URLs carry the base prefix; dist files sit at dist root, so strip it.
const BASE = '/annamatejska.pl/';
function stripBase(clean) {
  if (clean === BASE || clean === BASE.replace(/\/$/, '')) return '';
  if (clean.startsWith(BASE)) return decodeURIComponent(clean.slice(BASE.length - 1)).replace(/^\//, '');
  return decodeURIComponent(clean).replace(/^\//, '');
}
function resolvesToDist(url, pagePath) {
  if (/^(https?:)?\/\//.test(url)) return null; // external
  if (url.startsWith('mailto:') || url.startsWith('tel:') || url.startsWith('data:')) return null;
  let clean = url.split('#')[0].split('?')[0];
  if (clean === '' || clean === '/') return null;
  let rel;
  if (clean.startsWith('/')) rel = stripBase(clean);
  else rel = posix.normalize(posix.join(relative(DIST, pagePath).split('\\').join('/'), '..', clean));
  if (rel === '') return null; // site root
  if (distFileSet.has(rel)) return true;
  if (distFileSet.has(posix.join(rel, 'index.html'))) return true;
  return false; // internal and missing
}

const canonicals = new Set();
const sitemapLocs = new Set();

for (const page of pages) {
  const rel = relative(DIST, page);
  const html = readFileSync(page, 'utf8');

  // exactly one title / description / h1
  const titles = html.match(/<title[^>]*>/g) || [];
  if (titles.length !== 1) fail(`${rel}: expected 1 <title>, found ${titles.length}`);
  const descs = html.match(/<meta name="description"/g) || [];
  if (descs.length !== 1) fail(`${rel}: expected 1 meta description, found ${descs.length}`);
  const h1s = html.match(/<h1[\s>]/g) || [];
  if (h1s.length !== 1) fail(`${rel}: expected 1 <h1>, found ${h1s.length}`);

  // canonical (noindex pages are deliberately excluded from sitemap parity)
  const can = html.match(/<link rel="canonical" href="([^"]+)"/);
  const isNoindex = /name="robots" content="noindex/.test(html);
  if (!can) fail(`${rel}: missing canonical`);
  else if (!isNoindex) canonicals.add(can[1]);

  // no double base prefix
  if (html.includes('annamatejska.pl/annamatejska.pl')) fail(`${rel}: double base prefix`);

  // no unevaluated template braces in href/src attributes
  const attrBrace = html.match(/(?:href|src)="[^"]*\{[^"]*}[^"]*"/);
  if (attrBrace) fail(`${rel}: literal braces in attribute: ${attrBrace[0].slice(0, 90)}`);

  // tel: format
  for (const m of html.matchAll(/href="(tel:[^"]+)"/g)) {
    if (!/^tel:\+48[0-9]{9}$/.test(m[1])) fail(`${rel}: bad tel: URI "${m[1]}" (want tel:+48 + 9 digits)`);
  }

  // internal links/images resolve
  for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const url = m[1];
    if (/^(https?:)?\/\//.test(url)) continue;
    const r = resolvesToDist(url, page);
    if (r === false) fail(`${rel}: broken internal URL "${url}"`);
  }

  // og:image resolves to a real dist file (must carry the base prefix)
  const og = html.match(/<meta property="og:image" content="([^"]+)"/);
  if (og) {
    const u = new URL(og[1]);
    if (!u.pathname.startsWith(BASE)) fail(`${rel}: og:image missing base prefix: ${og[1]}`);
    const relOg = stripBase(decodeURIComponent(u.pathname));
    const f = join(DIST, relOg);
    if (!existsSync(f)) fail(`${rel}: og:image 404s in dist: ${og[1]}`);
  } else {
    fail(`${rel}: missing og:image`);
  }
}

// ---- 404 page exists ----
if (!existsSync(join(DIST, '404.html'))) fail('dist/404.html missing');

// ---- sitemap parity with canonicals ----
const sitemapPath = join(DIST, 'sitemap.xml');
if (!existsSync(sitemapPath)) {
  fail('dist/sitemap.xml missing');
} else {
  const sm = readFileSync(sitemapPath, 'utf8');
  for (const m of sm.matchAll(/<loc>([^<]+)<\/loc>/g)) sitemapLocs.add(m[1]);
  for (const c of canonicals) {
    if (!sitemapLocs.has(c)) fail(`sitemap.xml missing canonical URL: ${c}`);
  }
  for (const l of sitemapLocs) {
    if (!canonicals.has(l)) fail(`sitemap.xml lists non-canonical URL: ${l}`);
  }
}

if (errors.length) {
  console.error(`VALIDATE FAIL — ${errors.length} problem(s):`);
  for (const e of errors) console.error('  ✗ ' + e);
  process.exit(1);
} else {
  console.log(`VALIDATE OK — ${pages.length} pages, ${canonicals.size} canonicals == sitemap, all internal URLs resolve`);
}
