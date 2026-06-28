// Deprecated compatibility adapter. New behavior lives in js/components/astro-button.js.
document.addEventListener('DOMContentLoaded', function () {
    if (window.console && window.console.warn) {
        window.console.warn('button-loading.js is deprecated. Use <astro-button> instead.');
    }

    var legacyButtons = document.querySelectorAll('button[type="submit"]');
    legacyButtons.forEach(function (button) {
        var form = button.closest('form');
        if (!form) {
            return;
        }

        form.addEventListener('submit', function (event) {
            if (event.submitter !== button) {
                return;
            }

            var submitButtons = form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach(function (submitButton) {
                submitButton.disabled = true;
                submitButton.classList.add('loading');
            });

            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<span class="spinner"></span> Loading...';
        });
    });
});
