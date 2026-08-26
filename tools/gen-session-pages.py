#!/usr/bin/env python3
"""One-off generator for the 6 session landing pages (sesje/*.html)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SESSIONS = {
 "rodzinne": ("Sesje rodzinne", "Sesja rodzinna Kraków – naturalne zdjęcia | Anna Matejska-Gazda",
  "Rodzinne zdjęcia nie muszą być idealne. Wystarczy, że będą Wasze.",
  ["Tu nie chodzi o równe uśmiechy i patrzenie prosto w obiektyw. Chodzi bardziej o opadający kosmyk włosów i spojrzenie pełne czułości. O małe paluszki trzymające się dłoni rodzica. O ten śmiech, kiedy ktoś kogoś łaskocze.",
   "Podczas sesji daję Wam przestrzeń na bycie razem. Możecie spacerować, bawić się, wygłupiać. Ja obserwuję i łapię momenty, które dzieją się pomiędzy."],
  "ok. 1,5 h",
  "„Robimy sesję rodzinną u Ani już kolejny raz. Ania elastycznie podeszła do terminu, wybrała idealne miejsce, pomogła w doborze strojów dla całej naszej rodziny. Sama sesja przebiegła w bardzo przyjaznej atmosferze, a efekt przeszedł nasze oczekiwania!” — Aneta Hoły"),
 "dzieciece": ("Sesje dziecięce", "Sesja dziecięca Kraków – zabawa, nie pozowanie | Anna Matejska-Gazda",
  "Obawiasz się, że Twoje dziecko nie będzie chciało współpracować? Spokojnie — podczas sesji przede wszystkim… się bawimy!",
  ["Jestem mamą dwójki małych dzieci i wiem z doświadczenia, kiedy wychodzą najlepsze i najbardziej prawdziwe kadry — te, do których wraca się latami ze wzruszeniem.",
   "Najczęściej umawiamy się w plenerze: jest przestrzeń do biegania, skakania i dziecięcych zabaw. Sesje tematyczne (roczkowe, świąteczne, Dzień Babci…) wykonuję też w moim domowym studiu (Kraków–Czyżyny) lub w Waszym domu.",
   "Sezonowe plenery: kwitnący sad (marzec–kwiecień), pole maków (maj), lawenda (lipiec), farma kwiatowa (sierpień), farma dyniowa (wrzesień–październik)."],
  "1–1,5 h",
  "„Wszystko przebiegało swobodnie, bez presji pozowania, były zabawy i wygłupy z córeczkami, a Ania uchwyciła to wszystko w piękne kadry!” — Paulina Noszczyk"),
 "kobiece": ("Sesje kobiece", "Sesja kobieca Kraków | Anna Matejska-Gazda Fotograf",
  "Jaka sesja fotograficzna Ci się marzy? Najważniejsze — żebyś Ty czuła się dobrze.",
  ["Lekkie i delikatne kobiece kadry w plenerze? Bardziej nastrojowe w studio? A może całkiem formalne, biznesowe portrety?",
   "Jeśli nigdy wcześniej nie uczestniczyłaś w takiej sesji — pokieruję Cię, zaproponuję pozy albo będziemy wspólnie eksperymentować z kadrami, żeby podkreślić to, co w Tobie piękne i wyjątkowe.",
   "Najważniejsze — żebyś Ty czuła się dobrze."],
  "1,5–2 h",
  "„Efekty sesji przerosły moje oczekiwania — różnorodne stylizacje, ciekawe kadry, niepowtarzalny klimat… Znajomi podkreślali, że Ani udało się uchwycić MNIE — dokładnie taką, jaka jestem.” — Agnieszka Krawczyk"),
 "ciazowe": ("Sesje ciążowe", "Sesja ciążowa Kraków | Anna Matejska-Gazda Fotograf",
  "Zachować ten wyjątkowy czas na zdjęciach i pokazywać później swoim dzieciom — bezcenne.",
  ["Gładka cera, gęste włosy, brzuszek z bijącym w środku serduszkiem i ta niepowtarzalna radość w oczach.",
   "Sesję najlepiej wykonać między 28. a 34. tygodniem ciąży — dolegliwości pierwszego trymestru zwykle już minęły, brzuch jest pięknie widoczny, a Ty nie jesteś jeszcze zmęczona. Inne terminy oczywiście też są możliwe.",
   "Możesz przyjść sama, z mężem/partnerem lub z dziećmi. Sesję wykonuję w plenerze, w moim studio lub u Ciebie w domu."],
  "1–1,5 h",
  "„Mamy piękną pamiątkę sesji ciążowej, dziś pozdrawiamy już we trójkę!” — Natalia Zaklikiewicz"),
 "romantyczne": ("Sesje romantyczne", "Sesja romantyczna dla par – Kraków | Anna Matejska-Gazda",
  "Czy sesja zdjęciowa może być randką? Moim zdaniem tak.",
  ["Jeśli chcecie mieć piękne kadry, ale nie lubicie pozować — ta sesja jest zdecydowanie dla Was.",
   "Umawiamy się w plenerze, w wybranym wspólnie miejscu. Jest czas na spacer, rozmowy czy przytulanie. Ja jestem obok z aparatem — łapię Wasze uśmiechy, spojrzenia, splecione dłonie.",
   "Autorka projektu społecznego „Małżeństwo w kadrze” (2023)."],
  "ok. 1 h",
  "„Po sesji dostaliśmy do wyboru wiele ciekawych zdjęć. Gorąco polecamy Anię za profesjonalizm oraz ciepłe usposobienie, które sprawia, że sesje są naturalne i pełne unikalnego uroku.” — Anna i Paweł Basisty"),
 "wizerunkowe": ("Sesje wizerunkowe", "Sesja wizerunkowa i biznesowa Kraków | Anna Matejska-Gazda",
  "Twój wizerunek to coś więcej niż zdjęcie — to opowieść o tym, kim jesteś.",
  ["Tworzysz markę osobistą, prowadzisz małą firmę, potrzebujesz profesjonalnych portretów do mediów społecznościowych? Zadbam o to, by kadry były kreatywne i spójne z Tobą.",
   "Przed spotkaniem rozmawiamy o tym, czym się zajmujesz i jak chcesz być odbierana. Wspólnie wybieramy miejsce, styl i detale. Podczas sesji prowadzę Cię tak, żebyś czuła się naturalnie i swobodnie."],
  "1–2 h",
  "„Anna ma bardzo profesjonalne, a zarazem delikatne podejście do klientów. Słucha i obserwuje, by wyczuć potrzeby i styl. Serdecznie polecam, dobry czas i świetne zdjęcia!” — Maria Arkuszewska"),
}

TPL = """<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_tag}</title>
<meta name="description" content="{meta}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Jost:wght@300;400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
<header>
  <nav class="nav">
    <a class="brand" href="../index.html">Anna Matejska<em>-Gazda</em></a>
    <button class="menu-toggle" aria-label="Menu">&#9776;</button>
    <div class="nav-links">
      <a href="../index.html#o-mnie">O mnie</a>
      <a href="../index.html#sesje">Sesje</a>
      <a href="../galerie.html">Galerie</a>
      <a href="../index.html#opinie">Opinie</a>
      <a href="../kontakt.html" class="btn">Umów sesję</a>
    </div>
  </nav>
</header>

<section class="page-hero">
  <div class="container gal-meta">
    <span class="kicker">{cat} &middot; Kraków i okolice</span>
    <h1>{heading}</h1>
    <p>{lede}</p>
  </div>
</section>

<section style="padding-top:0">
  <div class="container" style="max-width:820px">
{paras}
    <div style="display:flex;gap:40px;flex-wrap:wrap;margin-top:36px;padding:26px 32px;border:1px solid var(--line);border-radius:3px;background:var(--white)">
      <div><span class="kicker" style="margin-bottom:.3rem">Czas trwania</span><strong style="font-family:var(--serif);font-size:1.5rem;font-weight:500">{dur}</strong></div>
      <div style="flex:1;min-width:240px"><span class="kicker" style="margin-bottom:.3rem">Zawsze w cenie</span><span style="color:var(--ink-soft);font-size:.92rem">kawa i rozmowa przed sesją &middot; pomoc w doborze strojów i miejsca &middot; selekcja oraz retusz zdjęć &middot; galeria online</span></div>
    </div>
    <blockquote style="font-family:var(--serif);font-style:italic;font-size:1.35rem;line-height:1.6;color:var(--ink-soft);border-left:2px solid var(--taupe);padding-left:24px;margin:52px 0">{testi}</blockquote>
    <p style="text-align:center;margin-top:44px"><a class="btn btn-taupe" href="../kontakt.html">Umów tę sesję</a></p>
  </div>
</section>

<footer class="site">
  <div class="container">
    <span>&copy; 2026 Anna Matejska-Gazda Fotografia &middot; Kraków</span>
    <span><a href="https://www.instagram.com/annamatejska.fotografia/">Instagram</a> &middot; <a href="https://www.facebook.com/annamatejska.fotografia">Facebook</a></span>
  </div>
</footer>
<script src="../assets/js/main.js"></script>
</body>
</html>
"""

def main():
    sdir = ROOT / "sesje"; sdir.mkdir(exist_ok=True)
    for slug, (cat, title_tag, meta, paras, dur, testi) in SESSIONS.items():
        heading = cat.capitalize()
        lede = paras[0] if False else meta  # first sentence as hero lede
        body = "\n".join(
            f'    <p style="color:var(--ink-soft);margin-bottom:1rem">{p}</p>' for p in paras)
        page = TPL.format(title_tag=title_tag, meta=meta, cat=cat, heading=heading,
                          lede=lede, paras=body, dur=dur, testi=testi)
        (sdir / f"{slug}.html").write_text(page, encoding="utf-8")
        print("wrote", f"sesje/{slug}.html")

if __name__ == "__main__":
    main()
