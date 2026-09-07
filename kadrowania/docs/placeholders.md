# Placeholdery `kadrowania/` — jak działają i jak je zastąpić

## Po co w ogóle placeholdery?

Strona ma wypełnioną siatkę portfolio i hero jeszcze zanim Anna wrzuci
swoje własne zdjęcia. Generator produkuje jasne, miękkie, czarno-białe
obrazy — nie przyciągają uwagi, nie "wołają" o treść, po prostu pokazują
układ strony.

Każde zdjęcie ma tę samą orientację i proporcje, co docelowa fotka, więc
layout nie "skacze" przy podmianie.

## Jak działają

Plik `tools/make-placeholders.py` (Python, wymaga PIL/Pillow):

```
python3 tools/make-placeholders.py
# → zapisuje 14 plików JPG do images/
```

Dla każdej kategorii losuje miękkie gradienty, kilka rozmytych "plam"
świetlnych, delikatne ziarno i subtelną winietę. Żaden placeholder nie
wygląda jak realne zdjęcie — ma być neutralnym wypełniaczem, a nie
udawać treść.

Generowanie ma ziarno deterministyczne: **kolejne uruchomienie produkuje
te same pliki** (dopóki nie zmienisz kodu).

## Gdzie lądują

| Plik | Orientacja | Gdzie użyty |
|---|---|---|
| `images/hero.jpg` | pozioma ~4:3 | Sekcja hero (pierwszy widok) |
| `images/manifesto.jpg` | pionowa ~3:4 | Sekcja "Manifest" i "O mnie" |
| `images/portfolio/<kategoria>/01.jpg` | pozioma | Siatka portfolio, pierwszy kadr |
| `images/portfolio/<kategoria>/02.jpg` | pionowa | Siatka portfolio, drugi kadr |
| `images/portfolio/<kategoria>/03.jpg` | pozioma | Siatka portfolio, trzeci kadr |
| `images/portfolio/<kategoria>/04.jpg` | pionowa | Siatka portfolio, czwarty kadr |

Kategorie (2026): **wydarzenia**, **architektura**, **podróże**.

## Jak zastąpić prawdziwymi zdjęciami

1. Wybierz zdjęcie i przeskaluj je — dłuższa krawędź ~1600 px, JPEG,
   jakość ~80. Nie musi być idealnie 4:3 — object-fit: cover wyrówna.
2. Zapisz pod tą samą ścieżką i nazwą pliku co placeholder.
3. (Opcjonalnie) zedytuj podpis i `alt` w `index.html` — każdy kadr ma
   swój `<h3 class="tile__title">` i `alt`.

Strona niczego nie przyciemnia (biały design), więc pilnuj, żeby zdjęcia
były odpowiednio naświetlone na jasnej stronie.

## Historia: skąd się wziął bug

Pierwotna (ciemna) wersja generatora miała w `vignette()` wzór:
`255 - int(v * strength)`, gdzie `strength` było losowane z zakresu 18–30.
Efekt: wszystkie placeholdery wychodziły prawie-czarne (mean jasności 2.2),
mimo że reszta kodu produkowała jasne gradienty. Naprawione na:
`int(255 - (255 - v) * strength)` ze `strength` w zakresie `[0.08, 0.16]` —
teraz przyciemnia tylko rogi, środek zachowuje jasność.