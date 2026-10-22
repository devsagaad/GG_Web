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

Journal posts are pages with an "article" block. Their read time is counted
from the words in the post, the journal index lists them through <!--@posts-->,
and the homepage's hand-written journal list is checked against them, so a
post's title, date or read time cannot drift between the three. A post with
"unpublished": true is kept as a source but not built, listed or mapped: the
static twin of a draft item in the Webflow Journal collection.

Authors live in src/authors.json, the twin of the Webflow Authors collection.
Each post names one by slug; each author gets a page at /authors/<slug>.

Post and author pages mirror Webflow collection templates, where the page-level
JSON-LD setting leaves CMS field tokens empty. Webflow marks those pages up with
schema.org microdata on the visible elements instead, so these pages do the
same and carry no JSON-LD.

    python3 tools/build-pages.py           write the pages
    python3 tools/build-pages.py --check   exit 1 if any page on disk is stale

Page source format (src/pages/<name>.html):

    <!--page
    {"path": "services/brand-identity", "title": "...", "description": "...",
     "crumb": "Brand identity", "parent": ["Services", "/#services"],
     "type": "WebPage" | "ContactPage" | "AboutPage" | "CollectionPage",
     "service": {"name": "...", "serviceType": "...", "description": "..."},
     "article": {"date": "2026-10-21", "headline": "...", "summary": "...", "author": "<slug>"},
     "unpublished": true,
     "microdata": true,
     "people": ["<author slug>"],
     "work": {"client": "...", "year": "2025", "summary": "...", "tag": "BRAND + WEB",
              "tile": "/assets/work/<slug>-tile.svg", "featured": true,
              "services": ["brand-identity", "webflow-websites", "ai-integration"]}}

"microdata": true marks a page that mirrors a Webflow page carrying microdata
(its markup has the itemscope attributes) and so gets no JSON-LD.

A "work" block makes the page a case study, the twin of an item in the Webflow
Work collection. "services" records what the studio delivered, one switch per
service there. Tiles are listed through <!--@work--> (every project) and
<!--@work:<service>--> (projects that included it), in the Work Collection
Lists' order: year descending, then client. The homepage's hand-written work
section is checked against the featured projects.
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
AUTHORS = ROOT / "src" / "authors.json"
HOME = ROOT / "index.html"
ORIGIN = "https://gridandglint.com"
# Hosted on Webflow, so the same file serves both builds: structured data and
# link previews. A 512px PNG of the mark on forest green, legible on white.
LOGO = "https://cdn.prod.website-files.com/6acfa22f20186e84030ebfb9/6ad9420df49388480a5cb8f1_grid-and-glint-logo-512.png"
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
        # Pulled into a page body with <!--@mailbox-->, so the contact page and
        # the homepage share one set of contact details instead of two that drift.
        "mailbox": between(t, '<div class="mailbox">', '</address>', "mailbox") + "\n        </div>",
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
    if not re.match(r'<main id="top"[ >]', main):
        fail(f'{path.name}: body must open with <main id="top"> (the footer\'s back-to-top targets it)')
    if len(meta["title"]) > 60:
        fail(f"{path.name}: title is {len(meta['title'])} chars; Google truncates past ~60")
    if not 110 <= len(meta["description"]) <= 160:
        fail(f"{path.name}: description is {len(meta['description'])} chars; keep it 110-160")
    return meta, main


WPM = 220  # reading speed behind the "N MIN" read times


def human(date):
    """2026-10-21 -> October 21, 2026: what a Webflow date binding prints, so
    the journal reads the same in both builds. The ISO date stays in
    <time datetime> and the schema."""
    import datetime
    d = datetime.date.fromisoformat(date)
    return f"{d:%B} {d.day}, {d.year}"


def prose_words(main):
    body = re.search(r'<div class="prose">(.*?)</div>\s*</div>\s*</section>', main, re.S)
    return len(re.sub(r"<[^>]+>", " ", body.group(1) if body else main).split())


def byline(meta, authors):
    a = meta["article"]
    who = authors[a["author"]]
    # The author link is a schema.org Person inside the page's BlogPosting,
    # as on the Webflow post template.
    return (f'<p class="byline lbl"><time datetime="{a["date"]}" itemprop="datePublished">{human(a["date"])}</time>'
            f'<span aria-hidden="true">&#183;</span><span>{a["minutes"]} MIN READ</span>'
            f'<span aria-hidden="true">&#183;</span><span>BY</span>'
            f'<a href="/authors/{who["slug"]}" itemprop="author" itemscope itemtype="https://schema.org/Person">'
            f'<span itemprop="name">{html.escape(who["name"], quote=False)}</span>'
            f'<meta itemprop="url" content="/authors/{who["slug"]}"></a></p>'
            f'\n      <link itemprop="publisher" href="{ORIGIN}/#org">')


EMPTY = "The first posts are on their way."


def post_list(posts, authors):
    """The journal index's list: the homepage's .posts markup, newest first."""
    esc = lambda s: html.escape(s, quote=False)
    if not posts:
        # The Webflow Collection List's empty state carries the same line.
        return f'<div class="posts">\n        <p class="empty">{EMPTY}</p>\n      </div>'
    rows = []
    # Newest first, then by title: the same order as the Webflow Collection List
    # (sort: published descending, name ascending), so both builds list alike.
    by_title = sorted(posts, key=lambda m: m["article"]["headline"])
    for m in sorted(by_title, key=lambda m: m["article"]["date"], reverse=True):
        a = m["article"]
        rows.append(f'        <a href="/{m["path"]}"><time class="data" datetime="{a["date"]}">{human(a["date"])}</time>'
                    f'<span class="tt"><h2 class="tth">{esc(a["headline"])}</h2><span class="ex">{esc(a["summary"])}</span></span>'
                    f'<span class="lbl r">BY {esc(authors[a["author"]]["name"])} &#183; {a["minutes"]} MIN</span></a>')
    return '<div class="posts">\n' + "\n".join(rows) + "\n      </div>"


def check_home(posts, authors):
    """Every journal link on the homepage must match a published post: title,
    date, author, minutes."""
    by = {"/" + m["path"]: m for m in posts}
    t = HOME.read_text()
    for href in re.findall(r'href="(/journal/[^"#?]+)"', t):
        if href not in by:
            fail(f"index.html links {href}, which is not a published post")
    for href, date, title, who, mins in re.findall(
            r'<a href="(/journal/[^"]+)"><time class="data" datetime="[^"]+">([^<]+)</time><span class="tt"><h3 class="tth">(.*?)</h3>.*?BY (.*?) (?:&#183;|·) (\d+) MIN</span></a>', t):
        a = by[href]["article"]
        want = (human(a["date"]), html.escape(a["headline"], quote=False),
                html.escape(authors[a["author"]]["name"], quote=False), str(a["minutes"]))
        if (date, title, who, mins) != want:
            fail(f"index.html journal entry {href} says {(date, title, who, mins)}, post says {want}")


def sitemap(pages, authors):
    """Every indexable page: the homepage, each non-draft source and each author.
    Drafts are noindex, so listing them would only send Google mixed signals."""
    urls = [("", None)] + sorted([(m["path"], m.get("article", {}).get("date"))
                                  for _, m, _ in pages if not m.get("draft")]
                                 + [(f"authors/{s}", None) for s in authors])
    rows = []
    for path, date in urls:
        lastmod = f"\n    <lastmod>{date}</lastmod>" if date else ""
        rows.append(f"  <url>\n    <loc>{ORIGIN}/{path}</loc>{lastmod}\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- GENERATED by tools/build-pages.py; drafts are left out. -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")


def faq_from(main):
    pairs = re.findall(r'<summary><h3>(.*?)</h3></summary>\s*<p class="ans">(.*?)</p>', main, re.S)
    clean = lambda s: html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()
    return [{"@type": "Question", "name": clean(q),
             "acceptedAnswer": {"@type": "Answer", "text": clean(a)}} for q, a in pairs]


def person(a):
    """An author as a schema.org Person: one @id for them across the site."""
    url = f"{ORIGIN}/authors/{a['slug']}"
    return {"@type": "Person", "@id": f"{url}#person", "name": a["name"], "jobTitle": a["jobTitle"], "url": url,
            "worksFor": {"@id": f"{ORIGIN}/#org"}, "sameAs": [a["linkedin"]]}


def schema(meta, main, authors):
    url = f"{ORIGIN}/{meta['path']}"
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{ORIGIN}/"}]
    if "parent" in meta:
        crumbs.append({"@type": "ListItem", "position": 2, "name": meta["parent"][0], "item": ORIGIN + meta["parent"][1]})
    crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": meta["crumb"], "item": url})
    graph = [
        {"@type": meta.get("type", "WebPage"), "@id": f"{url}#page", "url": url, "name": meta["title"],
         "description": meta["description"], "isPartOf": {"@id": f"{ORIGIN}/#website"},
         "breadcrumb": {"@id": f"{url}#crumbs"}, "inLanguage": "en"},
        {"@type": "BreadcrumbList", "@id": f"{url}#crumbs", "itemListElement": crumbs},
    ]
    for slug in meta.get("people", []):
        graph.append(person(authors[slug]))
    if "service" in meta:
        s = meta["service"]
        graph.append({"@type": "Service", "@id": f"{url}#service", "name": s["name"], "serviceType": s["serviceType"],
                      "description": s["description"], "url": url, "provider": ORG,
                      "areaServed": [{"@type": "Country", "name": "Philippines"}, "Worldwide"]})
    qs = faq_from(main)
    if qs:
        graph.append({"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": qs})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)


def article_microdata(meta, main):
    """Mark a post up as a schema.org BlogPosting, attribute for attribute as the
    Webflow post template does (the byline adds the date, author and publisher)."""
    for old, new in (('<main id="top">', '<main id="top" itemscope itemtype="https://schema.org/BlogPosting">'),
                     ('<h1 class="disp" id="h1">', '<h1 class="disp" id="h1" itemprop="headline">'),
                     ('<p class="lede">', '<p class="lede" itemprop="description">'),
                     ('<div class="prose">', '<div class="prose" itemprop="articleBody">')):
        if main.count(old) != 1:
            fail(f"{meta['_src']}: needs exactly one {old} for the post's microdata")
        main = main.replace(old, new)
    return main


def author_page(a):
    """An author's page, the twin of the Webflow Authors template."""
    esc = lambda s: html.escape(s, quote=False)
    meta = {"path": f"authors/{a['slug']}", "title": f"{a['name']}, {a['jobTitle']} | Grid and Glint",
            "description": a["seoDescription"], "crumb": a["name"], "_src": "authors.json", "microdata": True}
    # Webflow hides an empty Rich Text binding, so the bio appears only once
    # written. No itemprop: Webflow still publishes the empty element, and an
    # empty description is worse than none.
    bio = f'\n      <div class="prose">{a["bio"]}</div>' if a["bio"] else ""
    main = f"""<main id="top" itemscope itemtype="https://schema.org/ProfilePage">
  <section class="page-hero wrap" aria-labelledby="h1">
    <div class="xs"><span class="x"></span><span class="x"></span><span class="x"></span></div>
    <div class="inner" itemprop="mainEntity" itemscope itemtype="https://schema.org/Person">
      <nav class="crumbs lbl" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/journal">Journal</a><span aria-hidden="true">/</span><span aria-current="page">{esc(a['name'])}</span></nav>
      <h1 class="disp" id="h1" itemprop="name">{esc(a['name'])}</h1>
      <p class="lede" itemprop="jobTitle">{esc(a['role'])}</p>{bio}
      <div class="actions page-cta"><a class="btn mag" href="{a['linkedin']}" rel="noopener" itemprop="sameAs">LinkedIn <span class="arr">&#8599;</span></a><a class="btn ghost" href="/about">About the studio</a></div>
      <link itemprop="url" href="/authors/{a['slug']}"><link itemprop="worksFor" href="{ORIGIN}/#org">
    </div>
  </section>
</main>"""
    return meta, main


SERVICES = ("brand-identity", "webflow-websites", "ai-integration")


def work_tile(m):
    w, esc, href = m["work"], (lambda s: html.escape(s, quote=False)), "/" + m["path"]
    return (f'<article class="tile rv"><a class="plate media" href="{href}" tabindex="-1" aria-hidden="true">'
            f'<img class="plate-img" src="{w["tile"]}" width="800" height="600" alt="" loading="lazy"></a>'
            f'<div class="meta"><h3 class="name"><a href="{href}">{esc(w["client"])}</a></h3>'
            f'<div class="data">{w["year"]}</div><div class="lbl">{esc(w["summary"])}</div>'
            f'<div class="tag">{esc(w["tag"])}</div></div></article>')


def work_list(works, keep=lambda w: True):
    """Tiles for the projects `keep` selects, ordered like the Webflow Work
    Collection Lists: year descending, then client."""
    sel = sorted((m for m in works if keep(m["work"])), key=lambda m: m["work"]["client"])
    rows = [work_tile(m) for m in sorted(sel, key=lambda m: m["work"]["year"], reverse=True)]
    return '<div class="work">\n        ' + "\n        ".join(rows) + "\n      </div>"


def check_work(m):
    w = m.get("work")
    for k in ("client", "year", "summary", "tag", "tile", "services"):
        if k not in w:
            fail(f"{m['_src']}: work block needs {k!r}")
    for s in w["services"]:
        if s not in SERVICES:
            fail(f"{m['_src']}: unknown service {s!r}; use one of {', '.join(SERVICES)}")
    if not (ROOT / w["tile"].lstrip("/")).exists():
        fail(f"{m['_src']}: tile {w['tile']} does not exist")


def check_home_work(works):
    """The homepage's work tiles must be exactly the featured projects."""
    want = work_list(works, lambda w: w.get("featured"))
    if want not in HOME.read_text():
        fail("index.html's work section does not match the featured projects. It should read:\n      " + want)


def render(meta, main, c, authors):
    for name in ("mailbox", "posts"):
        main = main.replace(f"<!--@{name}-->", c[name])
    main = main.replace("<!--@work-->", work_list(c["works"]))
    main = re.sub(r"<!--@work:([a-z-]+)-->", lambda g: work_list(c["works"], lambda w: g.group(1) in w["services"])
                  if g.group(1) in SERVICES else fail(f"{meta['_src']}: unknown service {g.group(1)!r}"), main)
    if "article" in meta:
        main = main.replace("<!--@byline-->", byline(meta, authors))
        main = article_microdata(meta, main)
        meta["microdata"] = True
    if "<!--@" in main:
        fail(f"{meta['_src']}: unknown include {re.search(r'<!--@[^>]*-->', main).group(0)}")
    esc = lambda s: html.escape(s, quote=True)
    url = f"{ORIGIN}/{meta['path']}"
    # An unreviewed legal draft should not be indexed; flip "draft" off once
    # a lawyer has read it and the page will be indexed normally.
    robots = meta.get("robots", "noindex, follow" if meta.get("draft") else "index, follow")
    draft = ("<!-- DRAFT: not reviewed by a lawyer. Have it checked before this page goes live. -->\n"
             if meta.get("draft") else "")
    ld = ("" if meta.get("microdata") else
          f'<script type="application/ld+json">\n{schema(meta, main, authors)}\n</script>\n')
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
<meta property="og:type" content="{'article' if 'article' in meta else 'website'}">
<meta property="og:site_name" content="Grid and Glint">
<meta property="og:title" content="{esc(meta['title'])}">
<meta property="og:description" content="{esc(meta['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{LOGO}">
<meta property="og:image:alt" content="Grid and Glint logomark">
<meta name="twitter:card" content="summary">
{ld}{c['fonts']}
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


def read_authors():
    authors = {}
    for a in json.loads(AUTHORS.read_text()):
        for k in ("slug", "name", "jobTitle", "role", "linkedin", "seoDescription", "bio"):
            if k not in a:
                fail(f"authors.json: {a.get('slug', '?')} needs {k!r}")
        if not 110 <= len(a["seoDescription"]) <= 160:
            fail(f"authors.json: {a['slug']} seoDescription is {len(a['seoDescription'])} chars; keep it 110-160")
        authors[a["slug"]] = a
    return authors


def main():
    check = "--check" in sys.argv
    c = chrome()
    authors = read_authors()
    stale = []
    sources = sorted(SRC.glob("*.html"))
    if not sources:
        fail(f"no page sources in {SRC}")
    pages, unpublished = [], []
    for src in sources:
        meta, body = read_source(src)
        meta["_src"] = src.name
        for slug in meta.get("people", []) + ([meta["article"].get("author")] if "article" in meta else []):
            if slug not in authors:
                fail(f"{src.name}: author {slug!r} is not in authors.json")
        if meta.get("unpublished"):
            unpublished.append(ROOT / meta["path"] / "index.html")
            continue
        if "article" in meta:
            words = prose_words(body)
            meta["article"].update(words=words, minutes=max(1, round(words / WPM)))
        pages.append((src, meta, body))
    posts = [m for _, m, _ in pages if "article" in m]
    c["posts"] = post_list(posts, authors)
    check_home(posts, authors)
    c["works"] = [m for _, m, _ in pages if "work" in m]
    for m in c["works"]:
        check_work(m)
    check_home_work(c["works"])
    built = [(meta, render(meta, body, c, authors)) for _, meta, body in pages]
    for a in authors.values():
        meta, body = author_page(a)
        built.append((meta, render(meta, body, c, authors)))
    for meta, page in built:
        out = ROOT / meta["path"] / "index.html"
        if check:
            if not out.exists() or out.read_text() != page:
                stale.append(str(out.relative_to(ROOT)))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page)
        print(f"  /{meta['path']:<34} {len(page):>7,} bytes")
    # An unpublished post must not linger on disk from an earlier build.
    for out in unpublished:
        if out.exists():
            if check:
                stale.append(f"{out.relative_to(ROOT)} (unpublished; delete it)")
            else:
                out.unlink()
                if not any(out.parent.iterdir()):
                    out.parent.rmdir()
                print(f"  removed /{out.parent.relative_to(ROOT)} (unpublished)")
    sm = ROOT / "sitemap.xml"
    if check:
        if sm.read_text() != sitemap(pages, authors):
            stale.append("sitemap.xml")
    else:
        sm.write_text(sitemap(pages, authors))
    if check:
        if stale:
            print("stale — run tools/build-pages.py:\n  " + "\n  ".join(stale))
            sys.exit(1)
        print(f"all {len(built)} pages current ({len(unpublished)} unpublished)")


if __name__ == "__main__":
    main()
