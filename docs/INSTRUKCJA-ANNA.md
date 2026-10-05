# Instrukcja dla Ani — jak dodawać i aktualizować galerie

> Strona annamatejska.pl składa się z **dwóch serwisów**:
> **Strona główna** (sesje rodzinne, dziecięce, kobiece, ciążowe, romantyczne, wizerunkowe)
> i **Kadrowania** (fotografia wydarzeń, architektury i podróży).

**Są dwa sposoby zmian:**

1. **Panel zarządzania** (zalecany) — strona `…/admin/`, logowanie kontem GitHub.
   Dodajesz galerie, zdjęcia i opinie przez formularze — bez dotykania plików.
   Instrukcja: [docs/design-ux-pl/panel-instrukcja.md](design-ux-pl/panel-instrukcja.md).
2. **Ręcznie przez GitHub** — edycja plików JSON + wgrywanie zdjęć (poniżej).
   Przydaje się, gdy panel jest niedostępny albo trzeba zmienić coś, czego panel nie obsługuje.

---

## Spis treści

1. [Najszybsza droga: edycja przez stronę GitHub](#1-najszybsza-droga-edycja-przez-stronę-github)
2. [Jak dodać nową galerię (sesję)](#2-jak-dodać-nową-galerię-sesję)
3. [Jak edytować istniejącą galerię](#3-jak-edytować-istniejącą-galerię)
4. [Jak dodać zdjęcia do Kadrowania](#4-jak-dodać-zdjęcia-do-kadrowania)
5. [Jak zmienić teksty na stronie głównej (sesje, opinie, kontakt)](#5-jak-zmienić-teksty-na-stronie-głównej)
6. [Zasady dobrych zdjęć (waga, wymiary, nazwy)](#6-zasady-dobrych-zdjęć-waga-wymiary-nazwy)
7. [Rozwiązywanie problemów](#7-rozwiązywanie-problemów)

---

## 1. Najszybsza droga: edycja przez stronę GitHub

Cała zawartość strony siedzi w plikach:

| Co chcesz zmienić | Plik |
|---|---|
| Galerie sesji (główna strona) | `src/data/galleries.json` |
| Opisy sesji (rodzinne, dziecięce…) | `src/data/services.json` |
| Opinie klientów | `src/data/testimonials.json` |
| Telefon, e-mail, Instagram, Facebook | `src/data/site.json` |
| Zdjęcia | katalog `public/images/…` |
| Zdjęcia Kadrowania | katalog `public/kadrowania/images/…` |

**Wejście:** [github.com/michalgazda/annamatejska.pl](https://github.com/michalgazda/annamatejska.pl)
→ kliknij plik → ołówek (**Edit this file**) → zmień → **Commit changes**.
Po maksymunalnie 2–3 minutach strona sama się przebuduje i opublikuje
(GitHub Actions). Sprawdź efekt na stronie i gotowe.

> **Wskazówka:** Jeśli Michal skonfiguruje Ci dostęp, będziesz mogła edytować
> bezpośrednio. Do tego czasu zmiany robimy razem albo Michal zatwierdza
> (pull request).

---

## 2. Jak dodać nową galerię (sesję)

### Krok 1 — przygotuj zdjęcia

1. Wybierz **5–10 najlepszych zdjęć** z sesji.
2. Przekonwertuj je do **JPEG, maksymalnie 1920 px dłuższego boku**
   (np. darmowym [Squoosh](https://squoosh.app)), jakość ~80.
3. Nazwij pliki `01.jpg`, `02.jpg`, `03.jpg`… (kolejność = kolejność w galerii).
4. Wymyśl **slug** — krótką nazwę po angielsku bez polskich znaków, np.
   `sesja-rodzinna-krakow-zima`. Użyjesz jej dwa razy (folder i JSON).

### Krok 2 — wgraj zdjęcia

Na GitHubie: **Add file → Create new file** nie wgra zdjęć, więc użyj
**Add file → Upload files** w katalogu `public/images/galleries/`:

1. Wejdź w `public/images/galleries/`.
2. Kliknij **Add file → Upload files**.
3. Najpierw utwórz podfolder: w polu nazwy pliku wpisz
   `twoj-slug/01.jpg` (GitHub sam utworzy folder), wgraj `01.jpg`.
4. Powtórz dla pozostałych zdjęć — wszystkie w **jednym commicie**.

### Krok 3 — dodaj wpis do `src/data/galleries.json`

Otwórz `src/data/galleries.json` → ołówek. Na **początku** listy `"galleries": [`
dodaj nowy wpis (zwróć uwagę na przecinki między wpisami!):

```json
{
  "slug": "sesja-rodzinna-krakow-zima",
  "title": "Rodzinna zimą w Krakowie",
  "category": "Sesje rodzinne",
  "date": "2026-10-05",
  "cover": "images/galleries/sesja-rodzinna-krakow-zima/01.jpg",
  "excerpt": "Krótki, jeden-dwa zdaniowy opis, który widać na kafelku galerii.",
  "photos": 6
}
```

Co oznaczają pola:

- **slug** — nazwa folderu ze zdjęciami i adres strony (…/galerie/sesja-rodzinna-krakow-zima).
- **title** — tytuł widoczny na stronie (mogą być polskie znaki).
- **category** — jedna z: `Sesje rodzinne`, `Sesje dziecięce`, `Sesje kobiece`, `Sesje ciążowe`, `Sesje romantyczne`, `Sesje wizerunkowe`.
- **date** — format RRRR-MM-DD (ważne: sortowanie od najnowszych).
- **cover** — zdjęcie okładkowe, prawie zawsze `01.jpg`.
- **excerpt** — 1–2 zdania zachęty.
- **photos** — **liczba zdjęć** w folderze (musi się zgadzać, inaczej strona będzie kierować do nieistniejących zdjęć).

### Krok 4 — commit i sprawdzenie

**Commit changes** → odczekaj 2–3 min → wejdź na
`https://michalgazda.github.io/annamatejska.pl/galerie` → nowa galeria powinna być pierwsza.
Jeśli jej nie widać, patrz [Rozwiązywanie problemów](#7-rozwiązywanie-problemów).

---

## 3. Jak edytować istniejącą galerię

- **Zmiana opisu / tytułu / daty:** edytuj tylko jej wpis w `galleries.json`.
- **Dodanie zdjęć:** wgraj dodatkowe `07.jpg`, `08.jpg`… do jej folderu
  i **zwiększ pole `photos`** (np. z 6 na 8).
- **Zmiana okładki:** zmień `cover` na inny plik.
- **Usunięcie galerii:** usuń wpis z JSON-a (i najlepiej folder ze zdjęciami).

---

## 4. Jak dodać zdjęcia do Kadrowania

**Przez panel (zalecane):** zakładka **Kadrowania** w panelu `/admin/`.

- **Kadry** — dodaj kafelek: podpis, kategoria (wydarzenia/architektura/podroze),
  opcjonalnie szerszy kafelek, i zdjęcie wgrane przez bibliotekę Media.
- **Kategorie** — lista nazw; kolejność = kolejność na stronie. Nowa kategoria
  automatycznie dostaje własny przycisk filtra.
- Zdjęcie wgrane przez panel ma pierwszeństwo; jeśli go nie ma, strona użyje
  domyślnego pliku z folderu kategorii (kolejny numer `NN.jpg`).

**Ręcznie (fallback):** wymień pliki 1:1 w
`public/kadrowania/images/portfolio/<kategoria>/` (`01.jpg`–`04.jpg`) lub edytuj
`src/data/kadrowania.json` (kategorie + kadry). Hero podstrony:
`public/kadrowania/images/hero.jpg` (poziome), `manifesto.jpg` (pion 3:4).

---

## 5. Jak zmienić teksty na stronie głównej

- **Opisy sesji** (np. co wliczone, czas trwania): `src/data/services.json`.
- **Opinie:** `src/data/testimonials.json` — dodaj wpis z `text`, `name`, `session`.
- **Dane kontaktowe / social media:** `src/data/site.json`.

---

## 6. Zasady dobrych zdjęć (waga, wymiary, nazwy)

- Format **JPEG**, jakość ~80, dłuższy bok **max 1920 px**.
- Jeden zdjęciowy plik **do ~400 KB**. Mniej = szybsza strona = lepsza pozycja w Google.
- Nazwy: **tylko małe litery, cyfry i myślniki** — `01.jpg`, `02.jpg`. Bez spacji i polskich znaków (ą, ę, ł…) w nazwach plików.
- Hero Kadrowania: `public/kadrowania/images/hero.jpg` (poziome), `manifesto.jpg` (pionowe 3:4).
- Ważne: obecnie wiele zdjęć na stronie to **zaślepki (placeholdery)** —
  gdy będziesz mieć gotowe kadry, wymień je po prostu plik po pliku
  (ten sam folder, ta sama nazwa).

---

## 7. Rozwiązywanie problemów

**Nowa galeria nie pokazuje się**
→ najczęściej literówka w JSON: brak przecinka, cudzysłów, albo `photos` nie zgadza się z liczbą plików. GitHub pokazuje błąd walidacji przy commit — nie ignoruj go.

**Zdjęcie nie widać (rozwalona kafelka)**
→ sprawdź, czy ścieżka w `cover` odpowiada folderowi i nazwie pliku 1:1 (wielkość liter ma znaczenie!).

**Formularz nie wysyła maili**
→ Web3Forms/hCaptcha — to ustawienia poza repo; powiedz Michalowi.

**Zmieniłam tekst, a strona bez zmian**
→ odczekaj 3 min (deploy), potem odśwież z Ctrl+Shift+R (twardy refresh, czyszczenie cache).

---

*Instrukcja aktualna na: październik 2026. Pytania? Napisz do Michala 🙂*
