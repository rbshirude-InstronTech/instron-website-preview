/* Offline review interactions. No analytics, cookies, input storage, remote requests or automatic sending. */
(()=>{'use strict';
 const nav=document.getElementById('it-navigation'),toggle=document.getElementById('it-toggle');
 const buttons=Array.from(document.querySelectorAll('.it-trigger'));
 const panelFor=b=>document.getElementById(b.getAttribute('aria-controls'));
 function closeAll(except,restore){let previous=null;buttons.forEach(b=>{if(b===except)return;if(b.getAttribute('aria-expanded')==='true')previous=b;b.setAttribute('aria-expanded','false');const p=panelFor(b);if(p)p.hidden=true});if(restore&&previous)previous.focus()}
 function openMenu(b){closeAll(b,false);b.setAttribute('aria-expanded','true');const p=panelFor(b);if(p)p.hidden=false}
 buttons.forEach(b=>{
  b.addEventListener('click',()=>{const wasOpen=b.getAttribute('aria-expanded')==='true';closeAll(null,false);if(!wasOpen)openMenu(b)});
  b.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();openMenu(b);panelFor(b)?.querySelector('a')?.focus()}if(e.key==='ArrowUp'){e.preventDefault();openMenu(b);const links=panelFor(b)?.querySelectorAll('a');if(links?.length)links[links.length-1].focus()}});
  panelFor(b)?.addEventListener('keydown',e=>{const links=Array.from(panelFor(b).querySelectorAll('a'));const i=links.indexOf(document.activeElement);if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();links[(i+(e.key==='ArrowDown'?1:-1)+links.length)%links.length]?.focus()}if(e.key==='Home'){e.preventDefault();links[0]?.focus()}if(e.key==='End'){e.preventDefault();links[links.length-1]?.focus()}});
 });
 function closeMobile(){if(!nav||!toggle)return;nav.classList.remove('open');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-label','Ouvrir la navigation');closeAll(null,false)}
 toggle?.addEventListener('click',()=>{const open=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Fermer la navigation':'Ouvrir la navigation');if(!open)closeAll(null,false)});
 document.addEventListener('keydown',e=>{if(e.key!=='Escape')return;const panelOpen=buttons.some(b=>b.getAttribute('aria-expanded')==='true');if(panelOpen){e.preventDefault();closeAll(null,true)}else if(nav?.classList.contains('open')){e.preventDefault();closeMobile();toggle.focus()}});
 document.addEventListener('click',e=>{if(!e.target.closest('.it-group'))closeAll(null,false);if(nav?.classList.contains('open')&&!e.target.closest('.it-header'))closeMobile()});
 document.addEventListener('focusin',e=>{if(!e.target.closest('.it-nav'))closeAll(null,false)});
 nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMobile));
 const mobileQuery=window.matchMedia('(max-width:1120px)');mobileQuery.addEventListener?.('change',closeMobile);
 const search=document.getElementById('it-page-search');
 if(search){const cards=Array.from(document.querySelectorAll('.it-page-card'));const status=document.getElementById('it-search-result');search.addEventListener('input',()=>{const q=search.value.trim().toLocaleLowerCase();let count=0;cards.forEach(c=>{const wrap=c.closest('.directory-item');const hay=(wrap||c).textContent.toLocaleLowerCase();const visible=hay.includes(q);c.hidden=!visible;if(wrap)wrap.hidden=!visible;if(visible)count++});document.querySelectorAll('.solutions-flagship').forEach(g=>g.hidden=!Array.from(g.querySelectorAll('.it-page-card')).some(c=>!c.hidden));document.querySelectorAll('.it-index-content>section').forEach(sec=>{const list=sec.querySelectorAll('.it-page-card');if(list.length)sec.hidden=!Array.from(list).some(c=>!c.hidden)});if(status)status.textContent=q?(count?count+' page'+(count===1?' trouvée.':'s trouvées.'):'Aucune page ne correspond. Essayez le nom d’une solution, d’un secteur ou d’une application.') :''});}
 document.querySelectorAll('[data-open-layer]').forEach(b=>{const d=document.getElementById(b.dataset.openLayer);if(!d)return;const sync=()=>b.setAttribute('aria-expanded',String(d.open));sync();d.addEventListener('toggle',sync);b.addEventListener('click',()=>{d.open=true;sync();d.querySelector('summary')?.focus({preventScroll:true});if(window.matchMedia('(max-width:900px)').matches)d.scrollIntoView({block:'center',behavior:window.matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'})});});
 function revealFragment(){if(!location.hash)return;let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return}const target=document.getElementById(id);if(!target)return;for(let parent=target.parentElement;parent;parent=parent.parentElement){if(parent.tagName==='DETAILS')parent.open=true}}
 window.addEventListener('hashchange',revealFragment);revealFragment();
 if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion:reduce)').matches){const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('is-revealed');observer.unobserve(e.target)}}),{threshold:.12});document.querySelectorAll('.flagship-card,.journey-stage,.why-card,.detail-card,.project-slot,.engineering-system,.related-link').forEach(el=>observer.observe(el));}
 const form=document.getElementById('enquiry-draft');
 if(form){
  form.addEventListener('submit',e=>e.preventDefault());const status=document.getElementById('enquiry-result');
  function enquiry(){const d=new FormData(form);return ['Instron Technologies - Demande technique','Nom : '+d.get('name'),'Courriel professionnel : '+d.get('email'),'Organisation : '+d.get('company'),'Pays : '+d.get('country'),'Domaine d’intérêt : '+(d.get('type')||'Non précisé'),'Étape du projet : '+(d.get('stage')||'Non précisé'),'Téléphone : '+(d.get('phone')||'Non précisé'),'','Description du projet :',d.get('challenge')].join('\n')}
  document.getElementById('open-enquiry')?.addEventListener('click',()=>{if(!form.reportValidity())return;const a=document.createElement('a');a.href='mailto:sales@instrontechnologies.com?subject='+encodeURIComponent('Demande technique Instron')+'&body='+encodeURIComponent(enquiry());a.target='_top';document.body.append(a);a.click();a.remove();status.textContent='Votre logiciel de courriel s’ouvre. Aucun message n’a été envoyé par ce site.'});
  document.getElementById('copy-enquiry')?.addEventListener('click',async()=>{if(!form.reportValidity())return;const value=enquiry();try{if(!navigator.clipboard?.writeText)throw new Error('Copy manually');await navigator.clipboard.writeText(value);status.textContent='Texte de la demande copié sur votre appareil. Aucun message n’a été envoyé.'}catch{let t=document.getElementById('enquiry-copy-fallback');if(!t){t=document.createElement('textarea');t.id='enquiry-copy-fallback';t.readOnly=true;t.rows=12;t.setAttribute('aria-label','Texte de la demande à copier');form.append(t)}t.value=value;t.focus();t.select();status.textContent='Sélectionnez et copiez le texte de la demande ci-dessous. Aucun message n’a été envoyé.'}});
 }
})();

/* v2.20: on a laptop (mouse, wide screen) clicking Solutions / Industries / How We Work opens that page; the list opens on hover. Touch screens keep tap-to-open. */
(()=>{'use strict';const mq=window.matchMedia('(min-width:1121px) and (hover:hover) and (pointer:fine)');
 document.querySelectorAll('.it-trigger').forEach(b=>{const p=document.getElementById(b.getAttribute('aria-controls'));const all=p&&p.querySelector('.it-viewall');if(!all)return;
  b.addEventListener('click',e=>{if(!mq.matches)return;e.preventDefault();e.stopImmediatePropagation();all.click()},true);});
})();

/* v2.21: filter links. A link to a filter option id (e.g. portfolio #pf-auto) selects that option. */
(()=>{'use strict';const pick=id=>{const el=id&&document.getElementById(id);if(!el||el.tagName!=='INPUT'||(el.type!=='radio'&&el.type!=='checkbox'))return;el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));const box=el.closest('section')||el.parentElement;if(box)setTimeout(()=>box.scrollIntoView({block:'start'}),60)};
 const fromHash=()=>{if(!location.hash)return;try{pick(decodeURIComponent(location.hash.slice(1)))}catch{}};window.addEventListener('hashchange',fromHash);fromHash();
 window.addEventListener('message',e=>{const m=e.data;if(m&&typeof m==='object'&&m.kind==='instron-review-scroll'&&m.section)pick(m.section)});
})();
