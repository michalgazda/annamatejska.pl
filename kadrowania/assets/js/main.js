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

  /* ---------- Hero: slow, gentle parallax on the background photo ---------- */
  function initHeroParallax() {
    if (prefersReduced) return;
    var hero = document.querySelector(".hero");
    var img = document.querySelector(".hero__img");
    if (!hero || !img) return;
    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          var y = window.scrollY;
          if (y < window.innerHeight * 1.2) {
            // Translate at a fraction of scroll speed + subtle fade.
            img.style.transform = "translateY(" + y * 0.22 + "px) scale(1.06)";
            hero.style.setProperty("--hero-fade", String(Math.max(0, 1 - y / (window.innerHeight * 0.75))));
          }
          ticking = false;
        });
      },
      { passive: true }
    );
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

  function init() {
    initReveals();
    initHeroParallax();
    initHeader();
    initNavToggle();
    initFilter();
    initTileImageLoad();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
