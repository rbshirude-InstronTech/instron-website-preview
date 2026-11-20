"""Build a multi-page static site from the v2.5 review build, re-skinned in the live instrontechnologies.com theme.
Usage: python3 -I build.py <data.json> <assetnames.json> <theme.css> <outdir>"""
import sys, json, re, colorsys, os, html

data_path, names_path, theme_path, out = sys.argv[1:5]
d = json.load(open(data_path, encoding='utf-8'))
asset_names = json.load(open(names_path))
pages = d['pages']; texts = d['texts']

SLUG = {
 'home': 'index', 'solutions': 'solutions', 'process': 'process-skid-plants', 'pilot': 'pilot-demonstration-plants',
 'industrial': 'industrial-process-skids', 'automation': 'industrial-automation', 'planton': 'planton-digital-factory',
 'how': 'how-we-work', 'industries': 'industries', 'cleantech': 'energy-transition-critical-minerals',
 'research': 'research-technology-development', 'chemical': 'chemicals-refining-consumer-products',
 'food': 'food-beverage-dairy', 'pharma': 'pharma-life-sciences', 'manufacturing': 'industrial-manufacturing',
 'portfolio': 'project-portfolio', 'cases': 'case-studies', 'company': 'our-company', 'global': 'global-presence',
 'leadership': 'leadership', 'trust': 'trust-responsibility', 'careers': 'careers', 'contact': 'contact',
 'legal': 'privacy-terms-accessibility', 'scaleup': 'technology-scale-up', 'separation': 'separation-solvent-recovery',
 'modernization': 'brownfield-automation-modernization', 'batch': 'batch-process-automation', 'oee': 'production-visibility-oee',
 'utilities': 'utility-energy-monitoring', 'applications': 'applications', 'sitemap': 'website-index'}
assert set(SLUG) == set(pages), set(pages) ^ set(SLUG)
def href_for(page, section=''):
    f = SLUG.get(page, 'index') + '.html'
    return f + ('#' + section if section else '')

# ---------------- colour remapping (review navy system -> live blue/green/grey system) ----------------
EXACT = {'c4451c': '0979ae', '5cba3c': '61ce70', '3f8f22': '38aa3d', '2d6ab4': '0979ae', '6cc64d': '4ac150', '102d19': 'ffffff'}
def remap_rgb(r, g, b, prop):
    key = '%02x%02x%02x' % (r, g, b)
    if key == '1a3668':
        return (0x21, 0x21, 0x21) if prop == 'color' else (0x09, 0x79, 0xae)
    if key in EXACT:
        v = EXACT[key]; return tuple(int(v[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255); H = h*360
    if s < 0.06: return (r, g, b)
    if 185 <= H <= 245:
        if l >= 0.88 or s < 0.30:              # light tints and slate greys -> neutral greys
            gv = round(l*255); return (gv, gv, gv)
        if prop == 'color' and l < 0.40:
            return (0x21, 0x21, 0x21)
        rr, gg, bb = colorsys.hls_to_rgb(199/360, max(l, 0.17), 0.9)
        return (round(rr*255), round(gg*255), round(bb*255))
    if 80 <= H <= 160:
        rr, gg, bb = colorsys.hls_to_rgb(128/360, l, min(s, 0.55))
        return (round(rr*255), round(gg*255), round(bb*255))
    return (r, g, b)

HEX = re.compile(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b')
RGBA = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+%?)\s*)?\)')
def recolor_value(val, prop):
    prop = prop.lower()
    shadow = 'shadow' in prop
    if prop == 'color':
        val = val.replace('var(--navy)', '#212121')
    def hx(m):
        s = m.group(1); alpha = ''
        if len(s) in (3, 4):
            alpha = s[3]*2 if len(s) == 4 else ''; s = ''.join(c*2 for c in s[:3])
        elif len(s) == 8:
            alpha = s[6:]; s = s[:6]
        r, g, b = (int(s[i:i+2], 16) for i in (0, 2, 4))
        if shadow: nr = (0, 0, 0) if 185 <= colorsys.rgb_to_hls(r/255, g/255, b/255)[0]*360 <= 245 else (r, g, b)
        else: nr = remap_rgb(r, g, b, prop)
        return '#%02x%02x%02x%s' % (*nr, alpha)
    def rg(m):
        r, g, b, a = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        if shadow: nr = (0, 0, 0)
        else: nr = remap_rgb(r, g, b, 'bg')   # translucent tints/overlays: treat as non-text
        return ('rgba(%d,%d,%d,%s)' % (*nr, a)) if a is not None else ('rgb(%d,%d,%d)' % nr)
    val = HEX.sub(hx, val)
    val = RGBA.sub(rg, val)
    return val

DECL = re.compile(r'([{;\s])([-a-zA-Z]+)\s*:\s*([^;{}]+)')
FONT_RE = re.compile(r'"IBM Plex Sans"|\'IBM Plex Sans\'|IBM Plex Sans|Calibri|"Inter Tight"|Inter Tight|"Fraunces"|Fraunces')
def process_css(css, img_prefix):
    css = re.sub(r'@font-face\s*\{[^}]*IBM Plex[^}]*\}', '', css)
    def decl(m):
        lead, prop, val = m.groups()
        if 'data:' in val and 'url(' in val and prop not in ('color',):
            return m.group(0)
        val = recolor_value(val, prop)
        if prop in ('font-family', 'font'):
            val = FONT_RE.sub('Roboto', val)
        return f'{lead}{prop}:{val}'
    css = DECL.sub(decl, '{' + css)[1:]
    css = re.sub(r'__INSTRON_EMBED_ASSET_[a-f0-9]{64}__', lambda m: img_prefix + asset_names[m.group(0)], css)
    return css

def process_inline_style(s):
    return process_css(s, 'assets/img/')

# ---------------- write shared assets ----------------
os.makedirs(f'{out}/assets/css', exist_ok=True); os.makedirs(f'{out}/assets/js', exist_ok=True)
text_files = {}
for k, v in texts.items():
    short = k[len('__INSTRON_EMBED_TEXT_'):][:10]
    if v.lstrip().startswith('/* Offline review interactions'):
        fn = f'assets/js/site-{short}.js'
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(v)
    else:
        fn = f'assets/css/{short}.css'
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(process_css(v, '../img/'))
    text_files[k] = fn
open(f'{out}/assets/css/live-theme.css', 'w', encoding='utf-8').write(open(theme_path, encoding='utf-8').read())

# ---------------- shared header / footer ----------------
ICON = {
 'phone': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
}
SOLID = {
 'mail': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 5.5A1.5 1.5 0 0 1 3.5 4h17A1.5 1.5 0 0 1 22 5.5v.4l-10 6.3L2 5.9zM2 8.2v10.3A1.5 1.5 0 0 0 3.5 20h17a1.5 1.5 0 0 0 1.5-1.5V8.2l-9.5 6a1 1 0 0 1-1 0z"/></svg>',
 'phone': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>',
}
TOPBAR = ('<div class="lv-preview-note">Theme preview: new website content (review build v2.5) shown in the current live-site look. Not indexed.</div>'
  '<div class="lv-topbar"><div class="lv-wrap lv-tb-row"><div class="lv-tb-left">'
  f'<a href="tel:+16478743958">{ICON["phone"]}+1 (647) 874-3958</a>'
  f'<a href="mailto:sales@instrontechnologies.ca">{ICON["mail"]}sales@instrontechnologies.ca</a>'
  f'<span>{ICON["pin"]}Toronto · Pune</span></div>'
  '<div class="lv-tb-right">Engineer | Embrace | Elevate</div></div></div>')

home_html = pages['home']['html']
review_header = re.search(r'<header class="it-header">.*?</header>', home_html, re.S).group(0)
review_footer = re.search(r'<footer class="it-footer">.*?</footer>', home_html, re.S).group(0)
logo = re.search(r'src="(__INSTRON_EMBED_ASSET_afd2b6d3[a-f0-9]+__)"', review_header).group(1)

hdr = review_header.replace('<header class="it-header">', '<header class="it-header lv-header">', 1)
hdr = hdr.replace('<span class="it-tagline">Engineer | Embrace | Elevate</span>', '', 1)
hdr = hdr.replace('<div class="it-group">', '<a class="lv-home" data-review-route="home" href="#">Home</a><div class="it-group">', 1)
hdr = hdr.replace('</nav>', '</nav><a class="lv-search" data-review-route="sitemap" href="#" aria-label="Find a page (Website Index)">'
                  '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg></a>', 1)
HEADER = TOPBAR + hdr

cols = re.findall(r'<section><h2>.*?</section>', review_footer, re.S)
regional = re.search(r'<strong>Regional presence</strong>.*?(?=</div><div class="v22-badge">)', review_footer, re.S).group(0)
badge_src = re.search(r'<div class="v22-badge"><img[^>]*src="([^"]+)"', review_footer).group(1)
FOOTER = (
 '<section class="lv-contact-band" aria-label="Contact Instron Technologies"><div class="lv-wrap lv-cb-grid">'
 f'<div>{SOLID["mail"]}<h3>Email</h3><p><a href="mailto:sales@instrontechnologies.ca">sales@instrontechnologies.ca</a><br/><a href="mailto:sales@instrontechnologies.com">sales@instrontechnologies.com</a></p></div>'
 f'<div>{SOLID["phone"]}<h3>Contact</h3><p>Toronto: <a href="tel:+16478743958">+1 (647) 874-3958</a><br/>Pune: <a href="tel:+917028015958">+91 70280 15958</a></p></div>'
 f'<div>{SOLID["pin"]}<h3>Company offices</h3><p>Toronto, Ontario, Canada<br/>Pune, Maharashtra, India</p></div>'
 '</div></section>'
 '<footer class="lv-footer"><div class="lv-wrap lv-f-grid">'
 f'<div class="lv-f-brand"><img alt="Instron Technologies" src="{logo}" width="720" height="379" loading="lazy"/>'
 '<p class="lv-f-name">Instron Technologies</p><p class="lv-f-tag">Engineer | Embrace | Elevate</p>'
 f'{regional}</div>'
 f'<div class="lv-f-cols">{"".join(cols)}</div>'
 f'<div class="lv-f-badge"><img alt="Ontario Made — Fabriqué en Ontario" src="{badge_src}" width="96" height="96" loading="lazy"/><p>Ontario Made applies to systems built in Ontario.</p></div>'
 '</div><div class="lv-wrap lv-f-bottom">'
 '<span class="lv-pill">© 2026 Instron Technologies · Engineering since 2013</span>'
 '<a class="lv-pill" data-review-route="sitemap" href="#">Website Index</a>'
 '<span class="lv-pill">Independent company, not affiliated with Instron® (ITW)</span>'
 '</div></footer>')

# ---------------- page assembly ----------------
ROUTE_A = re.compile(r'<a\b([^>]*?)\bdata-review-route="([^"]*)"([^>]*)>')
def fix_links(h):
    def rep(m):
        attrs = m.group(1) + 'data-review-route="' + m.group(2) + '"' + m.group(3)
        sec = re.search(r'data-review-section="([^"]*)"', attrs)
        new = href_for(m.group(2), sec.group(1) if sec else '')
        attrs = re.sub(r'\bhref="[^"]*"', 'href="' + new + '"', attrs)
        if 'href=' not in attrs: attrs += ' href="' + new + '"'
        attrs = attrs.replace(' target="_top"', '')
        return '<a' + attrs + '>'
    h = ROUTE_A.sub(rep, h)
    h = h.replace('__INSTRON_REVIEW_URL__', 'index.html')
    return h

def recolor_html(h):
    h = re.sub(r'(<style\b[^>]*>)(.*?)(</style>)', lambda m: m.group(1) + process_css(m.group(2), 'assets/img/') + m.group(3), h, flags=re.S)
    h = re.sub(r'\bstyle="([^"]*)"', lambda m: 'style="' + process_inline_style(html.unescape(m.group(1))).replace('"', '&quot;') + '"', h)
    h = re.sub(r'\b(fill|stroke|stop-color|color)="([^"]+)"', lambda m: f'{m.group(1)}="{recolor_value(m.group(2), "fill")}"', h)
    return h

import hashlib
VER = hashlib.sha1(open(theme_path,'rb').read()+open(__file__,'rb').read()).hexdigest()[:8]
report = []
for key, p in pages.items():
    h = p['html']
    h = re.sub(r'<header class="it-header">.*?</header>', lambda m: HEADER, h, count=1, flags=re.S)
    h = re.sub(r'<footer class="it-footer">.*?</footer>', lambda m: FOOTER, h, count=1, flags=re.S)
    # shared text blocks -> linked files
    def styletag(m):
        tok = m.group(2); attrs = m.group(1)
        return f'<link rel="stylesheet" href="{text_files[tok]}"{attrs}/>'
    h = re.sub(r'<style([^>]*)>(__INSTRON_EMBED_TEXT_[a-f0-9]{64}__)</style>', styletag, h)
    h = re.sub(r'<script>(__INSTRON_EMBED_TEXT_[a-f0-9]{64}__)</script>', lambda m: f'<script src="{text_files[m.group(1)]}" defer></script>', h)
    h = h.replace('__INSTRON_REVIEW_BRIDGE__', '')
    h = recolor_html(h)
    h = re.sub(r'__INSTRON_EMBED_ASSET_[a-f0-9]{64}__', lambda m: 'assets/img/' + asset_names[m.group(0)], h)
    h = fix_links(h)
    # mark current page in nav
    cur = href_for(key)
    h = re.sub(r'(<a\b[^>]*href="' + re.escape(cur) + r'")', r'\1 aria-current="page"', h)
    h = h.replace('</head>', '<link rel="stylesheet" href="assets/css/live-theme.css"/><link rel="icon" href="assets/img/afd2b6d3f3.png"/></head>', 1)
    h = re.sub(r'((?:href|src)="assets/(?:css|js)/[^"?]+)"', r'\1?v=' + VER + '"', h)
    leftovers = re.findall(r'__INSTRON_[A-Z_]+', h)
    report.append((key, len(h), leftovers[:3]))
    open(f'{out}/{SLUG[key]}.html', 'w', encoding='utf-8').write(h)
for r in report: print(r)
