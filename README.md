# Instron Technologies — Live-Theme Preview

This repo shows the new website content from the review build (v2.6, `instron-website-review`) in the look of the current live site, instrontechnologies.com. Use it to judge look and feel, and how all content and navigation would appear if the existing theme were kept.

- It has 32 static pages, one `.html` file per page with its own web address, and real links between pages and sections. JavaScript is only needed for the dropdown menus and the contact email draft.
- The live-site look comes from `assets/css/live-theme.css`. It covers Roboto, the navy/green top bar, white header with the green CTA, green pill buttons, `#0979AE` blue bands, curved grey sections, dark photo banners on inner pages, and the blue contact band with the photo footer.
- Content is unchanged from review build v2.6. Only colours, fonts and the header and footer layout were changed.
- Pages are set to `noindex,nofollow`.
- The contact page builds an email draft locally. Nothing is sent or stored.

Master content stays in `rbshirude-instrontech/instron-website-review`. This repo is a preview only.

## IRA page finder (25 Nov 2026, test only)
IRA, Instron's Resource Assistant, is switched off for normal visitors. Add `?ira=1` to any page address to try it (for example `index.html?ira=1`); `?ira=0` or a plain address turns it off. While it is on, links between pages keep it on.
- Runs entirely in the browser: guided questions, then up to three pages from `assets/ira/ira-content.json`, then an optional brief carried into the Contact form. No cookies, browser storage, outside services or AI model; nothing is sent until the visitor sends the email themselves.
- `tools/ira_content.py` rebuilds the page list from the built pages (titles and summaries are site copy; the need tags in the script are the part to review). `tools/build.py` runs it and adds the one script tag to every page, so syncs keep IRA.
- Files: `assets/ira/ira.js`, `assets/ira/ira.css`, `assets/ira/ira-content.json`.
