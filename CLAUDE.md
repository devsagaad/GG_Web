# Grid and Glint

The studio site. `grid-and-glint-website/` is the static reference build; it is
mirrored into Webflow (site `grid-and-glint-c5e174`, staging at
`grid-and-glint-c5e174.webflow.io`).

## Build rule

**Always check whether Webflow can reproduce something natively before reaching
for custom code.** Native elements, classes, pseudo-states and interactions
first. An HTML Embed is the fallback, used only once Webflow has been shown not
to express the thing — as with the WebGL hero, which needs a canvas and a
shader. When an embed is unavoidable, its opening comment says why Webflow
could not do it, so the decision can be revisited when Webflow gains the
feature.

Prefer native even when the embed would be quicker: content in embeds cannot be
edited in the Designer or the Editor, which is most of the reason to be on
Webflow at all.

## Shared assets, one source

`assets/glint.css` and `assets/glint-hero.js` are linked by both the static page
and the Webflow build, pinned to immutable jsDelivr commit URLs:

```
https://cdn.jsdelivr.net/gh/devsagaad/GG_Web@<commit-sha>/grid-and-glint-website/assets/<file>
```

Never paste either file's contents into Webflow — that is the drift the split
was meant to prevent. Change the file, commit, re-pin the SHA. Pin to a commit,
never a branch: a branch URL lets any push silently rewrite the live site, and
jsDelivr caches it hard.

`assets/glint-mark.json` is the source mesh, compiled into `glint-hero.js` at
build time by `tools/build-hero.py`; it is not fetched at runtime.

`tools/embed-harness.html` renders the hero in a host with no CSS variables, no
`.hero` ancestor and no `.stage` rule — i.e. Webflow's conditions. Check changes
to the hero against it.

## Page contract

The footer is a Webflow Component ("Site footer") and the same markup in
`index.html`. It goes last on every page, and nothing in it is page-specific:
every link is an absolute path, never a homepage anchor.

It does rely on one thing from each page: **the top of the page must carry
`id="top"`**, because the footer's back-to-top link targets `#top`. On the
reference page that is `<main id="top">`; in Webflow it is the hero section.
Any new page needs it or the link silently does nothing.

## Pages in the static build

`index.html` is hand-edited and is the **one source for everything shared**: the
head's fonts and stylesheet, the logo `<defs>`, header, menu, footer, cursor,
Ask Glint panel, and the brief form. Every other page is generated:

```
grid-and-glint-website/src/pages/<name>.html   ->  <path>/index.html
python3 tools/build-pages.py                     # write
python3 tools/build-pages.py --check             # exit 1 if anything is stale
```

- **Never edit a generated `<path>/index.html`.** Its banner says so; the next
  build overwrites it. Edit the source, or `index.html` for shared chrome.
- After changing anything shared in `index.html`, rebuild and run `--check`
  before committing.
- Page structured data is derived: the FAQPage schema is read out of the page's
  own visible FAQ, so the two cannot disagree. Don't hand-write it.
- A source with `"draft": true` is rendered `noindex` with a DRAFT comment. The
  privacy and terms pages are drafts until a lawyer has read them.

`assets/glint-ui.js` holds the page behaviour for the static pages. Each
page-specific block is guarded on its element, so one missing element cannot
throw and take every later feature down. The Webflow build does not load it.

## Proof and claims

**Real work only.** The site runs ads, and Google Ads' misrepresentation policy
covers invented clients and case studies. Three fictional case studies were
removed for that reason. Real projects: Umbrella Dental Clinic (website) and
Lunamoury (brand identity, website and AI integration). Nothing goes in the
work section, a testimonial or a result line without the user confirming it.

## Webflow API gotchas

Learned the hard way; each one cost a failed call.

- **A list of class names is a combo chain, not independent classes.**
  `["hero","wrap"]` means `.hero.wrap`, and fails unless that combo exists.
  Create combos with `create_style(name, parent_style_names=[...])`. Every
  multi-class element in the reference markup needs its combo created first —
  `.sec.wrap`, `.lbl.a`, `.btn.mag`, `.flow.rv` and so on. This is the single
  cause of nearly every "styles not found" error; `set_style` works fine on an
  existing element once the combo exists.
- **A style with no properties is registered but not materialised** — it lists
  in `get_styles` yet cannot be applied. Give every class one real declaration.
- `set_text` takes `{"text": "..."}`, not a bare string.
- **Share the logomark as a `<g>` in `<defs>`, never a `<symbol>`.** A `<use>`
  on a symbol creates a new viewport at 0,0 sized to the `<use>`, which shifts
  this artwork by 48.3 units and clips it — its paths are authored in the
  space `48.3 48.3 160 160` that each referencing `<svg>` declares as its
  viewBox. A `<use>` on a group clones into the current user space and lands
  correctly. Symptom: the mark looks cropped at small sizes.
- Embeds do not execute in the Designer canvas, so the canvas shows unstyled
  structure. Preview on the staging URL.
- **Interactions are how shared CSS drives Webflow.** An IX3 click trigger with
  a `toggleClass` action flips a class; `glint.css` then draws every frame, so
  the motion is authored once and both builds play it identically. Reach for
  this before an embed whenever the behaviour is "a class goes on and comes
  off". A `wf:class` target takes a bare class slug — no style-block id lookup
  — but `selectors` on the class property needs the id.
- **An interaction cannot write an attribute.** So key any CSS a Webflow
  interaction must drive off a class, never off `[aria-*]`, and leave the
  attribute to a script that *watches* the class. The watcher must not also
  handle the click, or it fights the interaction for the open state.
- **`data_whtml_builder` turns `<button>` into a Link**, i.e. an `<a>` with no
  href. For a real button, build a `DOM` element and `set_tag` it to `button`.
  Everything else it produces — nested tags, classes, attributes — is faithful.
- **`data_element_builder` ignores `tag`, `styles` and `attributes` in
  `element_schema`.** It creates the right shape of `div`s and nothing else;
  set the tag, style and attributes afterwards in their own calls.
- **`set_dom_id` fails on a whtml-inserted element** — "could not be applied to
  the component map", permanently, while `set_attributes` on the same element
  succeeds and `id` is refused there as reserved. Have the page script assign
  the id at runtime if something needs to point at it.

## Repository

- Work on the branch named in the session brief; never push to `main`.
- This session's GitHub credentials push branches but **not tags** (403), so
  jsDelivr pins use commit SHAs.
