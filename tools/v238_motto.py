"""v2.38: company motto "Let’s grow together" on every sales page's closing band (Rahul, 26 Nov 2026).

- Process Skid Plants, Pilot & Demonstration Plants, Industrial Process Skids: closing band had no label;
  adds <p class="eyebrow">Let’s grow together</p> above the H2.
- Solutions overview (closing label "Next step") and the Insights hub plus three articles (label "Next step"):
  label becomes "Let’s grow together".
- Every existing "Let's grow together" (straight apostrophe) becomes "Let’s grow together" (curly), as on About Us.
- Not changed: Contact, Applications overview, Privacy, Website Index (utility pages); headings, body copy, buttons.
Usage: python3 -I v238_motto.py <review repo dir>   (starts from the committed index.html; refuses to run twice)
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
P = DATA['pages']
MOTTO = 'Let’s grow together'


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def once(key, old, new):
    h = P[key]['html']
    if h.count(old) != 1:
        sys.exit(f'{key}: expected exactly one match for {old[:60]!r}, found {h.count(old)} (already applied?)')
    P[key]['html'] = h.replace(old, new)


# 1. Process Skid Plants pages: add the label above the closing H2.
for key in ('process', 'pilot', 'industrial'):
    once(key, '<section class="closing-band"><div class="shell"><h2>',
         f'<section class="closing-band"><div class="shell"><p class="eyebrow">{MOTTO}</p><h2>')

# 2. Solutions overview: closing label "Next step" -> motto.
once('solutions', '<div class="container closing-inner"><div><p class="eyebrow">Next step</p>',
     f'<div class="container closing-inner"><div><p class="eyebrow">{MOTTO}</p>')

# 3. Insights hub and articles: closing label "Next step" -> motto.
for key in ('insights', 'insight-plant-data', 'insight-scaleup', 'insight-brownfield'):
    once(key, '<section class="ab-close"><div class="mk-wrap"><div><p class="k">Next step</p>',
         f'<section class="ab-close"><div class="mk-wrap"><div><p class="k">{MOTTO}</p>')

# 4. One apostrophe style site-wide.
n = 0
for key, p in P.items():
    p['html'], c = re.subn(r"Let's grow together", MOTTO, p['html'])
    n += c

out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print({'labels_added': 3, 'labels_renamed': 5, 'apostrophes_fixed': n})
print({k: v['html'].count(MOTTO) for k, v in P.items() if MOTTO in v['html']})
