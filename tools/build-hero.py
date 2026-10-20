#!/usr/bin/env python3
"""
One-time migration: lift the WebGL hero out of index.html into a standalone,
self-contained bundle (assets/glint-hero.js).

The shader sources, the logomark path data and the matrix math are copied
byte-exact from index.html — only the couplings to the surrounding page are
rewritten, and every rewrite is an exact-match replacement that raises if it
does not hit exactly once.

After the cutover index.html no longer carries the shader, so this script is a
record of how the extraction was done rather than a step you run again.

    python3 tools/build-hero.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "grid-and-glint-website"
SRC = SITE / "index.html"
MESH_JSON = SITE / "assets" / "glint-mark.json"
OUT = SITE / "assets" / "glint-hero.js"

# Inclusive 1-based line span of the WebGL block inside index.html.
SHARED_FROM, SHARED_TO = 857, 876   # material tokens, GL helpers, MARK path data
HERO_FROM, HERO_TO = 879, 1028      # body of the `hero()` IIFE


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        fail(f"[{label}] expected exactly 1 match, found {n}")
    return text.replace(old, new)


lines = SRC.read_text().split("\n")


def span(a, b):
    return "\n".join(lines[a - 1:b])


shared = span(SHARED_FROM, SHARED_TO)
hero = span(HERO_FROM, HERO_TO)

# Guard the boundaries so a shifted line number can't silently truncate the shader.
if "var M = { ior: 1.45" not in shared:
    fail("shared block does not start at the material tokens")
if "function visible(el, cb)" not in shared:
    fail("shared block does not reach visible()")
if "var stage = document.getElementById('stage')" not in hero:
    fail("hero block does not start at the stage lookup")
if "ResizeObserver" not in hero:
    fail("hero block does not reach the end of build()")

# ---------------------------------------------------------------- shared edits

shared = replace_once(
    shared,
    "function visible(el, cb) { if (!('IntersectionObserver' in window)) return cb(true); "
    "new IntersectionObserver(function (es) { cb(es[0].isIntersecting); }).observe(el); }",
    "function visible(el, cb) { if (!('IntersectionObserver' in window)) { cb(true); return null; } "
    "var o = new IntersectionObserver(function (es) { cb(es[0].isIntersecting); }); o.observe(el); return o; }",
    "visible returns its observer so destroy() can disconnect it",
)

shared = replace_once(
    shared,
    "  function paintGrid(g, W, H, cx, cy) {\n"
    "    g.fillStyle = css('--bg', '#1a1a1a'); g.fillRect(0, 0, W, H);\n"
    "    g.fillStyle = css('--rule-grid', '#262626');",
    "  function paintGrid(g, W, H, cx, cy, bg, grid) {\n"
    "    g.fillStyle = bg; g.fillRect(0, 0, W, H);\n"
    "    g.fillStyle = grid;",
    "paintGrid takes colours instead of reading the page's CSS variables",
)

# ------------------------------------------------------------------ hero edits

shared_state = """    var stage = resolveEl(opts.stage);
    if (!stage) return null;
    if (getComputedStyle(stage).position === 'static') stage.style.position = 'relative';

    var fb = resolveEl(opts.fallback)
          || stage.querySelector('[data-glint-fallback]')
          || document.getElementById('stage-fallback');

    // The page that owned this code styled the canvas from CSS (.stage canvas).
    // A Webflow embed has no such rule, so the canvas is styled inline instead.
    var canvas = document.createElement('canvas');
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block';
    stage.appendChild(canvas);

    var pointerTarget = resolveEl(opts.pointerTarget) || stage.parentElement || stage;
    var themeMode = opts.theme || 'auto';
    var themeListeners = [];
    var raf = 0, io = null, ro = null, mo = null, mq = null;
    var onPointer = null, onScheme = null, destroyed = false;

    // 'auto' keeps the original behaviour: sniff the page's CSS variables.
    // An explicit mode uses the built-in palette, for hosts that define no such
    // variables — otherwise the hero would silently lock to dark.
    function activePalette() {
        return themeMode === 'dark' ? PALETTE.dark : themeMode === 'light' ? PALETTE.light : null;
    }
    function themeBg() { var p = activePalette(); return p ? p.bg : css('--bg', '#1a1a1a'); }
    function themeGrid() { var p = activePalette(); return p ? p.grid : css('--rule-grid', '#262626'); }
    function isDark() {
        var p = activePalette();
        return p ? p === PALETTE.dark : dot3(hex(css('--bg', '#1a1a1a'), [0.1, 0.1, 0.1])) < 0.5;
    }
    function emitThemeChange() { themeListeners.forEach(function (f) { f(); }); }
"""

hero = replace_once(
    hero,
    "    var stage = document.getElementById('stage'), canvas = document.getElementById('mark-canvas'), "
    "fb = document.getElementById('stage-fallback'), yawEl = null;",
    shared_state.rstrip("\n"),
    "stage/canvas/fallback resolved from options; canvas created by the bundle",
)

hero = replace_once(
    hero,
    "    if (!gl) { canvas.remove(); return; }",
    "    if (!gl) { canvas.remove(); return null; }",
    "no-WebGL early return yields null to the caller",
)

hero = replace_once(
    hero,
    "catch (e) { canvas.remove(); return; }",
    "catch (e) { canvas.remove(); return null; }",
    "shader link failure early return yields null to the caller",
)

hero = replace_once(
    hero,
    "      paintGrid(g, W, H, cx, cy);",
    "      paintGrid(g, W, H, cx, cy, themeBg(), themeGrid());",
    "paintGrid call passes the resolved theme colours",
)

hero = replace_once(
    hero,
    "    fetch('assets/glint-mark.json').then(function (r) { if (!r.ok) throw 0; return r.json(); })"
    ".then(build).catch(function () { canvas.remove(); });",
    "    try { build(MESH); } catch (e) { canvas.remove(); return null; }",
    "mesh is compiled in, so no fetch and no cross-origin question",
)

hero = replace_once(
    hero,
    "      var target = 0, yaw = reduce ? 0.42 : 0, pitch = -0.2, t0 = performance.now(), on = true, raf = 0;",
    "      var target = 0, yaw = reduce ? 0.42 : 0, pitch = -0.2, t0 = performance.now(), on = true;",
    "raf hoisted to instance scope for destroy()",
)

hero = replace_once(
    hero,
    "      stage.closest('.hero').addEventListener('pointermove', function (e) { "
    "var r = stage.getBoundingClientRect(); target = ((e.clientX - r.left) / r.width - 0.5) * 1.2; });",
    "      onPointer = function (e) { var r = stage.getBoundingClientRect(); "
    "target = ((e.clientX - r.left) / r.width - 0.5) * 1.2; };\n"
    "      pointerTarget.addEventListener('pointermove', onPointer);",
    "pointer-follow binds to a configurable element, not an ancestor .hero class",
)

hero = replace_once(
    hero,
    "      function draw(now) {\n        size();",
    "      function draw(now) {\n        if (destroyed) return;\n        size();",
    "draw bails once destroyed so no frame outlives the instance",
)

hero = replace_once(
    hero,
    "      visible(stage, function (v) {",
    "      io = visible(stage, function (v) {",
    "keep the IntersectionObserver for destroy()",
)

hero = replace_once(
    hero,
    "      if (window.ResizeObserver) new ResizeObserver(function () { if (reduce) requestAnimationFrame(draw); }).observe(stage);",
    "      if (window.ResizeObserver) { ro = new ResizeObserver(function () { if (reduce) requestAnimationFrame(draw); }); ro.observe(stage); }",
    "keep the ResizeObserver for destroy()",
)

# ------------------------------------------------------------------- the mesh

mesh = json.loads(MESH_JSON.read_text())
positions = mesh["positions"]
indices = mesh["indices"]
if max(abs(v) for v in positions) > 1.0001:
    fail("unexpected position range; the mesh is not in the assumed unit space")
mesh_js = (
    "  var MESH = {\n"
    "    positions: " + json.dumps(positions, separators=(",", ":")) + ",\n"
    "    indices: " + json.dumps(indices, separators=(",", ":")) + "\n"
    "  };\n"
)

# --------------------------------------------------------------------- assemble

header = '''/*!
 * Glint Hero - the Grid and Glint logomark in mint glass.
 *
 * Lifted out of index.html so one renderer serves both the static reference page
 * and a Webflow HTML Embed. Self-contained: no dependencies, mesh compiled in,
 * no network request, nothing read from the host page's stylesheet unless you
 * ask for it.
 *
 *   var hero = GlintHero.mount({ stage: '#glint-stage' });
 *   hero.setTheme('light');          // 'auto' | 'dark' | 'light'
 *   hero.destroy();
 *
 * Options
 *   stage          element or selector; the canvas is appended to it   (required)
 *   fallback       element or selector shown until the first frame lands
 *   pointerTarget  element or selector the pointer-follow listens on
 *   theme          'auto' reads the page's --bg / --rule-grid variables;
 *                  'dark' or 'light' uses the built-in palette instead
 *
 * Returns null when WebGL is unavailable, leaving the fallback in place.
 */
(function (global) {
  'use strict';

  var reduce = false;
  try { reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  // Mirrors the :root values in the reference page, for hosts that define no
  // CSS variables of their own.
  var PALETTE = {
    dark: { bg: '#1a1a1a', grid: '#262626' },
    light: { bg: '#f7f7f7', grid: '#e6e6e6' }
  };

  function resolveEl(v) {
    if (!v) return null;
    return typeof v === 'string' ? document.querySelector(v) : v;
  }
  function css(n, d) { var v = getComputedStyle(document.documentElement).getPropertyValue(n).trim(); return v || d; }
  function hex(s, d) { var m = /^#([0-9a-f]{6})/i.exec(s || ''); if (!m) return d; var h = m[1]; return [parseInt(h.slice(0, 2), 16) / 255, parseInt(h.slice(2, 4), 16) / 255, parseInt(h.slice(4, 6), 16) / 255]; }
  function dot3(c) { return (c[0] + c[1] + c[2]) / 3; }

'''

tail = '''
    function setTheme(t) {
      themeMode = t || 'auto';
      emitThemeChange();
    }

    function destroy() {
      if (destroyed) return;
      destroyed = true;
      cancelAnimationFrame(raf);
      if (io) io.disconnect();
      if (ro) ro.disconnect();
      if (mo) mo.disconnect();
      if (mq && onScheme) { mq.removeEventListener ? mq.removeEventListener('change', onScheme) : mq.removeListener(onScheme); }
      if (onPointer) pointerTarget.removeEventListener('pointermove', onPointer);
      themeListeners.length = 0;
      if (canvas.parentNode) canvas.remove();
      if (fb) fb.style.display = '';
    }

    // Replaces the themeListeners array the page used to own: the bundle watches
    // for a theme flip itself, so the host needs no wiring.
    if (typeof MutationObserver === 'function') {
      mo = new MutationObserver(emitThemeChange);
      mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class', 'style'] });
    }
    try {
      mq = matchMedia('(prefers-color-scheme: dark)');
      onScheme = emitThemeChange;
      mq.addEventListener ? mq.addEventListener('change', onScheme) : mq.addListener(onScheme);
    } catch (e) {}

    return { setTheme: setTheme, destroy: destroy, stage: stage, canvas: canvas };
  }

  global.GlintHero = { mount: mountHero, version: '1.0.0' };
})(typeof window !== 'undefined' ? window : this);
'''

bundle = (
    header
    + shared
    + "\n\n"
    + mesh_js
    + "\n"
    + "  function mountHero(opts) {\n"
    + "    opts = opts || {};\n"
    + hero
    + tail
)

OUT.write_text(bundle)

# ------------------------------------------------------------------- integrity

src_text = SRC.read_text()
checks = {
    "fragment shader": '"  gl_FragColor = vec4(clamp(floor(c * uLv + B4(f / max(uDi * uDpr, 1.0))) / uLv, 0.0, 1.0), 1.0);",',
    "vertex shader": "var VS = 'attribute vec3 aP; attribute vec3 aN;",
    "dither helper": "float B2(vec2 a){ a = floor(a); return fract(a.x * 0.5 + a.y * a.y * 0.75); }",
    "material tokens": "var M = { ior: 1.45, thick: 0.42, disp: 0.035, rough: 0.08, fres: 3.0, dither: 2, levels: 32, grain: 0.04 };",
    "distance field bevel": "var out = new Uint8Array(N * N), BEV = 22;",
    "perspective matrix": "function persp(f, a) { var t = 1 / Math.tan(f / 2), n = 0.1, fa = 60, nf = 1 / (n - fa);",
}
bad = [k for k, v in checks.items() if v not in bundle or v not in src_text]
if bad:
    fail("these survived the move unverified: " + ", ".join(bad))

marks_src = re.findall(r'"(M\d[^"]{40,})"', src_text)
marks_out = re.findall(r'"(M\d[^"]{40,})"', bundle)
if not marks_src or marks_src[:4] != marks_out[:4]:
    fail("logomark path data differs between index.html and the bundle")

print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size:,} bytes)")
print(f"  shader sources, material tokens and {len(marks_out[:4])} logomark paths verified byte-exact")
print(f"  mesh compiled in: {len(positions)//3} vertices, {len(indices)//3} triangles")
