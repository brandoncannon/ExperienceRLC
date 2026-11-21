/* Legacy 2026 page: tree rings, dotted globe, serving dots, count-up numbers. */
(function () {
  var root = document.querySelector('.lg');
  if (!root) return;
  var NS = 'http://www.w3.org/2000/svg';

  function rings(id, n) {
    var s = document.getElementById(id); if (!s) return;
    for (var i = 1; i <= n; i++) {
      var c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', 500 + Math.sin(i) * 3); c.setAttribute('cy', 500 + Math.cos(i) * 3);
      c.setAttribute('r', i * (480 / n) + Math.sin(i * 1.7) * 4);
      c.setAttribute('stroke-width', i % 5 === 0 ? 1.6 : .8);
      if (i === n - 2 || i === Math.round(n / 2)) c.setAttribute('class', 'hl');
      s.appendChild(c);
    }
  }
  rings('lgHeroRings', 26); rings('lgCloseRings', 22);

  // dotted globe; lit dots = top Bible Breakdown listening places (Buzzsprout)
  var g = document.getElementById('lgGlobe');
  if (g) {
    var ring = document.createElementNS(NS, 'circle');
    ring.setAttribute('cx', 100); ring.setAttribute('cy', 100); ring.setAttribute('r', 96); ring.setAttribute('class', 'ring'); g.appendChild(ring);
    var rot = -40;
    function proj(la, lo) {
      var L = (lo + rot) * Math.PI / 180, P = la * Math.PI / 180;
      return { x: 100 + 92 * Math.cos(P) * Math.sin(L), y: 100 - 92 * Math.sin(P), z: Math.cos(P) * Math.cos(L) };
    }
    for (var la = -80; la <= 80; la += 7) {
      var step = 7 / Math.max(.2, Math.cos(la * Math.PI / 180));
      for (var lo = -180; lo < 180; lo += step) {
        var p = proj(la, lo); if (p.z < 0) continue;
        var d = document.createElementNS(NS, 'circle');
        d.setAttribute('cx', p.x.toFixed(1)); d.setAttribute('cy', p.y.toFixed(1)); d.setAttribute('r', (.8 + .9 * p.z).toFixed(2)); d.setAttribute('class', 'dot');
        g.appendChild(d);
      }
    }
    [[37, -86], [33, -97], [30, -95], [34, -84], [39, -105], [51, 0], [53, -6], [52, 5], [49, 2], [52, 13],
     [39, -9], [44, -79], [6, 0], [-7, 39], [32, -65], [-34, 18]].forEach(function (ll, i) {
      var p = proj(ll[0], ll[1]); if (p.z < 0) return;
      var d = document.createElementNS(NS, 'circle');
      d.setAttribute('cx', p.x.toFixed(1)); d.setAttribute('cy', p.y.toFixed(1)); d.setAttribute('r', 3); d.setAttribute('class', 'lit');
      var a = document.createElementNS(NS, 'animate');
      a.setAttribute('attributeName', 'r'); a.setAttribute('values', '2.4;4;2.4'); a.setAttribute('dur', (2 + (i % 4) * .5) + 's'); a.setAttribute('repeatCount', 'indefinite');
      d.appendChild(a); g.appendChild(d);
    });
  }

  var people = document.getElementById('lgPeople');
  if (people) for (var k = 0; k < 100; k++) { var dot = document.createElement('i'); if (k < 54) dot.className = 'on'; people.appendChild(dot); }

  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;
  root.classList.add('lg-anim');

  function fmt(v, el) {
    var s = (el.hasAttribute('data-comma') || v >= 10000) ? Math.round(v).toLocaleString('en-US') : String(Math.round(v));
    return s + (el.getAttribute('data-suffix') || '');
  }
  function count(el) {
    var end = +el.getAttribute('data-count'), t0 = performance.now(), dur = 1400;
    (function step(t) {
      var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(end * e, el); if (k < 1) requestAnimationFrame(step);
    })(t0);
  }
  var vh = window.innerHeight;
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target; io.unobserve(el); el.classList.remove('pre');
      el.querySelectorAll('[data-count]').forEach(count);
      var r = el.querySelector('#lgRing');
      if (r) { r.style.strokeDashoffset = '314.16'; requestAnimationFrame(function () { requestAnimationFrame(function () { r.style.strokeDashoffset = '141.37'; }); }); }
    });
  }, { threshold: .2 });
  root.querySelectorAll('.lg-rv').forEach(function (el) { if (el.getBoundingClientRect().top > vh) el.classList.add('pre'); io.observe(el); });
})();
