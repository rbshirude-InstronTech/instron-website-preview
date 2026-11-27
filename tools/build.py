"""Build a multi-page static site from the review build, re-skinned in the live instrontechnologies.com theme.
Usage: python3 -I build.py <data.json> <assetnames.json> <theme.css> <outdir>"""
import sys, json, re, colorsys, os, html

data_path, names_path, theme_path, out = sys.argv[1:5]
d = json.load(open(data_path, encoding='utf-8'))
asset_names = json.load(open(names_path))
pages = d['pages']; texts = d['texts']
# v2.24: .com is the only sales address (Rahul, 24 Nov)
EMAIL_FIX = lambda h: h.replace('sales@instrontechnologies.ca', 'sales@instrontechnologies.com')

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
 'utilities': 'utility-energy-monitoring', 'applications': 'applications', 'sitemap': 'website-index',
 'insights': 'insights', 'insight-plant-data': 'insights-plant-data-rollout', 'insight-scaleup': 'insights-lab-to-pilot-to-industrial',
 'insight-brownfield': 'insights-brownfield-modernization'}
assert set(SLUG) == set(pages), set(pages) ^ set(SLUG)
def href_for(page, section=''):
    f = SLUG.get(page, 'index') + '.html'
    return f + ('#' + section if section else '')

# ---------------- colour remapping (review navy system -> live blue/green/grey system) ----------------
EXACT = {'c4451c': '0979ae', '5cba3c': '61ce70', '3f8f22': '38aa3d', '2d6ab4': '0979ae', '6cc64d': '4ac150', '102d19': 'ffffff'}
def remap_rgb(r, g, b, prop):
    out = _remap_rgb(r, g, b, prop)
    return _text_contrast(out) if prop == 'color' else out

def _text_contrast(rgb):
    """QA fix (v2.8): text colours that fell short of WCAG AA after the theme remap.
    Mid blues -> darker live blue, mid greens -> dark green, mid greys -> #5f5f5f, light blue-greys -> white."""
    r, g, b = rgb; h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255); H = h*360
    if s < 0.06:
        if 0.40 <= l <= 0.56: return (0x5f, 0x5f, 0x5f)
        if 0.82 <= l < 0.99: return (0xff, 0xff, 0xff)
        return rgb
    if 185 <= H <= 215:
        if 0.28 <= l <= 0.60: return (0x06, 0x61, 0x8c)
        if l >= 0.70: return (0xff, 0xff, 0xff)
    if 100 <= H <= 145 and 0.30 <= l <= 0.58:
        return (0x2b, 0x7d, 0x30)
    return rgb

def _remap_rgb(r, g, b, prop):
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
        open(f'{out}/{fn}', 'w', encoding='utf-8').write(EMAIL_FIX(v))
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
TOPBAR = ('<div class="lv-topbar"><div class="lv-wrap lv-tb-row"><div class="lv-tb-left">'
  f'<a href="mailto:sales@instrontechnologies.com">{ICON["mail"]}sales@instrontechnologies.com</a>'
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
 f'<div>{SOLID["mail"]}<h3>Email</h3><p><a href="mailto:sales@instrontechnologies.com">sales@instrontechnologies.com</a></p></div>'
 f'<div>{SOLID["pin"]}<h3>Company offices</h3><p>Toronto, Ontario, Canada<br/>Pune, Maharashtra, India</p></div>'
 '<div class="lv-follow"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 16a3 3 0 0 0-2.2 1l-7-3.9a3 3 0 0 0 0-2.2l7-3.9A3 3 0 1 0 15 5.5l-7 3.9a3 3 0 1 0 0 5.2l7 3.9A3 3 0 1 0 18 16z"/></svg><h3>Follow us</h3><ul class="lv-social" aria-label="Instron Technologies on social media"><li><a href="https://www.linkedin.com/company/instrontechnologies/" target="_blank" rel="noopener noreferrer" aria-label="Instron Technologies on LinkedIn (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.6c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9V21H9z"/></svg></a></li><li><a href="https://www.youtube.com/@instrontechnologiesllp6630" target="_blank" rel="noopener noreferrer" aria-label="Instron Technologies on YouTube (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.8 15.1V8.9l5.8 3.1z"/></svg></a></li><li><a href="https://www.instagram.com/instrontechnologies0510/" target="_blank" rel="noopener noreferrer" aria-label="Instron Technologies on Instagram (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm5 3.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zm0 2a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zm5.3-4.1a1.3 1.3 0 1 1 0 2.6 1.3 1.3 0 0 1 0-2.6z"/></svg></a></li><li><a href="https://www.facebook.com/InstronTech" target="_blank" rel="noopener noreferrer" aria-label="Instron Technologies on Facebook (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8.5V6.8c0-.8.2-1.3 1.4-1.3H17V2.2c-.3 0-1.3-.2-2.5-.2-2.5 0-4.2 1.5-4.2 4.3v2.2H7.5V12h2.8v10H14V12h2.8l.4-3.5z"/></svg></a></li><li><a href="https://x.com/InstronTech" target="_blank" rel="noopener noreferrer" aria-label="Instron Technologies on X (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.2-8.3L1.8 3h6.4l4.4 5.8zm-1.1 16.2h1.7L7.4 4.7H5.6z"/></svg></a></li></ul></div>'
 '</div></section>'
 '<footer class="lv-footer"><div class="lv-wrap lv-f-grid">'
 f'<div class="lv-f-brand"><img alt="Instron Technologies" src="{logo}" width="720" height="379" loading="lazy"/>'
 '<p class="lv-f-name">Instron Technologies</p><p class="lv-f-tag">Engineer | Embrace | Elevate</p>'
 f'{regional}</div>'
 f'<div class="lv-f-cols">{"".join(cols)}</div>'
 f'<div class="lv-f-badge"><img alt="Ontario Made | Fabriqué en Ontario" src="{badge_src}" width="96" height="96" loading="lazy"/><p>Ontario Made applies to systems built in Ontario.</p></div>'
 '</div><div class="lv-wrap lv-f-bottom">'
 '<span class="lv-f-note">© 2026 Instron Technologies · Engineering since 2013</span>'
 '<a class="lv-f-note" data-review-route="sitemap" href="#">Website Index</a>'
 '<span class="lv-f-note">Independent company, not affiliated with Instron® (ITW)</span>'
 '<span class="lv-f-note">PlantON<sup class="pon-tm">™</sup> is a trademark of Instron Technologies Inc.</span>'
 '</div></footer>')

# v2.35 footer (Sumit 26 Nov, approved): regional locations as chips, upcoming presence as a dashed chip
def _chips(m, cls=''):
    items = [x.strip() for x in re.split(r'\s*·\s*', m.group(2)) if x.strip()]
    return m.group(1) + f'<ul class="lv-chips{cls}">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
FOOTER = re.sub(r'(<strong>Regional presence</strong>)<p>(.*?)</p>', _chips, FOOTER, count=1, flags=re.S)
FOOTER = re.sub(r'(<strong>Upcoming presence</strong>)<p>(.*?)</p>', lambda m: _chips(m, ' lv-up'), FOOTER, count=1, flags=re.S)
assert FOOTER.count('class="lv-chips') == 2, 'v2.35 footer chips not applied'

# v2.25 bottom of page (Rahul, 24 Nov): one navy footer with the contact row inside, Back to top in the legal line,
# footer duplicates removed; Home closing banner becomes a card with tightened copy and an email route.
def V225(h, key):
    import re as _re
    m = _re.search(r'<section class="lv-contact-band"[^>]*>(.*?)</section>(<footer class="lv-footer">)', h, _re.S)
    if m:
        h = h[:m.start()] + m.group(2) + m.group(1) + h[m.end():]
    h = h.replace('<p class="lv-f-name">Instron Technologies</p>', '')
    h = _re.sub(r'<p><a data-review-route="global" href="global-presence\.html"[^>]*>Global presence</a></p>', '', h)
    h = _re.sub(r'(<li><a data-review-route="contact" href="contact\.html"[^>]*>)Discuss Your Project(</a></li></ul></section></div><div class="lv-f-badge">)', r'\1Contact\2', h)
    h = _re.sub(r'<a class="lv-f-note" data-review-route="sitemap" href="website-index\.html"[^>]*>Website Index</a>', '', h)
    if 'class="lv-top"' not in h:
        h = h.replace('</div></footer>', '<a class="lv-top" href="#top">Back to top ↑</a></div></footer>', 1)
    if key == 'home':
        h = h.replace('<p class="closing-overline">DISCUSS YOUR PROJECT</p>', '<p class="closing-overline">LET’S GROW TOGETHER</p>', 1)
        h = h.replace('Whether you are developing a new technology, planning a pilot or demonstration plant, or evaluating an industrial process skid, our engineering team can help you define the next steps.',
                      'Whether you are developing a new technology, planning a pilot or demonstration plant, specifying an industrial skid or modernizing an operating plant, our engineering team will help you define the next step.', 1)
        h = _re.sub(r'<a class="closing-secondary btn btn-outline" data-review-route="how" href="how-we-work\.html"[^>]*>Explore How We Work</a>',
                    '<span class="cta-mail">or email <a href="mailto:sales@instrontechnologies.com">sales@instrontechnologies.com</a></span>', h, count=1)
    return h

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
# IRA page finder (25 Nov): one deferred script on every page. It does nothing unless the address has ?ira=1,
# except carrying an IRA brief into the Contact form. Files live in assets/ira/ (kept in the repo, not generated).
_ira_files = [os.path.join(out, 'assets', 'ira', f) for f in ('ira.js', 'ira.css')]
IRA_VER = hashlib.sha1(b''.join(open(f, 'rb').read() for f in _ira_files if os.path.exists(f))).hexdigest()[:8]
def IRA(h):
    if not all(os.path.exists(f) for f in _ira_files) or 'assets/ira/ira.js' in h:
        return h
    return h.replace('</body>', f'<script src="assets/ira/ira.js?v={IRA_VER}" defer></script></body>', 1)
report = []
for key, p in pages.items():
    h = p['html']
    # v2.23 (M4): highlight the menu group this page sits under, as marked in the review build's own header
    grp = re.search(r'<button aria-controls="(it-menu-\d+)"[^>]*class="it-trigger is-current-group"', h)
    page_header = HEADER
    if grp:
        tag = f'<button aria-controls="{grp.group(1)}" aria-expanded="false" class="it-trigger" type="button">'
        assert page_header.count(tag) == 1, (key, tag)
        page_header = page_header.replace(tag, tag.replace('class="it-trigger"', 'class="it-trigger is-current-group"'))
    h = re.sub(r'<header class="it-header">.*?</header>', lambda m: page_header, h, count=1, flags=re.S)
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
    # v2.29: How We Work is a direct menu link (no sub-menu); highlight it like a current menu group
    h = re.sub(r'class="it-trigger it-direct"([^>]*aria-current="page")', r'class="it-trigger it-direct is-current-group"\1', h)
    h = h.replace('</head>', '<link rel="stylesheet" href="assets/css/live-theme.css"/><link rel="icon" href="assets/img/afd2b6d3f3.png"/></head>', 1)
    h = re.sub(r'((?:href|src)="assets/(?:css|js)/[^"?]+)"', r'\1?v=' + VER + '"', h)
    leftovers = re.findall(r'__INSTRON_[A-Z_]+', h)
    report.append((key, len(h), leftovers[:3]))
    open(f'{out}/{SLUG[key]}.html', 'w', encoding='utf-8').write(IRA(V225(EMAIL_FIX(h), key)))
for r in report: print(r)
# v2.26 search and share layer (titles, descriptions, canonical, share cards, schema.org, robots/sitemap/llms.txt)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('seo', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seo.py'))
_seo = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_seo); _seo.run(out)
# IRA approved page list, refreshed from the pages just built
import subprocess as _sp
_sp.run([sys.executable, '-I', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ira_content.py'), out], check=True)
