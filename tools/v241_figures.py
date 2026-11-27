"""v2.41: company figures on Home and Global Presence (Sumit 27 Nov, point 4; Rahul approved 26 Nov).

- Home, "Trusted since 2013 by": a four-figure row above the client-type tiles:
  200+ customers, 12 countries, 300+ industrial solutions, Since 2013. Customers and countries link to
  Global Presence #installed-footprint; industrial solutions links to the Project Portfolio.
  Static numbers (no count-up animation).
- Global Presence hero strip: "One team" item replaced by "200+ customers / Systems installed in 12 countries",
  linking to #installed-footprint.
- Not included (Rahul 26 Nov): 24/7 support, projects/installations counts, CO2 and energy figures, 35+ engineers.
Usage: python3 -I v241_figures.py <review repo dir>   (refuses to run twice)
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
P = DATA['pages']
if 'instron-v241' in P['home']['html']:
    sys.exit('v2.41 already applied')


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def link(page, section=None):
    if section:
        return (f'data-review-route="{page}" data-review-section="{section}" '
                f'href="__INSTRON_REVIEW_URL__#page={page}&amp;section={section}" target="_top"')
    return f'data-review-route="{page}" href="__INSTRON_REVIEW_URL__#page={page}" target="_top"'


def once(key, old, new):
    h = P[key]['html']
    if h.count(old) != 1:
        sys.exit(f'{key}: expected one match for {old[:70]!r}, found {h.count(old)}')
    P[key]['html'] = h.replace(old, new)


# 1. Home figures row.
FIGS = [('200+', 'customers', link('global', 'installed-footprint')),
        ('12', 'countries with installed systems', link('global', 'installed-footprint')),
        ('300+', 'industrial solutions delivered', link('portfolio')),
        ('Since 2013', 'engineering process and automation systems', None)]
items = ''.join(
    (f'<li><a {l}><strong>{n}</strong><span>{t}</span></a></li>' if l else f'<li><strong>{n}</strong><span>{t}</span></li>')
    for n, t, l in FIGS)
once('home', '<section class="v22-band mk-trust" id="trusted-by" aria-labelledby="trusted-title"><div class="v22-wrap">',
     '<section class="v22-band mk-trust" id="trusted-by" aria-labelledby="trusted-title"><div class="v22-wrap">'
     f'<ul class="v241-figs" aria-label="Instron Technologies in figures">{items}</ul>')

CSS_HOME = (
    '.v241-figs{list-style:none;margin:0 0 40px;padding:0 0 36px;display:grid;grid-template-columns:repeat(4,1fr);gap:24px;'
    'border-bottom:1px solid var(--line,#d5dfec)}'
    '.v241-figs li{margin:0;padding:0 0 0 18px;border-left:3px solid var(--green,#5CBA3C)}'
    '.v241-figs a{display:block;color:inherit;text-decoration:none}'
    '.v241-figs a:hover span,.v241-figs a:focus-visible span{text-decoration:underline;text-underline-offset:3px}'
    '.v241-figs strong{display:block;font-size:clamp(30px,3vw,42px);line-height:1.05;font-weight:700;color:var(--navy,#1A3668);letter-spacing:-.02em}'
    '.v241-figs span{display:block;margin-top:6px;font-size:15px;line-height:1.4;color:#4a5566}'
    '@media(max-width:900px){.v241-figs{grid-template-columns:1fr 1fr;gap:22px 18px;margin-bottom:30px;padding-bottom:28px}}'
)
h = P['home']['html']
anchor = re.search(r'<style id="instron-v235">', h) or re.search(r'<style id="[^"]+">', h)
P['home']['html'] = h[:anchor.start()] + f'<style id="instron-v241">{CSS_HOME}</style>' + h[anchor.start():]

# 2. Global Presence hero strip.
once('global', '<li><strong>One team</strong><span>Engineering across offices and regions</span></li>',
     f'<li><a class="v241-proof" {link("global", "installed-footprint")}><strong>200+ customers</strong>'
     '<span>Systems installed in 12 countries</span></a></li>')
CSS_GLOBAL = ('.v241-proof{display:block;color:inherit;text-decoration:none}.v241-proof,.v241-proof strong,.v241-proof span{display:block;text-align:left}'
              '.v241-proof:hover span,.v241-proof:focus-visible span{text-decoration:underline;text-underline-offset:3px}')
g = P['global']['html']
anchor = re.search(r'<style id="instron-v237">', g) or re.search(r'<style id="[^"]+">', g)
P['global']['html'] = g[:anchor.start()] + f'<style id="instron-v241">{CSS_GLOBAL}</style>' + g[anchor.start():]

for k in ('home', 'global'):
    P[k]['ids'] = sorted(set(P[k]['ids']) | {'instron-v241'})

out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok')
