import { drawText, textWidth, LINE_HEIGHT } from "./font.js";

const MESSAGE_LIFE = 2;
const TITLE_LIFE = 3;
const messages = [];
let title = null;

export function drawFrame(ctx, colors, x, y, w, h) {
  ctx.fillStyle = colors["void-0"];
  ctx.fillRect(x - 1, y - 1, w + 2, h + 2);
  ctx.fillStyle = colors["steel-1"];
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = colors["steel-2"];
  ctx.fillRect(x, y, w - 1, 1);
  ctx.fillRect(x, y, 1, h - 1);
  ctx.fillStyle = colors["void-1"];
  ctx.fillRect(x + 1, y + 1, w - 2, h - 2);
}

// Style A (gothic iron and bone) for the 2x-resolution UI, in canvas pixels.
const RIVET_EVERY = 32;
const CORNER = 16;

function bevel(ctx, colors, x, y, w, h, light, dark) {
  ctx.fillStyle = colors[light];
  ctx.fillRect(x, y, w, 1);
  ctx.fillRect(x, y, 1, h);
  ctx.fillStyle = colors[dark];
  ctx.fillRect(x, y + h - 1, w, 1);
  ctx.fillRect(x + w - 1, y, 1, h);
}

// A sunken panel or slot: dark fill with a bevel lit from the top-left.
export function drawInset(ctx, colors, x, y, w, h, fill) {
  ctx.fillStyle = colors[fill];
  ctx.fillRect(x, y, w, h);
  bevel(ctx, colors, x, y, w, h, "void-0", "steel-1");
}

export function drawRule(ctx, colors, x, y, w) {
  ctx.fillStyle = colors["void-0"];
  ctx.fillRect(x, y, w, 1);
  ctx.fillStyle = colors["steel-1"];
  ctx.fillRect(x, y + 1, w, 1);
}

// Blackened iron band with rivets and gilt corner bosses, each holding a small bone skull.
export function drawIronFrame(ctx, colors, x, y, w, h) {
  ctx.fillStyle = colors["void-0"];
  ctx.fillRect(x - 2, y - 2, w + 4, h + 4);
  ctx.fillStyle = colors["steel-0"];
  ctx.fillRect(x, y, w, h);
  bevel(ctx, colors, x, y, w, h, "steel-2", "void-1");
  ctx.fillStyle = colors["void-1"];
  ctx.fillRect(x + 6, y + 6, w - 12, h - 12);
  bevel(ctx, colors, x + 6, y + 6, w - 12, h - 12, "void-0", "steel-1");
  for (let rx = x + 24; rx < x + w - 20; rx += RIVET_EVERY) {
    for (const ry of [y + 2, y + h - 5]) {
      ctx.fillStyle = colors["ash-2"];
      ctx.fillRect(rx, ry, 2, 2);
      ctx.fillStyle = colors["void-0"];
      ctx.fillRect(rx + 1, ry + 1, 1, 1);
    }
  }
  for (const [cx, cy] of [[x, y], [x + w - CORNER, y], [x, y + h - CORNER], [x + w - CORNER, y + h - CORNER]]) {
    drawCornerBoss(ctx, colors, cx, cy);
  }
}

function drawCornerBoss(ctx, colors, x, y) {
  const px = (name, ...rects) => {
    ctx.fillStyle = colors[name];
    rects.forEach(([rx, ry, rw = 1, rh = 1]) => ctx.fillRect(x + rx, y + ry, rw, rh));
  };
  px("gilt-0", [0, 0, CORNER, CORNER]);
  bevel(ctx, colors, x, y, CORNER, CORNER, "gilt-2", "void-0");
  px("gilt-1", [3, 3, 10, 10]);
  px("bone-0", [5, 4, 6, 5], [6, 9, 4, 2]);
  px("bone-1", [5, 4, 6, 1]);
  px("void-0", [6, 6], [9, 6]);
  px("void-1", [7, 10], [8, 10]);
}

// lines: [[text, colorName], ...]
export function drawTooltip(ctx, colors, lines, x, y, screenW, screenH) {
  const w = Math.max(...lines.map(([text]) => textWidth(text))) + 6;
  const h = lines.length * LINE_HEIGHT + 5;
  x = Math.min(x, screenW - w - 2);
  y = Math.min(y, screenH - h - 2);
  drawFrame(ctx, colors, x, y, w, h);
  lines.forEach(([text, color], i) => drawText(ctx, text, x + 3, y + 3 + i * LINE_HEIGHT, colors[color]));
}

export function drawKeyPrompt(ctx, colors, key, x, y) {
  drawFrame(ctx, colors, x - 3, y, 7, 9);
  drawText(ctx, key, x - 1, y + 2, colors["bone-1"]);
}

export function say(text, color) {
  messages.push({ text, color, age: 0 });
}

export function drawMessages(ctx, colors, x, y, dt) {
  for (let i = messages.length - 1; i >= 0; i--) {
    if ((messages[i].age += dt) > MESSAGE_LIFE) messages.splice(i, 1);
  }
  messages.forEach((m, i) => {
    ctx.globalAlpha = Math.min(1, (MESSAGE_LIFE - m.age) * 2);
    const ty = y - (messages.length - i) * 7 - Math.floor(m.age * 6);
    drawText(ctx, m.text, x - (textWidth(m.text) >> 1), ty, colors[m.color], colors["void-0"]);
  });
  ctx.globalAlpha = 1;
}

export function showTitle(text) {
  title = { text, age: 0 };
}

// Big fading zone name at the top of the screen, with an optional small line under it.
export function drawTitle(ctx, colors, screenW, dt, subtitle) {
  if (title && (title.age += dt) > TITLE_LIFE) title = null;
  if (title) {
    ctx.globalAlpha = Math.min(1, (TITLE_LIFE - title.age) * 2, title.age * 4);
    drawText(ctx, title.text, (screenW - textWidth(title.text, 2)) >> 1, 12, colors["bone-0"], colors["void-0"], 2);
    ctx.globalAlpha = 1;
  }
  if (subtitle) drawText(ctx, subtitle, (screenW - textWidth(subtitle)) >> 1, title ? 26 : 6, colors["ash-4"], colors["void-0"]);
}

export function drawSpeech(ctx, colors, text, x, y) {
  const w = textWidth(text) + 6;
  drawFrame(ctx, colors, x - (w >> 1), y, w, 11);
  drawText(ctx, text, x - (w >> 1) + 3, y + 3, colors["bone-0"]);
}

// shield: Leech-shell HP drawn over the bar's start in steel.
export function drawHealth(ctx, colors, hp, max, x, y, shield = 0) {
  const w = 60;
  drawFrame(ctx, colors, x, y, w, 7);
  ctx.fillStyle = colors["void-0"];
  ctx.fillRect(x + 2, y + 2, w - 4, 3);
  ctx.fillStyle = colors["blood-3"];
  ctx.fillRect(x + 2, y + 2, Math.round(((w - 4) * hp) / max), 3);
  ctx.fillStyle = colors["blood-4"];
  ctx.fillRect(x + 2, y + 2, Math.round(((w - 4) * hp) / max), 1);
  if (shield <= 0) return;
  ctx.fillStyle = colors["steel-3"];
  ctx.fillRect(x + 2, y + 2, Math.min(w - 4, Math.round(((w - 4) * shield) / max)), 2);
}
