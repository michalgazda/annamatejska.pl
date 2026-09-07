# Decap CMS setup (annamatejska.pl)

The admin panel lives at `/admin/` (entry `admin/index.html` + `admin/config.yml`).
A friendly landing page is at `/panel.html`.

## What Anna can do in the panel

- **Galerie** — create/edit gallery pages (`galerie/*.html` as markdown-with-frontmatter
  entries is NOT used; this repo keeps generated HTML). The CMS edits the registry
  `data/galleries.json` and stores photos under `images/uploads/`.
- **Opinie** — add/remove client testimonials stored in `data/testimonials.json`.
- **Ustawienia** — the gallery registry (auto-maintained).

After CMS saves to `main`, a deploy hook (Netlify / GitHub Action) must run:

```bash
python3 tools/build-home-galleries.py   # refresh homepage + galerie.html cards
python3 tools/build-testimonials.py     # refresh homepage Opinie section
```

Then the built static output is published.

## Auth

Decap CMS with `backend.name: github` needs an OAuth bridge:

- **Easiest:** enable Netlify Identity on the Netlify site (free tier) and invite
  Anna by email — no code, works out of the box with `name: github` replaced by
  `name: git-gateway`.
- **Self-hosted option:** run an external OAuth provider (e.g. oauth2-proxy or
  https://github.com/i40west/decap-github-oauth) on the Hetzner VPS.

## Local testing (without auth)

```bash
npx decap-server          # in a second terminal, proxies to local git
python3 -m http.server 8088
# open http://localhost:8088/admin/ — saves go to your local repo
```

## TODO before production

- [ ] Decide Netlify Identity vs VPS OAuth, then flip `backend.name` accordingly
      (git-gateway vs github + `base_url`).
- [ ] Add deploy hook that runs the two build tools above.
- [ ] Consider `publish_mode: editorial_workflow` (already on) so Anna's changes
      go through a review branch before publishing.
