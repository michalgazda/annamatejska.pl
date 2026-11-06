#!/usr/bin/env node
/**
 * gallery-sync — pobiera zdjęcia z folderu Google Drive („wrzutnia” Anny),
 * sprawdza je (rozmiar / rozdzielczość / format), optymalizuje pod stronę
 * i podpina do repo: public/images/galleries/<slug>/ + src/data/galleries.json.
 *
 * Użycie:
 *   node tools/gallery-sync.mjs                 # pełny przebieg (Drive)
 *   node tools/gallery-sync.mjs --dry-run       # pokaż co by zrobił, nic nie zapisuj
 *   node tools/gallery-sync.mjs --local-dir X   # tryb testowy: lokalny katalog zamiast Drive
 *   node tools/gallery-sync.mjs --allow-small   # przyjmij zdjęcia poniżej minLongEdge
 *   node tools/gallery-sync.mjs --folder ID     # inny folder Drive niż w configu
 *
 * Struktura wrzutni:
 *   <folder Drive>/
 *     Nazwa sesji/            <- jeden podfolder = jedna galeria
 *       01.jpg, 02.jpg ...
 *     inne-luźne-zdjecia.jpg  <- lądują w galerii rootGallerySlug (jeśli ustawione)
 *
 * Reguły (config: tools/gallery-sync.config.json):
 *   - JPG/PNG/WEBP/TIFF, długi bok >= 1600 px, plik <= 60 MB
 *   - wynik: pełne zdjęcie 2400 px / q82, miniatura 900 px / q78, bez EXIF (GPS!)
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, statSync } from 'node:fs';
import { rename, rm } from 'node:fs/promises';
import { join, dirname, basename, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import os from 'node:os';
import { createHash } from 'node:crypto';
import sharp from 'sharp';

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const CFG_PATH = join(REPO, 'tools/gallery-sync.config.json');
const GALLERIES_JSON = join(REPO, 'src/data/galleries.json');
const OUT_DIR = join(REPO, 'public/images/galleries');
const TOKEN_FILE = process.env.GDRIVE_TOKEN_FILE || join(os.homedir(), '.hermes/google_token.json');

// Sekrety/identyfikatory spoza repo: tools/gallery-sync.local.json jest w .gitignore
// (id folderu Drive, ewentualne nadpisania limitów), albo zmienna GDRIVE_FOLDER_ID.
const LOCAL_CFG_PATH = join(REPO, 'tools/gallery-sync.local.json');
const CFG = {
  ...JSON.parse(readFileSync(CFG_PATH, 'utf8')),
  ...(existsSync(LOCAL_CFG_PATH) ? JSON.parse(readFileSync(LOCAL_CFG_PATH, 'utf8')) : {}),
};
const args = process.argv.slice(2);
const flag = (n) => args.includes(n);
const opt = (n, d = null) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] ? args[i + 1] : d; };
const DRY = flag('--dry-run');
const ALLOW_SMALL = flag('--allow-small');
const LOCAL_DIR = opt('--local-dir');

const IMAGE_EXT = new Set(['.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.avif']);
const IMAGE_MIME = /^image\/(jpe?g|png|webp|tiff?|avif)$/i;

/* ---------- nazwy / slugi ---------- */
const TRANSLIT = { ą: 'a', ć: 'c', ę: 'e', ł: 'l', ń: 'n', ó: 'o', ś: 's', ź: 'z', ż: 'z', ß: 'ss', ä: 'a', ö: 'o', ü: 'u', é: 'e', á: 'a', í: 'i', ú: 'u', å: 'a', ø: 'o', æ: 'ae' };
export function slugify(input) {
  return String(input)
    .toLowerCase()
    .replace(/[ąćęłńóśźżßäöüéáíúåøæ]/g, (c) => TRANSLIT[c] ?? c)
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60)
    .replace(/-+$/g, '');
}

/** Naturalne sortowanie: IMG_2 przed IMG_10; polskie znaki bez znaczenia. */
export function naturalCompare(a, b) {
  const chunk = (s) => String(s).match(/(\d+|\D+)/g) ?? [];
  const A = chunk(a), B = chunk(b);
  for (let i = 0; i < Math.min(A.length, B.length); i++) {
    const x = A[i], y = B[i];
    const nx = /^\d+$/.test(x), ny = /^\d+$/.test(y);
    if (nx && ny) { if (+x !== +y) return +x - +y; }
    else { const c = x.localeCompare(y, 'pl', { sensitivity: 'base' }); if (c) return c; }
  }
  return A.length - B.length;
}

/* ---------- Google Drive ---------- */
async function accessToken() {
  const t = JSON.parse(readFileSync(TOKEN_FILE, 'utf8'));
  if (t.token && t.expiry && new Date(t.expiry).getTime() - Date.now() > 120000) return t.token;
  const res = await fetch(t.token_uri || 'https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: t.client_id, client_secret: t.client_secret,
      refresh_token: t.refresh_token, grant_type: 'refresh_token',
    }),
  });
  const j = await res.json();
  if (!res.ok) throw new Error(`Odświeżenie tokenu Google nie wyszło (${res.status}): ${j.error_description || j.error}. Uruchom ponownie autoryzację: setup.py --auth-url`);
  t.token = j.access_token;
  t.expiry = new Date(Date.now() + (j.expires_in ?? 3600) * 1000).toISOString();
  if (!DRY) writeFileSync(TOKEN_FILE, JSON.stringify(t));
  return t.token;
}

async function driveList(token, folderId) {
  const files = [];
  let pageToken = '';
  const fields = 'nextPageToken,files(id,name,mimeType,size,md5Checksum,createdTime,imageMediaMetadata(width,height))';
  do {
    const q = new URLSearchParams({
      q: `'${folderId}' in parents and trashed = false`,
      fields, pageSize: '1000', orderBy: 'name_natural',
      supportsAllDrives: 'true', includeItemsFromAllDrives: 'true',
      ...(pageToken ? { pageToken } : {}),
    });
    const res = await fetch(`https://www.googleapis.com/drive/v3/files?${q}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const j = await res.json();
    if (!res.ok) throw new Error(`Drive list ${res.status}: ${j.error?.message || JSON.stringify(j)}`);
    files.push(...(j.files ?? []));
    pageToken = j.nextPageToken ?? '';
  } while (pageToken);
  return files;
}

async function driveDownload(token, fileId, dest) {
  const res = await fetch(`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media&supportsAllDrives=true`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`Drive download ${res.status} (${fileId})`);
  writeFileSync(dest, Buffer.from(await res.arrayBuffer()));
  return dest;
}

/** Tryb testowy: udaje strukturę Drive z lokalnego katalogu. */
function localList(dir) {
  return readdirSync(dir).map((name) => {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) return { id: `local:${full}`, name, mimeType: 'application/vnd.google-apps.folder', isDir: true, localPath: full };
    return {
      id: `local:${full}`, name, isDir: false, localPath: full,
      size: String(st.size), mimeType: mimeFromExt(extname(name)),
    };
  });
}

function mimeFromExt(ext) {
  const e = ext.toLowerCase();
  return { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.tif': 'image/tiff', '.tiff': 'image/tiff', '.avif': 'image/avif' }[e] || 'application/octet-stream';
}

function parseMeta(text, where) {
  try { return JSON.parse(text); }
  catch (e) { throw new Error(`Plik _meta.json w "${where}" nie jest poprawnym JSON-em: ${e.message}`); }
}

/* ---------- stan (idempotencja) ---------- */
function loadState() {
  const p = join(REPO, CFG.stateFile);
  return existsSync(p) ? JSON.parse(readFileSync(p, 'utf8')) : { files: {} };
}
function saveState(state) {
  if (DRY) return;
  writeFileSync(join(REPO, CFG.stateFile), JSON.stringify(state, null, 2) + '\n');
}

/* ---------- przetwarzanie zdjęcia ---------- */
function rotatedDims(meta) {
  const swap = typeof meta.orientation === 'number' && meta.orientation >= 5;
  const w = swap ? meta.height : meta.width;
  const h = swap ? meta.width : meta.height;
  return { width: w, height: h, longEdge: Math.max(w, h), shortEdge: Math.min(w, h) };
}

async function writeJpeg(pipeline, outPath, maxEdge, quality) {
  const tmp = `${outPath}.part`;
  await pipeline
    .rotate()
    .resize({ width: maxEdge, height: maxEdge, fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality, progressive: true, mozjpeg: true })
    .toFile(tmp);
  await rename(tmp, outPath);
}

function nextIndex(dir) {
  if (!existsSync(dir)) return 1;
  const used = readdirSync(dir)
    .map((n) => /^(\d+)\.jpg$/i.exec(n))
    .filter(Boolean)
    .map((m) => parseInt(m[1], 10));
  return used.length ? Math.max(...used) + 1 : 1;
}

/**
 * Sprawdza i przetwarza jedno zdjęcie. Zwraca {status:'ok'|'skip'|'reject', ...}.
 */
async function processFile(item, bucket, cfg, ctx) {
  const where = `${bucket.title}/${item.name}`;
  const bytes = Number(item.size || 0);
  if (bytes && bytes > cfg.rejectOverMB * 1024 * 1024) {
    return { status: 'reject', file: item.name, reason: `plik ma ${(bytes / 1048576).toFixed(1)} MB — limit to ${cfg.rejectOverMB} MB (wyeksportuj JPG z Lightrooma w jakości 80–90, nie wrzucaj RAW/TIFF)` };
  }

  const cached = ctx.state.files[item.id];
  if (cached && cached.md5 && item.md5Checksum && cached.md5 === item.md5Checksum && existsSync(join(REPO, 'public', cached.file))) {
    return { status: 'skip', file: item.name, reason: 'już wgrany wcześniej' };
  }

  const tmp = join(ctx.tmpdir, `gs-${process.pid}-${ctx.seq++}${extname(item.name) || '.jpg'}`);
  if (item.localPath) writeFileSync(tmp, readFileSync(item.localPath));
  else await driveDownload(ctx.token, item.id, tmp);

  // Tożsamość pliku: md5 z Drive albo liczone lokalnie (tryb --local-dir).
  const md5 = item.md5Checksum || createHash('md5').update(readFileSync(tmp)).digest('hex');
  if (cached && cached.md5 === md5 && existsSync(join(REPO, 'public', cached.file))) {
    await rm(tmp, { force: true });
    return { status: 'skip', file: item.name, reason: 'już wgrany wcześniej (ten sam plik)' };
  }

  try {
    const probe = sharp(tmp, { failOn: 'none' });
    let meta;
    try { meta = await probe.metadata(); }
    catch { return { status: 'reject', file: item.name, reason: 'nie umiem odczytać tego pliku (uszkodzony albo nieobsługiwany format — np. HEIC z iPhone’a; wyeksportuj JPG)' }; }

    const dims = rotatedDims(meta);
    if (!dims.width || !dims.height) {
      return { status: 'reject', file: item.name, reason: 'brak informacji o wymiarach — wyeksportuj JPG' };
    }
    if (dims.longEdge < cfg.minLongEdge && !ALLOW_SMALL) {
      return { status: 'reject', file: item.name, reason: `rozdzielczość ${dims.width}×${dims.height} px — minimum to ${cfg.minLongEdge} px na dłuższym boku (na stronie byłoby rozmyte)` };
    }

    const dir = join(OUT_DIR, bucket.slug);
    if (!DRY) mkdirSync(dir, { recursive: true });
    const idx = bucket.nextIndex++;
    const num = String(idx).padStart(2, '0');
    const fullPath = join(dir, `${num}.jpg`);
    const thumbPath = join(dir, `${num}-thumb.jpg`);

    if (!DRY) {
      // bez .withMetadata() — sharp domyślnie usuwa EXIF (m.in. GPS sesji), a .rotate() wpieka orientację
      await writeJpeg(sharp(tmp, { failOn: 'none' }), fullPath, cfg.fullMax, cfg.quality);
      await writeJpeg(sharp(tmp, { failOn: 'none' }), thumbPath, cfg.thumbMax, cfg.thumbQuality);
    }

    const relFull = `/images/galleries/${bucket.slug}/${num}.jpg`;
    const relThumb = `/images/galleries/${bucket.slug}/${num}-thumb.jpg`;
    return {
      status: 'ok',
      file: item.name, out: relFull, thumb: relThumb, dims: `${dims.width}×${dims.height}`,
      sizeIn: bytes, sizeOut: DRY ? 0 : statSync(fullPath).size,
      id: item.id, md5, index: num,
    };
  } finally {
    await rm(tmp, { force: true });
  }
}

/** Lista zdjęć galerii odczytana z katalogu na dysku (naprawa, gdy JSON rozjechał się z plikami). */
function diskPhotoList(slug) {
  const dir = join(OUT_DIR, slug);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((n) => /^\d+\.jpg$/i.test(n))
    .sort(naturalCompare)
    .map((n) => `/images/galleries/${slug}/${n.replace(/\.jpg$/i, '-thumb.jpg')}`)
    .filter((thumb) => existsSync(join(REPO, 'public', thumb)));
}

/* ---------- gallery JSON ---------- */
function upsertGallery(slug, bucket, results, cfg) {
  const db = JSON.parse(readFileSync(GALLERIES_JSON, 'utf8'));
  // Strona oczekuje w photos_list ścieżek miniatur (siatka ładuje thumb, powiększenie podmienia na pełny plik).
  const list = results.map((r) => r.thumb).filter(Boolean);
  const fromDisk = list.length ? null : diskPhotoList(slug);   // brak nowych zdjęć → bierz to, co jest na dysku
  const meta = bucket.meta || {};
  let g = db.galleries.find((x) => x.slug === slug);
  if (!g) {
    g = {
      slug,
      title: meta.title || bucket.title,
      category: meta.category || cfg.defaultCategory,
      date: meta.date || new Date().toISOString().slice(0, 10),
      excerpt: meta.excerpt || cfg.defaultExcerpt,
      photos: 0,
      photos_list: [],
      cover: `/images/galleries/${slug}/cover.jpg`,
    };
    db.galleries.push(g);
    bucket.created = true;
  } else {
    // metadane z _meta.json mają pierwszeństwo nad tym, co wpisałem przy tworzeniu galerii
    if (meta.title) g.title = meta.title;
    if (meta.category) g.category = meta.category;
    if (meta.date) g.date = meta.date;
    if (meta.excerpt) g.excerpt = meta.excerpt;
  }
  const have = new Set(g.photos_list || []);
  for (const p of (fromDisk ?? list)) if (!have.has(p)) { g.photos_list.push(p); have.add(p); }
  g.photos = g.photos_list.length;
  if (!g.cover && g.photos_list.length) g.cover = `/images/galleries/${slug}/cover.jpg`;
  if (!DRY) writeFileSync(GALLERIES_JSON, JSON.stringify(db, null, 2) + '\n');
  return g;
}

/**
 * Podpina galerię do sekcji strony, żeby była linkowana (sama strona /galerie/<slug>/
 * istnieje, ale bez wpisu w sekcji nikt na nią nie trafi).
 * meta.link = { type: 'sesje', session: 'rodzinne' }
 *           | { type: 'reportaze', group: 'Reportaże – uroczystości rodzinne' }
 *           | [ ...więcej niż jedna sekcja naraz... ]
 * Opcje per link: position: 'first' (nowa sesja na początku listy),
 * samples_title / landscape (sesja bez sekcji przykładowych — np. ciażowe).
 */
function linkSection(slug, bucket, cfg) {
  const raw = bucket.meta?.link;
  const links = Array.isArray(raw) ? raw : raw ? [raw] : [];
  if (!links.length) return null;
  const title = bucket.meta?.title || bucket.title;
  const parts = links.map((link) => applyLink(slug, title, link));
  return parts.some((p) => String(p).startsWith('BŁĄD')) ? `BŁĄD: ${parts.join(' + ')}` : parts.join(' + ');
}

function applyLink(slug, title, link) {
  if (!link || !link.type) return 'BŁĄD: link bez typu';
  if (link.type === 'sesje') {
    const p = join(REPO, 'src/data/sesje.json');
    const db = JSON.parse(readFileSync(p, 'utf8'));
    const session = db.sessions.find((s) => s.slug === link.session);
    if (!session) return `BŁĄD: nie ma sesji "${link.session}" w sesje.json`;
    session.samples ||= [];
    if (link.samples_title) session.samples_title = link.samples_title;
    if (link.landscape !== undefined) session.samples_landscape = !!link.landscape;
    if (!session.samples.some((s) => s.slug === slug)) {
      const item = { title, slug };
      if (link.position === 'first') session.samples.unshift(item);
      else session.samples.push(item);
    }
    if (!DRY) writeFileSync(p, JSON.stringify(db, null, 2) + '\n');
    return `/sesje/${link.session}/`;
  }
  if (link.type === 'reportaze') {
    const p = join(REPO, 'src/data/reportaze.json');
    const db = JSON.parse(readFileSync(p, 'utf8'));
    const group = link.group
      ? db.groups.find((g) => g.title === link.group)
      : db.groups[0];
    if (!group) return `BŁĄD: nie ma grupy "${link.group}" w reportaze.json`;
    group.items ||= [];
    if (!group.items.some((i) => i.slug === slug)) {
      const item = { title, slug };
      if (link.position === 'first') group.items.unshift(item);
      else group.items.push(item);
    }
    if (!DRY) writeFileSync(p, JSON.stringify(db, null, 2) + '\n');
    return `/reportaze/ (grupa: ${group.title})`;
  }
  return `BŁĄD: nieznany typ linku "${link.type}"`;
}

/* ---------- raport ---------- */
function writeReport(buckets, cfg) {
  const lines = [];
  const now = new Date().toLocaleString('pl-PL', { timeZone: 'Europe/Warsaw' });
  lines.push('# Synchronizacja galerii — raport', '', `Ostatnie uruchomienie: ${now}${DRY ? ' (dry-run)' : ''}`, '');
  let ok = 0, rejected = 0, skipped = 0;
  for (const b of buckets) {
    const good = b.results.filter((r) => r.status === 'ok');
    const bad = b.results.filter((r) => r.status === 'reject');
    const skip = b.results.filter((r) => r.status === 'skip');
    ok += good.length; rejected += bad.length; skipped += skip.length;
    if (!good.length && !bad.length) continue;
    lines.push(`## ${b.gallery?.title || b.title} → /galerie/${b.slug}/`);
    if (b.section && !String(b.section).startsWith('BŁĄD')) {
      lines.push(`Podpięta do sekcji: ${b.section}`, '');
    } else if (b.section) {
      lines.push(`⚠️ ${b.section}`, '');
    } else {
      lines.push('⚠️ Nie jest podpięta do żadnej sekcji (brak `_meta.json` z `link`) — nikt na nią nie trafi z menu. Dopisz meta i puść sync ponownie.', '');
    }
    if (good.length) {
      lines.push(`Dodane zdjęcia (${good.length}):`);
      for (const r of good) {
        const kb = r.sizeOut ? `${Math.round(r.sizeOut / 1024)} kB` : '—';
        lines.push(`- ${r.file} → \`${r.out}\` + miniatura (${r.dims}, ${kb})`);
      }
      lines.push('');
    }
    if (bad.length) {
      lines.push(`Odrzucone (${bad.length}):`);
      for (const r of bad) lines.push(`- ${r.file} — ${r.reason}`);
      lines.push('');
    }
    if (skip.length) lines.push(`Pominięte (już były): ${skip.length}`, '');
  }
  lines.push('---', `Razem: dodane ${ok}, odrzucone ${rejected}, pominięte ${skipped}.`, '');
  lines.push(`Limity: długi bok ≥ ${cfg.minLongEdge} px, plik ≤ ${cfg.rejectOverMB} MB, wynik ${cfg.fullMax} px / miniatura ${cfg.thumbMax} px.`);
  const p = join(REPO, cfg.reportFile);
  if (!DRY) writeFileSync(p, lines.join('\n') + '\n');
  return lines.join('\n');
}

/** Wrzuca raport z powrotem do folderu Drive (Anna widzi, co odpadło i dlaczego). */
async function uploadReportToDrive(token, folderId, text) {
  const name = '_RAPORT-synchronizacji.txt';
  const q = new URLSearchParams({
    q: `'${folderId}' in parents and name = '${name}' and trashed = false`,
    fields: 'files(id,name)',
  });
  const found = await fetch(`https://www.googleapis.com/drive/v3/files?${q}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then((r) => r.json());
  const existing = found.files?.[0];

  if (existing) {
    const res = await fetch(`https://www.googleapis.com/upload/drive/v3/files/${existing.id}?uploadType=media`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'text/plain; charset=utf-8' },
      body: text,
    });
    if (!res.ok) throw new Error(`Nie udało się podmienić raportu na Drive (${res.status})`);
    return existing.id;
  }

  const boundary = 'gs-' + Date.now();
  const meta = JSON.stringify({ name, parents: [folderId], mimeType: 'text/plain' });
  const body = [
    `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${meta}\r\n`,
    `--${boundary}\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n${text}\r\n`,
    `--${boundary}--`,
  ].join('');
  const res = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': `multipart/related; boundary=${boundary}` },
    body,
  });
  const j = await res.json();
  if (!res.ok) throw new Error(`Nie udało się wgrać raportu na Drive (${res.status}): ${j.error?.message || ''}`);
  return j.id;
}

/* ---------- main ---------- */
async function main() {
  const { mkdtemp } = await import('node:fs/promises');
  const tmpdir = await mkdtemp(join(os.tmpdir(), 'gallery-sync-'));
  const state = loadState();
  const buckets = [];

  if (LOCAL_DIR) {
    const root = resolve(LOCAL_DIR);
    if (!existsSync(root)) throw new Error(`Nie ma katalogu ${root}`);
    const entries = localList(root);
    const subdirs = entries.filter((e) => e.isDir);
    const rootImages = entries.filter((e) => !e.isDir && IMAGE_EXT.has(extname(e.name).toLowerCase()));
    for (const d of subdirs) {
      const all = localList(d.localPath);
      const files = all.filter((f) => !f.isDir && IMAGE_EXT.has(extname(f.name).toLowerCase()));
      if (!files.length) continue;
      const metaFile = all.find((f) => !f.isDir && /^_meta\.json$/i.test(f.name));
      buckets.push({
        title: d.name, slug: slugify(d.name) || 'sesja',
        files: files.sort((a, b) => naturalCompare(a.name, b.name)),
        meta: metaFile ? parseMeta(readFileSync(metaFile.localPath, 'utf8'), d.name) : null,
      });
    }
    if (rootImages.length) {
      const slug = CFG.rootGallerySlug || slugify(basename(root));
      buckets.push({ title: CFG.rootGallerySlug ? (CFG.rootGallerySlug) : basename(root), slug, files: rootImages.sort((a, b) => naturalCompare(a.name, b.name)), loose: true });
    }
  } else {
    const folderId = opt('--folder', process.env.GDRIVE_FOLDER_ID || CFG.driveFolderId);
    if (!folderId) throw new Error('Brak id folderu Drive — wpisz je do tools/gallery-sync.local.json (gitignore), ustaw GDRIVE_FOLDER_ID albo podaj --folder ID');
    const token = await accessToken();
    const entries = await driveList(token, folderId);
    const subdirs = entries.filter((e) => e.mimeType === 'application/vnd.google-apps.folder');
    const rootImages = entries.filter((e) => IMAGE_MIME.test(e.mimeType || ''));
    const ignored = entries.filter((e) => e.mimeType !== 'application/vnd.google-apps.folder' && !IMAGE_MIME.test(e.mimeType || ''));

    for (const d of subdirs) {
      const all = await driveList(token, d.id);
      const files = all.filter((f) => IMAGE_MIME.test(f.mimeType || ''));
      if (!files.length) continue;
      const metaFile = all.find((f) => !f.mimeType.includes('folder') && /^_meta\.json$/i.test(f.name));
      let meta = null;
      if (metaFile) {
        const metaTmp = join(tmpdir, `meta-${slugify(d.name) || 'g'}.json`);
        await driveDownload(token, metaFile.id, metaTmp);
        meta = parseMeta(readFileSync(metaTmp, 'utf8'), d.name);
      }
      buckets.push({ title: d.name, slug: slugify(d.name) || 'sesja', files: files.sort((a, b) => naturalCompare(a.name, b.name)), meta });
    }
    if (rootImages.length) {
      const slug = CFG.rootGallerySlug || 'nowe-zdjecia';
      buckets.push({ title: CFG.rootGallerySlug || 'Nowe zdjęcia', slug, files: rootImages.sort((a, b) => naturalCompare(a.name, b.name)), loose: true });
    }
    if (ignored.length) console.log(`Pominięto ${ignored.length} plik(ów) innych niż zdjęcia: ${ignored.map((f) => f.name).join(', ')}`);
    globalThis.__token = token;
  }

  if (!buckets.length) {
    console.log('Wrzutnia jest pusta — brak zdjęć do dodania.');
    return;
  }

  let seq = 0;
  for (const b of buckets) {
    const dir = join(OUT_DIR, b.slug);
    b.nextIndex = nextIndex(dir);
    b.results = [];
    for (const f of b.files) {
      const r = await processFile(f, b, CFG, { state, tmpdir, seq: seq++, token: globalThis.__token });
      if (r.status === 'ok') {
        b.results.push(r);
        state.files[f.id] = { md5: r.md5, gallery: b.slug, file: r.out.replace(/^\//, ''), processedAt: new Date().toISOString(), source: f.name };
      } else b.results.push(r);
    }
    // Galeria istnieje już na stronie? Wtedy sam _meta.json (bez nowych zdjęć) też ma zadziałać.
    const already = JSON.parse(readFileSync(GALLERIES_JSON, 'utf8')).galleries.some((x) => x.slug === b.slug);
    const onDisk = diskPhotoList(b.slug).length > 0;
    if (b.results.some((r) => r.status === 'ok') || already || onDisk) {
      // okładka: `cover` z _meta.json (nazwa pliku źródłowego albo numer zdjęcia),
      // domyślnie pierwsze zdjęcie galerii — i tylko jeśli jeszcze jej nie ma
      if (!DRY) {
        const coverOut = join(OUT_DIR, b.slug, 'cover.jpg');
        const added = b.results.filter((r) => r.status === 'ok');
        const wanted = b.meta?.cover;
        const wantedStem = typeof wanted === 'string' ? wanted.replace(/\.[^.]+$/, '').toLowerCase() : null;
        const pick = wanted === undefined || wanted === null
          ? added[0]
          : (typeof wanted === 'number'
            ? added.find((r) => Number(r.index) === wanted)
            : added.find((r) => r.file === wanted || String(r.file).replace(/\.[^.]+$/, '').toLowerCase() === wantedStem));
        if (wanted !== undefined && wanted !== null && !pick) {
          console.log(`Uwaga: w _meta.json galerii "${b.slug}" jest cover = ${JSON.stringify(wanted)}, ale nie ma takiego zdjęcia w tej synchronizacji — zostawiam pierwsze zdjęcie galerii.`);
        }
        const first = pick || added[0];
        if (first && !existsSync(coverOut)) {
          await writeJpeg(sharp(join(OUT_DIR, b.slug, `${first.index}.jpg`)), coverOut, CFG.coverMax ?? 1600, CFG.quality);
        }
      }
      const g = upsertGallery(b.slug, b, b.results, CFG);
      b.section = linkSection(b.slug, b, CFG);
      b.gallery = g;
    }
  }

  saveState(state);
  const report = writeReport(buckets, CFG);
  console.log('\n' + report);
  if (!LOCAL_DIR && CFG.uploadReportToDrive && globalThis.__token && !DRY) {
    const folderId = opt('--folder', process.env.GDRIVE_FOLDER_ID || CFG.driveFolderId);
    try {
      await uploadReportToDrive(globalThis.__token, folderId, report);
      console.log('Raport wrzucony do folderu na Drive (_RAPORT-synchronizacji.txt).');
    } catch (e) {
      console.log(`Uwaga: nie udało się wgrać raportu na Drive — ${e.message}`);
    }
  }
  console.log(DRY ? '\n(dry-run: nic nie zostało zapisane)' : `\nRaport: ${CFG.reportFile}`);
}

main().catch((e) => { console.error('BŁĄD:', e.message); process.exit(1); });
