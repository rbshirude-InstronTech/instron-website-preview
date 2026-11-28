#!/usr/bin/env node
/* Build the WordPress theme content (content/pages.json + header/footer partials) from this preview repo.

   Reconstructed 28 Nov 2026 from the installed 2.47.0 theme on ira.instrontechnologies.com, because the 2.47.0
   package builder (source/build_wp.py) was not available. Proven byte-identical: run on commit 8fa0823 it
   reproduces the installed 2.47.0 pages.json and all six partials exactly (52 pages).

   Usage:  node tools/wp_pages.js <out-dir> [version]
   Writes: <out-dir>/content/pages.json, <out-dir>/partials/{header,footer}{,-fr,-es}.html
   Copy them into the theme folder (wp-content/themes/instron-technologies/), set style.css Version to the same
   version, then Appearance > Instron Pages > Import all pages (overwrite).

   Not handled here (unchanged by content builds): functions.php, inc/, assets/ (copy changed files from assets/;
   assets/ira/ira.js on WordPress carries a few WordPress-only edits, so patch it rather than replacing it),
   partials/generic-head.html (only its stylesheet version stamp changes), content/redirects.json, llms.txt,
   robots.txt.
*/
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');

// English page list in WordPress order: [file stem, package key, WordPress slug, admin title]
const EN = [
  ['index', 'home', 'home', 'Home'],
  ['solutions', 'solutions', 'solutions', 'Solutions'],
  ['process-skid-plants', 'process', 'process-skid-plants', 'Process Skid Plants'],
  ['pilot-demonstration-plants', 'pilot', 'pilot-demonstration-plants', 'Pilot & Demonstration Plants'],
  ['industrial-process-skids', 'industrial', 'industrial-process-skids', 'Industrial Process Skids'],
  ['industrial-automation', 'automation', 'industrial-automation', 'Industrial Automation'],
  ['planton-digital-factory', 'planton', 'planton-digital-factory', 'PlantON™ by Instron Technologies'],
  ['how-we-work', 'how', 'how-we-work', 'How We Work'],
  ['industries', 'industries', 'industries', 'Industries'],
  ['energy-transition-critical-minerals', 'cleantech', 'energy-transition-critical-minerals', 'Energy Transition & Critical Minerals'],
  ['research-technology-development', 'research', 'research-technology-development', 'Research & Technology Development'],
  ['chemicals-refining-consumer-products', 'chemical', 'chemicals-refining-consumer-products', 'Chemicals, Refining & Consumer Products'],
  ['food-beverage-dairy', 'food', 'food-beverage-dairy', 'Food, Beverage & Dairy'],
  ['pharma-life-sciences', 'pharma', 'pharma-life-sciences', 'Pharma & Life Sciences'],
  ['industrial-manufacturing', 'manufacturing', 'industrial-manufacturing', 'Industrial Manufacturing'],
  ['project-portfolio', 'portfolio', 'project-portfolio', 'Project Portfolio'],
  ['case-studies', 'cases', 'case-studies', 'Case Studies'],
  ['our-company', 'company', 'our-company', 'Our Company'],
  ['global-presence', 'global', 'global-presence', 'Global Presence & Partners'],
  ['leadership', 'leadership', 'leadership', 'Leadership & Engineering Team'],
  ['trust-responsibility', 'trust', 'trust-responsibility', 'Trust & Responsibility'],
  ['careers', 'careers', 'careers', 'Careers'],
  ['contact', 'contact', 'contact', 'Contact'],
  ['privacy-terms-accessibility', 'legal', 'privacy-terms-accessibility', 'Privacy, Terms & Accessibility'],
  ['technology-scale-up', 'scaleup', 'technology-scale-up', 'Technology Scale-Up & Commercialization'],
  ['separation-solvent-recovery', 'separation', 'separation-solvent-recovery', 'Separation & Solvent Recovery'],
  ['brownfield-automation-modernization', 'modernization', 'brownfield-automation-modernization', 'Brownfield PLC & SCADA Modernization'],
  ['batch-process-automation', 'batch', 'batch-process-automation', 'Batch & Process Automation'],
  ['production-visibility-oee', 'oee', 'production-visibility-oee', 'Production Visibility & OEE'],
  ['utility-energy-monitoring', 'utilities', 'utility-energy-monitoring', 'Utility & Energy Monitoring'],
  ['applications', 'applications', 'applications', 'Applications'],
  ['website-index', 'sitemap', 'website-index', 'Website Index'],
  ['insights', 'insights', 'insights', 'Insights'],
  ['insights-plant-data-rollout', 'insight-plant-data', 'insights-plant-data-rollout', 'Plant Data People Actually Use'],
  ['insights-lab-to-pilot-to-industrial', 'insight-scaleup', 'insights-lab-to-pilot-to-industrial', 'Lab to Pilot to Industrial Scale-Up'],
  ['insights-brownfield-modernization', 'insight-brownfield', 'insights-brownfield-modernization', 'Modernize a Running Plant'],
];
const LANGS = [['', 'en', ''], ['fr', 'fr-CA', ' (FR)'], ['es', 'es-MX', ' (ES)']];

function resolve(dir, u) {
  const out = [];
  for (const x of (dir ? dir.split('/') : []).concat(u.split('/'))) { if (x === '..') out.pop(); else if (x !== '.' && x !== '') out.push(x); }
  return out.join('/');
}
// site-relative address -> WordPress token address; null = leave as is
function mapUrl(dir, u) {
  if (/^(https?:|mailto:|tel:|#|data:|%%)/.test(u)) return null;
  const m = u.match(/^([^#]*)(#.*)?$/), frag = m[2] || '';
  const r = resolve(dir, m[1]);
  if (/\.html$/.test(r)) {
    let q = r.replace(/\.html$/, '').replace(/(^|\/)index$/, '$1');
    return '%%INSTRON_HOME%%/' + (q && !q.endsWith('/') ? q + '/' : q) + frag;
  }
  if (r.startsWith('assets/')) return '%%INSTRON_THEME%%/' + r + frag;
  return null;
}
const links = (h, dir) => h.replace(/(href|src)="([^"]+)"/g, (all, a, u) => { const v = mapUrl(dir, u); return v === null ? all : a + '="' + v + '"'; });
const noTracker = h => h.replace(/<a [^>]*review-tracker\.html[^>]*>.*?<\/a>/gs, '');
const noCurrent = h => h.replace(/ aria-current="page"/g, '').replace(/aria-current="page" /g, '');
const mainOf = s => s.slice(s.indexOf('<main'), s.lastIndexOf('</main>') + 7);
const headOf = s => s.slice(s.indexOf('<head>') + 6, s.indexOf('</head>'));

function cleanMain(h, stem) {
  if (stem.endsWith('website-index')) {
    for (const t of ['Website review \\(internal\\)', 'Révision du site \\(interne\\)', 'Revisión del sitio \\(interna\\)']) {
      h = h.replace(new RegExp('<section><h2>' + t + '</h2>.*?</section>', 's'), '');
    }
  }
  return h;
}
function head(src, dir) {
  let h = headOf(src).replace(/<meta content="noindex,nofollow" name="robots"\/>/, '').replace(/<meta content="[^"]*" http-equiv="Content-Security-Policy"\/>/, '');
  h = links(h, dir);
  return h.replace(/https:\/\/instrontechnologies\.com\/([A-Za-z0-9_\-\/.]*)((?:#[A-Za-z0-9_\-]*)?)/g, (all, p, frag) => {
    if (p === '' || p.endsWith('/')) return '%%INSTRON_HOME%%/' + p + frag;
    const v = mapUrl('', p + frag); return v === null ? all : v;
  });
}
function group(src, dir) {
  const top = noCurrent(links(noTracker(src.slice(src.indexOf('<body'), src.indexOf('</header>'))), dir));
  const m = top.match(/<(button|a) [^>]*class="[^"]*is-current-group[^"]*"[^>]*>/);
  return m ? [m[0].replace(' is-current-group', ''), m[0]] : null;
}
function langLinks(src, dir) {
  const m = src.match(/<div class="lv-tb-right">(.*?)Engineer \| Embrace/s);
  return m ? links(m[1], dir) : '';
}
function headerPartial(src, dir) {
  let r = noTracker(src);
  r = links(r.slice(r.indexOf('<a class="it-skip"'), r.indexOf('</header>') + 9), dir);
  r = r.replace(/(<a class="it-skip" data-review-route=")[^"]*(" data-review-section="main" href=")[^"#]*#main"/, '$1%%INSTRON_KEY%%$2%%INSTRON_SELF%%#main"');
  r = r.replace(/(<div class="lv-tb-right">).*?(Engineer \| Embrace)/s, '$1%%INSTRON_LANGS%%$2');
  return noCurrent(r.replace(/ is-current-group/g, ''));
}
const footerPartial = (src, dir) => links(noTracker(src.slice(src.indexOf('<footer'), src.lastIndexOf('</body>'))), dir);
const md5 = s => crypto.createHash('md5').update(s, 'utf8').digest('hex');

function build(root, version, pagesFilter) {
  const read = f => fs.readFileSync(path.join(root, f), 'utf8');
  const pages = []; let order = 0;
  for (const [dir, lang, suffix] of LANGS) {
    for (const [stem, key, slug, title] of EN) {
      const file = (dir ? dir + '/' : '') + stem + '.html';
      if (pagesFilter && !pagesFilter(dir, stem)) continue;
      if (!fs.existsSync(path.join(root, file))) continue;
      const src = read(file), fullStem = (dir ? dir + '/' : '') + stem;
      const e = {
        key: (dir ? dir + ':' : '') + key,
        slug: dir ? (stem === 'index' ? dir : stem) : slug,
        stem: fullStem, lang, dir,
        parent: dir && stem !== 'index' ? dir + ':home' : null,
        title: title + suffix,
        order: order++,
        body_page: (src.match(/<body[^>]*data-page="([^"]*)"/) || [])[1],
        group: group(src, dir),
        langs: langLinks(src, dir),
        head: head(src, dir),
        main: cleanMain(links(noTracker(mainOf(src)), dir), fullStem),
      };
      e.hash = md5(e.head + e.main);
      pages.push(e);
    }
  }
  const partials = {};
  for (const [dir] of LANGS) {
    const src = read((dir ? dir + '/' : '') + 'index.html'), sfx = dir ? '-' + dir : '';
    partials['header' + sfx + '.html'] = headerPartial(src, dir);
    partials['footer' + sfx + '.html'] = footerPartial(src, dir);
  }
  return { pj: { version, source: 'instron-website-preview', pages }, partials };
}

if (require.main === module) {
  const out = process.argv[2]; const version = process.argv[3] || '0.0.0';
  if (!out) { console.error('Usage: node tools/wp_pages.js <out-dir> [version]'); process.exit(1); }
  const { pj, partials } = build(ROOT, version);
  fs.mkdirSync(path.join(out, 'content'), { recursive: true }); fs.mkdirSync(path.join(out, 'partials'), { recursive: true });
  fs.writeFileSync(path.join(out, 'content', 'pages.json'), JSON.stringify(pj, null, 1));   // no trailing newline, as installed
  for (const [f, s] of Object.entries(partials)) fs.writeFileSync(path.join(out, 'partials', f), s);
  console.log(`${pj.pages.length} pages (${['en', 'fr-CA', 'es-MX'].map(l => l + ' ' + pj.pages.filter(p => p.lang === l).length).join(', ')}), version ${version}, written to ${out}`);
}
module.exports = { build, md5 };
