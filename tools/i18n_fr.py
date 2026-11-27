"""French (Canada) pages for the preview site.

Usage:
  python3 -I tools/i18n_fr.py extract [root]   refresh i18n/fr-CA.json from the built English pages
  python3 -I tools/i18n_fr.py build [root]     write fr/*.html, assets/js/site-fr.js, assets/css/i18n.css,
                                               and add the language switcher and hreflang to the English pages
  python3 -I tools/i18n_fr.py report [root]    list English text on the French pages that has no translation yet
  python3 -I tools/i18n_fr.py csv [root]       write i18n/fr-CA-review.csv (page, English, French) for a reviewer

tools/build.py runs "build" at the end, so a sync keeps the French pages in step. English text that changes in
the review build shows up as untranslated (it falls back to English and is listed by "report") until the
catalogue gets a French line for it.

Catalogue: i18n/fr-CA.json  {"segments": {english: french}}.
  Keys are the English text with inline markup simplified: tags that carry attributes become <a1>, <span2> ...
  (numbered in order inside the segment), and the PlantON(TM) wordmark becomes {PlantON}. The French line must use
  the same numbered tags and {PlantON}. An empty French line means "not translated yet".
"""
import sys, os, re, json, html as H, copy, hashlib
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

PAGES = ['index', 'process-skid-plants', 'industrial-automation', 'planton-digital-factory', 'how-we-work',
         'global-presence', 'contact', 'privacy-terms-accessibility']
SITE = 'https://instrontechnologies.com/'
LANG = 'fr-CA'
PHRASING = {'a', 'b', 'strong', 'em', 'i', 'br', 'sup', 'sub', 'code', 'abbr', 'small', 'span', 'u', 'time', 'mark', 'q', 'wbr', 'cite'}
CONTAINER = {'div', 'nav', 'section', 'article', 'ul', 'ol', 'header', 'footer', 'main', 'figure', 'aside', 'form', 'fieldset', 'table', 'thead', 'tbody', 'tr', 'dl', 'details'}
SKIP = {'script', 'style', 'svg', 'template'}
ATTRS = ('alt', 'title', 'aria-label', 'placeholder')
META = {('name', 'description'), ('property', 'og:title'), ('property', 'og:description'), ('property', 'og:image:alt'),
        ('name', 'twitter:title'), ('name', 'twitter:description')}
LD_KEYS = {'name', 'description', 'disambiguatingDescription', 'headline'}
LETTER = re.compile(r'[A-Za-z]')

# strings inside the shared site script
JS = [
    ("'Open navigation'", "'Ouvrir la navigation'"),
    ("'Close navigation'", "'Fermer la navigation'"),
    ("count+' page'+(count===1?'':'s')+' found.'", "count+' page'+(count===1?' trouvée.':'s trouvées.')"),
    ("'No pages match. Try a solution, industry or application name.'",
     "'Aucune page ne correspond. Essayez le nom d’une solution, d’un secteur ou d’une application.'"),
    ("'Instron Technologies - Technical Enquiry'", "'Instron Technologies - Demande technique'"),
    ("'Name: '", "'Nom : '"), ("'Work email: '", "'Courriel professionnel : '"),
    ("'Organization: '", "'Organisation : '"), ("'Country: '", "'Pays : '"),
    ("'Area of interest: '", "'Domaine d’intérêt : '"), ("'Not specified'", "'Non précisé'"),
    ("'Project stage: '", "'Étape du projet : '"), ("'Phone: '", "'Téléphone : '"),
    ("'Project description:'", "'Description du projet :'"),
    ("'Instron technical enquiry'", "'Demande technique Instron'"),
    ("'Your email application is being opened. No message has been sent by this website.'",
     "'Votre logiciel de courriel s’ouvre. Aucun message n’a été envoyé par ce site.'"),
    ("'Enquiry text copied locally. No message has been sent.'",
     "'Texte de la demande copié sur votre appareil. Aucun message n’a été envoyé.'"),
    ("'Enquiry text to copy'", "'Texte de la demande à copier'"),
    ("'Select and copy the enquiry text below. No message has been sent.'",
     "'Sélectionnez et copiez le texte de la demande ci-dessous. Aucun message n’a été envoyé.'"),
]

CSS = """/* language switcher (tools/i18n_fr.py) */
.lv-tb-right{display:flex;align-items:center;gap:14px}
.lv-lang{color:inherit;text-decoration:none;font-weight:600;border:1px solid currentColor;border-radius:999px;padding:1px 10px;font-size:.85em;line-height:1.6;white-space:nowrap}
.lv-lang:hover,.lv-lang:focus-visible{background:rgba(255,255,255,.16)}
/* French copy runs longer: keep the Home key figures on one line */
html[lang="fr-CA"] .v241-figs strong{white-space:nowrap;font-size:clamp(26px,2.5vw,36px)}
"""


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def is_pon(t):
    return isinstance(t, Tag) and t.name == 'span' and 'pon' in (t.get('class') or [])


def phrasing_only(el):
    return all(d.name in PHRASING for d in el.find_all(True))


def open_tag(t):
    a = ''.join(f' {k}' if v == '' else f' {k}="{H.escape(" ".join(v) if isinstance(v, list) else v)}"' for k, v in t.attrs.items())
    return f'<{t.name}{a}>'


def key_of(el):
    """Simplified inner markup of a segment and the original tags/PlantON marks it stands for."""
    store, pons = [], []

    def ser(node):
        out = []
        for c in node.children:
            if isinstance(c, Comment):
                continue
            if isinstance(c, NavigableString):
                out.append(H.escape(str(c), quote=False))
            elif is_pon(c):
                pons.append(str(c)); out.append('{PlantON}')
            elif c.name in ('br', 'wbr'):
                out.append(f'<{c.name}>')
            elif c.attrs:
                store.append(c); n = len(store)
                out.append(f'<{c.name}{n}>' + ser(c) + f'</{c.name}{n}>')
            else:
                out.append(f'<{c.name}>' + ser(c) + f'</{c.name}>')
        return ''.join(out)
    return norm(ser(el)), store, pons


def expand(fr, store, pons):
    pon = pons[0] if pons else ''
    s = fr.replace('{PlantON}', pon)
    for n, t in enumerate(store, 1):
        s = re.sub(rf'<{t.name}{n}>', lambda m: open_tag(t), s)
        s = s.replace(f'</{t.name}{n}>', f'</{t.name}>')
    return s


def segments(root_el):
    """Yield ('el', tag) for phrasing-only elements with text, and ('txt', string) for loose text."""
    def walk(el):
        for c in list(el.children):
            if isinstance(c, Comment):
                continue
            if isinstance(c, Tag):
                if c.name in SKIP or 'lv-lang' in (c.get('class') or []):
                    continue
                if is_pon(c):
                    continue
                txt = c.get_text()
                if not LETTER.search(txt):
                    continue
                loose = any(isinstance(x, NavigableString) and not isinstance(x, Comment) and LETTER.search(str(x)) for x in c.children)
                if c.name in CONTAINER and not loose:
                    yield from walk(c)
                elif c.name not in ('br', 'wbr') and phrasing_only(c):
                    yield ('el', c)
                else:
                    yield from walk(c)
            elif isinstance(c, NavigableString) and LETTER.search(str(c)):
                yield ('txt', c)
    yield from walk(root_el)


def soup(path):
    d = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    for a in d.select('a.lv-lang'):      # our own language link: re-added after translation
        a.decompose()
    return d


def ld_strings(obj, out):
    if isinstance(obj, dict):
        if obj.get('@type') in ('PostalAddress',):
            return
        for k, v in obj.items():
            if k in LD_KEYS and isinstance(v, str) and LETTER.search(v) and not (obj.get('@type') == 'Organization' and k == 'name'):
                out.append(norm(v))
            else:
                ld_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            ld_strings(v, out)


def page_keys(path):
    d = soup(path)
    keys = []
    for kind, node in segments(d.body):
        keys.append(key_of(node)[0] if kind == 'el' else norm(H.escape(str(node), quote=False)))
    for t in d.find_all(True):
        if t.name in SKIP or 'lv-lang' in (t.get('class') or []):
            continue
        for a in ATTRS:
            if t.has_attr(a) and LETTER.search(t[a]):
                keys.append(norm(H.escape(t[a], quote=False)))
    for m in d.find_all('meta'):
        for attr, val in META:
            if m.get(attr) == val and m.get('content'):
                keys.append(norm(H.escape(m['content'], quote=False)))
    if d.title:
        keys.append(norm(H.escape(d.title.get_text(), quote=False)))
    for s in d.find_all('script', type='application/ld+json'):
        out = []; ld_strings(json.loads(s.string), out)
        keys += [H.escape(x, quote=False) for x in out]
    return keys


def cat_path(root):
    return os.path.join(root, 'i18n', 'fr-CA.json')


def load(root):
    p = cat_path(root)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'segments': {}}


def extract(root):
    cat = load(root); seg = cat['segments']
    order, where = [], {}
    for p in PAGES:
        for k in page_keys(os.path.join(root, p + '.html')):
            if k not in where:
                where[k] = []; order.append(k)
            if p not in where[k]:
                where[k].append(p)
    new = {k: seg.get(k, '') for k in order}
    stale = {k: v for k, v in seg.items() if k not in new and v}
    cat['segments'] = new
    if stale:
        cat['retired'] = {**cat.get('retired', {}), **stale}
    cat['pages'] = {k: where[k] for k in order}
    os.makedirs(os.path.dirname(cat_path(root)), exist_ok=True)
    json.dump(cat, open(cat_path(root), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    done = sum(1 for v in new.values() if v)
    print(f'i18n extract: {len(new)} segments, {done} translated, {len(stale)} retired')


def fr_href(v, here_fr):
    """Rewrite a link or asset path for a page that lives in fr/."""
    if not v or v.startswith(('#', 'mailto:', 'tel:', 'http:', 'https:', '//', 'data:', 'javascript:')):
        return v
    m = re.match(r'([^#?]*)(.*)', v); path, rest = m.group(1), m.group(2)
    if path.endswith('.html') and path[:-5] in PAGES and '/' not in path:
        return v if here_fr else 'fr/' + v
    return '../' + v if here_fr else v


def translate_page(root, page, seg, missing):
    d = soup(os.path.join(root, page + '.html'))
    T = lambda k: seg.get(k) or None

    for kind, node in list(segments(d.body)):
        if kind == 'el':
            k, store, pons = key_of(node)
            fr = T(k)
            if not fr:
                missing.append((page, k)); continue
            frag = BeautifulSoup(expand(fr, store, pons), 'html.parser')
            if node.name == 'option' and not node.has_attr('value'):
                node['value'] = node.get_text()
            node.clear()
            for c in list(frag.contents):
                node.append(c)
        else:
            raw = str(node); k = norm(H.escape(raw, quote=False)); fr = T(k)
            if not fr:
                missing.append((page, k)); continue
            lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
            node.replace_with(NavigableString(lead + H.unescape(fr) + trail))

    for t in d.find_all(True):
        if t.name in SKIP or 'lv-lang' in (t.get('class') or []):
            continue
        for a in ATTRS:
            if t.has_attr(a) and LETTER.search(t[a]):
                k = norm(H.escape(t[a], quote=False)); fr = T(k)
                if fr:
                    t[a] = H.unescape(fr)
                else:
                    missing.append((page, k))
    for m in d.find_all('meta'):
        for attr, val in META:
            if m.get(attr) == val and m.get('content'):
                k = norm(H.escape(m['content'], quote=False)); fr = T(k)
                if fr:
                    m['content'] = H.unescape(fr)
                else:
                    missing.append((page, k))
    if d.title:
        k = norm(H.escape(d.title.get_text(), quote=False)); fr = T(k)
        if fr:
            d.title.string = H.unescape(fr)

    en_url = SITE if page == 'index' else f'{SITE}{page}.html'
    fr_url = f'{SITE}fr/' if page == 'index' else f'{SITE}fr/{page}.html'

    def ld(obj):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if k in LD_KEYS and isinstance(v, str):
                    fr = T(H.escape(norm(v), quote=False))
                    if fr and not (obj.get('@type') == 'Organization' and k == 'name'):
                        obj[k] = H.unescape(fr)
                elif isinstance(v, str) and k in ('url', '@id', 'item'):
                    for p in PAGES:
                        u = SITE if p == 'index' else f'{SITE}{p}.html'
                        f = f'{SITE}fr/' if p == 'index' else f'{SITE}fr/{p}.html'
                        if obj.get('@type') == 'Organization' or v.startswith(SITE + '#'):
                            break
                        if v == u or v.startswith(u + '#'):
                            obj[k] = f + v[len(u):]; break
                else:
                    ld(v)
            if obj.get('inLanguage') == 'en':
                obj['inLanguage'] = LANG
        elif isinstance(obj, list):
            for v in obj:
                ld(v)
    for s in d.find_all('script', type='application/ld+json'):
        j = json.loads(s.string); ld(j)
        s.string = json.dumps(j, ensure_ascii=False, separators=(',', ':'))

    d.html['lang'] = LANG
    for l in d.find_all('link', rel='canonical'):
        l['href'] = fr_url
    for m in d.find_all('meta', property='og:url'):
        m['content'] = fr_url
    for m in d.find_all('meta', property='og:locale'):
        m['content'] = 'fr_CA'
        alt = d.new_tag('meta', property='og:locale:alternate', content='en_CA'); m.insert_after(alt)

    # IRA guide is English-only for now: not loaded on French pages
    for s in d.find_all('script', src=re.compile(r'assets/ira/')):
        s.decompose()
    for l in d.find_all('link', href=re.compile(r'assets/ira/')):
        l.decompose()
    # French build of the site script
    for s in d.find_all('script', src=re.compile(r'assets/js/site-[0-9a-f]{10}\.js')):
        s['src'] = re.sub(r'site-[0-9a-f]{10}\.js', 'site-fr.js', s['src'])

    for t in d.find_all(True):
        for a in ('href', 'src'):
            if t.has_attr(a):
                t[a] = fr_href(t[a], True)
        if t.has_attr('srcset'):
            t['srcset'] = ', '.join(' '.join([fr_href(p.split()[0], True)] + p.split()[1:]) for p in t['srcset'].split(','))
        if t.has_attr('style') and 'url(' in t['style']:
            t['style'] = re.sub(r'url\((["\']?)(assets/)', r'url(\1../\2', t['style'])
    add_lang_bits(d, page, here_fr=True)
    return '<!DOCTYPE html>\n' + str(d).replace('<!DOCTYPE html>', '', 1).lstrip()


def add_lang_bits(d, page, here_fr):
    """hreflang alternates, the i18n stylesheet and the topbar language link (idempotent)."""
    for l in d.find_all('link', rel='alternate', hreflang=True):
        l.decompose()
    for a in d.select('a.lv-lang'):
        a.decompose()
    for l in d.find_all('link', id='instron-i18n'):
        l.decompose()
    if page in PAGES:
        en_url = SITE if page == 'index' else f'{SITE}{page}.html'
        fr_url = f'{SITE}fr/' if page == 'index' else f'{SITE}fr/{page}.html'
        anchor = d.find('link', rel='canonical') or d.head.find('title')
        for hl, u in (('en', en_url), (LANG, fr_url), ('x-default', en_url)):
            l = d.new_tag('link', rel='alternate', hreflang=hl, href=u)
            anchor.insert_after(l); anchor = l
    css = d.new_tag('link', rel='stylesheet', href=('../' if here_fr else '') + 'assets/css/i18n.css', id='instron-i18n')
    d.head.append(css)
    right = d.select_one('.lv-tb-right')
    if right:
        if here_fr:
            a = d.new_tag('a', href=f'../{page}.html', hreflang='en', lang='en'); a.string = 'English'
            a['aria-label'] = 'English version of this page'
        else:
            target = page if page in PAGES else 'index'
            a = d.new_tag('a', href=f'fr/{target}.html', hreflang=LANG, lang=LANG); a.string = 'Français'
            a['aria-label'] = 'Version française de cette page' if page in PAGES else 'Site en français'
        a['class'] = 'lv-lang'
        right.insert(0, a)


def lang_bits_text(h, page):
    """Same as add_lang_bits for an English page, by plain text edits so the rest of the file is untouched."""
    h = re.sub(r'<link href="[^"]*" hreflang="[^"]*" rel="alternate"/>', '', h)
    h = re.sub(r'<a aria-label="[^"]*" class="lv-lang"[^>]*>[^<]*</a>', '', h)
    h = h.replace('<link href="assets/css/i18n.css" id="instron-i18n" rel="stylesheet"/>', '')
    if page in PAGES:
        en_url = SITE if page == 'index' else f'{SITE}{page}.html'
        fr_url = f'{SITE}fr/' if page == 'index' else f'{SITE}fr/{page}.html'
        alt = ''.join(f'<link href="{u}" hreflang="{hl}" rel="alternate"/>' for hl, u in (('en', en_url), (LANG, fr_url), ('x-default', en_url)))
        h, n = re.subn(r'(<link rel="canonical" href="[^"]*"/>)', lambda m: m.group(1) + alt, h, count=1)
        assert n == 1, page
    h = h.replace('</head>', '<link href="assets/css/i18n.css" id="instron-i18n" rel="stylesheet"/></head>', 1)
    target = page if page in PAGES else 'index'
    label = 'Version française de cette page' if page in PAGES else 'Site en français'
    a = f'<a aria-label="{label}" class="lv-lang" href="fr/{target}.html" hreflang="{LANG}" lang="{LANG}">Français</a>'
    h, n = re.subn(r'(<div class="lv-tb-right">)', lambda m: m.group(1) + a, h, count=1)
    assert n == 1, page
    return h


def patch_english(root):
    n = 0
    for f in sorted(os.listdir(root)):
        if not f.endswith('.html'):
            continue
        p = os.path.join(root, f); src = open(p, encoding='utf-8').read()
        if 'lv-tb-right' not in src:
            continue
        out = lang_bits_text(src, f[:-5])
        if out != src:
            open(p, 'w', encoding='utf-8').write(out); n += 1
    return n


def build(root):
    seg = load(root)['segments']
    os.makedirs(os.path.join(root, 'fr'), exist_ok=True)
    # site script, French strings
    js = [f for f in os.listdir(os.path.join(root, 'assets', 'js')) if re.fullmatch(r'site-[0-9a-f]{10}\.js', f)]
    assert len(js) == 1, js
    s = open(os.path.join(root, 'assets', 'js', js[0]), encoding='utf-8').read()
    for a, b in JS:
        assert a in s, a
        s = s.replace(a, b)
    open(os.path.join(root, 'assets', 'js', 'site-fr.js'), 'w', encoding='utf-8').write(s)
    open(os.path.join(root, 'assets', 'css', 'i18n.css'), 'w', encoding='utf-8').write(CSS)
    missing = []
    for p in PAGES:
        out = translate_page(root, p, seg, missing)
        open(os.path.join(root, 'fr', p + '.html'), 'w', encoding='utf-8').write(out)
    n = patch_english(root)
    print(f'i18n build: {len(PAGES)} French pages in fr/, {n} English pages given the language link; '
          f'{len(missing)} untranslated strings fall back to English')
    return missing


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'build'
    root = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else '.')
    if cmd == 'extract':
        extract(root)
    elif cmd == 'csv':      # review sheet for a French reviewer: page, English, French
        import csv
        cat = load(root)
        with open(os.path.join(root, 'i18n', 'fr-CA-review.csv'), 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f); w.writerow(['First page', 'Also on', 'English', 'French (fr-CA)'])
            for k, v in cat['segments'].items():
                pg = cat.get('pages', {}).get(k, [''])
                w.writerow([pg[0], ' '.join(pg[1:]), H.unescape(k), H.unescape(v)])
        print('i18n/fr-CA-review.csv written')
    elif cmd == 'report':
        miss = build(root)
        for p, k in miss:
            print(f'{p}: {k}')
    else:
        build(root)
