'use strict';
(function () {
  document.documentElement.classList.add('js');

  // Reveal the skip link for keyboard users only — programmatic focus (headless
  // browsers, in-page scripts) must not paint it over the wordmark.
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Tab' || e.key === 'Shift') document.documentElement.classList.add('kb');
  }, { once: true });

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

  // Scroll reveal — elements fade/slide in once when they enter the viewport
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if (reveals.length) {
    if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
      reveals.forEach(function (el) { io.observe(el); });
    } else {
      reveals.forEach(function (el) { el.classList.add('is-in'); });
    }
  }

  // Lightbox (for photo-grid gallery pages only)
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.photo-grid figure img, .portfolio-grid figure img'));
  var lbEl = null, lbImg = null, countEl = null;
  var cur = 0, lastFocus = null;

  function show(i) {
    if (!lbEl) return;
    cur = (i + imgs.length) % imgs.length;
    lbImg.src = imgs[cur].getAttribute('data-full') || imgs[cur].src.replace(/-thumb(\.[^.]+)$/i, '$1');
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

  // Manual horizontal sliders (opinions carousel + /albumy photo strip + season tiles):
  // arrows, drag-to-scroll with a mouse (touch scrolls natively), arrow keys.
  // Przewijanie animujemy sami (easeInOutCubic) — natywne `smooth` jest szarpnięciem,
  // a Ania prosiła o „bardziej płynne i delikatne”.
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function glide(track, target) {
    var max = track.scrollWidth - track.clientWidth;
    var left = Math.max(0, Math.min(max, target));
    if (reduceMotion) { track.scrollLeft = left; return; }
    var start = track.scrollLeft, dist = left - start;
    if (Math.abs(dist) < 1) return;
    var dur = Math.min(720, Math.max(340, Math.abs(dist) * 0.5));
    var t0 = null;
    track.classList.add('is-gliding');
    track.style.scrollBehavior = 'auto';
    function step(now) {
      if (t0 === null) t0 = now;
      var p = Math.min(1, (now - t0) / dur);
      var e = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
      track.scrollLeft = start + dist * e;
      if (p < 1) requestAnimationFrame(step);
      else { track.style.scrollBehavior = ''; track.classList.remove('is-gliding'); }
    }
    requestAnimationFrame(step);
  }

  function initSlider(track, prevSel, nextSel, slideSel, gapFallback) {
    if (!track) return;
    var step = function () {
      var slide = track.querySelector(slideSel);
      if (!slide) return track.clientWidth * 0.9;
      var gap = parseFloat(getComputedStyle(track).columnGap || gapFallback) || gapFallback;
      return slide.getBoundingClientRect().width + gap;
    };
    var prevBtn = document.querySelector(prevSel);
    var nextBtn = document.querySelector(nextSel);
    if (prevBtn) prevBtn.addEventListener('click', function () { glide(track, track.scrollLeft - step()); });
    if (nextBtn) nextBtn.addEventListener('click', function () { glide(track, track.scrollLeft + step()); });

    var down = false, startX = 0, startScroll = 0, moved = 0;
    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') return; // let the browser scroll natively with the finger
      down = true; moved = 0; startX = e.clientX; startScroll = track.scrollLeft;
      track.classList.add('is-dragging');
    });
    track.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      moved = Math.abs(dx);
      track.scrollLeft = startScroll - dx;
      if (moved > 4) e.preventDefault();
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (ev) {
      track.addEventListener(ev, function () {
        if (!down) return;
        down = false;
        track.classList.remove('is-dragging');
        glide(track, Math.round(track.scrollLeft / step()) * step());
      });
    });
    // keyboard support on the focused strip
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); glide(track, track.scrollLeft - step()); }
      if (e.key === 'ArrowRight') { e.preventDefault(); glide(track, track.scrollLeft + step()); }
    });

    // klasy dla CSS: czy jest co przewijać (no-scroll) i czy jesteśmy na początku / końcu
    var upd = function () {
      var max = track.scrollWidth - track.clientWidth;
      track.classList.toggle('no-scroll', max <= 4);
      track.classList.toggle('at-start', track.scrollLeft <= 4);
      track.classList.toggle('at-end', track.scrollLeft >= max - 8);
    };
    track.addEventListener('scroll', upd, { passive: true });
    window.addEventListener('resize', upd);
    upd();
  }

  initSlider(document.getElementById('opinie-track'), '.opinie-prev', '.opinie-next', '.opinie-card', 22);
  initSlider(document.getElementById('album-track'), '.album-prev', '.album-next', '.album-slide', 16);
  initSlider(document.getElementById('season-track'), '.season-prev', '.season-next', '.season-card', 16);

  // Contact form (Web3Forms)
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.querySelector('.form-status');
      var btn = form.querySelector('[type="submit"]');
      status.textContent = '';
      status.className = 'form-status';
      // hCaptcha: submit only with a token, otherwise the API answers
      // "Could not validate hCaptcha. Please try later".
      var token = form.querySelector('textarea[name="h-captcha-response"], textarea[name="g-recaptcha-response"]');
      if (form.querySelector('.h-captcha') && !(token && token.value)) {
        status.textContent = 'Najpierw potwierdź, że nie jesteś robotem (pole hCaptcha powyżej).';
        status.className = 'form-status is-error';
        return;
      }
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
            // token hCaptcha jest jednorazowy — po błędzie trzeba go odświeżyć
            if (window.hcaptcha && window.hcaptcha.reset) { try { window.hcaptcha.reset(); } catch (e) {} }
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