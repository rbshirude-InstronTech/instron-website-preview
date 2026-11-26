/* IRA, Instron's Resource Assistant, for the Instron Technologies website.
   A guided project map (three short steps) or a typed description, ending in a project brief:
   suggested first step, pages to read, related projects and inputs to prepare.
   Runs entirely in the visitor's browser and uses only the approved list in ira-content.json.
   The brief can be saved as PDF, copied, or carried into the Contact form.
   No cookies, no browser storage, no outside services; nothing is sent anywhere by this script.
   On by default (DEFAULT_ON below); ?ira=0 in the page address switches it off for that visit.
   v2.33: safety and information routes first, negation and corrections, one result model for chat
   and brief, track-specific first steps, evidence threshold for related projects.
   v2.34: several data-capture answers allowed (start from the least mature), optional "Also involves" area,
   on by default. */
(function () {
  'use strict';

  /* =====================================================================================
     Matching engine (no page access; tools/ira_test.js runs it in Node)
     ===================================================================================== */
  var INTENTS = {
    pilot: ['pilot and demonstration plants', [/\bpilot/, /\bdemonstrat/, /\bdemo (plant|unit|skid)/, /\blab(oratory)?[- ]scale/, /\bbench[- ]scale/, /\bmini[- ]?plant/, /\btest (rig|unit|bench|system)/, /\brigs?\b/, /\btrials?\b/]],
    skid: ['process skid plants', [/\bskids?\b/, /\bmodular\b/, /\bprocess (plant|system|package|unit)/, /\bpackaged? (unit|plant|system)/]],
    industrial_skid: ['industrial process skids', [/\b(production|industrial|commercial)[- ](scale|skid|plant|unit|duty)/, /\bdosing/, /\bfull[- ]scale/]],
    scaleup: ['technology scale-up', [/\bscale[- ]?up/, /\bscal(e|ing) (it|this|our|the)\b/, /\bcommerciali[sz]/, /\bfoak\b|\bfirst[- ]of[- ]a[- ]kind|\bfirst commercial/, /\blab to (pilot|plant|industrial)/, /\btrl\b/]],
    repeat: ['repeat deployment', [/\bnoak\b|\bnth[- ]of[- ]a[- ]kind/, /\brepeat (plant|unit|deployment|build|order|skid)s?\b/, /\breplicat/, /\bstandardi[sz]ed? (plant|skid|unit|design)/, /\bsecond (plant|unit|skid)\b/, /\bfleet of\b/]],
    separation: ['separation and solvent recovery', [/\bdistill/, /\bsolvents?\b/, /\bevaporat/, /\bseparat/, /\bmembrane/, /\bcrystalli[sz]/, /\bdryers?\b|\bdrying\b/, /\bfractionat/, /\bpurif/, /\bmethanol|\bethanol|\bacetone/]],
    extraction: ['extraction', [/\bextract/, /\bbotanical|\bnatural products?/, /\bsupercritical/]],
    reaction: ['reaction and synthesis', [/\breact(ion|ions|or|ors)\b/, /\bsynthes/, /\bcstr\b/, /\bpolymeri[sz]/, /\bhydrogenat/, /\besterif/]],
    carbon: ['carbon capture', [/\bco2\b|co₂/, /\bcarbon (capture|dioxide)/, /\bccus?\b/, /\bflue gas/, /\bamine/]],
    hydrogen: ['hydrogen and electrochemical systems', [/\bhydrogen/, /\belectroly[sz]/, /\bfuel cell/, /\bammonia/, /\bmethane/, /\bgraphene/, /\bpyrolysis/]],
    battery: ['battery recycling and critical minerals', [/\bbatter(y|ies)/, /\blithium|\bnickel|\bcobalt|\brare[- ]earth/, /\bcritical (mineral|material)/, /\bhydrometallurg|\bleach/, /\bblack mass/, /\bmining\b|\bminerals?\b/]],
    energy: ['energy transition', [/\benergy transition/, /\bclean ?tech/, /\bdecarboni[sz]/, /\brenewable/, /\bbiofuel|\bbiogas|\bsaf\b/]],
    research: ['research and technology development', [/\bresearch/, /\buniversit/, /\binstitute/, /\bacademi/, /\br ?& ?d\b|\br and d\b/, /\bstart[- ]?up\b/, /\btechnology developer/, /\bexperiment/]],
    automation: ['industrial automation and controls', [/\bplcs?\b/, /\bscada/, /\bhmis?\b/, /\bdcs\b/, /\bautomat/, /\bcontrols?\b/, /\bcontrol (system|panel|logic|philosophy)/, /\binstrument/, /\be ?& ?i\b|\belectrical and instrumentation/, /\bvfds?\b|\bdrives\b/, /\bsensors?\b/, /\bpid\b|\bloop tuning/, /\binterlocks?\b/]],
    modernize: ['brownfield modernization', [/\bupgrad/, /\bobsole/, /\blegacy/, /\bold (plc|scada|system|control|panel|hmi|dcs)/, /\bmigrat/, /\bmoderni[sz]/, /\bretrofit/, /\bend[- ]of[- ](life|support)/, /\breplac\w* (the |our |an? )?(old )?(plc|scada|hmi|dcs|panel|control)/, /\bbrownfield/, /\bs5\b|\bs7[- ]?300|\bplc[- ]?5\b|\bslc ?500/]],
    batch: ['batch and recipe control', [/\bbatch(es|ing)?\b/, /\brecipes?\b/, /\bs88\b|\bisa[- ]?88/, /\bformulat/, /\bmaterial (movement|transfer|addition)/, /\bsequenc/]],
    cip: ['clean-in-place', [/\bcip\b/, /\bclean[- ]in[- ]place/, /\bsip\b|\bsteam[- ]in[- ]place/, /\bsanitary|\bhygienic/]],
    panels: ['control panels', [/\bcontrol panels?\b/, /\bpanel (build|design|shop)/, /\bul ?508a|\bcsa\b|\bce mark/, /\bmcc\b/]],
    oee: ['production visibility and OEE', [/\boee\b/, /\bdowntime/, /\bproduction (target|visibility|loss|losses|report|tracking)/, /\bthroughput/, /\bplan (vs|versus) actual/, /\bavailability\b/, /\bscrap\b|\breject/, /\bproductivity/, /\bshift reports?/, /\bbottleneck/, /\bcycle time/, /\bmachine (performance|status|monitoring)/, /\blosses\b|\bloss analysis/]],
    utility: ['utility and energy monitoring', [/\benergy (use|usage|consumption|monitor\w*|costs?|bills?)/, /\belectricity/, /\bpower (consumption|use|usage|bills?)/, /\bkwh\b/, /\butilit(y|ies)/, /\bcompressed air/, /\bwater (use|usage|consumption)/, /\bsteam (use|usage|consumption)/, /\b(sub[- ]?)?meters?\b|\bmetering/, /\bconsumption/]],
    trace: ['traceability and digital records', [/\btraceab/, /\bgenealog/, /\bbatch (records?|history|reports?)/, /\bpaperless|\bpaper (records|forms|logs)/, /\bdigital (forms|records|logbook)/, /\bpasteuri[sz]/, /\bhaccp/, /\brecalls?\b/]],
    plantdata: ['PlantON plant data', [/\bplant ?on\b/, /\bdashboards?/, /\bkpis?\b/, /\b(plant|production|machine|process) data/, /\bvisibility/, /\breal[- ]time (data|monitor\w*|view)/, /\biiot|\biot\b|\bindustry 4/, /\bhistorian/, /\bmes\b/, /\bmis\b|\bdaily reports?/, /\bdigital factory|\bdigiti[sz]/, /\btrends?\b/]],
    compliance: ['validation and compliance', [/\b21 ?cfr|\bpart 11/, /\bgamp/, /\bc?gmp\b/, /\bvalidat/, /\biq\b|\boq\b/, /\baudit trails?/, /\bcompliance reports?/]],
    feasibility: ['basic engineering and feasibility', [/\bfeasib/, /\bbasic engineering/, /\bconcept(ual)? (design|study|engineering)/, /\bfeed\b(?! (stream|rate|material|stock))/, /\bpfds?\b|\bprocess flow diagram/, /\bmass balance/, /\bcost estimate|\bbudget(ary)? (estimate|price|quote|number)/, /\bdesign basis/]],
    detailed: ['detailed engineering', [/\bdetailed (engineering|design|drawings)/, /\bp ?& ?ids?\b|\bp and ids?\b/, /\bga drawings?|\bgeneral arrangement/, /\b3d model/, /\bengineering package|\bdrawings\b/, /\bdatasheets?/]],
    build: ['integrated design and build', [/\bdesign (and|&) build/, /\bfabricat/, /\bturnkey/, /\bfat\b|\bfactory acceptance/, /\bcommission/, /\binstallation/, /\bsat\b|\bsite acceptance/]],
    hazop: ['HAZOP and process safety studies', [/\bhazop/, /\bhazid/, /\bprocess safety (study|review)/]],
    food: ['food, beverage and dairy', [/\bfood/, /\bbeverages?\b|\bdrinks?\b|\bbrew|\bjuices?\b/, /\bdairy|\bmilk|\bcheese|\byogh?urt|\bice cream/, /\bchocolate|\bconfection|\bbakery|\bsnacks?\b/]],
    pharma: ['pharma and life sciences', [/\bpharma/, /\bapis?\b|\bactive (pharmaceutical )?ingredients?/, /\bbiotech|\blife sciences?/, /\bvaccin|\badjuvant/, /\bnutraceutical/, /\bmedical|\bhealthcare/]],
    chemical: ['chemicals, refining and consumer products', [/\bchemicals?\b/, /\brefin(ery|eries|ing)/, /\bpetrochem|\boil (and|&) gas/, /\bspecialty|\bpolymers?\b|\bresins?\b|\bcoatings?\b/, /\bpersonal[- ]care|\bcosmetic|\bdetergent|\bcleaning products?|\bconsumer products?/, /\breactors?\b|\bcstr/]],
    manufacturing: ['industrial manufacturing', [/\bmanufactur\w* (line|plant|floor)/, /\bassembly/, /\bdie[- ]?cast/, /\bpaint ?shop|\bpaint line/, /\bautomotive|\bauto parts|\balloy wheels?/, /\bcnc\b|\bmachining|\bmachine shop/, /\bdiscrete/, /\bpresses\b|\bmou?lding/]],
    /* one-off routes: answered directly, never turned into a project */
    proof: ['project references', [/\bcase stud/, /\breferences?\b/, /\bexamples?\b/, /\bsimilar (projects?|work)/, /\bexperience/, /\bhave you (ever )?(done|built|worked|delivered)/, /\bportfolio/, /\bpast projects?/]],
    company: ['about the company', [/\bwho are you|\babout (you|instron|the company|your company)/, /\bcompany (profile|overview)/, /\bleadership|\bfounders?\b/]],
    location: ['offices and regional presence', [/\boffices?\b/, /\bwhere are you( based| located)?/, /\blocations?\b/, /\b(street|postal|mailing) address/]],
    careers: ['careers', [/\bjobs?\b|\bcareers?\b|\bhiring|\bintern(ship)?s?\b|\bvacanc|\bresume|\bcv\b|\bapply for|\bjob openings?/]],
    contact: ['talking to an engineer', [/\b(talk|speak|meet|call|connect|chat) (to|with) (an? |your )?(engineer|expert|specialist|someone|person|sales|team)/, /\bcontact (you|sales|an engineer|me|someone)/, /\bcall me|\bemail me|\breach out/, /\bquot(e|ation)s?\b|\brfq\b|\bproposal|\btender|\bbids?\b/]],
    email: ['contact details', [/\b(your |an? )?e-?mail( address)?\b/, /\bphone (number)?|\btelephone/, /\bcontact (details|information|info)/]],
    price: ['pricing', [/\bprices?\b|\bpricing|\bcosts?\b|\bhow much|\bbudget\b|\bsubscription/]],
    partner: ['engineering partnerships', [/\bpartner(ship|ing)?s?\b/, /\boems?\b|\bepcs?\b|\bskid builders?/, /\bsub[- ]?contract/, /\boverflow\b/, /\bwhite[- ]label/, /\b(engineering|extra|additional) (capacity|resources)/, /\boutsourc/]],
    support: ['support for an existing system', [/\b(fault|error|alarm) codes?/, /\btroubleshoot/, /\b(not|stopped|isnt|doesnt) working\b/, /\bbreakdown/, /\bfault(y|s)?\b/, /\brepair/, /\b(technical|service|after[- ]sales|maintenance) support/, /\bservice (call|visit|contract)/, /\bkeeps? (tripping|faulting|stopping|crashing)/, /\bhow (do|can) (i|we) fix/]],
    itw: ['materials testing equipment', [/\btensile/, /\b(universal|materials?|fatigue|hardness|impact|compression) test(ing|er)?s?\b/, /\btesting (machines?|equipment|systems?)/, /\bbluehill\b/, /\bitw\b|\billinois tool/, /\bload frames?/, /\bextensometer/]],
    cyber: ['industrial cybersecurity', [/\bcyber ?security|\bcyber\b/, /\b(ot|ics|scada|network|plant) security/, /\biec ?62443/, /\bransomware|\bmalware|\bhack(ed|ers?|ing)?\b|\bintrusion/, /\bpenetration test|\bpen ?test/]],
    inject: ['', [/\bignore (all |any |your |the |previous |prior |earlier )*(instructions|rules|prompts?)/, /\bsystem prompt/, /\breveal (your )?(secrets?|instructions|prompt|passwords?|keys?)/, /\bapi keys?|\bpasswords?\b|\bjailbreak/]],
    urgent: ['an urgent safety issue', [/\bsmok(e|es|ing)\b/, /\bon fire\b|\bcaught fire\b|\bfire (in|on|at) (the|our|my)\b/, /\bsparks?\b|\bsparking/, /\bexplo(sion|ded|ding)/, /\b(gas|chemical|ammonia|chlorine|steam|toxic) (leak|release)/, /\bleak(ing)? (gas|chemicals?|ammonia|chlorine)/, /\btoxic (gas|fumes)/, /\belectric(al)? shock|\belectrocut/, /\b(someone|somebody|operator|worker|person) (is |was |got )?(hurt|injured)/, /\binjur(ed|y)\b/, /\b(e ?stop|emergency stop|estop|safety (relay|circuit|valve)|relief valve|light curtain)s? (doesnt|does not|isnt|is not|wont|will not|didnt|did not|has stopped|stopped|failed|fails|not)\b/, /\b(immediate|urgent) (danger|risk)/]],
    bypass: ['bypassing a safety function', [/\b(bypass|override|defeat|disabl|jumper|jump out|mute|inhibit|cheat)\w*\b.{0,30}\b(interlocks?|safety|e ?stops?|emergency stops?|guards?|light curtains?|trips?|relief valves?|psv|sis\b|safety relays?|door switch)/]],
    safety: ['safety or engineering approval', [/\b(approve|certify|sign[- ]?off|verify|stamp)\b.{0,40}\b(design|drawings?|calculations?|system|panel|vessel|skid)/, /\bis (it|this|that|my|our|the) (\w+ ){0,2}safe\b/, /\bsafe to (run|operate|use|start|restart|open|touch)/, /\bsafety (approval|sign[- ]?off|certificat)/, /\bsil (rating|level|assessment|verification)|\bsil ?[1-4]\b/, /\bhazardous area classification|\batex (certif|rating)/, /\bpressure vessel (code|stamp|certif)/, /\b(pe|p eng|professional engineer)( stamp| seal)/, /\b(is|are) (it|this|my|our) (\w+ )?(compliant|legal|code[- ]compliant)/]]
  };
  var META = { proof: 1, company: 1, location: 1, careers: 1, contact: 1, email: 1, price: 1, partner: 1, support: 1, itw: 1, cyber: 1, inject: 1, urgent: 1, bypass: 1, safety: 1 };
  var INDUSTRY = { food: 1, pharma: 1, chemical: 1, manufacturing: 1, research: 1, energy: 1 };
  // track and stage words: they shape the ranking but are not, on their own, evidence of a matching project
  var GENERIC = { skid: 1, pilot: 1, industrial_skid: 1, scaleup: 1, build: 1, feasibility: 1, detailed: 1, hazop: 1 };
  var AREA = { // matches the Contact form "Area of interest" options
    P: 'Process skid / pilot plant', A: 'Automation & controls', D: 'PlantON / industrial data',
    C: 'Engineering collaboration', O: 'Other technical enquiry'
  };
  var AREA_OF = {
    pilot: 'P', skid: 'P', industrial_skid: 'P', scaleup: 'P', repeat: 'P', separation: 'P', extraction: 'P', reaction: 'P',
    carbon: 'P', hydrogen: 'P', battery: 'P', feasibility: 'P', detailed: 'P', build: 'P', hazop: 'P',
    automation: 'A', modernize: 'A', batch: 'A', cip: 'A', panels: 'A', compliance: 'A',
    oee: 'D', utility: 'D', trace: 'D', plantdata: 'D'
  };
  var STAGES = [ // first match wins; labels match the Contact form "Project stage" options
    ['Detailed engineering', [/\bdetailed (engineering|design|drawings)/, /\bp ?& ?ids?\b/, /\bready to build|\bissued for construction|\bready for (fabrication|procurement)/]],
    ['Operating plant / upgrade', [/\bexisting\b/, /\brunning\b/, /\boperating (plant|line|site)/, /\bupgrad/, /\bretrofit/, /\blegacy/, /\bold (plc|scada|system|control|panel|hmi|machines?|line)/, /\bcurrent(ly)? (plant|system|line|setup)/, /\bbrownfield/, /\bdowntime/, /\bour (plant|line|lines|machines|factory|site)\b/, /\bend[- ]of[- ](life|support)|\bobsole/]],
    ['Industrial implementation', [/\bcommercial/, /\bfull[- ]scale/, /\bindustrial[- ]scale/, /\bproduction[- ](line|plant|scale)/, /\bnew (plant|line|facility|factory)/, /\bgreenfield/, /\bnoak\b|\brepeat (plant|unit)|\breplicat|\bsecond plant/]],
    ['Pilot or demonstration', [/\bpilot/, /\bdemonstrat/, /\blab(oratory)?\b/, /\bbench/]],
    ['Concept / feasibility', [/\bfeasib/, /\bconcept/, /\bidea\b/, /\bearly stage/, /\bexplor/, /\bstudy\b/, /\bbudget/]]
  ];
  var OLD_WORK = /\b(upgrad|legacy|old (plc|scada|hmi|dcs|system|control)|retrofit|replac\w* (the |our |an? )?(old )?(plc|scada|hmi|dcs|panel|control)|migrat|obsole)/;
  var NEW_WORK = /\bnew (plant|line|skid|facility|factory|controls?)\b|\bgreenfield/;
  var READY = /\bready to build|\b(design|drawings) (is |are )?(complete|ready|approved|finished)|\bdetailed (drawings|design) (is |are )?(ready|complete)|\bissued for construction|\bifc drawings|\bready for (fabrication|procurement)|\bdetailed drawings ready/;
  var NEGATOR = /\b(?:(?:do|does|did) not|dont|doesnt|didnt|no longer|not|never) (?:need|want|require|looking for|interested in|planning|asking (?:about|for))\b|\bno need for\b|\bnot (?:a|an|any)\b|\binstead of\b|\brather than\b|\bother than\b|\bexcept\b|\bwithout (?:a|an|any)\b/g;
  var PAST = /\b(after|following|beyond|post)( the| a| our| successful| a successful)? (pilot|demo|demonstration)( (plant|phase|stage|unit|campaign|trials?))?/g;
  var CORRECTION = /\b(actually|instead|correction|i meant|scratch that|change of plan|on second thought|not anymore|only interested in|just interested in|forget (that|the))\b/;

  function norm(t) { return (' ' + String(t || '').toLowerCase().replace(/[’']/g, '').replace(/\s+/g, ' ') + ' '); }
  function hitsIn(t) {
    var hits = {};
    Object.keys(INTENTS).forEach(function (k) {
      var n = 0;
      INTENTS[k][1].forEach(function (re) { re.lastIndex = 0; if (re.test(t)) n++; });
      if (n) hits[k] = Math.min(n, 3);
    });
    return hits;
  }
  function stageIn(t) {
    for (var i = 0; i < STAGES.length; i++) for (var j = 0; j < STAGES[i][1].length; j++) if (STAGES[i][1][j].test(t)) return STAGES[i][0];
    return '';
  }

  /* Read one message: what is asked for, what is ruled out ("not a pilot plant"), the stage. */
  function analyse(text) {
    var t = norm(text), neg = '', m;
    t = t.replace(PAST, function (s) { return new Array(s.length + 1).join(' '); });
    NEGATOR.lastIndex = 0;
    while ((m = NEGATOR.exec(t))) {
      var end = m.index + m[0].length, rest = t.slice(end);
      var stop = rest.search(/[.;!?,]| but | only | just | however | we need | we want /);
      var spanEnd = stop < 0 ? t.length : end + stop;
      neg += ' ' + t.slice(end, spanEnd) + ' ';
      t = t.slice(0, m.index) + new Array(spanEnd - m.index + 1).join(' ') + t.slice(spanEnd);
      NEGATOR.lastIndex = m.index + 1;
    }
    var hits = hitsIn(t), negHits = neg ? hitsIn(neg) : {}, negated = {};
    Object.keys(negHits).forEach(function (k) { if (!hits[k] && !META[k]) negated[k] = 1; });
    var mixed = OLD_WORK.test(t) && NEW_WORK.test(t);
    return { hits: hits, negated: negated, stage: mixed ? '' : stageIn(t), mixed: mixed, ready: READY.test(t) };
  }
  function detect(text) { return analyse(text).hits; }
  function detectStage(text) { return analyse(text).stage; }

  function areaScores(intents) {
    var s = { P: 0, A: 0, D: 0 };
    Object.keys(intents).forEach(function (k) { if (AREA_OF[k]) s[AREA_OF[k]] += intents[k]; });
    return s;
  }
  function areaOf(intents) {
    var s = areaScores(intents), best = '', v = 0;
    Object.keys(s).forEach(function (a) { if (s[a] > v) { v = s[a]; best = a; } });
    return best;
  }
  function solutionSignal(intents) {
    var n = 0;
    Object.keys(intents).forEach(function (k) { if (!META[k] && !INDUSTRY[k]) n += intents[k]; });
    return n;
  }
  // the visitor's specific needs: a broad word drops out when a narrower one in the same family is there
  function refineDirect(d) {
    var out = {};
    Object.keys(d).forEach(function (k) { if (!GENERIC[k] && !META[k] && !INDUSTRY[k]) out[k] = d[k]; });
    if (out.automation && (out.modernize || out.batch || out.cip || out.panels || out.compliance)) delete out.automation;
    if (out.plantdata && (out.oee || out.utility || out.trace)) delete out.plantdata;
    return out;
  }

  var STAGE_BOOST = {
    'Concept / feasibility': { 'how-we-work-phase-1': 2.5, 'technology-scale-up': 0.5 },
    'Pilot or demonstration': { 'pilot-demonstration-plants': 1.5, 'insights-lab-to-pilot-to-industrial': 0.5 },
    'Detailed engineering': { 'how-we-work-phase-2': 2.5 },
    'Industrial implementation': { 'industrial-process-skids': 1.5, 'how-we-work-phase-3': 1.5, 'technology-scale-up': 0.5 },
    'Operating plant / upgrade': { 'brownfield-automation-modernization': 1, 'planton-digital-factory': 0.5 }
  };

  /* Score every approved entry. Returns {pages:[...], cases:[...]} sorted, each with matched need keys. */
  function rank(entries, intents, stage, text, metaWanted) {
    var t = norm(text);
    metaWanted = metaWanted || {};
    var scored = [];
    entries.forEach(function (e) {
      if (!e || !e.url || !/^[a-z0-9-]+\.html(#[a-z0-9-]+)?$/.test(e.url)) return; // only our own pages
      var s = 0, matched = [], kw = false;
      Object.keys(e.tags || {}).forEach(function (k) {
        if (metaWanted[k]) { s += e.tags[k] * 1.5; matched.push(k); return; }
        if (!intents[k]) return;
        s += e.tags[k] * intents[k]; matched.push(k);
      });
      (e.keywords || []).forEach(function (w) { if (t.indexOf(String(w).toLowerCase()) >= 0) { s += 1.5; kw = true; } });
      if (stage && STAGE_BOOST[stage] && STAGE_BOOST[stage][e.id] && s > 0) s += STAGE_BOOST[stage][e.id];
      if (stage && STAGE_BOOST[stage] && STAGE_BOOST[stage][e.id] && s === 0 && solutionSignal(intents) > 0 && e.type === 'phase') s += STAGE_BOOST[stage][e.id] * 0.8;
      if (e.type === 'company' && !Object.keys(e.tags || {}).some(function (k) { return metaWanted[k]; })) s = 0;
      if (e.type === 'contact') s = 0; // the Contact route is offered as an action, not a card
      if (e.type === 'industry' && solutionSignal(intents) > 0) s *= 0.75;
      if (e.type === 'insight') s *= 0.6;
      if (s > 0) scored.push({ e: e, s: s, matched: matched, kw: kw });
    });
    scored.sort(function (a, b) { return b.s - a.s; });
    return {
      pages: scored.filter(function (x) { return x.e.type !== 'case'; }),
      cases: scored.filter(function (x) { return x.e.type === 'case'; })
    };
  }

  /* Card reason: the visitor's own needs first, strongest first. */
  function reasonFor(x, direct) {
    direct = direct || {};
    var keys = x.matched.filter(function (k) { return INTENTS[k] && INTENTS[k][0]; });
    keys.sort(function (a, b) {
      var da = direct[a] ? 1 : 0, db = direct[b] ? 1 : 0;
      if (da !== db) return db - da;
      return ((direct[b] || 0) * 10 + (x.e.tags[b] || 0)) - ((direct[a] || 0) * 10 + (x.e.tags[a] || 0));
    });
    var labels = keys.slice(0, 2).map(function (k) { return INTENTS[k][0]; });
    if (x.also) return 'Also involved: ' + TRACKS[x.also].title.toLowerCase() + '.';
    if (x.e.type === 'case') {
      if (x.adjacent) return labels.length ? 'Not the same application; related work on ' + labels.join('; ') + '.' : 'Related work, not the same application.';
      return labels.length ? 'A completed project involving ' + labels.join('; ') + '.' : 'A completed project matching what you described.';
    }
    return labels.length ? 'Relevant to: ' + labels.join('; ') + '.' : 'Related to what you described.';
  }

  /* =====================================================================================
     Map options (site wording). Every choice maps to need tags the page list uses.
     ===================================================================================== */
  var TRACKS = {
    process: { title: 'Process systems and scale-up', line: 'Pilot, demonstration and industrial process skids', page: 'process-skid-plants', area: 'P', tags: { skid: 1 } },
    automation: { title: 'Controls and automation', line: 'New controls, upgrades, batch and validated systems', page: 'industrial-automation', area: 'A', tags: { automation: 1 } },
    data: { title: 'Plant data with PlantON', line: 'OEE, energy, traceability and production visibility', page: 'planton-digital-factory', area: 'D', tags: { plantdata: 1 } }
  };
  var PATH = [
    { id: 'lab', label: 'Lab or concept', hint: 'It works at lab scale, or it is still an idea', stage: 'Concept / feasibility', tags: { scaleup: 1 } },
    { id: 'pilot', label: 'Pilot', hint: 'Proving the process at small scale, batch or continuous', stage: 'Pilot or demonstration', tags: { pilot: 2 } },
    { id: 'demo', label: 'Demonstration', hint: 'A larger unit to prove performance and economics', stage: 'Pilot or demonstration', tags: { pilot: 2, scaleup: 1 } },
    { id: 'foak', label: 'First commercial plant', hint: 'Moving a proven process into industrial production', stage: 'Industrial implementation', tags: { industrial_skid: 2, scaleup: 1 } },
    { id: 'repeat', label: 'Repeat or standard plant', hint: 'Another unit of a design that already runs', stage: 'Industrial implementation', tags: { industrial_skid: 2, repeat: 2 } },
    { id: 'operating', label: 'Operating plant', hint: 'Expanding or improving a running plant', stage: 'Operating plant / upgrade', tags: { industrial_skid: 1 } }
  ];
  var PROCESS = [
    { id: 'sep', label: 'Separation or solvent recovery', tags: { separation: 2 } },
    { id: 'react', label: 'Reaction or synthesis', tags: { reaction: 2, chemical: 1 } },
    { id: 'extract', label: 'Extraction', tags: { extraction: 2 } },
    { id: 'carbon', label: 'Carbon capture', tags: { carbon: 2 } },
    { id: 'hydrogen', label: 'Hydrogen or electrochemical', tags: { hydrogen: 2 } },
    { id: 'battery', label: 'Battery or critical minerals', tags: { battery: 2 } },
    { id: 'food', label: 'Food, beverage or dairy', tags: { food: 2 } },
    { id: 'pharma', label: 'Pharma or API', tags: { pharma: 2 } },
    { id: 'research', label: 'A research program', tags: { research: 2 } },
    { id: 'other', label: 'Something else', tags: {}, only: true }
  ];
  var NEEDS = {
    automation: [
      { id: 'legacy', label: 'Replace or upgrade an old PLC, SCADA or HMI', tags: { modernize: 3, automation: 1 }, svc: 'modernize' },
      { id: 'newline', label: 'Controls for a new line, skid or plant', tags: { automation: 3 }, svc: 'new' },
      { id: 'batch', label: 'Batch and recipe control', tags: { batch: 3 }, svc: 'batch' },
      { id: 'validated', label: 'Validated systems (GAMP 5, 21 CFR Part 11)', tags: { compliance: 3 }, svc: 'batch' },
      { id: 'panels', label: 'Control panels and electrical design', tags: { panels: 3 }, svc: 'ei' },
      { id: 'cip', label: 'Clean-in-place automation', tags: { cip: 3 }, svc: 'new' }
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
  var AUTO_TODAY = [
    { id: 'none', label: 'Little or no documentation' },
    { id: 'docs', label: 'Drawings, I/O lists or a control philosophy' },
    { id: 'spec', label: 'A detailed specification, ready to implement' },
    { id: 'unsure', label: 'Not sure' }
  ];
  var DATA_TODAY = [ // start: which PlantON deployment steps are the likely starting point
    { id: 'manual', label: 'Manual logs or spreadsheets', start: [0, 1] },
    { id: 'partial', label: 'Some PLC or meter data, not connected', start: [1] },
    { id: 'system', label: 'A historian or MES is already in place', start: [2] },
    { id: 'unsure', label: 'Not sure', start: [0, 1], only: true }
  ];
  var SEC_TITLE = { 'phase-1': 'Suggested first step', 'phase-2': 'Suggested first step', 'phase-3': 'Suggested first step',
    'auto-modernize': 'Suggested approach', 'auto-services': 'Work packages to discuss', 'planton-deploy': 'Suggested approach' };
  var NOTE = {
    phaseUnstated: 'Suggested from the stage you chose. The engineering that exists today was not stated, so an engineer confirms the right starting point after seeing what you have.',
    mixed: 'This covers both an existing system and new controls. An engineer will confirm which comes first, or plan them as two workstreams.',
    safety: 'Your note raises a safety, approval or security question. IRA cannot answer it; a qualified engineer reviews it with you. The suggested step and related projects are left out until then.',
    noCase: 'No closely matching public project for this combination. An engineer can discuss relevant references with you.',
    start: 'Highlighted: the likely starting point, based on how the figures are captured today.',
    startUnknown: 'Highlighted: the usual starting point. A short review of your data sources confirms it.',
    panels: 'We provide control panels with UL 508A, CSA or CE approval; the applicable standard and scope are confirmed for each project.'
  };

  /* =====================================================================================
     Brief model: one result object for the map, the chat cards and the brief
     ===================================================================================== */
  var data = null;
  function setData(d) { data = d || { entries: [] }; }
  var BASE_HREF = (typeof location !== 'undefined' && location.href) || 'https://instrontechnologies.com/';
  function find(list, id) { list = list || []; for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i]; return null; }
  function entry(id) { var es = (data && data.entries) || []; for (var i = 0; i < es.length; i++) if (es[i].id === id) return es[i]; return null; }
  function addTags(into, tags) { Object.keys(tags || {}).forEach(function (k) { into[k] = (into[k] || 0) + tags[k]; }); }
  function absUrl(u) { var x = new URL(u, BASE_HREF); x.search = ''; return x.href; }
  function joinList(a) { return a.length < 2 ? (a[0] || '') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1]; }
  var PAGE_TYPES = /^(solution|application|industry|insight)$/;

  function build(spec) {
    var r = rank(data.entries, spec.tags, spec.stage, spec.text);
    var direct = spec.direct || {}, dkeys = Object.keys(direct).sort(function (a, b) { return direct[b] - direct[a]; });
    var pages = [];
    r.pages.forEach(function (x) {
      if (pages.length < 3 && x.s >= 2 && PAGE_TYPES.test(x.e.type) && !pages.some(function (y) { return y.e.id === x.e.id; })) pages.push(x);
    });
    // every specific need gets its own page when the site has one (e.g. solvent recovery next to pilot plants)
    var covers = function (x, k) { return (x.e.tags[k] || 0) >= 2; };
    dkeys.forEach(function (k) {
      if (pages.some(function (x) { return covers(x, k); })) return;
      var cand = r.pages.filter(function (x) { return PAGE_TYPES.test(x.e.type) && covers(x, k) && pages.indexOf(x) < 0; })
        .sort(function (a, b) { return (b.e.tags[k] - a.e.tags[k]) || (b.s - a.s); })[0];
      if (!cand) return;
      if (pages.length < 3) { pages.push(cand); return; }
      for (var i = pages.length - 1; i >= 0; i--) {
        var only = dkeys.some(function (d) { return covers(pages[i], d) && !pages.some(function (q, j) { return j !== i && covers(q, d); }); });
        if (!only) { pages[i] = cand; return; }
      }
    });
    // related projects need evidence: one of the visitor's own needs, or a named match
    var used = {}, strong = [], weak = [];
    pages.forEach(function (x) { if (x.e.image) used[x.e.image[0]] = 1; });
    r.cases.forEach(function (x) {
      if (x.s < 2) return;
      var ok = x.kw || x.matched.some(function (k) { return direct[k]; });
      (ok ? strong : weak).push(x);
    });
    var cases = [];
    var take = function (x, adjacent) {
      var e2 = x.e;
      if (x.e.image && used[x.e.image[0]]) { e2 = {}; Object.keys(x.e).forEach(function (k) { e2[k] = x.e[k]; }); e2.image = null; }
      else if (x.e.image) used[x.e.image[0]] = 1;
      cases.push({ e: e2, s: x.s, matched: x.matched, kw: x.kw, adjacent: !!adjacent });
    };
    strong.slice(0, 2).forEach(function (x) { take(x); });
    if (!cases.length && weak.length && weak[0].s >= 3) take(weak[0], true);
    if (!pages.length) { var d0 = entry(TRACKS[spec.track].page); if (d0) pages.push({ e: d0, s: 1, matched: [] }); }
    (spec.also || []).forEach(function (t) {                              // "Also involves": that area's main page
      var e1 = entry(TRACKS[t].page);
      if (e1 && !pages.some(function (x) { return x.e.id === e1.id; })) pages.push({ e: e1, s: 1, matched: [], also: t });
    });
    // inputs to prepare: the two best pages that have a list, merged without repeats
    var pool = pages.map(function (x) { return x.e; }).concat(r.pages.map(function (x) { return x.e; }), [entry(TRACKS[spec.track].page)]);
    var srcs = [], items = [], seen = {};
    for (var i = 0; i < pool.length && srcs.length < 2; i++) {
      var e = pool[i];
      if (!e || !e.prepare || !e.prepare.length || srcs.some(function (s) { return s.url === e.url; })) continue;
      srcs.push({ title: e.title, url: e.url });
      e.prepare.forEach(function (q) { var k = q.toLowerCase(); if (!seen[k] && items.length < 6) { seen[k] = 1; items.push(q); } });
    }
    if (!srcs.length && data.prepare_default) { srcs.push({ title: 'How We Work', url: data.prepare_default.source }); items = data.prepare_default.items.slice(0, 6); }
    var phase = data.phases && data.phases[spec.phaseId];
    if (phase && spec.order && phase.keys) { // automation: the visitor's work packages first
      var idx = phase.deliverables.map(function (_, i) { return i; });
      idx.sort(function (a, b) {
        var pa = spec.order.indexOf(phase.keys[a]), pb = spec.order.indexOf(phase.keys[b]);
        return (pa < 0 ? 99 : pa) - (pb < 0 ? 99 : pb) || a - b;
      });
      var p2 = {}; Object.keys(phase).forEach(function (k) { p2[k] = phase[k]; });
      p2.deliverables = idx.map(function (i) { return phase.deliverables[i]; });
      p2.highlight = idx.map(function (i, n) { return spec.order.indexOf(phase.keys[i]) >= 0 ? n : -1; }).filter(function (n) { return n >= 0; });
      phase = p2;
    }
    if (phase && spec.start) { var p3 = {}; Object.keys(phase).forEach(function (k) { p3[k] = phase[k]; }); p3.highlight = spec.start; phase = p3; }
    var b = {
      track: spec.track, area: TRACKS[spec.track].area, stage: spec.stage || '', told: spec.told, headline: spec.headline,
      phase: phase, phaseId: spec.phaseId, phaseNote: spec.phaseNote || '', startNote: spec.startNote || '',
      notices: spec.notices || [], pages: pages, cases: cases, noCase: !strong.length, direct: direct,
      prepare: items.length ? { items: items, sources: srcs } : null, safety: !!spec.safety, urgent: !!spec.urgent, date: new Date()
    };
    if (b.safety) { b.phase = null; b.cases = []; b.noCase = false; }
    return b;
  }

  function cleanNotes(text) {
    var a = analyse(text), tags = {}, direct = {};
    Object.keys(a.hits).forEach(function (k) { if (!META[k]) { tags[k] = a.hits[k]; direct[k] = a.hits[k]; } });
    return { a: a, tags: tags, direct: direct };
  }

  function briefFromMap(sel) {
    var tr = TRACKS[sel.track];
    if (!tr) return null;
    var tags = {}, direct = {}, stage = '', told = [['Area', tr.title]], notices = [];
    addTags(tags, tr.tags);
    var p = sel.track === 'process' ? find(PATH, sel.path) : null;
    if (p) { addTags(tags, p.tags); stage = p.stage; told.push(['Stage', p.label]); }
    var inList = function (list, ids) { return (list || []).filter(function (x) { return (ids || []).indexOf(x.id) >= 0; }); }; // list order, not click order
    var procs = sel.track === 'process' ? inList(PROCESS, sel.process) : [];
    procs.forEach(function (x) { addTags(tags, x.tags); addTags(direct, x.tags); });
    if (procs.length) told.push(['Process', procs.map(function (x) { return x.label; }).join('; ')]);
    var needs = inList(NEEDS[sel.track], sel.need);
    needs.forEach(function (x) { addTags(tags, x.tags); addTags(direct, x.tags); });
    if (needs.length) told.push(['Main need', needs.map(function (x) { return x.label; }).join('; ')]);
    var has = function (id) { return needs.some(function (x) { return x.id === id; }); };
    var mixed = false;
    if (sel.track === 'automation') {
      mixed = has('legacy') && has('newline');
      stage = mixed ? '' : has('legacy') ? 'Operating plant / upgrade' : has('newline') ? 'Industrial implementation' : '';
      if (mixed) { told.push(['Stage', 'Existing system and new controls']); notices.push(NOTE.mixed); }
    }
    if (sel.track === 'data') stage = 'Operating plant / upgrade';
    var ind = sel.track !== 'process' ? find(INDUSTRIES, sel.industry) : null;
    if (ind) { addTags(tags, ind.tags); told.push(['Industry', ind.label]); }
    var notes = cleanNotes(sel.notes);
    addTags(tags, notes.tags); addTags(direct, notes.direct);
    var safety = !!(notes.a.hits.safety || notes.a.hits.bypass || notes.a.hits.cyber), urgent = !!notes.a.hits.urgent;
    if (safety) notices.push(NOTE.safety);
    var phaseId, phaseNote = '', order = null, start = null, startNote = '';
    if (sel.track === 'process') {
      var eng = find(ENGINEERING, sel.engineering);
      if (eng) told.push(['Engineering today', eng.label]);
      phaseId = eng ? eng.phase : 'phase-1';
      if (!eng || eng.id === 'unsure') phaseNote = NOTE.phaseUnstated;
    } else if (sel.track === 'automation') {
      var at = find(AUTO_TODAY, sel.engineering);
      if (at) told.push(['Documentation today', at.label]);
      phaseId = has('legacy') ? 'auto-modernize' : 'auto-services';
      order = []; needs.forEach(function (x) { if (x.svc && order.indexOf(x.svc) < 0) order.push(x.svc); });
    } else {
      phaseId = 'planton-deploy';
      var tds = inList(DATA_TODAY, [].concat(sel.today || []));     // several sources can be true at once
      if (tds.length) told.push(['Data today', tds.map(function (x) { return x.label; }).join('; ')]);
      var known = tds.filter(function (x) { return !x.only; });
      start = known.length ? known[0].start : [0, 1];                 // the least mature source sets the start
      startNote = known.length ? NOTE.start : NOTE.startUnknown;
    }
    if (has('panels')) notices.push(NOTE.panels);
    var also = Object.keys(TRACKS).filter(function (t) { return t !== sel.track && (sel.also || []).indexOf(t) >= 0; });
    if (also.length) told.push(['Also involves', also.map(function (t) { return TRACKS[t].title; }).join('; ')]);
    if (sel.notes) told.push(['Notes', sel.notes]);
    var headline;
    if (sel.track === 'process') {
      var named = procs.filter(function (x) { return !x.only; }).map(function (x) { return x.label.toLowerCase(); });
      headline = (p ? p.label : 'Process system') + (named.length ? ': ' + joinList(named) : '');
    } else headline = needs.length ? needs.map(function (x) { return x.label; }).join(' · ') : tr.title;
    return build({ track: sel.track, tags: tags, direct: refineDirect(direct), stage: stage, text: sel.notes || '', phaseId: phaseId,
      phaseNote: phaseNote, order: order, start: start, startNote: startNote, told: told, headline: headline,
      notices: notices, safety: safety, urgent: urgent, also: also });
  }

  /* =====================================================================================
     Typed conversation: state and decisions (rendered by the page code below)
     ===================================================================================== */
  function newChat() {
    return { msgs: [], intents: {}, negated: {}, flags: {}, stage: '', mixed: false, ready: false,
      askedArea: false, askedStage: false, area: '', safety: false, kind: '', pendingPrice: false, trimmed: false };
  }
  function resetProject(c) {
    c.msgs = []; c.intents = {}; c.negated = {}; c.stage = ''; c.mixed = false; c.ready = false; c.askedStage = false; c.area = ''; c.trimmed = false;
  }
  var AREA_CHIPS = [
    ['process', 'Build a pilot plant or process skid', { pilot: 1, skid: 1 }],
    ['automation', 'Automate or upgrade plant controls', { automation: 1 }],
    ['data', 'Use plant data: OEE, energy, traceability', { plantdata: 1 }],
    ['study', 'Engineering studies or design', { feasibility: 1, detailed: 1 }],
    ['info', 'Company information, careers or support', null],
    ['unsure', 'Not sure yet', null]
  ];
  var STAGE_CHIPS = {
    P: [['Idea or feasibility', 'Concept / feasibility'], ['Lab, pilot or demonstration', 'Pilot or demonstration'],
      ['Ready for detailed engineering', 'Detailed engineering'], ['Design complete, ready to build', 'Detailed engineering', 'ready'],
      ['New industrial plant or line', 'Industrial implementation'], ['Operating plant or upgrade', 'Operating plant / upgrade'], ['Skip this question', '']],
    A: [['A new line, skid or plant', 'Industrial implementation'], ['An existing system', 'Operating plant / upgrade'],
      ['Both: an upgrade and new controls', '', 'mixed'], ['Skip this question', '']]
  };
  var MSG = {
    urgent: 'If anyone is in danger or the equipment is unsafe right now, please stop here: follow your site emergency procedure and contact your site’s qualified personnel or the local emergency services. IRA is an automated page guide and cannot help with a live safety issue. Once the situation is safe, our engineers can review what happened with you.',
    bypass: 'I can’t help with bypassing, overriding or disabling a safety function. Interlocks, emergency stops and trips protect people and equipment, and any change to them needs a documented review by qualified engineers. If a safety function is causing a production problem, our engineers can discuss a reviewed solution with you.',
    safety: 'I can’t approve designs or give safety, code or certification decisions, and IRA cannot judge whether equipment is safe or compliant. Engineering sign-off is agreed for each project with a qualified engineer. This page explains how we approach safety, and our engineers can review your question directly.',
    cyber: 'Industrial cybersecurity needs a qualified review of your actual systems, so IRA cannot give security advice. An engineer can discuss the controls and network scope with you, and who should be involved.',
    inject: 'I’m an automated page guide for this website. I don’t have private instructions or data to share; I only use the pages published on this site. Tell me what you want to build or improve and I’ll point you to the right pages.',
    itw: 'Instron Technologies is an independent engineering company, not affiliated with Instron® (ITW), which makes materials testing equipment such as tensile testers. For testing machines, please contact Instron® (ITW) directly. If you need a process system, controls or plant data, I can help with that.',
    careers: 'It sounds like you are interested in working with us. Applications go to careers@instrontechnologies.com, and this page lists current openings. If you also have a project in mind, describe it and I’ll help with that too.',
    email: 'You can email us at sales@instrontechnologies.com, or use the form on the Contact page.',
    partner: 'We work as a dependable engineering and controls partner under OEM, skid-builder and EPC projects, with scope boundaries agreed up front. This page explains who we work with; an engineer can discuss your scope.',
    support: 'IRA can’t diagnose faults. For an existing system, our engineers can help: share the make, model and what you see, and leave out anything confidential. If the fault creates a safety risk, stop the equipment under your site procedures first.',
    info: 'Here are the main company pages. For support on an existing system, describe the issue or contact our engineers.',
    company: 'Here is where to find that:',
    proof: 'These projects are the closest match:',
    proofNone: 'Our project references are collected here:',
    noMatch: 'I could not match this to a specific need. The guided map takes about two minutes, or an engineer can read your description.',
    area: 'Thanks. Which of these is closest to what you need?',
    stage: 'Where is the project today?',
    priceArea: 'Pricing depends on what you need. Which area is it for?',
    price: {
      P: 'Pricing depends on scope, so an engineer agrees it with you. A Basic Engineering & Feasibility phase gives a Class 4 budgetary estimate before you commit to detailed design.',
      A: 'Automation pricing depends on scope: the platform, I/O count, panels, software and site work. An engineer agrees it with you after reviewing the requirement.',
      D: 'PlantON pricing depends on scope: the data sources, interfaces, users and how far the rollout goes. An engineer agrees it with you after a first review.'
    }
  };
  function labelsOf(obj, n) {
    return Object.keys(obj).filter(function (k) { return INTENTS[k] && INTENTS[k][0]; })
      .sort(function (a, b) { return obj[b] - obj[a]; }).slice(0, n || 3).map(function (k) { return INTENTS[k][0]; });
  }
  function card1(id, why) { var e = entry(id); return e ? { e: e, s: 1, matched: why ? [why] : [] } : null; }
  function cards(list) { return { cards: list.filter(Boolean) }; }

  function chatTurn(c, text) {
    text = String(text || '').trim().slice(0, 1200);
    if (text.length < 2) return [];
    var a = analyse(text), t = norm(text), H = a.hits;
    var sigNew = solutionSignal(H);
    var jobSeeker = H.careers && !/\b(we|our|us)\b/.test(t);
    var infoOnly = !sigNew && (H.careers || H.company || H.location || H.email || H.itw);
    if (jobSeeker || (infoOnly && solutionSignal(c.intents))) resetProject(c);       // topic changed
    else if (CORRECTION.test(t) && sigNew) resetProject(c);                          // "actually, only ..."
    c.msgs.push(text);
    if (c.msgs.length > 6) { c.msgs.shift(); c.trimmed = true; }
    c.flags = {};
    Object.keys(H).forEach(function (k) {
      if (META[k]) c.flags[k] = 1;
      else if (!jobSeeker) { c.intents[k] = Math.min((c.intents[k] || 0) + H[k], 3); delete c.negated[k]; }
    });
    Object.keys(a.negated).forEach(function (k) { delete c.intents[k]; c.negated[k] = 1; });
    if (a.stage || a.mixed) { c.stage = a.stage; c.mixed = a.mixed; }                // the latest stated stage wins
    if (a.ready) c.ready = true;
    if (H.safety || H.bypass || H.urgent) c.safety = true;
    return respond(c);
  }

  function chatPick(c, kind, chip) {
    if (kind === 'area') {
      c.flags = c.pendingPrice ? { price: 1 } : {};
      if (chip[0] === 'info') return [{ say: MSG.info }, cards([card1('our-company', 'company'), card1('careers', 'careers'), card1('global-presence', 'location')]), { actions: { contact: true, map: true } }];
      if (chip[2]) addTags(c.intents, chip[2]);
      return respond(c);
    }
    if (kind === 'stage') {
      c.flags = {};
      c.stage = chip[1]; c.mixed = chip[2] === 'mixed'; if (chip[2] === 'ready') c.ready = true;
      return respond(c);
    }
    return [];
  }

  function respond(c) {
    var I = c.intents, F = c.flags, sig = solutionSignal(I), ops = [];
    c.kind = '';
    if (F.urgent) { c.kind = 'urgent'; return [{ say: MSG.urgent }, { actions: { contact: true } }]; }
    if (F.bypass) { c.kind = 'safety'; return [{ say: MSG.bypass }, cards([card1('trust-responsibility', 'safety')]), { actions: { talk: 'safety', first: true } }]; }
    if (F.safety) { c.kind = 'safety'; return [{ say: MSG.safety }, cards([card1('trust-responsibility', 'safety')]), { actions: { talk: 'safety', first: true } }]; }
    if (F.cyber) { c.kind = 'cyber'; return [{ say: MSG.cyber }, { actions: { talk: 'cyber', first: true } }]; }
    if (F.inject) return [{ say: MSG.inject }, { actions: { map: true } }];
    if (F.itw) return [{ say: MSG.itw }, { actions: { map: true } }];
    if (F.careers && !sig) return [{ say: MSG.careers }, cards([card1('careers', 'careers')])];
    if (F.support) { c.kind = 'support'; return [{ say: MSG.support }, { actions: { talk: 'support', first: true } }]; }
    if (F.partner) {
      c.kind = 'partner';
      return [{ say: MSG.partner }, cards([card1('industries-who', 'partner')]), { actions: { talk: 'partner', first: true } }];
    }
    if (!sig && (F.email || F.company || F.location)) {
      if (F.email) ops.push({ say: MSG.email });
      var meta = {}; ['company', 'location'].forEach(function (k) { if (F[k]) meta[k] = 1; });
      if (meta.company || meta.location) {
        var cp = rank(data.entries, {}, '', '', meta).pages.filter(function (x) { return x.e.type === 'company'; }).slice(0, 2);
        if (cp.length) { ops.push({ say: MSG.company }); ops.push(cards(cp)); }
      }
      ops.push({ actions: { contact: true, map: true } });
      return ops;
    }
    if (F.proof && !sig) return [{ say: MSG.proofNone }, cards([card1('case-studies', 'proof'), card1('project-portfolio', 'proof')]), { actions: { map: true } }];
    if (F.price) c.pendingPrice = true;
    if (!sig) {
      if (!c.askedArea) { c.askedArea = true; return [{ say: c.pendingPrice ? MSG.priceArea : MSG.area }, { chips: 'area', list: AREA_CHIPS }]; }
      return [{ say: MSG.noMatch }, { actions: { map: true, talk: 'general' } }];
    }
    var area = areaOf(I); c.area = area;
    if (c.pendingPrice) { ops.push({ say: MSG.price[area] || MSG.price.P }); c.pendingPrice = false; }
    var skipStage = F.contact || F.proof || ops.length || area === 'D';
    if (!c.stage && !c.mixed && !c.askedStage && !skipStage && STAGE_CHIPS[area]) {
      c.askedStage = true;
      return ops.concat([{ say: MSG.stage }, { chips: 'stage', list: STAGE_CHIPS[area] }]);
    }
    var b = briefFromChat(c);
    var understood = 'I understood: ' + TRACKS[b.track].title.toLowerCase();
    if (b.stage) understood += ', ' + b.stage.toLowerCase();
    else if (c.mixed) understood += ', an existing system and new controls';
    var need = labelsOf(b.direct, 3);
    if (need.length) understood += '; ' + joinList(need);
    var neg = labelsOf(c.negated, 2);
    if (neg.length) understood += '. Not: ' + joinList(neg);
    ops.push({ say: understood + '. If that is not right, add a correction.' });
    if (I.panels) ops.push({ say: NOTE.panels });
    if (F.proof) {
      ops.push({ say: b.cases.length && !b.cases[0].adjacent ? MSG.proof : NOTE.noCase });
      ops.push(cards(b.cases.filter(function (x) { return !x.adjacent; }).concat([card1('case-studies', 'proof')])));
    } else {
      var list = b.pages.slice(0, 3);
      if (b.cases.length && !b.cases[0].adjacent) list.push(b.cases[0]);   // same pages as the brief, plus the best project
      ops.push({ say: list.length === 1 ? 'This page is the closest match:' : 'These pages are the closest match:' });
      ops.push(cards(list));
    }
    ops.push({ actions: { brief: !c.safety, talk: c.safety ? 'safety' : 'brief', first: !!F.contact } });
    return ops;
  }

  function briefFromChat(c) {
    var I = c.intents, s = areaScores(I), area = areaOf(I) || c.area;
    if (!area) return null;
    var track = area === 'A' ? 'automation' : area === 'D' ? 'data' : 'process';
    var told = [['Area', TRACKS[track].title]], notices = [];
    var dir = refineDirect(I);
    var second = Object.keys(s).filter(function (k) {
      return k !== area && s[k] >= Math.max(1, s[area] / 2) && Object.keys(dir).some(function (d) { return AREA_OF[d] === k; });
    })[0];
    var also = second ? [second === 'A' ? 'automation' : second === 'D' ? 'data' : 'process'] : [];
    if (also.length) told.push(['Also involves', TRACKS[also[0]].title]);
    if (c.stage) told.push(['Stage', c.stage]);
    else if (c.mixed) { told.push(['Stage', 'Existing system and new controls']); notices.push(NOTE.mixed); }
    told.push([c.trimmed ? 'Described as (latest messages)' : 'Described as', c.msgs.join(' / ')]);
    var neg = labelsOf(c.negated, 3); if (neg.length) told.push(['Not needed', neg.join('; ')]);
    var tags = {}; Object.keys(I).forEach(function (k) { if (!META[k]) tags[k] = I[k]; });
    addTags(tags, TRACKS[track].tags);
    var phaseId, phaseNote = '', order = null, start = null, startNote = '';
    if (track === 'data') { phaseId = 'planton-deploy'; start = [0, 1]; startNote = NOTE.startUnknown; }
    else if (track === 'automation') {
      phaseId = I.modernize ? 'auto-modernize' : 'auto-services';
      order = [];
      [['modernize', 'modernize'], ['batch', 'batch'], ['compliance', 'batch'], ['panels', 'ei'], ['cip', 'new'], ['automation', 'new']].forEach(function (p) { if (I[p[0]] && order.indexOf(p[1]) < 0) order.push(p[1]); });
    } else {
      phaseId = c.ready ? 'phase-3' : c.stage === 'Detailed engineering' ? 'phase-2' : 'phase-1';
      if (!c.ready && /Industrial|Operating/.test(c.stage)) phaseNote = NOTE.phaseUnstated;
    }
    var head = c.msgs[0] || TRACKS[track].title;
    if (head.length > 90) head = head.slice(0, 87).replace(/\s+\S*$/, '') + '…';
    return build({ track: track, tags: tags, direct: refineDirect(I), stage: c.stage, text: c.msgs.join(' '), phaseId: phaseId,
      phaseNote: phaseNote, order: order, start: start, startNote: startNote, told: told, headline: head, notices: notices, safety: c.safety, also: also });
  }

  /* =====================================================================================
     Text versions: copy, PDF footer and Contact handoff
     ===================================================================================== */
  var LIMIT = 2900; // Contact form description limit
  function briefText(b) {
    var L = ['Project brief prepared with IRA on the Instron Technologies website', ''];
    b.told.forEach(function (t) { L.push(t[0] + ': ' + t[1]); });
    b.notices.forEach(function (n) { L.push('Note: ' + n); });
    if (b.phase) L.push('', (SEC_TITLE[b.phaseId] || 'Suggested first step') + ': ' + b.phase.title + ' (' + absUrl(b.phase.url) + ')');
    if (b.pages.length) { L.push('', 'Pages to read:'); b.pages.forEach(function (x) { L.push('- ' + x.e.title + ' (' + absUrl(x.e.url) + ')'); }); }
    if (b.cases.length) { L.push('', 'Related projects:'); b.cases.forEach(function (x) { L.push('- ' + (x.adjacent ? '[related capability] ' : '') + x.e.title + ' (' + absUrl(x.e.url) + ')'); }); }
    if (b.prepare) { L.push('', 'Useful inputs to prepare:'); b.prepare.items.forEach(function (q) { L.push('- ' + q); }); }
    return L.join('\n');
  }
  var KIND_LINE = { safety: 'Safety, approval or certification question (for qualified review)', cyber: 'Industrial cybersecurity question',
    support: 'Support for an existing system', partner: 'Engineering partnership or extra capacity', general: 'General enquiry' };
  var KIND_AREA = { safety: '', cyber: 'O', support: 'O', partner: 'C', general: '' };
  function enquiryText(kind, c) {
    return ['Enquiry from IRA on the Instron Technologies website', '', 'Question type: ' + KIND_LINE[kind], 'Visitor’s words: ' + c.msgs.join(' / ')].join('\n');
  }
  function fit(text) {
    if (text.length <= LIMIT) return { text: text, cut: false };
    return { text: text.slice(0, LIMIT - 90).replace(/\s+\S*$/, '') + '\n[Shortened to fit the form; Copy brief in IRA gives the full text]', cut: true };
  }
  function handoffPayload(b, kind, c) {
    var f;
    if (kind && kind !== 'brief') {
      f = fit(enquiryText(kind, c));
      var ar = KIND_AREA[kind];
      if (kind === 'support' && c && areaOf(c.intents)) ar = areaOf(c.intents);
      return { v: 3, brief: f.text, cut: f.cut, area: AREA[ar] || '', stage: kind === 'partner' ? 'Early discussion' : kind === 'support' ? 'Operating plant / upgrade' : '' };
    }
    f = fit(briefText(b));
    return { v: 3, brief: f.text, cut: f.cut, area: AREA[b.area] || '', stage: b.stage || '' };
  }

  var ENGINE = { analyse: analyse, detect: detect, detectStage: detectStage, areaOf: areaOf, solutionSignal: solutionSignal, rank: rank,
    reasonFor: reasonFor, refineDirect: refineDirect, setData: setData, briefFromMap: briefFromMap, briefFromChat: briefFromChat,
    newChat: newChat, chatTurn: chatTurn, chatPick: chatPick, briefText: briefText, handoffPayload: handoffPayload,
    AREA: AREA, INTENTS: INTENTS, TRACKS: TRACKS, PATH: PATH, PROCESS: PROCESS, NEEDS: NEEDS, INDUSTRIES: INDUSTRIES,
    ENGINEERING: ENGINEERING, AUTO_TODAY: AUTO_TODAY, DATA_TODAY: DATA_TODAY, LIMIT: LIMIT };
  if (typeof module !== 'undefined' && module.exports) { module.exports = ENGINE; return; }
  if (typeof document === 'undefined') return;

  /* =====================================================================================
     Page integration: switch, link carry-over, Contact page prefill
     ===================================================================================== */
  var params = new URLSearchParams(location.search);
  var self = document.currentScript;
  var base = self ? new URL('.', self.src) : new URL('assets/ira/', location.href);
  var DEFAULT_ON = true;                                     // v2.34: shown on every page unless ?ira=0
  var ON = DEFAULT_ON ? params.get('ira') !== '0' : params.get('ira') === '1';
  var CARRY = DEFAULT_ON ? (params.get('ira') === '0' ? '0' : '') : (ON ? '1' : '');   // keep a non-default choice across links
  var BRIEF_KEY = '#ira-brief=';
  var PAGE = (location.pathname.split('/').pop() || 'index.html').replace(/\?.*$/, '') || 'index.html';
  var BRIEF_START = /(Project brief prepared with IRA|Enquiry from IRA)/;

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
    if (!form || !payload || typeof payload.brief !== 'string') return false;
    ensureCss();
    var ta = form.querySelector('textarea[name="challenge"]'), cut = !!payload.cut;
    if (ta) {
      var cur = ta.value, at = cur.search(BRIEF_START);
      if (at >= 0) cur = cur.slice(0, at);                       // a second hand-off replaces the earlier brief
      cur = cur.trim();
      var max = ta.maxLength > 0 ? Math.min(ta.maxLength, LIMIT) : LIMIT;
      var room = max - (cur ? cur.length + 2 : 0), txt = payload.brief.slice(0, 6000);
      if (txt.length > room) { txt = txt.slice(0, Math.max(0, room - 40)) + '\n[Shortened to fit the form]'; cut = true; }
      ta.value = (cur ? cur + '\n\n' : '') + txt;
    }
    [['type', payload.area], ['stage', payload.stage]].forEach(function (p) {
      var s = form.querySelector('select[name="' + p[0] + '"]');
      if (!s || !p[1] || (s.value && s.dataset.ira !== '1')) return;  // never overwrite the visitor's own choice
      for (var i = 0; i < s.options.length; i++) if (s.options[i].text === p[1]) { s.selectedIndex = i; s.dataset.ira = '1'; break; }
      if (!s._iraWatch) { s._iraWatch = 1; s.addEventListener('change', function () { delete s.dataset.ira; }); }
    });
    var note = document.getElementById('ira-prefill-note');
    if (!note) {
      note = document.createElement('p');
      note.id = 'ira-prefill-note'; note.className = 'ira-prefill'; note.setAttribute('role', 'status');
      form.insertBefore(note, form.firstChild);
    }
    note.textContent = 'Your IRA brief has been added to the project description' + (cut ? ' (shortened to fit; use Copy brief in IRA for the full text)' : '') +
      '. Please review it, remove anything confidential, add your details and open the email draft. Nothing is sent until you send the email yourself.';
    var first = form.querySelector('input[name="name"]');
    form.scrollIntoView({ block: 'start' });
    if (first) first.focus({ preventScroll: true });
    return true;
  }

  if (onContactPage() && location.hash.indexOf(BRIEF_KEY) === 0) {
    var payload0 = null;
    try { payload0 = JSON.parse(decodeURIComponent(location.hash.slice(BRIEF_KEY.length))); } catch (err) { payload0 = null; }
    history.replaceState(null, '', location.pathname + location.search);   // the brief does not stay in the address or history
    var run0 = function () { fillContact(payload0); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run0); else run0();
  }

  function carry(a) {
    var raw = a.getAttribute('href');
    if (!raw || /^(mailto:|tel:|#|javascript:)/i.test(raw)) return;
    var u;
    try { u = new URL(raw, location.href); } catch (err) { return; }
    if (!CARRY || u.origin !== location.origin || !/\.html$/.test(u.pathname) || u.searchParams.has('ira')) return;
    u.searchParams.set('ira', CARRY);
    a.setAttribute('href', u.pathname.split('/').pop() + u.search + u.hash);
  }
  function flagUrl(u) { return CARRY ? String(u).replace(/^([^#?]+)/, '$1?ira=' + CARRY) : String(u); }
  if (!ON) { if (CARRY) { var off = function () { Array.prototype.forEach.call(document.querySelectorAll('a[href]'), carry); };
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', off); else off(); } return; }

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
  var loading = null;
  var sel, chat, mode, step;
  function resetAll() {
    sel = { track: '', path: '', process: [], need: [], industry: '', engineering: '', today: [], also: [], notes: '' };
    chat = newChat();
    mode = 'map'; step = 1;
  }
  resetAll();
  // one place that changes the track: answers that belong to another track are cleared
  function setTrack(t) {
    if (t === sel.track) return;
    var keepIndustry = /^(automation|data)$/.test(sel.track) && /^(automation|data)$/.test(t);
    sel.track = t; sel.path = ''; sel.process = []; sel.need = []; sel.engineering = ''; sel.today = [];
    sel.also = (sel.also || []).filter(function (x) { return x !== t; });
    if (!keepIndustry) sel.industry = '';
  }

  function el(tag, cls, txt) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }
  function btn(cls, txt, on) { var b = el('button', cls, txt); b.type = 'button'; if (on) b.addEventListener('click', on); return b; }
  function imgUrl(src) { return src ? new URL(src, location.href).href : ''; }

  function loadData() {
    if (data) return Promise.resolve(data);
    if (!loading) {
      loading = fetch(new URL('ira-content.json', base).href, { credentials: 'same-origin', cache: 'no-cache' })
        .then(function (r) { if (!r.ok) throw new Error('content'); return r.json(); })
        .then(function (d) { setData(d); return data; })
        .catch(function () { loading = null; throw new Error('content'); });
    }
    return loading;
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

  // a side panel next to the page (not modal): the page stays usable, Esc closes, focus returns to where it came from
  var panel = el('section', 'ira-panel');
  panel.id = 'ira-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'false');
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
  var note = el('p', 'ira-note', 'Automated guide. It uses pages from this website only. Nothing you enter is stored or sent; an engineer sees your brief only if you choose to email it. Please leave out confidential details.');
  var status = el('p', 'ira-sr'); status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
  panel.appendChild(head); panel.appendChild(view); panel.appendChild(foot); panel.appendChild(note); panel.appendChild(status);
  root.appendChild(launcher); root.appendChild(panel);

  function announce(t) { status.textContent = ''; setTimeout(function () { status.textContent = t; }, 30); }
  function setProgress(n) {
    Array.prototype.forEach.call(progress.children, function (s, i) { s.className = i < n ? 'is-on' : ''; });
    progress.style.display = n ? '' : 'none';
  }

  function clearView() { cleanupPrint(); view.textContent = ''; foot.textContent = ''; view.scrollTop = 0; panel.classList.remove('is-brief', 'is-chat'); }

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

  // arrow keys move through a radio group and choose (ARIA radio pattern); Tab enters at the chosen item
  function roving(box, items, choose) {
    var sync = function () {
      var on = -1;
      items.forEach(function (b, i) { if (b.getAttribute('aria-checked') === 'true') on = i; });
      items.forEach(function (b, i) { b.tabIndex = (on < 0 ? i === 0 : i === on) ? 0 : -1; });
    };
    box.addEventListener('keydown', function (e) {
      var i = items.indexOf(document.activeElement);
      if (i < 0) return;
      var d = (e.key === 'ArrowDown' || e.key === 'ArrowRight') ? 1 : (e.key === 'ArrowUp' || e.key === 'ArrowLeft') ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var j = (i + d + items.length) % items.length;
      items[j].focus(); choose(j); sync();
    });
    return sync;
  }

  // choice buttons: single choice behaves like radios, multi like toggles; tracks are plain buttons (choosing moves on)
  function choices(list, opts) {
    var box = el('div', 'ira-choices ' + (opts.cls || ''));
    var radio = !opts.multi && !opts.go;
    box.setAttribute('role', radio ? 'radiogroup' : 'group');
    box.setAttribute('aria-label', opts.label);
    var items = [];
    var paint = function () {
      items.forEach(function (c, i) {
        var picked = opts.multi ? opts.get().indexOf(list[i].id) >= 0 : opts.get() === list[i].id;
        c.classList.toggle('is-on', picked);
        if (radio) c.setAttribute('aria-checked', String(picked)); else c.setAttribute('aria-pressed', String(picked));
      });
      if (sync) sync();
    };
    var sync = null;
    list.forEach(function (o) {
      var b = btn('ira-choice');
      if (radio) b.setAttribute('role', 'radio');
      if (o.img) {
        var im = el('img', 'ira-choice-img'); im.src = imgUrl(o.img[0]); im.alt = ''; im.loading = 'lazy'; im.decoding = 'async';
        b.appendChild(im);
      }
      var tx = el('span', 'ira-choice-text');
      tx.appendChild(el('span', 'ira-choice-label', o.label));
      if (o.hint) tx.appendChild(el('span', 'ira-choice-hint', o.hint));
      b.appendChild(tx);
      b.addEventListener('click', function () {
        if (opts.multi) {
          var cur = opts.get().slice(), i = cur.indexOf(o.id);
          if (i >= 0) cur.splice(i, 1);
          else if (o.only) cur = [o.id];                                        // "Something else" stands alone
          else {
            cur = cur.filter(function (id) { var x = find(list, id); return !(x && x.only); });
            if (opts.max && cur.length >= opts.max) { announce('You can choose up to ' + opts.max + '. Deselect one to change your choice.'); if (opts.limit) opts.limit(); return; }
            cur.push(o.id);
          }
          opts.set(cur);
        } else {
          var on = opts.get() === o.id;
          opts.set(on && opts.optional ? '' : o.id);
        }
        paint();
        if (opts.change) opts.change();
      });
      items.push(b); box.appendChild(b);
    });
    if (radio) sync = roving(box, items, function (j) { opts.set(list[j].id); paint(); if (opts.change) opts.change(); });
    view.appendChild(box);
    paint();
    return box;
  }

  function limitNote(after) {
    var n = el('p', 'ira-limit'); n.hidden = true; after.parentNode.insertBefore(n, after.nextSibling);
    return function (max) { n.textContent = 'You can choose up to ' + max + '. Deselect one to change your choice.'; n.hidden = false; };
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
    choices(list, { label: 'Area', cls: 'ira-tracks', go: true, get: function () { return sel.track; }, set: setTrack,
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
    var h, box, show;
    if (sel.track === 'process') {
      h = stepHead('Step 2 of 3', 'Where is the technology today?', 'Choose the point on the path that fits best.');
      var path = el('ol', 'ira-path');
      path.setAttribute('role', 'radiogroup');
      path.setAttribute('aria-label', 'Technology stage');
      var nodes = [];
      var paintPath = function () {
        var idx = -1;
        PATH.forEach(function (s, i) { if (s.id === sel.path) idx = i; });
        Array.prototype.forEach.call(path.children, function (li, i) {
          li.classList.toggle('is-done', idx >= 0 && i < idx && PATH[i].id !== 'repeat');
          li.classList.toggle('is-on', i === idx);
          li.firstChild.setAttribute('aria-checked', String(i === idx));
        });
        if (syncPath) syncPath();
      };
      var syncPath = null;
      PATH.forEach(function (s) {
        var li = el('li', 'ira-node');
        var b = btn('ira-node-btn', null, function () { sel.path = s.id; paintPath(); upd(); });
        b.setAttribute('role', 'radio');
        b.appendChild(el('span', 'ira-node-dot')).setAttribute('aria-hidden', 'true');
        b.appendChild(el('span', 'ira-node-label', s.label));
        b.appendChild(el('span', 'ira-node-hint', s.hint));
        li.appendChild(b); path.appendChild(li); nodes.push(b);
      });
      syncPath = roving(path, nodes, function (j) { sel.path = PATH[j].id; paintPath(); upd(); });
      view.appendChild(path); paintPath();
      view.appendChild(el('h4', 'ira-q', 'What does the process involve? (optional, up to three)'));
      box = choices(PROCESS, { label: 'Process', multi: true, max: 3, cls: 'ira-chips', get: function () { return sel.process; }, set: function (v) { sel.process = v; },
        limit: function () { show(3); } });
      show = limitNote(box);
    } else {
      var t = sel.track === 'automation' ? 'What is the main need?' : 'What do you want to see or improve?';
      var max = sel.track === 'data' ? 3 : 2;
      h = stepHead('Step 2 of 3', t, sel.track === 'data' ? 'Choose up to three.' : 'Choose one or two.');
      box = choices(NEEDS[sel.track], { label: 'Main need', multi: true, max: max, cls: 'ira-needs',
        get: function () { return sel.need; }, set: function (v) { sel.need = v; }, change: upd, limit: function () { show(max); } });
      show = limitNote(box);
      view.appendChild(el('h4', 'ira-q', 'Industry (optional)'));
      choices(INDUSTRIES, { label: 'Industry', optional: true, cls: 'ira-chips', get: function () { return sel.industry; }, set: function (v) { sel.industry = v; } });
    }
    var others = Object.keys(TRACKS).filter(function (k) { return k !== sel.track; }).map(function (k) { return { id: k, label: TRACKS[k].title }; });
    view.appendChild(el('h4', 'ira-q', 'Also involves (optional)'));
    choices(others, { label: 'Also involves', multi: true, cls: 'ira-chips', get: function () { return sel.also; }, set: function (v) { sel.also = v; } });
    next = navRow(renderStart, 'Next', renderLast, ready());
    focusTitle(h);
  }

  function renderLast() {
    mode = 'map'; step = 3; clearView(); setProgress(3);
    var h;
    if (sel.track === 'data') {
      h = stepHead('Step 3 of 3', 'How are these figures captured today?', 'Choose all that apply; plants often have a mix. This shows where a PlantON deployment would likely start.');
      choices(DATA_TODAY, { label: 'Data today', multi: true, cls: 'ira-needs', get: function () { return sel.today; }, set: function (v) { sel.today = v; } });
    } else if (sel.track === 'automation') {
      h = stepHead('Step 3 of 3', 'What documentation exists today?', 'Choose the most complete you have. This helps an engineer judge where to start.');
      choices(AUTO_TODAY, { label: 'Documentation today', optional: true, cls: 'ira-list', get: function () { return sel.engineering; }, set: function (v) { sel.engineering = v; } });
    } else {
      h = stepHead('Step 3 of 3', 'What engineering exists today?', 'Choose the most advanced you have. This sets the suggested first step. Each phase is contracted separately, with no obligation to continue.');
      choices(ENGINEERING, { label: 'Engineering today', optional: true, cls: 'ira-list', get: function () { return sel.engineering; }, set: function (v) { sel.engineering = v; } });
    }
    var other = sel.process.indexOf('other') >= 0;
    var lab = el('label', 'ira-q', other ? 'Please describe the process briefly (optional)' : 'Anything else we should know? (optional)'); lab.htmlFor = 'ira-notes';
    var ta = el('textarea', 'ira-input'); ta.id = 'ira-notes'; ta.rows = 3; ta.maxLength = 600; ta.value = sel.notes;
    ta.placeholder = (other ? 'For example: the feed, the product and what the next stage must prove.' : 'For example: capacity, timing, or what the next stage must prove.') + ' Please leave out confidential details.';
    ta.addEventListener('input', function () { sel.notes = ta.value.trim(); });
    view.appendChild(lab); view.appendChild(ta);
    navRow(renderNeeds, 'Create my project brief', function () { withData(function () { renderBrief(briefFromMap(sel), renderLast, 'brief'); }); }, true);
    focusTitle(h);
  }

  /* =====================================================================================
     Project brief view (also used for printing)
     ===================================================================================== */
  function card(x, direct) {
    var isCase = x.e.type === 'case';
    var a = el('a', 'ira-rcard' + (isCase ? ' ira-rcard-case' : '') + (x.adjacent ? ' ira-rcard-adj' : ''));
    a.href = flagUrl(x.e.url);
    if (x.e.image) {
      var im = el('img', 'ira-rcard-img'); im.src = imgUrl(x.e.image[0]); im.alt = ''; im.loading = 'lazy'; im.decoding = 'async';
      a.appendChild(im);
    }
    var body = el('span', 'ira-rcard-body');
    if (isCase) body.appendChild(el('span', 'ira-rcard-k', x.adjacent ? 'Related capability' : 'Completed project'));
    body.appendChild(el('span', 'ira-rcard-title', x.e.title));
    body.appendChild(el('span', 'ira-rcard-reason', reasonFor(x, direct)));
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
    b.notices.forEach(function (n) { top.appendChild(el('p', 'ira-notice', n)); });
    wrap.appendChild(top);

    if (b.phase) {
      var ph = el('section', 'ira-sec ira-phase');
      ph.appendChild(el('h4', 'ira-sec-title', SEC_TITLE[b.phaseId] || 'Suggested first step'));
      var pt = el('p', 'ira-phase-name');
      var pa = el('a', null, b.phase.title); pa.href = flagUrl(b.phase.url); pt.appendChild(pa);
      ph.appendChild(pt);
      ph.appendChild(el('p', 'ira-phase-what', b.phase.what));
      if (b.phase.best_when && b.track === 'process') ph.appendChild(el('p', 'ira-phase-when', 'Best when: ' + b.phase.best_when));
      if (b.phaseNote) ph.appendChild(el('p', 'ira-phase-when', b.phaseNote));
      ph.appendChild(el('p', 'ira-mini', b.phase.list_label || 'Typical deliverables'));
      var ul = el('ul', 'ira-deliv' + (b.phase.highlight ? ' ira-deliv-steps' : ''));
      var all = b.phase.deliverables || [], n = forPrint ? all.length : Math.min(6, all.length);
      for (var i = 0; i < n; i++) {
        var li = el('li', null, all[i]);
        if (b.phase.highlight && b.phase.highlight.indexOf(i) >= 0) { li.className = 'is-start'; li.appendChild(el('span', 'ira-start-tag', b.phaseId === 'auto-services' ? 'Your need' : 'Likely starting point')); }
        ul.appendChild(li);
      }
      ph.appendChild(ul);
      if (b.startNote) ph.appendChild(el('p', 'ira-fine', b.startNote));
      if (!forPrint && all.length > n) {
        var more = el('a', 'ira-more', 'See all ' + all.length + ' deliverables'); more.href = flagUrl(b.phase.url); ph.appendChild(more);
      }
      if (/^phase-/.test(b.phaseId)) ph.appendChild(el('p', 'ira-fine', 'Each phase is contracted separately, with no obligation to continue. Deliverables are typical and agreed per project.'));
      wrap.appendChild(ph);
    }
    if (b.pages.length) {
      var rp = el('section', 'ira-sec');
      rp.appendChild(el('h4', 'ira-sec-title', 'Read next'));
      var g = el('div', 'ira-rgrid'); b.pages.forEach(function (x) { g.appendChild(card(x, b.direct)); }); rp.appendChild(g);
      wrap.appendChild(rp);
    }
    if (b.cases.length || b.noCase) {
      var rc = el('section', 'ira-sec');
      rc.appendChild(el('h4', 'ira-sec-title', 'Related projects'));
      if (b.noCase) rc.appendChild(el('p', 'ira-fine ira-nocase', NOTE.noCase));
      if (b.cases.length) { var g2 = el('div', 'ira-rgrid'); b.cases.forEach(function (x) { g2.appendChild(card(x, b.direct)); }); rc.appendChild(g2); }
      wrap.appendChild(rc);
    }
    if (b.prepare) {
      var qs = el('section', 'ira-sec');
      qs.appendChild(el('h4', 'ira-sec-title', 'Useful inputs to prepare for a first conversation'));
      var ol = el('ul', 'ira-qs'); b.prepare.items.forEach(function (q) { ol.appendChild(el('li', null, q)); }); qs.appendChild(ol);
      var src = el('p', 'ira-fine');
      src.appendChild(document.createTextNode('From '));
      b.prepare.sources.forEach(function (s, i) {
        if (i) src.appendChild(document.createTextNode(' and '));
        var sa = el('a', null, s.title); sa.href = flagUrl(s.url); src.appendChild(sa);
      });
      qs.appendChild(src);
      wrap.appendChild(qs);
    }
    return wrap;
  }

  function renderUrgent(backFn) {
    mode = 'brief'; clearView(); setProgress(0);
    var h = stepHead(null, 'Safety first', null);
    view.appendChild(el('p', 'ira-notice ira-urgent', MSG.urgent));
    foot.textContent = '';
    if (backFn) foot.appendChild(btn('ira-btn', 'Back', backFn));
    foot.appendChild(el('span', 'ira-spacer'));
    var a = el('a', 'ira-btn', 'Contact page'); a.href = flagUrl('contact.html'); foot.appendChild(a);
    focusTitle(h);
  }

  function renderBrief(b, backFn) {
    if (!b) return renderStart();
    if (b.urgent) return renderUrgent(backFn);
    mode = 'brief'; clearView(); setProgress(4); panel.classList.add('is-brief');
    var node = briefNode(b, false);
    var tools = el('div', 'ira-tools');
    tools.appendChild(btn('ira-tool', 'Save as PDF', function () { printBrief(b); }));
    var copy = btn('ira-tool', 'Copy brief', function () { copyText(briefText(b), copy); });
    tools.appendChild(copy);
    node.querySelector('.ira-brief-top').appendChild(tools);
    var h = handoffPayload(b, 'brief');
    if (h.cut) node.querySelector('.ira-brief-top').appendChild(el('p', 'ira-fine', 'The email version is shortened to fit the form. Copy brief gives the full text.'));
    view.appendChild(node);
    foot.textContent = '';
    if (backFn) foot.appendChild(btn('ira-btn', 'Back', backFn));
    foot.appendChild(btn('ira-btn ira-quiet', 'Start over', function () { resetAll(); renderStart(); }));
    foot.appendChild(el('span', 'ira-spacer'));
    foot.appendChild(handoffButton(h, b.safety ? 'Ask an engineer to review' : 'Discuss with an engineer', true));
    focusTitle(node.querySelector('.ira-brief-title'));
  }

  function handoffButton(payload, label, primary) {
    var cls = 'ira-btn' + (primary ? ' ira-primary' : '');
    if (onContactPage()) return btn(cls, 'Add to the Contact form', function () { fillContact(payload); setOpen(false, true); });
    var a = el('a', cls, label); a.href = flagUrl('contact.html') + BRIEF_KEY + encodeURIComponent(JSON.stringify(payload));
    return a;
  }

  function copyText(t, b) {
    var o = b.textContent;
    var show = function (msg) { b.textContent = msg; announce(msg); setTimeout(function () { b.textContent = o; }, 1800); };
    var fallback = function () {
      var ta = el('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (err) { ok = false; }
      ta.remove();
      show(ok ? 'Copied' : 'Could not copy; use Save as PDF');
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { show('Copied'); }, fallback); else fallback();
  }

  function cleanupPrint() {
    var old = document.getElementById('ira-print'); if (old) old.remove();
    document.body.classList.remove('ira-printing');
  }
  function printBrief(b) {
    cleanupPrint();
    var pr = el('div'); pr.id = 'ira-print';
    var hd = el('div', 'ira-print-head');
    var logo = document.querySelector('header img, .lv-header img');
    if (logo) { var lg = el('img', 'ira-print-logo'); lg.src = logo.currentSrc || logo.src; lg.alt = 'Instron Technologies'; hd.appendChild(lg); }
    hd.appendChild(el('p', 'ira-print-tag', 'Engineer | Embrace | Elevate'));
    pr.appendChild(hd);
    pr.appendChild(briefNode(b, true));
    var ft = el('div', 'ira-print-foot');
    ft.appendChild(el('p', null, 'Instron Technologies · sales@instrontechnologies.com · instrontechnologies.com'));
    ft.appendChild(el('p', null, 'Instron Technologies is an independent company, not affiliated with Instron® (ITW). This brief was prepared from the visitor’s own answers on the website; it is a starting point for a conversation, not a design or commercial commitment.'));
    pr.appendChild(ft);
    document.body.appendChild(pr);
    document.body.classList.add('ira-printing');
    var after = function () { cleanupPrint(); window.removeEventListener('afterprint', after); };
    window.addEventListener('afterprint', after);   // fallback: the next IRA view also cleans up
    setTimeout(function () { window.print(); }, 60);
  }

  /* =====================================================================================
     Typed conversation: renders the engine's decisions
     ===================================================================================== */
  var log, input, sendBtn, busy = false;
  function renderChat() {
    mode = 'chat'; clearView(); setProgress(0); panel.classList.add('is-chat');
    log = el('div', 'ira-log'); log.setAttribute('role', 'log'); log.setAttribute('aria-live', 'polite'); log.setAttribute('aria-relevant', 'additions');
    view.appendChild(log);
    var form = el('form', 'ira-form');
    var label = el('label', 'ira-sr', 'Describe what you want to improve or build'); label.htmlFor = 'ira-text';
    input = el('textarea', 'ira-input'); input.id = 'ira-text'; input.rows = 2; input.maxLength = 1200;
    input.placeholder = 'For example: we want to scale a solvent recovery process to a pilot skid';
    sendBtn = el('button', 'ira-send', 'Send'); sendBtn.type = 'submit';
    form.appendChild(label); form.appendChild(input); form.appendChild(sendBtn);
    form.addEventListener('submit', function (e) { e.preventDefault(); if (busy) return; var v = input.value; input.value = ''; handle(v); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit', { cancelable: true })); }
    });
    foot.appendChild(form);
    say('Describe what you are trying to improve or build, in your own words. I will point you to the right pages and can turn it into a project brief. Please leave out confidential details.');
    var alt = el('p', 'ira-alt'); alt.appendChild(btn('ira-link', 'Use the guided map instead', function () { renderStart(); }));
    log.appendChild(alt);
    setTimeout(function () { input.focus(); }, 30);
  }

  function scrollLog() { view.scrollTop = view.scrollHeight; }
  function say(text, who) {
    var m = el('p', 'ira-msg ' + (who === 'you' ? 'ira-you' : 'ira-bot'), text);
    log.appendChild(m); scrollLog(); return m;
  }
  function staleChips() { Array.prototype.forEach.call(log.querySelectorAll('.ira-chatchips button'), function (x) { x.disabled = true; }); }
  function chipRow(kind, list) {
    var box = el('div', 'ira-chatchips'); box.setAttribute('role', 'group'); box.setAttribute('aria-label', kind === 'area' ? 'Type of need' : 'Project stage');
    list.forEach(function (c) {
      var b = btn('ira-chip', kind === 'area' ? c[1] : c[0], function () {
        staleChips(); b.classList.add('is-picked');
        say(kind === 'area' ? c[1] : c[0], 'you');
        render(chatPick(chat, kind, c));
      });
      box.appendChild(b);
    });
    log.appendChild(box); scrollLog();
    var f = box.querySelector('button'); if (f) f.focus();
  }
  function actionRow(o) {
    var row = el('div', 'ira-actions');
    var items = [];
    if (o.brief) items.push(btn('ira-btn', 'Create my project brief', function () { renderBrief(briefFromChat(chat), renderChat); }));
    if (o.talk) {
      var label = { safety: 'Ask an engineer to review', cyber: 'Ask an engineer', support: 'Ask an engineer', partner: 'Discuss a partnership', general: 'Ask an engineer', brief: 'Discuss with an engineer' }[o.talk];
      var payload = o.talk === 'brief' ? handoffPayload(briefFromChat(chat), 'brief') : handoffPayload(null, o.talk, chat);
      items.push(handoffButton(payload, label, false));
    }
    if (o.contact) { var a = el('a', 'ira-btn', 'Contact page'); a.href = flagUrl('contact.html'); items.push(a); }
    if (o.map) items.push(btn('ira-btn', 'Use the guided map', function () { renderStart(); }));
    // the first action is the main one
    if (o.first && items.length > 1 && o.brief) items.push(items.shift());
    items.forEach(function (x, i) { if (i === 0) x.className += ' ira-primary'; row.appendChild(x); });
    row.appendChild(btn('ira-btn ira-quiet', 'Start over', function () { resetAll(); renderChat(); }));
    log.appendChild(row); scrollLog();
  }
  function render(ops) {
    ops.forEach(function (op) {
      if (op.say) say(op.say);
      else if (op.cards) {
        if (!op.cards.length) return;
        var g = el('div', 'ira-rgrid ira-rgrid-chat');
        var dir = refineDirect(chat.intents);
        op.cards.forEach(function (x) { g.appendChild(card(x, dir)); });
        log.appendChild(g); scrollLog();
      } else if (op.chips) chipRow(op.chips, op.list);
      else if (op.actions) actionRow(op.actions);
    });
  }

  function handle(text) {
    text = String(text || '').trim().slice(0, 1200);
    if (text.length < 2) return;
    staleChips();
    say(text, 'you');
    busy = true; if (sendBtn) sendBtn.disabled = true;
    var wait = say('…'); wait.setAttribute('aria-hidden', 'true');
    loadData().then(function () {
      wait.remove(); render(chatTurn(chat, text));
    }).catch(function () {
      wait.remove();
      say('Sorry, I could not load the page list just now. You can still reach our engineers through the Contact page.');
      var row = el('div', 'ira-actions'); var a = el('a', 'ira-btn ira-primary', 'Contact page'); a.href = flagUrl('contact.html'); row.appendChild(a);
      row.appendChild(btn('ira-btn', 'Try again', function () { row.remove(); handle(text); }));
      log.appendChild(row); scrollLog();
    }).then(function () { busy = false; if (sendBtn) sendBtn.disabled = false; });
  }

  /* =====================================================================================
     Open/close, page entry points, mount
     ===================================================================================== */
  function withData(fn) {
    loadData().then(fn).catch(function () {
      clearView(); setProgress(0);
      view.appendChild(el('p', 'ira-lede', 'Sorry, IRA could not load just now. You can still reach our engineers through the Contact page.'));
      var a = el('a', 'ira-btn ira-primary', 'Go to the Contact page'); a.href = flagUrl('contact.html'); view.appendChild(a);
    });
  }

  var opener = null;
  function setOpen(open, quiet) {
    if (open && panel.hidden) { var ae = document.activeElement; opener = ae && !panel.contains(ae) && ae !== document.body ? ae : null; }
    panel.hidden = !open;
    launcher.setAttribute('aria-expanded', String(open));
    root.classList.toggle('is-open', open);
    document.documentElement.classList.toggle('ira-open', open);
    if (open) {
      if (!view.childNodes.length) withData(renderStart);
    } else {
      cleanupPrint();
      if (!quiet) {
        var back = opener && document.contains(opener) && opener.offsetParent !== null ? opener : launcher;
        setTimeout(function () { back.focus(); }, 0);
      }
    }
  }

  function openAt(track, chatMode) {
    setOpen(true, true);
    withData(function () {
      if (chatMode) return renderChat();
      if (track) { setTrack(track); renderNeeds(); } else renderStart();
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
