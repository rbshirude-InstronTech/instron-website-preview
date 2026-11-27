"""v2.44: customer testimonials (Sumit pointer 2, approved by Rahul 26 Nov 2026).

Source: the five testimonials on the live site (instrontechnologies.com/ca/, read 27 Nov 2026).
Attribution is role and customer type only: no person or company names (19 Nov rule).
Light edits only: spelling ("Trunkey", "KPI's"), IoT and PlantON™ styling, punctuation; the die-casting
quote is trimmed to its outcome sentences and "Instron Technologies LLP" reads "Instron Technologies".

- Home: "In our customers' words" after Selected Projects, all five quotes, solutions order.
- Process Skid Plants (after the case studies), Industrial Automation and PlantON (before the FAQ):
  one matching quote each.
Usage: python3 -I v244_testimonials.py <review repo dir>   (re-runnable)
"""
import sys, os, re, json

REPO = os.path.abspath(sys.argv[1])
src = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
P = DATA['pages']


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


TM = 'PlantON<sup class="pon-tm">™</sup>'
ROUTE = {'process': 'Process Skid Plants', 'automation': 'Industrial Automation', 'planton': TM}

Q = {
    'battery': ('process',
                'Instron Technologies successfully delivered a Pilot Skid Plant for Battery Recycling Technology within a '
                'challenging timeline, ensuring high quality and reliability. The plug-and-play skid system, flexible design '
                'for research trials, and advanced automation with SCADA-based real-time data monitoring have been invaluable. '
                'We are highly satisfied with their technical expertise and look forward to future collaborations.',
                'Senior Research Scientist', 'Research university, Middle East'),
    'cstr': ('process',
             'I want to acknowledge Instron Technologies for their exceptional work on our pharma processing units in India '
             f'and Australia. Instron delivered a fully automated CSTR system with {TM} IoT integration. Their professionalism '
             'and expertise have strengthened our trust in their partnership, and we look forward to a continued successful '
             'collaboration.',
             'General Manager', 'Pharmaceutical manufacturer'),
    'programmer': ('automation',
                   'I highly recommend Instron Technologies. Their dedicated programmer team has provided invaluable support '
                   'for our pharmaceutical and dairy projects. They are thorough, collaborative and always committed to '
                   'finding the best solutions.',
                   'Director', 'Turnkey solution provider, process industry'),
    'paintshop': ('planton',
                  'Instron’s team collaborated with our members to identify critical parameters and KPIs for our alloy wheel '
                  f'paint shop. They delivered an IoT-based {TM} solution with additional sensors, enabling real-time paint '
                  'shop monitoring and enhancing traceability, quality and productivity.',
                  'Plant Head', 'Automotive manufacturer'),
    'diecast': ('planton',
                'Instron Technologies developed an IoT solution linking 13 different machines and consolidating the data at '
                'one point, converting it into a daily MIS report circulated directly from the IIoT server. The real-time '
                'performance data is also displayed on the shop floor to support corrective action and decisions.',
                'Vice President', 'Die-casting manufacturer'),
}
HOME_ORDER = ['battery', 'cstr', 'programmer', 'paintshop', 'diecast']   # solutions order: skids, automation, PlantON
PAGE_QUOTE = {'process': 'battery', 'automation': 'programmer', 'planton': 'paintshop'}


def card(key, tag=True):
    route, text, role, org = Q[key]
    t = (f'<a class="ts-tag" data-review-route="{route}" href="__INSTRON_REVIEW_URL__#page={route}" target="_top">'
         f'{ROUTE[route]}</a>') if tag else ''
    return (f'<figure class="ts-card"><span class="ts-mark" aria-hidden="true">“</span>'
            f'<blockquote><p>{text}</p></blockquote>'
            f'<figcaption><strong>{role}</strong><span>{org}</span>{t}</figcaption></figure>')


NOTE = '<p class="ts-note">Customer names are withheld. References are available on request.</p>'

CSS = ('<style id="instron-v244">'
       '.ts-sec{background:#F3F6FA;padding:72px 0}'
       '.ts-wrap{max-width:1200px;margin:0 auto;padding:0 32px}'
       '.ts-eyebrow{margin:0 0 10px;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--blue,#2D6AB4)}'
       '.ts-sec h2{margin:0 0 28px;font-size:clamp(26px,2.6vw,36px);line-height:1.2;color:var(--navy,#1A3668)}'
       '.ts-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}'
       '.ts-card{position:relative;margin:0;background:#fff;border:1px solid var(--line,#d5dfec);border-radius:12px;padding:30px 26px 24px;display:flex;flex-direction:column}'
       '.ts-mark{position:absolute;top:6px;left:20px;font-size:64px;line-height:1;font-family:Georgia,serif;color:var(--green,#5CBA3C)}'
       '.ts-card blockquote{margin:22px 0 18px;padding:0;border:0;flex:1}'
       '.ts-card blockquote p{margin:0;font-size:16px;line-height:1.6;color:#2f3b4b}'
       '.ts-card figcaption{border-top:1px solid var(--line,#d5dfec);padding-top:14px}'
       '.ts-card figcaption strong{display:block;font-size:15px;color:var(--navy,#1A3668)}'
       '.ts-card figcaption span{display:block;font-size:14px;color:#5a6878;margin-top:2px}'
       '.ts-tag{display:inline-block;margin-top:12px;padding:4px 12px;border-radius:999px;background:#EAF5E5;color:#24612f;font-size:13px;font-weight:600;text-decoration:none}'
       '.ts-tag:hover,.ts-tag:focus-visible{text-decoration:underline}'
       '.ts-note{margin:22px 0 0;font-size:15px;color:#4a5b6e}'
       '.ts-single .ts-card{max-width:860px}'
       '.ts-single .ts-card blockquote p{font-size:18px}'
       '@media(max-width:1000px){.ts-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'
       '@media(max-width:640px){.ts-sec{padding:52px 0}.ts-wrap{padding:0 20px}.ts-grid{grid-template-columns:1fr}.ts-single .ts-card blockquote p{font-size:16px}}'
       '</style>')

home_sec = ('<section class="ts-sec" id="customer-testimonials" aria-labelledby="ts-title"><div class="ts-wrap">'
            '<p class="ts-eyebrow">What our customers say</p><h2 id="ts-title">In our customers’ words</h2>'
            '<div class="ts-grid">' + ''.join(card(k) for k in HOME_ORDER) + '</div>' + NOTE + '</div></section>')


def page_sec(key):
    return ('<section class="ts-sec ts-single" id="customer-testimonials" aria-labelledby="ts-title"><div class="ts-wrap">'
            '<p class="ts-eyebrow">Customer feedback</p><h2 id="ts-title">In our customer’s words</h2>'
            + card(key, tag=False) + NOTE + '</div></section>')


def clean(h):
    h = re.sub(r'<section class="ts-sec[^"]*" id="customer-testimonials".*?</section>', '', h, flags=re.S)
    return re.sub(r'<style id="instron-v244">.*?</style>', '', h, flags=re.S)


def insert_before(h, anchor, block):
    assert h.count(anchor) == 1, anchor
    return h.replace(anchor, block + anchor)


def add_css(h):
    m = list(re.finditer(r'<style id="instron-v[0-9]+">.*?</style>', h, re.S))[-1]
    return h[:m.end()] + CSS + h[m.end():]


ANCHORS = {
    'home': '<section aria-labelledby="work-title" class="website-module work-section section work" id="how-we-work-home">',
    'process': '<section class="closing-band">',
    'automation': '<section class="sx-sec sx-band" id="faq">',
    'planton': '<section class="sx-sec sx-band" id="faq">',
}
for key, anchor in ANCHORS.items():
    h = clean(P[key]['html'])
    h = insert_before(h, anchor, home_sec if key == 'home' else page_sec(PAGE_QUOTE[key]))
    h = add_css(h)
    P[key]['html'] = h
    P[key]['ids'] = sorted(set(P[key]['ids']) | {'customer-testimonials', 'ts-title', 'instron-v244'})

out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('testimonials: home 5, process/automation/planton 1 each')
