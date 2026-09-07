# kadrowania — portfolio zawodowe

Jasna, ciepła, przystępna wersja strony Anny Matejskiej-Gazdy dla fotografii
**wydarzeń, architektury i podróży**. Biało-czarny look, przyjazny dla
małych lokalnych marek, organizacji społecznych i placówek kultury.
Docelowo: subdomena `kadrowania.annamatejska.pl` (obecnie pod `/kadrowania/`).

Strona rodzinna (taupe/ivory) zostaje na `annamatejska.pl` —
link w stopce prowadzi do `../index.html`.

## Struktura

```
kadrowania/
├── index.html              # strona jednostronicowa (hero, manifest, portfolio,
│                           #   o mnie, współpraca, kontakt, stopka)
├── assets/
│   ├── css/
│   │   ├── fonts.css       # @font-face — lokalne woff2
│   │   └── style.css       # cały wygląd (tokeny w :root na górze pliku)
│   ├── js/
│   │   └── main.js         # reveal-on-scroll, filtr portfolio, menu mobilne —
│   │                       #   vanilla JS, brak zależności
│   └── fonts/              # Syne + Space Grotesk (woff2, latin + latin-ext,
│                           #   polskie znaki działają)
├── images/
│   ├── hero.jpg            # duże zdjęcie w hero (poziome)
│   ├── manifesto.jpg       # zdjęcie w sekcji manifest i „O mnie" (pionowe)
│   └── portfolio/
│       ├── wydarzenia/     # 01.jpg … 04.jpg
│       ├── architektura/   # 01.jpg … 04.jpg
│       └── podroze/        # 01.jpg … 04.jpg
├── tools/
│   └── make-placeholders.py  # generator jasnych placeholderów (PIL)
└── README-pl.md
```

Zero frameworków, zero CDN — wszystko lokalne, ścieżki względne
(strona działa też z podkatalogu, np. `/kadrowania/`).

## Jak podmienić placeholdery na prawdziwe zdjęcia

Wszystkie obecne pliki JPG to **generowane placeholdery** (jasne, miękkie,
czarno-białe). Zamień je po prostu własnymi zdjęciami, **zachowując nazwy
plików i orientacje** (pliki `01`/`03` są poziome, `02`/`04` pionowe,
`hero.jpg` poziome, `manifesto.jpg` pionowe):

1. `images/hero.jpg` — szerokie, jasne zdjęcie do sekcji hero (min. ~1600 px szerokości).
2. `images/manifesto.jpg` — pionowe zdjęcie 3:4, używane w „Manifest" i „O mnie".
3. `images/portfolio/<kategoria>/01.jpg … 04.jpg` — kadry do siatki portfolio.

Optymalnie: eksportuj JPEG w dłuższej krawędzi ~1600 px, jakość ~80.
Strona nie przyciemnia zdjęć (jasny design) — pilnuj, żeby zdjęcia były
odpowiednio dobrej jakości i jasności. Podpisy i alty edytuje się w `index.html`.

Gdyby trzeba było odtworzyć placeholdery:

```bash
python3 tools/make-placeholders.py
```

## Podgląd lokalnie

```bash
# z katalogu głównego repo (ważne dla linku ../index.html w stopce):
python3 -m http.server 8123
# → http://127.0.0.1:8123/kadrowania/
```

## Kategorie portfolio

Filtry na stronie: **Wydarzenia / Architektura / Podróże**
(`data-cat` w `index.html`, katalogi w `images/portfolio/` — trzymają się 1:1).
Dodanie nowego kadru = nowy `<figure class="portfolio-grid__item">` z
`data-cat` + plik JPG w odpowiednim katalogu.