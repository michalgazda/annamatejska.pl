#!/usr/bin/env bash
# Wrzutnia zdjęć → strona: synchronizacja z Google Drive i publikacja, jeśli coś przyszło.
#
#   1. tools/gallery-sync.mjs — pobiera zdjęcia z folderu Drive, sprawdza limity,
#      optymalizuje, wpisuje galerię do src/data/*.json (i raport w docs/ + na Drive)
#   2. jeśli coś się zmieniło: npm run build + npm run validate, commit, push na main
#      (GitHub Pages publikuje stronę automatyzmem repo)
#
# Wyjście: "BRAK_NOWYCH_ZDJEC" albo "OPUBLIKOWANO" / błąd (nic nie wypycha przy błędzie).
set -euo pipefail
cd "$(dirname "$0")/.."

node tools/gallery-sync.mjs

WATCH=(src/data public/images docs/gallery-sync-report.md tools/gallery-sync.state.json)
if [ -z "$(git status --porcelain -- "${WATCH[@]}")" ]; then
  echo "BRAK_NOWYCH_ZDJEC"
  exit 0
fi

npm run build
npm run validate

git add -A -- "${WATCH[@]}"
git -c user.name="Hermes (wrzutnia zdjęć)" -c user.email="hermichalg@gmail.com" \
    commit -q -m "galeria: zdjęcia z wrzutni Anny ($(date +%Y-%m-%d))"
if [ "${DRY_PUSH:-0}" = "1" ]; then
  echo "OPUBLIKOWANO (dry-push — commit lokalny, bez push) $(git log --oneline -1)"
else
  git push -q origin main
  echo "OPUBLIKOWANO $(git log --oneline -1)"
fi
