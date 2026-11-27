"""v2.45: Growth team titles (Rahul, 26 Nov 2026).
- Mustapha Abdul: Marketing Lead, Canada (LinkedIn: company-page profile kept).
- Sneha Jagtap: Marketing Lead.
Usage: python3 -I v245_titles.py <review repo dir>   (refuses to run twice)
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
page = DATA['pages']['leadership']
h = page['html']

EDITS = [
    ('<small>Sales</small><h3>Sneha Jagtap</h3><p>Senior Executive, Sales. Pilot plants, process skids and automation.</p>',
     '<small>Marketing</small><h3>Sneha Jagtap</h3><p>Marketing Lead. Pilot plants, process skids and automation.</p>'),
    ('<small>Business Solutions</small><h3>Mustapha Abdul</h3><p>Business Solutions Consultant. MBA, PMP.</p>',
     '<small>Marketing, Canada</small><h3>Mustapha Abdul</h3><p>Marketing Lead, Canada. MBA, PMP.</p>'),
]
for old, new in EDITS:
    if h.count(old) != 1:
        sys.exit(f'expected one match for {old[:60]!r} (already applied?)')
    h = h.replace(old, new)

page['html'] = h
out = src[:M.start(2)] + json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026') + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok')
