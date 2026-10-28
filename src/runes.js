import { itemInfo, runeKey, TIERS } from "./items.js";

// Runes socketed into the wanderer's blade (3) and armor (2). Each rune gives a passive by type and tier;
// the set of types in one part forms resonances (named effects). Percentages per tier, Pale to Crimson.
export const SOCKETS = { blade: 3, armor: 2 };
const FITS = { blade: ["rend", "hunger"], armor: ["ward"] };
const PASSIVE = { rend: [5, 9, 14, 20, 28, 40], hunger: [2, 3, 5, 7, 10, 15], ward: [4, 7, 11, 16, 22, 30] };
const PASSIVE_TEXT = { rend: "damage", hunger: "of damage dealt heals you", ward: "damage taken" };
const NOTCH_BONUS = 0.2;
export const MAX_NOTCHES = 5;
export const CARVE_COST = [3, 6, 10, 15, 21];
const FUSE_COST_PER_TIER = 5;
const CRIMSON = TIERS.length;
const CRIMSON_HURT = 3;
const CRIMSON_STARVE = 0.5;
const CRIMSON_SLOW = 0.85;
const CURSED_DAMAGE_TAKEN = 1.1;

// needs: how many runes of each type (a fused rune counts as both of its types).
const RESONANCES = [
  { name: "Flay", part: "blade", needs: { rend: 3 }, desc: "Every third hit opens a bleed." },
  { name: "Gorge", part: "blade", needs: { hunger: 3 }, desc: "Killing blows heal." },
  { name: "Bloodletting", part: "blade", needs: { rend: 1, hunger: 1 }, desc: "Every third hit bleeds; hitting the bleeding heals." },
  { name: "Riposte", part: "blade", needs: { rend: 1, ward: 1 }, desc: "Dodge a blow and your next strike deals double." },
  { name: "Leech-shell", part: "blade", needs: { hunger: 1, ward: 1 }, desc: "Overhealing becomes a shield." },
  { name: "Bulwark", part: "armor", needs: { ward: 2 }, desc: "Blows shove you no more and lose some force." },
  { name: "Scab", part: "armor", needs: { ward: 1, hunger: 1 }, desc: "Out of the fight, wounds close." },
];
const BLEED = { every: 3, dps: 4, time: 3, lightDps: 2, lightTime: 2 };
const GORGE_HEAL = 0.1;
const BLOODLET_HEAL = 2;
const SHIELD_MAX = 20;
const BULWARK_BLOCK = 5;
const SCAB = { after: 3, regen: 1 };

export const createSockets = () => ({ blade: Array(SOCKETS.blade).fill(null), armor: Array(SOCKETS.armor).fill(null) });
export const fits = (key, part) => itemInfo(key).types.some((t) => FITS[part].includes(t));

const strength = (info) => 1 + info.notches * NOTCH_BONUS;
const tierPercent = (type, info) => PASSIVE[type][info.tier - 1] * strength(info);

export function passiveLines(key) {
  const info = itemInfo(key);
  return info.types.map((t) => `${t === "ward" ? "-" : "+"}${Math.round(tierPercent(t, info))}% ${PASSIVE_TEXT[t]}`);
}

export const carveCost = (key) => CARVE_COST[itemInfo(key).notches];
export const canFuse = (a, b) => {
  const [x, y] = [itemInfo(a), itemInfo(b)];
  return x.types.length === 1 && y.types.length === 1 && x.types[0] !== y.types[0];
};
export const fuseCost = (a, b) => FUSE_COST_PER_TIER * Math.max(itemInfo(a).tier, itemInfo(b).tier);
export const carved = (key) => {
  const info = itemInfo(key);
  return runeKey(info.types, info.tier, info.notches + 1);
};
export function fused(a, b) {
  const [x, y] = [itemInfo(a), itemInfo(b)];
  const order = ["rend", "ward", "hunger"];
  const types = [x.types[0], y.types[0]].sort((p, q) => order.indexOf(p) - order.indexOf(q));
  return runeKey(types, Math.max(x.tier, y.tier));
}

// Everything the sockets do, recomputed whenever they change.
export function runeStats(sockets) {
  const stats = { rend: 0, hunger: 0, ward: 0, cursed: {}, resonances: [] };
  for (const part of Object.keys(SOCKETS)) {
    const infos = sockets[part].filter(Boolean).map(itemInfo);
    for (const info of infos) {
      for (const t of info.types) {
        stats[t] += tierPercent(t, info) / 100;
        if (info.tier === CRIMSON) stats.cursed[t] = true;
      }
    }
    for (const r of RESONANCES.filter((r) => r.part === part)) {
      const formers = infos.filter((info) => info.types.some((t) => r.needs[t]));
      const met = Object.entries(r.needs).every(([t, n]) => formers.filter((info) => info.types.includes(t)).length >= n);
      if (!met) continue;
      const cursed = formers.some((info) => info.tier === CRIMSON);
      const power = (0.6 + 0.2 * Math.min(...formers.map((info) => Math.min(info.tier, CRIMSON - 1)))) * (cursed ? 2 : 1);
      stats.resonances.push({ ...r, power, cursed });
    }
  }
  return stats;
}

export const resonance = (stats, name) => stats.resonances.find((r) => r.name === name);

// Combat hooks. p is the player: { hp, maxHp, shield, runeHits, riposte, sinceHurt, selfBleed }.
export function strikeDamage(stats, p, base) {
  const double = p.riposte ? 2 : 1;
  p.riposte = false;
  return base * (1 + stats.rend) * double;
}

export function heal(stats, p, amount, source) {
  const gorge = resonance(stats, "Gorge");
  if (gorge?.cursed && source !== "Gorge") return;
  const room = p.maxHp - p.hp;
  p.hp += Math.min(room, amount);
  const leech = resonance(stats, "Leech-shell");
  if (leech && amount > room) p.shield = Math.min(SHIELD_MAX * leech.power, (p.shield ?? 0) + amount - room);
}

// After a hit lands on enemy e for `damage`; returns whether the hit opened a bleed.
export function onStrike(stats, p, e, damage) {
  p.runeHits = (p.runeHits ?? 0) + 1;
  if (stats.hunger) heal(stats, p, damage * stats.hunger, "hunger");
  const bloodlet = resonance(stats, "Bloodletting");
  if (bloodlet && e.bleed?.time > 0) heal(stats, p, BLOODLET_HEAL * bloodlet.power, "Bloodletting");
  if (p.runeHits % BLEED.every) return false;
  const flay = resonance(stats, "Flay");
  if (flay) {
    e.bleed = { dps: BLEED.dps * flay.power, time: BLEED.time };
    if (flay.cursed) p.selfBleed = BLEED.time;
  } else if (bloodlet) e.bleed = { dps: BLEED.lightDps * bloodlet.power, time: BLEED.lightTime };
  return Boolean(flay || bloodlet);
}

export function onKill(stats, p) {
  const gorge = resonance(stats, "Gorge");
  if (gorge) heal(stats, p, p.maxHp * GORGE_HEAL * gorge.power, "Gorge");
}

// A dodged blow arms Riposte.
export function onDodged(stats, p) {
  if (resonance(stats, "Riposte")) p.riposte = true;
}

// Damage the player actually takes from a blow of `damage`, after shields; also whether to knock back.
export function takeHit(stats, p, damage) {
  const bulwark = resonance(stats, "Bulwark");
  const cursedSets = stats.resonances.filter((r) => r.cursed && r.name !== "Flay" && r.name !== "Gorge").length;
  let hurt = damage * (1 - Math.min(0.75, stats.ward)) * CURSED_DAMAGE_TAKEN ** cursedSets;
  if (stats.cursed.rend) hurt += CRIMSON_HURT;
  if (bulwark) hurt = Math.max(1, hurt - BULWARK_BLOCK * bulwark.power);
  const absorbed = Math.min(p.shield ?? 0, hurt);
  p.shield = (p.shield ?? 0) - absorbed;
  p.sinceHurt = 0;
  return { hurt: hurt - absorbed, knockback: !bulwark };
}

// Per frame: Scab regeneration, crimson Hunger starvation and Flay's self-bleed. calm: no enemy near.
export function updateRunes(stats, p, dt, calm) {
  p.sinceHurt = (p.sinceHurt ?? 0) + dt;
  const scab = resonance(stats, "Scab");
  if (scab && calm && p.sinceHurt > SCAB.after) heal(stats, p, SCAB.regen * scab.power * dt, "Scab");
  if (stats.cursed.hunger && calm) p.hp = Math.max(1, p.hp - CRIMSON_STARVE * dt);
  if (p.selfBleed > 0) {
    p.selfBleed -= dt;
    p.hp = Math.max(1, p.hp - dt);
  }
}

export const speedFactor = (stats) => (stats.cursed.ward ? CRIMSON_SLOW : 1);
