"""Build assets/ira/ira-content.json: the approved page list IRA may recommend.

Usage: python3 -I tools/ira_content.py <repo root>

Titles and summaries are read from the built pages (approved website copy), so they stay in step
with every sync. The tags below say which visitor needs each page answers; they are the part to
review. A page or case study that is not listed here can never be recommended.
Tag weights: 3 = the main page for this need, 2 = strongly relevant, 1 = related.
"""
import sys, os, re, json, html

root = os.path.abspath(sys.argv[1])

PAGES = [
    # (file, section id or '', type, tags, extra keywords)
    ('process-skid-plants.html', '', 'solution', {'skid': 3, 'pilot': 2, 'industrial_skid': 2, 'scaleup': 1, 'build': 1}, []),
    ('pilot-demonstration-plants.html', '', 'solution', {'pilot': 3, 'research': 2, 'scaleup': 2, 'skid': 1}, ['trial', 'test rig']),
    ('industrial-process-skids.html', '', 'solution', {'industrial_skid': 3, 'skid': 2, 'build': 1}, ['production duty']),
    ('industrial-automation.html', '', 'solution', {'automation': 3, 'panels': 3, 'modernize': 1, 'batch': 1, 'compliance': 1}, ['e&i design']),
    ('planton-digital-factory.html', '', 'solution', {'plantdata': 3, 'oee': 2, 'trace': 2, 'utility': 1, 'compliance': 1}, ['planton']),
    ('how-we-work.html', 'phase-1', 'phase', {'feasibility': 3, 'hazop': 1, 'price': 2}, ['class 4 estimate']),
    ('how-we-work.html', 'phase-2', 'phase', {'detailed': 3, 'hazop': 2}, []),
    ('how-we-work.html', 'phase-3', 'phase', {'build': 3, 'skid': 1}, []),
    ('technology-scale-up.html', '', 'application', {'scaleup': 3, 'pilot': 2, 'research': 1}, []),
    ('separation-solvent-recovery.html', '', 'application', {'separation': 3, 'chemical': 1}, []),
    ('brownfield-automation-modernization.html', '', 'application', {'modernize': 3, 'automation': 1}, []),
    ('batch-process-automation.html', '', 'application', {'batch': 3, 'cip': 1, 'automation': 1, 'compliance': 1}, []),
    ('production-visibility-oee.html', '', 'application', {'oee': 3, 'plantdata': 1, 'manufacturing': 1}, []),
    ('utility-energy-monitoring.html', '', 'application', {'utility': 3, 'plantdata': 1}, []),
    ('energy-transition-critical-minerals.html', '', 'industry', {'energy': 3, 'battery': 3, 'carbon': 3, 'hydrogen': 3, 'pilot': 1}, []),
    ('research-technology-development.html', '', 'industry', {'research': 3, 'pilot': 2}, []),
    ('chemicals-refining-consumer-products.html', '', 'industry', {'chemical': 3, 'separation': 1}, []),
    ('food-beverage-dairy.html', '', 'industry', {'food': 3, 'cip': 2, 'trace': 1}, []),
    ('pharma-life-sciences.html', '', 'industry', {'pharma': 3, 'compliance': 2, 'batch': 1}, []),
    ('industrial-manufacturing.html', '', 'industry', {'manufacturing': 3, 'oee': 1}, []),
    ('insights-lab-to-pilot-to-industrial.html', '', 'insight', {'scaleup': 2, 'pilot': 1}, []),
    ('insights-brownfield-modernization.html', '', 'insight', {'modernize': 2}, []),
    ('insights-plant-data-rollout.html', '', 'insight', {'plantdata': 2, 'oee': 1}, []),
    ('case-studies.html', '', 'proof', {'proof': 3}, []),
    ('project-portfolio.html', '', 'proof', {'proof': 2}, []),
    ('trust-responsibility.html', '', 'company', {'safety': 3, 'compliance': 1}, []),
    ('contact.html', '', 'contact', {'contact': 3, 'price': 1}, []),
    ('global-presence.html', '', 'company', {'location': 3}, []),
    ('our-company.html', '', 'company', {'company': 3}, []),
    ('leadership.html', '', 'company', {'company': 1}, []),
    ('careers.html', '', 'company', {'careers': 3}, []),
]

CASES = {
    'case-mexico': ({'separation': 3, 'skid': 1, 'chemical': 1}, ['methanol', 'distillation tower']),
    'case-steam': ({'skid': 1, 'automation': 1, 'chemical': 1}, ['steam quality', 'analyzer', 'oil recovery']),
    'case-extraction': ({'pharma': 2, 'separation': 2, 'batch': 1}, ['botanical', 'cstr']),
    'case-battery': ({'battery': 3, 'pilot': 2, 'research': 1}, ['ultrasonic']),
    'case-cryogenic': ({'carbon': 3, 'pilot': 2, 'separation': 1, 'research': 1}, ['cryogenic', 'flue gas']),
    'case-co2': ({'carbon': 3, 'hydrogen': 3, 'pilot': 2}, ['amine', 'membrane']),
    'case-api': ({'pharma': 3, 'skid': 2, 'automation': 1, 'separation': 1}, ['hazardous area']),
    'case-propulsion': ({'pilot': 3, 'research': 2}, ['propulsion fuel', 'space']),
    'case-adjuvant': ({'cip': 3, 'pharma': 2, 'automation': 2}, ['adjuvant']),
    'case-cleaning': ({'chemical': 2, 'automation': 2}, ['capacity expansion']),
    'case-personal-care': ({'batch': 3, 'chemical': 2, 'automation': 1}, ['greenfield']),
    'case-chocolate': ({'food': 3, 'automation': 2, 'modernize': 1}, ['chocolate', 'redundant scada']),
    'case-dairy': ({'food': 3, 'plantdata': 2, 'trace': 2, 'utility': 1}, ['pasteurizer', 'dairy']),
    'case-diecast': ({'manufacturing': 3, 'oee': 3, 'utility': 1}, ['die casting']),
    'case-paintshop': ({'manufacturing': 3, 'oee': 2, 'plantdata': 1}, ['paint shop', 'alloy wheel']),
}

def text(s):
    s = re.sub(r'</?span[^>]*>', '', s)   # the PlantON wordmark is split into spans
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s))).strip()

def read(f):
    return open(os.path.join(root, f), encoding='utf-8').read()

entries = []
for f, sec, kind, tags, kw in PAGES:
    h = read(f)
    title = text(re.search(r'<title>(.*?)</title>', h, re.S).group(1)).split(' | ')[0]
    desc = re.search(r'<meta content="([^"]*)" name="description"', h) or re.search(r'<meta name="description" content="([^"]*)"', h)
    summary = html.unescape(desc.group(1)) if desc else ''
    if sec:
        m = re.search(r'id="' + re.escape(sec) + r'"[^>]*>(.*?)</(?:article|section)>', h, re.S)
        assert m, (f, sec)
        hd = re.search(r'<h[23][^>]*>(.*?)</h[23]>', m.group(1), re.S)
        title = re.sub(r'^\d+\s*·\s*', '', text(hd.group(1))) if hd else title
        para = re.search(r'<p>(.*?)</p>', m.group(1), re.S)
        summary = text(para.group(1)) if para else summary
    entries.append({'id': f[:-5] + ('-' + sec if sec else ''), 'type': kind, 'title': title,
                    'url': f + ('#' + sec if sec else ''), 'summary': summary[:240], 'tags': tags, 'keywords': kw})

h = read('case-studies.html')
found = set()
for m in re.finditer(r'<article[^>]*id="(case-[a-z0-9-]+)"[^>]*>(.*?)</article>', h, re.S):
    cid, body = m.group(1), m.group(2)
    if cid not in CASES:
        continue
    found.add(cid)
    title = text(re.search(r'<h[23][^>]*>(.*?)</h[23]>', body, re.S).group(1))
    sit = re.search(r'Situation\s*</[^>]+>\s*<p[^>]*>(.*?)</p>', body, re.S)
    summary = text(sit.group(1)) if sit else ''
    if len(summary) > 220:
        summary = summary[:217].rsplit(' ', 1)[0] + '...'
    tags, kw = CASES[cid]
    entries.append({'id': cid, 'type': 'case', 'title': title, 'url': 'case-studies.html#' + cid,
                    'summary': summary, 'tags': tags, 'keywords': kw})
missing = set(CASES) - found
assert not missing, f'case studies not found on the page: {missing}'

out = {'version': 1, 'note': 'Generated by tools/ira_content.py from the built pages. Only entries listed here can be recommended.',
       'entries': entries}
os.makedirs(os.path.join(root, 'assets', 'ira'), exist_ok=True)
with open(os.path.join(root, 'assets', 'ira', 'ira-content.json'), 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(f'IRA content: {len(entries)} entries ({len(found)} case studies)')
