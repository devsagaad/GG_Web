/* Grid and Glint — page behaviour shared by every page.

   Loaded by the static reference pages. Anything that exists on only one page
   (the manifesto, the process line, the WebGL hero) is guarded
   on its element, so a page without it simply skips that block instead of
   throwing and taking every later feature down with it.

   The Webflow build does NOT load this file: there, the menu is a native
   interaction and the rest is not built yet. If that changes, pin it like
   glint.css — never paste it into an embed. */
(function () {
  var root = document.documentElement;
  var reduce = false; try { reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  function pad(v, n) { v = Math.max(0, Math.round(v)); return ('0000' + v).slice(-(n || 4)); }
  function css(n, d) { var v = getComputedStyle(root).getPropertyValue(n).trim(); return v || d; }
  function hex(s, d) { var m = /^#([0-9a-f]{6})/i.exec(s || ''); if (!m) return d; var h = m[1]; return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255]; }
  function isDark() { return dot3(hex(css('--bg', '#1a1a1a'), [0.1, 0.1, 0.1])) < 0.5; }
  function dot3(c) { return (c[0] + c[1] + c[2]) / 3; }

  /* ---- theme toggle, also on the A key ---- */
  var themeListeners = [];
  function flipTheme() { root.setAttribute('data-theme', isDark() ? 'light' : 'dark'); themeListeners.forEach(function (f) { f(); }); }
  document.querySelectorAll('.theme-btn').forEach(function (b) { b.addEventListener('click', flipTheme); });
  addEventListener('keydown', function (e) { if ((e.key === 'a' || e.key === 'A') && !/INPUT|TEXTAREA/.test(document.activeElement.tagName) && !e.metaKey && !e.ctrlKey) flipTheme(); });

  /* ---- in-page links: a short eased scroll ----
     The same curve webflow.js uses for its anchor links, at the 0.3 multiplier
     the Webflow pages set with data-scroll-time="0.3" on <body>, so a click on
     "Systems" moves the same way in both builds: about 0.4 s for a short hop, 0.7 s
     for the length of the homepage. CSS scroll-behavior: smooth stays off: in
     Webflow it stacks on webflow.js's own animation and doubled the wait. */
  var SCROLL_TIME = 0.3;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="#"]');
    if (!a || e.defaultPrevented || e.button || e.metaKey || e.ctrlKey || e.shiftKey) return;
    if (a.host !== location.host || a.pathname !== location.pathname || !/^#[a-zA-Z][\w:.-]*$/.test(a.hash)) return;
    var el = document.getElementById(a.hash.slice(1));
    if (!el) return;
    e.preventDefault();
    if (location.hash !== a.hash) history.pushState(null, '', a.hash);
    var from = scrollY, to = Math.round(el.getBoundingClientRect().top + scrollY), d = to - from;
    var ms = reduce ? 0 : Math.max(0, (472.143 * Math.log(Math.abs(d) + 125) - 2000) * SCROLL_TIME), t0 = performance.now();
    function done() { el.setAttribute('tabindex', el.getAttribute('tabindex') || '-1'); el.focus({ preventScroll: true }); }
    if (!ms) { scrollTo(0, to); done(); return; }
    (function step(now) {
      var k = Math.min(1, (now - t0) / ms);
      scrollTo(0, from + d * (k < 0.5 ? 4 * k * k * k : (k - 1) * (2 * k - 2) * (2 * k - 2) + 1));
      if (k < 1) requestAnimationFrame(step); else done();
    })(t0);
  });

  /* ---- menu for mobile and tablet ----
     A button, not :target or a checkbox, because the close has to play the
     open in reverse; both of those snap shut. The page is held still while it
     is open so the view does not jump back to the top on close. */
  var burger = document.getElementById('burger'), menu = document.getElementById('menu'), held = 0;
  function setMenu(open, refocus) {
    if (open === (burger.getAttribute('aria-expanded') === 'true')) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    menu.classList.toggle('open', open);
    burger.classList.toggle('open', open);
    root.classList.toggle('menu-open', open);
    if (open) { held = scrollY; document.body.style.cssText = 'position:fixed;top:' + -held + 'px;left:0;right:0'; }
    /* the read forces a reflow: until the document is tall again the browser
       clamps the restore to the collapsed height and lands short */
    else { document.body.style.cssText = ''; void document.body.offsetHeight; scrollTo({ top: held, behavior: 'instant' }); if (refocus) burger.focus(); }
  }
  burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true', true); });
  menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false, true); });
  var wide = matchMedia('(min-width: 1025px)');
  function onWide(e) { if (e.matches) setMenu(false); }
  if (wide.addEventListener) wide.addEventListener('change', onWide); else wide.addListener(onWide);

  /* ---- clock and coordinates: measured, never typed in ---- */
  var clock = document.getElementById('clock'), xy = document.getElementById('xy');
  function tick() { var d = new Date(), off = -d.getTimezoneOffset() / 60; clock.textContent = 'GMT' + (off < 0 ? '-' : '+') + Math.abs(off).toString().replace('.5', ':30') + ' ' + pad(d.getHours(), 2) + ':' + pad(d.getMinutes(), 2) + ':' + pad(d.getSeconds(), 2); }
  tick(); setInterval(tick, 1000);

  /* ---- crosshair cursor ---- */
  var cur = document.getElementById('cur'), curxy = document.getElementById('cur-xy');
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  addEventListener('pointermove', function (e) {
    xy.textContent = pad(e.clientX) + ' X ' + pad(e.clientY) + ' Y';
    if (!fine) return;
    cur.classList.add('live');
    cur.style.transform = 'translate(' + e.clientX + 'px,' + e.clientY + 'px)' + (e.target.closest && e.target.closest('a,button,input') ? ' scale(1.6)' : '');
    curxy.textContent = pad(e.clientX) + ' · ' + pad(e.clientY);
  }, { passive: true });
  document.addEventListener('pointerleave', function () { cur.classList.remove('live'); });

  /* ---- text scramble on hover, mono-decoder style ---- */
  var GL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+×#';
  document.querySelectorAll('.scr').forEach(function (el) {
    var node = el.firstChild; if (!node || node.nodeType !== 3) return;
    var orig = node.textContent, busy = false;
    el.addEventListener('mouseenter', function () {
      if (reduce || busy) return; busy = true; var f = 0;
      (function step() {
        node.textContent = orig.split('').map(function (c, i) { return i < f / 2 ? c : GL[(Math.random() * GL.length) | 0]; }).join('');
        if (f++ < orig.length * 2) requestAnimationFrame(step); else { node.textContent = orig; busy = false; }
      })();
    });
  });

  /* ---- magnetic buttons ---- */
  if (fine && !reduce) document.querySelectorAll('.mag').forEach(function (b) {
    b.addEventListener('pointermove', function (e) { var r = b.getBoundingClientRect(); b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.18) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.28) + 'px)'; });
    b.addEventListener('pointerleave', function () { b.style.transform = ''; });
  });

  /* ---- reveal: visible at rest, a short settle when it enters ---- */
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    document.querySelectorAll('.rv').forEach(function (el, i) { el.style.animationDelay = (i % 4) * 80 + 'ms'; if (el.getBoundingClientRect().top > innerHeight) io.observe(el); });
  }

  /* ---- manifesto: words light as you read; process fills as you scroll ----
     Independent of each other: a service page has the process but no
     manifesto, and its steps must still light. */
  var man = document.getElementById('manifesto'), proc = document.getElementById('proc');
  var words = [], steps = [], bar = null;
  if (man) {
    (function split() {
      var out = [];
      man.childNodes.forEach(function (n) {
        if (n.nodeType === 3) n.textContent.split(/(\s+)/).forEach(function (w) { out.push(/^\s+$/.test(w) || !w ? document.createTextNode(w) : mk(w, false)); });
        else out.push(mk(n.textContent, true));
      });
      function mk(t, g) { var s = document.createElement('span'); s.className = 'w' + (g ? ' g' : ''); s.textContent = t; return s; }
      man.textContent = ''; out.forEach(function (n) { man.appendChild(n); });
    })();
    words = man.querySelectorAll('.w');
  }
  if (proc) { steps = proc.querySelectorAll('li'); bar = proc.querySelector('.line b'); }
  function onScroll() {
    if (man) {
      var r = man.getBoundingClientRect(), p = (innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.35);
      p = reduce ? 1 : Math.max(0, Math.min(1, p));
      var n = Math.round(p * words.length);
      words.forEach(function (w, i) { w.classList.toggle('on', i < n); });
    }
    if (proc) {
      var q = proc.getBoundingClientRect(), pp = reduce ? 1 : Math.max(0, Math.min(1, (innerHeight * 0.8 - q.top) / (q.height + innerHeight * 0.2)));
      if (bar) bar.style.setProperty('--p', pp.toFixed(3));
      steps.forEach(function (s, i) { s.classList.toggle('on', pp >= i / steps.length + 0.02); });
    }
  }
  if (man || proc) { addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', onScroll); onScroll(); }

  /* ---- copy the email ---- */
  var copy = document.getElementById('copy'), mail = document.getElementById('mail');
  if (copy && mail) copy.addEventListener('click', function () {
    function sel() { var r = document.createRange(); r.selectNodeContents(mail); var s = getSelection(); s.removeAllRanges(); s.addRange(r); copy.textContent = 'SELECTED'; }
    try { navigator.clipboard.writeText(mail.textContent).then(function () { copy.textContent = 'COPIED'; }, sel); } catch (e) { sel(); }
    setTimeout(function () { copy.textContent = 'COPY'; }, 1800);
  });

  /* ---- Ask Glint: scripted demo ---- */
  var panel = document.getElementById('panel'), launch = document.getElementById('launch'), log = document.getElementById('log');
  var A = {
    'Can you build us a chatbot?': 'Yes. We build assistants like this one, connected to your content and your CRM, in your brand voice, with a person reviewing what matters. Each build is scoped on a short call, and your Product Spec sets the timeline.',
    'How long does a website take?': 'Most sites take 6 to 10 weeks: two for the system, the rest for design and build. Identity plus website runs about 12.',
    'Do you build in Webflow?': 'Yes. We set up your design tokens as Webflow variables and build a CMS your team can edit without us.',
    'What does it cost?': 'Every project is scoped on a short call so you only pay for what you need. You get a written proposal after the call.'
  };
  function setOpen(o) { panel.hidden = !o; launch.setAttribute('aria-expanded', String(o)); if (!o) launch.focus(); }
  launch.addEventListener('click', function () { setOpen(panel.hidden); });
  document.getElementById('close').addEventListener('click', function () { setOpen(false); });
  document.getElementById('sug').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var q = b.textContent, m = document.createElement('div'); m.className = 'msg me'; m.textContent = q; log.appendChild(m);
    setTimeout(function () { var r = document.createElement('div'); r.className = 'msg bot'; r.textContent = A[q]; log.appendChild(r); log.scrollTop = log.scrollHeight; }, reduce ? 0 : 450);
    log.scrollTop = log.scrollHeight;
  });

  /* ---- the hero: the logomark in mint glass, now in assets/glint-hero.js ---- */
  if (window.GlintHero && document.getElementById('stage')) GlintHero.mount({ stage: '#stage', fallback: '#stage-fallback', pointerTarget: '.hero' });

})();
