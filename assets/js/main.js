/* Anna Matejska-Gazda Fotografia — shared behaviour: nav + lightbox */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  // ---------- mobile menu ----------
  var toggle = document.querySelector('.menu-toggle');
  var navLinks = document.querySelector('.nav-links');
  var menuOpen = function () { return navLinks && navLinks.classList.contains('open'); };
  var closeMenu = function () {
    if (!navLinks || !menuOpen()) return;
    navLinks.classList.remove('open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  };

  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close the panel as soon as the visitor picks a link, so it never stays
    // open over the content (matters for same-page anchors like #o-mnie).
    navLinks.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });
  }

  // ---------- lightbox (any .photo-grid figure > img) ----------
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.photo-grid figure img'));
  var lb = null, lbImg = null, count = null;
  var cur = 0, lastFocus = null;

  function show(i) {
    if (!lb) return;
    cur = (i + imgs.length) % imgs.length;
    // Prefer the full-size variant when a -thumb file is used in the grid.
    lbImg.src = imgs[cur].src.replace(/-thumb(\.\w+)$/i, '$1');
    lbImg.alt = imgs[cur].alt || 'Zdjęcie ' + (cur + 1);
    count.textContent = (cur + 1) + ' / ' + imgs.length;
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    if (!lb || !lb.classList.contains('open')) return;
    lb.classList.remove('open');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus(); // return focus to the tile
    lastFocus = null;
  }

  if (imgs.length > 0) {
    lb = document.createElement('div');
    lb.className = 'lb';
    lb.setAttribute('role', 'dialog');
    lb.setAttribute('aria-modal', 'true');
    lb.setAttribute('aria-label', 'Podgląd zdjęć');
    lb.innerHTML =
      '<button class="lb-close" aria-label="Zamknij">✕</button>' +
      '<button class="lb-prev" aria-label="Poprzednie">‹</button>' +
      '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="">' +
      '<button class="lb-next" aria-label="Następne">›</button>' +
      '<div class="lb-count"></div>';
    document.body.appendChild(lb);

    lbImg = lb.querySelector('img');
    count = lb.querySelector('.lb-count');

    imgs.forEach(function (im, i) {
      im.parentElement.addEventListener('click', function () {
        lastFocus = im.parentElement;
        show(i);
      });
    });
    lb.querySelector('.lb-close').addEventListener('click', closeLightbox);
    lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(cur - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLightbox(); });
  }

  // ---------- keyboard (menu + lightbox share one handler) ----------
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' && e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    if (e.key === 'Escape') {
      if (menuOpen()) closeMenu();
      else closeLightbox();
      return;
    }
    if (lb && lb.classList.contains('open')) {
      if (e.key === 'ArrowLeft') show(cur - 1);
      else if (e.key === 'ArrowRight') show(cur + 1);
    }
  });

  // ---------- contact form (Web3Forms) ----------
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.querySelector('.form-status');
      var btn = form.querySelector('[type="submit"]');
      status.textContent = '';
      status.className = 'form-status';
      btn.disabled = true;
      btn.textContent = 'Wysyłanie…';
      var data = new FormData(form);
      fetch(form.action, { method: 'POST', body: data })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.success) {
            status.textContent = 'Dziękuję! Wiadomość wysłana — odpowiem w ciągu 48 godzin.';
            status.className = 'form-status is-success';
            form.reset();
          } else {
            status.textContent = 'Coś poszło nie tak. Spróbuj ponownie lub napisz bezpośrednio na maila.';
            status.className = 'form-status is-error';
          }
        })
        .catch(function () {
          status.textContent = 'Błąd połączenia. Spróbuj ponownie lub napisz na maila.';
          status.className = 'form-status is-error';
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = 'Wyślij zapytanie';
        });
    });
  }
})();
