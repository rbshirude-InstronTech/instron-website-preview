"""v2.39: Careers page with team photos from the live instrontechnologies.com Career page (Rahul, 26 Nov 2026).

- Hero photo: control enclosures -> team outing photo (people first on a careers page).
- New section "Life at Instron Technologies" (id life-at-instron-technologies) right after the hero:
  four-photo mosaic (team day in "Let's grow together" jackets, office celebration under the motto wall,
  ropes course, Pune office team) with short captions. Copy draws only on statements already on the live
  Career page (training for new and experienced staff, get-togethers, team-building, sports, events, treks).
- Photos: /home/claude/careers-img/*.webp, taken from the live site's full-size uploads (Jan 2026).
- No other copy changed.
Usage: python3 -I v239_careers.py <review repo dir> <image dir>
"""
import sys, os, re, json, subprocess, hashlib, base64

REPO, IMG = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
page = DATA['pages']['careers']
h = page['html']
if 'instron-v239' in h:
    sys.exit('v2.39 already applied')


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def asset(name):
    raw = open(os.path.join(IMG, name + '.webp'), 'rb').read()
    key = '__INSTRON_EMBED_ASSET_' + hashlib.sha256(raw).hexdigest() + '__'
    DATA['assets'][key] = 'data:image/webp;base64,' + base64.b64encode(raw).decode()
    return key


def once(old, new):
    global h
    if h.count(old) != 1:
        sys.exit(f'expected one match for {old[:70]!r}, found {h.count(old)}')
    h = h.replace(old, new)


A = {k: asset(k) for k in ('outing', 'hero', 'celebration', 'adventure', 'office')}

# 1. Hero photo.
m = re.search(r'<figure class="ab-hero-photo"><img alt="Open industrial control enclosures with installed equipment"[^>]*/></figure>', h)
if not m:
    sys.exit('hero photo not found')
once(m.group(0), '<figure class="ab-hero-photo v239-hero"><img alt="Instron Technologies team members on a company outing" '
     f'decoding="async" src="{A["outing"]}" style="display:block;width:100%;height:100%;object-fit:cover"/></figure>')


# 2. Life at Instron Technologies.
def tile(cls, key, alt, title, text):
    return (f'<figure class="v239-tile {cls}"><img alt="{alt}" decoding="async" loading="lazy" src="{A[key]}"/>'
            f'<figcaption><strong>{title}</strong><span>{text}</span></figcaption></figure>')


LIFE = (
    '<section class="ab-sec off" id="life-at-instron-technologies"><div class="mk-wrap">'
    '<div class="mk-head"><div><p class="mk-eyebrow">Life at Instron Technologies</p>'
    '<h2>One team that learns, celebrates and grows together.</h2></div>'
    '<p>New team members get structured training, and experienced engineers take advanced courses. '
    'Outside project work, we make time for get-togethers, team-building, sports and treks.</p></div>'
    '<div class="v239-mosaic">'
    + tile('v239-big', 'hero', 'Instron Technologies team in matching jackets printed with Let’s grow together',
           'Let’s grow together', 'Our motto, worn on our team jackets.')
    + tile('', 'celebration', 'Team members at the Pune office holding gifts under a Let’s grow together wall sign',
           'Celebrate together', 'Festivals and get-togethers at the office.')
    + tile('', 'adventure', 'Team members in helmets and harnesses on an outdoor ropes course',
           'Step outside', 'Team-building, sports and treks.')
    + tile('v239-wide', 'office', 'Instron Technologies team at the Pune office in festive dress',
           'One team', 'Engineers, project staff and leadership working side by side.')
    + '</div></div></section>'
)
once('<section class="ab-sec" id="curiosity-and-ownership-grounded-in-engineering-evidence">',
     LIFE + '<section class="ab-sec" id="curiosity-and-ownership-grounded-in-engineering-evidence">')

# 3. Styles.
CSS = (
    '.v239-hero img{object-position:50% 38%}'
    '.v239-mosaic{display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:260px 260px;gap:16px}'
    '.v239-tile{position:relative;margin:0;border-radius:10px;overflow:hidden;background:#dfe7f1}'
    '.v239-tile img{display:block;width:100%;height:100%;object-fit:cover}'
    '.v239-big{grid-column:1/3;grid-row:1/3}'
    '.v239-wide{grid-column:3/5}'
    '.v239-tile figcaption{position:absolute;left:0;right:0;bottom:0;padding:44px 20px 16px;color:#fff;'
    'background:linear-gradient(180deg,rgba(14,32,62,0) 0%,rgba(14,32,62,.82) 62%,rgba(14,32,62,.9) 100%)}'
    '.v239-tile figcaption strong{display:block;font-size:18px;line-height:1.25;margin-bottom:4px}'
    '.v239-tile figcaption span{display:block;font-size:15px;line-height:1.45;color:rgba(255,255,255,.9)}'
    '.v239-big figcaption strong{font-size:24px}'
    '.v239-big img{object-position:50% 45%}.v239-wide img{object-position:50% 88%}.v239-wide figcaption{padding-top:30px}'
    '@media(max-width:900px){.v239-mosaic{grid-template-columns:1fr 1fr;grid-template-rows:none;grid-auto-rows:220px}'
    '.v239-big{grid-column:1/3;grid-row:auto}.v239-wide{grid-column:1/3}}'
    '@media(max-width:560px){.v239-mosaic{grid-template-columns:1fr;grid-auto-rows:240px}'
    '.v239-big,.v239-wide{grid-column:auto}}'
)
once('<style id="instron-v229">', f'<style id="instron-v239">{CSS}</style><style id="instron-v229">')

page['html'] = h
page['ids'] = sorted(set(page['ids']) | {'life-at-instron-technologies', 'instron-v239'})

out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok', {k: v[22:32] for k, v in A.items()})
