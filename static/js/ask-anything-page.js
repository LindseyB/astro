(function () {
    document.body.dataset.disableTrail = 'true';
    document.body.classList.add('ask-page');

    // Auto-grow the textarea and submit on Enter (Shift+Enter for newline)
    function initializeChatInput() {
        var input = document.querySelector('.chat-input');
        if (!input) return;

        function grow() {
            var cs = getComputedStyle(input);
            // Under box-sizing: border-box, height must include the borders or
            // the content box ends up too short and forces a scrollbar.
            var borderY = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth);
            var maxPx = parseFloat(cs.maxHeight);
            input.style.height = 'auto';
            var needed = input.scrollHeight + borderY;
            if (needed > maxPx) {
                input.style.height = maxPx + 'px';
                input.style.overflowY = 'auto';
            } else {
                input.style.height = needed + 'px';
                input.style.overflowY = 'hidden';
            }
        }

        grow();
        input.addEventListener('input', grow);
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (input.value.trim()) input.form.submit();
            }
        });
    }

    // Handle navigation form submission
    window.submitFormNav = function submitFormNav(e, action) {
        e.preventDefault();
        var form = document.getElementById('navForm');
        if (!form) return;
        form.action = action;
        form.submit();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeChatInput);
    } else {
        initializeChatInput();
    }
})();