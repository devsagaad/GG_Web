# Grid and Glint — website

The studio's landing page as a static website. No build step: upload this folder as it is.

## Files

| File | What |
| --- | --- |
| `index.html` | The landing page, with page title, search description, structured data (business, website, FAQ) and all styles and scripts inline |
| `assets/glint-hero.js` | The hero logomark in mint glass (WebGL), with the mesh compiled in. The Webflow build loads this same file |
| `assets/glint-mark.json` | Source mesh for the logomark. Compiled into `glint-hero.js`; not loaded at runtime |
| `assets/umbrella-dental-clinic.svg` | Client logo (Umbrella Dental Clinic) |
| `assets/favicon.svg` | Browser-tab icon |
| `404.html` | Page-not-found page |
| `robots.txt`, `sitemap.xml` | For search engines, pointing at https://gridandglint.com |
| `site.webmanifest` | App name and icon for phones |

## Preview on your computer

Opening `index.html` by double-click shows the whole page, 3D logo included — the mesh is compiled into `assets/glint-hero.js`, so nothing is fetched at runtime. To serve it over HTTP instead:

```
python3 -m http.server 8000
```

then open http://localhost:8000.

## Before going live

- Fonts load from Google Fonts. Thunder (the brand display face) is not included; headings use Big Shoulders Display until Thunder's licensed web-font files are added.
- Footer and service links point to pages that do not exist yet (`/services/...`, `/work/...`, `/journal/...`, `/privacy`, `/terms`, `/ai-policy`, `/imprint`). They will show the 404 page until those pages are built.
- Dashed "fill in" slots still need real content: team names, photos and credentials, client quotes, measured results, more client logos.
- Add a 1200×630 share image and reference it as `og:image` in `index.html`.
- The Ask Glint chat and the brief form are demos: nothing is sent anywhere. Connect the form to your email or CRM before launch.
- Add the DTI registration number to the contact section and footer once it is issued.
