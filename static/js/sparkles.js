function createSparkle() {
    const sparkleContainer = document.getElementById('sparkleContainer');
    if (!sparkleContainer) return;
    
    const sparkle = document.createElement('div');
    sparkle.className = 'sparkle';
    
    // Random star characters (matching star-trail)
    const starChars = ['✦', '✧', '⋆', '✩', '✪', '✫', '✬', '✭', '✮', '✯'];
    sparkle.textContent = starChars[Math.floor(Math.random() * starChars.length)];
    
    // Random position across the width
    sparkle.style.left = Math.random() * 100 + '%';

    // Random animation duration (1-3 seconds)
    const duration = Math.random() * 2 + 1;
    sparkle.style.animationDuration = duration + 's';
    
    // Random size
    const size = Math.random() * 15 + 15;
    sparkle.style.fontSize = size + 'px';
    
    // Random color (matching star-trail)
    const colors = ['#FFD700', '#FFA500', '#FF69B4', '#9370DB', '#00CED1', '#FFFFFF', '#FFB6C1'];
    const color = colors[Math.floor(Math.random() * colors.length)];
    sparkle.style.color = color;
    sparkle.style.textShadow = `0 0 ${size/2}px ${color}`;
    
    // Some sparkles get extra twinkle
    if (Math.random() > 0.7) {
        sparkle.classList.add('twinkle');
    }
    
    sparkleContainer.appendChild(sparkle);
    
    // Remove sparkle after animation completes
    setTimeout(() => {
        if (sparkle.parentNode) {
            sparkle.parentNode.removeChild(sparkle);
        }
    }, duration * 1000);
}

function startSparkleRain() {
    const sparkleContainer = document.getElementById('sparkleContainer');
    if (!sparkleContainer) return;
    
    // Create initial burst
    for (let i = 0; i < 15; i++) {
        setTimeout(() => createSparkle(), i * 100);
    }

    // Continue with random sparkles for 5 seconds
    const sparkleInterval = setInterval(() => {
        if (Math.random() > 0.6) {
            createSparkle();
        }
    }, 200);
    
    // Stop after 5 seconds
    setTimeout(() => {
        clearInterval(sparkleInterval);
        // Fade out container after sparkles finish
        setTimeout(() => {
            if (sparkleContainer) {
                sparkleContainer.style.opacity = '0';
                sparkleContainer.style.transition = 'opacity 1s ease';
                setTimeout(() => {
                    sparkleContainer.style.display = 'none';
                }, 1000);
            }
        }, 4000);
    }, 5000);
}

// Start sparkle animation when page loads (only on chart page)
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('sparkleContainer')) {
        setTimeout(startSparkleRain, 500); // Small delay for page to settle
    }
});
