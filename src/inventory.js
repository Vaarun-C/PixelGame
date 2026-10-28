import { itemInfo, drawIcon, TIERS } from "./items.js";
import { drawText, textWidth, LARGE } from "./font.js";
import { drawIronFrame, drawInset, drawRule } from "./ui.js";
import {
  SOCKETS, MAX_NOTCHES, createSockets, fits, passiveLines, carveCost, carved, canFuse, fuseCost, fused,
} from "./runes.js";

const COLS = 6;
const ROWS = 4;
const SAVE_KEY = "pixelgame.inventory";
const SOCKETS_KEY = "pixelgame.sockets";
// Layout of the 2x-resolution panel, in canvas pixels.
const SLOT = 36;
const GAP = 4;
const ICON = 32;
const PANEL_W = 640;
const PANEL_H = 360;
const BAG_X = 196;
const BAG_Y = 52;
const SIDE_W = 160;
const SECTION_H = 228;
const SOCKET_R = 13;
const SOCKET_STEP = 32;
const BUTTON = { w: 78, h: 20 };
const MESSAGE_TIME = 2.5;

// selected: bag index of the item shown in the detail panel; fusing: waiting for a second rune.
export function createInventory() {
  return { open: false, slots: load(), sockets: loadSockets(), selected: null, fusing: false };
}

function loadSockets() {
  const sockets = createSockets();
  try {
    const saved = JSON.parse(localStorage.getItem(SOCKETS_KEY)) ?? {};
    for (const part of Object.keys(SOCKETS)) {
      sockets[part] = sockets[part].map((_, i) => {
        const key = saved[part]?.[i];
        return key && itemInfo(key)?.types && fits(key, part) ? key : null;
      });
    }
  } catch {}
  return sockets;
}

function load() {
  try {
    const slots = JSON.parse(localStorage.getItem(SAVE_KEY));
    // Items that no longer exist (e.g. old coins) are dropped; everything else is kept.
    if (Array.isArray(slots) && slots.length === COLS * ROWS) {
      return slots.map((s) => (s && itemInfo(s.key) && s.count > 0 ? s : null));
    }
  } catch {}
  return Array(COLS * ROWS).fill(null);
}

function save(inventory) {
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify(inventory.slots));
    localStorage.setItem(SOCKETS_KEY, JSON.stringify(inventory.sockets));
  } catch {}
}

// Returns how many didn't fit.
export function addItem(inventory, key, count) {
  const { stack } = itemInfo(key);
  const { slots } = inventory;
  for (const slot of slots) {
    if (slot?.key !== key) continue;
    const n = Math.min(count, stack - slot.count);
    slot.count += n;
    count -= n;
  }
  for (let i = 0; i < slots.length && count > 0; i++) {
    if (slots[i]) continue;
    const n = Math.min(count, stack);
    slots[i] = { key, count: n };
    count -= n;
  }
  save(inventory);
  return count;
}

export const countItem = (inventory, key) =>
  inventory.slots.reduce((sum, slot) => sum + (slot?.key === key ? slot.count : 0), 0);

// Removes up to `count`; returns how many were removed.
export function removeItem(inventory, key, count) {
  let removed = 0;
  inventory.slots.forEach((slot, i) => {
    if (slot?.key !== key || removed === count) return;
    const n = Math.min(slot.count, count - removed);
    slot.count -= n;
    removed += n;
    if (!slot.count) inventory.slots[i] = null;
  });
  save(inventory);
  return removed;
}

// Panel geometry in canvas pixels, shared by drawing and clicks.
function layout(screenW, screenH) {
  const x0 = (screenW - PANEL_W) >> 1;
  const y0 = (screenH - PANEL_H) >> 1;
  const bag = Array.from({ length: COLS * ROWS }, (_, i) => ({
    x: x0 + BAG_X + (i % COLS) * (SLOT + GAP), y: y0 + BAG_Y + Math.floor(i / COLS) * (SLOT + GAP), w: SLOT, h: SLOT,
  }));
  const side = { x: x0 + 18, y: y0 + 38 };
  const sockets = Object.entries(SOCKETS).flatMap(([part, count], row) => Array.from({ length: count }, (_, i) => {
    const cx = side.x + 73 + i * SOCKET_STEP;
    const cy = side.y + 141 + row * SOCKET_STEP;
    return { part, i, row, cx, cy, x: cx - SOCKET_R, y: cy - SOCKET_R, w: SOCKET_R * 2 + 1, h: SOCKET_R * 2 + 1 };
  }));
  const detail = { x: x0 + PANEL_W - 194, y: y0 + 38, w: SIDE_W + 16, h: SECTION_H };
  const by = detail.y + detail.h - BUTTON.h - 8;
  const buttons = [
    { id: "carve", x: detail.x + 8, y: by, ...BUTTON },
    { id: "fuse", x: detail.x + detail.w - 8 - BUTTON.w, y: by, ...BUTTON },
  ];
  return { x0, y0, bag, side, sockets, detail, buttons };
}

const inside = (r, p) => p.x >= r.x && p.x < r.x + r.w && p.y >= r.y && p.y < r.y + r.h;
const isRune = (slot) => Boolean(slot && itemInfo(slot.key).types);
const selectedRune = (inv) => (isRune(inv.slots[inv.selected]) ? inv.slots[inv.selected].key : null);

// A click on the open inventory at canvas point p. Returns a message to show, if any.
export function clickInventory(inv, p, screenW, screenH) {
  const L = layout(screenW, screenH);
  const bagIndex = L.bag.findIndex((r) => inside(r, p));
  if (bagIndex >= 0) return clickBag(inv, bagIndex);
  const socket = L.sockets.find((r) => inside(r, p));
  if (socket) return clickSocket(inv, socket.part, socket.i);
  const button = selectedRune(inv) && L.buttons.find((r) => inside(r, p));
  if (button?.id === "carve") return carve(inv);
  if (button?.id === "fuse") {
    if (itemInfo(selectedRune(inv)).types.length > 1) return "Fused runes can't fuse again.";
    inv.fusing = !inv.fusing;
    return null;
  }
  if (!inside(L.detail, p)) Object.assign(inv, { selected: null, fusing: false });
  return null;
}

function clickBag(inv, i) {
  const slot = inv.slots[i];
  if (inv.fusing && i !== inv.selected) return fuse(inv, i);
  Object.assign(inv, { selected: inv.selected === i || !slot ? null : i, fusing: false });
  return null;
}

function clickSocket(inv, part, i) {
  const current = inv.sockets[part][i];
  const key = selectedRune(inv);
  if (key) {
    if (!fits(key, part)) return `${itemInfo(key).name} won't sit in the ${part}.`;
    inv.slots[inv.selected] = current ? { key: current, count: 1 } : null;
    inv.sockets[part][i] = key;
    Object.assign(inv, { selected: null, fusing: false });
  } else if (current) {
    const free = inv.slots.indexOf(null);
    if (free < 0) return "Bag is full.";
    inv.slots[free] = { key: current, count: 1 };
    inv.sockets[part][i] = null;
  }
  save(inv);
  return null;
}

function carve(inv) {
  const key = selectedRune(inv);
  if (itemInfo(key).notches >= MAX_NOTCHES) return "No room for another notch.";
  const cost = carveCost(key);
  if (countItem(inv, "shard") < cost) return `Carving needs ${cost} shards.`;
  removeItem(inv, "shard", cost);
  inv.slots[inv.selected] = { key: carved(key), count: 1 };
  save(inv);
  return `Notch ${itemInfo(key).notches + 1} carved.`;
}

function fuse(inv, i) {
  const a = selectedRune(inv);
  const b = isRune(inv.slots[i]) ? inv.slots[i].key : null;
  if (!b) return "Pick a rune to fuse with.";
  if (!canFuse(a, b)) return "Only two single runes of different types can fuse.";
  const cost = fuseCost(a, b);
  if (countItem(inv, "shard") < cost) return `Fusing needs ${cost} shards.`;
  const key = fused(a, b);
  inv.slots[i] = null;
  inv.slots[inv.selected] = { key, count: 1 };
  removeItem(inv, "shard", cost);
  inv.fusing = false;
  inv.selected = inv.slots.findIndex((s) => s?.key === key);
  save(inv);
  return `Fused: ${itemInfo(key).name}.`;
}

// Drawn at native canvas pixels (the 2x-resolution UI): screenW/screenH and mouse are canvas pixels.
// stats: the socketed runes' effects (runes.js runeStats), for the active resonances.
// inv.message: { text, time } from the last click, shown for MESSAGE_TIME seconds after `time`.
export function drawInventory(ctx, inv, images, colors, mouse, screenW, screenH, stats, time) {
  const L = layout(screenW, screenH);
  const text = (t, x, y, color, shadow) => drawText(ctx, t, x, y, colors[color], shadow && colors[shadow], 1, LARGE);
  const centred = (t, x, w, y, color, shadow) => text(t, x + ((w - textWidth(t, 1, LARGE)) >> 1), y, color, shadow);
  const ui = { ctx, images, colors, text, centred };

  ctx.globalAlpha = 0.6;
  ctx.fillStyle = colors["void-0"];
  ctx.fillRect(0, 0, screenW, screenH);
  ctx.globalAlpha = 1;
  drawIronFrame(ctx, colors, L.x0, L.y0, PANEL_W, PANEL_H);
  centred("Inventory", L.x0, PANEL_W, L.y0 + 14, "bone-0", "void-0");
  drawRule(ctx, colors, L.x0 + 20, L.y0 + 28, PANEL_W - 40);

  const hoveredBag = drawBag(ui, inv, L, mouse);
  const hoveredSocket = drawCharacter(ui, inv, L, mouse, stats);
  const shown = inv.slots[inv.selected] ?? hoveredBag ?? hoveredSocket;
  drawDetail(ui, inv, L, shown, mouse, stats);
  drawSummary(ui, inv, L.x0 + 18, L.y0 + PANEL_H - 82);
  const close = "I  Close";
  text(close, L.x0 + PANEL_W - 20 - textWidth(close, 1, LARGE), L.y0 + PANEL_H - 14, "ash-3");
  if (inv.message && time - inv.message.time < MESSAGE_TIME) text(inv.message.text, L.x0 + 20, L.y0 + PANEL_H - 14, "bone-0");
}

function drawBag({ ctx, images, colors, text }, inv, L, mouse) {
  let hovered = null;
  text("Bag", L.bag[0].x, L.bag[0].y - 12, "ash-3");
  inv.slots.forEach((slot, i) => {
    const { x, y } = L.bag[i];
    drawInset(ctx, colors, x, y, SLOT, SLOT, "void-0");
    const ring = i === inv.selected ? "bone-0" : inv.fusing && isRune(slot) ? "rune-pale-dark" : inside(L.bag[i], mouse) && slot ? "gilt-2" : null;
    if (ring) {
      ctx.fillStyle = colors[ring];
      outline(ctx, x - 1, y - 1, SLOT + 2, SLOT + 2);
    }
    if (!slot) return;
    if (inside(L.bag[i], mouse)) hovered = slot;
    drawIcon(ctx, images, slot.key, slot.count, x + 2, y + 2, ICON);
    drawNotches(ctx, colors, slot.key, x + 3, y + SLOT - 4);
    if (slot.count > 1) text(String(slot.count), x + SLOT - 2 - textWidth(String(slot.count), 1, LARGE), y + SLOT - 9, "bone-1", "void-0");
  });
  return hovered;
}

// Carved notches as small marks in the rune's tier colour along the slot's bottom edge.
function drawNotches(ctx, colors, key, x, y) {
  const info = itemInfo(key);
  if (!info.notches) return;
  ctx.fillStyle = colors[`rune-${TIERS[info.tier - 1]}-mid`];
  for (let n = 0; n < info.notches; n++) ctx.fillRect(x + n * 3, y, 2, 2);
}

function drawCharacter({ ctx, images, colors, text, centred }, inv, L, mouse, stats) {
  const { x, y } = L.side;
  drawInset(ctx, colors, x, y, SIDE_W, SECTION_H, "void-2");
  centred("Wanderer", x, SIDE_W, y + 8, "ash-3");
  ctx.drawImage(images.wanderer.idle, 0, 0, 96, 96, x + ((SIDE_W - 96) >> 1), y + 22, 96, 96);
  const key = selectedRune(inv);
  let hovered = null;
  for (const s of L.sockets) {
    if (s.i === 0) text(s.part, x + 10, s.cy - 3, "ash-4");
    disc(ctx, colors[key && fits(key, s.part) ? "gilt-2" : "void-0"], s.cx, s.cy, SOCKET_R);
    disc(ctx, colors["void-2"], s.cx, s.cy, SOCKET_R - 2);
    const rune = inv.sockets[s.part][s.i];
    if (rune) {
      drawIcon(ctx, images, rune, 1, s.cx - 16, s.cy - 16, ICON);
      if (inside(s, mouse)) hovered = { key: rune, count: 1 };
    } else disc(ctx, colors["void-3"], s.cx, s.cy, 2);
  }
  const names = stats.resonances.map((r) => [r.name, r.cursed ? "rune-crimson-mid" : "bone-0"]);
  if (!names.length) names.push(["No resonance", "ash-3"]);
  names.slice(0, 3).forEach(([name, color], i) => centred(name, x, SIDE_W, y + 192 + i * LARGE.line, color, "void-0"));
  return hovered;
}

function drawDetail({ ctx, images, colors, text, centred }, inv, L, slot, mouse, stats) {
  const { x, y, w } = L.detail;
  drawInset(ctx, colors, x, y, w, L.detail.h, "void-2");
  if (!slot) {
    if (!stats.resonances.length) return centred("Pick an item", x, w, y + 104, "ash-3");
    let ly = y + 12;
    for (const r of stats.resonances) {
      text(r.name, x + 10, ly, r.cursed ? "rune-crimson-mid" : "bone-0");
      wrap(r.desc, 26).forEach((line, i) => text(line, x + 10, ly + 12 + i * LARGE.line, "ash-4"));
      ly += 16 + wrap(r.desc, 26).length * LARGE.line;
    }
    return;
  }
  const info = itemInfo(slot.key);
  drawInset(ctx, colors, x + ((w - 40) >> 1), y + 10, 40, 40, "void-0");
  drawIcon(ctx, images, slot.key, slot.count, x + ((w - ICON) >> 1), y + 14, ICON);
  const name = wrap(info.name, 26);
  name.forEach((line, i) => centred(line, x, w, y + 56 + i * LARGE.line, info.color, "void-0"));
  let ly = y + 60 + name.length * LARGE.line;
  drawRule(ctx, colors, x + 16, ly, w - 32);
  ly += 8;
  const lines = info.types ? passiveLines(slot.key) : wrap(info.desc, 26);
  lines.forEach((line, i) => text(line, x + 10, ly + i * LARGE.line, info.types ? "bone-0" : "ash-4"));
  ly += lines.length * LARGE.line + 6;
  if (info.unit) text(`Weight: ${slot.count}${info.unit}`, x + 10, ly, "ash-3");
  if (!info.types) return;
  TIERS.forEach((tier, i) => drawTierGem(ctx, colors, tier, x + 15 + i * 14, ly + 5, i < info.tier));
  text(`${info.notches}/${MAX_NOTCHES}`, x + w - 10 - textWidth(`${info.notches}/${MAX_NOTCHES}`, 1, LARGE), ly + 2, "ash-3");
  wrap(info.desc, 26).forEach((line, i) => text(line, x + 10, ly + 16 + i * LARGE.line, "ash-3"));

  if (slot !== inv.slots[inv.selected]) return;
  if (inv.fusing) centred("Pick a rune to fuse", x, w, L.buttons[0].y - 14, "rune-pale-mid");
  const labels = {
    carve: info.notches < MAX_NOTCHES ? `Carve ${carveCost(slot.key)}` : "Carved",
    fuse: inv.fusing ? "Cancel" : "Fuse",
  };
  for (const b of L.buttons) {
    drawInset(ctx, colors, b.x, b.y, b.w, b.h, inside(b, mouse) ? "steel-0" : "void-1");
    centred(labels[b.id], b.x, b.w, b.y + 7, inside(b, mouse) ? "bone-1" : "bone-0");
  }
}

function drawSummary({ ctx, images, colors, text }, inv, x, y) {
  const w = PANEL_W - 36;
  drawInset(ctx, colors, x, y, w, 64, "void-2");
  let lx = x + 14;
  for (const [key, unit] of [["bronze", "g"], ["silver", "g"], ["gold", "g"], ["shard", ""]]) {
    const count = countItem(inv, key);
    drawIcon(ctx, images, key, Math.max(count, 1), lx, y + 16, ICON);
    const label = `${count}${unit}`;
    text(label, lx + 36, y + 28, count ? "ash-4" : "ash-2");
    lx += 36 + textWidth(label, 1, LARGE) + 22;
  }
  text("Runes", lx + 6, y + 12, "ash-3");
  TIERS.forEach((tier, i) => {
    const count = inv.slots.reduce((n, s) => n + (s && itemInfo(s.key).tier === i + 1 ? s.count : 0), 0);
    const tx = lx + 6 + i * 30;
    drawTierGem(ctx, colors, tier, tx + 5, y + 34, count > 0);
    text(String(count), tx + 14, y + 31, count ? "ash-4" : "ash-2");
  });
}

// A faceted gem in a rune tier's colours; dimmed tiers show only the dark facet.
function drawTierGem(ctx, colors, tier, cx, cy, lit) {
  for (let d = 0; d <= 4; d++) {
    const w = d * 2 + 1;
    ctx.fillStyle = colors["void-0"];
    ctx.fillRect(cx - d - 1, cy - 5 + d, w + 2, 1);
    ctx.fillRect(cx - d - 1, cy + 5 - d, w + 2, 1);
  }
  for (let d = 0; d <= 3; d++) {
    const w = d * 2 + 1;
    ctx.fillStyle = colors[lit ? `rune-${tier}-mid` : `rune-${tier}-dark`];
    ctx.fillRect(cx - d, cy - 4 + d, w, 1);
    ctx.fillStyle = colors[lit ? `rune-${tier}-dark` : "void-3"];
    ctx.fillRect(cx - d, cy + 4 - d, w, 1);
  }
  if (lit) {
    ctx.fillStyle = colors[`rune-${tier}-core`];
    ctx.fillRect(cx - 1, cy - 2, 1, 1);
  }
}

function disc(ctx, color, cx, cy, r) {
  ctx.fillStyle = color;
  for (let dy = -r; dy <= r; dy++) {
    const dx = Math.floor(Math.sqrt(r * r + r - dy * dy));
    ctx.fillRect(cx - dx, cy + dy, dx * 2 + 1, 1);
  }
}

function outline(ctx, x, y, w, h) {
  ctx.fillRect(x, y, w, 1);
  ctx.fillRect(x, y + h - 1, w, 1);
  ctx.fillRect(x, y, 1, h);
  ctx.fillRect(x + w - 1, y, 1, h);
}

function wrap(text, chars) {
  const lines = [""];
  for (const word of text.split(" ")) {
    const line = lines[lines.length - 1];
    if (line && line.length + word.length + 1 > chars) lines.push(word);
    else lines[lines.length - 1] = line ? `${line} ${word}` : word;
  }
  return lines;
}
