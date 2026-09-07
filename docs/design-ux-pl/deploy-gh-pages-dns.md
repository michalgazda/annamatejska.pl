# Wdrożenie na GitHub Pages + DNS — przewodnik (PL)

Status: **GitHub Pages jest darmowy** dla repozytoriów publicznych
(limity: 1 GB na stronę, ~100 GB ruchu/mies., 10 buildów/h — dla strony
fotografki to zapas). Repo `michalgazda/annamatejska.pl` jest publiczne,
więc koszt = 0 zł. Płatny plan (Pro) potrzebny dopiero, gdyby repo miało
być prywatne.

> Uwaga: przy publicznym repo kod strony jest publiczny — to nie problem
> (treści i tak są na stronie), ale panel CMS jest zabezpieczony hasłem
> GitHub, więc nikt poza Anną i Michalem nie zmieni treści.

---

## Krok 1 — Włącz GitHub Pages (raz, 2 minuty)

1. Wejdź na `https://github.com/michalgazda/annamatejska.pl`
2. **Settings → Pages**
3. **Source:** „GitHub Actions”
4. Gotowe — workflow utworzymy w kroku 2.

## Krok 2 — Dodaj workflow deployujący (ja to zrobię przy commicie)

Plik `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v5
      # odbuduj HTML z danych CMS (galerie, opinie, oferta)
      - run: |
          python3 tools/build-gallery-pages.py
          python3 tools/build-home-galleries.py
          python3 tools/build-testimonials.py
          python3 tools/build-services.py
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deployment
        uses: actions/deploy-pages@v4
```

Efekt: każdy push na `main` (w tym każdy „Publish” Anny w panelu)
automatycznie odświeża stronę po ~1 minucie.

## Krok 3 — Dwie strony, jedno repo

Struktura już jest przygotowana:

| Strona | Adres docelowy | Katalog w repo |
|---|---|---|
| Sesje rodzinne | `annamatejska.pl` | `/` (root) |
| Portfolio | `kadrowania.annamatejska.pl` | `/kadrowania` |

GitHub Pages obsługuje **tylko jedną domenę na repo**. Dlatego
`kadrowania.annamatejska.pl` kierujemy na ten sam hosting, a routing
załatwia plik `.github/workflows` (krok 2) + przekierowanie:

Plik **`kadrowania/index.html`** już działa pod `/kadrowania/`, więc na
GitHub Pages wygodne jest dwa repozytoria... **ALE** — żeby zostać przy
jednym repo (decyzja z zakresu organizacji pracy), stosujemy wariant A
lub B:

### Wariant A (rekomendowany): dwa repozytoria, zero trików
1. `annamatejska.pl` → repo `michalgazda/annamatejska.pl` (root)
2. Repo `michalgazda/kadrowania.annamatejska.pl`, do którego kopiujemy
   zawartość `kadrowania/` (jednorazowo; potem zmiany trafiają tu).
   - Settings → Pages → custom domain: `kadrowania.annamatejska.pl`
   - Obie strony dostają niezależne ustawienia i własny CNAME.

### Wariant B: jedno repo, podstrona pod ścieżką
Strona portfolio dostępna jako `annamatejska.pl/kadrowania/`,
a `kadrowania.annamatejska.pl` robi przekierowanie 301 (ustawiane u
rejestratora DNS lub Cloudflare). Najprostsze, ale adres w przeglądarce
po przekierowaniu zmienia się na `/kadrowania/`.

---

## Krok 4 — DNS u rejestratora (gdzie kupiona jest domena)

### annamatejska.pl (strona główna)

W panelu DNS rejestratora (np. OVH, nazwa.pl, Cloudflare):

```
Typ:   A     @      185.199.108.153
Typ:   A     @      185.199.109.153
Typ:   A     @      185.199.110.153
Typ:   A     @      185.199.111.153
Typ:   CNAME www    michalgazda.github.io.
```

Następnie w repo: **Settings → Pages → Custom domain** → wpisz
`annamatejska.pl` → Add. GitHub utworzy plik `CNAME` w repo.

### kadrowania.annamatejska.pl (portfolio — wariant A)

```
Typ:   CNAME kadrowania   michalgazda.github.io.
```

W repo `kadrowania.annamatejska.pl`: Settings → Pages → Custom domain →
`kadrowania.annamatejska.pl`.

### Uwagi
- **Propagacja DNS:** od 15 minut do kilku godzin.
- **HTTPS:** w Settings → Pages zaznacz „Enforce HTTPS” (certyfikat
  Let's Encrypt wystawia GitHub automatycznie — darmowy).
- **www vs bez www:** najlepiej ustawić w Pages domenę `www.annamatejska.pl`
  jako custom domain — GitHub sam przekieruje `annamatejska.pl` na `www`
  (albo odwrotnie; byle konsekwentnie, dla SEO).
- Jeśli DNS trzyma Cloudflare, ustaw tryb proxy „DNS only” (szara chmurka)
  na rekordach GitHub Pages — GitHub sam terminuje HTTPS.

---

## Krok 5 — Co z panelem CMS na GitHub Pages?

Panel `/admin/` zadziała po jednej dodatkowej rzeczy: **logowaniu**.

1. W repo: **Settings → Pages →** włącz **GitHub Pages** i wejdź w
   ustawienia aplikacji OAuth:
   `Settings → Developer settings → OAuth Apps → New OAuth App`
   - Homepage: `https://annamatejska.pl`
   - Callback: `https://served-with-care.vercel.app/callback`
     (albo własny most OAuth — patrz `docs/tech-en/cms-setup.md`)
2. Prostsza droga: **Netlify Identity** (darmowe) — wtedy hostujemy na
   Netlify zamiast GitHub Pages i logowanie Anną ma zero konfiguracji.

> **Rekomendacja:** skoro i tak potrzebny jest most OAuth albo Netlify
> Identity, rozważ **Netlify zamiast GitHub Pages** — darmowy plan,
> custom domain, HTTPS i wbudowane logowanie do panelu oraz formularz
> kontaktowy (Forms) bez żadnego kodu. GitHub Pages zostawiamy jako
> plan B.

---

## Checklist wdrożenia

- [ ] Workflow deploy.yml w repo (ja dodam)
- [ ] Settings → Pages → Source: GitHub Actions
- [ ] DNS: rekordy A/CNAME u rejestratora
- [ ] Settings → Pages → Custom domain + Enforce HTTPS
- [ ] Test: https://annamatejska.pl i https://kadrowania.annamatejska.pl
- [ ] Logowanie do panelu (OAuth App lub Netlify Identity)
