# Wrzutnia zdjęć Anny — jak to działa

Zdjęcia do galerii na annamatejska.pl wrzucamy do **jednego folderu na Google Drive**,
z którego agent (Hermes) pobiera je, sprawdza, optymalizuje i podpina do repo.

## Przepływ

```
Google Drive: "annamatejska.pl — zdjęcia do galerii"
   └── Sesja rodzinna – Kowalscy (24.05.2026)/      <- podfolder = jedna galeria
          ├── 01.jpg … 24.jpg                        <- JPG-i z Lightrooma
          └── _meta.json  (opcjonalnie)              <- tytuł/opis/termin + gdzie podpiąć
                │
                ▼  npm run gallery:sync
   public/images/galleries/<slug>/NN.jpg + NN-thumb.jpg + cover.jpg
   src/data/galleries.json                 <- wpis galerii (+ photos_list)
   src/data/sesje.json / reportaze.json    <- podpięcie do sekcji (link z menu)
   docs/gallery-sync-report.md             <- raport (+ kopia na Drive)
```

## Użycie

```bash
npm run gallery:sync              # pełny przebieg: Drive → repo
npm run gallery:dry               # co by zrobił, bez zapisu
node tools/gallery-sync.mjs --local-dir ~/Pictures/test   # test bez Drive (lokalny katalog)
node tools/gallery-sync.mjs --allow-small                 # przyjmij też zdjęcia < 1600 px
node tools/gallery-sync.mjs --folder <FOLDER_ID>           # inny folder niż w configu
```

Po synchronizacji: `npm run build && npm run validate`, potem commit + push (deploy GH Pages).

## Reguły (tools/gallery-sync.config.json)

- dozwolone: JPG, PNG, WEBP, TIFF, AVIF (HEIC z iPhone'a **nie** — brak dekodera, odrzucane z komunikatem)
- długi bok **≥ 1600 px** (`minLongEdge`), plik **≤ 25 MB** (`rejectOverMB`)
- wynik: pełne zdjęcie 2400 px / jakość 82, miniatura 900 px / 78, **EXIF i GPS usuwane**
- `cover.jpg` (1600 px) powstaje z pierwszego zdjęcia galerii

Odrzucone pliki nie trafiają do repo, a powód ląduje w `docs/gallery-sync-report.md`
i w pliku `_RAPORT-synchronizacji.txt` w folderze na Drive (Anna widzi, co poprawić).

## `_meta.json` (w podfolderze sesji)

```json
{
  "title": "Sesja rodzinna w Ogrodzie Botanicznym – Kowalscy",
  "category": "Sesje",
  "date": "2026-05-24",
  "excerpt": "Rodzinna sesja plenerowa — kadry bez pozowania.",
  "link": { "type": "sesje", "session": "rodzinne" }
}
```

- `link.type`: `sesje` (+`session`: romantyczne, rodzinne, dzieciece, kobiece, ciazowe, wizerunkowe)
  albo `reportaze` (+`group`: tytuł grupy z `reportaze.json`, domyślnie pierwsza).
- Bez `link` galeria istnieje jako strona `/galerie/<slug>/`, ale **nikt na nią nie trafi** —
  raport wypisuje wtedy ostrzeżenie.
- `_meta.json` działa też bez nowych zdjęć: sam dopisany plik wystarczy, żeby poprawić tytuł
  i podpiąć galerię do sekcji.

## Idempotencja

`tools/gallery-sync.state.json` pamięta md5 każdego przetworzonego pliku. Kolejne przebiegi
pomijają to, co już jest, a numeracja (`NN.jpg`) kontynuuje się od najwyższego numeru w katalogu.
Jeśli JSON galerii rozjedzie się z plikami na dysku, sync odbuduje `photos_list` z katalogu.

## Wrzutnia — stan

- Folder Drive: `annamatejska.pl — zdjęcia do galerii`
  `https://drive.google.com/drive/folders/1XE4zHmcb6UAMwKb2B1ZJc1yb7OsLoo5q`
  (właściciel `hermichalg@gmail.com`, Anna `annamatejskagazda@gmail.com` = edytor),
  w środku `CZYTAJ-TO-PRZED-WRZUCENIEM-ZDJEC.txt` (instrukcja dla Anny)
- Publicznie (skrypt, jedna komenda): `./tools/gallery-sync-and-publish.sh`
  = sync → `npm run build` → `npm run validate` → commit → push na `main`.
  `DRY_PUSH=1` robi wszystko poza wypchnięciem (commit lokalny).
- Cron celowo NIE jest ustawiony (Michał: wrzutki będą sporadyczne) —
  uruchamiamy na żądanie, wtedy gdy Anna wrzuci zdjęcia.
- Raport po każdej synchronizacji: `docs/gallery-sync-report.md` + `_RAPORT-synchronizacji.txt` na Drive.
