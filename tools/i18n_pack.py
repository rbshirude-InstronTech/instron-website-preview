"""Make translation packs (Markdown files for an outside translator, e.g. ChatGPT) for pages not yet translated.

  python3 -I tools/i18n_pack.py <pack> <page>[,<page>...] [<page>...] [--root .]
    Each argument after the pack name is one file group (comma-separated pages); a group over MAX_LINES is split.
    Writes i18n/packs/<pack>/<pack>-ids.json and, per language, <pack>-<locale>-<nn>.md.

Lines already translated in a language (header, footer, shared lines) are left out of that language's files.
Return the filled files and load them with tools/i18n_import.py.
"""
import sys, os, re, json, html as H, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('i18n', os.path.join(HERE, 'i18n.py'))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
MAX_LINES = 180

COMMON_RULES = """1. Translate every `{T}:` line. Do not change the `[ID]` lines or the `EN:` lines. Keep one line per entry: no line breaks inside a translation.
2. **Codes stay exactly as written**, in the same order: tags like `<a1>`, `</a1>`, `<span2>`, `<strong>`, `<em>`, `<b>`, `<small>`, `<br>`, `<wbr>`, `<i1></i1>`, and the mark `{PlantON}`. Translate the words between the tags, never the tags. Empty tag pairs such as `<span1></span1>` stay where they are.
3. **Facts never change.** Every number, unit, range, percentage, year, count and standard stays the same. Only the number format follows the language (see conventions).
4. **Keep these names exactly as written:** Instron Technologies, PlantON™, Rockwell (Allen-Bradley), Siemens, Schneider, Mitsubishi, Honeywell, Omron, ControlLogix, CompactLogix, Studio 5000, FactoryTalk, PlantPAx, TIA Portal, WinCC, Experion, AVEVA, Modicon, 21 CFR Part 11, GAMP 5, ISA-88, S88, UL 508A, CSA, CE, NEMA 4X, IEC 61131-3, AACE, TRL, HAZOP, HAZID, OPC UA, MQTT, EtherNet/IP, Modbus, PROFIBUS, PLC, HMI, SCADA, DCS, MES, ERP, KPI, IIoT, OEM, EPC, FAT, SAT, PFD, P&ID, IQ, OQ, URS, FDS, VFD, Ontario Made, BusinessDMX, Mafave, Chemponics, city names in their usual form, email addresses.
5. No long dashes (— or –). Use a comma, colon or full stop instead.
6. Do not add, remove or soften claims. Do not add client names. Do not write anything about AI.
7. Tone: professional, plain and direct, written for engineers and plant managers. Keep sentences about as long as the English.
8. Headings and button labels: keep them short (translations tend to run longer; menus and buttons must still fit).
9. If an English line is only a name, a number or a code, copy it unchanged."""

LANG = {
    'fr-CA': {
        'T': 'FR', 'title': 'French (Canada), Quebec usage',
        'conventions': """- Quebec French, not France French. Address the reader as « vous ».
- Numbers: 1 000 (space as thousands separator), 0,07 (decimal comma), 15 % (space before %).
- Space before a colon ( : ). No space before ? ! ;
- Quotes « ». Apostrophe ’.
- courriel (not e-mail), Nous joindre (Contact), témoin (cookie).""",
        'glossary': [
            ('Process Skid Plants', 'Usines de procédé sur skid'), ('Pilot & Demonstration Plants', 'Usines pilotes et de démonstration'),
            ('Industrial Process Skids', 'Skids de procédé industriels'), ('Industrial Automation', 'Automatisation industrielle'),
            ('PlantON by Instron Technologies', '{PlantON} par Instron Technologies'), ('How We Work', 'Notre façon de travailler'),
            ('Discuss Your Project', 'Parlons de votre projet'), ('Basic Engineering & Feasibility', 'Ingénierie de base et faisabilité'),
            ('Detailed Engineering', 'Ingénierie détaillée'), ('Integrated Design & Build', 'Conception et construction intégrées'),
            ('commissioning', 'mise en service'), ('control panel', 'panneau de commande'), ('I/O', 'E/S'), ('E&I', 'É-I'),
            ('OEE', 'TRG (OEE)'), ('CIP', 'NEP (CIP)'), ('utilities', 'utilités'), ('heat & mass balance', 'bilan de matière et d’énergie'),
            ('battery limits', 'limites de batterie'), ('line list', 'liste des lignes'), ('general arrangement', 'plan d’ensemble'),
            ('cause-and-effect matrix', 'matrice causes-effets'), ('interlocks / permissives / trips', 'verrouillages / permissifs / déclenchements'),
            ('nuisance trips', 'déclenchements intempestifs'), ('HAZOP deviations', 'dérives'), ('fail-safe state', 'état de repli sûr'),
            ('relief and venting', 'protection contre les surpressions et évents'), ('EHS', 'SSE (santé, sécurité et environnement)'),
            ('API (pharma ingredient)', 'IPA (ingrédient pharmaceutique actif); never "API", which means a PLC in French'),
            ('QA/QC', 'AQ/CQ'), ('procurement', 'approvisionnement'), ('batch / recipe', 'lot / recette'), ('historian', 'historien'),
            ('loop checks', 'vérifications de boucles'), ('as-built drawings', 'plans tels que construits'), ('hygienic design', 'conception hygiénique'),
            ('long-lead items', 'équipements à long délai de livraison'), ('throughput', 'débit'), ('equipment duty', 'tenue en service / fonction des équipements'),
            ('scale-up', 'mise à l’échelle'), ('pilot (the plant)', 'usine pilote / unité pilote, never "pilote" alone'),
            ('gas handling / fluid handling', 'manipulation des gaz / transfert des fluides (never "manutention")'),
            ('equipment arrangement / layout', 'implantation des équipements'), ('S88 control module', 'module de commande'),
            ('brownfield / greenfield', 'site existant / nouveau site'), ('Insights', 'Perspectives'), ('Case Studies', 'Études de cas'),
            ('Industries', 'Secteurs'), ('Applications', 'Applications'), ('Read the case study', 'Lire l’étude de cas'),
            ('Let’s grow together', 'Grandissons ensemble'), ('Independent company, not affiliated with Instron® (ITW)', 'Société indépendante, non affiliée à Instron® (ITW)'),
            ('control system / control philosophy', 'système de contrôle / philosophie de contrôle (panneau de commande stays)'),
            ('R&D', 'R-D'), ('data or software pilot (a trial project)', 'projet pilote'),
            ('Engineer | Embrace | Elevate (tagline)', 'keep in English'),
        ],
    },
    'es-MX': {
        'T': 'ES', 'title': 'Spanish (Mexico)',
        'conventions': """- Mexican Spanish, not Spain Spanish. Address the reader as «usted».
- Numbers as in English: 1,000 and 0.07; 15% (no space).
- Use opening ¿ and ¡ marks.
- correo electrónico (not e-mail), Contáctenos / Contacto, reporte, monitoreo, refacciones, alambrado, clemas.""",
        'glossary': [
            ('Process Skid Plants', 'Plantas de proceso en skid'), ('Pilot & Demonstration Plants', 'Plantas piloto y de demostración'),
            ('Industrial Process Skids', 'Skids de proceso industriales'), ('Industrial Automation', 'Automatización industrial'),
            ('PlantON by Instron Technologies', '{PlantON} de Instron Technologies'), ('How We Work', 'Cómo trabajamos'),
            ('Discuss Your Project', 'Hablemos de su proyecto'), ('Basic Engineering & Feasibility', 'Ingeniería básica y factibilidad'),
            ('Detailed Engineering', 'Ingeniería de detalle'), ('Integrated Design & Build', 'Diseño y construcción integrados'),
            ('commissioning', 'puesta en marcha'), ('start-up', 'arranque'), ('control panel', 'tablero de control (never "panel de control")'),
            ('I/O', 'E/S'), ('E&I', 'E&I (eléctrica e instrumentación)'), ('OEE', 'OEE'), ('CIP', 'CIP (limpieza en sitio)'),
            ('utilities', 'servicios auxiliares (never "utilidades")'), ('heat & mass balance', 'balance de materia y energía'),
            ('battery limits', 'límites de batería'), ('line list', 'lista de líneas'), ('general arrangement', 'arreglo general'),
            ('cause-and-effect matrix', 'matriz causa-efecto'), ('interlocks / permissives / trips', 'enclavamientos / permisivos / disparos'),
            ('nuisance trips', 'disparos en falso'), ('HAZOP deviations', 'desviaciones'), ('fail-safe state', 'estado seguro ante falla'),
            ('relief and venting', 'alivio de presión y venteo'), ('EHS', 'SSMA (seguridad, salud y medio ambiente)'),
            ('API (pharma ingredient)', 'IFA (ingrediente farmacéutico activo)'), ('QA/QC', 'AC/CC; the QA department: el área de aseguramiento de calidad'),
            ('procurement', 'procura'), ('batch / recipe', 'lote / receta'), ('historian', 'historiador'), ('loop checks', 'verificación de lazos'),
            ('as-built drawings', 'planos as-built'), ('hygienic design', 'diseño higiénico'), ('long-lead items', 'equipos de largo tiempo de entrega'),
            ('throughput', 'capacidad de procesamiento'), ('equipment duty', 'servicio de los equipos'), ('scale-up', 'escalamiento'),
            ('pilot (the plant)', 'planta piloto / unidad piloto, never "piloto" alone'), ('equipment arrangement / layout', 'arreglo de equipos'),
            ('S88 control module', 'módulo de control'), ('brownfield / greenfield', 'planta existente / planta nueva'),
            ('shift', 'turno'), ('downtime', 'paro / tiempo de paro'), ('spare parts', 'refacciones'), ('Insights', 'Perspectivas'),
            ('Case Studies', 'Casos de estudio'), ('Industries', 'Industrias'), ('Applications', 'Aplicaciones'), ('Read the case study', 'Leer el caso de estudio'),
            ('Let’s grow together', 'Crezcamos juntos'), ('Independent company, not affiliated with Instron® (ITW)', 'Empresa independiente, no afiliada a Instron® (ITW)'),
            ('control system / control philosophy', 'sistema de control / filosofía de control'),
            ('layout (of equipment or a skid)', 'arreglo (never "distribución")'), ('terminal / marshalling cabinet', 'gabinete de clemas'),
            ('batch hold / abort / restart', 'pausa / aborto / rearranque (ISA-88; not "cancelación")'), ('R&D', 'I+D'),
            ('Explore (link label)', 'Explorar'), ('data or software pilot (a trial project)', 'etapa piloto / proyecto piloto'),
            ('Engineer | Embrace | Elevate (tagline)', 'keep in English'),
        ],
    },
}

# Page and menu names already live on the site, copied from the catalogue at pack time so the pack
# always matches the menus. Filled in main().
NAMES = {}
NAME_EXTRA = ['Applications', 'Separation & Solvent Recovery', 'Brownfield Automation Modernization',
              'Production Visibility & OEE', 'Utility & Energy Monitoring', 'Read the case study', 'Discuss Your Project']


def live_names(root, cats):
    import html, re as _re
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(open(os.path.join(root, 'index.html'), encoding='utf-8'), 'html.parser')
    names = []
    for a in soup.select('nav#it-navigation a, nav#it-navigation button.it-trigger'):
        t = ' '.join(a.get_text(' ', strip=True).split())
        if t and 'internal' not in t and 'Plant ON' not in t and t not in names:
            names.append(t)
    names += [n for n in NAME_EXTRA if n not in names]
    out = {}
    for loc, S in cats.items():
        rows = []
        for n in names:
            k = html.escape(n, quote=False)
            hit = next((x for x in S if x == k or _re.fullmatch(_re.escape(k) + r'<span\d+></span\d+>', x)), None)
            if hit and S.get(hit):
                rows.append((n, _re.sub(r'</?span\d+>', '', S[hit])))
        out[loc] = rows
    return out


def show(k):
    """English line as the translator sees it: entities decoded, codes kept."""
    return k.replace('&amp;', '&').replace('&lt;', '‹').replace('&gt;', '›')


def header(pack, loc, nn, total, pages, n_lines):
    L = LANG[loc]; T = L['T']
    gl = '\n'.join(f'| {a} | {b} |' for a, b in L['glossary'])
    nm = '\n'.join(f'| {show(a)} | {b} |' for a, b in NAMES.get(loc, []))
    return f"""# Instron Technologies website: translation pack {pack}, {L['title']}, file {nn} of {total}

**Pages in this file:** {', '.join(pages)}  ·  **Lines:** {n_lines}

## Instructions for the translator (paste this whole file into ChatGPT)

You are a senior technical translator and a process and automation engineer. Translate the website text below from English into **{L['title']}** for Instron Technologies, an engineering company that designs and builds process skid plants (pilot, demonstration and industrial), industrial automation (PLC, HMI, SCADA) and the PlantON™ plant-data platform. Readers are plant managers, process engineers and R&D leaders.

**Return the completed file as a downloadable .md file with exactly the same structure.** If you cannot create a file, return the whole file inside one code block (```), so the tags are not lost. Do not add comments, notes or summaries.

### Rules
{COMMON_RULES.replace('{T}', T)}

### Conventions for {L['title']}
{L['conventions']}

### Glossary (use these terms every time)
| English | {T} |
|---|---|
{gl}

### Page and menu names already on the site (use exactly these words, also inside sentences)
| English | {T} |
|---|---|
{nm}

---

## Text to translate
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--root')]
    root = os.path.abspath(next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--root=')), '.'))
    pack, groups = args[0], [g.split(',') for g in args[1:]]
    out_dir = os.path.join(root, 'i18n', 'packs', pack); os.makedirs(out_dir, exist_ok=True)
    cats = {loc: E.load(root, loc)['segments'] for loc in LANG}
    NAMES.update(live_names(root, cats))
    # every English line on the pack pages, numbered once for all languages
    ids, files = {}, []
    n = 0
    for g in groups:
        lines = []
        for p in g:
            for k in E.page_keys(os.path.join(root, p + '.html')):
                if any(v['key'] == k for v in ids.values()) or all(cats[l].get(k) for l in LANG):
                    continue
                n += 1; i = f'{pack.upper()}-{n:04d}'
                ids[i] = {'key': k, 'page': p}; lines.append(i)
        for s in range(0, len(lines), MAX_LINES):
            files.append((g, lines[s:s + MAX_LINES]))
    json.dump({'pack': pack, 'pages': [p for g in groups for p in g], 'ids': ids},
              open(os.path.join(out_dir, f'{pack}-ids.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for loc, L in LANG.items():
        T = L['T']; todo = [(g, [i for i in ls if not cats[loc].get(ids[i]['key'])]) for g, ls in files]
        todo = [(g, ls) for g, ls in todo if ls]
        for nn, (g, ls) in enumerate(todo, 1):
            body, page = [], None
            for i in ls:
                if ids[i]['page'] != page:
                    page = ids[i]['page']; body.append(f'\n### Page: {page}\n')
                body.append(f"[{i}]\nEN: {show(ids[i]['key'])}\n{T}: \n")
            fn = os.path.join(out_dir, f'{pack}-{loc}-{nn:02d}.md')
            open(fn, 'w', encoding='utf-8').write(header(pack, loc, nn, len(todo), g, len(ls)) + '\n'.join(body) + '\n')
            print(fn, len(ls), 'lines')


if __name__ == '__main__':
    main()
