function initBirthdayConfetti() {
  var celebration = window.birthdayCelebration || {};
  if (!celebration.isBirthday) {
    return;
  }

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  if (!document.body) {
    return;
  }

  var canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.position = 'fixed';
  canvas.style.top = '0';
  canvas.style.left = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.pointerEvents = 'none';
  canvas.style.zIndex = '55';
  document.body.appendChild(canvas);

  var ctx = canvas.getContext('2d');
  var particles = [];
  var endAt = Date.now() + 4500;
  var colors = ['#f59e0b', '#22c55e', '#0ea5e9', '#f43f5e', '#a855f7'];

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
  }

  function spawnBurst() {
    for (var i = 0; i < 260; i += 1) {
      particles.push({
        x: randomBetween(0, canvas.width),
        y: randomBetween(-40, -10),
        vx: randomBetween(-2.5, 2.5),
        vy: randomBetween(1.8, 5.2),
        size: randomBetween(3, 8),
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: randomBetween(0, Math.PI * 2),
        spin: randomBetween(-0.2, 0.2),
        life: randomBetween(70, 130)
      });
    }
  }

  function drawParticle(particle) {
    ctx.save();
    ctx.translate(particle.x, particle.y);
    ctx.rotate(particle.rotation);
    ctx.fillStyle = particle.color;
    ctx.fillRect(-particle.size / 2, -particle.size / 2, particle.size, particle.size * 0.65);
    ctx.restore();
  }

  function tick() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (var i = particles.length - 1; i >= 0; i -= 1) {
      var p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.05;
      p.rotation += p.spin;
      p.life -= 1;

      if (p.life <= 0 || p.y > canvas.height + 20) {
        particles.splice(i, 1);
      } else {
        drawParticle(p);
      }
    }

    if (Date.now() < endAt || particles.length) {
      window.requestAnimationFrame(tick);
    } else if (canvas.parentNode) {
      canvas.parentNode.removeChild(canvas);
    }
  }

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas, { passive: true });

  spawnBurst();
  window.requestAnimationFrame(tick);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initBirthdayConfetti, { once: true });
} else {
  initBirthdayConfetti();
}
