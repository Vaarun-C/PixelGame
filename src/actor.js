import { tinted } from "./effects.js";

// Shared by the player, villagers and enemies.
// sheets.frame overrides this. scale 0.5 draws a 2x-resolution sheet at native pixels in the 2x canvas.
const LOW_RES = { w: 32, h: 48, feet: 46, scale: 1 };
export const HIGH_RES = { w: 96, h: 96, feet: 94, scale: 0.5 };
// Player attack sheets: the 96x96 body padded to leave room for the swing.
export const ATTACK_RES = { w: 128, h: 144, feet: 142, scale: 0.5 };
// Fodder enemies (Hollow) at 2x, and their attack sheets padded for the spear.
export const FODDER_RES = { w: 64, h: 96, feet: 94, scale: 0.5 };
export const FODDER_ATTACK_RES = { w: 128, h: 112, feet: 110, scale: 0.5 };
export const FODDER_DEATH_RES = { w: 96, h: 96, feet: 94, scale: 0.5 };
const MIN_FRAME_TIME = 0.04;
const DIRS = ["down", "left", "right", "up"];
const ANIMS = {
  idle: { frames: 4, ms: 180 },
  walk: { frames: 6, ms: 100 },
};
const RUN_MULT = 1.7;
const ACCEL = 20;
const SHADOW_ROWS = [8, 14, 16, 14, 8];

// sheets: { idle, walk } images.
export function createActor(sheets, x = 0, y = 0, speed = 60) {
  return { x, y, vx: 0, vy: 0, speed, facing: "down", anim: "idle", time: 0, sheets };
}

// ground: { speed, slide } under the actor's feet. blocked(x, y): whether the feet can't stand there.
export function updateActor(a, input, dt, ground, blocked) {
  const moving = input.x !== 0 || input.y !== 0;
  const mult = (moving && input.run ? RUN_MULT : 1) * (ground.speed ?? 1);
  const len = Math.hypot(input.x, input.y) || 1;
  const accel = Math.min(1, (ground.slide ?? ACCEL) * dt);
  a.vx += ((input.x / len) * a.speed * mult - a.vx) * accel;
  a.vy += ((input.y / len) * a.speed * mult - a.vy) * accel;

  const nx = a.x + a.vx * dt;
  if (blocked(nx, a.y)) a.vx = 0;
  else a.x = nx;
  const ny = a.y + a.vy * dt;
  if (blocked(a.x, ny)) a.vy = 0;
  else a.y = ny;

  const anim = moving ? "walk" : "idle";
  if (anim !== a.anim) {
    a.anim = anim;
    a.time = 0;
  }
  a.time += dt * (moving ? Math.max(0.5, Math.hypot(a.vx, a.vy) / a.speed) : 1);
  if (moving) a.facing = facingFor(input, a.facing);
}

// The 4-way facing for a movement direction. Near-diagonals keep the current facing, so analog
// input (enemy steering) doesn't flip between left/right and up/down every frame.
export function facingFor({ x, y }, current) {
  const horizontal = x < 0 ? "left" : "right";
  const vertical = y < 0 ? "up" : "down";
  if (Math.abs(x) > Math.abs(y) * 2) return horizontal;
  if (Math.abs(y) > Math.abs(x) * 2) return vertical;
  return current === horizontal || current === vertical ? current : horizontal;
}

// The 4-way facing closest to an angle (radians, screen space).
export function facingFromAngle(angle) {
  const x = Math.cos(angle);
  const y = Math.sin(angle);
  if (Math.abs(x) > Math.abs(y)) return x < 0 ? "left" : "right";
  return y < 0 ? "up" : "down";
}

// Attack sheet frame for a moment of an attack. times: { windup, strike, recover } in seconds.
// The frames before impact play during the windup (short windups skip the earliest so each lasts
// MIN_FRAME_TIME), the impact frame holds through the strike, the rest play during recovery.
export function attackFrame(phase, t, times, frames, impact) {
  const k = Math.min(0.999, t / times[phase]);
  if (phase === "windup") {
    const shown = Math.max(1, Math.min(impact, Math.floor(times.windup / MIN_FRAME_TIME)));
    return impact - shown + Math.floor(k * shown);
  }
  if (phase === "strike") return impact;
  return impact + Math.ceil(k * (frames - 1 - impact));
}

export const SHADOW_WIDTH = Math.max(...SHADOW_ROWS);

// Flat ellipse in void-0 at 50% (ART_RULES §2), centred on the ground contact point; scale 1 = 16px wide.
export function drawShadow(ctx, x, y, scale, colors, alpha = 1) {
  ctx.globalAlpha = 0.5 * alpha;
  ctx.fillStyle = colors["void-0"];
  SHADOW_ROWS.forEach((w, i) => ctx.fillRect(x - (w * scale) / 2, y - 2 + i, w * scale, 1));
  ctx.globalAlpha = 1;
}

// opts: sheets/frame override the animation; tint + tintAlpha overlay a silhouette; alpha fades the whole actor.
export function drawActor(ctx, a, x, y, colors, opts = {}) {
  const sheets = opts.sheets ?? a.sheets;
  const f = sheets.frame ?? LOW_RES;
  const dw = f.w * f.scale;
  const dh = f.h * f.scale;
  drawShadow(ctx, x, y, dw / LOW_RES.w, colors, opts.alpha);

  const anim = opts.sheets ? "idle" : a.anim;
  const img = sheets[anim];
  const { frames, ms } = ANIMS[anim];
  const frame = opts.frame ?? Math.floor((a.time * 1000) / ms) % frames;
  const sx = frame * f.w;
  const sy = DIRS.indexOf(a.facing) * f.h;
  const dx = x - dw / 2 + (opts.lean?.[0] ?? 0);
  const dy = y - f.feet * f.scale + (opts.lean?.[1] ?? 0);
  ctx.globalAlpha = opts.alpha ?? 1;
  ctx.drawImage(img, sx, sy, f.w, f.h, dx, dy, dw, dh);
  if (opts.tint) {
    ctx.globalAlpha = (opts.alpha ?? 1) * (opts.tintAlpha ?? 1);
    ctx.drawImage(tinted(img, sx, sy, f.w, f.h, colors[opts.tint]), dx, dy, dw, dh);
  }
  ctx.globalAlpha = 1;
}
