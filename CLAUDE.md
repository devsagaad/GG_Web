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
Ask Glint panel, and the contact details (`<!--@mailbox-->`). Every other page
is generated:

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

**The journal lives in two places.** Static: one `src/pages/journal-<slug>.html`
per post with an `"article"` block naming its `"author"`; the build counts the
read time, lists posts on `/journal` and fails if the homepage's journal list
disagrees. Webflow: the **Journal** CMS collection (fields mirror the front
matter, `author` references Authors), a template page bound to it, and a
Collection List on `/journal` sorted published-descending then name-ascending,
the same order the generator uses. A new post goes into both. `sitemap.xml` is
generated too.

- **Unpublished posts.** `"unpublished": true` keeps a source but builds,
  lists and maps nothing, the twin of a draft CMS item. The three current posts
  are unpublished at the user's request; they are credited to Mark Sagaad.
  While none is published, `/journal` shows its empty state and the homepage
  journal section is off (removed in `index.html`, visibility off in Webflow).
  Republishing: drop the flag, flip the CMS items to published, put the
  homepage section back in `index.html` and make it visible in Webflow. The
  drafts' bodies and `related-service-link` still say `/services/...`; check
  them against where the service pages live by then.
- **Authors.** `src/authors.json` is the twin of the Webflow **Authors**
  collection; each author has a page at `/authors/<slug>`. The Person `@id` is
  `https://gridandglint.com/authors/<slug>#person` everywhere it appears.
- **Post and author pages carry microdata, not JSON-LD**, in both builds,
  because Webflow cannot fill CMS fields into JSON-LD (see the gotchas).

**The team.** The studio has a team, but only the founder, Mark Sagaad, is named
on the site, by the user's choice. Do not add team cards or placeholders for
the others.

`assets/glint-ui.js` holds the page behaviour for the static pages. Each
page-specific block is guarded on its element, so one missing element cannot
throw and take every later feature down. The Webflow build does not load it.

## No forms: contact is the chatbot's job

The site is for marketing, search and answer engines. Enquiries are taken by a
separate AI chatbot the user is building (requirements, a booked time, name and
number), integrated later. So **build no contact or brief forms**, in either
build. "Get a quote" links go to `/contact?service=<slug>`; the parameter is
kept for the chatbot to read. The contact page carries the studio's details and
ContactPage schema. When the chatbot launches, the privacy policy must cover
what it collects and that AI processes it.

## The assistant and the gateway

The chatbot that will take enquiries, and the AI gateway it runs through (also
offered to clients and billed per use), are specified in
`docs/glint-assistant.md`. They are built from scratch: the user designed a
similar system at their day job, and none of that employer's code, prompts,
names or configuration may come into this repo.

## Proof and claims

**Real work only.** The site runs ads, and Google Ads' misrepresentation policy
covers invented clients and case studies. Three fictional case studies were
removed for that reason. The one project on the site is Umbrella Dental Clinic
(brand identity and Webflow website). Lunamoury is a real client but comes off
the site until there is finished work to show. Nothing goes in the work
section, a testimonial or a result line without the user confirming it.

**Case studies live in two places**, like the journal. Static: a source per
project, `src/pages/work-<slug>.html` (`"microdata": true`), images in
`assets/work/`. Webflow: the **Work** CMS collection, whose template serves
`/work/<slug>`; the body is Rich Text, an H3 per decision with full-width
figures. The Umbrella case study is drawn from the clinic's brand guidelines in
the studio's Figma (file `42b7iYEm9BViV7ZFlSW4Yg`, page "BRAND GUIDELINES").
That file also holds the proposal, contract and invoice; never publish from
those pages, and use no photos of people from it.

**The record of what we did drives every work list.** Each project says which
services it delivered and whether it is featured, and the lists follow:

- Static: the source's `"work"` block (`client`, `year`, `summary`, `tag`,
  `tile`, `featured`, `services` from `brand-identity`, `webflow-websites`,
  `ai-integration`). `<!--@work-->` renders every project, `<!--@work:<service>-->`
  only that service's. The homepage list is pasted, not included, and the build
  fails if it is not exactly the featured projects.
- Webflow: Switch fields `brand-identity`, `webflow-website` (singular),
  `ai-integration` and `featured` on the Work item. Collection Lists on `/`
  (filter `featured`), `/work` (none) and each service page (its switch), all
  sorted year-descending then name-ascending, like the generator.
- A service with no projects has no work section: `ai-integration` has none
  today. Add the section back on both builds with its first project.
- Tile images are 800x600, `assets/work/<slug>-tile.svg` statically and the
  `tile` Image field in Webflow. The tile links by the `case-link` stopgap; see
  the gotchas.

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
  `element_schema`.** Its own `set_style` key does work on children, but
  `set_text` on child Text Blocks does not; set text and attributes afterwards
  in their own calls.
- **Webflow's base stylesheet styles some tags.** `blockquote` gets padding
  and a 5px left border, `figcaption` a top margin and centring, headings
  margins. When a Webflow section comes out taller than the reference, look
  for a tag default and reset it in `glint.css`, never in a Webflow class.
- **Images need a managed asset.** whtml inserts an `<img>` with an outside
  `src` as an unmanaged image. Create the asset with `data_assets_tool
  create_asset`, POST the bytes to the returned S3 form, then
  `set_image_asset` on the element.
- **`set_dom_id` fails on a whtml-inserted element** — "could not be applied to
  the component map", permanently, while `set_attributes` on the same element
  succeeds and `id` is refused there as reserved. Have the page script assign
  the id at runtime if something needs to point at it.
- **whtml's `css` must not redeclare an existing class.** If `.n` already
  exists with different properties, the import makes a second class `n-1` and
  puts the new elements on it. Query the classes first and declare only new
  ones, each with a property that matches `glint.css`.
- **A bare boolean attribute is dropped on publish.** `<details open>` shows
  `open: ""` in the Designer but publishes without it; write `open="open"`.
- **Never remove a Collection List's empty state.** Deleting the
  `DynamoEmpty` child deletes the whole list.
- CMS binding keys: `text` on Heading, Paragraph and Text Block (not on a
  whtml `<span>`; use a Text Block), `richText` on Rich Text, `link` on links.
  Collection List config is `source` = `{"collectionId"}` and `sort` =
  `[{"fieldSlug","direction":"descending"}]`.
- **Collection List filters**: `filters` = `[{"fieldSlug":"featured",
  "operator":"isOn"}]` for a Switch (`equals` is refused). It fails with an
  MPS "Conflict" while the list's item is empty, so build the row first. **Read
  `filters` back after setting it**: a filter set during the build was later
  found empty on all three lists, and nothing failed. Prove a filter by
  switching a field off, publishing and checking the page.
- **A list row cannot link to "Current item" through the API**: `page` and
  `collectionPage` modes publish a fixed href. The Journal row binds a stopgap
  `post-link` field instead; switch it to "Current Journal" in the Designer and
  delete the field. The post byline likewise binds the Authors `profile-link`
  stopgap; link it to the Author in the Designer and delete that field. Work
  tiles bind the Work `case-link` stopgap the same way; link them to "Current
  Work" and delete it.
- **Reference fields bind like their own**: field id
  `"<referenceFieldId>:::<fieldIdInTheOtherCollection>"`, e.g. the post's
  author name.
- Template **SEO title and description** take field tokens:
  `{{wf {&quot;path&quot;:&quot;seo-title&quot;,&quot;type&quot;:&quot;PlainText&quot;\} }}`.
- **CMS field tokens do not resolve in JSON-LD on a collection template.**
  Tested October 2026: the page-level JSON-LD setting published every token
  empty, in both the `&quot;` and plain-quote forms; tokens written into an
  HTML Embed's code through the API publish as literal text. So template pages
  use **schema.org microdata**: `itemscope`/`itemtype`/`itemprop` attributes on
  the visible elements (write `itemscope="itemscope"`, see the boolean rule),
  plus hidden `<link>`/`<meta>` DOM elements whose `href`/`content` attribute
  is bound to a field with `set_settings` `attributes` + `value_binding`.
  Create those DOM elements with `data_element_builder` first, with no
  settings; inserting `<meta>`/`<link>` through whtml timed out.
- **A Date field bound to an attribute publishes as "October 21, 2026"**, not
  ISO 8601, so it cannot fill `datePublished`. The Webflow post microdata has
  no date; the static build's does.
- **Conditional visibility cannot be set through the API on a template page**
  ("not inside a CMS context"). An empty Rich Text binding is still published,
  as an empty `w-dyn-bind-empty` element.
- **A Block's text cannot be set** ("doesn't support text"): remove the Block
  and insert a new one with the text.
- A static page may share its slug with a collection (`/journal` page and
  `/journal/<slug>` items coexist).
- **Link pages by reference, not by path.** `set_link` with `linkType: "page"`
  and the page id publishes the page's current URL and follows it if the page
  moves. Remove the `href` attribute whtml left behind, or it wins.
- Page folders (`/services/...`) need the Designer bridge: `create_page_folder`
  only works while the Webflow MCP app is open in the Designer. Until then the
  service pages sit at the root (`/ai-integration`), and every Webflow link to
  them is a page reference, so moving them into a folder carries the links
  along. The static build and the schema already use the `/services/...` URLs.

## Repository

- Work on the branch named in the session brief; never push to `main`.
- This session's GitHub credentials push branches but **not tags** (403), so
  jsDelivr pins use commit SHAs.
