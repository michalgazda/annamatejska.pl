#!/usr/bin/env python3
"""End-to-end render + behaviour check for annamatejska.pl (Playwright, headless).

Optional QA tool — requires a local server and Playwright's Chromium:

    # 1. serve the site (either of these):
    docker compose up -d --build          # -> http://127.0.0.1:8890
    # or:  python3 -m http.server 8890
    # 2. run the check:
    python3 tools/qa-check.py             # uses http://127.0.0.1:8890
    QA_URL=http://localhost:8088 python3 tools/qa-check.py   # override

First time only (installs headless Chromium):
    python3 -m playwright install chromium

Checks every page for broken images, console errors, mobile-menu behaviour and
the lightbox (open / navigate / Escape-to-close). Exits non-zero on any failure.
"""
import os
import sys

BASE = os.environ.get("QA_URL", "http://127.0.0.1:8890")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("Playwright is not installed in this interpreter.\n"
             "Run:  python3 -m playwright install chromium\n"
             "(or run this script with the interpreter that has it)")
PAGES = ["/", "/galerie.html", "/kontakt.html",
         "/sesje/rodzinne.html", "/sesje/kobiece.html", "/sesje/ciazowe.html",
         "/galerie/sesja-rodzinna-kopiec-kraka.html",
         "/galerie/sesja-rodzinna-ogrod-botaniczny.html",
         "/galerie/sesja-kobieca-studio-czyzyny.html",
         "/galerie/sesja-ciazowa-wawel.html",
         "/galerie/sesja-romantyczna-wisl-zmierzch.html",
         "/galerie/sesja-wizerunkowa-biznes-portret.html"]

failures = []

def check(page_url, name, p):
    # collect console errors across the whole page life
    errors = []
    def on_console(m):
        if m.type == "error":
            errors.append(m.text)
    p.on("console", on_console)
    # force mobile viewport so the menu toggle is visible
    p.set_viewport_size({"width": 390, "height": 800})
    p.goto(page_url, wait_until="networkidle")

    # broken images — scroll the whole page first so loading="lazy" images load
    p.eval_on_selector_all("img", "els => els.forEach(i => i.loading = 'eager')")
    p.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    p.wait_for_timeout(400)
    p.evaluate("window.scrollTo(0, 0)")
    broken = p.eval_on_selector_all(
        "img",
        "els => els.filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src)")
    for b in broken:
        failures.append(f"[{name}] broken image: {b}")

    # mobile nav behaviour (toggle is display:none until <960px)
    has_toggle = p.query_selector(".menu-toggle")
    if has_toggle:
        p.set_viewport_size({"width": 390, "height": 800})
        toggle = p.query_selector(".menu-toggle")
        toggle.click()
        opened = p.eval_on_selector(".nav-links", "el => el.classList.contains('open')")
        if not opened:
            failures.append(f"[{name}] mobile menu did not open on toggle")
        # tap a nav link -> should close
        link = p.query_selector(".nav-links a")
        if link:
            link.click()
            closed = p.eval_on_selector(".nav-links", "el => !el.classList.contains('open')")
            if not closed:
                failures.append(f"[{name}] mobile menu did not close after tapping a link")
    # lightbox (gallery pages only)
    if "/galerie/" in page_url:
        tile = p.query_selector(".photo-grid figure img")
        if tile:
            tile.click()
            p.wait_for_timeout(250)
            lb_open = p.eval_on_selector(".lb", "el => el.classList.contains('open')")
            if not lb_open:
                failures.append(f"[{name}] lightbox did not open on tile click")
            count_txt = p.eval_on_selector(".lb-count", "el => el.textContent")
            if not (count_txt and "/" in count_txt):
                failures.append(f"[{name}] lightbox count missing: {count_txt!r}")
            # navigate next
            p.click(".lb-next")
            p.wait_for_timeout(150)
            # close via Escape
            p.keyboard.press("Escape")
            p.wait_for_timeout(150)
            still_open = p.eval_on_selector(".lb", "el => el.classList.contains('open')")
            if still_open:
                failures.append(f"[{name}] lightbox did not close on Escape")

    # record console errors captured for this page, then detach the listener
    for m in errors:
        failures.append(f"[{name}] console error: {m}")
    p.remove_listener("console", on_console)

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        for path in PAGES:
            name = path.strip("/") or "index"
            check(BASE + path, name, page)
        browser.close()
    if failures:
        print(f"FAIL — {len(failures)} problem(s):")
        for f in failures:
            print("  ✗", f)
        sys.exit(1)
    print(f"PASS — {len(PAGES)} pages checked: no broken images, no console errors, "
          f"mobile nav + lightbox OK")

if __name__ == "__main__":
    main()
