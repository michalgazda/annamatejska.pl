# Decap CMS setup (annamatejska.pl)

The admin panel lives at `/admin/` (`public/admin/index.html` + `config.yml`
+ self-hosted `decap-cms.js` bundle). It is a static page shipped in `dist/`.

## What Anna can do in the panel

- **Galerie** — add/edit galleries. The panel edits `src/data/galleries.json`;
  photos are uploaded through the Media library into `public/images/`
  (Media library also lists all existing main-site photos). Image paths are
  stored with the GH Pages prefix and normalized by `assetPath()` on build.
- **Opinie** — testimonials in `src/data/testimonials.json`.
- **Oferta (sesje)** — full service copy in `src/data/services.json`.
- **Ustawienia** — contact data in `src/data/site.json`.

Saving (publish) creates a commit on `main` → GitHub Actions builds `dist/`
and deploys to GH Pages. Nothing else to run — the Astro build reads the same
JSON files the panel edits.

## Auth — Cloudflare Worker OAuth bridge (provisioned)

The Worker URL is live at `https://annamatejska-decap-oauth.annamatejska.workers.dev`,
and the GitHub OAuth client ID/secret are configured. Deployed Worker version
`6c5042b6-bec2-4bba-9b15-4ba5564a8d89` returns a GitHub authorization redirect,
validates a short-lived HttpOnly/Secure/SameSite=Lax OAuth state cookie, exchanges
the code server-side, and performs Decap's `authorizing:github` /
`authorization:github:success` popup handshake restricted to `ALLOWED_ORIGINS`.
`public/admin/config.yml` is wired to this URL. The latest Pages workflow passed.

**Interactive login remains to be completed by Michal/Anna:** open
`https://michalgazda.github.io/annamatejska.pl/admin/`, click "Login with GitHub",
and complete GitHub's authorization in the popup. The account must have write
access to `michalgazda/annamatejska.pl`. The OAuth app requests `repo` scope;
GitHub collaborator permissions control repository access.

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
stored under `public/images/`. The Media library points at that existing image
tree (50 images currently), so existing work is selectable and new uploads are
available too. `public_folder` is `/annamatejska.pl/images` to preview correctly
on project Pages; Astro `assetPath()` normalizes paths on output for GH Pages
and Docker. Gallery pages use the list and its first image for `og:image`; older
galleries without a list retain the `images/galleries/<slug>/NN.jpg` convention.

## Remaining before Anna can publish

- [ ] Complete an interactive login test from the deployed panel. The Worker `/auth` endpoint and GitHub callback redirect are live; callback state validation is implemented. A browser-based GitHub approval is required to verify the final handshake.
- [ ] Add Anna's GitHub account as a collaborator with write access and have her accept the invitation.
- [ ] After any Worker code changes, deploy with `cd oauth-bridge && npx wrangler deploy` (the latest repo source should be deployed before production login).
