# Instron Technologies — Live-Theme Preview

This repo shows the new website content from the review build (v2.6, `instron-website-review`) in the look of the current live site, instrontechnologies.com. Use it to judge look and feel, and how all content and navigation would appear if the existing theme were kept.

- It has 32 static pages, one `.html` file per page with its own web address, and real links between pages and sections. JavaScript is only needed for the dropdown menus and the contact email draft.
- The live-site look comes from `assets/css/live-theme.css`. It covers Roboto, the navy/green top bar, white header with the green CTA, green pill buttons, `#0979AE` blue bands, curved grey sections, dark photo banners on inner pages, and the blue contact band with the photo footer.
- Content is unchanged from review build v2.6. Only colours, fonts and the header and footer layout were changed.
- Pages are set to `noindex,nofollow`.
- The contact page builds an email draft locally. Nothing is sent or stored.

Master content stays in `rbshirude-instrontech/instron-website-review`. This repo is a preview only.

## IRA project map (v2.31, 26 Nov 2026, test only)
IRA, Instron's Resource Assistant, is switched off for normal visitors. Add `?ira=1` to any page address to try it (for example `index.html?ira=1`); a plain address turns it off. While it is on, links between pages keep it on.
- Guided map in three steps (area; technology stage or main need, with process or industry; engineering or data today) that ends in a **project brief**: what the visitor told us, a suggested first step (How We Work phase, or the PlantON deployment sequence), up to three pages to read, up to two related projects, and the page's own "Useful inputs to prepare". The brief can be saved as PDF, copied, or carried into the Contact form.
- "Describe it in your own words" keeps the typed route; it ends in the same brief.
- With `?ira=1`, Home shows a "Start with your problem" band under the hero, and solution, application and industry pages show a short "Map my project" band before the footer.
- Every line in the brief is site copy except the map's own questions and option labels in `assets/ira/ira.js`.
- Runs entirely in the browser: no cookies, browser storage, outside services or AI model; nothing is sent until the visitor sends the email themselves.
- `tools/ira_content.py` rebuilds `assets/ira/ira-content.json` from the built pages (titles, summaries, photos, phases, PlantON deployment steps, prepare lists). The need tags in the script are the part to review. `tools/build.py` runs it and adds the one script tag to every page, so syncs keep IRA.

## v2.35 design layouts (26 Nov 2026)
Sumit's design suggestions as approved by Rahul page by page (review: https://claude.ai/artifact/Ft5h8Azz3pbrxEu3pKUuRD).
- `tools/v235_review.py <review repo>` applies the section layouts to the review build's pages (from its committed index.html), then `tools/sync.py` rebuilds this site. Icons in `tools/v235_icons.json` (Lucide, ISC licence).
- Theme-only parts: closing band (text left, photo right, green diagonal) on every page, footer location chips (`build.py`), IRA start-card tint and the IRA page prompt as a light card (`assets/ira/ira.css`).
- `tools/ira_content.py` reads capability cards that now carry an icon; ira-content.json output unchanged.
- About Us pages follow when Sumit's captures arrive.
- v2.35.1: `tools/v2351_industries.py <review repo>` applies the same layouts to the six Industries pages (run after v2.35 is in the review repo).
