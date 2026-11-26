"""v2.35.1: carry the approved v2.35 layouts onto the six Industries pages (Rahul, 26 Nov).

Sumit skipped the Industries pages because they share section types with pages he covered; each section here
takes the layout Rahul approved for the same section type elsewhere:
  problem cards -> 2 x 2 icon grid (PlantON, Industrial Automation)
  How we help -> icon cards (icon rule; three solution cards stay in one row)
  stage / path / validation steps -> numbered rail (Modernize, PlantON deployment)
  research stakeholders -> four icon columns (Process Skid Plants)
  recovery / CIP list -> photo left, icon list right (E&I)
  Work in this field -> unchanged (like Automation's delivered projects)
  inputs checklist -> 2 x 2 checklist card (PlantON discovery)
  Where to go next -> two-column link rows (PlantON related)

Starts from the committed review index.html (which already contains v2.35) and touches only these six pages.
Usage: python3 -I tools/v2351_industries.py <review repo dir>
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
TOOLS = os.path.dirname(os.path.abspath(__file__))
ICONS = json.load(open(os.path.join(TOOLS, 'v235_icons.json')))

src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
PAGES = DATA['pages']


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def ico(name):
    return (f'<svg class="v235-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def section(h, sid):
    m = re.search(r'<section\b[^>]*\bid="%s"' % re.escape(sid), h)
    if not m:
        return None
    depth = 0
    for t in re.finditer(r'<section\b|</section>', h[m.start():]):
        depth += 1 if t.group(0) == '<section' else -1
        if depth == 0:
            return m.start(), m.start() + t.end()


def edit_section(h, sid, fn):
    r = section(h, sid)
    assert r, sid
    a, b = r
    return h[:a] + fn(h[a:b]) + h[b:]


def icon_cards(s, names):
    """Icon at the top of each sx-card, in order (before any tag)."""
    it = iter(names)
    out, n = re.subn(r'<article class="sx-card( sx-pain)?">',
                     lambda m: f'<article class="sx-card{m.group(1) or ""} v235-icard"><span class="v235-ib">{ico(next(it))}</span>', s)
    assert n == len(names), (n, len(names))
    return out


def help_icon(title):
    t = re.sub('<[^>]+>', '', title)
    if 'Process Skid' in t:
        return 'boxes'
    if 'Automation' in t:
        return 'cpu'
    if 'PlantON' in t:
        return 'chart-line'
    raise ValueError(t)


PAINS = {
    'cleantech': ['chart-column', 'sliders-horizontal', 'flask-conical', 'hard-hat'],
    'research': ['target', 'hard-hat', 'chart-line', 'wrench'],
    'chemical': ['droplets', 'refresh-cw', 'users', 'settings'],
    'food': ['file-text', 'shield-check', 'activity', 'zap'],
    'pharma': ['triangle-alert', 'database', 'clock', 'droplets'],
    'manufacturing': ['cog', 'chart-column', 'link', 'lock'],
}
LISTS = {
    'recovery': ['search', 'box', 'cpu', 'list-checks'],
    'cip': ['refresh-cw', 'file-check', 'layers', 'link', 'zap'],
}

CSS = r"""
/* v2.35.1 Industries pages: approved v2.35 layouts by section type (Rahul, 26 Nov) */
html body main .v235-icard{position:relative}
html body main .v235-ib{display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:#EBF2FA;color:#2D6AB4;margin:0 0 14px}
html body main .v235-ib .v235-ico{width:22px;height:22px}
html body main .v235-g22{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:16px!important}
html body main .v235-g22 .v235-icard{display:grid!important;grid-template-columns:44px minmax(0,1fr);column-gap:14px;align-items:start!important;padding:20px!important;border-left:0!important}
html body main .v235-g22 .v235-ib{margin:0;grid-row:1/3;align-self:start}
html body main .v235-g22 .v235-icard>*:not(.v235-ib){grid-column:2;min-width:0}
html body main .v235-g22 .v235-icard h3{margin:0 0 4px!important;align-self:center}
html body main .v235-g22 .v235-icard p{margin:0!important}
html body main .v235-help .v235-icard{display:flex!important;flex-direction:column}
html body main .v235-help .v235-icard .sx-more{margin-top:auto!important}
html body main .v235-help .v22-tag{position:absolute;top:20px;right:20px;margin:0!important}
html body main .v235-rail-ol{display:grid!important;grid-template-columns:repeat(var(--n),minmax(0,1fr))!important;gap:18px!important;counter-reset:v235;list-style:none!important;padding:0!important;margin:24px 0 0!important;position:relative}
html body main .v235-rail-ol::before{content:"";position:absolute;left:22px;right:22px;top:21px;height:2px;background:#2D6AB4;z-index:0}
html body main .v235-rail-ol>li{position:relative;counter-increment:v235;background:none!important;border:0!important;box-shadow:none!important;padding:62px 0 0!important;margin:0!important;min-width:0}
html body main .v235-rail-ol>li::before{content:counter(v235,decimal-leading-zero)!important;position:absolute!important;left:0;top:0;display:grid!important;place-items:center;width:44px!important;height:44px!important;border-radius:50%!important;background:#fff!important;border:2px solid #2D6AB4!important;color:#2D6AB4!important;font-weight:700!important;font-size:14px!important;z-index:1;transform:none!important}
html body main .v235-rail-ol>li::after,html body main .v235-rail-ol>li>strong::before,html body main .v235-rail-ol>li>strong::after,html body main .v235-rail-ol>li>span::after{content:none!important;display:none!important}
html body main .v235-rail-ol>li>strong{display:block;font-size:17px;margin:0 0 6px}
html body main .v235-rail-ol>li>span{display:block;color:#555;font-size:14.5px;line-height:1.5}
html body main .v235-g4c{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:16px!important}
html body main .v235-ei{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:32px;align-items:start;margin:8px 0 0}
html body main .v235-ei figure{margin:0!important}
html body main .v235-ei figure img{width:100%;height:auto;border-radius:10px}
html body main .v235-eilist{list-style:none!important;padding:0!important;margin:0!important;display:grid;gap:0}
html body main .v235-eilist li{display:flex!important;gap:14px;align-items:flex-start;padding:14px 0!important;border:0!important;border-bottom:1px solid #e1e7ef!important;border-radius:0!important;background:none!important;box-shadow:none!important;margin:0!important}
html body main .v235-eilist li::before{content:none!important;display:none!important}
html body main .v235-eilist li strong{display:block;margin-bottom:3px}
html body main .v235-lico{display:grid;place-items:center;width:36px;height:36px;border-radius:8px;background:#EBF2FA;color:#2D6AB4;flex:none}
html body main .v235-lico .v235-ico{width:19px;height:19px}
html body main .v235-ready ul{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;padding:0!important;list-style:none}
html body main .v235-ready li{background:#fff;border:1px solid #e1e7ef;border-radius:8px;padding:12px 12px 12px 38px!important;position:relative;margin:0!important;line-height:1.4}
html body main .v235-ready li::before{content:"✓"!important;position:absolute!important;left:12px;top:11px;width:18px;height:18px;border-radius:4px;background:#2D6AB4!important;color:#fff!important;font-size:12px;display:grid!important;place-items:center;font-weight:700}
html body main .v235-related{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:0 24px!important;border:1px solid #e1e7ef;border-radius:10px;background:#fff;padding:6px 18px!important}
html body main .v235-related .related-link{display:block!important;position:relative;padding:12px 40px 12px 14px!important;margin:8px 0!important;border:0!important;border-left:3px solid #5CBA3C!important;border-radius:0!important;background:none!important;box-shadow:none!important;min-height:0!important}
html body main .v235-related .related-link::after{content:"→"!important;position:absolute;right:6px;top:50%;transform:translateY(-50%);width:26px;height:26px;border-radius:50%;background:#EBF2FA;color:#2D6AB4;display:grid;place-items:center;font-size:14px}
@media(max-width:900px){
html body main .v235-rail-ol{grid-template-columns:minmax(0,1fr)!important;gap:0!important}
html body main .v235-rail-ol::before{left:21px;right:auto;top:22px;bottom:22px;width:2px;height:auto}
html body main .v235-rail-ol>li{padding:0 0 22px 64px!important;min-height:52px}
html body main .v235-g4c{grid-template-columns:repeat(2,minmax(0,1fr))!important}
html body main .v235-ei{grid-template-columns:minmax(0,1fr)}
html body main .v235-related,html body main .v235-ready ul{grid-template-columns:minmax(0,1fr)!important}}
@media(max-width:700px){html body main .v235-g22,html body main .v235-g4c{grid-template-columns:minmax(0,1fr)!important}}
"""


def build(key):
    h = PAGES[key]['html']
    assert 'instron-v2351' not in h, f'{key}: v2.35.1 already applied'
    # Problem cards: 2 x 2 icon grid
    h = edit_section(h, 'pains', lambda s: icon_cards(s, PAINS[key]).replace(
        '<div class="sx-grid sx-g4">', '<div class="sx-grid sx-g4 v235-g22">', 1))
    # How we help: icon cards, solution icons by title
    def helpsec(s):
        titles = re.findall(r'<article class="sx-card">(?:<span class="v22-tag">.*?</span>)?<h3>(.*?)</h3>', s, re.S)
        s = icon_cards(s, [help_icon(t) for t in titles])
        return re.sub(r'<div class="sx-grid (sx-g[23])">', r'<div class="sx-grid \1 v235-help">', s, count=1)
    h = edit_section(h, 'help', helpsec)
    # Steps: numbered rail
    for sid in ('stages', 'path', 'validation'):
        if section(h, sid):
            def rail(s):
                m = re.search(r'<ol class="sx-steps h">(.*?)</ol>', s, re.S)
                assert m, sid
                n = m.group(1).count('<li')
                return s.replace('<ol class="sx-steps h">', f'<ol class="sx-steps h v235-rail-ol" style="--n:{n}">', 1)
            h = edit_section(h, sid, rail)
    # Research stakeholders: four icon columns
    if section(h, 'stakeholders'):
        h = edit_section(h, 'stakeholders', lambda s: icon_cards(s, ['test-tube', 'wrench', 'hard-hat', 'trending-up']).replace(
            '<div class="sx-grid sx-g4">', '<div class="sx-grid sx-g4 v235-g4c">', 1))
    # Recovery / CIP list: head on top, photo left, icon list right
    for sid in ('recovery', 'cip'):
        if section(h, sid):
            def split(s):
                m = re.search(r'<div class="sx-wrap sx-split"><div>(<div class="sx-head">.*?</div>)(<ul class="sx-list">.*?</ul>)</div>(<figure>.*?</figure>)</div>', s, re.S)
                assert m, sid
                icons = iter(LISTS[sid])
                ul, n = re.subn(r'<li><strong>(.*?)</strong>(.*?)</li>',
                                lambda x: f'<li><span class="v235-lico">{ico(next(icons))}</span><span><strong>{x.group(1)}</strong>{x.group(2)}</span></li>',
                                m.group(2), flags=re.S)
                assert n == len(LISTS[sid]), (sid, n)
                ul = ul.replace('<ul class="sx-list">', '<ul class="sx-list v235-eilist">', 1)
                return s[:m.start()] + f'<div class="sx-wrap">{m.group(1)}<div class="v235-ei">{m.group(3)}{ul}</div></div>' + s[m.end():]
            h = edit_section(h, sid, split)
    # Inputs checklist and related links
    h = edit_section(h, 'start', lambda s: s.replace('<div class="ready-panel">', '<div class="ready-panel v235-ready">', 1))
    assert h.count('<div class="related-grid">') == 1, key
    h = h.replace('<div class="related-grid">', '<div class="related-grid v235-related">', 1)
    h = h.replace('</head>', '<style id="instron-v2351">' + re.sub(r'\s*\n\s*', '', CSS) + '</style></head>', 1)
    PAGES[key]['html'] = h
    PAGES[key]['ids'] = sorted(set(re.findall(r'\bid="([^"]+)"', h)))


KEYS = ['cleantech', 'research', 'chemical', 'food', 'pharma', 'manufacturing']
for k in KEYS:
    build(k)
out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('v2.35.1 industries pages changed:', ', '.join(KEYS))
