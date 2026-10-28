import { addItem, removeItem, countItem } from "./inventory.js";
import { itemInfo, drawIcon } from "./items.js";
import { drawText, textWidth } from "./font.js";
import { drawFrame } from "./ui.js";

const W = 176;
const PAD = 6;
const ROW_H = 12;
const METALS = ["bronze", "silver", "gold"];
export const SHIFT_TIMES = 10;

function layout(screenW, screenH, count) {
  const h = PAD * 2 + 32 + count * ROW_H + 12;
  return { x: (screenW - W) >> 1, y: (screenH - h) >> 1, h };
}

const rowTop = (box, i) => box.y + PAD + 32 + i * ROW_H;

// Trades as many times as asked and affordable. Returns how many went through.
export function trade(inventory, offer, times) {
  let done = 0;
  for (; done < times && countItem(inventory, offer.give[0]) >= offer.give[1]; done++) {
    removeItem(inventory, ...offer.give);
    const left = addItem(inventory, ...offer.get);
    if (left) {
      removeItem(inventory, offer.get[0], offer.get[1] - left);
      addItem(inventory, ...offer.give);
      break;
    }
  }
  return done;
}

// Index of the offer under a point, or -1.
export function offerAt(offers, x, y, screenW, screenH) {
  const box = layout(screenW, screenH, offers.length);
  if (x < box.x + PAD || x >= box.x + W - PAD) return -1;
  return offers.findIndex((_, i) => y >= rowTop(box, i) && y < rowTop(box, i) + ROW_H - 1);
}

export function drawBarter(ctx, colors, images, inventory, village, offers, mouse, screenW, screenH) {
  const box = layout(screenW, screenH, offers.length);
  drawFrame(ctx, colors, box.x, box.y, W, box.h);
  drawText(ctx, `Barterer of ${village.name}`, box.x + PAD, box.y + PAD - 1, colors["bone-0"], colors["void-0"]);

  METALS.forEach((key, i) => {
    const x = box.x + PAD + i * 56;
    const count = countItem(inventory, key);
    drawIcon(ctx, images, key, count, x, box.y + PAD + 8);
    drawText(ctx, `${count}g`, x + 18, box.y + PAD + 14, colors[count ? "bone-1" : "ash-2"]);
  });

  const hovered = offerAt(offers, mouse.x, mouse.y, screenW, screenH);
  offers.forEach((offer, i) => {
    const y = rowTop(box, i);
    const affordable = countItem(inventory, offer.give[0]) >= offer.give[1];
    if (i === hovered && affordable) {
      ctx.fillStyle = colors["void-3"];
      ctx.fillRect(box.x + PAD - 2, y - 2, W - PAD * 2 + 4, ROW_H - 1);
    }
    const give = `${offer.give[1]}g ${itemInfo(offer.give[0]).name}`;
    const get = `${offer.get[1]}g ${itemInfo(offer.get[0]).name}`;
    const color = colors[affordable ? "bone-0" : "ash-2"];
    drawText(ctx, give, box.x + PAD, y, color);
    drawText(ctx, ">", box.x + 76, y, colors["ash-3"]);
    drawText(ctx, get, box.x + W - PAD - textWidth(get), y, color);
  });

  const hint = "Click trade  Shift x10  E close";
  drawText(ctx, hint, box.x + ((W - textWidth(hint)) >> 1), box.y + box.h - PAD - 5, colors["ash-3"]);
}

