# Panel zarządzania stroną — instrukcja dla Anny (PL)

## Gdzie jest panel?

Adres: **`annamatejska.pl/admin/`** (lokalnie/testowo: `http://127.0.0.1:8890/admin/`).

Logowanie kontem GitHub (przycisk „Login with GitHub”). Jeśli nie masz konta
GitHub, Michal je założy i doda dostęp — zajmie 5 minut.

> **Status (październik 2026):** panel działa i pokazuje ekran logowania,
> ale logowanie GitHubem wymaga skonfigurowania autoryzacji OAuth
> (jednorazowa robota Michala — patrz `docs/tech-en/cms-setup.md`).

## Co możesz robić w panelu?

### 📷 Galerie
- Dodaj nową galerię: tytuł, kategoria, data, krótki opis, liczba zdjęć.
- Zdjęcia wgraj przez bibliotekę „Media” (panel sam je umieści w
  `images/uploads/`), a potem w polu galerii wybierz okładkę.
- Zmiana kolejności: przeciągnij galerię na liście (nowe wpisy dodają się na górze).

### 📝 Opinie
- Dodaj / edytuj / usuwaj opinie klientek i klientów.
- Sekcja „Opinie” na stronie głównej aktualizuje się po zapisaniu.

### 🌿 Oferta (sesje)
- Edytuj **wszystkie teksty** każdej sesji: tytuł, lead, opis (akapity),
  czas trwania, „zawsze w cenie”, cytat klienta.
- Zmień zdjęcie kafelka na stronie głównej lub krótkie teksty kafelka.
- Ukryj sesję z oferty (przełącznik „Widoczna w ofercie”).

### ⚙️ Ustawienia
- Telefon, e-mail, Instagram, Facebook, obszar działania — jedno miejsce,
  zmiana aktualizuje stopkę, stronę kontakt i dane dla Google.

## Jak zapisuje się zmiany?

Panel działa w trybie **przeglądu (editorial workflow)**:

1. Zmiany najpierw trafiają do zakładki **„Praca” (Workflow)** jako szkic.
2. W zakładce Workflow klikasz **„Publish”** — wtedy zmiana trafia na stronę.
3. GitHub buduje stronę na nowo (2–3 min) — odśwież z Ctrl+Shift+R.

Dzięki temu nic nie zopsuje się „przypadkiem” — każdą zmianę widać przed
publikacją, a historię można cofnąć na GitHubie.

## Zdjęcia

- Wgraj pliki prosto z telefonu/komputera — panel umieści je w `images/uploads/`.
- Format **JPEG**, jakość ~80, dłuższy bok **max 1920 px**, rozmiar do ~400 KB.
  Panel nie przeskaluje zdjęć automatycznie — duże pliki zmniejsz przed wgraniem
  (np. darmowym [Squoosh](https://squoosh.app)).
- Nazwy plików: małe litery, cyfry, myślniki — bez spacji i polskich znaków.

## Bezpieczeństwo

- Panel jest ukryty przed Google (`noindex`).
- Dostęp tylko po zalogowaniu GitHubem; uprawnienia: odczyt/zapis repozytorium.
- Każda zmiana jest wersjonowana — można cofnąć dowolną zmianę jednym kliknięciem.

## A gdy panel nie działa?

Zawsze można zmienić te same dane **ręcznie przez stronę GitHub** —
instrukcja: [docs/INSTRUKCJA-ANNA.md](../INSTRUKCJA-ANNA.md).

---

*Instrukcja aktualna: październik 2026.*
