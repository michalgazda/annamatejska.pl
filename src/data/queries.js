import { readFileSync } from 'fs';

export function site() {
  return JSON.parse(readFileSync('src/data/site.json', 'utf-8'));
}

export function services() {
  return JSON.parse(readFileSync('src/data/services.json', 'utf-8')).services;
}

export function testimonials() {
  return JSON.parse(readFileSync('src/data/testimonials.json', 'utf-8')).testimonials;
}

export function galleries() {
  return JSON.parse(readFileSync('src/data/galleries.json', 'utf8')).galleries;
}

// Normalize Decap CMS public_folder paths and legacy relative paths to the
// current Astro base (GH Pages subpath or Docker root).
export function assetPath(path, base = '/') {
  if (!path) return path;
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('data:')) return path;
  const basePrefix = base.replace(/^\/+|\/+$/g, '');
  let clean = path.replace(/^\/+/, '');
  if (basePrefix) {
    while (clean.startsWith(`${basePrefix}/`)) clean = clean.slice(basePrefix.length + 1);
  } else if (clean.startsWith('annamatejska.pl/')) {
    while (clean.startsWith('annamatejska.pl/')) clean = clean.slice('annamatejska.pl/'.length);
  }
  return `${base}${clean}`;
}

export function kadrowania() {
  return JSON.parse(readFileSync('src/data/kadrowania.json', 'utf8'));
}

// Shared Polish long-date formatter (used by galerie listing + detail)
const months = ['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];
export function formatDate(d) {
  const p = d.split('-');
  return `${parseInt(p[2])} ${months[parseInt(p[1])-1]} ${p[0]}`;
}