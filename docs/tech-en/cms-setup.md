# Decap CMS setup (annamatejska.pl)

The admin panel lives at `/admin/` (`public/admin/index.html` + `config.yml`
+ self-hosted `decap-cms.js` bundle). It is a static page shipped in `dist/`.

## What Anna can do in the panel

- **Galerie** — add/edit galleries. The panel edits `src/data/galleries.json`;
  photos are uploaded through the Media library to `public/images/uploads/`.
  The gallery detail page (`src/pages/galerie/[slug].astro`) currently derives
  photo URLs as `images/galleries/<slug>/01..NN.jpg` — see "Known gap" below.
- **Opinie** — testimonials in `src/data/testimonials.json`.
- **Oferta (sesje)** — full service copy in `src/data/services.json`.
- **Ustawienia** — contact data in `src/data/site.json`.

Saving (publish) creates a commit on `main` → GitHub Actions builds `dist/`
and deploys to GH Pages. Nothing else to run — the Astro build reads the same
JSON files the panel edits.

## Auth (the unfinished part)

Decap with `backend.name: github` needs an OAuth bridge — GitHub does not
allow pure-browser token exchange. Options:

1. **Siberian GH OAuth bridge** (decap's community standard, e.g.
   `https://github.com/i40west/decap-github-oauth` — there are also free
   hosted instances) running on the Hetzner VPS (CX22, on order).
   Create a GitHub OAuth App:
   - Homepage URL: `https://michalgazda.github.io/annamatejska.pl/`
   - Callback: `https://<bridge-domain>/callback`
   Then in `public/admin/config.yml` add under `backend:`:
   `base_url: https://<bridge-domain>`
2. **Netlify Identity + git-gateway** — zero code, but ties hosting to Netlify
   (site is currently GH Pages + Docker; probably not worth it).
3. **Static CMS `github` backend with a PKCE-less flow** — not supported; skip.

Anna needs a GitHub account added as a collaborator on the repo
(Settings → Collaborators) OR the OAuth app can be limited to read/write
contents of this repo only (fine-grained PAT is not usable by Decap; the
OAuth scope is `repo`).

## Local testing (without auth)

```bash
npx decap-server                     # proxy backend on :8081, saves to local git
npm run build && docker compose up -d --build
# open http://127.0.0.1:8890/admin/ → "Login with GitHub" works against the proxy
```

Note: the local nginx CSP for `/admin/` already allows `unsafe-eval`
(Decap requirement) and `connect-src api.github.com`.

## Known gap: gallery photos path

The panel uploads photos to `public/images/uploads/`, but gallery detail
pages expect `images/galleries/<slug>/NN.jpg`. Two options:

- **A (panel-friendly):** change `[slug].astro` to read an optional
  `photos_list: []` array of uploaded image paths; fall back to the
  `NN.jpg` convention when absent. Small Astro change, recommended.
- **B (process):** Michal periodically moves uploads into per-gallery folders
  and sets `photos` count. Zero code, manual work.

## TODO before Anna uses it

- [ ] Provision Hetzner CX22 (on order) → run the OAuth bridge (+ TLS via
      certbot or Cloudflare in front).
- [ ] Create GitHub OAuth App; set `base_url` in `public/admin/config.yml`.
- [ ] Create Anna's GitHub account / add as collaborator.
- [ ] Decide gallery-photos path fix (option A above) and implement.
- [ ] Re-test full publish flow end-to-end (edit → workflow → publish → deploy).
