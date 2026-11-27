"""v2.36: PlantON trademark on every visible mention (Rahul, 26 Nov 2026).

- Every PlantON wordmark gets <sup class="pon-tm">TM</sup> (previously only the first in the header and body).
- Plain-text PlantON (filter labels, solution tags, card tags, milestones, buttons, footer trademark line)
  gets the same <sup class="pon-tm">; inside <option> and <title> (text only) a plain TM character is used.
- Not changed: alt text, meta descriptions, CSS, scripts.
Usage: python3 -I v236_tm.py <review repo dir>
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
TM = '™'
SUP = '<sup class="pon-tm">™</sup>'


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


WM = re.compile(r'(<span class="pon(?: pon-dark)?"><span class="pon-p">Plant</span><span class="pon-o">ON</span>)(</span>)')
TOK = re.compile(r'(<style\b.*?</style>|<script\b.*?</script>|<!--.*?-->|<[^>]+>)', re.S)
stats = {'wordmark': 0, 'text': 0, 'plain': 0}


def fix_text(h):
    out, stack = [], []
    for part in TOK.split(h):
        if not part:
            continue
        if part.startswith('<'):
            m = re.match(r'<(/?)([a-zA-Z0-9]+)', part)
            if m and m.group(2).lower() in ('option', 'title', 'textarea'):
                if m.group(1):
                    if stack: stack.pop()
                else:
                    stack.append(m.group(2).lower())
            out.append(part)
            continue
        def rep(mm):
            if stack:
                stats['plain'] += 1
                return 'PlantON' + TM
            stats['text'] += 1
            return 'PlantON' + SUP
        out.append(re.sub(r'PlantON(?!™)', rep, part))
    return ''.join(out)


for key, p in DATA['pages'].items():
    h = p['html']
    h, n = WM.subn(lambda m: m.group(1) + SUP + m.group(2), h)
    stats['wordmark'] += n
    h = fix_text(h)
    p['html'] = h

out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print(stats)
