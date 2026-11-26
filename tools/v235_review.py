"""v2.35 design layouts (Sumit's 26 Nov design suggestions, as approved by Rahul).

Applies the approved section layouts to the review build's embedded pages, then the preview is rebuilt with sync.py.
Always starts from the committed review index.html (git HEAD), so it can be re-run safely.

Usage: python3 -I tools/v235_review.py <review repo dir>
Decisions: project doc claude/sumit-design-suggestions-2026-11-26.md; review page https://claude.ai/artifact/Ft5h8Azz3pbrxEu3pKUuRD
Icons: Lucide (ISC licence), stored in tools/v235_icons.json.
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


def ico(name, cls='v235-ico'):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def section(h, sid):
    """(start, end) of <section ... id="sid"> ... </section>, nesting-aware."""
    m = re.search(r'<section\b[^>]*\bid="%s"' % re.escape(sid), h)
    assert m, sid
    depth, i = 0, m.start()
    for t in re.finditer(r'<section\b|</section>', h[m.start():]):
        depth += 1 if t.group(0) == '<section' else -1
        if depth == 0:
            return m.start(), m.start() + t.end()
    raise ValueError(sid)


def edit_section(h, sid, fn):
    a, b = section(h, sid)
    return h[:a] + fn(h[a:b]) + h[b:]


def sub1(pat, rep, s, flags=re.S):
    out, n = re.subn(pat, rep, s, count=1, flags=flags)
    assert n == 1, pat[:80]
    return out


def add_style(h, css):
    css = re.sub(r'\s*\n\s*', '', css)
    return h.replace('</head>', f'<style id="instron-v235">{css}</style></head>', 1)


CHANGED = []


def page(key):
    def deco(fn):
        h = PAGES[key]['html']
        h2, css = fn(h)
        h2 = add_style(h2, css)
        ids = set(re.findall(r'\bid="([^"]+)"', h2))
        PAGES[key]['html'] = h2
        PAGES[key]['ids'] = sorted(ids)
        CHANGED.append(key)
        return fn
    return deco


# ============================ Homepage ============================
@page('home')
def home(h):
    # Trusted since 2013 by: updated icon set
    trust_icons = iter(['atom', 'graduation-cap', 'satellite', 'wind', 'pill', 'fuel', 'milk', 'cog'])
    h = edit_section(h, 'trusted-by', lambda s: re.sub(
        r'<span class="mk-short-ico">.*?</span>', lambda m: f'<span class="mk-short-ico">{ico(next(trust_icons))}</span>', s, flags=re.S))

    # Where are you starting from?: chip links with the real page names
    def who(s):
        s = sub1(r'<a data-review-route="pilot"([^>]*)>Pilot &amp; Demonstration Plants</a></article>',
                 r'<div class="v235-chips"><a class="v235-chip" data-review-route="pilot"\1>Pilot &amp; Demonstration Plants</a></div></article>', s)
        s = sub1(r'<a data-review-route="industrial"([^>]*)>Industrial Process Skids</a></article>',
                 r'<div class="v235-chips"><a class="v235-chip" data-review-route="industrial"\1>Industrial Process Skids</a></div></article>', s)
        s = sub1(r'<a data-review-route="automation"([^>]*)>Industrial Automation · <span class="pon">.*?</span></a></article>',
                 r'<div class="v235-chips"><a class="v235-chip" data-review-route="automation"\1>Industrial Automation</a>'
                 r'<a class="v235-chip" data-review-route="planton" href="__INSTRON_REVIEW_URL__#page=planton" target="_top">'
                 r'<span class="pon"><span class="pon-p">Plant</span><span class="pon-o">ON</span></span></a></div></article>', s)
        return s
    h = edit_section(h, 'who-we-work-with', who)

    # Process Skid Plants: "Explore Process Skid Plants" moves beside the Applications label
    h = sub1(r'\n<div class="flagship-end">(<a class="flagship-explore"[^>]*>Explore Process Skid Plants</a>)</div>', '', h)
    h = sub1(r'(<h3 id="applications-heading">Applications</h3>)',
             r'\1<a class="flagship-explore v235-explore" data-review-route="process" href="__INSTRON_REVIEW_URL__#page=process" target="_top">Explore Process Skid Plants</a>', h)

    # How We Work: phase rail on top, outputs in a shaded box
    def hww(s):
        gate = '<span class="v235-gate"><i></i><small>Decision<br>go · adjust · stop</small></span>'
        rail = ('<div class="v235-rail" aria-hidden="true"><span class="v235-rn">01</span>' + gate +
                '<span class="v235-rn">02</span>' + gate + '<span class="v235-rn">03</span></div>')
        s = sub1(r'(<div class="work-card-grid work-grid mk-workflow">)', rail + r'\1', s)
        s, n = re.subn(r'(<p class="work-label">Typical outputs \(scope-specific\)</p><p>.*?</p>)', r'<div class="v235-out">\1</div>', s, flags=re.S)
        assert n == 3, n
        return s
    h = edit_section(h, 'how-we-work-home', hww)

    css = r'''
/* v2.35 Homepage layouts (Sumit 26 Nov, approved by Rahul) */
html body main #who-we-work-with .mk-who-card{display:flex!important;flex-direction:column}
html body main .v235-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding-top:16px}
html body main .v235-chip{display:inline-flex!important;align-items:center;min-height:38px;padding:7px 14px!important;border:1px solid #2D6AB4!important;border-radius:8px!important;background:#fff!important;color:#2D6AB4!important;font-size:14px!important;font-weight:600!important;line-height:1.2;text-decoration:none!important;margin:0!important}
html body main .v235-chip::after{content:none!important}
html body main .v235-chip:hover,html body main .v235-chip:focus-visible{background:#EBF2FA!important}
html body main .v235-chip .pon{white-space:nowrap}

html body main #scale-up-challenge .mk-chain-row{align-items:stretch}
html body main #scale-up-challenge .mk-node{display:flex!important;flex-direction:column;align-items:center;justify-content:flex-start;gap:8px;text-align:center;padding:16px 10px!important}
html body main #scale-up-challenge .mk-node small{display:grid!important;place-items:center;width:30px;height:30px;border-radius:50%;background:#2D6AB4!important;color:#fff!important;font-size:12px!important;font-weight:700;opacity:1!important;margin:0!important;flex:none}
html body main #scale-up-challenge .mk-link{position:relative;display:flex!important;align-items:center;justify-content:center;min-width:26px;flex:0 0 26px}
html body main #scale-up-challenge .mk-link i{display:none!important}
html body main #scale-up-challenge .mk-link::before{content:"";position:absolute;left:3px;right:7px;top:50%;height:2px;background:#2D6AB4;transform:translateY(-50%)}
html body main #scale-up-challenge .mk-link::after{content:"";position:absolute;right:3px;top:50%;width:7px;height:7px;border-top:2px solid #2D6AB4;border-right:2px solid #2D6AB4;transform:translateY(-50%) rotate(45deg)}
html body main #scale-up-challenge .mk-chain-basis{position:relative;text-align:center;margin:20px 0 0!important;padding:0!important;border:0!important;width:100%!important;max-width:none!important}
html body main #scale-up-challenge .mk-chain-basis::before{content:"";position:absolute;left:0;right:0;top:50%;height:2px;background:#5CBA3C;width:auto!important}
html body main #scale-up-challenge .mk-chain-basis::after{content:none!important}
html body main #scale-up-challenge .mk-chain-basis span{position:relative;display:inline-block;background:#fff;border:1.5px solid #5CBA3C;border-radius:999px;padding:5px 16px;font-weight:600}
html body main #scale-up-challenge .mk-pain-grid{border-top:0!important;padding-top:8px}
html body main #scale-up-challenge .mk-pain-item{position:relative;padding-top:20px!important;border:0!important}
html body main #scale-up-challenge .mk-pain-item::before{content:"";position:absolute;left:0;top:0;width:48px;height:3px;background:#2D6AB4;border-radius:2px}
html body main #scale-up-challenge .mk-pain-item b{display:block;font-size:44px!important;line-height:1;font-weight:300!important;color:#b6c2d1!important;margin:0 0 12px!important;letter-spacing:0}
html body main #scale-up-challenge .mk-pain-close{max-width:none!important}

html body main #process-skid-plants .flagship-card{position:relative!important;overflow:hidden!important;border-radius:10px!important;padding:0!important;display:block!important;background:#1A3668}
html body main #process-skid-plants .flagship-card img{display:block!important;width:100%!important;height:320px!important;object-fit:cover!important;margin:0!important;border-radius:0!important}
html body main #process-skid-plants .flagship-card::after{content:""!important;position:absolute!important;left:0;right:0;bottom:0;top:auto!important;width:auto!important;height:62%;border-radius:0!important;background:linear-gradient(rgba(10,22,40,0),rgba(10,22,40,.86))!important;pointer-events:none;z-index:1;display:block!important}
html body main #process-skid-plants .flagship-card::before{content:none!important}
html body main #process-skid-plants .flagship-card-no,html body main #process-skid-plants .flagship-card-rule{display:none!important}
html body main #process-skid-plants .flagship-card-title{position:absolute!important;left:26px;right:26px;bottom:24px;z-index:2;margin:0!important;padding:14px 0 0!important;background:none!important;color:#fff!important;font-size:24px!important;line-height:1.2!important;font-weight:700!important;text-shadow:0 1px 2px rgba(0,0,0,.35)}
html body main #process-skid-plants .flagship-card-title::before{content:"";position:absolute;left:0;top:0;width:36px;height:3px;background:#5CBA3C;border-radius:2px}
html body main #process-skid-plants .flagship-mini-heading{display:flex!important;align-items:center;gap:12px;flex-wrap:wrap}
html body main #process-skid-plants .v235-explore{margin-left:auto!important;font-size:15px}
html body main #process-skid-plants .mk-apps-grid{gap:0!important;border:1px solid #d5dfec;border-radius:10px;background:#fff;overflow:hidden}
html body main #process-skid-plants .mk-apps-grid>li{border-right:1px solid #d5dfec;min-width:0}
html body main #process-skid-plants .mk-apps-grid>li:last-child{border-right:0}
html body main #process-skid-plants .mk-apps-grid a{border:0!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;height:100%}
html body main #process-skid-plants .mk-apps-grid a:hover{background:#F4F7FB!important}
html body main #process-skid-plants .mk-app-ico{width:56px!important;height:56px!important}
html body main #process-skid-plants .mk-app-ico svg{width:26px!important;height:26px!important}

html body main #technology-scale-up-journey .mk-step{background:#fff!important;color:#1A1A1A!important;border:1px solid #d5dfec!important;border-top:3px solid #2D6AB4!important;border-radius:4px 4px 0 0!important;box-shadow:none!important}
html body main #technology-scale-up-journey .mk-step b{color:#1A3668!important}
html body main #technology-scale-up-journey .mk-step span{color:#555!important}
html body main #technology-scale-up-journey .mk-step em{color:#2D6AB4!important}
html body main #technology-scale-up-journey .mk-step.s0{background:#F4F7FB!important;border-top-color:#c9d3df!important}
html body main #technology-scale-up-journey .mk-step.s0 b{color:#555!important}
html body main #technology-scale-up-journey .mk-zone{background:rgba(92,186,60,.08)!important;border:1px dashed rgba(92,186,60,.55)!important}

html body main #engineering-beyond-process-plants .beyond-grid{grid-template-columns:minmax(0,1fr)!important;gap:18px!important}
html body main #engineering-beyond-process-plants .beyond-tile{display:grid!important;grid-template-columns:minmax(0,5fr) minmax(0,7fr);grid-template-rows:auto auto 1fr;grid-template-areas:"img top" "img h" "img p";column-gap:32px;align-items:start;padding:16px 28px 16px 16px!important;min-height:0!important;background:#fff!important;border:1px solid #e1e7ef!important;border-radius:10px!important}
html body main #engineering-beyond-process-plants .beyond-tile img{grid-area:img;position:static!important;width:100%!important;height:100%!important;min-height:210px;max-height:260px;object-fit:cover!important;border-radius:8px!important;margin:0!important}
html body main #engineering-beyond-process-plants .beyond-top{grid-area:top;position:static!important;padding:18px 0 0!important;margin:0!important;background:none!important}
html body main #engineering-beyond-process-plants .beyond-tile h3{grid-area:h;position:static!important;padding:6px 0 8px!important;margin:0!important;max-width:none!important}
html body main #engineering-beyond-process-plants .beyond-tile .beyond-desc{grid-area:p;position:static!important;padding:0!important;max-width:60ch}
html body main #engineering-beyond-process-plants .beyond-mark,html body main #engineering-beyond-process-plants .beyond-data-mark{display:none!important}

html body main #how-we-work-home .v235-rail{display:grid;grid-template-columns:auto 1fr auto 1fr auto;align-items:center;margin:4px 0 22px;padding:0 calc(16.66% - 22px)}
html body main #how-we-work-home .v235-rn{display:grid;place-items:center;width:44px;height:44px;border-radius:50%;border:2px solid #2D6AB4;background:#fff;color:#2D6AB4;font-weight:700;font-size:15px}
html body main #how-we-work-home .v235-gate{position:relative;display:flex;flex-direction:column;align-items:center;height:2px;background:#2D6AB4;margin:0 8px}
html body main #how-we-work-home .v235-gate i{position:absolute;top:50%;left:50%;width:16px;height:16px;background:#5CBA3C;transform:translate(-50%,-50%) rotate(45deg);border:2px solid #fff;box-shadow:0 0 0 1px #5CBA3C}
html body main #how-we-work-home .v235-gate small{position:absolute;top:14px;left:50%;transform:translateX(-50%);white-space:nowrap;text-align:center;font-size:11.5px;line-height:1.3;color:#555}
html body main #how-we-work-home .mk-gate{display:none!important}
html body main #how-we-work-home .work-card-grid{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:18px!important;margin-top:34px}
html body main #how-we-work-home .work-top{display:none!important}
html body main #how-we-work-home .work-card{border-top:3px solid #2D6AB4!important}
html body main #how-we-work-home .work-card h3{min-height:0!important;margin-bottom:12px!important}
html body main #how-we-work-home .work-content{align-content:start!important;row-gap:6px}
html body main #how-we-work-home .card-deep-link{margin-top:auto!important}
html body main #how-we-work-home .v235-out{background:#F4F7FB;border-radius:8px;padding:12px 14px;margin-top:12px}
html body main #how-we-work-home .v235-out p{margin-bottom:4px}

html body main #why-instron .why-grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:18px!important}
html body main #why-instron .why-card{display:grid!important;grid-template-columns:48px minmax(0,1fr);column-gap:16px;row-gap:8px;align-items:center;padding:24px!important;text-align:left!important}
html body main #why-instron .why-card .mk-ico{grid-column:1;grid-row:1;width:48px!important;height:48px!important;margin:0!important;border-radius:10px!important;background:#EBF2FA!important;display:grid!important;place-items:center}
html body main #why-instron .why-card h3{grid-column:2;grid-row:1;margin:0!important;padding:0!important}
html body main #why-instron .why-card .mk-why-p{grid-column:1/-1;margin:4px 0 0!important}
html body main #why-instron .why-no,html body main #why-instron .why-line{display:none!important}

@media(max-width:900px){
html body main #engineering-beyond-process-plants .beyond-tile{grid-template-columns:minmax(0,1fr);grid-template-areas:"img" "top" "h" "p";padding:14px!important}
html body main #engineering-beyond-process-plants .beyond-tile img{max-height:220px}
html body main #how-we-work-home .v235-rail{display:none}
html body main #how-we-work-home .work-card-grid{grid-template-columns:minmax(0,1fr)!important;margin-top:0}
html body main #process-skid-plants .mk-apps-grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}
html body main #process-skid-plants .mk-apps-grid>li{border-bottom:1px solid #d5dfec}
html body main #scale-up-challenge .mk-chain-row{flex-wrap:wrap!important;display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
html body main #scale-up-challenge .mk-link{display:none!important}
}
@media(max-width:600px){
html body main #why-instron .why-grid{grid-template-columns:minmax(0,1fr)!important}
html body main #process-skid-plants .mk-apps-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
html body main #process-skid-plants .flagship-card img{height:240px!important}
html body main #scale-up-challenge .mk-chain-row{grid-template-columns:repeat(2,minmax(0,1fr))}
}
'''
    return h, css



def icon_cards(s, names, h3tag='<h3>'):
    """Put an icon in front of each psp-card heading, in order."""
    it = iter(names)
    out, n = re.subn(r'<article class="psp-card"><h3>', lambda m: f'<article class="psp-card v235-icard"><span class="v235-ib">{ico(next(it))}</span><h3>', s)
    assert n == len(names), (n, len(names))
    return out


CARD_CSS = r"""
html body main .v235-icard{position:relative}
html body main .v235-ib{display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:#EBF2FA;color:#2D6AB4;margin:0 0 14px}
html body main .v235-ib .v235-ico{width:22px;height:22px}
"""


# ============================ Process Skid Plants ============================
@page('process')
def process(h):
    # 01 The skid is not the starting point: four icon columns
    h = edit_section(h, 'section-sec-1', lambda s: icon_cards(s, ['flask-conical', 'boxes', 'gauge', 'plug']))
    # 03 Relevant process applications: name on the photo
    h = edit_section(h, 'section-sec-3', lambda s: s.replace('<ul class="application-photo-grid">', '<ul class="application-photo-grid v235-apps">', 1))
    # 04 Engineering layers: icon on each layer
    layer_icons = iter(['workflow', 'box', 'gauge', 'cpu', 'chart-line', 'plug'])
    def layers(s):
        s, n = re.subn(r'(<summary>)(<span class="count">)', lambda m: m.group(1) + f'<span class="v235-lico">{ico(next(layer_icons))}</span>' + m.group(2), s)
        assert n == 6, n
        return s.replace('<div class="engineering-system">', '<div class="engineering-system v235-layers">', 1)
    h = edit_section(h, 'section-sec-4', layers)
    # 05 Engineering deliverables: four icon cards
    h = edit_section(h, 'section-sec-5', lambda s: icon_cards(s, ['file-text', 'box', 'circuit-board', 'list-checks']))
    # 06 Equipment classifications: statement left, list right
    def equip(s):
        return sub1(r'<ul class="details-list">(.*?)</ul><p>Each project requires its own process basis\. (Instron Technologies does not present one standard skid as suitable for every process\.)</p>',
                    r'<div class="v235-equip"><div class="v235-equip-l"><p class="v235-equip-k">Each project requires its own process basis.</p><p>\2</p></div>'
                    r'<ul class="details-list v235-equip-list">\1</ul></div>', s)
    h = edit_section(h, 'section-sec-6', equip)
    # Case studies: navy proof band, headline figure first
    FIG = {'case-mexico': ('Skid and distillation column, with a', 'repeat order', ''),
           'case-battery': ('Turnkey automated pilot,', '120 I/O', ''),
           'case-api': ('', '+24% batches,', 'ROI in 4 months')}
    def cases(s):
        def li(m):
            key, title = m.group(2), m.group(4)
            lead, big, green = FIG[key]
            return (f'<li>{m.group(1)}<span class="v235-pf-lead">{lead}</span><strong class="v235-pf-big">{big}</strong>'
                    + (f'<span class="v235-pf-green">{green}</span>' if green else '') +
                    f'<b>{title}</b><em>Read the case study</em></a></li>')
        out, n = re.subn(r'<li>(<a data-review-route="cases" data-review-section="(case-[a-z]+)"[^>]*>)(<b>(.*?)</b><span>.*?</span><em>Read the case study</em></a>)</li>',
                         lambda m: li(type('M', (), {'group': lambda self, i: [None, m.group(1), m.group(2), None, m.group(4)][i]})()), s)
        assert n == 3, n
        return out.replace('<ul class="v216-cases">', '<ul class="v216-cases v235-proof">', 1)
    h = edit_section(h, 'section-cases', cases)
    # Gallery: featured battery-recycling pilot skid, then a mosaic
    def gallery(s):
        figs = re.findall(r'<figure>.*?</figure>', s, re.S)
        assert len(figs) == 8, len(figs)
        feat = [f for f in figs if 'alt="Battery-recycling pilot skid"' in f]
        assert len(feat) == 1
        rest = [f for f in figs if f is not feat[0]]
        new = feat[0].replace('<figure>', '<figure class="v235-feat">', 1) + ''.join(rest)
        a = s.index(figs[0]); b = s.index(figs[-1]) + len(figs[-1])
        return s[:a] + new + s[b:]
    a = h.index('id="instron-archive-image-gallery"'); a = h.rfind('<section', 0, a); b = h.index('</section>', a) + 10
    h = h[:a] + gallery(h[a:b]).replace('<div class="gallery-grid">', '<div class="gallery-grid v235-gallery">', 1) + h[b:]

    css = CARD_CSS + r"""
/* v2.35 Process Skid Plants (approved 26 Nov) */
html body main #section-sec-1 .psp-areas,html body main #section-sec-5 .psp-packages{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:16px!important}
html body main .v235-apps{gap:20px!important}
html body main .v235-apps>li{position:relative;padding:0!important;overflow:hidden;border-radius:10px!important;background:#fff}
html body main .v235-apps>li img{display:block;width:100%!important;height:220px!important;object-fit:cover!important;margin:0!important;border-radius:0!important}
html body main .v235-apps>li::after{content:"";position:absolute;left:0;right:0;top:110px;height:110px;background:linear-gradient(rgba(10,22,40,0),rgba(10,22,40,.82));pointer-events:none}
html body main .v235-apps>li>span{position:absolute;left:18px;right:18px;top:220px;transform:translateY(-100%);padding:0 0 14px;z-index:1;color:#fff!important;font-weight:700;font-size:17px;line-height:1.25;text-shadow:0 1px 2px rgba(0,0,0,.4);margin:0!important;background:none!important}
html body main .v235-apps>li>.app-desc{padding:14px 18px 18px!important;margin:0!important}
html body main .v235-layers .system-photo{position:relative;overflow:hidden;border-radius:10px}
html body main .v235-layers .system-photo figcaption{position:absolute;left:0;right:0;bottom:0;padding:44px 18px 14px!important;margin:0!important;background:linear-gradient(rgba(10,22,40,0),rgba(10,22,40,.85))!important;color:#fff!important;font-weight:700}
html body main .v235-layers summary{display:flex!important;align-items:center;gap:10px}
html body main .v235-lico{display:grid;place-items:center;width:32px;height:32px;border-radius:8px;background:#EBF2FA;color:#2D6AB4;flex:none}
html body main .v235-lico .v235-ico{width:18px;height:18px}
html body main .v235-layers summary .count{font-size:12px!important;opacity:.7}
html body main .v235-equip{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:40px;align-items:start;margin-top:8px}
html body main .v235-equip-l{border-top:3px solid #5CBA3C;padding-top:16px}
html body main .v235-equip-k{font-size:24px!important;line-height:1.25!important;font-weight:700!important;color:#1A3668!important;margin:0 0 10px!important}
html body main .v235-equip-list{display:grid!important;grid-template-columns:minmax(0,1fr)!important;gap:0!important;margin:0!important;padding:0 0 0 18px!important;border-left:2px solid #d5dfec;list-style:none}
html body main .v235-equip-list li{position:relative;padding:10px 0 10px 18px!important;border:0!important;margin:0!important;width:auto!important}
html body main .v235-equip-list li::before{content:""!important;position:absolute;left:-25px;top:50%;width:10px;height:10px;border-radius:50%;background:#2D6AB4;border:2px solid #fff;transform:translateY(-50%)}
html body main .v235-proof{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:0!important;background:#0E2A47!important;border-radius:12px;padding:12px!important;list-style:none}
html body main .v235-proof>li{border-right:1px solid rgba(255,255,255,.16);margin:0!important;padding:0!important;background:none!important;border-top:0!important;border-bottom:0!important;border-left:0!important}
html body main .v235-proof>li:last-child{border-right:0}
html body main .v235-proof a{display:flex!important;flex-direction:column;gap:6px;padding:22px 24px!important;background:none!important;border:0!important;box-shadow:none!important;color:#fff!important;height:100%;text-decoration:none!important}
html body main .v235-proof a::before{content:"";width:28px;height:3px;background:#5CBA3C;border-radius:2px;margin-bottom:8px}
html body main .v235-proof .v235-pf-lead{color:#C9D8E6!important;font-size:14px;line-height:1.4;min-height:1.4em}
html body main .v235-proof .v235-pf-big{color:#fff!important;font-size:clamp(28px,2.8vw,38px);line-height:1.1;font-weight:700}
html body main .v235-proof .v235-pf-green{color:#7fd36a!important;font-weight:700;font-size:16px}
html body main .v235-proof b{color:#fff!important;font-size:15px;margin-top:auto;padding-top:16px;border-top:1px solid rgba(255,255,255,.16)}
html body main .v235-proof em{color:#fff!important;font-style:normal;font-size:13.5px;font-weight:600;text-decoration:underline;text-underline-offset:3px}
html body .v235-gallery{display:grid!important;grid-template-columns:repeat(12,minmax(0,1fr))!important;gap:14px!important}
html body .v235-gallery>figure{grid-column:span 4}
html body .v235-gallery>figure:nth-child(2),html body .v235-gallery>figure:nth-child(3),html body .v235-gallery>figure:nth-child(4),html body .v235-gallery>figure:nth-child(5){grid-column:span 3}
html body .v235-gallery>figure img{height:170px!important}
html body .v235-gallery>.v235-feat{grid-column:span 6;grid-row:span 2;position:relative}
html body .v235-gallery>.v235-feat img{height:100%!important;min-height:380px}
html body .v235-gallery>.v235-feat figcaption{position:absolute;left:0;right:0;bottom:0;padding:48px 20px 18px!important;background:linear-gradient(rgba(10,22,40,0),rgba(10,22,40,.85));color:#fff!important;font-size:18px!important}
@media(max-width:900px){
html body main #section-sec-1 .psp-areas,html body main #section-sec-5 .psp-packages{grid-template-columns:repeat(2,minmax(0,1fr))!important}
html body main .v235-equip{grid-template-columns:minmax(0,1fr);gap:20px}
html body main .v235-proof{grid-template-columns:minmax(0,1fr)!important}
html body main .v235-proof>li{border-right:0;border-bottom:1px solid rgba(255,255,255,.16)!important}
html body .v235-gallery>figure,html body .v235-gallery>figure:nth-child(n){grid-column:span 6}
html body .v235-gallery>.v235-feat{grid-column:1/-1;grid-row:auto}
html body .v235-gallery>.v235-feat img{min-height:0;height:260px!important}
}
@media(max-width:600px){html body main #section-sec-1 .psp-areas,html body main #section-sec-5 .psp-packages{grid-template-columns:minmax(0,1fr)!important}
html body .v235-gallery>figure,html body .v235-gallery>figure:nth-child(n){grid-column:1/-1}}
"""
    return h, css


# ============================ Pilot & Demonstration Plants ============================
@page('pilot')
def pilot(h):
    # 01 Research and pilot systems: two columns, icon in a tinted side panel
    def research(s):
        s = icon_cards(s, ['clipboard-list', 'sliders-horizontal', 'gauge', 'chart-column', 'trending-up', 'factory'])
        return s.replace('<div class="psp-cards">', '<div class="psp-cards v235-side">', 1)
    h = edit_section(h, 'section-sec-1', research)
    # 02 Demonstration systems: four in a row with a short rule; Q&A as a full-width band
    def demo(s):
        s = s.replace('<div class="psp-cards">', '<div class="psp-cards v235-rule4">', 1)
        return sub1(r'<p class="pilot-q">(Does pilot testing guarantee scale-up\?)</p><p>(No\..*?)</p>',
                    r'<div class="v235-qa"><p class="pilot-q">\1</p><p>\2</p></div>', s)
    h = edit_section(h, 'section-sec-2', demo)
    # 04 Engineering package: eight items, two columns, icons, no numbers
    pkg_icons = iter(['clipboard-list', 'workflow', 'file-text', 'cpu', 'layout-grid', 'list-checks', 'chart-column', 'file-check'])
    def pkg(s):
        s, n = re.subn(r'<li>(.*?)</li>', lambda m: f'<li><span class="v235-lico">{ico(next(pkg_icons))}</span><span>{m.group(1)}</span></li>', s)
        assert n == 8, n
        return s.replace('<ul class="details-list">', '<ul class="details-list v235-pkg">', 1)
    h = edit_section(h, 'section-sec-4', pkg)
    css = CARD_CSS + r"""
/* v2.35 Pilot & Demonstration Plants (approved 26 Nov) */
html body main .v235-side{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:16px!important}
html body main .v235-side .v235-icard{display:grid!important;grid-template-columns:78px minmax(0,1fr);grid-template-rows:auto 1fr;column-gap:20px;padding:0 22px 0 0!important;overflow:hidden;border-top:0!important;border-radius:10px!important}
html body main .v235-side .v235-ib{grid-row:1/3;width:auto;height:100%;margin:0;border-radius:0;background:#EBF2FA}
html body main .v235-side .v235-icard h3{padding-top:20px!important;margin:0 0 6px!important}
html body main .v235-side .v235-icard p{padding-bottom:20px!important;margin:0!important}
html body main .v235-rule4{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:24px!important}
html body main .v235-rule4 .psp-card{background:none!important;border:0!important;box-shadow:none!important;padding:16px 0 0!important;border-radius:0!important;position:relative}
html body main .v235-rule4 .psp-card::before{content:"";position:absolute;left:0;top:0;width:44px;height:3px;background:#2D6AB4;border-radius:2px}
html body main .v235-qa{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:28px;align-items:center;margin-top:28px;padding:22px 26px;background:#F4F7FB;border-left:4px solid #5CBA3C;border-radius:8px}
html body main .v235-qa p{margin:0!important}
html body main .v235-qa .pilot-q{font-size:19px!important;font-weight:700!important;color:#1A3668!important}
html body main .v235-pkg{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important;list-style:none;padding:0!important}
html body main .v235-pkg li{display:flex!important;align-items:center;gap:14px;padding:14px 16px!important;border:1px solid #e1e7ef!important;border-radius:10px;background:#fff;margin:0!important}
html body main .v235-pkg li::before{content:none!important;display:none!important}
html body main .v235-lico{display:grid;place-items:center;width:36px;height:36px;border-radius:8px;background:#EBF2FA;color:#2D6AB4;flex:none}
html body main .v235-lico .v235-ico{width:19px;height:19px}
@media(max-width:900px){html body main .v235-rule4{grid-template-columns:repeat(2,minmax(0,1fr))!important}html body main .v235-qa{grid-template-columns:minmax(0,1fr);gap:8px}}
@media(max-width:700px){html body main .v235-side,html body main .v235-pkg{grid-template-columns:minmax(0,1fr)!important}html body main .v235-rule4{grid-template-columns:minmax(0,1fr)!important}}
"""
    return h, css



def sx_icons(s, names, cls='v235-icard'):
    """Icon in front of each sx-card heading, in order."""
    it = iter(names)
    out, n = re.subn(r'<article class="sx-card( sx-pain)?"><h3>',
                     lambda m: f'<article class="sx-card{m.group(1) or ""} {cls}"><span class="v235-ib">{ico(next(it))}</span><h3>', s)
    assert n == len(names), (n, len(names))
    return out


RAIL_CSS = r"""
html body main .v235-rail-ol{display:grid!important;grid-template-columns:repeat(var(--n),minmax(0,1fr))!important;gap:18px!important;counter-reset:v235;list-style:none!important;padding:0!important;margin:24px 0 0!important;position:relative}
html body main .v235-rail-ol::before{content:"";position:absolute;left:22px;right:22px;top:21px;height:2px;background:#2D6AB4;z-index:0}
html body main .v235-rail-ol>li{position:relative;counter-increment:v235;background:none!important;border:0!important;box-shadow:none!important;padding:62px 0 0!important;margin:0!important;min-width:0}
html body main .v235-rail-ol>li::before{content:counter(v235,decimal-leading-zero)!important;position:absolute!important;left:0;top:0;display:grid!important;place-items:center;width:44px!important;height:44px!important;border-radius:50%!important;background:#fff!important;border:2px solid #2D6AB4!important;color:#2D6AB4!important;font-weight:700!important;font-size:14px!important;z-index:1;transform:none!important}
html body main .v235-rail-ol>li::after{content:none!important;display:none!important}
html body main .v235-rail-ol>li>strong{display:block;font-size:17px;margin:0 0 6px}
html body main .v235-rail-ol>li>strong::before,html body main .v235-rail-ol>li>strong::after,html body main .v235-rail-ol>li>span::after{content:none!important;display:none!important}
html body main .v235-rail-ol>li>span{display:block;color:#555;font-size:14.5px;line-height:1.5}
@media(max-width:900px){html body main .v235-rail-ol{grid-template-columns:minmax(0,1fr)!important;gap:0!important}
html body main .v235-rail-ol::before{left:21px;right:auto;top:22px;bottom:22px;width:2px;height:auto}
html body main .v235-rail-ol>li{padding:0 0 22px 64px!important;min-height:52px}}
"""
GRID22_CSS = r"""
html body main .v235-g22{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:16px!important}
html body main .v235-g22 .v235-icard{display:grid!important;grid-template-columns:44px minmax(0,1fr);column-gap:14px;align-items:center;padding:20px!important;border-left:0!important}
html body main .v235-g22 .v235-ib{margin:0;grid-row:1/3;align-self:start}
html body main .v235-g22 .v235-icard h3{margin:0 0 4px!important}
html body main .v235-g22 .v235-icard p{margin:0!important;grid-column:2}
html body main .v235-g22 .v235-icard>*:not(.v235-ib){grid-column:2;min-width:0}
html body main .v235-g22 .v235-icard .sx-more{display:inline-block!important;width:auto!important;margin-top:10px!important;white-space:normal}
html body main .v235-g22 .v235-icard{align-items:start!important}
html body main .v235-g22 .v235-icard h3{align-self:center}
@media(max-width:700px){html body main .v235-g22{grid-template-columns:minmax(0,1fr)!important}}
"""


# ============================ Industrial Automation ============================
@page('automation')
def automation(h):
    # 01 Where automation holds a plant back: navy statement left, 2 x 2 icon grid
    def pains(s):
        s = sx_icons(s, ['triangle-alert', 'file-text', 'network', 'clipboard-list'])
        s = sub1(r'(<h2>Where automation holds a plant back</h2>)<p>(.*?)</p></div><div class="sx-grid sx-g4">(.*?)</div></div></section>$',
                 r'\1</div><div class="v235-pains"><div class="v235-stmt"><p>\2</p></div><div class="sx-grid sx-g4 v235-g22">\3</div></div></div></section>', s)
        return s
    h = edit_section(h, 'pains', pains)
    # 02 Capabilities: two columns, icon beside title
    h = edit_section(h, 'services', lambda s: sx_icons(s, ['refresh-cw', 'cpu', 'list-checks', 'circuit-board', 'network', 'badge-check']).replace(
        '<div class="sx-grid sx-g3">', '<div class="sx-grid sx-g3 v235-g22">', 1))
    # 03 E&I: head on top; photo left, icon list right; "In practice" band under both
    def ei(s):
        m = re.search(r'<div class="sx-wrap sx-split"><div>(<div class="sx-head">.*?</div>)(<ul class="sx-list">.*?</ul>)(<p class="sx-proof">.*?</p>)</div>(<figure>.*?</figure>)</div></section>$', s, re.S)
        assert m, 'ei'
        icons = iter(['gauge', 'file-text', 'zap', 'server', 'cable'])
        ul, n = re.subn(r'<li><strong>(.*?)</strong>(.*?)</li>', lambda x: f'<li><span class="v235-lico">{ico(next(icons))}</span><span><strong>{x.group(1)}</strong>{x.group(2)}</span></li>', m.group(2))
        assert n == 5, n
        ul = ul.replace('<ul class="sx-list">', '<ul class="sx-list v235-eilist">', 1)
        return s[:m.start()] + f'<div class="sx-wrap">{m.group(1)}<div class="v235-ei">{m.group(4)}{ul}</div>{m.group(3)}</div></section>'
    h = edit_section(h, 'ei', ei)
    # 04 Batch: four topics as icon columns above; HMI screenshot full width below; Delivered box under it
    def batch(s):
        s = sx_icons(s, ['layers', 'sliders-horizontal', 'clipboard-list', 'shield-check'])
        m = re.search(r'(<figure style="margin:28px 0 8px.*?</figure>)(<div class="sx-grid sx-g2">.*?</div>)(<p class="sx-proof">)', s, re.S)
        assert m, 'batch'
        grid = m.group(2).replace('<div class="sx-grid sx-g2">', '<div class="sx-grid sx-g2 v235-g4i">', 1)
        return s[:m.start()] + grid + m.group(1) + m.group(3) + s[m.end():]
    h = edit_section(h, 'batch', batch)
    # 05 Modernize: connected numbered rail
    h = edit_section(h, 'modernize', lambda s: s.replace('<ol class="sx-steps h">', '<ol class="sx-steps h v235-rail-ol" style="--n:5">', 1))
    # 06 Platforms: control platforms boxed left; communications chips and engineering practice stacked right
    h = edit_section(h, 'platforms', lambda s: s.replace('<div class="sx-plat">', '<div class="sx-plat v235-plat">', 1))
    css = CARD_CSS + RAIL_CSS + GRID22_CSS + r"""
/* v2.35 Industrial Automation (approved 26 Nov; batch control changed to Option A) */
html body main .v235-pains{display:grid;grid-template-columns:minmax(0,4fr) minmax(0,8fr);gap:18px;align-items:stretch;margin-top:8px}
html body main .v235-stmt{background:#0E2A47;border-radius:10px;padding:28px;display:flex;flex-direction:column;justify-content:center}
html body main .v235-stmt::before{content:"";width:32px;height:3px;background:#5CBA3C;border-radius:2px;margin-bottom:14px}
html body main .v235-stmt p{color:#fff!important;font-size:19px!important;line-height:1.45!important;font-weight:600;margin:0!important}
html body main .v235-ei{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:32px;align-items:start;margin:8px 0 20px}
html body main .v235-ei figure{margin:0!important}
html body main .v235-ei figure img{width:100%;height:auto;border-radius:10px}
html body main .v235-eilist{list-style:none!important;padding:0!important;margin:0!important;display:grid;gap:0}
html body main .v235-eilist li{display:flex!important;gap:14px;align-items:flex-start;padding:14px 0!important;border-bottom:1px solid #e1e7ef;margin:0!important}
html body main .v235-eilist li::before{content:none!important;display:none!important}
html body main .v235-eilist li strong{display:block;margin-bottom:3px}
html body main .v235-lico{display:grid;place-items:center;width:36px;height:36px;border-radius:8px;background:#EBF2FA;color:#2D6AB4;flex:none}
html body main .v235-lico .v235-ico{width:19px;height:19px}
html body main #ei .sx-proof{border-left:4px solid #5CBA3C;background:#F4F7FB;border-radius:8px;padding:14px 18px}
html body main .v235-g4i{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:16px!important;margin:24px 0 8px}
html body main .v235-g4i .sx-card{border:0!important;border-left:1px solid #d5dfec!important;border-radius:0!important;background:none!important;box-shadow:none!important;padding:4px 18px!important}
html body main .v235-g4i .sx-card:first-child{border-left:0!important;padding-left:0!important}
html body main .v235-plat{display:grid!important;grid-template-columns:minmax(0,5fr) minmax(0,7fr)!important;grid-template-rows:auto 1fr;gap:16px!important}
html body main .v235-plat>div{display:block!important;background:#F4F7FB;border-radius:10px;padding:20px 22px!important;border:0!important;margin:0!important}
html body main .v235-plat ul{margin:0!important;padding:0!important;list-style:none}
html body main .v235-plat>div:first-child ul,html body main .v235-plat>div:nth-child(3) ul{display:block!important}
html body main .v235-plat>div:first-child li,html body main .v235-plat>div:nth-child(3) li{display:block!important;background:none!important;border-radius:0!important;margin:0!important;font-size:15px}
html body main .v235-plat>div:nth-child(3) li{padding:5px 0 5px 16px!important;position:relative;break-inside:avoid}
html body main .v235-plat>div:nth-child(3) li::before{content:""!important;position:absolute;left:0;top:13px;width:6px;height:6px;border-radius:50%;background:#5CBA3C}
html body main .v235-plat>div:first-child{grid-row:1/3;background:#fff;border:1px solid #d5dfec!important}
html body main .v235-plat>div:first-child li{padding:8px 0!important;border:0!important;border-bottom:1px solid #eef2f7!important;font-weight:600}
html body main .v235-plat>div:nth-child(2) ul{display:flex!important;flex-wrap:wrap;gap:8px;list-style:none;padding:0!important}
html body main .v235-plat>div:nth-child(2) li{border:1px solid #2D6AB4;color:#1A3668;border-radius:999px;padding:5px 12px!important;font-size:14px;background:#fff;margin:0!important}
html body main .v235-plat>div:nth-child(2) li::before{content:none!important}
html body main .v235-plat>div:nth-child(3) ul{columns:2;column-gap:24px}
html body main .v235-plat b{display:block;font-size:17px;margin-bottom:10px}
@media(max-width:900px){html body main .v235-pains,html body main .v235-ei,html body main .v235-plat{grid-template-columns:minmax(0,1fr)!important}
html body main .v235-plat>div:first-child{grid-row:auto}
html body main .v235-g4i{grid-template-columns:repeat(2,minmax(0,1fr))!important}
html body main .v235-g4i .sx-card,html body main .v235-g4i .sx-card:first-child{border-left:0!important;padding:4px 0!important}}
@media(max-width:600px){html body main .v235-g4i{grid-template-columns:minmax(0,1fr)!important}html body main .v235-plat>div:nth-child(3) ul{columns:1}}
"""
    return h, css


# ============================ PlantON ============================
@page('planton')
def planton(h):
    # 01 Outcomes: rows, icon and name left, description right, one panel
    def outcomes(s):
        s = sx_icons(s, ['link', 'trending-up', 'target', 'monitor', 'file-check'])
        return s.replace('<div class="sx-grid sx-g5">', '<div class="sx-grid sx-g5 v235-rows">', 1)
    h = edit_section(h, 'outcomes', outcomes)
    # 02 Pains: 2 x 2 with icons
    h = edit_section(h, 'pains', lambda s: sx_icons(s, ['file-text', 'zap', 'folder-search', 'triangle-alert']).replace(
        '<div class="sx-grid sx-g4">', '<div class="sx-grid sx-g4 v235-g22">', 1))
    # 03 Uses: two columns of icon cards
    h = edit_section(h, 'uses', lambda s: sx_icons(s, ['link', 'file-check', 'droplets', 'chart-column', 'shield-check', 'bell']).replace(
        '<div class="sx-grid sx-g3">', '<div class="sx-grid sx-g3 v235-g22">', 1))
    # 04 How it works: numbered rail with icons; four cards in a white panel
    def how(s):
        icons = iter(['plug', 'layers', 'monitor', 'chart-line', 'circle-check' if 'circle-check' in ICONS else 'badge-check'])
        s, n = re.subn(r'<div><b>(.*?)</b><span>(.*?)</span></div>',
                       lambda m: f'<li><strong>{m.group(1)}</strong><span>{m.group(2)}</span></li>', s)
        assert n == 5, n
        s = sub1(r'<div class="sx-flow">(.*?)</div>(\s*<div class="sx-grid sx-g4">)', r'<ol class="v235-rail-ol v235-flow" style="--n:5">\1</ol>\2', s)
        return s.replace('<div class="sx-grid sx-g4">', '<div class="sx-grid sx-g4 v235-panel4">', 1)
    h = edit_section(h, 'how', how)
    # 06 Deployment: connected numbered rail
    h = edit_section(h, 'deploy', lambda s: s.replace('<ol class="sx-steps h6 v24-flow">', '<ol class="sx-steps h6 v24-flow v235-rail-ol" style="--n:6">', 1))
    # 07 Results: figure-first columns in one panel
    h = edit_section(h, 'results', lambda s: s.replace('<div class="sx-grid sx-g3">', '<div class="sx-grid sx-g3 v235-results">', 1))
    # Discovery: inputs as a 2 x 2 checklist card
    h = edit_section(h, 'start', lambda s: s.replace('<div class="ready-panel">', '<div class="ready-panel v235-ready">', 1))
    # Related: two columns of link rows
    h = sub1(r'<div class="related-grid">', '<div class="related-grid v235-related">', h)

    css = CARD_CSS + RAIL_CSS + GRID22_CSS + r"""
/* v2.35 PlantON (approved 26 Nov) */
html body main .v235-rows{display:block!important;border:1px solid #d5dfec;border-top:3px solid #2D6AB4;border-radius:10px;background:#fff;overflow:hidden}
html body main .v235-rows .v235-icard{display:grid!important;grid-template-columns:40px minmax(0,3fr) minmax(0,7fr);column-gap:16px;align-items:center;padding:16px 22px!important;border:0!important;border-bottom:1px solid #e6ecf3!important;border-radius:0!important;box-shadow:none!important;margin:0!important;background:none!important}
html body main .v235-rows .v235-icard:last-child{border-bottom:0!important}
html body main .v235-rows .v235-ib{width:40px;height:40px;margin:0}
html body main .v235-rows h3{margin:0!important;font-size:17px!important}
html body main .v235-rows p{margin:0!important;padding-left:18px;border-left:1px solid #e6ecf3}
html body main #how .v235-flow{margin-bottom:28px!important}
html body main #how .v235-flow::before{background:rgba(255,255,255,.5)}
html body main #how .v235-flow>li::before{background:#0E2A47!important;border-color:#fff!important;color:#fff!important}
html body main #how .v235-flow>li>strong{color:#fff!important}
html body main #how .v235-flow>li>span{color:#d6e2ee!important}
html body main .v235-fico{display:none}
html body main .v235-panel4{background:#fff;border-radius:12px;padding:8px!important;gap:0!important}
html body main .v235-panel4 .sx-card{background:none!important;border:0!important;border-left:1px solid #e1e7ef!important;border-radius:0!important;box-shadow:none!important}
html body main .v235-panel4 .sx-card:first-child{border-left:0!important}
html body main .v235-panel4 .sx-card h3{color:#1A3668!important}
html body main .v235-panel4 .sx-card p{color:#4a5563!important}
html body main .v235-results{background:#F4F7FB;border-radius:12px;padding:8px!important;gap:0!important}
html body main .v235-results .sx-proj{background:none!important;border:0!important;border-left:1px solid #d5dfec!important;border-radius:0!important;box-shadow:none!important;padding:16px 22px!important}
html body main .v235-results .sx-proj:first-child{border-left:0!important}
html body main .v235-results .sx-fig{background:none!important;padding:0 0 14px!important;border-bottom:3px solid #5CBA3C;margin-bottom:14px;color:#1A1A1A!important}
html body main .v235-results .sx-fig strong{color:#2D6AB4!important;font-size:clamp(30px,3vw,40px)!important;line-height:1.1}
html body main .v235-results .sx-fig small{color:#555!important}
html body main .v235-results .sx-body{padding:0!important}
html body main .v235-ready ul{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;padding:0!important;list-style:none}
html body main .v235-ready li{background:#fff;border:1px solid #e1e7ef;border-radius:8px;padding:12px 12px 12px 38px!important;position:relative;margin:0!important;line-height:1.4}
html body main .v235-ready li::before{content:"✓"!important;position:absolute!important;left:12px;top:11px;width:18px;height:18px;border-radius:4px;background:#2D6AB4!important;color:#fff!important;font-size:12px;display:grid!important;place-items:center;font-weight:700}
html body main .v235-related{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:0 24px!important;border:1px solid #e1e7ef;border-radius:10px;background:#fff;padding:6px 18px!important}
html body main .v235-related .related-link{display:block!important;position:relative;padding:12px 40px 12px 14px!important;margin:8px 0!important;border:0!important;border-left:3px solid #5CBA3C!important;border-radius:0!important;background:none!important;box-shadow:none!important;min-height:0!important}
html body main .v235-related .related-link::after{content:"→"!important;position:absolute;right:6px;top:50%;transform:translateY(-50%);width:26px;height:26px;border-radius:50%;background:#EBF2FA;color:#2D6AB4;display:grid;place-items:center;font-size:14px}
@media(max-width:900px){html body main .v235-rows .v235-icard{grid-template-columns:40px minmax(0,1fr)}
html body main .v235-rows p{grid-column:1/-1;border-left:0;padding:8px 0 0}
html body main .v235-results,html body main .v235-panel4{grid-template-columns:minmax(0,1fr)!important}
html body main .v235-results .sx-proj,html body main .v235-panel4 .sx-card{border-left:0!important;border-bottom:1px solid #d5dfec!important}
html body main .v235-related,html body main .v235-ready ul{grid-template-columns:minmax(0,1fr)!important}}
"""
    return h, css



# ============================ How We Work ============================
@page('how')
def how(h):
    # 01 Starts with the application: heading and photo left, inputs card right, note strip below
    def overview(s):
        m = re.search(r'<div class="container intro-layout"><div>(<p class="eyebrow dark">.*?</h2>)(<ul class="sx-list v229-inputs">.*?</ul>)(<p class="v229-note">.*?</p>)(<a class="quiet-link".*?</a>)</div>(<figure class="intro-image">.*?</figure>)</div>', s, re.S)
        assert m, 'how overview'
        new = (f'<div class="container v235-ov"><div class="v235-ov-l">{m.group(1)}{m.group(5)}</div>'
               f'<div class="v235-ov-r">{m.group(2)}</div><div class="v235-ov-strip">{m.group(3)}{m.group(4)}</div></div>')
        return s[:m.start()] + new + s[m.end():]
    h = edit_section(h, 'overview', overview)
    # 03 Delivery logic: connected numbered rail
    h = edit_section(h, 'delivery', lambda s: s.replace('<ol class="process-flow">', '<ol class="process-flow v235-pflow">', 1))
    css = r"""
/* v2.35 How We Work (approved 26 Nov) */
html body main .v235-ov{display:grid!important;grid-template-columns:minmax(0,6fr) minmax(0,6fr);gap:20px 32px;align-items:start}
html body main .v235-ov-l h2{margin-bottom:20px!important}
html body main .v235-ov-l .intro-image{position:relative;margin:0!important;border-radius:10px;overflow:hidden}
html body main .v235-ov-l .intro-image img{display:block;width:100%;height:320px!important;object-fit:cover;border-radius:0!important}
html body main .v235-ov-l .intro-image figcaption{position:absolute;left:0;right:0;bottom:0;margin:0!important;padding:46px 18px 14px!important;background:linear-gradient(rgba(10,22,40,0),rgba(10,22,40,.85))!important;color:#fff!important}
html body main .v235-ov-r{background:#F4F7FB;border:1px solid #e1e7ef;border-radius:12px;padding:10px 24px}
html body main .v235-ov-r .v229-inputs{margin:0!important;gap:0!important}
html body main .v235-ov-r .v229-inputs li{border-left:0!important;border-bottom:1px solid #e1e7ef;padding:14px 0 14px 22px!important;position:relative}
html body main .v235-ov-r .v229-inputs li:last-child{border-bottom:0}
html body main .v235-ov-r .v229-inputs li::before{content:"";position:absolute;left:0;top:20px;width:8px;height:8px;border-radius:50%;background:#5CBA3C}
html body main .v235-ov-strip{grid-column:1/-1;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;background:#EBF2FA;border-radius:10px;padding:16px 22px}
html body main .v235-ov-strip .v229-note{margin:0!important}
html body main .v235-ov-strip .quiet-link::after{content:" →"}
html body main #approach .v229-strip .detail-card{border-top:0!important;position:relative;padding-top:26px!important;display:flex!important;flex-direction:column}
html body main #approach .v229-strip .detail-card .card-top{display:none!important}
html body main #approach .v229-strip .detail-card::before{content:"";position:absolute;left:24px;top:14px;width:36px;height:3px;background:#5CBA3C;border-radius:2px}
html body main #approach .v229-strip .ph-jump{display:flex!important;justify-content:space-between;align-items:center;margin-top:auto!important;padding-top:12px;border-top:1px solid #e6ecf3}
html body main #approach .v229-strip .ph-jump::after{content:"›";display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:#EBF2FA;color:#2D6AB4;font-size:17px;line-height:1}
html body main .v235-pflow{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:18px!important;position:relative;list-style:none;padding:24px!important;background:#F4F7FB;border-radius:12px}
html body main .v235-pflow::before{content:"";position:absolute;left:46px;right:46px;top:45px;height:2px;background:#2D6AB4}
html body main .v235-pflow li{position:relative;border:0!important;background:none!important;padding:0!important;display:block!important;box-shadow:none!important}
html body main .v235-pflow li::before,html body main .v235-pflow li::after{content:none!important;display:none!important}
html body main .v235-pflow .step-number{display:grid!important;place-items:center;width:44px;height:44px;border-radius:50%;border:2px solid #2D6AB4;background:#fff;color:#2D6AB4!important;font-weight:700;position:relative;z-index:1;margin-bottom:12px}
html body main .v235-pflow li>span:last-child{display:block;font-weight:600;line-height:1.4}
html body main #safety .safety-grid .detail-card{border-top:0!important;position:relative;padding-top:24px!important}
html body main #safety .safety-grid .detail-card .card-top{display:none!important}
html body main #safety .safety-grid .detail-card::before{content:"";position:absolute;left:0;top:22px;width:4px;height:44px;background:#2D6AB4;border-radius:0 2px 2px 0}
html body main #safety .safety-grid .detail-card:nth-child(even)::before{background:#5CBA3C}
@media(max-width:900px){html body main .v235-ov{grid-template-columns:minmax(0,1fr)}
html body main .v235-pflow{grid-template-columns:minmax(0,1fr)!important}
html body main .v235-pflow::before{left:45px;right:auto;top:46px;bottom:46px;width:2px;height:auto}
html body main .v235-pflow li{display:flex!important;align-items:center;gap:14px}
html body main .v235-pflow .step-number{margin:0;flex:none}}
"""
    return h, css


# ============================ Project Portfolio ============================
@page('portfolio')
def portfolio(h):
    h = edit_section(h, 'by-stage', lambda s: s.replace('<div class="ab-boxes">', '<div class="ab-boxes v235-stages">', 1))
    css = r"""
/* v2.35 Project Portfolio: From lab proof to production as a stage rail (approved 26 Nov) */
html body main .v235-stages{position:relative;padding:44px 22px 22px!important;background:#fff;border:1px solid #e1e7ef;border-radius:12px;gap:0!important}
html body main .v235-stages::before{content:"";position:absolute;left:34px;right:34px;top:26px;height:2px;background:#2D6AB4}
html body main .v235-stages::after{content:"";position:absolute;right:26px;top:21px;border:6px solid transparent;border-left:9px solid #2D6AB4;border-right:0}
html body main .v235-stages .ab-box{position:relative;background:none!important;border:0!important;border-left:1px solid #e6ecf3!important;border-radius:0!important;box-shadow:none!important;padding:14px 18px!important}
html body main .v235-stages .ab-box:first-child{border-left:0!important}
html body main .v235-stages .ab-box::before{content:""!important;position:absolute!important;left:18px;top:-24px;width:14px;height:14px;border-radius:50%;background:#fff;border:2px solid #2D6AB4;box-shadow:inset 0 0 0 3px #fff,inset 0 0 0 7px #5CBA3C;display:block!important}
html body main .v235-stages .pf-go::after{content:" →"}
@media(max-width:900px){html body main .v235-stages::before,html body main .v235-stages::after,html body main .v235-stages .ab-box::before{display:none!important}
html body main .v235-stages{padding:12px!important}
html body main .v235-stages .ab-box{border-left:0!important;border-bottom:1px solid #e6ecf3!important}}
"""
    return h, css


# ============================ Case Studies ============================
@page('cases')
def cases_page(h):
    h = sub1(r'<ul class="cs-index">', '<ul class="cs-index v235-csi">', h)
    css = r"""
/* v2.35 Case Studies: Fifteen projects as four-column link cards (approved 26 Nov) */
html body main .v235-csi{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:12px!important}
html body main .v235-csi li a{position:relative;display:flex!important;flex-direction:column;gap:6px;height:100%;padding:14px 40px 16px 16px!important;background:#fff!important;border:1px solid #e1e7ef!important;border-radius:10px!important;box-shadow:0 2px 8px rgba(14,42,71,.04)!important;text-decoration:none!important}
html body main .v235-csi li a:hover{border-color:#2D6AB4!important}
html body main .v235-csi li a::after{content:"→";position:absolute;right:12px;top:12px;color:#2D6AB4;font-size:15px}
html body main .v235-csi li a small{display:inline-block;align-self:flex-start;font-size:11px!important;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#2B7D30!important;background:#EEF7EA;border-radius:4px;padding:2px 7px}
html body main .v235-csi li a span{font-size:16px!important;font-weight:600;line-height:1.35}
@media(max-width:1000px){html body main .v235-csi{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
@media(max-width:560px){html body main .v235-csi{grid-template-columns:minmax(0,1fr)!important}}
"""
    return h, css


# ============================ write back ============================
out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('v2.35 pages changed:', ', '.join(CHANGED))
