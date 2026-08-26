# annamatejska.pl — new website

Professional redesign of Anna Matejska-Gazda's photography site (Kraków).
Plain static HTML/CSS — zero build step, deploys anywhere (GitHub Pages, Netlify, any VPS/nginx).

## Structure

```
index.html              # one-page site (P0)
images/                 # placeholder photos pulled from current WP site
docs/
├── design-ux-pl/       # product/UX docs in Polish
│   └── wizja-strony.md # vision, personas, structure, design system, roadmap
└── tech-en/            # technical docs in English (empty for now)
```

## Language policy

- Product/design/UX/marketing docs: **Polish** (`docs/design-ux-pl/`)
- Code & technical docs: **English** (`docs/tech-en/`, code comments)

## Local preview

```bash
python3 -m http.server 8088   # then open http://localhost:8088
```

## Before production

1. Replace placeholder images with Anna's final selection (high-res → convert to WebP)
2. Get model releases / consent for third-party people in photos
3. Swap the `mailto:` form for a real backend or form service (Netlify Forms / Formspree / own API)
4. Add per-session subpages as SEO landing pages (P1), pricing page, gallery lightbox
5. Add favicon + OG image, sitemap.xml, robots.txt

## Roadmap

- **P0 (done):** one-page site — hero, about, 6 session types, process, seasonal pleners, testimonials, gallery, contact; responsive; basic SEO meta
- **P1:** session subpages, pricing, lightbox, booking form
- **P2:** vouchers, albums, blog, booking integration
