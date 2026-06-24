/*
 * Free-typing date/time fields with a native picker fallback.
 *
 * The visible Date/Time fields are plain text inputs so users can type a
 * far-away birth date directly (native <input type="date"> only lets you
 * edit fixed segments). A calendar/clock button opens the native picker,
 * and typed text is normalized to the canonical format on blur:
 *   date -> YYYY-MM-DD   time -> HH:MM (24h)
 */
(function () {
  'use strict';

  function pad(n) { return String(n).padStart(2, '0'); }

  function buildDate(y, mo, d) {
    var year = parseInt(y, 10);
    var month = parseInt(mo, 10);
    var day = parseInt(d, 10);
    if (!year || month < 1 || month > 12 || day < 1 || day > 31) return '';
    return String(year).padStart(4, '0') + '-' + pad(month) + '-' + pad(day);
  }

  // Parse flexible date text into YYYY-MM-DD, or '' if unparseable.
  function normalizeDate(text) {
    var s = (text || '').trim();
    if (!s) return '';
    var m;
    // YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
    if ((m = s.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$/))) {
      return buildDate(m[1], m[2], m[3]);
    }
    // MM/DD/YYYY / M/D/YYYY / MM-DD-YYYY (US order)
    if ((m = s.match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$/))) {
      return buildDate(m[3], m[1], m[2]);
    }
    // Plain 8 digits: YYYYMMDD
    if ((m = s.match(/^(\d{4})(\d{2})(\d{2})$/))) {
      return buildDate(m[1], m[2], m[3]);
    }
    // Month names: "July 15, 1990" / "15 Jul 1990"
    var d = new Date(s);
    if (!isNaN(d.getTime())) {
      return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    }
    return '';
  }

  // Parse flexible time text into HH:MM (24h), or '' if unparseable.
  function normalizeTime(text) {
    var s = (text || '').trim();
    if (!s) return '';
    var m = s.match(/^(\d{1,2})(?::?(\d{2}))?\s*([ap]\.?m\.?)?$/i);
    if (!m) return '';
    var h = parseInt(m[1], 10);
    var min = m[2] ? parseInt(m[2], 10) : 0;
    var ampm = m[3] ? m[3].toLowerCase().charAt(0) : '';
    if (ampm === 'p' && h < 12) h += 12;
    if (ampm === 'a' && h === 12) h = 0;
    if (h > 23 || min > 59) return '';
    return pad(h) + ':' + pad(min);
  }

  function wire(textId, nativeId, btnId, normalizer) {
    var text = document.getElementById(textId);
    if (!text) return;
    var native = document.getElementById(nativeId);
    var btn = document.getElementById(btnId);

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

    // Normalize free-typed text when the field loses focus.
    text.addEventListener('blur', function () {
      var normalized = normalizer(text.value);
      if (normalized && normalized !== text.value) {
        text.value = normalized;
        text.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    wire('birth_date', 'birth_date_native', 'birth_date_btn', normalizeDate);
    wire('birth_time', 'birth_time_native', 'birth_time_btn', normalizeTime);
  });
})();
