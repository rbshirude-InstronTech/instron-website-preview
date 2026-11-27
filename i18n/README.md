# French (Canada) pages: fr-CA

v2.46 (27 Nov 2026). First French set: 8 core pages in `fr/`, built from the English pages by `tools/i18n_fr.py`.

| French page | English source |
|---|---|
| fr/index.html | Home |
| fr/process-skid-plants.html | Process Skid Plants |
| fr/industrial-automation.html | Industrial Automation |
| fr/planton-digital-factory.html | PlantON™ by Instron Technologies |
| fr/how-we-work.html | How We Work |
| fr/global-presence.html | Global Presence & Partners |
| fr/contact.html | Contact |
| fr/privacy-terms-accessibility.html | Privacy, Terms & Accessibility |

## How it works
- `i18n/fr-CA.json` holds every English string on these pages with its French line (1,056 strings, about 8,800 English words). `i18n/fr-CA-review.csv` is the same list as a sheet for a reviewer.
- `tools/build.py` runs `i18n_fr.py build` at the end of every sync, so the French pages follow the English layout and images. If English copy changes in the review build, that string shows in English on the French page until it gets a French line: run `python3 -I tools/i18n_fr.py extract .` then `report .` to list them.
- Every English page gets a "Français" link in the top bar (to its French page, or to French Home when there is none yet). French pages get an "English" link back. Both carry hreflang tags (en, fr-CA, x-default).
- On French pages: `lang="fr-CA"`, French title, description and share text, canonical `/fr/...`, French site script (`assets/js/site-fr.js`: menu labels, search messages and the email draft). The IRA guide is not loaded (English only for now).
- Contact form: labels and choices are French; the values sent in the email stay English, so sales and ERPNext see the same values whatever the language.

## Style and glossary (Quebec French)
Courriel (not e-mail), "Nous joindre", Quebec spacing for numbers (1 000, 15 %), no long dashes. Customer testimonials are translated and marked "(Traduit de l’anglais)".

| English | French used |
|---|---|
| Process Skid Plants | Usines de procédé sur skid |
| Pilot & Demonstration Plants | Usines pilotes et de démonstration |
| Industrial Process Skids | Skids de procédé industriels |
| Industrial Automation | Automatisation industrielle |
| Industrial Automation & Controls | Automatisation et contrôle industriels |
| PlantON™ by Instron Technologies | PlantON™ par Instron Technologies |
| How We Work | Notre façon de travailler |
| Discuss Your Project | Parlons de votre projet |
| Basic Engineering & Feasibility | Ingénierie de base et faisabilité |
| Detailed Engineering | Ingénierie détaillée |
| Integrated Design & Build | Conception et construction intégrées |
| OEE | TRG (OEE) |
| CIP | NEP (CIP) |
| I/O | E/S |
| E&I | É-I |
| commissioning | mise en service |
| FAT / SAT | FAT / SAT (essais en usine / essais sur site) |
| control panel | panneau de commande |
| utilities | utilités |
| EHS | santé, sécurité et environnement (SSE) |
| API (active pharmaceutical ingredient) | IPA (ingrédient pharmaceutique actif); in French "API" means a PLC |
| pilot (the plant) | usine pilote / unité pilote, never "pilote" alone |
| QA/QC | AQ/CQ |
| battery limits | limites de batterie |
| heat & mass balance | bilan de matière et d’énergie |
| gas handling / fluid handling | manipulation des gaz / transfert des fluides |
| equipment arrangement / layout | implantation des équipements |
| equipment duty (in service) | tenue en service des équipements |
| relief and venting | protection contre les surpressions et évents |
| HAZOP deviations | dérives |
| fail-safe state | état de repli sûr |
| S88 control module | module de commande |
| hygienic design | conception hygiénique |
| long-lead items | équipements à long délai de livraison |
| compounding plant | usine de formulation |
| Let's grow together | Grandissons ensemble |
| Independent company, not affiliated with Instron® (ITW) | Société indépendante, non affiliée à Instron® (ITW) |
| Engineer \| Embrace \| Elevate | kept in English (see decisions) |

## QA pass (27 Nov 2026)
Reviewer role: bilingual process and automation engineer. Checked all 1,056 strings for numbers, units and standards (EN vs FR), protected names (PlantON™, platforms, standards, entities), terminology, Quebec usage and typography, then all 8 pages at 1024, 1180, 1280, 1366 and 390 px.
Fixed: "API" (pharma) changed to IPA, because API means a PLC in French; "pilote" alone changed to "usine pilote" / "unité pilote"; EHS changed to SSE; "Les résultats de laboratoire ne prouvent pas l’échelle" reworded; "01 / Sujet" changed to "01 / Politique"; four page titles shortened to 65 characters or less; privacy sub-menu labels shortened (they wrapped and the last one was cut off on desktop); spacing before % made non-breaking; "site torontois" changed to "site de Toronto".
Clean: no number, unit or standard changed meaning; no English left (except legal names of foreign laws, kept on purpose); no long dashes; no overflow on any page; menus, language switch and email draft work in French; no console errors.

## Process engineering pass (27 Nov 2026)
Reviewer role: process engineer. Read every string on unit operations, equipment, scale-up, process documents and process safety (about 400 strings).
Fixed (19 strings): "manutention" (materials handling) used for gases and fluids, now manipulation des gaz / transfert des fluides; battery limits now limites de batterie (was "limites de fourniture", which means scope of supply); equipment duty now tenue en service; "un pilote" now une usine pilote; equipment arrangements now implantation; control devices now appareils de régulation; PFD named after "schémas de procédé"; hygienic design; S88 control modules now modules de commande (IEC 61512 wording); fail-safe now états de repli sûrs; relief and venting now protection contre les surpressions et évents; HAZOP deviations now dérives; "dossier constructible" now dossier prêt pour la construction; long-lead items now équipements à long délai de livraison; Instrumentation et capteurs.
Confirmed correct: bilan de matière et d’énergie, liste des lignes, plan d’ensemble, encombrement, matrice causes-effets, philosophie de contrôle, déclenchements intempestifs, permissifs, verrouillages, conchage / affinage / tempérage, hydrocraquage, électrolyseur, AACE class 4 / class 2 wording, TRL scale.

## Open decisions before French goes live
1. **Tagline** kept in English everywhere. Ask the legal reviewer whether it needs a French version on French pages under Quebec's Charter of the French Language.
2. **Privacy page**: French text needs the legal reviewer (LEG-01) before launch. Once approved, change "French version available on request" on the English page to a link to `fr/privacy-terms-accessibility.html`.
3. **Names**: confirm the French solution names above with a Quebec engineer or client.
4. **French enquiries**: decide who answers enquiries written in French.
5. **Coverage**: the menu and footer link to English pages that are not translated yet (industries, applications, case studies, About Us pages).
6. **WordPress**: the WordPress package (v2.45) does not include the French pages yet; add them in the next package build.
7. **Launch**: add the French pages to sitemap.xml and llms.txt when GO_LIVE is set; share images (assets/og) still carry English titles.
