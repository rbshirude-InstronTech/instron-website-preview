"""v2.37: installed footprint on Global Presence & Partners (Rahul, 26 Nov 2026).

Adds the section "Where our systems run" right after "Where we are":
- world map in the same projection and style as the presence map (land outline reused from that map),
  the 12 countries with installations shaded and a dot per installation region;
- regions listed by area in the agreed order: Americas, Australia, Middle East, then Asia and Europe;
- end-user types in the agreed industry order; no customer names (19 Nov decision).
Country paths come from tools/v237_countries.json (world-atlas countries-110m, d3.geoNaturalEarth1
scale 218.11, translate [599.9, 324], fitted to the existing map's markers).
Usage: python3 -I v237_footprint.py <review repo dir>   (re-runnable: replaces an earlier v2.37 section)
"""
import sys, os, re, json, subprocess

REPO = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
PAGE = DATA['pages']['global']
h = PAGE['html']


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


# remove an earlier run
h = re.sub(r'<section class="ab-sec ice" id="installed-footprint">.*?</section>', '', h, flags=re.S)
h = re.sub(r'<style id="instron-v237">.*?</style>', '', h, flags=re.S)

# land outline from the existing presence map (first long path inside it)
pm = re.search(r'<svg class="ab-worldmap"[^>]*aria-labelledby="wm-t wm-d">.*?</svg>', h, re.S)
LAND = re.search(r'<path d="([^"]{1000,})" fill="#E3EAF3"/>', pm.group(0)).group(1)
COUNTRIES = json.load(open(os.path.join(HERE, 'v237_countries.json')))['d']

GREEN, NAVY, GREY = '#3E9B2B', '#1A3668', '#4b5d72'
HALO = 'stroke="#fff" stroke-width="4" stroke-linejoin="round" paint-order="stroke"'

# installation regions (x, y already projected)
DOTS = [(361, 154), (389, 144),            # Ontario, Quebec
        (229, 181), (327, 168),            # California, Illinois
        (278, 225),                        # Monterrey
        (1074, 454),                       # Sydney
        (750, 229), (727, 241),            # Riyadh, Jeddah
        (775, 230), (752, 211),            # UAE, Kuwait
        (846, 214), (854, 236), (840, 251), (855, 274), (886, 237),  # India N, C, W, S, E
        (864, 297), (930, 271),            # Colombo, Thailand
        (612, 129), (594, 121)]            # Belgium, UK

# (x, y, anchor, country, sub-line)
LABELS = [(402, 140, 'start', 'Canada', 'Ontario · Quebec'),
          (216, 178, 'end', 'United States', 'California · Illinois'),
          (265, 230, 'end', 'Mexico', 'Monterrey'),
          (1088, 459, 'start', 'Australia', 'Sydney'),
          (714, 246, 'end', 'Saudi Arabia', 'Riyadh · Jeddah'),
          (742, 205, 'end', 'Kuwait', ''),
          (787, 226, 'start', 'UAE', ''),
          (862, 207, 'start', 'India', ''),
          (877, 309, 'start', 'Sri Lanka', 'Colombo'),
          (943, 276, 'start', 'Thailand', ''),
          (581, 112, 'end', 'United Kingdom', ''),
          (624, 140, 'start', 'Belgium', '')]

svg = ['<svg class="ab-worldmap fp-worldmap" viewBox="0 0 1200 560" role="img" aria-labelledby="fp-t fp-d">',
       '<title id="fp-t">Countries where Instron Technologies systems are installed</title>',
       '<desc id="fp-d">Installations in Canada (Ontario, Quebec), the United States (California, Illinois), '
       'Mexico (Monterrey), Australia (Sydney), Saudi Arabia (Riyadh, Jeddah), the United Arab Emirates, Kuwait, '
       'India (north, south, east, west and central), Sri Lanka (Colombo), Thailand, Belgium and the United Kingdom.</desc>',
       f'<path d="{LAND}" fill="#E3EAF3"/>',
       f'<path d="{COUNTRIES}" fill="#CFE6C6" stroke="#fff" stroke-width=".8"/>']
for x, y in DOTS:
    svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{GREEN}" stroke="#fff" stroke-width="2.5"/>')
for x, y, a, name, sub in LABELS:
    svg.append(f'<text x="{x}" y="{y}" text-anchor="{a}" font-size="15" font-weight="700" fill="{NAVY}" {HALO}>{name}</text>')
    if sub:
        svg.append(f'<text x="{x}" y="{y + 17}" text-anchor="{a}" font-size="13" font-weight="500" fill="{GREY}" {HALO}>{sub}</text>')
svg.append('</svg>')

AREAS = [('Americas', [('Canada', 'Ontario · Quebec'), ('United States', 'California · Illinois'),
                       ('Mexico', 'Monterrey, Nuevo León')]),
         ('Australia', [('Australia', 'Sydney, New South Wales')]),
         ('Middle East', [('Saudi Arabia', 'Riyadh · Jeddah'), ('United Arab Emirates', ''), ('Kuwait', '')]),
         ('Asia', [('India', 'North, South, East, West and Central India'), ('Sri Lanka', 'Colombo'), ('Thailand', '')]),
         ('Europe', [('Belgium', ''), ('United Kingdom', '')])]
areas = ''.join(
    '<div><small>%s</small><ul>%s</ul></div>' % (
        area, ''.join('<li><b>%s</b>%s</li>' % (c, f'<span>{s}</span>' if s else '') for c, s in items))
    for area, items in AREAS)

# agreed industry order (19 Nov): energy transition, research, chemicals, food, pharma, manufacturing
USERS = ['Hydrogen, gas processing and resource-recovery operators',
         'Research universities and national laboratories',
         'Chemical, edible-oil and consumer-products producers',
         'Dairy, cheese and food processors',
         'Pharmaceutical manufacturers',
         'Electronics, automotive and industrial manufacturers']

PON = '<span class="pon"><span class="pon-p">Plant</span><span class="pon-o">ON</span><sup class="pon-tm">™</sup></span>'
section = (
    '<section class="ab-sec ice" id="installed-footprint"><div class="mk-wrap">'
    '<div class="mk-head"><div><p class="mk-eyebrow">Where our systems run</p>'
    '<h2>Installed for customers in 12 countries.</h2></div>'
    f'<p>Process skid plants, automation systems and {PON} deployments engineered by Instron Technologies '
    'are installed at customer sites across the Americas, Australia, the Middle East, Asia and Europe.</p></div>\n'
    '<div class="ab-map fp-map">' + ''.join(svg) +
    '<div class="ab-legend"><span><i style="background:#CFE6C6;border-radius:3px"></i>Country with installations</span>'
    f'<span><i style="background:{GREEN}"></i>Installation region</span></div>'
    f'<div class="fp-regions">{areas}</div></div>\n'
    '<div class="fp-users"><small>End users</small><ul class="fp-chips">' +
    ''.join(f'<li>{u}</li>' for u in USERS) + '</ul>'
    '<p class="fp-note">Customer names are kept confidential on this site. References are available on request.</p></div>'
    '</div></section>')

CSS = ('<style id="instron-v237">'
       '.fp-regions{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:18px 24px;margin-top:22px;padding:20px 10px 10px;border-top:1px solid var(--line)}'
       '.fp-regions small,.fp-users small{display:block;font-size:12.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);margin-bottom:10px}'
       '.fp-regions ul{margin:0;padding:0;list-style:none;display:grid;gap:10px}'
       '.fp-regions li{font-size:15px;line-height:1.4;color:#4b5d72}'
       '.fp-regions b{display:block;color:var(--navy)}'
       '.fp-users{margin-top:28px}'
       '.fp-chips{display:flex;flex-wrap:wrap;gap:10px;margin:0;padding:0;list-style:none}'
       '.fp-chips li{background:#fff;border:1px solid var(--line);border-radius:20px;padding:8px 16px;font-size:14.5px;color:var(--navy)}'
       '.fp-note{margin:16px 0 0;font-size:15px;color:#4a5b6e}'
       '@media(max-width:1100px){.fp-regions{grid-template-columns:repeat(3,minmax(0,1fr))}}'
       '@media(max-width:700px){.fp-regions{grid-template-columns:1fr 1fr}}'
       '@media(max-width:460px){.fp-regions{grid-template-columns:1fr}}'
       '</style>')

anchor = '<section class="ab-sec off" id="full-addresses-for-our-two-company-offices">'
assert h.count(anchor) == 1
h = h.replace(anchor, section + anchor)
sm = re.search(r'<style id="instron-v228">.*?</style>', h, re.S)
h = h[:sm.end()] + CSS + h[sm.end():]

PAGE['html'] = h
PAGE['ids'] = sorted(set(PAGE['ids']) | {'installed-footprint', 'instron-v237', 'fp-t', 'fp-d'})
out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('global page:', len(h), 'chars; dots', len(DOTS), 'labels', len(LABELS))
