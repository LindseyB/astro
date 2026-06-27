(function () {

  // Panel open / close
  var overlay = document.getElementById('panelOverlay');
  var panel = document.getElementById('birthPanel');
  var main = document.getElementById('main-content');
  var header = document.getElementById('siteHeader');
  var openBtn = document.getElementById('birthInfoBtn');
  var closeBtn = document.getElementById('panelClose');
  var pending = null; // action URL queued while panel was opened
  var lastFocused = null;
  var releaseTrap = null;

  function isVisible(el) {
    return !!(el && (el.offsetWidth || el.offsetHeight || el.getClientRects().length));
  }

  function getFocusable(container) {
    if (!container) return [];
    var selectors = [
      'a[href]', 'area[href]', 'button:not([disabled])',
      'input:not([disabled]):not([type="hidden"])', 'select:not([disabled])',
      'textarea:not([disabled])', '[tabindex]:not([tabindex="-1"])'
    ];
    return Array.prototype.slice.call(container.querySelectorAll(selectors.join(',')))
      .filter(function (el) { return !el.hasAttribute('inert') && isVisible(el); });
  }

  function trapFocus(container) {
    function onKeyDown(e) {
      if (e.key !== 'Tab') return;
      var focusable = getFocusable(container);
      if (!focusable.length) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }

    container.addEventListener('keydown', onKeyDown);
    return function () {
      container.removeEventListener('keydown', onKeyDown);
    };
  }

  function setBackgroundInert(isInert) {
    [header, main].forEach(function (el) {
      if (!el) return;
      if (isInert) {
        el.setAttribute('inert', '');
      } else {
        el.removeAttribute('inert');
      }
    });
  }

  function releaseFocusTrap() {
    if (releaseTrap) {
      releaseTrap();
      releaseTrap = null;
    }
  }

  function activateDialog(dialogRoot, fallbackFocusEl) {
    releaseFocusTrap();
    releaseTrap = trapFocus(dialogRoot);
    var focusable = getFocusable(dialogRoot);
    if (focusable.length) {
      focusable[0].focus();
    } else if (fallbackFocusEl) {
      fallbackFocusEl.focus();
    }
  }

  function restoreLastFocus() {
    if (lastFocused && typeof lastFocused.focus === 'function') {
      lastFocused.focus();
    }
  }

  function panelIsOpen() {
    return panel.classList.contains('open');
  }

  function askModalIsOpen() {
    return askOverlay.classList.contains('open');
  }

  function openPanel(action, trigger) {
    lastFocused = trigger || document.activeElement;
    pending = action || null;
    panel.classList.add('open');
    overlay.classList.add('open');
    panel.removeAttribute('inert');
    panel.setAttribute('aria-hidden', 'false');
    openBtn.setAttribute('aria-expanded', 'true');
    setBackgroundInert(true);
    document.body.style.overflow = 'hidden';
    // show/hide question textarea
    var qSection = document.getElementById('questionSection');
    if (action === '/ask-anything') {
      qSection.style.display = '';
    } else {
      qSection.style.display = 'none';
    }
    activateDialog(panel, closeBtn);
  }

  function closePanel(options) {
    options = options || {};
    panel.classList.remove('open');
    overlay.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    panel.setAttribute('inert', '');
    openBtn.setAttribute('aria-expanded', 'false');
    releaseFocusTrap();
    if (!askModalIsOpen()) {
      setBackgroundInert(false);
    }
    document.body.style.overflow = '';
    if (!options.keepPending) {
      pending = null;
    }
    if (options.restoreFocus !== false) {
      restoreLastFocus();
    }
  }

  openBtn.addEventListener('click', function () { openPanel(null, openBtn); });
  closeBtn.addEventListener('click', function () { closePanel(); });
  overlay.addEventListener('click', function () { closePanel(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (askModalIsOpen()) {
      closeAskModal();
      return;
    }
    if (panelIsOpen()) {
      closePanel();
    }
  });

  // Ask the stars modal
  var askOverlay = document.getElementById('askModalOverlay');
  var askDialog = askOverlay.querySelector('.ask-modal');
  var askInput = document.getElementById('askModalInput');
  var askSubmit = document.getElementById('askModalSubmit');
  var askClose = document.getElementById('askModalClose');

  function openAskModal(trigger) {
    lastFocused = trigger || document.activeElement;
    askInput.value = document.getElementById('question_prompt').value || '';
    askOverlay.classList.add('open');
    askOverlay.setAttribute('aria-hidden', 'false');
    setBackgroundInert(true);
    document.body.style.overflow = 'hidden';
    activateDialog(askDialog, askInput);
  }

  function closeAskModal(options) {
    options = options || {};
    askOverlay.classList.remove('open');
    askOverlay.setAttribute('aria-hidden', 'true');
    releaseFocusTrap();
    if (!panelIsOpen()) {
      setBackgroundInert(false);
    }
    document.body.style.overflow = '';
    if (options.restoreFocus !== false) {
      restoreLastFocus();
    }
  }

  askClose.addEventListener('click', function () { closeAskModal(); });
  askOverlay.addEventListener('click', function (e) {
    if (e.target === askOverlay) closeAskModal();
  });
  askSubmit.addEventListener('click', function () {
    var q = askInput.value.trim();
    if (!q) {
      askInput.focus();
      return;
    }
    document.getElementById('question_prompt').value = q;
    if (hasBirthData()) {
      closeAskModal({ restoreFocus: false });
      submitToAction('/ask-anything');
    } else {
      // Still need birth info, so hand off to the side panel and keep question.
      closeAskModal({ restoreFocus: false });
      openPanel('/ask-anything', document.getElementById('askStarsTile'));
    }
  });

  // Tile interactions
  var actionTiles = Array.prototype.slice.call(document.querySelectorAll('.tile[data-action]'));
  var reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

  function allowTileGlowMotion() {
    return !reduceMotionQuery.matches;
  }

  function setTileGlowPosition(tile, clientX, clientY) {
    if (!allowTileGlowMotion()) return;
    var rect = tile.getBoundingClientRect();
    var x = clientX - rect.left;
    var y = clientY - rect.top;
    tile.style.setProperty('--edge-glow-x', x + 'px');
    tile.style.setProperty('--edge-glow-y', y + 'px');
  }

  actionTiles.forEach(function (tile) {
    tile.addEventListener('pointerenter', function (e) {
      if (!allowTileGlowMotion()) return;
      setTileGlowPosition(tile, e.clientX, e.clientY);
      tile.classList.add('glow-active');
    });

    tile.addEventListener('pointermove', function (e) {
      if (!allowTileGlowMotion()) return;
      setTileGlowPosition(tile, e.clientX, e.clientY);
    });

    // Fallback for environments that dispatch mouse events but not pointer events.
    tile.addEventListener('mouseenter', function (e) {
      if (!allowTileGlowMotion()) return;
      setTileGlowPosition(tile, e.clientX, e.clientY);
      tile.classList.add('glow-active');
    });

    tile.addEventListener('mousemove', function (e) {
      if (!allowTileGlowMotion()) return;
      setTileGlowPosition(tile, e.clientX, e.clientY);
    });

    tile.addEventListener('pointerleave', function () {
      tile.classList.remove('glow-active');
      tile.style.setProperty('--edge-glow-x', '92%');
      tile.style.setProperty('--edge-glow-y', '8%');
    });

    tile.addEventListener('mouseleave', function () {
      tile.classList.remove('glow-active');
      tile.style.setProperty('--edge-glow-x', '92%');
      tile.style.setProperty('--edge-glow-y', '8%');
    });

    tile.addEventListener('focus', function () {
      tile.classList.add('glow-active');
      tile.style.setProperty('--edge-glow-x', '92%');
      tile.style.setProperty('--edge-glow-y', '8%');
    });

    tile.addEventListener('blur', function () {
      tile.classList.remove('glow-active');
    });

    // Respect reduced-motion preference changes in real-time.
    if (typeof reduceMotionQuery.addEventListener === 'function') {
      reduceMotionQuery.addEventListener('change', function () {
        tile.classList.remove('glow-active');
        tile.style.setProperty('--edge-glow-x', '92%');
        tile.style.setProperty('--edge-glow-y', '8%');
      });
    }

    tile.addEventListener('click', function () {
      var action = tile.dataset.action;
      if (action === '/ask-anything') {
        openAskModal(tile);
        return;
      }
      if (!hasBirthData()) {
        openPanel(action, tile);
        return;
      }
      submitToAction(action);
    });
  });

  // Save & continue
  function setPanelError(message) {
    var el = document.getElementById('locationSearchError');
    if (!el) return;
    el.textContent = message || '';
    el.hidden = !message;
  }

  document.getElementById('panelSaveBtn').addEventListener('click', function () {
    setPanelError('');
    if (!hasBirthData()) {
      setPanelError('Please fill in birth date, time, timezone, and location.');
      return;
    }
    var action = pending || '/chart';
    if (action === '/ask-anything') {
      var q = document.getElementById('question_prompt').value.trim();
      if (!q) {
        setPanelError('Please enter your question.');
        return;
      }
    }
    closePanel({ restoreFocus: false });
    submitToAction(action);
  });

  // Clear data
  document.getElementById('clearDataBtn').addEventListener('click', function () {
    try {
      localStorage.removeItem('astro_form_data');
    } catch (e) {
      console.warn('Failed to clear form data from localStorage:', e);
    }
    ['birth_date', 'birth_time', 'timezone_offset', 'latitude', 'longitude', 'music_genre', 'other_genre', 'question_prompt']
      .forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.value = '';
      });
  });

  // Helpers
  // Read saved chart info persisted by form-persistence.js (key: astro_form_data)
  function getSavedFormData() {
    try {
      var stored = localStorage.getItem('astro_form_data');
      if (!stored) return {};
      var parsed = JSON.parse(stored);
      return parsed.data || parsed || {};
    } catch (e) {
      return {};
    }
  }

  // Field value preferring the live DOM, falling back to saved chart info
  // (the timezone Select2 widget doesn't always reflect its value on the native input)
  function fieldVal(id) {
    var el = document.getElementById(id);
    var domVal = el ? (el.value || '').trim() : '';
    if (domVal) return domVal;
    var saved = getSavedFormData();
    return (saved[id] || '').toString().trim();
  }

  function hasBirthData() {
    return !!(
      fieldVal('birth_date') &&
      fieldVal('birth_time') &&
      fieldVal('timezone_offset') &&
      fieldVal('latitude') &&
      fieldVal('longitude')
    );
  }

  function submitToAction(action) {
    var form = document.getElementById('masterForm');
    form.action = action;
    document.getElementById('f_birth_date').value = fieldVal('birth_date');
    document.getElementById('f_birth_time').value = fieldVal('birth_time');
    document.getElementById('f_timezone_offset').value = fieldVal('timezone_offset');
    document.getElementById('f_latitude').value = fieldVal('latitude');
    document.getElementById('f_longitude').value = fieldVal('longitude');
    document.getElementById('f_music_genre').value = fieldVal('music_genre');
    document.getElementById('f_other_genre').value = fieldVal('other_genre');
    document.getElementById('f_question_prompt').value = document.getElementById('question_prompt').value || '';
    form.submit();
  }

  // Flash message (auto-hides)
  function showFlash(message, duration) {
    var toast = document.getElementById('flashToast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(showFlash._timer);
    showFlash._timer = setTimeout(function () {
      toast.classList.remove('show');
    }, duration || 6000);
  }

  // First visit: prompt for birth info
  // If nothing has been saved yet, open the panel and nudge the user.
  if (!hasBirthData()) {
    openPanel(null, openBtn);
    showFlash('Please enter your birth information');
  }
})();
