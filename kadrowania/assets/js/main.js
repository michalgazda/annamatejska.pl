/* main.js -- vanilla-JS micro-interactions for the kadrowania site.
 * No dependencies; everything degrades gracefully without JS.
 */
(function () {
  "use strict";

  var prefersReduced = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  /* ---------- Reveal-on-scroll: sections and tiles fade up ---------- */
  function initReveals() {
    var items = document.querySelectorAll("[data-reveal]");
    if (!("IntersectionObserver" in window) || prefersReduced) {
      items.forEach(function (el) {
        el.classList.add("is-visible");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    items.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ---------- Hero: (layout is now a side-by-side grid; parallax disabled
   * to keep the image clean. Left as a no-op hook for future use.) ---------- */
  function initHeroParallax() {
    return;
  }

  /* ---------- Header: solid background once scrolled ---------- */
  function initHeader() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Mobile navigation toggle ---------- */
  function initNavToggle() {
    var btn = document.querySelector(".nav-toggle");
    var nav = document.querySelector(".site-nav");
    if (!btn || !nav) return;
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.classList.toggle("is-open", open);
    });
    // Close the menu after tapping a link.
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("is-open");
        btn.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Portfolio filter buttons ---------- */
  function initFilter() {
    var buttons = document.querySelectorAll(".filter__btn");
    var tiles = document.querySelectorAll(".portfolio-grid__item");
    if (!buttons.length || !tiles.length) return;
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var cat = btn.getAttribute("data-filter");
        buttons.forEach(function (b) {
          b.classList.toggle("is-active", b === btn);
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        tiles.forEach(function (tile) {
          var show = cat === "*" || tile.getAttribute("data-cat") === cat;
          tile.classList.toggle("is-hidden", !show);
          if (show) {
            // Re-trigger the fade-in so the grid re-composes gracefully.
            tile.classList.remove("is-visible");
            void tile.offsetWidth; /* force reflow to restart transition */
            tile.classList.add("is-visible");
          }
        });
      });
    });
  }

  /* ---------- Slow image reveal inside tiles (frame-by-frame feel) ---------- */
  function initTileImageLoad() {
    document.querySelectorAll(".tile img").forEach(function (img) {
      if (img.complete && img.naturalWidth > 0) {
        img.classList.add("is-loaded");
      } else {
        img.addEventListener("load", function () {
          img.classList.add("is-loaded");
        });
      }
    });
  }

  /* ---------- Copyright year ---------- */
  function initYear() {
    var el = document.getElementById("year");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  /* ---------- Contact form (Web3Forms) ---------- */
  function initForm() {
    var form = document.getElementById("contact-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".form__status");
      var btn = form.querySelector(".form__submit");
      status.textContent = "";
      status.className = "form__status";
      btn.disabled = true;
      btn.textContent = "Wysyłanie…";
      var data = new FormData(form);
      fetch(form.action, { method: "POST", body: data })
        .then(function (r) { return r.text(); })
        .then(function (text) {
          console.log("Web3Forms response:", text);
          try { var res = JSON.parse(text); } catch(e) { res = { success: false, message: text }; }
          if (res.success) {
            status.textContent = "Dziękuję! Wiadomość wysłana — odpowiem w ciągu 48 godzin.";
            status.className = "form__status is-success";
            form.reset();
          } else {
            status.textContent = "Błąd: " + (res.message || "nieznany");
            status.className = "form__status is-error";
          }
        })
        .catch(function (err) {
          status.textContent = "Błąd połączenia: " + err.message;
          status.className = "form__status is-error";
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = "Wyślij wiadomość";
        });
    });
  }

  function init() {
    initReveals();
    initHeroParallax();
    initHeader();
    initNavToggle();
    initFilter();
    initTileImageLoad();
    initYear();
    initForm();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
