"""v2.52: one banner style per page type (Rahul, 27 Nov 2026).

Usage: python3 -I tools/v252_banners.py <repo root>   (refuses to run twice)

- Process Skid Plants, Pilot & Demonstration Plants and Industrial Process Skids get the navy split banner
  (text left, photo right) already used on Industrial Automation, PlantON and the industry pages.
- Solutions, Applications and Industries banners get the same height; Applications gets a one-line intro
  (the list of applications, from the page's own approved search description, EN/FR/ES).
- New release stamp for CSS/JS.
"""
import sys, os, re, glob, hashlib

ROOT = os.path.abspath(sys.argv[1])
CSS_PATH = os.path.join(ROOT, 'assets/css/live-theme.css')
css = open(CSS_PATH, encoding='utf-8').read()
if 'v2.52' in css:
    sys.exit('v2.52 already applied')
OLD_VER = re.search(r'live-theme\.css\?v=([a-f0-9]{8})', open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()).group(1)

INTRO = {
    '': 'Technology scale-up, separation and solvent recovery, brownfield modernization, batch automation, OEE and utility monitoring.',
    'fr/': 'Mise à l’échelle des technologies, séparation et récupération de solvants, modernisation sur site existant, automatisation des lots, TRG (OEE) et suivi des utilités.',
    'es/': 'Escalamiento de tecnología, separación y recuperación de solventes, modernización de plantas existentes, automatización de lotes, OEE y monitoreo de servicios auxiliares.',
}

CSS = r'''
/* 15 v2.52 one banner style per page type */
/* Process Skid Plants family: the navy split banner of Industrial Automation, PlantON and the industry pages */
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .review-hero-grid{display:grid!important;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr)!important;gap:48px!important;align-items:center!important;max-width:1240px!important;width:calc(100% - 48px)!important;margin:0 auto!important;padding:0 0 40px!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .hero-copy{text-align:left!important;margin:0!important;max-width:none!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero :is(p,li,.intro,h1,.minibreadcrumb,.eyeline){margin-left:0!important;margin-right:0!important;text-align:left!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .eyeline{font-size:18px!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .intro{font-size:17px!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .cta-row{justify-content:flex-start!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .review-hero-photo{position:relative!important;inset:auto!important;z-index:auto!important;border-radius:8px!important;overflow:hidden!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .review-hero-photo img{position:static!important;width:100%!important;height:auto!important;max-height:340px!important;object-fit:cover!important;border-radius:8px!important}
html body#top .lv-topbar~main>.solution-hero.sx-split-hero .review-hero-photo::after{display:none!important}
@media(max-width:900px){
 html body#top .lv-topbar~main>.solution-hero.sx-split-hero .review-hero-grid{grid-template-columns:1fr!important;gap:28px!important;padding-bottom:48px!important}
 html body#top .lv-topbar~main>.solution-hero.sx-split-hero .eyeline{font-size:15px!important}
}
/* Solutions, Applications and Industries: the same banner height, text centred in it */
@media(min-width:701px){
 html body#top .lv-topbar~main>.it-index-hero .review-hero-grid.review-hero-grid{display:flex!important;flex-direction:column!important;justify-content:center!important;min-height:220px!important}
}
'''
css = css.rstrip('\n') + '\n' + CSS.lstrip('\n')
open(CSS_PATH, 'w', encoding='utf-8').write(css)

hsh = hashlib.md5()
for p in sorted(glob.glob(os.path.join(ROOT, 'assets/css/*.css')) + glob.glob(os.path.join(ROOT, 'assets/js/*.js'))):
    hsh.update(open(p, 'rb').read())
NEW_VER = hsh.hexdigest()[:8]

log = []
for full in sorted(glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, 'fr/*.html')) + glob.glob(os.path.join(ROOT, 'es/*.html'))):
    rel = os.path.relpath(full, ROOT)
    lang = rel[:3] if rel[:3] in ('fr/', 'es/') else ''
    name = rel[len(lang):]
    s0 = s = open(full, encoding='utf-8').read()
    s = s.replace('?v=' + OLD_VER, '?v=' + NEW_VER)
    if name in ('process-skid-plants.html', 'pilot-demonstration-plants.html', 'industrial-process-skids.html'):
        s, n = re.subn(r'<section class="solution-hero review-hero-section">', '<section class="solution-hero review-hero-section sx-split-hero">', s, count=1)
        assert n == 1, rel
        log.append('split ' + rel)
    if name == 'applications.html':
        pat = r'(<section class="it-index-hero review-hero-section"><div class="it-wrap review-hero-grid"><div class="hero-copy"><h1>[^<]+</h1>)(</div>)'
        s, n = re.subn(pat, r'\1<p class="hero-lede">' + INTRO[lang] + r'</p>\2', s, count=1)
        assert n == 1, rel
        log.append('intro ' + rel)
    if s != s0:
        open(full, 'w', encoding='utf-8').write(s)
print('stamp', OLD_VER, '->', NEW_VER)
print('\n'.join(log))
