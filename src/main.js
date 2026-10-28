import { readInput, mouse } from "./input.js";
import { createActor, updateActor, drawActor, HIGH_RES, ATTACK_RES, FODDER_RES, FODDER_ATTACK_RES, FODDER_DEATH_RES } from "./actor.js";
import {
  createWorld, drawGround, visibleProps, drawProp, nearestLootable, blocked, groundAt, biomeAt, nearbyVillages, villageAt,
  addCorpse, inVillageGrounds,
} from "./world.js";
import { createEffects, gameDt, shakeOffset, hitStop, shake, burst, updateParticles, drawParticles } from "./effects.js";
import { createCombat, updateCombat, drawPlayer, cancelCombat, dodgeInvulnerable } from "./combat.js";
import { createEnemies, updateEnemies, drawEnemy } from "./enemies.js";
import { createInventory, addItem, drawInventory, clickInventory } from "./inventory.js";
import { runeStats, takeHit, onDodged, updateRunes, speedFactor } from "./runes.js";
import { itemInfo, rollLoot, LOOT_TABLES } from "./items.js";
import { say, drawMessages, drawKeyPrompt, showTitle, drawTitle, drawSpeech, drawHealth } from "./ui.js";
import { drawText } from "./font.js";
import { PROPS } from "./props.js";
import { BIOMES } from "./biomes.js";
import { updateVillage, nearestVillager, talk, offers as barterOffers } from "./village.js";
import { drawBarter, offerAt, trade, SHIFT_TIMES } from "./barter.js";

// The world is drawn at 2x so 2x-resolution sprites (HIGH_RES) keep their native pixels.
const WORLD_SCALE = 2;
const VIEW_W = 480 * WORLD_SCALE;
const VIEW_H = 270 * WORLD_SCALE;
const BARTER_RANGE = 40;
const CONTROLS = "WASD move  Click attack  Space dodge  E use  I bag";
const CHARACTERS = ["peasant", "monk", "guard", "barterer"];
const MAX_HP = 100;
const PLAYER_SPEED = 60;
const CALM_RANGE = 120;
const HURT_INVULN = 0.7;
const HURT_KNOCK = 160;
const DEATH_SECONDS = 2.5;
const IMAGES = {
  runes: "art/runes/rune_icons.png",
  items: "art/items/item_icons.png",
  runes_hd: "art/runes/rune_icons_hd.png",
  items_hd: "art/items/item_icons_hd.png",
  ...Object.fromEntries(BIOMES.map(({ id }) => [`${id}_ground`, `art/tiles/${id}/${id}_ground.png`])),
  ...Object.fromEntries(Object.values(PROPS).map(({ sheet }) => [sheet, `art/props/${sheet}.png`])),
  ...Object.fromEntries(CHARACTERS.flatMap((n) => ["idle", "walk"].map((a) => [`${n}_${a}`, `art/characters/${n}/${n}_hd_${a}.png`]))),
  ...Object.fromEntries(["idle", "walk", "light", "heavy"].map((a) => [`wanderer_${a}`, `art/characters/wanderer_hd/wanderer_hd_${a}.png`])),
  ...Object.fromEntries(["idle", "walk", "attack", "death"].map((a) => [`hollow_${a}`, `art/enemies/hollow_hd/hollow_hd_${a}.png`])),
};

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

// Also groups character sheets as images[name] = { idle, walk }.
async function loadImages() {
  const entries = await Promise.all(Object.entries(IMAGES).map(async ([name, src]) => [name, await loadImage(src)]));
  const images = Object.fromEntries(entries);
  for (const n of CHARACTERS) images[n] = { idle: images[`${n}_idle`], walk: images[`${n}_walk`], frame: FODDER_RES };
  images.wanderer = { idle: images.wanderer_idle, walk: images.wanderer_walk, frame: HIGH_RES };
  images.hollow = {
    idle: images.hollow_idle, walk: images.hollow_walk, frame: FODDER_RES,
    attack: { idle: images.hollow_attack, frame: FODDER_ATTACK_RES },
    death: { idle: images.hollow_death, frame: FODDER_DEATH_RES },
  };
  images.wanderer_attack = {
    light: { idle: images.wanderer_light, frame: ATTACK_RES },
    heavy: { idle: images.wanderer_heavy, frame: ATTACK_RES },
  };
  return images;
}

async function loadPalette() {
  const text = await (await fetch("art/palette/master.gpl")).text();
  const colors = {};
  for (const line of text.split("\n")) {
    const [r, g, b, name] = line.trim().split(/\s+/);
    if (name && !isNaN(r)) colors[name] = `rgb(${r},${g},${b})`;
  }
  return colors;
}

function resize() {
  const scale = Math.max(1, Math.floor(Math.min(innerWidth / VIEW_W, innerHeight / VIEW_H)));
  canvas.width = Math.ceil(innerWidth / scale);
  canvas.height = Math.ceil(innerHeight / scale);
  canvas.style.width = `${canvas.width * scale}px`;
  canvas.style.height = `${canvas.height * scale}px`;
  ctx.imageSmoothingEnabled = false;
}

// Mouse position in world view pixels; scale 1 gives canvas pixels for the 2x-resolution UI.
function toView({ x, y }, scale = WORLD_SCALE) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: Math.floor(((x - rect.left) * canvas.width) / rect.width / scale),
    y: Math.floor(((y - rect.top) * canvas.height) / rect.height / scale),
  };
}

function search(world, inventory, prop) {
  const table = prop.def.loot;
  const loot = world.loot.get(prop.key) ?? rollLoot(table, biomeAt(world, prop.x, prop.y).loot);
  if (!loot.length) say(LOOT_TABLES[table].nothing, "ash-3");
  const left = [];
  for (const item of loot) {
    const rest = addItem(inventory, item.key, item.count);
    const { name, color, unit } = itemInfo(item.key);
    if (rest < item.count) say(`+${item.count - rest}${unit} ${name}`, color);
    if (rest) left.push({ ...item, count: rest });
  }
  if (left.length) say("Inventory full.", "blood-4");
  world.loot.set(prop.key, left);
}

async function start() {
  const [colors, images] = await Promise.all([loadPalette(), loadImages()]);
  const player = Object.assign(createActor(images.wanderer, 0, 0, PLAYER_SPEED), { hp: MAX_HP, maxHp: MAX_HP, shield: 0, invuln: 0, flash: 0, dead: 0 });
  const combat = createCombat();
  const world = createWorld(images);
  const inventory = createInventory();
  const enemies = createEnemies();
  const fx = createEffects();
  const isBlocked = (x, y) => blocked(world, x, y);
  const enemyBlocked = (x, y) => isBlocked(x, y) || inVillageGrounds(world, x, y);
  const groundUnder = (x, y) => groundAt(world, x, y);
  let respawn = { x: 0, y: 0 };
  let barter = null;
  let zone = null;

  function hurtPlayer(e, damage, angle) {
    if (dodgeInvulnerable(combat)) onDodged(player.runes, player);
    if (player.dead || player.invuln > 0 || dodgeInvulnerable(combat)) return;
    const { hurt, knockback } = takeHit(player.runes, player, damage);
    player.hp = Math.max(0, player.hp - hurt);
    player.invuln = HURT_INVULN;
    player.flash = 0.12;
    if (knockback) {
      player.vx = Math.cos(angle) * HURT_KNOCK;
      player.vy = Math.sin(angle) * HURT_KNOCK;
    }
    cancelCombat(combat);
    hitStop(fx, 0.08);
    shake(fx, 4);
    burst(fx, player.x, player.y - 16, angle, { count: 10, speed: 120, spread: 1.2, colors: ["blood-2", "blood-3"], life: 0.4 });
    if (!player.hp) {
      player.dead = DEATH_SECONDS;
      barter = null;
      showTitle("You have fallen");
    }
  }

  resize();
  addEventListener("resize", resize);

  let last = performance.now();
  let time = 0;
  function tick(now) {
    const realDt = Math.min((now - last) / 1000, 0.1);
    last = now;
    const dt = gameDt(fx, realDt);
    time += dt;

    const input = readInput();
    const w = Math.ceil(canvas.width / WORLD_SCALE);
    const h = Math.ceil(canvas.height / WORLD_SCALE);
    const px = w >> 1;
    const py = h >> 1;
    const villages = nearbyVillages(world, player.x, player.y);
    const village = villageAt(villages, player.x, player.y);
    if (village) respawn = { x: village.x, y: village.y + 40 };
    villages.forEach((v) => updateVillage(v, dt, groundUnder, isBlocked));

    player.runes = runeStats(inventory.sockets);
    player.speed = PLAYER_SPEED * speedFactor(player.runes);
    const calm = !enemies.list.some((e) => !e.dying && Math.hypot(e.x - player.x, e.y - player.y) < CALM_RANGE);
    if (!player.dead) updateRunes(player.runes, player, dt, calm);
    const uiOpen = Boolean(barter || inventory.open);
    const mouseView = toView(mouse);
    const aim = Math.atan2(mouseView.y - (py - 14), mouseView.x - px);
    const attack = !uiOpen && !player.dead && input.click?.button === 0;
    player.invuln -= dt;
    player.flash -= dt;
    if (player.dead) {
      if ((player.dead -= realDt) <= 0) {
        Object.assign(player, { ...respawn, hp: MAX_HP, shield: 0, dead: 0, vx: 0, vy: 0 });
        enemies.list = [];
      }
      updateActor(player, { x: 0, y: 0 }, dt, groundUnder(player.x, player.y), isBlocked);
    } else {
      const move = updateCombat(player, combat, { ...input, attack, dodge: input.dodge && !uiOpen }, aim, dt, enemies.list, fx);
      updateActor(player, move.input, dt, move.ground ?? groundUnder(player.x, player.y), isBlocked);
    }
    updateEnemies(enemies, dt, {
      player, sheets: images.hollow, playerSafe: Boolean(village), blocked: enemyBlocked, groundAt: groundUnder, hurtPlayer,
      canSpawn: (x, y) => !enemyBlocked(x, y) && !inVillageGrounds(world, x, y),
      onDeath: (e) => addCorpse(world, e.x, e.y, e.id, e.facing),
    });
    for (const e of enemies.list) {
      if (e.bleed?.time > 0 && Math.random() < dt * 8) burst(fx, e.x, e.y - 10, Math.PI / 2, { count: 1, speed: 30, spread: 0.6, colors: ["blood-2"], life: 0.5 });
    }
    updateParticles(fx, dt);

    if (barter && Math.hypot(barter.barterer.x - player.x, barter.barterer.y - player.y) > BARTER_RANGE) barter = null;
    const villager = village && nearestVillager(village, player.x, player.y);
    const lootable = !villager && nearestLootable(world, player.x, player.y);
    if (input.close) barter = null;
    if (input.inventory) inventory.open = !inventory.open;
    if (input.interact && !player.dead) {
      if (barter) barter = null;
      else if (villager?.role === "barterer") barter = village;
      else if (villager) talk(villager);
      else if (lootable) search(world, inventory, lootable);
      if (barter) inventory.open = false;
    }
    if (inventory.open && input.click) {
      const message = clickInventory(inventory, toView(input.click, 1), canvas.width, canvas.height);
      if (message) inventory.message = { text: message, time };
    }
    const offers = barter && barterOffers(barter, time);
    if (barter && input.click) {
      const click = toView(input.click);
      const i = offerAt(offers, click.x, click.y, w, h);
      if (i >= 0 && !trade(inventory, offers[i], input.click.shift ? SHIFT_TIMES : 1)) say("Not enough metal.", "ash-3");
    }

    const name = village ? village.name : biomeAt(world, player.x, player.y).name;
    if (name !== zone && !player.dead) showTitle((zone = name));

    const [sx, sy] = shakeOffset(fx, realDt);
    const camX = Math.round(player.x) - px + sx;
    const camY = Math.round(player.y) - py + sy;
    const screen = (a) => [Math.round(a.x) - camX, Math.round(a.y) - camY];
    const villagers = villages.flatMap((v) => [v.barterer, ...v.villagers]);

    ctx.setTransform(WORLD_SCALE, 0, 0, WORLD_SCALE, 0, 0);
    drawGround(ctx, world, camX, camY, w, h);
    const props = visibleProps(world, camX, camY, w, h);
    props.filter((p) => p.def.flat).forEach((p) => drawProp(ctx, world, p, camX, camY, time, colors));
    [...props.filter((p) => !p.def.flat), ...villagers, ...enemies.list, player]
      .sort((a, b) => a.y - b.y)
      .forEach((e) => {
        if (e === player) drawPlayer(ctx, player, combat, ...screen(player), colors, images, camX, camY);
        else if (e.state) drawEnemy(ctx, e, ...screen(e), colors, time);
        else if (e.sheets) drawActor(ctx, e, ...screen(e), colors);
        else drawProp(ctx, world, e, camX, camY, time, colors);
      });
    drawParticles(ctx, fx, colors, camX, camY);
    villagers.filter((a) => a.speech).forEach((a) => drawSpeech(ctx, colors, a.speech.text, screen(a)[0], screen(a)[1] - 62));

    if (player.dead) {
      ctx.globalAlpha = Math.min(0.75, (DEATH_SECONDS - player.dead) * 0.6);
      ctx.fillStyle = colors["void-0"];
      ctx.fillRect(0, 0, w, h);
      ctx.globalAlpha = 1;
    }
    if ((villager || lootable) && !barter && !player.dead) drawKeyPrompt(ctx, colors, "E", px, py - 58);
    drawMessages(ctx, colors, px, py - 50, realDt);
    drawTitle(ctx, colors, w, realDt, village ? "Safe" : null);
    drawHealth(ctx, colors, player.hp, MAX_HP, 4, 4, player.shield);
    drawText(ctx, CONTROLS, 4, h - 8, colors["ash-3"], colors["void-0"]);
    if (barter) drawBarter(ctx, colors, images, inventory, barter, offers, mouseView, w, h);
    if (inventory.open) {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      drawInventory(ctx, inventory, images, colors, toView(mouse, 1), canvas.width, canvas.height, player.runes, time);
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

start();
