(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.menu-toggle');
  var items = document.querySelectorAll('.nav-item.has-dropdown');
  var desktop = window.matchMedia('(min-width: 1081px)');

  function onScroll() {
    if (header) header.classList.toggle('is-scrolled', window.scrollY > 8);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  function closeAll(except) {
    items.forEach(function (item) {
      if (item !== except) {
        item.classList.remove('open');
        var b = item.querySelector('.nav-link');
        if (b) b.setAttribute('aria-expanded', 'false');
      }
    });
  }

  items.forEach(function (item) {
    var btn = item.querySelector('.nav-link');
    var timer;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = !item.classList.contains('open');
      closeAll(item);
      item.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
    item.addEventListener('mouseenter', function () {
      if (!desktop.matches) return;
      clearTimeout(timer);
      closeAll(item);
      item.classList.add('open');
      btn.setAttribute('aria-expanded', 'true');
    });
    item.addEventListener('mouseleave', function () {
      if (!desktop.matches) return;
      timer = setTimeout(function () {
        item.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }, 150);
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item')) closeAll();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAll();
      if (document.body.classList.contains('nav-open')) setMenu(false);
    }
  });

  function setMenu(open) {
    document.body.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    toggle.querySelector('.icon-open').style.display = open ? 'none' : '';
    toggle.querySelector('.icon-close').style.display = open ? '' : 'none';
  }
  if (toggle) {
    toggle.addEventListener('click', function () {
      setMenu(!document.body.classList.contains('nav-open'));
    });
    desktop.addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }

  var year = document.querySelector('[data-year]');
  if (year) year.textContent = new Date().getFullYear();

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
  }
})();
