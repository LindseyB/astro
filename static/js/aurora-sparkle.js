// Dramatic glitter sparkles layered over the light-mode aurora background.
// Inspired by the "Starshine glitter effect" (CodePen by Kurucz Csaba):
// https://gist.github.com/zamboney/ed398efded1a88f5217682eef750776c
(function () {
    var container = document.querySelector('.aurora-sparkles');
    if (!container) return;

    // Respect users who prefer reduced motion — no twinkling for them.
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    var STAR_COUNT = 120; // enough for drama without overwhelming the page
    var MAX_DELAY = 8;     // seconds; staggers each sparkle's twinkle

    var fragment = document.createDocumentFragment();
    for (var i = 0; i < STAR_COUNT; i++) {
        var star = document.createElement('span');
        star.className = 'aurora-sparkle';

        // Mix of sizes for depth, mirroring the gist's small/medium/large split.
        if (i % 2 === 0) {
            star.classList.add('small');
        } else if (i % 3 === 0) {
            star.classList.add('medium');
        } else {
            star.classList.add('large');
        }

        star.style.top = (Math.random() * 100) + '%';
        star.style.left = (Math.random() * 100) + '%';
        star.style.animationDelay = (Math.random() * MAX_DELAY) + 's';
        star.style.animationDuration = (5 + Math.random() * 4) + 's';

        fragment.appendChild(star);
    }
    container.appendChild(fragment);
})();
