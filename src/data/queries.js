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

// Homepage „O mnie” block (editable in Decap → „Strona główna”)
export function home() {
  return JSON.parse(readFileSync('src/data/home.json', 'utf8'));
}

// Cennik / pakiety (editable in Decap → „Oferta i cennik”)
export function oferta() {
  return JSON.parse(readFileSync('src/data/oferta.json', 'utf8'));
}

// Podstrona /o-mnie (editable in Decap → „Strona O mnie”)
export function aboutPage() {
  return JSON.parse(readFileSync('src/data/o-mnie.json', 'utf8'));
}

// Wybrane zdjęcia (curated portfolio) — editable in Decap → „Portfolio”
export function portfolio() {
  return JSON.parse(readFileSync('src/data/portfolio.json', 'utf8')).items;
}

// Podstrona /reportaze (editable in Decap → „Reportaże”)
export function reportaze() {
  return JSON.parse(readFileSync('src/data/reportaze.json', 'utf8'));
}

// Podstrony oferty — edytowalne w Decap → „Oferta — podstrony”
export function albumy() {
  return JSON.parse(readFileSync('src/data/albumy.json', 'utf8'));
}

export function studio() {
  return JSON.parse(readFileSync('src/data/studio.json', 'utf8'));
}

export function vouchery() {
  return JSON.parse(readFileSync('src/data/vouchery.json', 'utf8'));
}

export function krokPoKroku() {
  return JSON.parse(readFileSync('src/data/krok-po-kroku.json', 'utf8'));
}

export function ofertaNgo() {
  return JSON.parse(readFileSync('src/data/oferta-ngo.json', 'utf8'));
}

export function regulamin() {
  return JSON.parse(readFileSync('src/data/regulamin.json', 'utf8'));
}

// Shared Polish long-date formatter (used by galerie listing + detail)
const months = ['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];
export function formatDate(d) {
  const p = d.split('-');
  return `${parseInt(p[2])} ${months[parseInt(p[1])-1]} ${p[0]}`;
}