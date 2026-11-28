"""v2.51: look-and-feel and template fixes from the live-site QA (28 Nov 2026).

Source: project doc claude/live-site-qa-look-feel-template-2026-11-28.md
Usage: python3 -I tools/v251_lookfeel.py <repo root>   (refuses to run twice)

Pages (EN, FR, ES):
- T2  Gallery moved above the closing band (Process Skid Plants, Pilot & Demonstration, Industrial Process Skids)
- T5  Generic hero tag row (.hero-foot) removed; "01 / " numbers dropped from section eyebrows
- V5  "Read the case" -> "Read the case study" (ES "Leer el caso" -> "Leer el caso de estudio")
- V6  Clip-art "Mixing Tanks" illustration replaced by the CIP HMI screenshot (Food, Batch)
- V7  Website Index: three cards that repeated their title get the page's own search description
CSS (assets/css/live-theme.css, section 14): T1 one closing card, T3 heading scale, V1 testimonials,
V2 founders, V3 Insights read time, V9 13 px minimum, M1 IRA launcher, M2 IRA prompt, M3 "Contacto".
"""
import sys, os, re, glob, hashlib, html

ROOT = os.path.abspath(sys.argv[1])
CSS_PATH = os.path.join(ROOT, 'assets/css/live-theme.css')
css = open(CSS_PATH, encoding='utf-8').read()
if 'v2.51' in css:
    sys.exit('v2.51 already applied')

OLD_VER = '5fa8f118'
LANGS = {'': 'en', 'fr/': 'fr', 'es/': 'es'}
CLIP = 'b57548b00a.webp'
HMI = '013c2e66e2.webp'

def rd(p): return open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s): open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)

def meta_desc(s):
    m = re.search(r'<meta content="([^"]*)" name="description"', s) or re.search(r'<meta name="description" content="([^"]*)"', s)
    return m.group(1)

def hmi_alt(lang):
    s = rd(lang + 'industrial-automation.html')
    return re.search(r'<img alt="([^"]*)"[^>]*src="(?:\.\./)?assets/img/' + re.escape(HMI), s).group(1)

log = []
# ---------------------------------------------------------------- CSS
CSS = r'''
/* 14 v2.51 look-and-feel fixes (live-site QA, 28 Nov 2026) */
/* T1 one closing call-to-action design on every page: the Home white card, photo right, green diagonal */
html body#top main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home){background:#fff!important;border:1px solid #e3e3e3!important;border-radius:10px!important;box-shadow:0 14px 36px rgba(10,40,60,.08)!important;color:#212121!important}
html body#top main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home) h2{color:#212121!important}
html body#top main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home) :is(p,li){color:#5f5f5f!important}
html body#top main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home) :is(.eyebrow,.k){color:#0979ae!important;text-transform:uppercase!important;letter-spacing:.08em!important;font-size:13px!important;font-weight:700!important}
html body#top main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home) .pon-p{color:#212121!important}
/* page-relevant photo: control panels on automation pages, the OEE dashboard on PlantON pages */
html body#top:is([data-page="automation"],[data-page="batch"],[data-page="modernization"],[data-page="insight-brownfield"]) main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home)::after{background-image:url(../img/aac961337e.webp)!important;background-position:center!important}
html body#top:is([data-page="planton"],[data-page="oee"],[data-page="utilities"],[data-page="insight-plant-data"]) main>section:is(.closing-band,.closing-section,.ab-close):not(#discuss-your-project-home)::after{background-image:url(../img/318bb83539.webp)!important;background-position:left top!important;background-color:#fff!important}
/* T3 one heading scale: section headings 40 px, card titles 20 px, feature cards 24 px */
html body#top main#main h2{font-size:clamp(30px,2.9vw,40px)!important;line-height:1.18!important}
html body#top main#main .in-article .in-body h2{font-size:clamp(24px,2.2vw,30px)!important}
html body#top main#main h3{font-size:20px!important;line-height:1.3!important}
html body#top main#main :is(.detail-card,.app-pillar,.cs-head,.presence-card,.ph-side,.it-page-card,.beyond-tile,.ab-ppcard,.mk-who-card,.project-slot-info,.sol3-body,.work-card,.flagship-mini-heading,.tile) h3{font-size:24px!important;line-height:1.25!important}
html body#top main#main .ab-coreperson h3{font-size:18px!important}
@media(max-width:600px){
 html body#top main#main h3{font-size:18px!important}
 html body#top main#main :is(.detail-card,.app-pillar,.cs-head,.presence-card,.ph-side,.it-page-card,.beyond-tile,.ab-ppcard,.mk-who-card,.project-slot-info,.sol3-body,.work-card,.flagship-mini-heading,.tile) h3{font-size:20px!important}
}
/* V1 testimonials on the page grid; a last card alone on its row spans the row; a single quote uses the full width */
html body#top .ts-wrap{max-width:none;width:min(1240px,calc(100% - 2*max(4vw,20px)));padding:0;margin:0 auto;box-sizing:border-box}
@media(min-width:1001px){html body#top .ts-grid>.ts-card:last-child:nth-child(3n+1){grid-column:1/-1}}
@media(min-width:641px) and (max-width:1000px){html body#top .ts-grid>.ts-card:last-child:nth-child(2n+1){grid-column:1/-1}}
html body#top .ts-single .ts-card{max-width:none}
/* V2 founders across the full width */
@media(min-width:701px){html body#top .ab-founders.v246-founders{max-width:none}}
/* V3 Insights cards: space before the read time */
html body .in-card span i{margin-left:.45em}
/* V9 small meta text no smaller than 13 px */
html body#top main :is(.sx-meta,.cs-meta,.pf-meta,.pf-ind,.pf-sol,.ph-label,.pv-law,.ms-range,.work-label,.v22-tag,.cs-tags li,.pf-tags li,.ab-coreperson small,.ab-box small,.pt-body small,.in-short .k,.in-toc .k){font-size:13px!important}
html body#top main small{font-size:max(13px,.8em)}
/* M1 phones: the IRA launcher shrinks to its badge (the label stays for screen readers) */
@media(max-width:600px){
 html body .ira-launcher{padding:8px!important;gap:0!important;right:12px!important;bottom:12px!important}
 html body .ira-launcher .ira-launch-t{position:absolute!important;width:1px!important;height:1px!important;overflow:hidden!important;clip:rect(0 0 0 0)!important;white-space:nowrap!important}
}
/* M2 phones: the "Not sure this fits your process?" card stacks */
@media(max-width:640px){
 html body#top .ira-band .ira-band-wrap{flex-direction:column!important;align-items:flex-start!important}
 html body#top .ira-band .ira-band-wrap>div{width:100%!important;flex:none!important}
}
/* M3 Spanish phone header button */
@media(max-width:600px){html[lang="es-MX"] body .lv-header .it-cta::after{content:"Contacto"}}
'''
css = css.rstrip('\n') + '\n' + CSS.lstrip('\n')
open(CSS_PATH, 'w', encoding='utf-8').write(css)

# release stamp for every CSS/JS link
hsh = hashlib.md5()
for p in sorted(glob.glob(os.path.join(ROOT, 'assets/css/*.css')) + glob.glob(os.path.join(ROOT, 'assets/js/*.js'))):
    hsh.update(open(p, 'rb').read())
NEW_VER = hsh.hexdigest()[:8]

# ---------------------------------------------------------------- pages
pages = [p for p in glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, 'fr/*.html')) + glob.glob(os.path.join(ROOT, 'es/*.html'))]
for full in sorted(pages):
    rel = os.path.relpath(full, ROOT)
    lang = rel[:3] if rel[:3] in ('fr/', 'es/') else ''
    name = rel[len(lang):]
    s0 = s = rd(rel)
    s = s.replace('?v=' + OLD_VER, '?v=' + NEW_VER)
    # T2 gallery above the closing band
    if name in ('process-skid-plants.html', 'pilot-demonstration-plants.html', 'industrial-process-skids.html'):
        j = s.find('<section class="closing-band">')
        i = s.find('<section aria-label="', j)
        assert j > 0 and i > 0 and 'instron-image-gallery' in s[i:i + 200], rel
        e = s.find('</section>', i) + len('</section>')
        assert '<section' not in s[i + 8:e], rel
        jend = s.find('</section>', j) + len('</section>')
        assert jend == i, rel  # gallery follows the band directly
        s = s[:j] + s[i:e] + s[j:i] + s[e:]
        log.append(f'T2 {rel}')
    # T5 hero tag row and eyebrow numbers
    s, n = re.subn(r'<div class="hero-foot container">(?:<span>[^<]*</span>)+</div>', '', s)
    if n: log.append(f'T5 hero-foot {rel}')
    s, n = re.subn(r'(<p class="eyebrow dark">)\d\d / ', r'\1', s)
    if n: log.append(f'T5 eyebrow numbers x{n} {rel}')
    # V5 link labels
    if lang == '':
        s = s.replace('>Read the case<', '>Read the case study<')
    if lang == 'es/':
        s = s.replace('>Leer el caso<', '>Leer el caso de estudio<')
    # V6 clip-art
    if CLIP in s:
        alt = hmi_alt(lang)
        def rep(m):
            t = m.group(0)
            t = re.sub(r'alt="[^"]*"', 'alt="' + alt + '"', t)
            t = t.replace(CLIP, HMI)
            t = re.sub(r'width="\d+"', 'width="1100"', t)
            t = re.sub(r'height="\d+"', 'height="620"', t)
            return t
        s, n = re.subn(r'<img[^>]*' + re.escape(CLIP) + r'[^>]*>', rep, s)
        log.append(f'V6 x{n} {rel}')
    # V7 website index
    if name == 'website-index.html':
        for slug in ('process-skid-plants', 'pilot-demonstration-plants', 'industrial-process-skids'):
            desc = meta_desc(rd(lang + slug + '.html'))
            pat = r'(<a class="it-page-card"[^>]*href="' + slug + r'\.html"><h3>([^<]+)</h3><p>)([^<]+)(</p>)'
            m = re.search(pat, s)
            assert m and html.unescape(m.group(2)).strip() == html.unescape(m.group(3)).strip(), (rel, slug)
            s = s[:m.start()] + m.group(1) + desc + m.group(4) + s[m.end():]
        log.append(f'V7 {rel}')
    if s != s0:
        wr(rel, s)

print('stamp', OLD_VER, '->', NEW_VER)
print('\n'.join(log))
