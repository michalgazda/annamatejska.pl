# annamatejska.pl — Nowa strona fotograficzna dla Anny Matejskiej-Gazdy

Nowoczesna, ultra-szybka strona portfolio dla najlepszej krakowskiej fotografki.
Czysty HTML/CSS/JS (zero frameworków, zero baz danych, zero skomplikowanego hostingu) — działa wszędzie: Netlify, GitHub Pages, Cloudflare Pages lub dowolny serwer/VPS.

---

## 🎨 Design & Kolorystyka
- Odzwierciedla ciepłą, autorską paletę obecnej strony: **taupe/brąz (#A08C72)**, kość słoniowa/papier (#FAFAF8), głęboki grafit/ink (#0D0D0D).
- Typografia: editorial serif (`Cormorant Garamond`) + minimalistyczny sans (`Jost`).
- Koncepcja **„Photo-First”**: minimalistyczny interfejs ustępuje miejsca zdjęciom, które są głównym bohaterem.

---

## 📸 Jak Anna może dodawać galerie i edytować ofertę?

System został zaprojektowany tak, aby dodawanie nowych sesji było banalnie proste i **nie wymagało pisania kodu ani WordPressa**:

### 1. Dodanie nowej galerii w 2 krokach:
1. **Wrzuć zdjęcia:** Stwórz folder z numerowanymi zdjęciami: `images/galleries/nazwa-sesji/` (np. `01.jpg`, `02.jpg`, `03.jpg`...).
2. **Uruchom generator:**
   ```bash
   python3 tools/new-gallery.py \
     --slug "rodzinna-ogrod-botaniczny" \
     --title "Rodzinna w Ogrodzie Botanicznym" \
     --category "Sesje rodzinne" \
     --date "2026-08-26" \
     --excerpt "Ciepłe letnie kadry pośród zieleni i kwiatów." \
     --wide "1"
   ```
   *Generator automatycznie:*
   - Tworzy dedykowaną stronę galerii z lightboxem (`galerie/rodzinna-ogrod-botaniczny.html`)
   - Rejestruje galerię w `data/galleries.json`
   - Aktualizuje sekcję „Najnowsze galerie” na stronie głównej oraz w katalogu `galerie.html`

### 2. Edycja oferty i tekstów:
- Wszystkie podstrony ofertowe znajdują się w `sesje/*.html` (np. `sesje/rodzinne.html`, `sesje/kobiece.html`).
- Generator szablonów sesji: `tools/gen-session-pages.py` (pozwala błyskawicznie przeładować opisy dla wszystkich 6 kategorii sesji).

---

## 📂 Struktura repozytorium

```
annamatejska.pl/
├── index.html              # Strona główna (Hero, O mnie, Oferta 6 sesji, Proces, Pory roku, Galerie, Opinie)
├── galerie.html            # Główny katalog wszystkich galerii
├── kontakt.html            # Strona kontaktowa z formularzem (gotowym pod Netlify / Formspree)
├── assets/
│   ├── css/style.css       # Jeden czysty, responsywny arkusz stylów
│   └── js/main.js          # Menu mobilne + lekki lightbox dla galerii
├── data/
│   └── galleries.json      # Baza danych galerii w prostym formacie JSON
├── sesje/                  # Dedykowane strony landingowe SEO dla 6 typów sesji
│   ├── rodzinne.html
│   ├── dzieciece.html
│   ├── kobiece.html
│   ├── ciazowe.html
│   ├── romantyczne.html
│   └── wizerunkowe.html
├── galerie/                # Podstrony pojedynczych galerii zdjęć
│   └── sesja-rodzinna-kopiec-kraka.html
├── images/                 # Zdjęcia demonstracyjne i zasoby graficzne
├── tools/                  # Proste skrypty CLI dla Anny
│   ├── new-gallery.py
│   ├── build-home-galleries.py
│   └── gen-session-pages.py
└── docs/
    ├── design-ux-pl/       # Dokumentacja UX i wizja produktu po polsku
    └── tech-en/            # Specyfikacja techniczna po angielsku
```

---

## 🚀 Podgląd lokalny

```bash
cd ~/annamatejska.pl
python3 -m http.server 8088
# Otwórz w przeglądarce: http://localhost:8088
```

---

## ✅ Weryfikacja jakościowa (Automated QA)
- Wszystkie 10 podstron przetestowane silnikiem headless Chromium (Playwright).
- **Status HTTP 200** na wszystkich stronach.
- **Zero błędów konsoli JavaScript**.
- **Zero uszkodzonych lub brakujących obrazów**.
- Pełna responsywność (Desktop 1440px / Mobile 390px).
