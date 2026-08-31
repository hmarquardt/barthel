(function () {
  'use strict';

  /* ---- mobile navigation ---- */
  var toggle = document.querySelector('.nav-toggle');
  var panel = document.getElementById('mobile-nav');
  var closeBtn = panel ? panel.querySelector('.mobile-nav__close') : null;
  var scrim = panel ? panel.querySelector('.scrim') : null;

  function openNav() {
    if (!panel) return;
    panel.hidden = false;
    panel.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();
  }

  function closeNav() {
    if (!panel) return;
    panel.hidden = true;
    panel.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    toggle.focus();
  }

  function shutNav() {
    if (!panel || panel.hidden) return;
    panel.hidden = true;
    panel.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (toggle && panel) {
    toggle.addEventListener('click', openNav);
    if (closeBtn) closeBtn.addEventListener('click', closeNav);
    if (scrim) scrim.addEventListener('click', closeNav);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hidden) closeNav();
    });
    panel.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', shutNav);
    });
  }

  /* ---- contact form: client-side validation only (no data submission) ---- */
  var form = document.getElementById('contact-form');
  if (form) {
    var success = document.getElementById('form-success');

    function setError(field, msg) {
      var wrap = field.closest('.form-field');
      var err = wrap.querySelector('.error');
      if (msg) {
        field.setAttribute('aria-invalid', 'true');
        if (err) err.textContent = msg;
      } else {
        field.removeAttribute('aria-invalid');
        if (err) err.textContent = '';
      }
    }

    function validateField(field) {
      var v = field.value.trim();
      if (field.hasAttribute('required') && !v) {
        setError(field, 'This field is required.');
        return false;
      }
      if (field.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) {
        setError(field, 'Please enter a valid email address.');
        return false;
      }
      setError(field, null);
      return true;
    }

    form.querySelectorAll('input, textarea').forEach(function (f) {
      f.addEventListener('blur', function () {
        validateField(f);
      });
      f.addEventListener('input', function () {
        if (f.getAttribute('aria-invalid') === 'true') validateField(f);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var allValid = true;
      var firstBad = null;
      form.querySelectorAll('input, textarea').forEach(function (f) {
        var ok = validateField(f);
        if (!ok && !firstBad) firstBad = f;
        allValid = allValid && ok;
      });
      if (!allValid) {
        if (firstBad) firstBad.focus();
        return;
      }
      if (success) {
        success.classList.add('is-visible');
        success.setAttribute('tabindex', '-1');
        success.focus();
      }
      form.reset();
    });
  }

  /* ---- character counter for message field ---- */
  var msg = document.getElementById('cf-message');
  var counter = document.getElementById('cf-message-count');
  if (msg && counter) {
    var update = function () {
      counter.textContent = Math.max(0, 1000 - msg.value.length) + ' characters remaining';
    };
    msg.addEventListener('input', update);
    update();
  }
})();
