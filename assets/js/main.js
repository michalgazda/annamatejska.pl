/* Anna Matejska-Gazda Fotografia — shared behaviour: nav, reveal-on-scroll, lightbox */
(function () {
  document.documentElement.classList.add('js');
  // mobile menu
  var t = document.querySelector('.menu-toggle');
  if (t) t.addEventListener('click', function () {
    document.querySelector('.nav-links').classList.toggle('open');
  });

  // lightbox — works on any .photo-grid figure > img
  var imgs = Array.prototype.slice.call(document.querySelectorAll('.photo-grid figure img'));
  if (imgs.length === 0) return;

  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.innerHTML =
    '<button class="lb-close" aria-label="Zamknij">✕</button>' +
    '<button class="lb-prev" aria-label="Poprzednie">‹</button>' +
    '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="">' +
    '<button class="lb-next" aria-label="Następne">›</button>' +
    '<div class="lb-count"></div>';
  document.body.appendChild(lb);

  var cur = 0, lbImg = lb.querySelector('img'), count = lb.querySelector('.lb-count');

  function show(i) {
    cur = (i + imgs.length) % imgs.length;
    // prefer full-size variant if a -thumb file exists alongside
    var full = imgs[cur].src.replace(/-thumb(\.\w+)$/i, '$1');
    lbImg.src = full;
    count.textContent = (cur + 1) + ' / ' + imgs.length;
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function close() { lb.classList.remove('open'); document.body.style.overflow = ''; }

  imgs.forEach(function (im, i) { im.parentElement.addEventListener('click', function () { show(i); }); });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(cur - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(cur + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(cur - 1);
    if (e.key === 'ArrowRight') show(cur + 1);
  });
})();
