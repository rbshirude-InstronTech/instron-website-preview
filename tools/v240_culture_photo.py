"""v2.40: Careers culture section shows people, not equipment (Rahul, 26 Nov 2026: "these two photos are not correct").

- "Curiosity and ownership, grounded in engineering evidence." collage: the two equipment photos
  (steam quality analyzer skids, stainless separation skid) are removed; the team training session
  photo at the Pune office becomes the single image for the section.
Usage: python3 -I v240_culture_photo.py <review repo dir>   (refuses to run twice)
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
page = DATA['pages']['careers']
h = page['html']
if 'instron-v240' in h:
    sys.exit('v2.40 already applied')


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


m = re.search(r'<div class="ab-collage">(<div class="ph"[^>]*><img alt="Instron Technologies engineers in a team training session[^>]*/></div>)'
              r'<div class="ph"[^>]*><img alt="Steam quality analyzer skids[^>]*/></div>'
              r'<div class="ph"[^>]*><img alt="Stainless-steel process equipment[^>]*/></div></div>', h)
if not m:
    sys.exit('culture collage not found')
h = h.replace(m.group(0), f'<div class="ab-collage v240-one">{m.group(1)}</div>')

CSS = ('.ab-collage.v240-one{grid-template-columns:1fr;grid-template-rows:none;height:100%;min-height:380px}'
       '.ab-collage.v240-one .ph{grid-row:auto;min-height:380px}'
       '.ab-collage.v240-one img{object-position:50% 60%}'
       '@media(max-width:900px){.ab-collage.v240-one{min-height:0}.ab-collage.v240-one .ph{min-height:260px}}')
h = h.replace('<style id="instron-v239">', f'<style id="instron-v240">{CSS}</style><style id="instron-v239">', 1)
if 'instron-v240' not in h:
    sys.exit('style anchor not found')

page['html'] = h
page['ids'] = sorted(set(page['ids']) | {'instron-v240'})
out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok')
