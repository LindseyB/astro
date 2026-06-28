/*
 * Date/time fields with digit-only input, auto-delimiter insertion, clear on
 * focus, and a native picker fallback.
 *
 * UX behaviour:
 *   - Focusing a field clears it so the user can type fresh.
 *   - Only digit keys (0-9) are accepted; all other printable characters are
 *     blocked.
 *   - Delimiters are inserted automatically as the user types:
 *       date: YYYY-MM-DD  (dashes added after position 4 and 6 of digits)
 *       time: HH:MM       (colon added after position 2 of digits)
 *   - On blur the value is validated; invalid entries are cleared.
 *   - A calendar/clock button opens the native picker as a fallback.
 */
(function () {
  'use strict';

  function pad(n) { return String(n).padStart(2, '0'); }

  // Strip everything except digits.
  function digitsOnly(s) {
    return (s || '').replace(/\D/g, '');
  }

  // Format up-to-8 raw digits as YYYY-MM-DD (partial is fine while typing).
  function formatDateDigits(digits) {
    var d = digits.slice(0, 8);
    if (d.length <= 4) return d;
    if (d.length <= 6) return d.slice(0, 4) + '-' + d.slice(4);
    return d.slice(0, 4) + '-' + d.slice(4, 6) + '-' + d.slice(6);
  }

  // Format up-to-4 raw digits as HH:MM (partial is fine while typing).
  function formatTimeDigits(digits) {
    var d = digits.slice(0, 4);
    if (d.length <= 2) return d;
    return d.slice(0, 2) + ':' + d.slice(2);
  }

  function buildDate(y, mo, d) {
    var year = parseInt(y, 10);
    var month = parseInt(mo, 10);
    var day = parseInt(d, 10);
    if (!year || month < 1 || month > 12 || day < 1 || day > 31) return '';
    var dt = new Date(Date.UTC(year, month - 1, day));
    if (dt.getUTCFullYear() !== year || (dt.getUTCMonth() + 1) !== month || dt.getUTCDate() !== day) return '';
    return String(year).padStart(4, '0') + '-' + pad(month) + '-' + pad(day);
  }

  // Validate a date string/digits into YYYY-MM-DD, or '' if invalid.
  function normalizeDate(text) {
    var digits = digitsOnly(text);
    if (digits.length !== 8) return '';
    return buildDate(digits.slice(0, 4), digits.slice(4, 6), digits.slice(6, 8));
  }

  // Validate a time string/digits into HH:MM (24h), or '' if invalid.
  function normalizeTime(text) {
    var digits = digitsOnly(text);
    if (digits.length !== 4) return '';
    var h = parseInt(digits.slice(0, 2), 10);
    var m = parseInt(digits.slice(2, 4), 10);
    if (h > 23 || m > 59) return '';
    return pad(h) + ':' + pad(m);
  }

  function wire(textId, nativeId, btnId, formatter, normalizer) {
    var text = document.getElementById(textId);
    if (!text) return;
    var native = document.getElementById(nativeId);
    var btn = document.getElementById(btnId);

    // Requirement 1: clear field on focus so the user can type fresh.
    text.addEventListener('focus', function () {
      text.value = '';
    });

    // Requirement 3: only accept digit keys (plus navigation/editing keys).
    text.addEventListener('keydown', function (e) {
      var navigation = [
        'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
        'ArrowUp', 'ArrowDown', 'Tab', 'Home', 'End'
      ];
      if (navigation.indexOf(e.key) !== -1) return;
      if (e.ctrlKey || e.metaKey) return; // allow copy / paste / select-all
      // Only block printable characters; allow Enter/Escape/function keys, etc.
      if (e.key.length === 1 && !/^\d$/.test(e.key)) {
        e.preventDefault();
      }
    });

    // Requirement 2: auto-insert delimiters as digits accumulate.
    text.addEventListener('input', function () {
      var digits = digitsOnly(text.value);
      var formatted = formatter(digits);
      if (text.value !== formatted) {
        text.value = formatted;
      }
    });

    if (btn && native) {
      btn.addEventListener('click', function () {
        // Seed the native control with the current value so it opens there.
        native.value = normalizer(text.value) || native.value;
        try {
          native.showPicker();
        } catch (e) {
          native.focus();
          native.click();
        }
      });
      native.addEventListener('change', function () {
        if (!native.value) return;
        text.value = native.value; // native date/time value is already canonical
        text.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }

    // Validate and normalize when the field loses focus.
    text.addEventListener('blur', function () {
      var normalized = normalizer(text.value);
      var raw = (text.value || '').trim();
      if (raw && !normalized) {
        text.value = '';
        text.dispatchEvent(new Event('change', { bubbles: true }));
        return;
      }
      if (normalized && normalized !== text.value) {
        text.value = normalized;
        text.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    wire('birth_date', 'birth_date_native', 'birth_date_btn', formatDateDigits, normalizeDate);
    wire('birth_time', 'birth_time_native', 'birth_time_btn', formatTimeDigits, normalizeTime);
  });
})();
