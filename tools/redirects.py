"""301 redirect map: every address on the live instrontechnologies.com (Yoast sitemaps, 24 Nov 2026) to its new home.

Writes deploy/htaccess-redirects.conf (Bluehost / Apache: paste at the top of .htaccess, above any WordPress block)
and deploy/redirects.csv (source,target for the WordPress "Redirection" plugin import), plus deploy/redirects-table.csv
(the full map with reasons, for review).

NEW_STYLE: 'html' if the static build goes live as-is (pages at /contact.html), 'slug' if the new site goes onto
WordPress with /contact/ addresses. Rules whose old and new address end up identical are skipped, so no loops.
Usage: python3 -I tools/redirects.py [html|slug]
"""
import os, sys, csv, re

HOST = 'https://instrontechnologies.com'
NEW_STYLE = sys.argv[1] if len(sys.argv) > 1 else 'html'

# (old path, new page slug, #section or '', kind, reason)
PAGES = [
 ('/case-studies/', 'case-studies', '', 'Page', 'Same content, new page'),
 ('/solutions/', 'solutions', '', 'Page', 'Same content, new page'),
 ('/process-skid-plant/', 'process-skid-plants', '', 'Page', 'Primary solution'),
 ('/industrial-automation-solutions/', 'industrial-automation', '', 'Page', 'Solution page'),
 ('/about-us/', 'our-company', '', 'Page', 'About Us is now Our Company'),
 ('/career/', 'careers', '', 'Page', 'Careers page'),
 ('/contact/', 'contact', '', 'Page', 'Contact page'),
 ('/privacy-policy/', 'privacy-terms-accessibility', '', 'Page', 'Privacy now shares a page with terms and accessibility'),
 ('/distillation-plant/', 'separation-solvent-recovery', '', 'Page', 'Distillation sits under Separation & Solvent Recovery'),
 ('/evaporation-plant/', 'separation-solvent-recovery', '', 'Page', 'Evaporation sits under Separation & Solvent Recovery'),
 ('/solvent-extraction-systems/', 'separation-solvent-recovery', '', 'Page', 'Extraction sits under Separation & Solvent Recovery'),
 ('/hazop-study/', 'how-we-work', 'phase-1', 'Page + post', 'HAZOP support is in Basic Engineering & Feasibility; "100% compliance" claim retired'),
 ('/basic-engineering/', 'how-we-work', 'phase-1', 'Page + post', 'Phase 01 of How We Work'),
 ('/detailed-engineering/', 'how-we-work', 'phase-2', 'Page + post', 'Phase 02 of How We Work'),
 ('/combustion-systems/', 'industrial-automation', '', 'Page (retired)', 'Combustion systems are not one of the three solutions'),
 ('/test-bench-automation/', 'industrial-automation', '', 'Page (retired)', 'Test benches were dropped as a solution'),
 ('/greenfield-projects/', 'industrial-automation', '', 'Page', 'Greenfield automation is covered on Industrial Automation'),
 ('/brownfield-projects-smart-retrofitting/', 'brownfield-automation-modernization', '', 'Page', 'Brownfield Automation Modernization'),
 ('/process-automation-solutions/', 'batch-process-automation', '', 'Page', 'Batch & Process Automation'),
 ('/21-cfr-part-11-compliant-automation/', 'pharma-life-sciences', '', 'Page', '21 CFR Part 11 is stated on the Pharma & Life Sciences page'),
 ('/energy-optimization-solutions/', 'utility-energy-monitoring', '', 'Page', 'Utility & Energy Monitoring'),
 ('/oee-monitoring-solutions/', 'production-visibility-oee', '', 'Page', 'Production Visibility & OEE'),
 ('/utility-monitoring/', 'utility-energy-monitoring', '', 'Page', 'Utility & Energy Monitoring'),
 ('/traceability/', 'planton-digital-factory', '', 'Page', 'Traceability is part of PlantON'),
 ('/predictive-maintenance/', 'planton-digital-factory', '', 'Page (retired)', 'Not claimed on the new site; nearest page is PlantON'),
 ('/form-digitization/', 'planton-digital-factory', '', 'Page (retired)', 'Not claimed on the new site; nearest page is PlantON'),
 ('/oee-trial/', 'production-visibility-oee', '', 'Trial page (check)', 'CHECK: PlantON trial landing page updated Sep 2026; if still used in campaigns, keep a trial offer on the new site'),
 ('/traceability-trial/', 'planton-digital-factory', '', 'Trial page (check)', 'CHECK: PlantON trial landing page, as above'),
 ('/utility-trial/', 'utility-energy-monitoring', '', 'Trial page (check)', 'CHECK: PlantON trial landing page, as above'),
]

# posts: live at /<slug>/ and formerly at /ca/<slug>/ (blog migration sheet, 20 Nov), so both are redirected
POSTS = [
 ('empowering-production-and-sustainability-with-digital-transformation', 'case-studies', 'case-diecast', 'Die-casting PlantON case (validated figures; old 30%/20%/25% claims retired)'),
 ('skid-plant-for-rd', 'case-studies', 'case-propulsion', 'Propulsion-fuel pilot case'),
 ('advanced-production-unit-for-therapeutic-radiopharmaceutical-ingredients', 'project-portfolio', '', 'Government research systems card (sanitized)'),
 ('hazop-study-optimizing-plant-safety', 'how-we-work', 'phase-1', 'HAZOP support in Basic Engineering & Feasibility'),
 ('enhancing-operational-agility-and-efficiency-through-industry-4-0-transformation', 'planton-digital-factory', '', 'Glass plant write-up; figures not validated'),
 ('multipurpose-distillation-unit-for-polymer-research-trials', 'project-portfolio', '', 'Multipurpose distillation unit card (Thailand)'),
 ('solvent-recovery-system', 'separation-solvent-recovery', '', 'Flash-still write-up; +13%/+4% not validated'),
 ('automation-solution-energy-consumption-reporting', 'case-studies', 'case-chocolate', 'Chocolate lines case'),
 ('dairy-facility-modernization-in-california', 'case-studies', 'case-dairy', 'Dairy modernization case (94% / 12% / 11%)'),
 ('project-management', 'how-we-work', 'phase-3', 'Integrated Design & Build; "30% faster" retired'),
 ('extraction-plant-for-pharma-api-production', 'case-studies', 'case-extraction', 'Same project: botanical-extract API plants, India and Australia'),
 ('traceability-in-manufacturing-industry', 'planton-digital-factory', '', 'Traceability is part of PlantON'),
 ('energy-saving-in-hydraulic-press', 'utility-energy-monitoring', '', 'Hydraulic press write-up; 30% not validated'),
 ('automated-crane-synchronization', 'industrial-automation', '', 'Retired: discrete machine automation'),
 ('biaxial-fatigue-testing-for-truck-wheel-durability', 'industrial-automation', '', 'Retired: test benches dropped'),
 ('cooling-test-station-for-end-of-line-testing-of-refrigerators-ac-and-de-freezers', 'industrial-automation', '', 'Retired: test benches dropped'),
 ('increasing-production-capacity-for-a-personal-care-manufacturer', 'case-studies', 'case-cleaning', 'Capacity expansion case (+20%)'),
 ('iot-for-steel-wheel-plants', 'production-visibility-oee', '', 'Steel-wheel OEE write-up'),
 ('revolutionizing-manufacturing-with-industry-4-0-a-guide-to-choosing-the-right-iot-system', 'insights-plant-data-rollout', '', 'Rewritten as the plant-data Insights article'),
 ('indias-transformative-journey-in-defence-manufacturing', 'insights', '', 'Retired: external article excerpt'),
 ('mastering-chemical-process-design', 'insights-lab-to-pilot-to-industrial', 'balance', 'Merged into the scale-up article'),
 ('empowering-die-casting-product', 'case-studies', 'case-diecast', 'Die-casting PlantON case'),
 ('revolutionizing-color', 'industrial-automation', '', 'Retired: vision-system work'),
 ('digital-maturity-assessment', 'planton-digital-factory', '', '10-25% savings claim retired'),
 ('cycle-time-improvement', 'production-visibility-oee', '', 'Wheel-maker write-up; 13%/6% not validated'),
 ('induction-motor-type-test-bench-for-precision-and-compliance', 'industrial-automation', '', 'Retired: test benches dropped'),
 ('hazop-study', 'how-we-work', 'phase-1', 'Also a page; see above'),
 ('advanced-combustion-systems', 'industrial-automation', '', 'Retired: not one of the three solutions'),
 ('detailed-engineering', 'how-we-work', 'phase-2', 'Also a page; see above'),
 ('basic-engineering', 'how-we-work', 'phase-1', 'Also a page; see above'),
]

# (regex on the path without the leading slash, new slug, section, kind, reason)
PATTERNS = [
 (r'^blogs(/page/[0-9]+)?/?$', 'insights', '', 'Archive', 'Blog list pages'),
 (r'^ca/blogs?(/page/[0-9]+)?/?$', 'insights', '', 'Archive (old /ca/)', 'Old blog list pages'),
 (r'^category/.*$', 'insights', '', 'Archive', 'Yoast category archives'),
 (r'^author/.*$', 'our-company', '', 'Archive', 'Yoast author archives'),
 (r'^ca/?$', 'index', '', 'Old /ca/ home', 'The site used to sit under /ca/'),
 (r'^(sitemap_index|page-sitemap|post-sitemap|category-sitemap|author-sitemap|elementor-hf-sitemap)\.xml$', 'sitemap.xml', '', 'Sitemap', 'Old Yoast sitemaps point to the new sitemap'),
]


def target(slug, section):
    if slug == 'sitemap.xml': path = '/sitemap.xml'
    elif slug == 'index': path = '/'
    else: path = f'/{slug}.html' if NEW_STYLE == 'html' else f'/{slug}/'
    return HOST + path + (f'#{section}' if section else '')


def rows():
    out, seen = [], set()
    for old, slug, sec, kind, why in PAGES:
        out.append((old, target(slug, sec), kind, why)); seen.add(old)
    for slug_old, slug, sec, why in POSTS:
        for old, kind in ((f'/{slug_old}/', 'Post'), (f'/ca/{slug_old}/', 'Post (old /ca/)')):
            if old not in seen:
                out.append((old, target(slug, sec), kind, why)); seen.add(old)
    for rx, slug, sec, kind, why in PATTERNS:
        out.append(('PATTERN ' + rx, target(slug, sec), kind, why))
    # no loops: drop rules whose new address equals the old one
    return [r for r in out if not (not r[0].startswith('PATTERN') and HOST + r[0] == r[1].split('#')[0])]


def main(root):
    R = rows()
    d = os.path.join(root, 'deploy'); os.makedirs(d, exist_ok=True)
    L = ['# Instron Technologies: 301 redirects from the old site (generated by tools/redirects.py, style=' + NEW_STYLE + ')',
         '# Paste at the TOP of .htaccess on Bluehost, above "# BEGIN WordPress" if that block exists.',
         '<IfModule mod_rewrite.c>', 'RewriteEngine On',
         '# one address only: https, no www',
         'RewriteCond %{HTTPS} off [OR]', 'RewriteCond %{HTTP_HOST} ^www\\. [NC]',
         'RewriteRule ^(.*)$ https://instrontechnologies.com/$1 [R=301,L,NE]', '']
    for old, new, kind, why in R:
        rx = old[8:] if old.startswith('PATTERN ') else '^' + re.escape(old.strip('/')).replace('\\-', '-') + '/?$'
        L.append(f'RewriteRule {rx} {new} [R=301,L,NE,NC]')
    L += ['</IfModule>', '']
    open(os.path.join(d, 'htaccess-redirects.conf'), 'w').write('\n'.join(L))
    with open(os.path.join(d, 'redirects.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['source', 'target', 'regex', 'code'])
        for old, new, kind, why in R:
            if old.startswith('PATTERN '): w.writerow(['/' + old[8:].lstrip('^'), new, 1, 301])
            else: w.writerow([old, new, 0, 301])
    with open(os.path.join(d, 'redirects-table.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['Old address', 'New address', 'Type', 'Why'])
        for old, new, kind, why in R:
            w.writerow([old if not old.startswith('PATTERN ') else 'Pattern: ' + old[8:], new, kind, why])
    print(f'redirects: {len(R)} rules ({NEW_STYLE} style) -> deploy/')
    return R


if __name__ == '__main__':
    main(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
