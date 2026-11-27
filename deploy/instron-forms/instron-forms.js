/* Instron Technologies Forms: sends the website forms to our own server (no third-party form service).
 * Enhances:
 *   - the Contact page enquiry form  (form#enquiry-draft, or any form[data-instron-form="enquiry"])
 *   - a careers application form     (form[data-instron-form="application"], multipart, optional "cv" file)
 * Without JavaScript or if sending fails, the existing "Open email draft" / mailto route still works.
 */
(function () {
  'use strict';
  var cfg = window.InstronForms || {};
  var loadedAt = Date.now();

  function addHidden(form) {
    // Honeypot (hidden from people and screen readers) and load time for bot checks.
    if (!form.querySelector('input[name="website"]')) {
      var trap = document.createElement('div');
      trap.setAttribute('aria-hidden', 'true');
      trap.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden';
      trap.innerHTML = '<label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label>';
      form.appendChild(trap);
    }
    var ts = form.querySelector('input[name="_ts"]');
    if (!ts) {
      ts = document.createElement('input');
      ts.type = 'hidden'; ts.name = '_ts';
      form.appendChild(ts);
    }
    ts.value = String(loadedAt);
  }

  function statusBox(form) {
    var box = form.querySelector('.instron-form-status');
    if (!box) {
      box = document.createElement('p');
      box.className = 'instron-form-status';
      box.setAttribute('role', 'status');
      box.setAttribute('aria-live', 'polite');
      box.style.cssText = 'margin:14px 0 0;font-size:15px';
      form.appendChild(box);
    }
    return box;
  }

  function send(form, url, asJson, button) {
    if (!form.reportValidity()) return;
    var box = statusBox(form);
    var label = button.textContent;
    button.disabled = true; button.textContent = 'Sending...';
    box.textContent = '';
    var data = new FormData(form);
    data.set('_ts', String(loadedAt));
    var opts = { method: 'POST', credentials: 'same-origin' };
    if (asJson) {
      var obj = {};
      data.forEach(function (v, k) { if (typeof v === 'string') obj[k] = v; });
      obj.page = location.href;
      opts.headers = { 'Content-Type': 'application/json' };
      opts.body = JSON.stringify(obj);
    } else {
      opts.body = data;
    }
    fetch(url, opts)
      .then(function (r) { return r.json().catch(function () { return { ok: false }; }); })
      .then(function (res) {
        box.textContent = res.message || (res.ok ? 'Thank you. Your message has been sent.' :
          'The message could not be sent. Please email us directly.');
        box.style.color = res.ok ? '#1b6b2f' : '#a12a1a';
        if (res.ok) form.reset();
      })
      .catch(function () {
        box.textContent = 'The message could not be sent. Please use "Open email draft" or email us directly.';
        box.style.color = '#a12a1a';
      })
      .then(function () { button.disabled = false; button.textContent = label; });
  }

  function enhance(form, kind) {
    var url = cfg[kind];
    if (!url || form.dataset.instronEnhanced) return;
    form.dataset.instronEnhanced = '1';
    form.removeAttribute('onsubmit');
    addHidden(form);

    var btn = form.querySelector('[data-instron-submit]');
    if (!btn) {
      btn = document.createElement('button');
      btn.type = 'submit';
      btn.className = 'button dark';
      btn.setAttribute('data-instron-submit', '');
      btn.textContent = kind === 'application' ? 'Send application' : 'Send enquiry';
      var draft = form.querySelector('#open-enquiry');
      if (draft) {
        draft.className = draft.className.replace(/\bdark\b/, 'neutral');
        draft.parentNode.insertBefore(btn, draft);
      } else {
        form.appendChild(btn);
      }
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      send(form, url, kind === 'enquiry', btn);
    });
  }

  function init() {
    var enquiry = document.querySelectorAll('form#enquiry-draft, form[data-instron-form="enquiry"]');
    for (var i = 0; i < enquiry.length; i++) enhance(enquiry[i], 'enquiry');
    var apps = document.querySelectorAll('form[data-instron-form="application"]');
    for (var j = 0; j < apps.length; j++) enhance(apps[j], 'application');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
