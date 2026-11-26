/* IRA, Instron's Resource Assistant, for the Instron Technologies website.
   A guided project map (three short steps) or a typed description, ending in a project brief:
   suggested first engagement phase, pages to read, related projects and questions to prepare.
   Runs entirely in the visitor's browser and uses only the approved list in ira-content.json.
   The brief can be saved as PDF, copied, or carried into the Contact form.
   No cookies, no browser storage, no outside services; nothing is sent anywhere by this script.
   Hidden until switched on with ?ira=1 in the page address (?ira=0 switches it off). */
(function () {
  'use strict';

  /* ---------------- matching engine (no page access, testable on its own) ---------------- */
  var INTENTS = {
    pilot: ['pilot and demonstration plants', [/\bpilot/, /\bdemonstrat/, /\bdemo (plant|unit|skid)/, /\blab(oratory)?[- ]scale/, /\bbench[- ]scale/, /\bmini[- ]?plant/, /\btest (rig|unit|bench|system)/, /\brigs?\b/, /\btrials?\b/]],
    skid: ['process skid plants', [/\bskids?\b/, /\bmodular\b/, /\bprocess (plant|system|package|unit)/, /\bpackaged? (unit|plant|system)/]],
    industrial_skid: ['industrial process skids', [/\b(production|industrial|commercial)[- ](scale|skid|plant|unit|duty)/, /\bdosing/, /\bfull[- ]scale/]],
    scaleup: ['technology scale-up', [/\bscale[- ]?up/, /\bscal(e|ing) (it|this|our|the)\b/, /\bcommerciali[sz]/, /\bfoak\b|\bfirst[- ]of[- ]a[- ]kind/, /\blab to (pilot|plant|industrial)/, /\btrl\b/]],
    separation: ['separation and solvent recovery', [/\bdistill/, /\bsolvents?\b/, /\bevaporat/, /\bextract/, /\bseparat/, /\bmembrane/, /\bcrystalli[sz]/, /\bdryers?\b|\bdrying\b/, /\bfractionat/, /\bpurif/, /\bmethanol|\bethanol|\bacetone/]],
    carbon: ['carbon capture', [/\bco2\b|co₂/, /\bcarbon (capture|dioxide)/, /\bccus?\b/, /\bflue gas/, /\bamine/]],
    hydrogen: ['hydrogen and electrochemical systems', [/\bhydrogen/, /\belectroly[sz]/, /\bfuel cell/, /\bammonia/, /\bmethane/, /\bgraphene/, /\bpyrolysis/]],
    battery: ['battery recycling and critical minerals', [/\bbatter(y|ies)/, /\blithium|\bnickel|\bcobalt|\brare[- ]earth/, /\bcritical (mineral|material)/, /\bhydrometallurg|\bleach/, /\bblack mass/, /\bmining\b|\bminerals?\b/]],
    energy: ['energy transition', [/\benergy transition/, /\bclean ?tech/, /\bdecarboni[sz]/, /\brenewable/, /\bbiofuel|\bbiogas|\bsaf\b/]],
    research: ['research and technology development', [/\bresearch/, /\buniversit/, /\binstitute/, /\bacademi/, /\br ?& ?d\b|\br and d\b/, /\bstart[- ]?up\b/, /\btechnology developer/, /\bexperiment/]],
    automation: ['industrial automation and controls', [/\bplcs?\b/, /\bscada/, /\bhmis?\b/, /\bdcs\b/, /\bautomat/, /\bcontrols?\b/, /\bcontrol (system|panel|logic|philosophy)/, /\binstrument/, /\be ?& ?i\b|\belectrical and instrumentation/, /\bvfds?\b|\bdrives\b/, /\bsensors?\b/, /\bpid\b|\bloop tuning/, /\binterlocks?\b/]],
    modernize: ['brownfield modernization', [/\bupgrad/, /\bobsole/, /\blegacy/, /\bold (plc|scada|system|control|panel|hmi|dcs)/, /\bmigrat/, /\bmoderni[sz]/, /\bretrofit/, /\bend[- ]of[- ](life|support)/, /\breplac\w* (the |our |an? )?(old )?(plc|scada|hmi|dcs|panel|control)/, /\bbrownfield/, /\bs5\b|\bs7[- ]?300|\bplc[- ]?5\b|\bslc ?500/]],
    batch: ['batch and process automation', [/\bbatch(es|ing)?\b/, /\brecipes?\b/, /\bs88\b|\bisa[- ]?88/, /\bformulat/, /\bmaterial (movement|transfer|addition)/, /\bsequenc/]],
    cip: ['clean-in-place', [/\bcip\b/, /\bclean[- ]in[- ]place/, /\bsip\b|\bsteam[- ]in[- ]place/, /\bsanitary|\bhygienic/]],
    panels: ['control panels', [/\bcontrol panels?\b/, /\bpanel (build|design|shop)/, /\bul ?508a|\bcsa\b|\bce mark/, /\bmcc\b/]],
    oee: ['production visibility and OEE', [/\boee\b/, /\bdowntime/, /\bproduction (target|visibility|loss|losses|report|tracking)/, /\bthroughput/, /\bplan (vs|versus) actual/, /\bavailability\b/, /\bscrap\b|\breject/, /\bproductivity/, /\bshift reports?/, /\bbottleneck/, /\bcycle time/, /\bmachine (performance|status|monitoring)/, /\blosses\b|\bloss analysis/]],
    utility: ['utility and energy monitoring', [/\benergy (use|usage|consumption|monitor\w*|costs?|bills?)/, /\belectricity/, /\bpower (consumption|use|usage|bills?)/, /\bkwh\b/, /\butilit(y|ies)/, /\bcompressed air/, /\bwater (use|usage|consumption)/, /\bsteam (use|usage|consumption)/, /\b(sub[- ]?)?meters?\b|\bmetering/, /\bconsumption/]],
    trace: ['traceability and digital records', [/\btraceab/, /\bgenealog/, /\bbatch (records?|history|reports?)/, /\bpaperless|\bpaper (records|forms|logs)/, /\bdigital (forms|records|logbook)/, /\bpasteuri[sz]/, /\bhaccp/, /\brecalls?\b/]],
    plantdata: ['PlantON plant data', [/\bplant ?on\b/, /\bdashboards?/, /\bkpis?\b/, /\b(plant|production|machine|process) data/, /\bvisibility/, /\breal[- ]time (data|monitor\w*|view)/, /\biiot|\biot\b|\bindustry 4/, /\bhistorian/, /\bmes\b/, /\bmis\b|\bdaily reports?/, /\bdigital factory|\bdigiti[sz]/, /\btrends?\b/]],
    compliance: ['validation and compliance', [/\b21 ?cfr|\bpart 11/, /\bgamp/, /\bc?gmp\b/, /\bvalidat/, /\biq\b|\boq\b/, /\baudit trails?/, /\bcompliance reports?/]],
    feasibility: ['basic engineering and feasibility', [/\bfeasib/, /\bbasic engineering/, /\bconcept(ual)? (design|study|engineering)/, /\bfeed\b(?! (stream|rate|material|stock))/, /\bpfds?\b|\bprocess flow diagram/, /\bmass balance/, /\bcost estimate|\bbudget(ary)? (estimate|price|quote|number)/, /\bdesign basis/]],
    detailed: ['detailed engineering', [/\bdetailed (engineering|design)/, /\bp ?& ?ids?\b|\bp and ids?\b/, /\bga drawings?|\bgeneral arrangement/, /\b3d model/, /\bengineering package|\bdrawings\b/, /\bdatasheets?/]],
    build: ['integrated design and build', [/\bdesign (and|&) build/, /\bfabricat/, /\bturnkey/, /\bfat\b|\bfactory acceptance/, /\bcommission/, /\binstallation/, /\bsat\b|\bsite acceptance/]],
    hazop: ['HAZOP and process safety studies', [/\bhazop/, /\bhazid/, /\bprocess safety (study|review)/]],
    food: ['food, beverage and dairy', [/\bfood/, /\bbeverages?\b|\bdrinks?\b|\bbrew|\bjuices?\b/, /\bdairy|\bmilk|\bcheese|\byogh?urt|\bice cream/, /\bchocolate|\bconfection|\bbakery|\bsnacks?\b/]],
    pharma: ['pharma and life sciences', [/\bpharma/, /\bapis?\b|\bactive (pharmaceutical )?ingredients?/, /\bbiotech|\blife sciences?/, /\bvaccin|\badjuvant/, /\bnutraceutical|\bbotanical/, /\bmedical|\bhealthcare/]],
    chemical: ['chemicals, refining and consumer products', [/\bchemicals?\b/, /\brefin(ery|eries|ing)/, /\bpetrochem|\boil (and|&) gas/, /\bspecialty|\bpolymers?\b|\bresins?\b|\bcoatings?\b/, /\bpersonal[- ]care|\bcosmetic|\bdetergent|\bcleaning products?|\bconsumer products?/, /\breactors?\b|\bcstr/]],
    manufacturing: ['industrial manufacturing', [/\bmanufactur\w* (line|plant|floor)/, /\bassembly/, /\bdie[- ]?cast/, /\bpaint ?shop|\bpaint line/, /\bautomotive|\bauto parts|\balloy wheels?/, /\bcnc\b|\bmachining|\bmachine shop/, /\bdiscrete/, /\bpresses\b|\bmou?lding/]],
    proof: ['project references', [/\bcase stud/, /\breferences?\b/, /\bexamples?\b/, /\bsimilar (projects?|work)/, /\bexperience/, /\bhave you (ever )?(done|built|worked|delivered)/, /\bportfolio/, /\bpast projects?/]],
    company: ['about the company', [/\bwho are you|\babout (you|instron|the company|your company)/, /\bcompany (profile|overview)/, /\bleadership|\bfounders?\b/]],
    location: ['offices and regional presence', [/\boffices?\b/, /\bwhere are you( based| located)?/, /\blocations?\b/]],
    careers: ['careers', [/\bjobs?\b|\bcareers?\b|\bhiring|\bintern(ship)?s?\b|\bvacanc|\bresume|\bcv\b|\bapply for/]],
    contact: ['talking to an engineer', [/\b(talk|speak|meet|call|connect|chat) (to|with) (an? |your )?(engineer|expert|specialist|someone|person|sales|team)/, /\bcontact (you|sales|an engineer|me|someone)/, /\bcall me|\bemail me|\breach out/, /\bquot(e|ation)s?\b|\brfq\b|\bproposal|\btender|\bbids?\b/]],
    price: ['pricing', [/\bprices?\b|\bpricing|\bcosts?\b|\bhow much|\bbudget\b/]],
    safety: ['safety or engineering approval', [/\b(approve|certify|sign[- ]?off|verify|stamp)\b.{0,40}\b(design|drawings?|calculations?|system|panel|vessel|skid)/, /\bis (it|this|that) safe/, /\bsafety (approval|sign[- ]?off|certificat)/, /\bsil (rating|level|assessment|verification)|\bsil ?[1-4]\b/, /\bhazardous area classification|\batex (certif|rating)/, /\bpressure vessel (code|stamp|certif)/, /\b(is|are) (it|this|my|our) (\w+ )?(compliant|legal|code[- ]compliant)/]]
  };
  var META = { company: 1, location: 1, careers: 1, contact: 1, price: 1, proof: 1, safety: 1 };
  var INDUSTRY = { food: 1, pharma: 1, chemical: 1, manufacturing: 1, research: 1, energy: 1 };
  var AREA = { // matches the Contact form "Area of interest" options
    P: 'Process skid / pilot plant', A: 'Automation & controls', D: 'PlantON / industrial data'
  };
  var AREA_OF = {
    pilot: 'P', skid: 'P', industrial_skid: 'P', scaleup: 'P', separation: 'P', carbon: 'P', hydrogen: 'P', battery: 'P',
    feasibility: 'P', detailed: 'P', build: 'P', hazop: 'P',
    automation: 'A', modernize: 'A', batch: 'A', cip: 'A', panels: 'A', compliance: 'A',
    oee: 'D', utility: 'D', trace: 'D', plantdata: 'D'
  };
  var STAGES = [ // order matters: the first match wins; labels match the Contact form "Project stage" options
    ['Detailed engineering', [/\bdetailed (engineering|design)/, /\bp ?& ?ids?\b/]],
    ['Operating plant / upgrade', [/\bexisting\b/, /\brunning\b/, /\boperating (plant|line|site)/, /\bupgrad/, /\bretrofit/, /\blegacy/, /\bold (plc|scada|system|control|panel|hmi|machines?|line)/, /\bcurrent(ly)? (plant|system|line|setup)/, /\bbrownfield/, /\bdowntime/, /\bour (plant|line|lines|machines|factory|site)\b/]],
    ['Industrial implementation', [/\bcommercial/, /\bfull[- ]scale/, /\bindustrial[- ]scale/, /\bproduction[- ](line|plant|scale)/, /\bnew (plant|line|facility|factory)/, /\bgreenfield/]],
    ['Pilot or demonstration', [/\bpilot/, /\bdemonstrat/, /\blab(oratory)?\b/, /\bbench/]],
    ['Concept / feasibility', [/\bfeasib/, /\bconcept/, /\bidea\b/, /\bearly stage/, /\bexplor/, /\bstudy\b/, /\bbudget/]]
  ];

  function norm(t) { return (' ' + String(t || '').toLowerCase().replace(/[’']/g, '').replace(/\s+/g, ' ') + ' '); }

  function detect(text) {
    var t = norm(text), hits = {};
    Object.keys(INTENTS).forEach(function (k) {
      var n = 0;
      INTENTS[k][1].forEach(function (re) { if (re.test(t)) n++; });
      if (n) hits[k] = Math.min(n, 3);
    });
    return hits;
  }

  function detectStage(text) {
    var t = norm(text);
    for (var i = 0; i < STAGES.length; i++) {
      for (var j = 0; j < STAGES[i][1].length; j++) if (STAGES[i][1][j].test(t)) return STAGES[i][0];
    }
    return '';
  }

  function areaOf(intents) {
    var s = { P: 0, A: 0, D: 0 };
    Object.keys(intents).forEach(function (k) { if (AREA_OF[k]) s[AREA_OF[k]] += intents[k]; });
    var best = '', v = 0;
    Object.keys(s).forEach(function (a) { if (s[a] > v) { v = s[a]; best = a; } });
    return best;
  }

  function solutionSignal(intents) {
    var n = 0;
    Object.keys(intents).forEach(function (k) { if (!META[k] && !INDUSTRY[k]) n += intents[k]; });
    return n;
  }

  var STAGE_BOOST = {
    'Concept / feasibility': { 'how-we-work-phase-1': 2.5, 'technology-scale-up': 0.5 },
    'Pilot or demonstration': { 'pilot-demonstration-plants': 1.5, 'insights-lab-to-pilot-to-industrial': 0.5 },
    'Detailed engineering': { 'how-we-work-phase-2': 2.5 },
    'Industrial implementation': { 'industrial-process-skids': 1.5, 'how-we-work-phase-3': 1.5, 'technology-scale-up': 0.5 },
    'Operating plant / upgrade': { 'brownfield-automation-modernization': 1, 'planton-digital-factory': 0.5 }
  };

  /* Score every approved entry. Returns {pages:[...], cases:[...]} sorted, each with matched intent keys. */
  function rank(entries, intents, stage, text) {
    var t = norm(text);
    var metaWanted = {};
    Object.keys(intents).forEach(function (k) { if (META[k]) metaWanted[k] = 1; });
    var scored = [];
    entries.forEach(function (e) {
      if (!e || !e.url || !/^[a-z0-9-]+\.html(#[a-z0-9-]+)?$/.test(e.url)) return; // only our own pages
      var s = 0, matched = [];
      Object.keys(e.tags || {}).forEach(function (k) {
        if (!intents[k]) return;
        if (META[k] && k !== 'proof' && k !== 'safety' && k !== 'price') { s += e.tags[k] * 1.5; matched.push(k); return; }
        s += e.tags[k] * intents[k]; matched.push(k);
      });
      (e.keywords || []).forEach(function (w) { if (t.indexOf(String(w).toLowerCase()) >= 0) s += 1.5; });
      if (stage && STAGE_BOOST[stage] && STAGE_BOOST[stage][e.id] && s > 0) s += STAGE_BOOST[stage][e.id];
      if (stage && STAGE_BOOST[stage] && STAGE_BOOST[stage][e.id] && s === 0 && solutionSignal(intents) > 0 && e.type === 'phase') s += STAGE_BOOST[stage][e.id] * 0.8;
      // company pages only when the visitor asked about the company
      if (e.type === 'company' && !Object.keys(e.tags || {}).some(function (k) { return metaWanted[k]; })) s = 0;
      if (e.type === 'contact') s = 0; // the Contact route is offered as an action, not a card
      // industry pages rank below solution pages unless the industry is all we know
      if (e.type === 'industry' && solutionSignal(intents) > 0) s *= 0.75;
      if (e.type === 'insight') s *= 0.6;
      if (s > 0) scored.push({ e: e, s: s, matched: matched });
    });
    scored.sort(function (a, b) { return b.s - a.s; });
    return {
      pages: scored.filter(function (x) { return x.e.type !== 'case'; }),
      cases: scored.filter(function (x) { return x.e.type === 'case'; })
    };
  }

  /* Pick up to 3: best pages, plus one related project when it is a good match. */
  function pick(r) {
    var out = [], minPage = 2, minCase = 3;
    var top = r.pages.length ? r.pages[0].s : 0;
    r.pages.forEach(function (x) {
      if (out.length < 3 && x.s >= minPage && x.s >= top * 0.34) out.push(x);
    });
    if (r.cases.length && r.cases[0].s >= minCase) {
      if (out.length === 3) out[2] = r.cases[0]; else out.push(r.cases[0]);
    }
    return out.slice(0, 3);
  }

  function reasonFor(x) {
    var labels = [];
    x.matched.forEach(function (k) { if (INTENTS[k] && labels.length < 2) labels.push(INTENTS[k][0]); });
    if (x.e.type === 'case') return labels.length ? 'A completed project involving ' + labels.join('; ') + '.' : 'A related completed project.';
    return labels.length ? 'Relevant to: ' + labels.join('; ') + '.' : 'Related to what you described.';
  }

  var ENGINE = { detect: detect, detectStage: detectStage, areaOf: areaOf, solutionSignal: solutionSignal, rank: rank, pick: pick, reasonFor: reasonFor, AREA: AREA, INTENTS: INTENTS };
  if (typeof module !== 'undefined' && module.exports) { module.exports = ENGINE; return; }
  if (typeof document === 'undefined') return;

  /* =====================================================================================
     Page integration: switch, link carry-over, Contact page prefill
     ===================================================================================== */
  var params = new URLSearchParams(location.search);
  var self = document.currentScript;
  var base = self ? new URL('.', self.src) : new URL('assets/ira/', location.href);
  var ON = params.get('ira') === '1';
  var BRIEF_KEY = '#ira-brief=';
  var PAGE = (location.pathname.split('/').pop() || 'index.html').replace(/\?.*$/, '') || 'index.html';

  function ensureCss() {
    if (document.getElementById('ira-css')) return;
    var l = document.createElement('link');
    l.id = 'ira-css'; l.rel = 'stylesheet';
    var v = self ? new URL(self.src).searchParams.get('v') : '';
    l.href = new URL('ira.css' + (v ? '?v=' + encodeURIComponent(v) : ''), base).href;
    document.head.appendChild(l);
  }

  function onContactPage() { return PAGE === 'contact.html'; }

  function fillContact(payload) {
    var form = document.getElementById('enquiry-draft');
    if (!form || !payload) return false;
    ensureCss();
    var ta = form.querySelector('textarea[name="challenge"]');
    if (ta && payload.brief) {
      var cur = ta.value.trim();
      ta.value = (cur ? cur + '\n\n' : '') + String(payload.brief).slice(0, Math.max(0, 2900 - cur.length));
    }
    [['type', payload.area], ['stage', payload.stage]].forEach(function (p) {
      var sel = form.querySelector('select[name="' + p[0] + '"]');
      if (!sel || !p[1] || sel.value) return;
      for (var i = 0; i < sel.options.length; i++) if (sel.options[i].text === p[1]) { sel.selectedIndex = i; break; }
    });
    var note = document.getElementById('ira-prefill-note');
    if (!note) {
      note = document.createElement('p');
      note.id = 'ira-prefill-note'; note.className = 'ira-prefill'; note.setAttribute('role', 'status');
      form.insertBefore(note, form.firstChild);
    }
    note.textContent = 'Your project brief from IRA has been added to the project description. Please review it, add your details and open the email draft. Nothing is sent until you send the email yourself.';
    var first = form.querySelector('input[name="name"]');
    form.scrollIntoView({ block: 'start' });
    if (first) first.focus({ preventScroll: true });
    return true;
  }

  if (onContactPage() && location.hash.indexOf(BRIEF_KEY) === 0) {
    var payload0 = null;
    try { payload0 = JSON.parse(decodeURIComponent(location.hash.slice(BRIEF_KEY.length))); } catch (err) { payload0 = null; }
    history.replaceState(null, '', location.pathname + location.search);
    var run0 = function () { fillContact(payload0); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run0); else run0();
  }

  if (!ON) return;

  function carry(a) {
    var raw = a.getAttribute('href');
    if (!raw || /^(mailto:|tel:|#|javascript:)/i.test(raw)) return;
    var u;
    try { u = new URL(raw, location.href); } catch (err) { return; }
    if (u.origin !== location.origin || !/\.html$/.test(u.pathname) || u.searchParams.has('ira')) return;
    u.searchParams.set('ira', '1');
    a.setAttribute('href', u.pathname.split('/').pop() + u.search + u.hash);
  }
  function flagUrl(u) { return String(u).replace(/^([^#?]+)/, '$1?ira=1'); }

  /* =====================================================================================
     Guided map: options (site wording; every choice maps to the same need tags the
     page list uses, so the map and the free-text route rank pages the same way)
     ===================================================================================== */
  var TRACKS = {
    process: { title: 'Process systems and scale-up', line: 'Pilot, demonstration and industrial process skids', page: 'process-skid-plants', area: 'P', tags: { skid: 1 } },
    automation: { title: 'Controls and automation', line: 'New controls, upgrades, batch and validated systems', page: 'industrial-automation', area: 'A', tags: { automation: 1 } },
    data: { title: 'Plant data with PlantON', line: 'OEE, energy, traceability and production visibility', page: 'planton-digital-factory', area: 'D', tags: { plantdata: 1 } }
  };
  var PATH = [
    { id: 'lab', label: 'Lab or concept', hint: 'It works at lab scale, or it is still an idea', stage: 'Concept / feasibility', tags: { scaleup: 1 } },
    { id: 'pilot', label: 'Pilot', hint: 'Proving the process at small continuous scale', stage: 'Pilot or demonstration', tags: { pilot: 2 } },
    { id: 'demo', label: 'Demonstration', hint: 'A larger unit to prove performance and economics', stage: 'Pilot or demonstration', tags: { pilot: 2, scaleup: 1 } },
    { id: 'foak', label: 'First commercial plant', hint: 'Moving into industrial production', stage: 'Industrial implementation', tags: { industrial_skid: 2, scaleup: 1 } },
    { id: 'operating', label: 'Operating plant', hint: 'Expanding or improving a running plant', stage: 'Operating plant / upgrade', tags: { industrial_skid: 1 } }
  ];
  var PROCESS = [
    { id: 'sep', label: 'Separation or solvent recovery', tags: { separation: 2 } },
    { id: 'react', label: 'Reaction or synthesis', tags: { chemical: 1 } },
    { id: 'carbon', label: 'Carbon capture or hydrogen', tags: { carbon: 2, hydrogen: 2 } },
    { id: 'battery', label: 'Battery or critical minerals', tags: { battery: 2 } },
    { id: 'food', label: 'Food, beverage or dairy', tags: { food: 2 } },
    { id: 'pharma', label: 'Pharma, API or extraction', tags: { pharma: 2 } },
    { id: 'research', label: 'A research program', tags: { research: 2 } },
    { id: 'other', label: 'Something else', tags: {} }
  ];
  var NEEDS = {
    automation: [
      { id: 'legacy', label: 'Replace or upgrade an old PLC, SCADA or HMI', tags: { modernize: 3, automation: 1 }, stage: 'Operating plant / upgrade' },
      { id: 'newline', label: 'Controls for a new line, skid or plant', tags: { automation: 3 }, stage: 'Industrial implementation' },
      { id: 'batch', label: 'Batch and recipe control', tags: { batch: 3 } },
      { id: 'validated', label: 'Validated systems (GAMP 5, 21 CFR Part 11)', tags: { compliance: 3, pharma: 1 } },
      { id: 'panels', label: 'Control panels and electrical design', tags: { panels: 3 } },
      { id: 'cip', label: 'Clean-in-place automation', tags: { cip: 3 } }
    ],
    data: [
      { id: 'oee', label: 'Downtime and OEE', tags: { oee: 3 } },
      { id: 'energy', label: 'Energy and utility use', tags: { utility: 3 } },
      { id: 'trace', label: 'Batch records and traceability', tags: { trace: 3 } },
      { id: 'reports', label: 'Dashboards and daily reports', tags: { plantdata: 3 } }
    ]
  };
  var INDUSTRIES = [ // agreed order
    { id: 'energy', label: 'Energy Transition & Critical Minerals', tags: { energy: 1 } },
    { id: 'research', label: 'Research & Technology Development', tags: { research: 1 } },
    { id: 'chemical', label: 'Chemicals, Refining & Consumer Products', tags: { chemical: 1 } },
    { id: 'food', label: 'Food, Beverage & Dairy', tags: { food: 1 } },
    { id: 'pharma', label: 'Pharma & Life Sciences', tags: { pharma: 1 } },
    { id: 'manufacturing', label: 'Industrial Manufacturing', tags: { manufacturing: 1 } }
  ];
  var ENGINEERING = [
    { id: 'none', label: 'Nothing formal yet', phase: 'phase-1' },
    { id: 'basic', label: 'A process basis, PFDs or a feasibility study', phase: 'phase-2' },
    { id: 'detailed', label: 'A detailed design, ready to build', phase: 'phase-3' },
    { id: 'unsure', label: 'Not sure', phase: 'phase-1' }
  ];
  var DATA_TODAY = [
    { id: 'manual', label: 'Manual logs or spreadsheets' },
    { id: 'partial', label: 'Some PLC or meter data, not connected' },
    { id: 'system', label: 'A historian or MES is already in place' },
    { id: 'unsure', label: 'Not sure' }
  ];
  var PAGE_TRACK = {
    'process-skid-plants.html': 'process', 'pilot-demonstration-plants.html': 'process', 'industrial-process-skids.html': 'process',
    'technology-scale-up.html': 'process', 'separation-solvent-recovery.html': 'process', 'insights-lab-to-pilot-to-industrial.html': 'process',
    'industrial-automation.html': 'automation', 'brownfield-automation-modernization.html': 'automation', 'batch-process-automation.html': 'automation',
    'insights-brownfield-modernization.html': 'automation',
    'planton-digital-factory.html': 'data', 'production-visibility-oee.html': 'data', 'utility-energy-monitoring.html': 'data',
    'insights-plant-data-rollout.html': 'data',
    'solutions.html': '', 'applications.html': '', 'industries.html': '', 'how-we-work.html': '', 'case-studies.html': '', 'project-portfolio.html': '',
    'energy-transition-critical-minerals.html': '', 'research-technology-development.html': '', 'chemicals-refining-consumer-products.html': '',
    'food-beverage-dairy.html': '', 'pharma-life-sciences.html': '', 'industrial-manufacturing.html': ''
  };

  /* =====================================================================================
     State and helpers
     ===================================================================================== */
  var data = null, loading = null;
  var sel, chat, mode, step;
  function resetAll() {
    sel = { track: '', path: '', process: [], need: [], industry: '', engineering: '', today: '', notes: '' };
    chat = { msgs: [], intents: {}, stage: '', area: '', askedArea: false, askedStage: false, results: [] };
    mode = 'map'; step = 1;
  }
  resetAll();

  function el(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }
  function btn(cls, txt, on) { var b = el('button', cls, txt); b.type = 'button'; if (on) b.addEventListener('click', on); return b; }
  function find(list, id) { for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i]; return null; }
  function entry(id) { var es = (data && data.entries) || []; for (var i = 0; i < es.length; i++) if (es[i].id === id) return es[i]; return null; }
  function imgUrl(src) { return src ? new URL(src, location.href).href : ''; }
  function addTags(into, tags) { Object.keys(tags || {}).forEach(function (k) { into[k] = (into[k] || 0) + tags[k]; }); }
  function absUrl(u) { var x = new URL(u, location.href); x.search = ''; return x.href; }

  function loadData() {
    if (data) return Promise.resolve(data);
    if (!loading) {
      loading = fetch(new URL('ira-content.json', base).href, { credentials: 'same-origin', cache: 'no-cache' })
        .then(function (r) { if (!r.ok) throw new Error('content'); return r.json(); })
        .then(function (d) { data = d || { entries: [] }; return data; })
        .catch(function () { loading = null; throw new Error('content'); });
    }
    return loading;
  }

  /* =====================================================================================
     Project brief model, built from the map or from a typed conversation
     ===================================================================================== */
  function briefFromMap() {
    var tr = TRACKS[sel.track], tags = {}, stage = '';
    addTags(tags, tr.tags);
    var p = find(PATH, sel.path);
    if (sel.track === 'process' && p) { addTags(tags, p.tags); stage = p.stage; }
    sel.process.forEach(function (id) { var x = find(PROCESS, id); if (x) addTags(tags, x.tags); });
    sel.need.forEach(function (id) {
      var x = find(NEEDS[sel.track] || [], id);
      if (x) { addTags(tags, x.tags); if (!stage && x.stage) stage = x.stage; }
    });
    var ind = find(INDUSTRIES, sel.industry); if (ind) addTags(tags, ind.tags);
    if (!stage && sel.track === 'data') stage = 'Operating plant / upgrade';
    var notesTags = detect(sel.notes); Object.keys(notesTags).forEach(function (k) { if (!META[k]) tags[k] = (tags[k] || 0) + notesTags[k]; });
    var eng = find(ENGINEERING, sel.engineering);
    var told = [['Area', tr.title]];
    if (p) told.push(['Stage', p.label]);
    if (sel.process.length) told.push(['Process', sel.process.map(function (id) { return find(PROCESS, id).label; }).join('; ')]);
    if (sel.need.length) told.push(['Main need', sel.need.map(function (id) { return find(NEEDS[sel.track], id).label; }).join('; ')]);
    if (ind) told.push(['Industry', ind.label]);
    if (eng) told.push(['Engineering today', eng.label]);
    var td = find(DATA_TODAY, sel.today); if (td) told.push(['Data today', td.label]);
    if (sel.notes) told.push(['Notes', sel.notes]);
    var headline;
    if (sel.track === 'process') headline = (p ? p.label + ' stage' : 'Process system') + (sel.process.length && sel.process[0] !== 'other' ? ': ' + find(PROCESS, sel.process[0]).label.toLowerCase() : '');
    else if (sel.need.length) headline = find(NEEDS[sel.track], sel.need[0]).label;
    else headline = tr.title;
    var phaseId = sel.track === 'data' ? 'planton-deploy' : (eng ? eng.phase : 'phase-1');
    return build(sel.track, tags, stage, sel.notes, phaseId, told, headline);
  }

  function briefFromChat() {
    var area = areaOf(chat.intents) || chat.area || 'P';
    var track = area === 'A' ? 'automation' : area === 'D' ? 'data' : 'process';
    var phase = track === 'data' ? 'planton-deploy' : chat.stage === 'Detailed engineering' ? 'phase-2' : 'phase-1';
    var told = [['Area', TRACKS[track].title]];
    if (chat.stage) told.push(['Stage', chat.stage]);
    told.push(['Described as', chat.msgs.join(' / ')]);
    var tags = {}; Object.keys(chat.intents).forEach(function (k) { if (!META[k]) tags[k] = chat.intents[k]; });
    addTags(tags, TRACKS[track].tags);
    return build(track, tags, chat.stage, chat.msgs.join(' '), phase, told, chat.msgs[0] || TRACKS[track].title);
  }

  function build(track, tags, stage, text, phaseId, told, headline) {
    var r = rank(data.entries, tags, stage, text);
    var pages = [], cases = [];
    r.pages.forEach(function (x) {
      if (pages.length < 3 && x.s >= 2 && /^(solution|application|industry|insight)$/.test(x.e.type) &&
          !pages.some(function (y) { return y.e.id === x.e.id; })) pages.push(x);
    });
    var used = {};
    pages.forEach(function (x) { if (x.e.image) used[x.e.image[0]] = 1; });
    r.cases.forEach(function (x) {
      if (cases.length >= 2 || x.s < 2) return;
      if (x.e.image && used[x.e.image[0]]) { // same photo already shown: keep the project, drop the repeat photo
        var e2 = {}; Object.keys(x.e).forEach(function (k) { e2[k] = x.e[k]; }); e2.image = null;
        x = { e: e2, s: x.s, matched: x.matched };
      } else if (x.e.image) used[x.e.image[0]] = 1;
      cases.push(x);
    });
    if (!pages.length) { var d0 = entry(TRACKS[track].page); if (d0) pages.push({ e: d0, s: 1, matched: [] }); }
    var prep = null;
    var pool = pages.map(function (x) { return x.e; }).concat(r.pages.map(function (x) { return x.e; }), [entry(TRACKS[track].page)]);
    for (var i = 0; i < pool.length && !prep; i++) if (pool[i] && pool[i].prepare && pool[i].prepare.length) prep = { items: pool[i].prepare, title: pool[i].title, url: pool[i].url };
    if (!prep && data.prepare_default) prep = { items: data.prepare_default.items, title: 'How We Work', url: data.prepare_default.source };
    return {
      track: track, area: TRACKS[track].area, stage: stage, told: told, headline: headline,
      phase: data.phases && data.phases[phaseId], phaseId: phaseId,
      pages: pages, cases: cases, prepare: prep, date: new Date()
    };
  }

  function briefText(b) {
    var L = ['Project brief prepared with IRA on the Instron Technologies website', ''];
    b.told.forEach(function (t) { L.push(t[0] + ': ' + t[1]); });
    if (b.phase) L.push('', 'Suggested first step: ' + b.phase.title + ' (' + absUrl(b.phase.url) + ')');
    if (b.pages.length) { L.push('', 'Pages to read:'); b.pages.forEach(function (x) { L.push('- ' + x.e.title + ' (' + absUrl(x.e.url) + ')'); }); }
    if (b.cases.length) { L.push('', 'Related projects:'); b.cases.forEach(function (x) { L.push('- ' + x.e.title + ' (' + absUrl(x.e.url) + ')'); }); }
    if (b.prepare) { L.push('', 'Useful inputs to prepare:'); b.prepare.items.forEach(function (q) { L.push('- ' + q); }); }
    return L.join('\n').slice(0, 2900);
  }

  function handoffHref(b) {
    var payload = { v: 2, brief: briefText(b), area: AREA[b.area] || '', stage: b.stage || '' };
    return { payload: payload, href: 'contact.html?ira=1' + BRIEF_KEY + encodeURIComponent(JSON.stringify(payload)) };
  }

  /* =====================================================================================
     Shell: launcher, panel, header with progress
     ===================================================================================== */
  var root = el('div', 'ira-root'); root.id = 'ira-root';
  var launcher = btn('ira-launcher');
  launcher.setAttribute('aria-expanded', 'false');
  launcher.setAttribute('aria-controls', 'ira-panel');
  launcher.appendChild(el('span', 'ira-dot')).setAttribute('aria-hidden', 'true');
  launcher.appendChild(el('span', 'ira-launch-k', 'IRA'));
  launcher.appendChild(el('span', 'ira-launch-t', 'Map your project'));

  var panel = el('section', 'ira-panel');
  panel.id = 'ira-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-labelledby', 'ira-title');
  panel.hidden = true;

  var head = el('div', 'ira-head');
  var hgroup = el('div', 'ira-hgroup');
  var h2 = el('h2', 'ira-title', 'IRA'); h2.id = 'ira-title';
  hgroup.appendChild(h2);
  hgroup.appendChild(el('p', 'ira-sub', 'Instron’s Resource Assistant'));
  var closeBtn = btn('ira-close', '×', function () { setOpen(false); });
  closeBtn.setAttribute('aria-label', 'Close IRA');
  head.appendChild(hgroup); head.appendChild(closeBtn);
  var progress = el('div', 'ira-progress'); progress.setAttribute('aria-hidden', 'true');
  for (var pi = 0; pi < 4; pi++) progress.appendChild(el('span'));
  head.appendChild(progress);

  var view = el('div', 'ira-view');
  var foot = el('div', 'ira-foot');
  var note = el('p', 'ira-note', 'Automated guide. It uses pages from this website only. Nothing you enter is stored or sent; an engineer sees your brief only if you choose to email it.');
  panel.appendChild(head); panel.appendChild(view); panel.appendChild(foot); panel.appendChild(note);
  root.appendChild(launcher); root.appendChild(panel);

  function setProgress(n) {
    Array.prototype.forEach.call(progress.children, function (s, i) { s.className = i < n ? 'is-on' : ''; });
    progress.style.display = n ? '' : 'none';
  }

  function clearView() { view.textContent = ''; foot.textContent = ''; view.scrollTop = 0; panel.classList.remove('is-brief', 'is-chat'); }

  function stepHead(kicker, title, lede) {
    if (kicker) view.appendChild(el('p', 'ira-kicker', kicker));
    var h = el('h3', 'ira-step-title', title); h.tabIndex = -1;
    view.appendChild(h);
    if (lede) view.appendChild(el('p', 'ira-lede', lede));
    return h;
  }

  function navRow(backFn, nextLabel, nextFn, canNext) {
    foot.textContent = '';
    if (backFn) foot.appendChild(btn('ira-btn', 'Back', backFn));
    var spacer = el('span', 'ira-spacer'); foot.appendChild(spacer);
    if (nextFn) {
      var n = btn('ira-btn ira-primary', nextLabel, nextFn);
      n.disabled = !canNext;
      foot.appendChild(n);
      return n;
    }
    return null;
  }

  // a group of choice buttons: single choice behaves like radios, multi like toggles
  function choices(list, opts) {
    var box = el('div', 'ira-choices ' + (opts.cls || ''));
    box.setAttribute('role', opts.multi ? 'group' : 'radiogroup');
    box.setAttribute('aria-label', opts.label);
    list.forEach(function (o) {
      var b = btn('ira-choice');
      if (o.img) {
        var im = el('img', 'ira-choice-img'); im.src = imgUrl(o.img[0]); im.alt = ''; im.loading = 'lazy'; im.decoding = 'async';
        b.appendChild(im);
      }
      var tx = el('span', 'ira-choice-text');
      tx.appendChild(el('span', 'ira-choice-label', o.label));
      if (o.hint) tx.appendChild(el('span', 'ira-choice-hint', o.hint));
      b.appendChild(tx);
      var on = function () { return opts.multi ? opts.get().indexOf(o.id) >= 0 : opts.get() === o.id; };
      var paint = function () {
        Array.prototype.forEach.call(box.children, function (c, i) {
          var picked = opts.multi ? opts.get().indexOf(list[i].id) >= 0 : opts.get() === list[i].id;
          c.classList.toggle('is-on', picked);
          if (opts.multi) c.setAttribute('aria-pressed', String(picked)); else c.setAttribute('aria-checked', String(picked));
        });
      };
      if (!opts.multi) b.setAttribute('role', 'radio');
      b.addEventListener('click', function () {
        if (opts.multi) {
          var cur = opts.get().slice(), i = cur.indexOf(o.id);
          if (i >= 0) cur.splice(i, 1); else { if (opts.max && cur.length >= opts.max) cur.shift(); cur.push(o.id); }
          opts.set(cur);
        } else {
          opts.set(on() && opts.optional ? '' : o.id);
        }
        paint();
        if (opts.change) opts.change();
      });
      box.appendChild(b);
      box._paint = paint;
    });
    view.appendChild(box);
    if (box._paint) box._paint();
    return box;
  }

  function focusTitle(h) { if (h) setTimeout(function () { h.focus({ preventScroll: true }); }, 30); }

  /* =====================================================================================
     Map steps
     ===================================================================================== */
  function renderStart() {
    mode = 'map'; step = 1; clearView(); setProgress(1);
    var h = stepHead('Step 1 of 3', 'What are you working on?', 'Pick the closest area. In about two minutes you get a project brief you can keep or share with your team.');
    var list = Object.keys(TRACKS).map(function (k) {
      var e = entry(TRACKS[k].page);
      return { id: k, label: TRACKS[k].title, hint: TRACKS[k].line, img: e && e.image };
    });
    choices(list, { label: 'Area', cls: 'ira-tracks', get: function () { return sel.track; },
      set: function (v) { if (v !== sel.track) { sel.track = v; sel.path = ''; sel.process = []; sel.need = []; sel.engineering = ''; sel.today = ''; } },
      change: function () { setTimeout(renderNeeds, 120); } });
    var alt = el('p', 'ira-alt');
    alt.appendChild(document.createTextNode('Prefer to type? '));
    alt.appendChild(btn('ira-link', 'Describe it in your own words', renderChat));
    view.appendChild(alt);
    navRow(null);
    focusTitle(h);
  }

  function renderNeeds() {
    if (!sel.track) return renderStart();
    mode = 'map'; step = 2; clearView(); setProgress(2);
    var next;
    var ready = function () { return sel.track === 'process' ? !!sel.path : sel.need.length > 0; };
    var upd = function () { if (next) next.disabled = !ready(); };
    var h;
    if (sel.track === 'process') {
      h = stepHead('Step 2 of 3', 'Where is the technology today?', 'Choose the point on the path that fits best.');
      var path = el('ol', 'ira-path');
      path.setAttribute('role', 'radiogroup');
      path.setAttribute('aria-label', 'Technology stage');
      var paintPath = function () {
        var idx = -1;
        PATH.forEach(function (s, i) { if (s.id === sel.path) idx = i; });
        Array.prototype.forEach.call(path.children, function (li, i) {
          li.classList.toggle('is-done', idx >= 0 && i < idx);
          li.classList.toggle('is-on', i === idx);
          li.firstChild.setAttribute('aria-checked', String(i === idx));
        });
      };
      PATH.forEach(function (s) {
        var li = el('li', 'ira-node');
        var b = btn('ira-node-btn', null, function () { sel.path = s.id; paintPath(); upd(); });
        b.setAttribute('role', 'radio');
        b.appendChild(el('span', 'ira-node-dot')).setAttribute('aria-hidden', 'true');
        b.appendChild(el('span', 'ira-node-label', s.label));
        b.appendChild(el('span', 'ira-node-hint', s.hint));
        li.appendChild(b); path.appendChild(li);
      });
      view.appendChild(path); paintPath();
      view.appendChild(el('h4', 'ira-q', 'What does the process involve? (optional, up to three)'));
      choices(PROCESS, { label: 'Process', multi: true, max: 3, cls: 'ira-chips', get: function () { return sel.process; }, set: function (v) { sel.process = v; } });
    } else {
      var t = sel.track === 'automation' ? 'What is the main need?' : 'What do you want to see or improve?';
      h = stepHead('Step 2 of 3', t, sel.track === 'data' ? 'Choose up to three.' : 'Choose one or two.');
      choices(NEEDS[sel.track], { label: 'Main need', multi: true, max: sel.track === 'data' ? 3 : 2, cls: 'ira-needs',
        get: function () { return sel.need; }, set: function (v) { sel.need = v; }, change: upd });
      view.appendChild(el('h4', 'ira-q', 'Industry (optional)'));
      choices(INDUSTRIES, { label: 'Industry', optional: true, cls: 'ira-chips', get: function () { return sel.industry; }, set: function (v) { sel.industry = v; } });
    }
    next = navRow(renderStart, 'Next', renderLast, ready());
    focusTitle(h);
  }

  function renderLast() {
    mode = 'map'; step = 3; clearView(); setProgress(3);
    var h;
    if (sel.track === 'data') {
      h = stepHead('Step 3 of 3', 'How are these figures captured today?', 'This helps an engineer judge where to start.');
      choices(DATA_TODAY, { label: 'Data today', optional: true, cls: 'ira-list', get: function () { return sel.today; }, set: function (v) { sel.today = v; } });
    } else {
      h = stepHead('Step 3 of 3', 'What engineering exists today?', 'This sets the suggested first step. Each phase is contracted separately, with no obligation to continue.');
      choices(ENGINEERING, { label: 'Engineering today', optional: true, cls: 'ira-list', get: function () { return sel.engineering; }, set: function (v) { sel.engineering = v; } });
    }
    var lab = el('label', 'ira-q', 'Anything else we should know? (optional)'); lab.htmlFor = 'ira-notes';
    var ta = el('textarea', 'ira-input'); ta.id = 'ira-notes'; ta.rows = 3; ta.maxLength = 600; ta.value = sel.notes;
    ta.placeholder = 'For example: capacity, timing, or what the next stage must prove. Please leave out confidential details.';
    ta.addEventListener('input', function () { sel.notes = ta.value.trim(); });
    view.appendChild(lab); view.appendChild(ta);
    navRow(renderNeeds, 'Create my project brief', function () { withData(function () { renderBrief(briefFromMap(), renderLast); }); }, true);
    focusTitle(h);
  }

  /* =====================================================================================
     Project brief view (also used for printing)
     ===================================================================================== */
  function card(x, kind) {
    var a = el('a', 'ira-rcard' + (kind === 'case' ? ' ira-rcard-case' : ''));
    a.href = flagUrl(x.e.url);
    if (x.e.image) {
      var im = el('img', 'ira-rcard-img'); im.src = imgUrl(x.e.image[0]); im.alt = ''; im.loading = 'lazy'; im.decoding = 'async';
      a.appendChild(im);
    }
    var body = el('span', 'ira-rcard-body');
    if (kind === 'case') body.appendChild(el('span', 'ira-rcard-k', 'Completed project'));
    body.appendChild(el('span', 'ira-rcard-title', x.e.title));
    body.appendChild(el('span', 'ira-rcard-reason', reasonFor(x)));
    a.appendChild(body);
    return a;
  }

  function briefNode(b, forPrint) {
    var wrap = el('div', 'ira-brief');
    var top = el('div', 'ira-brief-top');
    top.appendChild(el('p', 'ira-kicker', 'Your project brief · ' + b.date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })));
    var h = el('h3', 'ira-brief-title', b.headline); h.tabIndex = -1;
    top.appendChild(h);
    var dl = el('dl', 'ira-told');
    b.told.forEach(function (t) { dl.appendChild(el('dt', null, t[0])); dl.appendChild(el('dd', null, t[1])); });
    top.appendChild(dl);
    wrap.appendChild(top);

    if (b.phase) {
      var ph = el('section', 'ira-sec ira-phase');
      ph.appendChild(el('h4', 'ira-sec-title', 'Suggested first step'));
      var pt = el('p', 'ira-phase-name');
      var pa = el('a', null, b.phase.title); pa.href = flagUrl(b.phase.url); pt.appendChild(pa);
      ph.appendChild(pt);
      ph.appendChild(el('p', 'ira-phase-what', b.phase.what));
      if (b.phase.best_when && b.track === 'process') ph.appendChild(el('p', 'ira-phase-when', 'Best when: ' + b.phase.best_when));
      ph.appendChild(el('p', 'ira-mini', b.phase.list_label || 'Typical deliverables'));
      var ul = el('ul', 'ira-deliv');
      var all = b.phase.deliverables || [], n = forPrint ? all.length : Math.min(6, all.length);
      for (var i = 0; i < n; i++) ul.appendChild(el('li', null, all[i]));
      ph.appendChild(ul);
      if (!forPrint && all.length > n) {
        var more = el('a', 'ira-more', 'See all ' + all.length + ' deliverables'); more.href = flagUrl(b.phase.url); ph.appendChild(more);
      }
      if (b.phaseId !== 'planton-deploy') ph.appendChild(el('p', 'ira-fine', 'Each phase is contracted separately, with no obligation to continue.'));
      wrap.appendChild(ph);
    }
    if (b.pages.length) {
      var rp = el('section', 'ira-sec');
      rp.appendChild(el('h4', 'ira-sec-title', 'Read next'));
      var g = el('div', 'ira-rgrid'); b.pages.forEach(function (x) { g.appendChild(card(x)); }); rp.appendChild(g);
      wrap.appendChild(rp);
    }
    if (b.cases.length) {
      var rc = el('section', 'ira-sec');
      rc.appendChild(el('h4', 'ira-sec-title', 'Related projects'));
      var g2 = el('div', 'ira-rgrid'); b.cases.forEach(function (x) { g2.appendChild(card(x, 'case')); }); rc.appendChild(g2);
      wrap.appendChild(rc);
    }
    if (b.prepare) {
      var qs = el('section', 'ira-sec');
      qs.appendChild(el('h4', 'ira-sec-title', 'Useful inputs to prepare for a first conversation'));
      var ol = el('ul', 'ira-qs'); b.prepare.items.forEach(function (q) { ol.appendChild(el('li', null, q)); }); qs.appendChild(ol);
      var src = el('p', 'ira-fine');
      src.appendChild(document.createTextNode('From '));
      var sa = el('a', null, b.prepare.title); sa.href = flagUrl(b.prepare.url); src.appendChild(sa);
      qs.appendChild(src);
      wrap.appendChild(qs);
    }
    return wrap;
  }

  var lastBrief = null;
  function renderBrief(b, backFn) {
    lastBrief = b;
    mode = 'brief'; clearView(); setProgress(4); panel.classList.add('is-brief');
    var node = briefNode(b, false);
    var tools = el('div', 'ira-tools');
    tools.appendChild(btn('ira-tool', 'Save as PDF', function () { printBrief(b); }));
    var copy = btn('ira-tool', 'Copy brief', function () { copyText(briefText(b), copy); });
    tools.appendChild(copy);
    node.querySelector('.ira-brief-top').appendChild(tools);
    view.appendChild(node);
    var h = handoffHref(b);
    foot.textContent = '';
    if (backFn) foot.appendChild(btn('ira-btn', 'Back', backFn));
    foot.appendChild(btn('ira-btn ira-quiet', 'Start over', function () { resetAll(); renderStart(); }));
    foot.appendChild(el('span', 'ira-spacer'));
    if (onContactPage()) {
      foot.appendChild(btn('ira-btn ira-primary', 'Add the brief to the form', function () { fillContact(h.payload); setOpen(false, true); }));
    } else {
      var go = el('a', 'ira-btn ira-primary', 'Discuss with an engineer'); go.href = h.href; foot.appendChild(go);
    }
    focusTitle(node.querySelector('.ira-brief-title'));
  }

  function copyText(t, b) {
    var done = function () { var o = b.textContent; b.textContent = 'Copied'; setTimeout(function () { b.textContent = o; }, 1600); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(done, fallback); else fallback();
    function fallback() {
      var ta = el('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (err) { /* ignore */ }
      ta.remove();
    }
  }

  function printBrief(b) {
    var old = document.getElementById('ira-print'); if (old) old.remove();
    var pr = el('div'); pr.id = 'ira-print';
    var hd = el('div', 'ira-print-head');
    var logo = document.querySelector('header img, .lv-header img');
    if (logo) { var lg = el('img', 'ira-print-logo'); lg.src = logo.currentSrc || logo.src; lg.alt = 'Instron Technologies'; hd.appendChild(lg); }
    hd.appendChild(el('p', 'ira-print-tag', 'Engineer | Embrace | Elevate'));
    pr.appendChild(hd);
    pr.appendChild(briefNode(b, true));
    var ft = el('div', 'ira-print-foot');
    ft.appendChild(el('p', null, 'Instron Technologies · sales@instrontechnologies.com · instrontechnologies.com'));
    ft.appendChild(el('p', null, 'Instron Technologies is an independent company, not affiliated with Instron® (ITW). This brief was prepared from the visitor’s own answers on the website.'));
    pr.appendChild(ft);
    document.body.appendChild(pr);
    document.body.classList.add('ira-printing');
    var after = function () { document.body.classList.remove('ira-printing'); pr.remove(); window.removeEventListener('afterprint', after); };
    window.addEventListener('afterprint', after);
    setTimeout(function () { window.print(); }, 60);
  }

  /* =====================================================================================
     Typed conversation (same engine as before), ending in the same project brief
     ===================================================================================== */
  var log, input;
  function renderChat() {
    mode = 'chat'; clearView(); setProgress(0); panel.classList.add('is-chat');
    log = el('div', 'ira-log'); log.setAttribute('role', 'log'); log.setAttribute('aria-live', 'polite'); log.setAttribute('aria-relevant', 'additions');
    view.appendChild(log);
    var form = el('form', 'ira-form');
    var label = el('label', 'ira-sr', 'Describe what you want to improve or build'); label.htmlFor = 'ira-text';
    input = el('textarea', 'ira-input'); input.id = 'ira-text'; input.rows = 2; input.maxLength = 1200;
    input.placeholder = 'For example: we want to scale a solvent recovery process to a pilot skid';
    var send = el('button', 'ira-send', 'Send'); send.type = 'submit';
    form.appendChild(label); form.appendChild(input); form.appendChild(send);
    form.addEventListener('submit', function (e) { e.preventDefault(); var v = input.value; input.value = ''; handle(v); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit', { cancelable: true })); }
    });
    foot.appendChild(form);
    say('Describe what you are trying to improve or build, in your own words. I will point you to the right pages and can turn it into a project brief.');
    var alt = el('p', 'ira-alt'); alt.appendChild(btn('ira-link', 'Use the guided map instead', function () { renderStart(); }));
    log.appendChild(alt);
    setTimeout(function () { input.focus(); }, 30);
  }

  function scrollLog() { view.scrollTop = view.scrollHeight; }
  function say(text, who) {
    var m = el('p', 'ira-msg ' + (who === 'you' ? 'ira-you' : 'ira-bot'), text);
    log.appendChild(m); scrollLog(); return m;
  }
  function chips(list, onPick, ariaLabel) {
    var box = el('div', 'ira-chatchips'); box.setAttribute('role', 'group'); box.setAttribute('aria-label', ariaLabel);
    list.forEach(function (c) {
      var b = btn('ira-chip', c[0], function () {
        Array.prototype.forEach.call(box.querySelectorAll('button'), function (x) { x.disabled = true; });
        b.classList.add('is-picked'); onPick(c);
      });
      box.appendChild(b);
    });
    log.appendChild(box); scrollLog();
    var f = box.querySelector('button'); if (f) f.focus();
  }
  function chatCards(list) {
    var g = el('div', 'ira-rgrid ira-rgrid-chat');
    list.forEach(function (x) { g.appendChild(card(x, x.e.type === 'case' ? 'case' : '')); });
    log.appendChild(g); scrollLog();
  }
  function clearOneOffs() { Object.keys(META).forEach(function (k) { delete chat.intents[k]; }); }

  function chatActions(personFirst) {
    var row = el('div', 'ira-actions');
    var mk = btn('ira-btn ira-primary', 'Create my project brief', function () { renderBrief(briefFromChat(), renderChat); });
    var talk = btn('ira-btn', 'Discuss with an engineer', function () {
      var b = briefFromChat(); var h = handoffHref(b);
      if (onContactPage()) { fillContact(h.payload); setOpen(false, true); } else location.href = h.href;
    });
    if (personFirst) { talk.className = 'ira-btn ira-primary'; mk.className = 'ira-btn'; row.appendChild(talk); row.appendChild(mk); }
    else { row.appendChild(mk); row.appendChild(talk); }
    row.appendChild(btn('ira-btn', 'Start over', function () { resetAll(); renderChat(); }));
    log.appendChild(row); scrollLog();
  }

  function respond() {
    var I = chat.intents, text = chat.msgs.join(' ');
    var sig = solutionSignal(I);
    if (I.safety) {
      say('I cannot approve designs or give safety, code or certification decisions. Engineering sign-off is agreed for each project with a qualified engineer. This page explains how we approach safety, and our engineers can review your question directly.');
      var t = entry('trust-responsibility'); chat.results = t ? [{ e: t, s: 1, matched: ['safety'] }] : [];
      if (chat.results.length) chatCards(chat.results);
      clearOneOffs(); chatActions(true); return;
    }
    if (I.careers && !sig) {
      var c = entry('careers'); say('It sounds like you are interested in working with us.');
      if (c) chatCards([{ e: c, s: 1, matched: ['careers'] }]);
      clearOneOffs(); return;
    }
    var wantsPerson = !!I.contact;
    if (!sig && !chat.askedArea && !wantsPerson && !I.company && !I.location && !I.proof) {
      chat.askedArea = true;
      say('Thanks. Which of these is closest to what you need?');
      chips([
        ['Build a pilot plant or process skid', { pilot: 1, skid: 1 }],
        ['Automate or upgrade plant controls', { automation: 1, modernize: 1 }],
        ['Use plant data: OEE, energy, traceability', { plantdata: 1, oee: 1 }],
        ['Engineering studies or design', { feasibility: 1, detailed: 1 }],
        ['Not sure yet', null]
      ], function (c) { say(c[0], 'you'); if (c[1]) addTags(chat.intents, c[1]); respond(); }, 'Type of need');
      return;
    }
    if (sig && !chat.stage && !chat.askedStage && !wantsPerson) {
      chat.askedStage = true;
      say('Where is the project today?');
      chips([
        ['Idea or feasibility', 'Concept / feasibility'], ['Lab, pilot or demonstration', 'Pilot or demonstration'],
        ['Ready for detailed engineering', 'Detailed engineering'], ['New industrial plant or line', 'Industrial implementation'],
        ['Operating plant or upgrade', 'Operating plant / upgrade'], ['Skip this question', '']
      ], function (c) { say(c[0], 'you'); chat.stage = c[1]; respond(); }, 'Project stage');
      return;
    }
    chat.area = areaOf(I);
    var list = pick(rank(data.entries, I, chat.stage, text));
    if (!list.length && (I.proof || !sig)) {
      var gen = I.proof ? ['case-studies', 'project-portfolio'] : ['how-we-work-phase-1', 'case-studies', 'process-skid-plants'];
      list = gen.map(entry).filter(Boolean).map(function (e) { return { e: e, s: 1, matched: I.proof ? ['proof'] : [] }; });
    }
    if (I.company || I.location) {
      var cp = rank(data.entries, I, '', text).pages.filter(function (x) { return x.e.type === 'company'; }).slice(0, 2);
      if (cp.length) list = cp;
    }
    chat.results = list;
    if (I.price) say('Pricing depends on scope, so an engineer agrees it with you. A Basic Engineering & Feasibility phase gives a Class 4 budgetary estimate before you commit to detailed design.');
    if (list.length) { say(list.length === 1 ? 'This page is the closest match:' : 'These pages are the closest match:'); chatCards(list); }
    else say('I could not match this to a specific page. An engineer can read your description and reply.');
    clearOneOffs();
    chatActions(wantsPerson);
  }

  function handle(text) {
    text = String(text || '').trim().slice(0, 1200);
    if (text.length < 2) return;
    say(text, 'you');
    chat.msgs.push(text);
    addTags(chat.intents, detect(text));
    if (!chat.stage) chat.stage = detectStage(text);
    var wait = say('…'); wait.setAttribute('aria-hidden', 'true');
    loadData().then(function () { wait.remove(); respond(); }).catch(function () {
      wait.remove();
      say('Sorry, I could not load the page list just now. You can still reach our engineers through the Contact page.');
    });
  }

  /* =====================================================================================
     Open/close, page entry points, mount
     ===================================================================================== */
  function withData(fn) {
    loadData().then(fn).catch(function () {
      clearView(); setProgress(0);
      view.appendChild(el('p', 'ira-lede', 'Sorry, IRA could not load just now. You can still reach our engineers through the Contact page.'));
      var a = el('a', 'ira-btn ira-primary', 'Go to the Contact page'); a.href = 'contact.html?ira=1'; view.appendChild(a);
    });
  }

  function setOpen(open, quiet) {
    panel.hidden = !open;
    launcher.setAttribute('aria-expanded', String(open));
    root.classList.toggle('is-open', open);
    document.documentElement.classList.toggle('ira-open', open);
    if (open) {
      if (!view.childNodes.length) withData(renderStart);
    } else if (!quiet) launcher.focus();
  }

  function openAt(track, chatMode) {
    setOpen(true, true);
    withData(function () {
      if (chatMode) return renderChat();
      if (track) { sel.track = track; renderNeeds(); } else renderStart();
    });
  }

  launcher.addEventListener('click', function () { setOpen(panel.hidden); });
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.preventDefault(); setOpen(false); } });

  // Home: "Start with your problem" band under the hero
  function homeBand() {
    var hero = document.querySelector('section.mk-hero');
    if (!hero) return;
    var sec = el('section', 'ira-start'); sec.setAttribute('aria-labelledby', 'ira-start-title');
    var w = el('div', 'ira-start-wrap');
    w.appendChild(el('p', 'ira-start-k', 'Start with your problem'));
    var t = el('h2', 'ira-start-title', 'Map your project in about two minutes'); t.id = 'ira-start-title';
    w.appendChild(t);
    w.appendChild(el('p', 'ira-start-lede', 'Tell IRA where you are and what you need. You get a project brief with a suggested first step, pages to read and related projects, ready to share with your team.'));
    var g = el('div', 'ira-start-grid');
    loadData().then(function () {
      Object.keys(TRACKS).forEach(function (k) {
        var e = entry(TRACKS[k].page);
        var b = btn('ira-start-card', null, function () { openAt(k); });
        if (e && e.image) { var im = el('img'); im.src = imgUrl(e.image[0]); im.alt = ''; im.loading = 'lazy'; b.appendChild(im); }
        var s = el('span', 'ira-start-card-body');
        s.appendChild(el('span', 'ira-start-card-title', TRACKS[k].title));
        s.appendChild(el('span', 'ira-start-card-line', TRACKS[k].line));
        s.appendChild(el('span', 'ira-start-card-go', 'Start →'));
        b.appendChild(s); g.appendChild(b);
      });
    }).catch(function () { sec.remove(); });
    w.appendChild(g);
    var alt = el('p', 'ira-start-alt');
    alt.appendChild(document.createTextNode('Prefer to type? '));
    alt.appendChild(btn('ira-link', 'Describe it in your own words', function () { openAt('', true); }));
    w.appendChild(alt);
    sec.appendChild(w);
    hero.parentNode.insertBefore(sec, hero.nextSibling);
  }

  // Solution, application and industry pages: a short prompt before the page ends
  function pageBand() {
    if (!(PAGE in PAGE_TRACK)) return;
    var main = document.querySelector('main');
    if (!main) return;
    var sec = el('section', 'ira-band'); sec.setAttribute('aria-label', 'Map your project with IRA');
    var w = el('div', 'ira-band-wrap');
    var tx = el('div');
    tx.appendChild(el('p', 'ira-band-title', 'Not sure this fits your process?'));
    tx.appendChild(el('p', 'ira-band-line', 'Map your project in about two minutes and get a brief you can share with your team.'));
    w.appendChild(tx);
    w.appendChild(btn('ira-btn ira-primary', 'Map my project', function () { openAt(PAGE_TRACK[PAGE]); }));
    sec.appendChild(w);
    var back = main.querySelector('.back-to-top');
    if (back && back.parentNode === main) main.insertBefore(sec, back); else main.appendChild(sec);
  }

  function mount() {
    ensureCss();
    Array.prototype.forEach.call(document.querySelectorAll('a[href]'), carry);
    document.body.appendChild(root);
    if (PAGE === 'index.html') homeBand();
    pageBand();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
