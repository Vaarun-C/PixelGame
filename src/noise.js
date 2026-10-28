export function hash(...values) {
  let h = 2166136261;
  for (const v of values) h = Math.imul(h ^ v, 16777619);
  h ^= h >>> 15;
  return Math.imul(h, 2246822507) >>> 0;
}

export const random01 = (...values) => hash(...values) / 4294967296;

const smooth = (t) => t * t * (3 - 2 * t);
const lerp = (a, b, t) => a + (b - a) * t;

export function valueNoise(seed, x, y) {
  const x0 = Math.floor(x);
  const y0 = Math.floor(y);
  const sx = smooth(x - x0);
  const sy = smooth(y - y0);
  const v = (dx, dy) => random01(seed, x0 + dx, y0 + dy);
  return lerp(lerp(v(0, 0), v(1, 0), sx), lerp(v(0, 1), v(1, 1), sx), sy);
}
