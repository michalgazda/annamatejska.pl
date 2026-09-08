'use strict';
(function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open);
    });
  }

  // Reveal on scroll
  var reveals = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
  if (reveals.length > 0) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    reveals.forEach(function (el) { observer.observe(el); });
  }

  // Image lazy load (fade-in for portfolio tiles)
  var tiles = Array.prototype.slice.call(document.querySelectorAll('.tile img'));
  tiles.forEach(function (img) {
    if (img.complete) { img.classList.add('is-loaded'); }
    else { img.addEventListener('load', function () { img.classList.add('is-loaded'); }); }
  });

  // Portfolio filter
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll('.filter__btn'));
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-cat]'));
  if (filterBtns.length > 0) {
    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterBtns.forEach(function (b) { b.classList.remove('is-active'); b.setAttribute('aria-pressed', 'false'); });
        btn.classList.add('is-active'); btn.setAttribute('aria-pressed', 'true');
        var filter = btn.getAttribute('data-filter');
        items.forEach(function (item) {
          if (filter === '*' || item.getAttribute('data-cat') === filter) {
            item.classList.remove('is-hidden');
          } else {
            item.classList.add('is-hidden');
          }
        });
      });
    });
  }

  // Contact form (Web3Forms) — same pattern as main site
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.querySelector('.form__status');
      var btn = form.querySelector('[type="submit"]');
      status.textContent = '';
      status.className = 'form__status';
      btn.disabled = true;
      btn.textContent = 'Wysyłanie…';
      var data = new FormData(form);
      fetch(form.action, { method: 'POST', body: data })
        .then(function (r) { return r.text(); })
        .then(function (text) {
          try { var res = JSON.parse(text); } catch(e) { res = { success: false, message: text }; }
          if (res.success) {
            status.textContent = 'Dziękuję! Wiadomość wysłana — odpowiem w ciągu 48 godzin.';
            status.className = 'form__status is-success';
            form.reset();
          } else {
            status.textContent = 'Błąd: ' + (res.message || 'nieznany');
            status.className = 'form__status is-error';
          }
        })
        .catch(function (err) {
          status.textContent = 'Błąd połączenia: ' + err.message;
          status.className = 'form__status is-error';
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = 'Wyślij wiadomość';
        });
    });
  }
})();