#!/usr/bin/env python3
"""
Build every page except the homepage from src/pages/*.html.

index.html stays the one hand-edited source for everything shared: the head's
fonts and stylesheet, the logo <defs>, the header, the menu, the footer, the
cursor and the Ask Glint panel. Each page source carries only its own <main>
and a small JSON front matter; this script stamps the shared chrome around it,
so a change to the header is made once, in index.html, and reaches every page
on the next build.

Structured data is derived, not hand-written: the FAQPage schema is read out of
the page's own visible FAQ, so the two cannot disagree.

    python3 tools/build-pages.py           write the pages
    python3 tools/build-pages.py --check   exit 1 if any page on disk is stale

Page source format (src/pages/<name>.html):

    <!--page
    {"path": "services/brand-identity", "title": "...", "description": "...",
     "crumb": "Brand identity", "parent": ["Services", "/#services"],
     "type": "WebPage" | "ContactPage",
     "service": {"name": "...", "serviceType": "...", "description": "..."}}
    -->
    <main id="top"> ... </main>
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "grid-and-glint-website"
SRC = ROOT / "src" / "pages"
HOME = ROOT / "index.html"
ORIGIN = "https://gridandglint.com"
ORG = {"@type": "ProfessionalService", "@id": f"{ORIGIN}/#org", "name": "Grid and Glint", "url": f"{ORIGIN}/"}


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def between(text, start, end, label, include_end=True):
    s = text.find(start)
    if s < 0:
        fail(f"[{label}] start marker not found: {start[:60]!r}")
    e = text.find(end, s + len(start))
    if e < 0:
        fail(f"[{label}] end marker not found: {end[:60]!r}")
    return text[s:e + (len(end) if include_end else 0)]


def chrome():
    """Pull the shared pieces out of index.html, verbatim."""
    t = HOME.read_text()
    c = {
        "defs": between(t, '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>', "</defs></svg>", "defs"),
        "tracks": between(t, '<div class="tracks" aria-hidden="true">', "</div></div></div>", "tracks"),
        "header": between(t, '<header class="bar wrap">', "</header>", "header"),
        "menu": between(t, '<nav class="menu" id="menu"', "</nav>", "menu"),
        "footer": between(t, '<footer class="site-foot">', "</footer>", "footer"),
        "cursor": between(t, '<div class="cur" id="cur"', "</div>", "cursor"),
        "ask": between(t, '<div class="ask" id="ask">', '\n\n<script src="assets/glint-hero.js">', "ask", include_end=False).rstrip(),
        "fonts": between(t, '<link rel="preconnect" href="https://fonts.googleapis.com">', 'display=swap">', "fonts"),
        # Pulled into a page body with <!--@mailbox--> / <!--@brief-->, so the
        # contact page and the homepage share one form instead of two that drift.
        "mailbox": between(t, '<div class="mailbox">', '</address>', "mailbox") + "\n        </div>",
        "brief": between(t, '<form class="brief" id="brief"', "</form>", "brief"),
    }
    # The header and menu point at homepage sections. Off the homepage, those
    # anchors must go home first; the logo goes home; contact has its own page.
    # <a> only: the logo's <use href="#gg-mark"> must stay a same-document
    # reference, or the mark blanks on every inner page.
    def relink(m):
        target = {"top": "/", "contact": "/contact"}.get(m.group(2), "/#" + m.group(2))
        return f'{m.group(1)}{target}"'
    for k in ("header", "menu"):
        c[k] = re.sub(r'(<a\b[^>]*?\bhref=")#([a-z][\w-]*)"', relink, c[k])
    # The footer's back-to-top stays page-local: every page carries id="top".
    return c


def read_source(path):
    t = path.read_text()
    m = re.match(r"\s*<!--page\s*(\{.*?\})\s*-->\s*(.*)\Z", t, re.S)
    if not m:
        fail(f"{path.name}: missing <!--page {{...}} --> front matter")
    meta = json.loads(m.group(1))
    main = m.group(2).strip()
    for k in ("path", "title", "description", "crumb"):
        if k not in meta:
            fail(f"{path.name}: front matter needs {k!r}")
    if not main.startswith('<main id="top">'):
        fail(f'{path.name}: body must open with <main id="top"> (the footer\'s back-to-top targets it)')
    if len(meta["title"]) > 60:
        fail(f"{path.name}: title is {len(meta['title'])} chars; Google truncates past ~60")
    if not 110 <= len(meta["description"]) <= 160:
        fail(f"{path.name}: description is {len(meta['description'])} chars; keep it 110-160")
    return meta, main


def faq_from(main):
    pairs = re.findall(r'<summary><h3>(.*?)</h3></summary>\s*<p class="ans">(.*?)</p>', main, re.S)
    clean = lambda s: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()
    return [{"@type": "Question", "name": clean(q),
             "acceptedAnswer": {"@type": "Answer", "text": clean(a)}} for q, a in pairs]


def schema(meta, main):
    url = f"{ORIGIN}/{meta['path']}"
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{ORIGIN}/"},
              {"@type": "ListItem", "position": 2, "name": meta["crumb"], "item": url}]
    graph = [
        {"@type": meta.get("type", "WebPage"), "@id": f"{url}#page", "url": url, "name": meta["title"],
         "description": meta["description"], "isPartOf": {"@id": f"{ORIGIN}/#website"},
         "breadcrumb": {"@id": f"{url}#crumbs"}, "inLanguage": "en"},
        {"@type": "BreadcrumbList", "@id": f"{url}#crumbs", "itemListElement": crumbs},
    ]
    if "service" in meta:
        s = meta["service"]
        graph.append({"@type": "Service", "@id": f"{url}#service", "name": s["name"], "serviceType": s["serviceType"],
                      "description": s["description"], "url": url, "provider": ORG,
                      "areaServed": [{"@type": "Country", "name": "Philippines"}, "Worldwide"]})
    qs = faq_from(main)
    if qs:
        graph.append({"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": qs})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)


def render(meta, main, c):
    for name in ("mailbox", "brief"):
        main = main.replace(f"<!--@{name}-->", c[name])
    if "<!--@" in main:
        fail(f"{meta['_src']}: unknown include {re.search(r'<!--@[^>]*-->', main).group(0)}")
    esc = lambda s: html.escape(s, quote=True)
    url = f"{ORIGIN}/{meta['path']}"
    # An unreviewed legal draft should not be indexed; flip "draft" off once
    # a lawyer has read it and the page will be indexed normally.
    robots = meta.get("robots", "noindex, follow" if meta.get("draft") else "index, follow")
    draft = ("<!-- DRAFT: not reviewed by a lawyer. Have it checked before this page goes live. -->\n"
             if meta.get("draft") else "")
    return f"""<!doctype html>
<html lang="en">
<!-- GENERATED by tools/build-pages.py from src/pages/{meta['_src']}. Edit that file, or
     index.html for anything shared, then rebuild. Changes made here are overwritten. -->
{draft}<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#1a1a1a">
<link rel="manifest" href="/site.webmanifest">
<title>{esc(meta['title'])}</title>
<meta name="description" content="{esc(meta['description'])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Grid and Glint">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['description'])}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">
{schema(meta, main)}
</script>
{c['fonts']}
<link rel="stylesheet" href="/assets/glint.css">
</head>
<body>
{c['defs']}
{c['tracks']}

{c['header']}

{c['menu']}

{main}

{c['footer']}

{c['cursor']}

{c['ask']}

<script src="/assets/glint-ui.js"></script>
</body>
</html>
"""


def main():
    check = "--check" in sys.argv
    c = chrome()
    stale = []
    sources = sorted(SRC.glob("*.html"))
    if not sources:
        fail(f"no page sources in {SRC}")
    for src in sources:
        meta, body = read_source(src)
        meta["_src"] = src.name
        out = ROOT / meta["path"] / "index.html"
        page = render(meta, body, c)
        if check:
            if not out.exists() or out.read_text() != page:
                stale.append(str(out.relative_to(ROOT)))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page)
        print(f"  /{meta['path']:<34} {len(page):>7,} bytes   {len(faq_from(body))} FAQ")
    if check:
        if stale:
            print("stale — run tools/build-pages.py:\n  " + "\n  ".join(stale))
            sys.exit(1)
        print(f"all {len(sources)} pages current")


if __name__ == "__main__":
    main()
