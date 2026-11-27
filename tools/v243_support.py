"""v2.43: 24/7 service support on the Home figures band (Sumit pointer 4, Rahul 26 Nov 2026).

Adds a fifth figure after "Since 2013": 24/7 · service support, linked to Contact.
The v2.41 band grid goes from four to five columns (two columns under 900 px, as before).
Usage: python3 -I v243_support.py <review repo dir>   (re-runnable)
"""
import sys, os, re, json

REPO = os.path.abspath(sys.argv[1])
src = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


page = DATA['pages']['home']
h = page['html']
LI = ('<li class="v242-support"><a data-review-route="contact" href="__INSTRON_REVIEW_URL__#page=contact" target="_top">'
      '<strong>24/7</strong><span>service support</span></a></li>')
h = re.sub(r'<li class="v242-support">.*?</li>', '', h, flags=re.S)
m = re.search(r'(<ul class="v241-figs"[^>]*>.*?)(</ul>)', h, re.S)
assert m and 'Since 2013' in m.group(1)
h = h[:m.end(1)] + LI + h[m.end(1):]
h = h.replace('.v241-figs{list-style:none;margin:0 0 40px;padding:0 0 36px;display:grid;grid-template-columns:repeat(4,1fr)',
              '.v241-figs{list-style:none;margin:0 0 40px;padding:0 0 36px;display:grid;grid-template-columns:repeat(5,1fr)')
assert 'repeat(5,1fr)' in h
page['html'] = h
out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('home figures:', len(re.findall(r'<li', re.search(r'<ul class="v241-figs".*?</ul>', h, re.S).group(0))))
