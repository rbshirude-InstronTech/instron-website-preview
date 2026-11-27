"""v2.26 search and share layer for the Instron Technologies website (Rahul, 24 Nov 2026: "SEO friendly and appealing").

Adds to every page: a search title and description written for that page, a canonical URL, Open Graph and
Twitter share tags with a branded 1200x630 share image, and schema.org JSON-LD (Organization, WebSite,
BreadcrumbList, Service, FAQPage, Article). Writes robots.txt, sitemap.xml and llms.txt at the site root.

Every fact used here is already stated on the site. Nothing is marked up that a visitor cannot see.

Usage:  python3 -I tools/seo.py <site root>      (also called by build.py after each page is written)
Go-live: set GO_LIVE = True (removes the noindex tag) and check SITE matches the final address.
"""
import os, re, sys, json, html

GO_LIVE = False                      # keep noindex on the GitHub preview; flip at launch
SITE = 'https://instrontechnologies.com/'   # matches the live site's canonical host (no www)
NAME = 'Instron Technologies'
CLARIFIER = 'Independent company, not affiliated with Instron® (ITW).'
EMAIL = 'sales@instrontechnologies.com'
LOGO = 'assets/img/afd2b6d3f3.png'
SOCIAL = ['https://www.linkedin.com/company/instrontechnologies/', 'https://www.youtube.com/@instrontechnologiesllp6630',
          'https://www.instagram.com/instrontechnologies0510/', 'https://www.facebook.com/InstronTech', 'https://x.com/InstronTech']

# key: (slug, search title, description, breadcrumb parent key or None, short label for breadcrumb/share card, kind)
P = {
 'home': ('index', 'Pilot Plants & Process Skid Plants | Instron Technologies',
   'Pilot plants, demonstration plants, process skids, industrial automation and PlantON™ plant data, engineered and built by Instron Technologies since 2013.',
   None, 'Home', 'home'),
 'solutions': ('solutions', 'Process Skids, Automation & Plant Data | Instron Technologies',
   'Three solutions from one engineering team: process skid plants, industrial automation and controls, and PlantON™ by Instron Technologies for plant data.',
   'home', 'Solutions', 'page'),
 'process': ('process-skid-plants', 'Modular Process Skid Plants | Instron Technologies',
   'Pilot and demonstration plants and modular industrial process skids, engineered around your process with instruments, automation and site interfaces.',
   'solutions', 'Process Skid Plants', 'service'),
 'pilot': ('pilot-demonstration-plants', 'Pilot Plants & Demonstration Plants | Instron Technologies',
   'Pilot plants and demonstration plants for research centres, refinery R&D and technology developers, built for controlled trials and scale-up decisions.',
   'process', 'Pilot Plants & Demonstration Plants', 'service'),
 'industrial': ('industrial-process-skids', 'Industrial Process Skids | Instron Technologies',
   'Modular process skids for defined production duties: process engineering, equipment, instrumentation and automation for reliable operation on your site.',
   'process', 'Industrial Process Skids', 'service'),
 'automation': ('industrial-automation', 'Industrial Automation: PLC, HMI & SCADA | Instron Technologies',
   'E&I design, PLC, HMI and SCADA engineering, control panels and S88 batch control for new lines, upgrades and running plants.',
   'solutions', 'Industrial Automation & Controls', 'service'),
 'planton': ('planton-digital-factory', 'PlantON™ by Instron Technologies | OEE & Traceability',
   'PlantON™ turns PLC, SCADA, meter and business-system data into traceability, OEE, compliance reports and production views, without replacing your controls.',
   'solutions', 'PlantON™ by Instron Technologies', 'service'),
 'how': ('how-we-work', 'How We Work: Three Engineering Phases | Instron Technologies',
   'Basic Engineering & Feasibility, Detailed Engineering and Integrated Design & Build, each contracted on its own with no obligation to continue.',
   'home', 'How We Work', 'page'),
 'industries': ('industries', 'Industries We Engineer For | Instron Technologies',
   'Process systems for energy transition and critical minerals, research, chemicals and refining, food, beverage and dairy, pharma and manufacturing.',
   'home', 'Industries', 'page'),
 'cleantech': ('energy-transition-critical-minerals', 'Energy Transition & Critical Minerals | Instron Technologies',
   'Pilot and demonstration plants and modular skids for battery recycling, critical-mineral recovery, carbon capture, hydrogen and electrochemical systems.',
   'industries', 'Energy Transition & Critical Minerals', 'page'),
 'research': ('research-technology-development', 'Research & Technology Development | Instron Technologies',
   'Pilot and demonstration plants, custom process systems, test rigs and reactor engineering for universities, research institutes and technology developers.',
   'industries', 'Research & Technology Development', 'page'),
 'chemical': ('chemicals-refining-consumer-products', 'Chemicals, Refining & Consumer Products | Instron Technologies',
   'Solvent recovery and distillation skids, reactor control and batch automation for specialty chemicals, refining and consumer products.',
   'industries', 'Chemicals, Refining & Consumer Products', 'page'),
 'food': ('food-beverage-dairy', 'Food, Beverage & Dairy Engineering | Instron Technologies',
   'Batch control, CIP automation, pasteurizer records and utility data for food, beverage and dairy plants, from process skids to daily reports.',
   'industries', 'Food, Beverage & Dairy', 'page'),
 'pharma': ('pharma-life-sciences', 'Pharma & Life Sciences Process Skids | Instron Technologies',
   'Automated process skids and control systems with S88 batch control and 21 CFR Part 11 audit trails, validated with your quality team.',
   'industries', 'Pharma & Life Sciences', 'page'),
 'manufacturing': ('industrial-manufacturing', 'Manufacturing Automation & OEE | Instron Technologies',
   'Machine and line integration, brownfield controls and plant data for discrete manufacturing plants, connected to the equipment you already have.',
   'industries', 'Industrial Manufacturing', 'page'),
 'portfolio': ('project-portfolio', 'Project Portfolio | Instron Technologies',
   'Selected projects, from pilot skids and research systems to plant-wide automation and PlantON™ deployments. Client names withheld; references on request.',
   'home', 'Project Portfolio', 'page'),
 'cases': ('case-studies', 'Case Studies | Instron Technologies',
   'Fifteen projects in full: the situation, the scope we delivered and the measured result, across process skids, automation and plant data.',
   'home', 'Case Studies', 'page'),
 'company': ('our-company', 'About Instron Technologies | Engineering Since 2013',
   'Instron Technologies is an applied engineering and execution partner for process systems, industrial automation, plant data and technology scale-up.',
   'home', 'Our Company', 'about'),
 'global': ('global-presence', 'Global Presence: Toronto & Pune | Instron Technologies',
   'One engineering team with company offices in Toronto and Pune and regional presence across Canada, India, Saudi Arabia, the Netherlands and Mexico.',
   'company', 'Global Presence & Partners', 'page'),
 'leadership': ('leadership', 'Leadership & Engineering Team | Instron Technologies',
   'Meet the engineering leaders behind Instron Technologies, and the accountable project teams that deliver process, energy and automation systems.',
   'company', 'Leadership & Engineering Team', 'page'),
 'trust': ('trust-responsibility', 'Trust & Responsibility | Instron Technologies',
   'How Instron Technologies handles process safety, validation, cybersecurity, confidentiality and engineering sign-off, agreed for each project.',
   'company', 'Trust & Responsibility', 'page'),
 'careers': ('careers', 'Engineering Careers | Instron Technologies',
   'Engineering roles, internships and final-year projects at Instron Technologies, where process, instruments, automation and delivery meet on real plants.',
   'company', 'Careers', 'page'),
 'contact': ('contact', 'Contact Us: Discuss Your Project | Instron Technologies',
   'Talk to an engineer about your process, current stage and next milestone. Company offices in Toronto and Pune; email sales@instrontechnologies.com.',
   'home', 'Contact', 'contact'),
 'legal': ('privacy-terms-accessibility', 'Privacy, Terms & Accessibility | Instron Technologies',
   'How Instron Technologies handles personal information, the terms of this website, our approach to accessibility, and how our name relates to others.',
   'home', 'Privacy, Terms & Accessibility', 'page'),
 'applications': ('applications', 'Process & Automation Applications | Instron Technologies',
   'Applications we engineer: technology scale-up, separation and solvent recovery, brownfield modernization, batch automation, OEE and utility monitoring.',
   'solutions', 'Applications', 'page'),
 'scaleup': ('technology-scale-up', 'Technology Scale-Up & Commercialization | Instron Technologies',
   'Engineering the step from pilot evidence to demonstration or commercial deployment: equipment, utilities, instruments, operating ranges and safety.',
   'applications', 'Technology Scale-Up & Commercialization', 'service'),
 'separation': ('separation-solvent-recovery', 'Separation & Solvent Recovery | Instron Technologies',
   'Separation and solvent recovery systems engineered as a full loop: feed variation, utilities, solvent management, fouling and safe operation.',
   'applications', 'Separation & Solvent Recovery', 'service'),
 'modernization': ('brownfield-automation-modernization', 'Brownfield PLC & SCADA Modernization | Instron Technologies',
   'Modernize old PLC and SCADA systems in a plant that must keep running, starting from the installed logic, equipment and shutdown windows.',
   'applications', 'Brownfield Automation Modernization', 'service'),
 'batch': ('batch-process-automation', 'Batch & Process Automation | Instron Technologies',
   'Batch automation that brings manual steps, PLC sequences, recipes, material movements and records together without hiding what operators need.',
   'applications', 'Batch & Process Automation', 'service'),
 'oee': ('production-visibility-oee', 'Production Visibility & OEE | Instron Technologies',
   'Production visibility and OEE built on agreed definitions of running time, planned stops, counts, scrap and downtime, so the number supports a decision.',
   'applications', 'Production Visibility & OEE', 'service'),
 'utilities': ('utility-energy-monitoring', 'Utility & Energy Monitoring | Instron Technologies',
   'Utility and energy monitoring that links consumption to the line, batch, area or asset behind it, with clear measurement boundaries and reliable sources.',
   'applications', 'Utility & Energy Monitoring', 'service'),
 'insights': ('insights', 'Engineering Insights | Instron Technologies',
   'Practical engineering articles from Instron Technologies on scale-up, automation modernization and plant data, drawn from projects we have delivered.',
   'home', 'Insights', 'page'),
 'insight-plant-data': ('insights-plant-data-rollout', 'Plant Data People Actually Use | Instron Technologies',
   'Why plant-data projects stall after the pilot, and a six-step rollout that keeps them moving, with results from a dairy and a die-casting plant.',
   'insights', 'Start with one loss: plant data people actually use', 'article'),
 'insight-scaleup': ('insights-lab-to-pilot-to-industrial', 'Lab to Pilot to Industrial Scale-Up | Instron Technologies',
   'Each stage of scale-up answers a different question. What changes in instruments, automation, safety and documentation from pilot to industrial plant.',
   'insights', 'From lab to pilot to industrial: what changes at each step', 'article'),
 'insight-brownfield': ('insights-brownfield-modernization', 'Modernize a Running Plant | Instron Technologies',
   'How to modernize controls in a plant that is already producing: audit first, keep what works, test before site and cut over in planned windows.',
   'insights', 'Modernize a running plant without starting again', 'article'),
 'sitemap': ('website-index', 'Website Index | Instron Technologies',
   'Every page on the Instron Technologies website: solutions, industries, applications, projects, insights and company information.',
   'home', 'Website Index', 'page'),
}
BY_SLUG = {v[0]: k for k, v in P.items()}
for k, v in P.items():
    assert len(v[1]) <= 63, (k, len(v[1]))
    assert 70 <= len(v[2]) <= 158, (k, len(v[2]))
    assert '—' not in v[1] + v[2] and '#' not in v[2], k
    assert NAME in v[1], k


def url(key):
    s = P[key][0]
    return SITE if s == 'index' else SITE + s + '.html'


def text(fragment):
    t = re.sub(r'<(br|/p|/li|/div)[^>]*>', ' ', fragment)
    t = re.sub(r'<[^>]+>', '', t)
    return ' '.join(html.unescape(t).split())


ORG_ID = SITE + '#organization'
ORG = {
 '@type': 'Organization', '@id': ORG_ID, 'name': NAME, 'url': SITE, 'logo': SITE + LOGO, 'email': EMAIL,
 'foundingDate': '2013', 'slogan': 'Engineer | Embrace | Elevate',
 'description': 'Instron Technologies engineers and builds integrated process systems for technology developers and industrial '
                'manufacturers, from pilot and demonstration plants to industrial skids, with the automation and plant data to run them.',
 'disambiguatingDescription': CLARIFIER,
 'knowsAbout': ['Process skid plants', 'Pilot and demonstration plants', 'Industrial process skids', 'Industrial automation',
                'PLC, HMI and SCADA engineering', 'S88 batch control', 'Plant data and OEE', 'Technology scale-up'],
 'address': [
   {'@type': 'PostalAddress', 'name': 'Instron Technologies Inc.', 'streetAddress': '111 Peter Street, Suite 902',
    'addressLocality': 'Toronto', 'addressRegion': 'ON', 'postalCode': 'M5V 2H1', 'addressCountry': 'CA'},
   {'@type': 'PostalAddress', 'name': 'Instron Technologies LLP', 'streetAddress': 'Plot No. 88, Block F-II, Pimpri Industrial Area, MIDC, Bhosari',
    'addressLocality': 'Pune', 'addressRegion': 'Maharashtra', 'postalCode': '411018', 'addressCountry': 'IN'}],
 'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'availableLanguage': 'English'},
 'sameAs': SOCIAL,
}


def faqs(h):
    out = []
    for m in re.finditer(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>', h, re.S):
        q, a = text(m.group(1)), text(m.group(2))
        if q.endswith('?') and len(a) > 20:
            out.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    return out


def jsonld(key, h, img):
    slug, title, desc, parent, label, kind = P[key]
    g = []
    if key in ('home', 'contact', 'company', 'global'):
        g.append(ORG)
    if key == 'home':
        g.append({'@type': 'WebSite', '@id': SITE + '#website', 'url': SITE, 'name': NAME, 'publisher': {'@id': ORG_ID}, 'inLanguage': 'en'})
    ptype = {'about': 'AboutPage', 'contact': 'ContactPage'}.get(kind, 'WebPage')
    page = {'@type': ptype, '@id': url(key) + '#webpage', 'url': url(key), 'name': title, 'description': desc,
            'isPartOf': {'@id': SITE + '#website'}, 'about': {'@id': ORG_ID}, 'primaryImageOfPage': SITE + img, 'inLanguage': 'en'}
    if parent:
        chain, k = [], key
        while k:
            chain.append(k); k = P[k][3]
        chain.reverse()
        bc = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': P[c][4], 'item': url(c)} for i, c in enumerate(chain)]}
        g.append(bc); page['breadcrumb'] = bc
    g.append(page)
    if kind == 'service':
        g.append({'@type': 'Service', 'name': label, 'serviceType': label, 'description': desc, 'url': url(key),
                  'provider': {'@id': ORG_ID}, 'areaServed': 'Worldwide'})
    if kind == 'article':
        g.append({'@type': 'Article', 'headline': label, 'description': desc, 'url': url(key), 'image': SITE + img,
                  'author': {'@type': 'Organization', 'name': 'Instron Technologies engineering team', 'url': SITE},
                  'publisher': {'@id': ORG_ID}, 'mainEntityOfPage': url(key), 'inLanguage': 'en'})
    q = faqs(h)
    if q:
        g.append({'@type': 'FAQPage', 'mainEntity': q})
    return json.dumps({'@context': 'https://schema.org', '@graph': g}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def hero(h):
    m = re.search(r'<img[^>]*fetchpriority="high"[^>]*>', h) or re.search(r'<img(?![^>]*logo)[^>]*src="assets/img/[^"]+"[^>]*>', h)
    return re.search(r'src="(assets/img/[^"]+)"', m.group(0)).group(1) if m else None


# ---------------- branded share images (1200x630) ----------------
def fonts(root):
    from fontTools.ttLib import TTFont
    out = {}
    for w in ('700', '500'):
        src = os.path.join(root, f'assets/fonts/roboto-latin-{w}-normal.woff2')
        dst = f'/tmp/roboto-{w}.ttf'
        if not os.path.exists(dst):
            f = TTFont(src); f.flavor = None; f.save(dst)
        out[w] = dst
    return out


def share_image(root, key, src, ft):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    im = Image.open(os.path.join(root, src)).convert('RGB')
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((l, t, l + W, t + H))
    shade = Image.new('L', (W, H))
    px = shade.load()
    for x in range(W):            # navy panel on the left, fading to clear photo on the right
        a = 235 if x < 520 else max(0, int(235 * (1 - (x - 520) / 420)))
        for y in range(H):
            px[x, y] = a
    im = Image.composite(Image.new('RGB', (W, H), (10, 45, 74)), im, shade)
    d = ImageDraw.Draw(im)
    small = ImageFont.truetype(ft['500'], 26)
    d.text((64, 64), 'INSTRON TECHNOLOGIES', font=small, fill=(255, 255, 255))
    d.rectangle((64, 106, 140, 112), fill=(97, 206, 112))
    label = 'Process Skid Plants, Automation & Plant Data' if key == 'home' else P[key][4]
    size = 58
    while True:
        big = ImageFont.truetype(ft['700'], size)
        words, lines, cur = label.split(), [], ''
        for w in words:
            nxt = (cur + ' ' + w).strip()
            if d.textlength(nxt, font=big) <= 560: cur = nxt
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 4 or size <= 40: break
        size -= 4
    y = H - 96 - len(lines) * int(size * 1.18)
    for ln in lines:
        d.text((64, y), ln, font=big, fill=(255, 255, 255)); y += int(size * 1.18)
    d.text((64, H - 76), 'instrontechnologies.com', font=small, fill=(196, 214, 230))
    rel = f'assets/og/{P[key][0]}.jpg'
    os.makedirs(os.path.join(root, 'assets/og'), exist_ok=True)
    im.save(os.path.join(root, rel), 'JPEG', quality=84, optimize=True, progressive=True)
    return rel


# ---------------- page rewrite ----------------
def apply(h, key, root, ft=None):
    slug, title, desc, parent, label, kind = P[key]
    h = re.sub(r'<!--seo-->.*?<!--/seo-->', '', h, flags=re.S)                       # idempotent
    h = re.sub(r'<title>.*?</title>', '<title>' + html.escape(title, quote=False) + '</title>', h, count=1, flags=re.S)
    e = html.escape(desc)
    if re.search(r'<meta content="[^"]*" name="description"/?>', h):
        h = re.sub(r'<meta content="[^"]*" name="description"/?>', f'<meta content="{e}" name="description"/>', h, count=1)
    else:
        h = h.replace('</title>', f'</title><meta content="{e}" name="description"/>', 1)
    if GO_LIVE:
        h = re.sub(r'<meta content="noindex,nofollow" name="robots"/?>', '', h)
    # header logo is above the fold: load it straight away
    h = re.sub(r'(<img alt="Instron Technologies official logo" decoding="async" height="379") loading="lazy"', r'\1 loading="eager"', h, count=1)
    src = hero(h) or 'assets/img/72c3314843.webp'
    img = share_image(root, key, src, ft) if ft else f'assets/og/{slug}.jpg'
    u, ie, te = url(key), SITE + img, html.escape(title)
    tags = (f'<link rel="canonical" href="{u}"/>'
            f'<meta property="og:type" content="{"article" if kind == "article" else "website"}"/>'
            f'<meta property="og:site_name" content="{NAME}"/><meta property="og:locale" content="en_CA"/>'
            f'<meta property="og:title" content="{te}"/><meta property="og:description" content="{e}"/>'
            f'<meta property="og:url" content="{u}"/><meta property="og:image" content="{ie}"/>'
            f'<meta property="og:image:width" content="1200"/><meta property="og:image:height" content="630"/>'
            f'<meta property="og:image:alt" content="{html.escape(label)}, {NAME}"/>'
            f'<meta name="twitter:card" content="summary_large_image"/><meta name="twitter:site" content="@InstronTech"/>'
            f'<meta name="twitter:title" content="{te}"/><meta name="twitter:description" content="{e}"/>'
            f'<meta name="twitter:image" content="{ie}"/><meta name="theme-color" content="#0a2d4a"/>'
            f'<link rel="apple-touch-icon" href="{LOGO}"/>'
            f'<script type="application/ld+json">{jsonld(key, h, img)}</script>')
    return h.replace('</head>', '<!--seo-->' + tags + '<!--/seo--></head>', 1)


def site_files(root):
    keys = list(P)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'  <url><loc>{url(k)}</loc></url>' for k in keys]
    sm.append('</urlset>')
    open(os.path.join(root, 'sitemap.xml'), 'w').write('\n'.join(sm) + '\n')
    open(os.path.join(root, 'robots.txt'), 'w').write(
        '# Instron Technologies: all search engines and AI assistants may read the public site.\n'
        'User-agent: *\nAllow: /\n\n'
        '# Named so a blanket rule added later cannot block them by accident\n'
        + ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in
                  ('Googlebot', 'Bingbot', 'ClaudeBot', 'GPTBot', 'OAI-SearchBot', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended'))
        + f'Sitemap: {SITE}sitemap.xml\n')
    L = [f'# {NAME}', '',
         '> Instron Technologies engineers and builds integrated process systems for technology developers and industrial',
         '> manufacturers, from pilot and demonstration plants to industrial skids, with the automation and plant data to run them.',
         '> Engineering since 2013. ' + CLARIFIER, '',
         '## Solutions',
         f'- [Process Skid Plants]({url("process")}): pilot and demonstration plants and modular industrial process skids. Our core solution.',
         f'- [Industrial Automation & Controls]({url("automation")}): E&I design, PLC, HMI and SCADA engineering, control panels and S88 batch control. Delivered with our skids or on its own.',
         f'- [PlantON™ by Instron Technologies]({url("planton")}): plant data platform for traceability, OEE, compliance reports and production views, without replacing existing controls.',
         f'- [How We Work]({url("how")}): Basic Engineering & Feasibility, Detailed Engineering, and Integrated Design & Build, each contracted separately.', '',
         '## Industries',
         *[f'- [{P[k][4]}]({url(k)})' for k in ('cleantech', 'research', 'chemical', 'food', 'pharma', 'manufacturing')], '',
         '## Applications',
         *[f'- [{P[k][4]}]({url(k)})' for k in ('scaleup', 'separation', 'modernization', 'batch', 'oee', 'utilities')], '',
         '## Proof',
         f'- [Project Portfolio]({url("portfolio")}) and [Case Studies]({url("cases")}). Client names are withheld; references on request.',
         f'- [Insights]({url("insights")}): engineering articles on scale-up, modernization and plant data.', '',
         '## Company and contact',
         '- Company offices: Toronto, Ontario, Canada (Instron Technologies Inc., 111 Peter Street, Suite 902, Toronto, ON M5V 2H1) and',
         '  Pune, Maharashtra, India (Instron Technologies LLP, Plot No. 88, Block F-II, Pimpri Industrial Area, MIDC, Bhosari, Pune 411018).',
         f'- Regional presence: Calgary, Saskatoon, Mumbai, Riyadh, Voorhout and Monterrey. See [Global Presence]({url("global")}).',
         f'- Email: {EMAIL}. [Discuss your project]({url("contact")}).',
         f'- [Our Company]({url("company")}), [Leadership]({url("leadership")}), [Careers]({url("careers")}).', '']
    open(os.path.join(root, 'llms.txt'), 'w').write('\n'.join(L))


def run(root):
    ft = fonts(root)
    for key, v in P.items():
        f = os.path.join(root, v[0] + '.html')
        h = open(f, encoding='utf-8').read()
        open(f, 'w', encoding='utf-8').write(apply(h, key, root, ft))
    site_files(root)
    print(f'seo: {len(P)} pages, share images in assets/og, robots.txt, sitemap.xml, llms.txt (GO_LIVE={GO_LIVE})')


if __name__ == '__main__':
    run(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.'))
