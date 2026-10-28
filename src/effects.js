// Game feel: hit-stop, screen shake, particles and tinted sprite flashes.
const SHAKE_DECAY = 18;
const PARTICLE_DRAG = 5;

export function createEffects() {
  return { freeze: 0, shake: 0, particles: [] };
}

export function hitStop(fx, seconds) {
  fx.freeze = Math.max(fx.freeze, seconds);
}

export function shake(fx, amount) {
  fx.shake = Math.max(fx.shake, amount);
}

// Gameplay time for this frame: zero while frozen by hit-stop.
export function gameDt(fx, dt) {
  if (fx.freeze > 0) {
    fx.freeze -= dt;
    return 0;
  }
  return dt;
}

export function shakeOffset(fx, dt) {
  fx.shake = Math.max(0, fx.shake - SHAKE_DECAY * dt);
  const r = () => Math.round((Math.random() * 2 - 1) * fx.shake);
  return [r(), r()];
}

// A burst of 1px particles flying out around `angle`, e.g. blood away from the blow.
export function burst(fx, x, y, angle, { count, speed, spread, colors, life }) {
  for (let i = 0; i < count; i++) {
    const a = angle + (Math.random() - 0.5) * spread;
    const v = speed * (0.4 + Math.random() * 0.6);
    fx.particles.push({
      x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v,
      life: life * (0.6 + Math.random() * 0.4), color: colors[i % colors.length],
    });
  }
}

export function updateParticles(fx, dt) {
  for (const p of fx.particles) {
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.vx -= p.vx * PARTICLE_DRAG * dt;
    p.vy -= p.vy * PARTICLE_DRAG * dt;
    p.life -= dt;
  }
  fx.particles = fx.particles.filter((p) => p.life > 0);
}

export function drawParticles(ctx, fx, colors, camX, camY) {
  for (const p of fx.particles) {
    ctx.fillStyle = colors[p.color];
    ctx.fillRect(Math.round(p.x - camX), Math.round(p.y - camY), 1, 1);
  }
}

// A single-colour silhouette of a sprite frame, cached, for hit flashes and attack telegraphs.
const tints = new Map();
export function tinted(img, sx, sy, w, h, color) {
  const key = `${img.src}|${sx}|${sy}|${color}`;
  if (!tints.has(key)) {
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const c = canvas.getContext("2d");
    c.drawImage(img, sx, sy, w, h, 0, 0, w, h);
    c.globalCompositeOperation = "source-in";
    c.fillStyle = color;
    c.fillRect(0, 0, w, h);
    tints.set(key, canvas);
  }
  return tints.get(key);
}
