/* IRA, Instron's Resource Assistant: guided page finder for the Instron Technologies website.
   Runs entirely in the visitor's browser. It matches what the visitor types against the approved
   page list in ira-content.json and can carry a short brief to the Contact form.
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

  /* ---------------- switch, link carry-over and Contact page prefill ---------------- */
  var params = new URLSearchParams(location.search);
  var self = document.currentScript;
  var base = self ? new URL('.', self.src) : new URL('assets/ira/', location.href);
  var ON = params.get('ira') === '1';
  var BRIEF_KEY = '#ira-brief=';

  function ensureCss() {
    if (document.getElementById('ira-css')) return;
    var l = document.createElement('link');
    l.id = 'ira-css'; l.rel = 'stylesheet';
    var v = self ? new URL(self.src).searchParams.get('v') : '';
    l.href = new URL('ira.css' + (v ? '?v=' + encodeURIComponent(v) : ''), base).href;
    document.head.appendChild(l);
  }

  function onContactPage() { return /(^|\/)contact\.html$/.test(location.pathname); }

  function fillContact(payload) {
    var form = document.getElementById('enquiry-draft');
    if (!form || !payload) return false;
    ensureCss();
    var ta = form.querySelector('textarea[name="challenge"]');
    if (ta && payload.brief) {
      var cur = ta.value.trim();
      ta.value = (cur ? cur + '\n\n' : '') + String(payload.brief).slice(0, 2900 - cur.length);
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
    note.textContent = 'Your brief from IRA has been added to the project description. Please review it, add your details and open the email draft. Nothing is sent until you send the email yourself.';
    var first = form.querySelector('input[name="name"]');
    form.scrollIntoView({ block: 'start' });
    if (first) first.focus({ preventScroll: true });
    return true;
  }

  if (onContactPage() && location.hash.indexOf(BRIEF_KEY) === 0) {
    var payload = null;
    try { payload = JSON.parse(decodeURIComponent(location.hash.slice(BRIEF_KEY.length))); } catch (err) { payload = null; }
    history.replaceState(null, '', location.pathname + location.search);
    var run = function () { fillContact(payload); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
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

  /* ---------------- widget ---------------- */
  var entries = null, loading = null;
  var state;
  function reset() { state = { msgs: [], intents: {}, stage: '', area: '', askedArea: false, askedStage: false, results: [] }; }
  reset();

  function el(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }

  function loadEntries() {
    if (entries) return Promise.resolve(entries);
    if (!loading) {
      loading = fetch(new URL('ira-content.json', base).href, { credentials: 'same-origin', cache: 'no-cache' })
        .then(function (r) { if (!r.ok) throw new Error('content'); return r.json(); })
        .then(function (d) { entries = (d && d.entries) || []; return entries; })
        .catch(function () { loading = null; throw new Error('content'); });
    }
    return loading;
  }

  var root = el('div', 'ira-root'); root.id = 'ira-root';
  var launcher = el('button', 'ira-launcher');
  launcher.type = 'button';
  launcher.setAttribute('aria-expanded', 'false');
  launcher.setAttribute('aria-controls', 'ira-panel');
  launcher.appendChild(el('span', 'ira-dot')).setAttribute('aria-hidden', 'true');
  launcher.appendChild(el('span', null, 'Ask IRA'));

  var panel = el('section', 'ira-panel');
  panel.id = 'ira-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-labelledby', 'ira-title');
  panel.hidden = true;

  var head = el('div', 'ira-head');
  var hgroup = el('div');
  var h2 = el('h2', 'ira-title', 'IRA'); h2.id = 'ira-title';
  hgroup.appendChild(h2);
  hgroup.appendChild(el('p', 'ira-sub', 'Instron’s Resource Assistant'));
  var closeBtn = el('button', 'ira-close');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'Close IRA');
  closeBtn.textContent = '×';
  head.appendChild(hgroup); head.appendChild(closeBtn);

  var log = el('div', 'ira-log');
  log.setAttribute('role', 'log');
  log.setAttribute('aria-live', 'polite');
  log.setAttribute('aria-relevant', 'additions');

  var form = el('form', 'ira-form');
  var label = el('label', 'ira-sr', 'Describe what you want to improve or build'); label.htmlFor = 'ira-text';
  var input = el('textarea', 'ira-input');
  input.id = 'ira-text'; input.rows = 2; input.maxLength = 1200;
  input.placeholder = 'For example: we want to scale a solvent recovery process to a pilot skid';
  var send = el('button', 'ira-send', 'Send'); send.type = 'submit';
  form.appendChild(label); form.appendChild(input); form.appendChild(send);

  var note = el('p', 'ira-note', 'Automated guide. It suggests pages from this website only. Nothing you type is stored or sent; an engineer sees your brief only if you choose to email it. Please leave out confidential details.');

  panel.appendChild(head); panel.appendChild(log); panel.appendChild(form); panel.appendChild(note);
  root.appendChild(launcher); root.appendChild(panel);

  function scrollLog() { log.scrollTop = log.scrollHeight; }

  function say(text, who) {
    var m = el('p', 'ira-msg ' + (who === 'you' ? 'ira-you' : 'ira-bot'), text);
    if (who === 'you') m.setAttribute('aria-label', 'You: ' + text);
    log.appendChild(m); scrollLog(); return m;
  }

  function chips(list, onPick, ariaLabel) {
    var box = el('div', 'ira-chips');
    box.setAttribute('role', 'group');
    if (ariaLabel) box.setAttribute('aria-label', ariaLabel);
    list.forEach(function (c) {
      var b = el('button', 'ira-chip', c[0]); b.type = 'button';
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(box.querySelectorAll('button'), function (x) { x.disabled = true; });
        b.classList.add('is-picked');
        onPick(c);
      });
      box.appendChild(b);
    });
    log.appendChild(box); scrollLog();
    var first = box.querySelector('button'); if (first) first.focus();
    return box;
  }

  var EXAMPLES = [
    ['Scale a lab process to a pilot plant'],
    ['Recover a solvent from a waste stream'],
    ['Upgrade an old PLC or SCADA system'],
    ['Reduce downtime and track OEE'],
    ['Monitor energy and utility use'],
    ['Digital batch records and traceability']
  ];

  function greet() {
    log.textContent = '';
    say('Hello, I am IRA. What are you trying to improve or build? Describe it in your own words, or pick an example.');
    chips(EXAMPLES, function (c) { handle(c[0]); }, 'Examples');
  }

  function absUrl(u) { var x = new URL(u, location.href); x.search = ''; return x.href; }

  function brief() {
    var lines = ['Requirement described on the website:'];
    state.msgs.forEach(function (m) { lines.push('- ' + m); });
    var area = state.area ? AREA[state.area] : '';
    if (area || state.stage) lines.push('');
    if (area) lines.push('Area: ' + area);
    if (state.stage) lines.push('Stage: ' + state.stage);
    if (state.results.length) {
      lines.push('', 'Pages suggested by IRA:');
      state.results.forEach(function (x) { lines.push('- ' + x.e.title + ' (' + absUrl(x.e.url) + ')'); });
    }
    return lines.join('\n').slice(0, 2900);
  }

  function handoff() {
    say('I can carry your brief to the Contact form, where you add your details and open an email draft to our engineers. You can edit everything first, and nothing is sent until you send the email yourself.');
    var payload = { v: 1, brief: brief(), area: state.area ? AREA[state.area] : '', stage: state.stage };
    var row = el('div', 'ira-actions');
    if (onContactPage()) {
      var b = el('button', 'ira-btn ira-primary', 'Add my brief to the form'); b.type = 'button';
      b.addEventListener('click', function () { fillContact(payload); setOpen(false, true); });
      row.appendChild(b);
    } else {
      var a = el('a', 'ira-btn ira-primary', 'Continue to the Contact form');
      a.href = 'contact.html?ira=1' + BRIEF_KEY + encodeURIComponent(JSON.stringify(payload));
      row.appendChild(a);
    }
    log.appendChild(row); scrollLog();
    row.firstChild.focus();
  }

  function actions() {
    var row = el('div', 'ira-actions');
    var talk = el('button', 'ira-btn ira-primary', 'Discuss my requirement'); talk.type = 'button';
    talk.addEventListener('click', function () { row.remove(); handoff(); });
    var more = el('button', 'ira-btn', 'Add more detail'); more.type = 'button';
    more.addEventListener('click', function () { say('Add any detail, such as your process, scale, current stage or what you want to prove next.'); input.focus(); });
    var again = el('button', 'ira-btn', 'Start over'); again.type = 'button';
    again.addEventListener('click', function () { reset(); greet(); });
    row.appendChild(talk); row.appendChild(more); row.appendChild(again);
    log.appendChild(row); scrollLog();
  }

  function cards(list) {
    var box = el('div', 'ira-results');
    list.forEach(function (x) {
      var c = el('article', 'ira-card' + (x.e.type === 'case' ? ' ira-case' : ''));
      if (x.e.type === 'case') c.appendChild(el('p', 'ira-kicker', 'Related project'));
      var h = el('h3', 'ira-card-title');
      var a = el('a', null, x.e.title);
      a.href = x.e.url.replace(/^([^#]+)/, '$1?ira=1');
      h.appendChild(a); c.appendChild(h);
      c.appendChild(el('p', 'ira-reason', reasonFor(x)));
      if (x.e.summary) c.appendChild(el('p', 'ira-summary', x.e.summary));
      box.appendChild(c);
    });
    log.appendChild(box); scrollLog();
  }

  function findEntry(id) { for (var i = 0; i < entries.length; i++) if (entries[i].id === id) return entries[i]; return null; }

  // One-off requests (safety, careers, pricing, a person, company facts) are answered once and then
  // cleared, so a later message in the same conversation is matched on its own merits.
  function clearOneOffs() { Object.keys(META).forEach(function (k) { delete state.intents[k]; }); }

  function respond() {
    var I = state.intents, text = state.msgs.join(' ');
    var sig = solutionSignal(I);

    if (I.safety) {
      say('I cannot approve designs or give safety, code or certification decisions. Engineering sign-off is agreed for each project with a qualified engineer. This page explains how we handle process safety and sign-off, and our engineers can review your question directly.');
      var t = findEntry('trust-responsibility');
      state.results = t ? [{ e: t, s: 1, matched: ['safety'] }] : [];
      if (state.results.length) cards(state.results);
      clearOneOffs(); handoff(); return;
    }
    if (I.careers && !sig) {
      var c = findEntry('careers');
      say('It sounds like you are interested in working with us.');
      state.results = c ? [{ e: c, s: 1, matched: ['careers'] }] : [];
      if (state.results.length) cards(state.results);
      clearOneOffs(); actions(); return;
    }
    var wantsPerson = !!I.contact;
    if (!sig && !state.askedArea && !wantsPerson && !I.company && !I.location && !I.proof) {
      state.askedArea = true;
      say(Object.keys(I).some(function (k) { return INDUSTRY[k]; }) ?
        'Thanks. Which of these is closest to what you need?' :
        'Thanks. To point you to the right pages, which of these is closest to what you need?');
      chips([
        ['Build a pilot plant or process skid', { pilot: 1, skid: 1 }],
        ['Automate or upgrade plant controls', { automation: 1, modernize: 1 }],
        ['Use plant data: OEE, energy, traceability', { plantdata: 1, oee: 1 }],
        ['Engineering studies or design', { feasibility: 1, detailed: 1 }],
        ['Not sure yet', null]
      ], function (c) {
        say(c[0], 'you');
        if (c[1]) Object.keys(c[1]).forEach(function (k) { state.intents[k] = (state.intents[k] || 0) + c[1][k]; });
        else state.intents.contact = state.intents.contact || 0;
        respond();
      }, 'Type of need');
      return;
    }
    if (sig && !state.stage && !state.askedStage && !wantsPerson) {
      state.askedStage = true;
      say('Where is the project today?');
      chips([
        ['Idea or feasibility', 'Concept / feasibility'],
        ['Lab, pilot or demonstration', 'Pilot or demonstration'],
        ['Ready for detailed engineering', 'Detailed engineering'],
        ['New industrial plant or line', 'Industrial implementation'],
        ['Operating plant or upgrade', 'Operating plant / upgrade'],
        ['Skip this question', '']
      ], function (c) { say(c[0], 'you'); state.stage = c[1]; respond(); }, 'Project stage');
      return;
    }

    state.area = areaOf(I);
    var r = rank(entries, I, state.stage, text);
    var list = pick(r);
    if (!list.length && (I.proof || !sig)) {
      var gen = ['how-we-work-phase-1', 'case-studies', 'process-skid-plants'];
      if (I.proof) gen = ['case-studies', 'project-portfolio'];
      list = gen.map(findEntry).filter(Boolean).map(function (e) { return { e: e, s: 1, matched: I.proof ? ['proof'] : [] }; });
    }
    state.results = list;
    if (I.price) say('Pricing depends on scope, so an engineer agrees it with you. A Basic Engineering & Feasibility phase gives a Class 4 budgetary estimate before you commit to detailed design.');
    if (list.length) {
      say(list.length === 1 ? 'This page is the closest match to what you described:' : 'These pages are the closest match to what you described:');
      cards(list);
    } else {
      say('I could not match this to a specific page. An engineer can read your description and reply.');
    }
    clearOneOffs();
    if (wantsPerson) handoff(); else actions();
  }

  function handle(text) {
    text = String(text || '').trim().slice(0, 1200);
    if (text.length < 2) return;
    say(text, 'you');
    state.msgs.push(text);
    var d = detect(text);
    Object.keys(d).forEach(function (k) { state.intents[k] = (state.intents[k] || 0) + d[k]; });
    if (!state.stage) state.stage = detectStage(text);
    var wait = say('…');
    wait.setAttribute('aria-hidden', 'true');
    loadEntries().then(function () {
      wait.remove(); respond();
    }).catch(function () {
      wait.remove();
      say('Sorry, I could not load the page list just now. You can still reach our engineers through the Contact page.');
      var a = el('a', 'ira-btn ira-primary', 'Go to the Contact page'); a.href = 'contact.html?ira=1';
      var row = el('div', 'ira-actions'); row.appendChild(a); log.appendChild(row); scrollLog();
    });
  }

  function setOpen(open, quiet) {
    panel.hidden = !open;
    launcher.setAttribute('aria-expanded', String(open));
    root.classList.toggle('is-open', open);
    if (open) {
      if (!log.childNodes.length) greet();
      if (!quiet) input.focus();
      loadEntries().catch(function () {});
    } else if (!quiet) {
      launcher.focus();
    }
  }

  launcher.addEventListener('click', function () { setOpen(panel.hidden); });
  closeBtn.addEventListener('click', function () { setOpen(false); });
  panel.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.preventDefault(); setOpen(false); } });
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = input.value; input.value = '';
    handle(v);
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit', { cancelable: true })); }
  });

  function mount() {
    ensureCss();
    Array.prototype.forEach.call(document.querySelectorAll('a[href]'), carry);
    document.body.appendChild(root);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
