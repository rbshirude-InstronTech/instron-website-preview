"""Translated pages for the preview site: one engine, one settings block per language.

Usage:
  python3 -I tools/i18n.py build [root]              build every language that has a catalogue, add the language
                                                     links and hreflang to the English pages
  python3 -I tools/i18n.py extract <locale> [root]   refresh i18n/<locale>.json from the built English pages
  python3 -I tools/i18n.py report <locale> [root]    list English text on that language's pages with no translation yet
  python3 -I tools/i18n.py csv <locale> [root]       write i18n/<locale>-review.csv for a native reviewer

tools/build.py runs "build" after every sync. Rules for translators: Project doc claude/translation-guidelines.md.

Catalogue: i18n/<locale>.json  {"segments": {english: translation}}.
  Keys are the English text with inline markup simplified: tags that carry attributes become <a1>, <span2> ...
  (numbered in order inside the segment), and the PlantON(TM) wordmark becomes {PlantON}. The translation must use
  the same numbered tags and {PlantON}. An empty line means "not translated yet" (English is shown).
"""
import sys, os, re, json, html as H
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

# Core pages, translated in every language. Each language can list more in i18n/pages.json as its packs are imported.
PAGES = ['index', 'process-skid-plants', 'industrial-automation', 'planton-digital-factory', 'how-we-work',
         'global-presence', 'contact', 'privacy-terms-accessibility']
SITE = 'https://instrontechnologies.com/'
PHRASING = {'a', 'b', 'strong', 'em', 'i', 'br', 'sup', 'sub', 'code', 'abbr', 'small', 'span', 'u', 'time', 'mark', 'q', 'wbr', 'cite'}
CONTAINER = {'div', 'nav', 'section', 'article', 'ul', 'ol', 'header', 'footer', 'main', 'figure', 'aside', 'form', 'fieldset', 'table', 'thead', 'tbody', 'tr', 'dl', 'details'}
SKIP = {'script', 'style', 'svg', 'template'}
ATTRS = ('alt', 'title', 'aria-label', 'placeholder')
META = {('name', 'description'), ('property', 'og:title'), ('property', 'og:description'), ('property', 'og:image:alt'),
        ('name', 'twitter:title'), ('name', 'twitter:description')}
LD_KEYS = {'name', 'description', 'disambiguatingDescription', 'headline'}
LETTER = re.compile(r'[A-Za-z]')

# One block per language, in the order the language links appear.
LOCALES = {
    'fr-CA': {
        'dir': 'fr', 'og': 'fr_CA', 'name': 'Français', 'label_en': 'French',
        'aria_page': 'Version française de cette page', 'aria_site': 'Site en français',
        'js': [
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
        ],
    },
    'es-MX': {
        'dir': 'es', 'og': 'es_MX', 'name': 'Español', 'label_en': 'Spanish',
        'aria_page': 'Versión en español de esta página', 'aria_site': 'Sitio en español',
        'js': [
            ("'Open navigation'", "'Abrir la navegación'"),
            ("'Close navigation'", "'Cerrar la navegación'"),
            ("count+' page'+(count===1?'':'s')+' found.'", "count+(count===1?' página encontrada.':' páginas encontradas.')"),
            ("'No pages match. Try a solution, industry or application name.'",
             "'Ninguna página coincide. Pruebe con el nombre de una solución, una industria o una aplicación.'"),
            ("'Instron Technologies - Technical Enquiry'", "'Instron Technologies - Consulta técnica'"),
            ("'Name: '", "'Nombre: '"), ("'Work email: '", "'Correo electrónico de trabajo: '"),
            ("'Organization: '", "'Organización: '"), ("'Country: '", "'País: '"),
            ("'Area of interest: '", "'Área de interés: '"), ("'Not specified'", "'No especificado'"),
            ("'Project stage: '", "'Etapa del proyecto: '"), ("'Phone: '", "'Teléfono: '"),
            ("'Project description:'", "'Descripción del proyecto:'"),
            ("'Instron technical enquiry'", "'Consulta técnica a Instron'"),
            ("'Your email application is being opened. No message has been sent by this website.'",
             "'Se está abriendo su aplicación de correo. Este sitio no ha enviado ningún mensaje.'"),
            ("'Enquiry text copied locally. No message has been sent.'",
             "'Texto de la consulta copiado en su dispositivo. No se ha enviado ningún mensaje.'"),
            ("'Enquiry text to copy'", "'Texto de la consulta para copiar'"),
            ("'Select and copy the enquiry text below. No message has been sent.'",
             "'Seleccione y copie el texto de la consulta a continuación. No se ha enviado ningún mensaje.'"),
        ],
    },
}

CSS = """/* language switcher (tools/i18n.py) */
.lv-tb-right{display:flex;align-items:center;gap:14px}
.lv-lang{color:inherit;text-decoration:none;font-weight:600;border:1px solid currentColor;border-radius:999px;padding:1px 10px;font-size:.85em;line-height:1.6;white-space:nowrap}
.lv-lang:hover,.lv-lang:focus-visible{background:rgba(255,255,255,.16)}
.lv-lang+.lv-lang{margin-left:-6px}
/* phones: short codes (EN, FR, ES); the full name stays in aria-label */
@media(max-width:600px){.lv-lang[data-short]{font-size:0;padding:1px 8px}.lv-lang[data-short]::after{content:attr(data-short);font-size:12px}.lv-tb-right{gap:10px}.lv-lang+.lv-lang{margin-left:-4px}}
/* translated copy runs longer: keep the Home key figures on one line */
html[lang="fr-CA"] .v241-figs strong,html[lang="es-MX"] .v241-figs strong{white-space:nowrap;font-size:clamp(26px,2.5vw,36px)}
"""


def pages_for(root, loc):
    """Pages translated in this language: i18n/pages.json {locale: [pages]} if present, else the core PAGES."""
    p = os.path.join(root, 'i18n', 'pages.json')
    extra = json.load(open(p, encoding='utf-8')).get(loc, []) if os.path.exists(p) else []
    return PAGES + [x for x in extra if x not in PAGES]


def active_locales(root):
    return [l for l in LOCALES if os.path.exists(cat_path(root, l))]


def page_url(page, d=''):
    base = SITE + (d + '/' if d else '')
    return base if page == 'index' else f'{base}{page}.html'


def alternates(root, page):
    alts = [('en', page_url(page))] + [(l, page_url(page, LOCALES[l]['dir'])) for l in active_locales(root) if page in pages_for(root, l)]
    return alts + [('x-default', page_url(page))]


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


def cat_path(root, loc):
    return os.path.join(root, 'i18n', f'{loc}.json')


def load(root, loc):
    p = cat_path(root, loc)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {'segments': {}}


def extract(root, loc):
    cat = load(root, loc); seg = cat['segments']
    order, where = [], {}
    for p in pages_for(root, loc):
        for k in page_keys(os.path.join(root, p + '.html')):
            if k not in where:
                where[k] = []; order.append(k)
            if p not in where[k]:
                where[k].append(p)
    new = {k: seg.get(k, '') for k in order}
    # keep translations for pages not switched on yet (imported packs), as long as the English line is still on the site
    on_site = set()
    for f in os.listdir(root):
        if f.endswith('.html') and f[:-5] not in pages_for(root, loc):
            on_site.update(page_keys(os.path.join(root, f)))
    for k, v in seg.items():
        if v and k not in new and k in on_site:
            new[k] = v
    stale = {k: v for k, v in seg.items() if k not in new and v}
    cat['segments'] = new
    if stale:
        cat['retired'] = {**cat.get('retired', {}), **stale}
    cat['pages'] = {k: where[k] for k in order}
    os.makedirs(os.path.join(root, 'i18n'), exist_ok=True)
    json.dump(cat, open(cat_path(root, loc), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    done = sum(1 for v in new.values() if v)
    print(f'i18n extract {loc}: {len(new)} segments, {done} translated, {len(stale)} retired')


def loc_href(v, pages=PAGES):
    """Rewrite a link or asset path for a page that lives one folder down (fr/, es/); `pages` are the ones translated there."""
    if not v or v.startswith(('#', 'mailto:', 'tel:', 'http:', 'https:', '//', 'data:', 'javascript:')):
        return v
    m = re.match(r'([^#?]*)(.*)', v); path, rest = m.group(1), m.group(2)
    if path.endswith('.html') and path[:-5] in pages and '/' not in path:
        return v
    return '../' + v


def translate_page(root, loc, page, seg, missing):
    L = LOCALES[loc]; P = pages_for(root, loc)
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

    loc_url = page_url(page, L['dir'])

    def ld(obj):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if k in LD_KEYS and isinstance(v, str):
                    fr = T(H.escape(norm(v), quote=False))
                    if fr and not (obj.get('@type') == 'Organization' and k == 'name'):
                        obj[k] = H.unescape(fr)
                elif isinstance(v, str) and k in ('url', '@id', 'item'):
                    for p in P:
                        u = page_url(p)
                        f = page_url(p, L['dir'])
                        if obj.get('@type') == 'Organization' or v.startswith(SITE + '#'):
                            break
                        if v == u or v.startswith(u + '#'):
                            obj[k] = f + v[len(u):]; break
                else:
                    ld(v)
            if obj.get('inLanguage') == 'en':
                obj['inLanguage'] = loc
        elif isinstance(obj, list):
            for v in obj:
                ld(v)
    for s in d.find_all('script', type='application/ld+json'):
        j = json.loads(s.string); ld(j)
        s.string = json.dumps(j, ensure_ascii=False, separators=(',', ':'))

    d.html['lang'] = loc
    for l in d.find_all('link', rel='canonical'):
        l['href'] = loc_url
    for m in d.find_all('meta', property='og:url'):
        m['content'] = loc_url
    for m in d.find_all('meta', property='og:locale'):
        m['content'] = L['og']
        alt = d.new_tag('meta', property='og:locale:alternate', content='en_CA'); m.insert_after(alt)

    # IRA guide is English-only for now: not loaded on translated pages
    for s in d.find_all('script', src=re.compile(r'assets/ira/')):
        s.decompose()
    for l in d.find_all('link', href=re.compile(r'assets/ira/')):
        l.decompose()
    # translated build of the site script
    for s in d.find_all('script', src=re.compile(r'assets/js/site-[0-9a-f]{10}\.js')):
        s['src'] = re.sub(r'site-[0-9a-f]{10}\.js', f"site-{L['dir']}.js", s['src'])

    for t in d.find_all(True):
        for a in ('href', 'src'):
            if t.has_attr(a):
                t[a] = loc_href(t[a], P)
        if t.has_attr('srcset'):
            t['srcset'] = ', '.join(' '.join([loc_href(p.split()[0], P)] + p.split()[1:]) for p in t['srcset'].split(','))
        if t.has_attr('style') and 'url(' in t['style']:
            t['style'] = re.sub(r'url\((["\']?)(assets/)', r'url(\1../\2', t['style'])
    add_lang_bits(d, root, page, loc)
    return '<!DOCTYPE html>\n' + str(d).replace('<!DOCTYPE html>', '', 1).lstrip()


def lang_links(root, page, here):
    """(href, hreflang, label, aria) for the topbar of a page in language `here` ('en' or a locale)."""
    out = []
    up = '' if here == 'en' else '../'
    if here != 'en':
        out.append((f'{up}{page}.html', 'en', 'English', 'English version of this page'))
    for l in active_locales(root):
        if l == here:
            continue
        L = LOCALES[l]
        has = page in pages_for(root, l)
        target = page if has else 'index'
        aria = L['aria_page'] if has else L['aria_site']
        out.append((f"{up}{L['dir']}/{target}.html", l, L['name'], aria))
    return out


def add_lang_bits(d, root, page, here):
    """hreflang alternates, the i18n stylesheet and the topbar language links on a translated page (idempotent)."""
    for l in d.find_all('link', rel='alternate', hreflang=True):
        l.decompose()
    for a in d.select('a.lv-lang'):
        a.decompose()
    for l in d.find_all('link', id='instron-i18n'):
        l.decompose()
    anchor = d.find('link', rel='canonical') or d.head.find('title')
    for hl, u in alternates(root, page):
        l = d.new_tag('link', rel='alternate', hreflang=hl, href=u)
        anchor.insert_after(l); anchor = l
    d.head.append(d.new_tag('link', rel='stylesheet', href='../assets/css/i18n.css', id='instron-i18n'))
    right = d.select_one('.lv-tb-right')
    if right:
        for n, (href, hl, label, aria) in enumerate(lang_links(root, page, here)):
            a = d.new_tag('a', href=href, hreflang=hl, lang=hl); a.string = label
            a['aria-label'] = aria; a['class'] = 'lv-lang'; a['data-short'] = hl[:2].upper()
            right.insert(n, a)


def lang_bits_text(h, root, page):
    """Same for an English page, by plain text edits so the rest of the file is untouched."""
    h = re.sub(r'<link href="[^"]*" hreflang="[^"]*" rel="alternate"/>', '', h)
    h = re.sub(r'<a aria-label="[^"]*" class="lv-lang"[^>]*>[^<]*</a>', '', h)
    h = h.replace('<link href="assets/css/i18n.css" id="instron-i18n" rel="stylesheet"/>', '')
    if any(page in pages_for(root, l) for l in active_locales(root)):
        alt = ''.join(f'<link href="{u}" hreflang="{hl}" rel="alternate"/>' for hl, u in alternates(root, page))
        h, n = re.subn(r'(<link rel="canonical" href="[^"]*"/>)', lambda m: m.group(1) + alt, h, count=1)
        assert n == 1, page
    h = h.replace('</head>', '<link href="assets/css/i18n.css" id="instron-i18n" rel="stylesheet"/></head>', 1)
    a = ''.join(f'<a aria-label="{aria}" class="lv-lang" data-short="{hl[:2].upper()}" href="{href}" hreflang="{hl}" lang="{hl}">{label}</a>'
                for href, hl, label, aria in lang_links(root, page, 'en'))
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
        out = lang_bits_text(src, root, f[:-5])
        if out != src:
            open(p, 'w', encoding='utf-8').write(out); n += 1
    return n


def build(root, only=None):
    js = [f for f in os.listdir(os.path.join(root, 'assets', 'js')) if re.fullmatch(r'site-[0-9a-f]{10}\.js', f)]
    assert len(js) == 1, js
    site_js = open(os.path.join(root, 'assets', 'js', js[0]), encoding='utf-8').read()
    open(os.path.join(root, 'assets', 'css', 'i18n.css'), 'w', encoding='utf-8').write(CSS)
    missing = {}
    for loc in active_locales(root):
        L = LOCALES[loc]
        seg = load(root, loc)['segments']
        os.makedirs(os.path.join(root, L['dir']), exist_ok=True)
        s = site_js
        for a, b in L['js']:
            assert a in s, a
            s = s.replace(a, b)
        open(os.path.join(root, 'assets', 'js', f"site-{L['dir']}.js"), 'w', encoding='utf-8').write(s)
        missing[loc] = []
        for p in pages_for(root, loc):
            out = translate_page(root, loc, p, seg, missing[loc])
            open(os.path.join(root, L['dir'], p + '.html'), 'w', encoding='utf-8').write(out)
    n = patch_english(root)
    print('i18n build: ' + '; '.join(f"{loc} {len(pages_for(root, loc))} pages in {LOCALES[loc]['dir']}/, {len(missing[loc])} untranslated"
                                     for loc in missing) + f'; {n} English pages updated')
    return missing


if __name__ == '__main__':
    args = sys.argv[1:] or ['build']
    cmd = args[0]
    if cmd == 'build':
        build(os.path.abspath(args[1] if len(args) > 1 else '.'))
    else:
        loc = args[1]; assert loc in LOCALES, f'unknown locale {loc}'
        root = os.path.abspath(args[2] if len(args) > 2 else '.')
        if cmd == 'extract':
            extract(root, loc)
        elif cmd == 'csv':
            import csv
            cat = load(root, loc)
            with open(os.path.join(root, 'i18n', f'{loc}-review.csv'), 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f); w.writerow(['First page', 'Also on', 'English', f"{LOCALES[loc]['label_en']} ({loc})"])
                for k, v in cat['segments'].items():
                    pg = cat.get('pages', {}).get(k, [''])
                    w.writerow([pg[0], ' '.join(pg[1:]), H.unescape(k), H.unescape(v)])
            print(f'i18n/{loc}-review.csv written')
        elif cmd == 'report':
            for p, k in build(root)[loc]:
                print(f'{p}: {k}')
