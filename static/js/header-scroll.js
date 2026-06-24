// Adds a frosted backdrop to the sticky header once the page is scrolled,
// keeping the logo and header actions readable over content behind them.
(function () {
    var THRESHOLD = 8; // px scrolled before the bar frosts over

    function update() {
        document.body.classList.toggle('is-scrolled', window.scrollY > THRESHOLD);
    }

    window.addEventListener('scroll', update, { passive: true });
    update(); // set initial state (e.g. when reloaded mid-page)
})();
