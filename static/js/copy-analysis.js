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
            legacyButton.dispatchEvent(new MouseEvent('click', { bubbles: true }));
        }
    };
})();
