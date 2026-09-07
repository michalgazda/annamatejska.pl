# Panel zarządzania stroną — instrukcja dla Anny (PL)

## Gdzie jest panel?

Strona: **`twoja-domena.pl/panel.html`** → przycisk „Wejdź do panelu”
(bezpośrednio: `/admin/`).

Logowanie kontem GitHub (założymy je przy konfiguracji — zajmie 5 minut,
poprowadzę krok po kroku).

## Co możesz robić w panelu?

### 📷 Galerie
- Dodaj nową galerię: podaj tytuł, kategorię, datę, krótki opis
  i **wgraj zdjęcia** (przycisk „upload” w panelu).
- Zmiana kolejności: przeciągnij galerię na liście.
- Po zapisaniu strona główna i katalog `galerie.html` odświeżą się same.

### 📝 Opinie
- Dodaj / edytuj / usuwaj opinie klientek i klientów.
- Sekcja „Opinie” na stronie głównej aktualizuje się automatycznie.

### 🌿 Oferta (sesje)
- Edytuj **wszystkie teksty** każdej sesji: tytuł, lead, opis (akapity),
  czas trwania, „zawsze w cenie”, cytat klienta.
- Zmień zdjęcie kafelka na stronie głównej lub krótkie teksty kafelka.
- Ukryj sesję z oferty (przełącznik „Widoczna w ofercie”) — strona zniknie
  z menu i strony głównej, ale plik zostanie.

## Jak to działa „pod maską”?

Panel (Decap CMS) edytuje pliki JSON w repozytorium:
- `data/galleries.json` — galerie
- `data/testimonials.json` — opinie
- `data/services.json` — oferta

Po kliknięciu „Zapisz” (publish) powstaje commit na GitHubie, a system
hostingowy automatycznie uruchamia generatory (`tools/build-*.py`), które
odświeżają stronę HTML. Nie musisz niczego instalować ani ruszać kodem.

## Zdjęcia

- Wgraj pliki prosto z telefonu/komputera — panel sam umieści je w
  `images/uploads/`.
- Najlepiej JPEG, dłuższa strona ≥ 2000 px. Panel nie przeskaluje zdjęć,
  więc bardzo duże pliki warto zmniejszyć przed wgraniem (albo poprosimy
  o automat optymalizujący — do ustalenia).

## Bezpieczeństwo

- Panel jest ukryty przed Google (`noindex`).
- Dostęp tylko po zalogowaniu; hasło nie jest zapisane na stronie.
- Każda zmiana jest wersjonowana na GitHubie — można cofnąć dowolną
  zmianę jednym kliknięciem.
