// Deprecated compatibility adapter. New behavior lives in js/components/astro-copy-analysis.js.
(function () {
    function findComponentForLegacyButton(button) {
        if (!button) {
            return null;
        }
        return button.closest('astro-copy-analysis');
    }

    function triggerComponentCopy(component) {
        var nestedButton = component && component.querySelector('button');
        if (nestedButton) {
            nestedButton.click();
        }
    }

    window.copyAnalysis = function copyAnalysis() {
        if (window.console && window.console.warn) {
            window.console.warn('copyAnalysis() is deprecated. Use <astro-copy-analysis> instead.');
        }

        var legacyButton = document.getElementById('copyAnalysisBtn');
        var component = findComponentForLegacyButton(legacyButton);
        if (component) {
            triggerComponentCopy(component);
            return;
        }

        // Fallback for legacy templates not yet migrated.
        if (legacyButton) {
            var analysisElement = document.getElementById('analysisContent');
            if (!analysisElement) {
                return;
            }

            var analysisText = (analysisElement.innerText || analysisElement.textContent || '').trim();
            var section = analysisElement.closest('.analysis-section');
            var sun = section && section.dataset ? section.dataset.sun : '';
            var moon = section && section.dataset ? section.dataset.moon : '';
            var ascendant = section && section.dataset ? section.dataset.ascendant : '';
            var chartInfo = (sun && moon && ascendant)
                ? (sun + ' ☉ ' + moon + ' ☽ ' + ascendant + ' ⬆\n\n')
                : '';
            var fullText = chartInfo + analysisText + '\n\n✨ Get your cosmic vibe check at: ' + window.location.origin;

            var attemptCopy = function () {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    return navigator.clipboard.writeText(fullText);
                }
                return Promise.reject(new Error('Clipboard API unavailable.'));
            };

            attemptCopy().then(function () {
                var originalText = legacyButton.innerHTML;
                legacyButton.innerHTML = '✓';
                legacyButton.style.background = '#22c55e';
                window.setTimeout(function () {
                    legacyButton.innerHTML = originalText;
                    legacyButton.style.background = '';
                }, 2000);
            }).catch(function () {
                try {
                    var textArea = document.createElement('textarea');
                    textArea.value = fullText;
                    textArea.style.position = 'fixed';
                    textArea.style.left = '-999999px';
                    textArea.style.top = '-999999px';
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                } catch (err) {
                    // Ignore legacy copy failures.
                }
            });
        }
    };
})();
