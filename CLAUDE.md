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

## Webflow API gotchas

Learned the hard way; each one cost a failed call.

- **A list of class names is a combo chain, not independent classes.**
  `["hero","wrap"]` means `.hero.wrap`, and fails unless that combo exists.
  Create combos with `create_style(name, parent_style_names=[...])`.
- **Classes attach at creation time.** `data_element_tool > set_style` fails on
  an existing element; the builder's `set_style` works. Build elements with
  their classes rather than restyling afterwards.
- **A style with no properties is registered but not materialised** — it lists
  in `get_styles` yet cannot be applied. Give every class one real declaration.
- `set_text` takes `{"text": "..."}`, not a bare string.
- Embeds do not execute in the Designer canvas, so the canvas shows unstyled
  structure. Preview on the staging URL.

## Repository

- Work on the branch named in the session brief; never push to `main`.
- This session's GitHub credentials push branches but **not tags** (403), so
  jsDelivr pins use commit SHAs.
