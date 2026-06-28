// Deprecated compatibility adapter. New behavior lives in js/components/astro-section-toggle.js.

function updateSectionState(content, toggleIcon, header, expanded) {
    if (!content || !header) {
        return;
    }

    if (expanded) {
        content.classList.remove('collapsed');
        header.setAttribute('aria-expanded', 'true');
        if (toggleIcon) {
            toggleIcon.classList.remove('collapsed');
            toggleIcon.textContent = '▼';
        }
    } else {
        content.classList.add('collapsed');
        header.setAttribute('aria-expanded', 'false');
        if (toggleIcon) {
            toggleIcon.classList.add('collapsed');
            toggleIcon.textContent = '▶';
        }
    }
}

function restoreSectionStates() {
    var headers = document.querySelectorAll('.section-header[data-section]');
    headers.forEach(function (header) {
        var sectionId = header.getAttribute('data-section');
        var content = document.getElementById(sectionId);
        var toggleIcon = header.querySelector('.toggle-btn');
        var savedState = null;

        try {
            savedState = window.localStorage.getItem('section-' + sectionId);
        } catch (err) {
            savedState = null;
        }

        updateSectionState(content, toggleIcon, header, savedState === 'expanded');
    });
}

function initializeToggleSections() {
    if (window.console && window.console.warn) {
        window.console.warn('section-toggle.js is deprecated. Use <astro-section-toggle> instead.');
    }

    var headers = document.querySelectorAll('.section-header[data-section]');
    headers.forEach(function (header) {
        header.addEventListener('click', function (event) {
            event.preventDefault();
            var sectionId = header.getAttribute('data-section');
            var content = document.getElementById(sectionId);
            var toggleIcon = header.querySelector('.toggle-btn');
            var shouldExpand = Boolean(content && content.classList.contains('collapsed'));

            updateSectionState(content, toggleIcon, header, shouldExpand);

            try {
                window.localStorage.setItem('section-' + sectionId, shouldExpand ? 'expanded' : 'collapsed');
            } catch (err) {
                // Ignore localStorage failures.
            }
        });
    });

    restoreSectionStates();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeToggleSections);
} else {
    initializeToggleSections();
}
