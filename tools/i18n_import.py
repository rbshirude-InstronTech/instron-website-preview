"""Check and load translation-pack files returned by an outside translator (e.g. ChatGPT).

  python3 -I tools/i18n_import.py <locale> <file.md> [<file.md> ...] [--dry-run] [--root=.]

For each [ID] block, the returned line is checked against the English:
  rejected  codes (<a1>, {PlantON} ...) not identical, a number changed or missing, a protected name dropped,
            a long dash, a banned term from the glossary (e.g. "panel de control", "utilidades", "manutention",
            "API" for the pharma ingredient), missing ¿ / ¡ in Spanish, empty line
  warning   line identical to the English (fine for names; check the rest), much shorter or longer than the English
Accepted lines go into i18n/<locale>.json. A page is switched on in that language (i18n/pages.json) once every line
on it is translated, then the site is rebuilt. Rejected lines stay in English and are listed in
i18n/packs/<pack>/<pack>-<locale>-import-report.md, to send back to the translator or fix by hand.
Rules: Project doc claude/translation-guidelines.md.
"""
import sys, os, re, json, html as H, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('i18n', os.path.join(HERE, 'i18n.py'))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

TOK = re.compile(r'</?[a-z]+\d*>|\{PlantON\}')
PROTECT = ['Instron Technologies', 'PlantON', 'Rockwell', 'Allen-Bradley', 'Siemens', 'Schneider', 'Mitsubishi', 'Honeywell',
           'Omron', 'ControlLogix', 'CompactLogix', 'Studio 5000', 'FactoryTalk', 'PlantPAx', 'TIA Portal', 'WinCC', 'Experion',
           'AVEVA', '21 CFR Part 11', 'GAMP 5', 'ISA-88', 'S88', 'UL 508A', 'CSA', 'NEMA 4X', 'IEC 61131-3', 'AACE', 'TRL',
           'HAZOP', 'HAZID', 'OPC UA', 'MQTT', 'PLC', 'HMI', 'SCADA', 'DCS', 'MES', 'ERP', 'IIoT', 'OEM', 'EPC', 'FAT', 'SAT',
           'PFD', 'P&amp;ID', 'URS', 'FDS', 'VFD', 'Ontario Made', 'sales@instrontechnologies.com', 'privacy@instrontechnologies.com']
BANNED = {
    'fr-CA': [(r'\bAPI\b', 'pharma API is IPA in French'), (r'\bmanutention\b', 'use manipulation (gas) / transfert (fluids)'),
              (r'\bcommissionnement\b', 'use mise en service'), (r'\be-?mail\b', 'use courriel'), (r'\bpanneaux? de contrôle\b', 'use panneau de commande'),
              (r'(^|[\s(])[Pp]ilote (de|d’|automatisé)', 'say usine pilote / unité pilote'), (r'\bTRS\b', 'use TRG (OEE)')],
    'es-MX': [(r'\bAPI\b', 'pharma API is IFA'), (r'\bpanel(es)? de control\b', 'use tablero de control'), (r'\butilidades\b', 'use servicios auxiliares'),
              (r'\bcomisionamiento\b', 'use puesta en marcha'), (r'\be-?mail\b', 'use correo electrónico'), (r'\binterbloqueo', 'use enclavamiento'),
              (r'(^|[\s(])[Pp]iloto (de|automatizado)', 'say planta piloto / unidad piloto'), (r'\bordenador', 'Spain Spanish: use computadora')],
}
TAG = {'fr-CA': 'FR', 'es-MX': 'ES'}


def plain(s):
    return H.unescape(re.sub(r'<[^>]+>', ' ', s)).replace(' ', ' ')


def nums(s):
    s = plain(s)
    s = re.sub(r'(\d)[ , ](\d{3})\b', r'\1\2', s)
    s = re.sub(r'(\d),(\d{1,2})\b', r'\1.\2', s)
    return sorted(re.findall(r'\d+(?:\.\d+)?', s))


def to_key_form(t):
    """Translator text back to catalogue form: & as &amp;, the display marks ‹ › back to &lt; &gt;."""
    t = re.sub(r'&(?!amp;|lt;|gt;|nbsp;|#\d+;)', '&amp;', t.strip())
    return t.replace('‹', '&lt;').replace('›', '&gt;')


def parse(text, tag):
    text = re.sub(r'^```[a-z]*\s*$', '', text, flags=re.M)
    out = {}
    for m in re.finditer(r'^\s*\**\[([A-Z]+\d*-\d{4})\]\**[^\n]*\n(.*?)(?=^\s*\**\[[A-Z]+\d*-\d{4}\]|\Z)', text, re.S | re.M):
        i, block = m.group(1), m.group(2)
        t = re.search(rf'^\s*\**\s*{tag}\s*\**\s*:\s*\**\s*(.*?)\s*$', block, re.M)
        out[i] = t.group(1).strip().strip('*').strip() if t else ''
    return out


def check(loc, en, tr):
    errs, warns = [], []
    if not tr:
        return ['empty'], []
    if sorted(TOK.findall(en)) != sorted(TOK.findall(tr)):
        errs.append(f'codes differ: EN {TOK.findall(en)} vs {TOK.findall(tr)}')
    if nums(en) != nums(tr):
        errs.append(f'numbers differ: EN {nums(en)} vs {nums(tr)}')
    for p in PROTECT:
        if re.search(rf'(?<![\w-]){re.escape(p)}(?![\w-])', en) and p not in tr:
            if not (p == 'API' or (p == 'PlantON' and '{PlantON}' in tr)):
                errs.append(f'name dropped: {H.unescape(p)}')
    if re.search(r'[—–]', tr):
        errs.append('long dash')
    for pat, why in BANNED.get(loc, []):
        if re.search(pat, plain(tr)):
            errs.append(f'glossary: {why}')
    if loc == 'es-MX':
        f = plain(tr)
        if '?' in f and '¿' not in f: errs.append('missing ¿')
        if '!' in f and '¡' not in f: errs.append('missing ¡')
    pe, pt = plain(en).strip(), plain(tr).strip()
    if pe == pt and re.search(r'[a-z]{4}', pe):
        warns.append('identical to English (fine for a name; check otherwise)')
    elif len(pe) > 30 and not (0.7 <= len(pt) / max(len(pe), 1) <= 1.7):
        warns.append(f'length {len(pt)} vs English {len(pe)}')
    return errs, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    root = os.path.abspath(next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--root=')), '.'))
    loc, files = args[0], args[1:]
    assert loc in TAG, loc
    got = {}
    for f in files:
        got.update(parse(open(f, encoding='utf-8').read(), TAG[loc]))
    if not got:
        sys.exit('no [ID] blocks found')
    pack = got and next(iter(got)).split('-')[0].lower()
    meta = json.load(open(os.path.join(root, 'i18n', 'packs', pack, f'{pack}-ids.json'), encoding='utf-8'))
    ids = meta['ids']
    cat = E.load(root, loc); seg = cat['segments']; where = cat.setdefault('pages', {})
    ok, rej, warn = [], [], []
    for i, tr in got.items():
        if i not in ids:
            rej.append((i, '', tr, ['unknown ID'])); continue
        en = ids[i]['key']; t = to_key_form(tr)
        errs, warns = check(loc, en, t)
        if errs:
            rej.append((i, en, tr, errs)); continue
        ok.append((i, en, t))
        if warns:
            warn.append((i, en, tr, warns))
    if not dry:
        for i, en, t in ok:
            seg[en] = t
            where.setdefault(en, [])
            if ids[i]['page'] not in where[en]:
                where[en].append(ids[i]['page'])
        json.dump(cat, open(E.cat_path(root, loc), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # pages complete in this language
    complete, incomplete = [], {}
    for p in meta['pages']:
        missing = [k for k in E.page_keys(os.path.join(root, p + '.html')) if not seg.get(k)]
        (complete.append(p) if not missing else incomplete.__setitem__(p, len(missing)))
    if not dry:
        pj = os.path.join(root, 'i18n', 'pages.json')
        pages = json.load(open(pj, encoding='utf-8')) if os.path.exists(pj) else {}
        cur = pages.setdefault(loc, [])
        for p in complete:
            if p not in cur and p not in E.PAGES:
                cur.append(p)
        json.dump(pages, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # report
    rep = [f'# Import report: pack {pack}, {loc}', '',
           f'Lines returned: {len(got)} · accepted: {len(ok)} · rejected: {len(rej)} · warnings: {len(warn)}' + ('  (dry run: nothing saved)' if dry else ''), '',
           f'Pages now complete in {loc}: {", ".join(complete) or "none"}',
           f'Pages still waiting: {", ".join(f"{p} ({n} lines)" for p, n in incomplete.items()) or "none"}', '']
    if rej:
        rep += ['## Rejected (stay in English until fixed)', '', 'Send these back to the translator with the reason, or fix by hand.', '']
        for i, en, tr, errs in rej:
            rep += [f'[{i}]', f'EN: {en.replace("&amp;", "&")}', f'{TAG[loc]}: {tr}', f'Reason: {"; ".join(errs)}', '']
    if warn:
        rep += ['## Accepted with a warning (read these)', '']
        for i, en, tr, w in warn:
            rep += [f'[{i}] {"; ".join(w)}', f'EN: {en.replace("&amp;", "&")}', f'{TAG[loc]}: {tr}', '']
    rp = os.path.join(root, 'i18n', 'packs', pack, f'{pack}-{loc}-import-report.md')
    open(rp, 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    print('\n'.join(rep[:7])); print('report:', rp)
    if not dry and complete:
        E.build(root)


if __name__ == '__main__':
    main()
