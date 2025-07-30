// Star trail cursor effect
class StarTrail {
    constructor() {
        this.stars = [];
        this.maxStars = 25;
        this.mouseX = 0;
        this.mouseY = 0;
        this.init();
    }

    init() {
        // Create star trail container
        this.container = document.createElement('div');
        this.container.id = 'star-trail-container';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
        `;
        document.body.appendChild(this.container);

        // Track mouse movement
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
            this.createStar();
        });

        // Start animation loop
        this.animate();
    }

    createStar() {
        const star = document.createElement('div');
        star.className = 'cursor-star';
        
        // Random star character
        const starChars = ['✦', '✧', '⋆', '✩', '✪', '✫', '✬', '✭', '✮', '✯'];
        star.textContent = starChars[Math.floor(Math.random() * starChars.length)];
        
        // Random size
        const size = Math.random() * 12 + 8;
        
        // Random color
        const colors = ['#FFD700', '#FFA500', '#FF69B4', '#9370DB', '#00CED1', '#FFFFFF', '#FFB6C1'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        star.style.cssText = `
            position: absolute;
            left: ${this.mouseX}px;
            top: ${this.mouseY}px;
            font-size: ${size}px;
            color: ${color};
            pointer-events: none;
            user-select: none;
            opacity: 1;
            transform: translate(-50%, -50%) rotate(0deg) scale(1);
            text-shadow: 0 0 ${size/2}px ${color};
            transition: none;
            z-index: 9999;
        `;

        this.container.appendChild(star);
        this.stars.push({
            element: star,
            life: 1,
            velocityX: (Math.random() - 0.5) * 0.5, // Reduced from 2 to 0.5
            velocityY: (Math.random() - 0.5) * 0.5, // Reduced from 2 to 0.5
            rotation: 0,
            rotationSpeed: (Math.random() - 0.5) * 10
        });

        // Remove oldest stars if we have too many
        if (this.stars.length > this.maxStars) {
            const oldStar = this.stars.shift();
            if (oldStar.element.parentNode) {
                oldStar.element.parentNode.removeChild(oldStar.element);
            }
        }
    }

    animate() {
        this.stars.forEach((star, index) => {
            // Update star properties
            star.life -= 0.015; 
            star.rotation += star.rotationSpeed;
            
            // Get current position
            const rect = star.element.getBoundingClientRect();
            const currentX = rect.left + rect.width / 2;
            const currentY = rect.top + rect.height / 2;
            
            // Apply velocity
            const newX = currentX + star.velocityX;
            const newY = currentY + star.velocityY;
            
            // Calculate scale and opacity based on life
            const scale = star.life;
            const opacity = Math.max(0, star.life);
            
            // Update star position and appearance
            star.element.style.transform = `
                translate(-50%, -50%) 
                rotate(${star.rotation}deg) 
                scale(${scale})
            `;
            star.element.style.opacity = opacity;
            star.element.style.left = `${newX}px`;
            star.element.style.top = `${newY}px`;
            
            // Add some drift
            star.velocityY += 0.05;
            star.velocityX *= 0.99; 
            
            // Remove dead stars
            if (star.life <= 0) {
                if (star.element.parentNode) {
                    star.element.parentNode.removeChild(star.element);
                }
                this.stars.splice(index, 1);
            }
        });

        requestAnimationFrame(() => this.animate());
    }

    // Method to temporarily disable the effect
    disable() {
        this.container.style.display = 'none';
    }

    // Method to re-enable the effect
    enable() {
        this.container.style.display = 'block';
    }

    // Method to clean up
    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        this.stars = [];
    }
}


document.addEventListener('DOMContentLoaded', function() {
    window.starTrail = new StarTrail();

    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        window.starTrail.maxStars = 15;
    }
});

document.addEventListener('visibilitychange', function() {
    if (window.starTrail) {
        if (document.hidden) {
            window.starTrail.disable();
        } else {
            window.starTrail.enable();
        }
    }
});
