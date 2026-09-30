'use strict';
(function () {
  document.documentElement.classList.add('js');

  // Mobile menu
  var toggle = document.querySelector('.menu-toggle');
  var navLinks = document.querySelector('.nav-links');
  function closeMenu() {
    if (!navLinks) return;
    navLinks.classList.remove('open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    navLinks.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });
  }

  // Lightbox (for photo-grid gallery pages only)
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.photo-grid figure img'));
  var lbEl = null, lbImg = null, countEl = null;
  var cur = 0, lastFocus = null;

  function show(i) {
    if (!lbEl) return;
    cur = (i + imgs.length) % imgs.length;
    lbImg.src = imgs[cur].src.replace(/-thumb(\.[^.]+)$/i, '$1');
    lbImg.alt = imgs[cur].alt || 'Zdjęcie ' + (cur + 1);
    countEl.textContent = (cur + 1) + ' / ' + imgs.length;
    lbEl.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    if (!lbEl || !lbEl.classList.contains('open')) return;
    lbEl.classList.remove('open');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
    lastFocus = null;
  }

  if (imgs.length > 0) {
    lbEl = document.createElement('div');
    lbEl.className = 'lb';
    lbEl.setAttribute('role', 'dialog');
    lbEl.setAttribute('aria-modal', 'true');
    lbEl.setAttribute('aria-label', 'Podgląd zdjęć');
    lbEl.innerHTML =
      '<button class="lb-close" aria-label="Zamknij">✕</button>' +
      '<button class="lb-prev" aria-label="Poprzednie">‹</button>' +
      '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="">' +
      '<button class="lb-next" aria-label="Następne">›</button>' +
      '<div class="lb-count" aria-live="polite"></div>';
    document.body.appendChild(lbEl);
    lbImg = lbEl.querySelector('img');
    countEl = lbEl.querySelector('.lb-count');
    imgs.forEach(function (im, i) {
      var fig = im.parentElement;
      fig.setAttribute('tabindex', '0');
      fig.setAttribute('role', 'button');
      fig.setAttribute('aria-label', 'Powiększ zdjęcie: ' + (im.alt || 'zdjęcie ' + (i + 1)));
      function open() { lastFocus = fig; show(i); }
      fig.addEventListener('click', open);
      fig.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
      });
    });
    lbEl.querySelector('.lb-close').addEventListener('click', closeLightbox);
    lbEl.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(cur - 1); });
    lbEl.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
    lbEl.addEventListener('click', function (e) { if (e.target === lbEl) closeLightbox(); });
    // focus trap: cycle Tab within the dialog while open
    lbEl.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var focusables = [lbEl.querySelector('.lb-close'), lbEl.querySelector('.lb-prev'), lbEl.querySelector('.lb-next')];
      var idx = focusables.indexOf(document.activeElement);
      if (e.shiftKey && (idx === 0 || idx === -1)) { e.preventDefault(); focusables[focusables.length - 1].focus(); }
      else if (!e.shiftKey && idx === focusables.length - 1) { e.preventDefault(); focusables[0].focus(); }
    });
    // move focus into the dialog when it opens
    var origShow = show;
    show = function (i) { origShow(i); lbEl.querySelector('.lb-close').focus(); };
  }

  // Keyboard
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' && e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    if (e.key === 'Escape') {
      if (navLinks && navLinks.classList.contains('open')) closeMenu();
      else closeLightbox();
      return;
    }
    if (lbEl && lbEl.classList.contains('open')) {
      if (e.key === 'ArrowLeft') show(cur - 1);
      else if (e.key === 'ArrowRight') show(cur + 1);
    }
  });

  // Contact form (Web3Forms)
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
        .then(function (r) { return r.text(); })
        .then(function (text) {
          try { var res = JSON.parse(text); } catch(e) { res = { success: false, message: text }; }
          if (res.success) {
            status.textContent = 'Dziękuję! Wiadomość wysłana — odpowiem w ciągu 48 godzin.';
            status.className = 'form-status is-success';
            form.reset();
          } else {
            status.textContent = 'Błąd: ' + (res.message || 'nieznany');
            status.className = 'form-status is-error';
          }
        })
        .catch(function (err) {
          status.textContent = 'Błąd połączenia: ' + err.message;
          status.className = 'form-status is-error';
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = 'Wyślij zapytanie';
        });
    });
  }
})();