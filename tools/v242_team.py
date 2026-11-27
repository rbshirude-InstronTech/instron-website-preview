"""v2.42: Leadership page, wider team with LinkedIn links (Rahul, 26 Nov 2026).

Adds after "Core team":
- Growth team (#growth-team): Saloni Dublay Gupta, Sneha Jagtap, Nasrin Ejner, Mustapha Abdul.
- Engineering team (#engineering-team): Ajay Deshmukh, Tushar Gangawane, Parshuram Kolpuse, Mayur Ghule,
  Jaydeep Ladvikar, Areeb Kamal, Sumit Patil.
- Mentors, advisors & partners (#mentors-advisors-partners): the four mentors from the live site
  (S. V. Bhokare, R. A. Raichur, Rajeev Khade, Prashant Joshi), advisors Rajiv Bavishi, Vinay Pandit,
  G.V. Shankar, partners David Valle (BusinessDMX) and Andert van der Kraan (Chemponics).
LinkedIn icon links (plain links, new tab, no LinkedIn scripts) on every card with a verified profile,
including founders and managers. Titles: LinkedIn self-description, HR sheet or email signature (26 Nov).
Usage: python3 -I v242_team.py <review repo dir>   (refuses to run twice)
"""
import sys, os, re, json, subprocess, html

REPO = os.path.abspath(sys.argv[1])
src = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:index.html'], capture_output=True, check=True).stdout.decode('utf-8')
M = re.search(r'(<script[^>]*id="instron-review-data"[^>]*>)(.*?)(</script>)', src, re.S)
DATA = json.loads(M.group(2))
page = DATA['pages']['leadership']
h = page['html']
if 'instron-v242' in h:
    sys.exit('v2.42 already applied')


def enc(o):
    s = json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    return s.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def once(old, new):
    global h
    if h.count(old) != 1:
        sys.exit(f'expected one match for {old[:70]!r}, found {h.count(old)}')
    h = h.replace(old, new)


LI_PATH = ('M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05'
           'c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13z'
           'M7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73'
           'V1.73C24 .77 23.2 0 22.22 0z')


def li(name, slug):
    if not slug:
        return ''
    return (f'<a class="v242-li" href="https://www.linkedin.com/in/{slug}/" target="_blank" rel="noopener noreferrer" '
            f'aria-label="{html.escape(name)} on LinkedIn (opens in a new tab)">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="{LI_PATH}"/></svg>'
            '<span>LinkedIn</span></a>')


def initials(name):
    parts = [p for p in re.sub(r',.*$', '', name).replace('.', ' ').split() if p[0].isupper()]
    return (parts[0][0] + parts[-1][0]) if len(parts) > 1 else parts[0][:2]


def card(name, role, line, slug):
    return (f'<article class="ab-coreperson v242-card"><div class="ab-face">{initials(name)}</div>'
            f'<small>{role}</small><h3>{name}</h3><p>{line}</p>{li(name, slug)}</article>')


# 1. LinkedIn on founders and managers.
for name, slug in [('Rahul Shirude', 'rahul-shirude-3a76b828'), ('Milind Saindane', 'milind-saindane-itllp'),
                   ('Rahul Bhokare', 'rahul-bhokare-851a7b15')]:
    m = re.search(rf'(<h3>{name}</h3>.*?<span class="yrs">[^<]*</span>)(</div></article>)', h, re.S)
    if not m:
        sys.exit(f'founder card not found: {name}')
    h = h[:m.end(1)] + li(name, slug) + h[m.end(1):]
for name, slug in [('Shailesh Bangale', 'shailesh-bangale-98622b23'), ('Rohit Shinde', 'rohit-shinde-60340999'),
                   ('Pawan Dhumane', 'dhumane-pawan-itllp'), ('Anjali Sinkar', 'anjali-sinkar-6380b8101')]:
    m = re.search(rf'(<h3>{name}</h3><p>[^<]*</p>)(</article>)', h)
    if not m:
        sys.exit(f'manager card not found: {name}')
    h = h[:m.end(1)] + li(name, slug) + h[m.end(1):]

# 2. New sections after Core team.
GROWTH = [
    ('Saloni Dublay Gupta', 'Business Development', 'Manager, Business Development. Process skids, pilot plants and scale-up.', 'saloni-dublay-gupta-77005434'),
    ('Sneha Jagtap', 'Sales', 'Senior Executive, Sales. Pilot plants, process skids and automation.', 'sneha-jagtap-377b93258'),
    ('Nasrin Ejner', 'Business Consulting', 'Engineer and Business Consultant.', 'nasrin-ejner'),
    ('Mustapha Abdul', 'Business Solutions', 'Business Solutions Consultant. MBA, PMP.', 'mustapha-abdul-888b7a2b9'),
]
ENG = [
    ('Ajay Deshmukh', 'Process', 'Senior Process Design Engineer. M.Tech, Chemical Technology.', 'ajay-deshmukh-532572154'),
    ('Tushar Gangawane', 'Projects', 'Senior Project Engineer.', 'tushar-gangawane-9679b7b6'),
    ('Parshuram Kolpuse', 'Instrumentation &amp; controls', 'Instrumentation and Control Engineer.', 'parshuram-kolpuse'),
    ('Mayur Ghule', 'Automation', 'Automation Engineer. PLC, SCADA and industrial control systems.', 'mayur-arjun-ghule-01aab4220'),
    ('Jaydeep Ladvikar', 'Projects', 'Project Engineer.', 'jaydeep-ladvikar-98a413175'),
    ('Areeb Kamal, MASc, EIT', 'Automation &amp; controls', 'Automation and Controls Engineer, Canada. Siemens and Rockwell PLCs, HMI/SCADA, commissioning.', 'kamal-areeb'),
    ('Sumit Patil', 'IT &amp; IIoT', 'Senior IT Engineer. Software and IIoT development.', 'sumitpatil198'),
]
MENTORS = [
    ('S. V. Bhokare', 'Mentor', 'Indian Navy veteran with 37+ years of leadership and project management.', None),
    ('R. A. Raichur', 'Mentor', '31+ years of consultancy in instrumentation system design.', None),
    ('Rajeev Khade', 'Mentor', '38 years in digitalization, IoT, Industry 4.0 and cloud transformation.', None),
    ('Prashant Joshi', 'Mentor', '30 years in automotive and engineering IT.', None),
]
ADVISORS = [
    ('Rajiv Bavishi', 'Advisor', 'Engineering and project advisor, Calgary. Technical reviews, project planning and process development.', 'rajivbavishi'),
    ('Vinay Pandit', 'Advisor', 'Digital workflows and ERPNext, Oakville.', 'vinay-pandit'),
    ('G.V. Shankar', 'Advisor', 'President and CEO, Global Connect Inc., Saskatoon. Business development in Saskatchewan.', 'g-v-shankar-1712284'),
]
PARTNERS = [
    ('David Valle', 'Partner · Mexico', 'Director, Business Development MX (BusinessDMX), Monterrey.', 'david-valle-79617628'),
    ('Andert van der Kraan', 'Partner · Netherlands', 'Owner and Founder, Chemponics B.V., Voorhout.', 'andert-van-der-kraan'),
]


def grid(items, cls=''):
    return f'<div class="v242-grid{cls}">' + ''.join(card(*i) for i in items) + '</div>'


GLOBAL_LINK = ('<a class="v242-more" data-review-route="global" data-review-section="partners" '
               'href="__INSTRON_REVIEW_URL__#page=global&amp;section=partners" target="_top">All partners on Global Presence</a>')
NEW = (
    '<section class="ab-sec" id="growth-team"><div class="mk-wrap"><div class="mk-head"><div>'
    '<p class="mk-eyebrow">Growth team</p><h2>The people who build our customer relationships.</h2></div>'
    '<p>Business development, sales and customer support, working alongside the engineers who deliver each project.</p></div>'
    + grid(GROWTH) + '</div></section>'
    '<section class="ab-sec off" id="engineering-team"><div class="mk-wrap"><div class="mk-head"><div>'
    '<p class="mk-eyebrow">Engineering team</p><h2>Engineers who design, build and commission the systems.</h2></div>'
    '<p>Process, project, automation and IT engineers across our Pune and Toronto teams.</p></div>'
    + grid(ENG) + '</div></section>'
    '<section class="ab-sec" id="mentors-advisors-partners"><div class="mk-wrap"><div class="mk-head"><div>'
    '<p class="mk-eyebrow">Mentors, advisors &amp; partners</p><h2>Experience we draw on beyond our own team.</h2></div>'
    '<p>Independent mentors and advisors who guide our engineering and growth, and partners who work with us in their markets.</p></div>'
    '<p class="v242-sub">Mentors</p>' + grid(MENTORS) +
    '<p class="v242-sub">Advisors</p>' + grid(ADVISORS, ' v242-three') +
    '<p class="v242-sub">Partners</p>' + grid(PARTNERS, ' v242-two') + GLOBAL_LINK +
    '</div></section>'
)
anchor = re.search(r'<section class="ab-sec off" id="the-managers-who-own-each-engineering-handoff">.*?</section>', h, re.S)
if not anchor:
    sys.exit('core team section not found')
h = h[:anchor.end()] + NEW + h[anchor.end():]

CSS = (
    '.v242-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}'
    '.v242-grid.v242-three{grid-template-columns:repeat(3,minmax(0,1fr))}'
    '.v242-grid.v242-two{grid-template-columns:repeat(2,minmax(0,1fr));max-width:760px}'
    '.v242-card{display:flex;flex-direction:column;align-items:center}'
    '.v242-card p{flex:1}'
    '.v242-sub{margin:34px 0 14px;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--navy,#1A3668)}'
    '.mk-head+.v242-sub{margin-top:0}'
    '.v242-li{display:inline-flex;align-items:center;gap:6px;margin-top:14px;font-size:13.5px;font-weight:600;'
    'color:#0A66C2;text-decoration:none}'
    '.v242-li svg{width:18px;height:18px;flex:none}'
    '.v242-li:hover span,.v242-li:focus-visible span{text-decoration:underline;text-underline-offset:3px}'
    '.ab-person .v242-li{display:flex;width:max-content}'
    '.v242-more{display:inline-block;margin-top:18px;font-weight:700;color:var(--navy,#1A3668)}'
    '@media(max-width:1000px){.v242-grid,.v242-grid.v242-three{grid-template-columns:repeat(2,minmax(0,1fr))}}'
    '@media(max-width:560px){.v242-grid,.v242-grid.v242-three,.v242-grid.v242-two{grid-template-columns:1fr}}'
)
once('<style id="instron-v229">', f'<style id="instron-v242">{CSS}</style><style id="instron-v229">')

page['html'] = h
page['ids'] = sorted(set(page['ids']) | {'growth-team', 'engineering-team', 'mentors-advisors-partners', 'instron-v242'})
out = src[:M.start(2)] + enc(DATA) + src[M.end(2):]
open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(out)
print('ok', len(GROWTH), len(ENG), len(MENTORS) + len(ADVISORS) + len(PARTNERS))
