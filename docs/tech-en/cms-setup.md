# Decap CMS setup (annamatejska.pl)

The admin panel lives at `/admin/` (`public/admin/index.html` + `config.yml`
+ self-hosted `decap-cms.js` bundle). It is a static page shipped in `dist/`.

## What Anna can do in the panel

- **Galerie** — add/edit galleries. The panel edits `src/data/galleries.json`;
  photos are uploaded through the Media library to `public/images/uploads/`
  and saved in `photos_list` for the gallery page.
- **Opinie** — testimonials in `src/data/testimonials.json`.
- **Oferta (sesje)** — full service copy in `src/data/services.json`.
- **Ustawienia** — contact data in `src/data/site.json`.

Saving (publish) creates a commit on `main` → GitHub Actions builds `dist/`
and deploys to GH Pages. Nothing else to run — the Astro build reads the same
JSON files the panel edits.

## Auth — Cloudflare Worker OAuth bridge (provisioned)

The Worker URL is live at `https://annamatejska-decap-oauth.annamatejska.workers.dev`,
and its GitHub OAuth client ID/secret are configured. The deployed Worker version
currently redirects `/auth` to GitHub. The repo source `oauth-bridge/src/worker.js`
has the corrected Decap popup handshake plus state-cookie validation; deploy this
latest source before enabling the CMS config:

```bash
cd oauth-bridge
npx wrangler deploy
```

Then set `base_url: https://annamatejska-decap-oauth.annamatejska.workers.dev`
and `auth_endpoint: /auth` under `backend:` in `public/admin/config.yml`, push,
and test an interactive login from `/admin/`. A local mocked callback verifies
the handshake and state validation; the live GitHub approval/login still needs
a browser session.

## Local testing (without auth)

```bash
npx decap-server                     # proxy backend on :8081, saves to local git
npm run build && docker compose up -d --build
# open http://127.0.0.1:8890/admin/ → "Login with GitHub" works against the proxy
```

Note: the local nginx CSP for `/admin/` already allows `unsafe-eval`
(Decap requirement) and `connect-src api.github.com`.

## Gallery photos path (implemented)

The Decap collection includes `photos_list`, an ordered list of Media uploads
stored under `public/images/uploads/`. Gallery detail pages use that list and
its first image for `og:image`; older galleries without a list retain the
`images/galleries/<slug>/NN.jpg` convention.

## Remaining before Anna can publish

- [ ] Complete an interactive login test from the deployed panel. The Worker `/auth` endpoint and GitHub callback redirect are live; callback state validation is implemented. A browser-based GitHub approval is required to verify the final handshake.
- [ ] Add Anna's GitHub account as a collaborator with write access and have her accept the invitation.
- [ ] After any Worker code changes, deploy with `cd oauth-bridge && npx wrangler deploy` (the latest repo source should be deployed before production login).
