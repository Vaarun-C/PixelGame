import { createActor, updateActor, drawActor, facingFor, facingFromAngle, attackFrame } from "./actor.js";

// The Hollow: a husk of a dead soldier. Slow, telegraphs a lunging swipe with an ember flash.
// Times in seconds, distances in px, speeds in px/s.
const HOLLOW = {
  hp: 40, speed: 32, aggro: 150, leash: 330, range: 26, windup: 0.6, strike: 0.14, recover: 0.75,
  lunge: 170, damage: 15, arc: 1.2, stagger: 0.28, knockdown: 0.9, dying: 0.72,
};
// Spear thrust sheet: frame count and, per facing, the frame where the spear lands (see attackFrame).
const THRUST = { frames: 6, impact: { down: 3, left: 4, right: 3, up: 3 } };
const ATTACKING = ["windup", "strike", "recover"];
const DEATH_FRAMES = 6;
const TARGET_COUNT = 10;
const SPAWN_MIN = 300;
const SPAWN_MAX = 460;
const DESPAWN = 800;
const SPAWN_EVERY = 0.35;
const SPACING = 14;
const WANDER = 80;
let nextId = 1;

export function createEnemies() {
  return { list: [], timer: 0 };
}

function spawnHollow(sheets, x, y) {
  return Object.assign(createActor(sheets, x, y, HOLLOW.speed), {
    id: nextId++, hp: HOLLOW.hp, state: "wander", t: 0, aim: 0, target: null, flash: 0, stagger: 0, dying: 0,
  });
}

export function damageEnemy(e, damage, angle, knock, knockdown) {
  e.hp -= damage;
  e.flash = 0.12;
  e.vx = Math.cos(angle) * knock;
  e.vy = Math.sin(angle) * knock;
  e.stagger = knockdown ? HOLLOW.knockdown : HOLLOW.stagger;
  e.knockedDown = Boolean(knockdown);
  if (e.state === "windup" || e.state === "strike") e.state = "chase";
  if (e.hp <= 0) e.dying = HOLLOW.dying;
}

// env: { player, sheets, canSpawn(x, y), blocked(x, y), groundAt(x, y), playerSafe, hurtPlayer(e, damage, angle), onDeath(e) }
export function updateEnemies(en, dt, env) {
  const { player } = env;
  en.list = en.list.filter((e) => Math.hypot(e.x - player.x, e.y - player.y) < DESPAWN);
  if (en.list.length < TARGET_COUNT && (en.timer -= dt) <= 0) {
    en.timer = SPAWN_EVERY;
    const a = Math.random() * Math.PI * 2;
    const d = SPAWN_MIN + Math.random() * (SPAWN_MAX - SPAWN_MIN);
    const x = player.x + Math.cos(a) * d;
    const y = player.y + Math.sin(a) * d;
    if (env.canSpawn(x, y)) en.list.push(spawnHollow(env.sheets, x, y));
  }

  for (const e of en.list) {
    e.flash -= dt;
    if (e.bleed?.time > 0 && !e.dying) {
      e.bleed.time -= dt;
      if ((e.hp -= e.bleed.dps * dt) <= 0) e.dying = HOLLOW.dying;
    }
    if (e.dying) {
      if ((e.dying -= dt) <= 0 && !e.dead) {
        e.dead = true;
        env.onDeath(e);
      }
      updateActor(e, { x: 0, y: 0 }, dt, env.groundAt(e.x, e.y), env.blocked);
      continue;
    }
    const intent = think(e, dt, env);
    const input = { ...intent };
    for (const o of en.list) {
      const d = Math.hypot(e.x - o.x, e.y - o.y);
      if (o !== e && d < SPACING && d > 0) {
        input.x += (e.x - o.x) / d;
        input.y += (e.y - o.y) / d;
      }
    }
    const facing = e.facing;
    updateActor(e, input, dt, env.groundAt(e.x, e.y), env.blocked);
    // Face where the Hollow means to go, not where crowding shoves it.
    e.facing = intent.x || intent.y ? facingFor(intent, facing) : facing;
    if (e.state === "windup" || e.state === "strike") e.facing = facingFromAngle(e.aim);
  }
  en.list = en.list.filter((e) => !e.dead);
}

// One step of the Hollow's state machine; returns its movement input.
function think(e, dt, env) {
  const { player } = env;
  const dx = player.x - e.x;
  const dy = player.y - e.y;
  const dist = Math.hypot(dx, dy);
  const toward = { x: dx / (dist || 1), y: dy / (dist || 1) };
  const still = { x: 0, y: 0 };
  if (e.stagger > 0) {
    e.stagger -= dt;
    return still;
  }
  e.knockedDown = false;
  e.t += dt;
  switch (e.state) {
    case "wander":
      if (dist < HOLLOW.aggro && !env.playerSafe && !player.dead) e.state = "chase";
      if (!e.target || e.t > 4) {
        e.t = 0;
        e.target = { x: e.x + (Math.random() - 0.5) * WANDER * 2, y: e.y + (Math.random() - 0.5) * WANDER * 2 };
      }
      if (Math.hypot(e.target.x - e.x, e.target.y - e.y) < 6 || e.t < 1.5) return still;
      const tx = e.target.x - e.x;
      const ty = e.target.y - e.y;
      const td = Math.hypot(tx, ty);
      return { x: (tx / td) * 0.5, y: (ty / td) * 0.5 };
    case "chase":
      if (dist > HOLLOW.leash || env.playerSafe || player.dead) {
        e.state = "wander";
        return still;
      }
      if (dist < HOLLOW.range) {
        Object.assign(e, { state: "windup", t: 0, aim: Math.atan2(dy, dx) });
        return still;
      }
      return toward;
    case "windup":
      if (e.t >= HOLLOW.windup) {
        Object.assign(e, { state: "strike", t: 0, hit: false });
        e.vx = Math.cos(e.aim) * HOLLOW.lunge;
        e.vy = Math.sin(e.aim) * HOLLOW.lunge;
      }
      return still;
    case "strike": {
      const angle = Math.atan2(dy, dx);
      const facing = Math.abs(Math.atan2(Math.sin(angle - e.aim), Math.cos(angle - e.aim))) < HOLLOW.arc;
      if (!e.hit && dist < HOLLOW.range + 8 && facing) {
        e.hit = true;
        env.hurtPlayer(e, HOLLOW.damage, e.aim);
      }
      if (e.t >= HOLLOW.strike) Object.assign(e, { state: "recover", t: 0 });
      return still;
    }
    default:
      if (e.t >= HOLLOW.recover) Object.assign(e, { state: "chase", t: 0 });
      return still;
  }
}

// The collapse plays over the dying time; its last frame is the corpse prop left behind.
const deathFrame = (e) => Math.min(DEATH_FRAMES - 1, Math.floor((1 - e.dying / HOLLOW.dying) * DEATH_FRAMES));

export function drawEnemy(ctx, e, x, y, colors, time) {
  const telegraph = e.state === "windup" && !e.stagger;
  const pulse = 0.35 + 0.35 * Math.sin(time * 30);
  const attacking = !e.dying && ATTACKING.includes(e.state) && e.sheets.attack;
  const death = e.dying && e.sheets.death;
  drawActor(ctx, e, x, y, colors, {
    sheets: death ? e.sheets.death : attacking ? e.sheets.attack : null,
    frame: death ? deathFrame(e) : attacking ? attackFrame(e.state, e.t, HOLLOW, THRUST.frames, THRUST.impact[e.facing]) : null,
    tint: e.flash > 0 ? "bone-1" : telegraph ? "ember-2" : null,
    tintAlpha: e.flash > 0 ? 1 : pulse,
    alpha: e.dying && !death ? Math.max(0, e.dying / HOLLOW.dying) : 1,
    lean: e.knockedDown ? [0, 3] : null,
  });
}
