"""v2.46: founder cards as small circular photos with experience only (Rahul, 26 Nov 2026).
Each founder card: circular portrait, name, experience line, LinkedIn. The focus/role line is removed
("no designation"). Same card frame as the core team.
Usage: python3 -I v246_founders.py <review repo dir>   (refuses to run twice)
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
page = DATA['pages']['leadership']
h = page['html']
if 'instron-v246' in h:
    sys.exit('v2.46 already applied')

m = re.search(r'<div class="ab-founders">(.*?</div></article>)</div>', h, re.S)
if not m:
    sys.exit('founders grid not found')
block = m.group(0)
# face centre (x%, y%) per portrait, measured on the 560 x 560 crops
FOCUS = {'Rahul Shirude': '44% 30%', 'Milind Saindane': '48% 28%', 'Rahul Bhokare': '52% 26%'}
cards = []
for art in re.findall(r'<article class="ab-person">.*?</article>', block, re.S):
    name = re.search(r'<h3>([^<]+)</h3>', art).group(1)
    src_img = re.search(r'src="(__INSTRON_EMBED_ASSET_\w+__)"', art).group(1)
    yrs = re.search(r'<span class="yrs">([^<]+)</span>', art).group(1)
    link = re.search(r'<a class="v242-li".*?</a>', art, re.S).group(0)
    cards.append(
        f'<article class="ab-coreperson v246-founder"><div class="v246-photo">'
        f'<img alt="{name}" decoding="async" loading="lazy" src="{src_img}" style="transform-origin:{FOCUS[name]}"/></div>'
        f'<h3>{name}</h3><p class="v246-yrs">{yrs}</p>{link}</article>')
if len(cards) != 3:
    sys.exit(f'expected 3 founders, found {len(cards)}')
h = h.replace(block, '<div class="ab-founders v246-founders">' + ''.join(cards) + '</div>')

CSS = ('.ab-founders.v246-founders{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;max-width:980px}'
       '.v246-founder{display:flex;flex-direction:column;align-items:center}'
       '.v246-photo{width:132px;height:132px;border-radius:50%;overflow:hidden;margin:0 auto 16px;background:#e9e8e4;'
       'box-shadow:0 0 0 4px #fff,0 0 0 5px var(--line,#d5dfec)}'
       '.v246-photo img{display:block;width:100%;height:100%;object-fit:cover;transform:scale(1.35)}'
       '.v246-founder h3{font-size:20px}'
       '.v246-founder .v246-yrs{font-size:14.5px}'
       '@media(max-width:760px){.ab-founders.v246-founders{grid-template-columns:1fr;max-width:420px}}')
anchor = '<style id="instron-v242">'
if h.count(anchor) != 1:
    sys.exit('style anchor not found')
h = h.replace(anchor, f'<style id="instron-v246">{CSS}</style>' + anchor)

page['html'] = h
page['ids'] = sorted(set(page['ids']) | {'instron-v246'})
out = src[:M.start(2)] + json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026') + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok')
