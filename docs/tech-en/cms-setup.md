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

## Auth — Cloudflare Worker OAuth bridge (chosen plan, free)

GitHub doesn't allow pure-browser token exchange, so Decap needs a tiny OAuth
bridge. **Cloudflare Workers free tier** (100k req/day) hosts it for free —
code in `oauth-bridge/` in this repo (single `src/worker.js`, no dependencies).

Deploy steps (one-time, Michal):

1. **GitHub OAuth App**: github.com → Settings → Developer settings →
   OAuth Apps → New:
   - Application name: `annamatejska-decap`
   - Homepage URL: `https://michalgazda.github.io/annamatejska.pl/`
   - Authorization callback URL: `https://annamatejska-decap-oauth.<account>.workers.dev/callback`
   - Note the Client ID, generate a Client Secret.
2. **Deploy the worker**:
   ```bash
   cd oauth-bridge
   npx wrangler login            # browser auth to your Cloudflare account
   npx wrangler secret put GITHUB_CLIENT_ID
   npx wrangler secret put GITHUB_CLIENT_SECRET
   npx wrangler deploy
   ```
   Worker URL: `https://annamatejska-decap-oauth.<account>.workers.dev`
3. **Point Decap at it**: in `public/admin/config.yml` under `backend:` add
   ```yaml
   base_url: https://annamatejska-decap-oauth.<account>.workers.dev
   auth_endpoint: /auth
   ```
   (`ALLOWED_ORIGINS` in `oauth-bridge/wrangler.toml` lists the panel origins
   allowed to receive the token — update if the site domain changes.)
4. **Anna's access**: create a GitHub account for Anna and add her as a
   collaborator on the repo (Settings → Collaborators). The OAuth token scope
   is `repo`, so repo privacy stays enforced by GitHub.

Why not the alternatives: Netlify Identity ties auth+hosting to Netlify;
self-hosted bridge needs the Hetzner VPS (still on order) + TLS certs.
Cloudflare is free, zero-maintenance, and on your own account.

Local testing note: `http://127.0.0.1:8890` is in ALLOWED_ORIGINS, so the
panel on Docker can log in against the production worker too.

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
