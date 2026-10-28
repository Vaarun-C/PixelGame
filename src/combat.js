import { hitStop, shake, burst } from "./effects.js";
import { facingFromAngle, drawActor, attackFrame } from "./actor.js";
import { damageEnemy } from "./enemies.js";
import { strikeDamage, onStrike, onKill } from "./runes.js";

const DEG = Math.PI / 180;
// The sword combo. Times in seconds, lunge/knock in px/s, cone in degrees around the aim.
// Each swing hits once, at the start of its strike, everything within reach and inside the cone.
// anim picks the player attack sheet.
export const COMBO = [
  { windup: 0.08, strike: 0.07, recover: 0.22, anim: "light", damage: 10, reach: 34, cone: 150, lunge: 150, knock: 130, hitstop: 0.05, shake: 2 },
  { windup: 0.06, strike: 0.07, recover: 0.22, anim: "light", damage: 12, reach: 34, cone: 150, lunge: 150, knock: 140, hitstop: 0.05, shake: 2.5 },
  { windup: 0.1, strike: 0.06, recover: 0.24, anim: "light", damage: 14, reach: 44, cone: 60, lunge: 260, knock: 180, hitstop: 0.06, shake: 3 },
  { windup: 0.32, strike: 0.09, recover: 0.45, anim: "heavy", damage: 34, reach: 42, cone: 170, lunge: 210, knock: 300, knockdown: true, hitstop: 0.13, shake: 7 },
];
// Attack sheet length and, per facing, the frame where the blade lands (see attackFrame).
const ATTACK_FRAMES = {
  light: { frames: 6, impact: { down: 3, left: 2, right: 2, up: 4 } },
  heavy: { frames: 8, impact: { down: 6, left: 5, right: 4, up: 6 } },
};
const CHAIN_AFTER = 0.06;
const CHEST_Y = -26;
const DODGE = { time: 0.32, iframes: 0.24, speed: 175, cooldown: 0.45 };
const GHOST_EVERY = 0.03;
const GHOST_LIFE = 0.2;

export function createCombat() {
  return { move: -1, phase: null, t: 0, aim: 0, queued: false, dodge: 0, dodgeCooldown: 0, dodgeDir: [0, 0], ghosts: [], ghostTimer: 0 };
}

export const attacking = (c) => c.move >= 0;
export const dodgeInvulnerable = (c) => c.dodge > DODGE.time - DODGE.iframes;

export function cancelCombat(c) {
  c.move = -1;
  c.phase = null;
  c.queued = false;
}

function startMove(c, move, aim) {
  Object.assign(c, { move, phase: "windup", t: 0, aim, queued: false });
}

const angleDiff = (a, b) => Math.atan2(Math.sin(a - b), Math.cos(a - b));

function resolveHits(p, c, m, enemies, fx) {
  const cy = p.y + CHEST_Y + 8;
  let hit = false;
  for (const e of enemies) {
    if (e.dying) continue;
    const dx = e.x - p.x;
    const dy = e.y - 12 - cy;
    const angle = Math.atan2(dy, dx);
    if (Math.hypot(dx, dy) > m.reach + 8 || Math.abs(angleDiff(angle, c.aim)) > (m.cone / 2) * DEG) continue;
    const damage = strikeDamage(p.runes, p, m.damage);
    damageEnemy(e, damage, angle, m.knock, m.knockdown);
    if (onStrike(p.runes, p, e, damage)) burst(fx, e.x, e.y - 14, angle, { count: 8, speed: 60, spread: 2.5, colors: ["blood-1", "blood-2"], life: 0.6 });
    if (e.hp <= 0) onKill(p.runes, p);
    burst(fx, e.x, e.y - 14, angle, { count: m.knockdown ? 22 : 12, speed: 140, spread: 1.4, colors: ["blood-2", "blood-3", "blood-4"], life: 0.45 });
    burst(fx, e.x, e.y - 14, angle + Math.PI, { count: 4, speed: 90, spread: 2, colors: ["bone-1", "steel-3"], life: 0.15 });
    hit = true;
  }
  if (hit) {
    hitStop(fx, m.hitstop);
    shake(fx, m.shake);
  }
  if (m.knockdown) {
    const ix = p.x + Math.cos(c.aim) * m.reach * 0.8;
    const iy = p.y + Math.sin(c.aim) * m.reach * 0.6;
    burst(fx, ix, iy, 0, { count: 26, speed: 110, spread: Math.PI * 2, colors: ["ash-2", "ash-3", "leather-2"], life: 0.4 });
    shake(fx, hit ? m.shake : 3);
  }
}

// Returns the movement input to apply this frame (rooted while swinging, forced while dodging) and the
// ground override for a dodge. aim: radians from the player's chest toward the mouse.
export function updateCombat(p, c, input, aim, dt, enemies, fx) {
  c.dodgeCooldown -= dt;
  c.ghosts = c.ghosts.filter((g) => (g.age += dt) < GHOST_LIFE);

  if (input.dodge && c.dodgeCooldown <= 0 && (c.move < 0 || c.phase === "recover")) {
    const moving = input.x || input.y;
    const len = Math.hypot(input.x, input.y) || 1;
    c.dodgeDir = moving ? [input.x / len, input.y / len] : [Math.cos(aim), Math.sin(aim)];
    c.dodge = DODGE.time;
    c.dodgeCooldown = DODGE.time + DODGE.cooldown;
    cancelCombat(c);
  }
  if (c.dodge > 0) {
    c.dodge -= dt;
    if ((c.ghostTimer -= dt) <= 0) {
      c.ghostTimer = GHOST_EVERY;
      c.ghosts.push({ x: p.x, y: p.y, facing: p.facing, time: p.time, age: 0 });
    }
    return { input: { x: c.dodgeDir[0], y: c.dodgeDir[1] }, ground: { speed: DODGE.speed / p.speed, slide: 40 } };
  }

  if (input.attack) {
    if (c.move < 0) startMove(c, 0, aim);
    else c.queued = true;
  }
  if (c.move < 0) return { input };

  const m = COMBO[c.move];
  c.t += dt;
  if (c.phase === "windup" && c.t >= m.windup) {
    c.phase = "strike";
    c.t -= m.windup;
    p.vx = Math.cos(c.aim) * m.lunge;
    p.vy = Math.sin(c.aim) * m.lunge;
    resolveHits(p, c, m, enemies, fx);
  }
  if (c.phase === "strike" && c.t >= m.strike) {
    c.phase = "recover";
    c.t -= m.strike;
  }
  if (c.phase === "recover") {
    const last = c.move === COMBO.length - 1;
    if (c.queued && !last && c.t >= CHAIN_AFTER) startMove(c, c.move + 1, aim);
    else if (c.t >= m.recover) {
      const again = c.queued;
      cancelCombat(c);
      if (again) startMove(c, 0, aim);
    }
  }
  p.facing = facingFromAngle(c.aim);
  return { input: { x: 0, y: 0 } };
}

// Attack sheet frame and body lean (px toward the aim) for the current moment of the swing.
function attackPose(c, facing) {
  const m = COMBO[c.move];
  const { frames, impact } = ATTACK_FRAMES[m.anim];
  const frame = attackFrame(c.phase, c.t, m, frames, impact[facing]);
  const lean = { windup: -1, strike: 2, recover: 1 - Math.min(1, c.t / m.recover) }[c.phase];
  return { frame, lean };
}

// Draws the player: dodge afterimages, then the body, or the attack animation while swinging.
export function drawPlayer(ctx, p, c, x, y, colors, images, camX, camY) {
  for (const g of c.ghosts) {
    drawActor(ctx, { ...p, ...g, anim: "walk" }, Math.round(g.x) - camX, Math.round(g.y) - camY, colors, {
      tint: "steel-1", tintAlpha: 1, alpha: 0.35 * (1 - g.age / GHOST_LIFE),
    });
  }
  const blink = p.invuln > 0 && Math.floor(p.invuln * 20) % 2 === 0;
  const opts = { tint: p.flash > 0 ? "bone-1" : null, alpha: blink ? 0.5 : 1 };
  if (c.move < 0) {
    drawActor(ctx, p, x, y, colors, opts);
    return;
  }
  const pose = attackPose(c, p.facing);
  const lean = [Math.round(Math.cos(c.aim) * pose.lean), Math.round(Math.sin(c.aim) * pose.lean)];
  drawActor(ctx, p, x, y, colors, { ...opts, sheets: images.wanderer_attack[COMBO[c.move].anim], frame: pose.frame, lean });
}
