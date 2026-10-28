// Pixel fonts. Each glyph is one character per row, read as a base-32 number whose bits are the
// pixels left to right. SMALL is the 3x5 HUD font; LARGE is the 5x7 font for the 2x-resolution UI.
const SMALL_GLYPHS = {
  A: "75755", B: "65656", C: "74447", D: "65556", E: "74647", F: "74644", G: "74557",
  H: "55755", I: "72227", J: "11157", K: "55655", L: "44447", M: "57755", N: "65555",
  O: "75557", P: "75744", Q: "75571", R: "75655", S: "74717", T: "72222", U: "55557",
  V: "55552", W: "55775", X: "55255", Y: "55222", Z: "71247",
  0: "75557", 1: "26227", 2: "71747", 3: "71317", 4: "55711", 5: "74717", 6: "74757",
  7: "71111", 8: "75757", 9: "75717",
  " ": "00000", ".": "00002", ",": "00024", ":": "02020", "!": "22202", "?": "71202",
  "'": "22000", "-": "00700", "+": "02720", "/": "11244", ">": "42124", "<": "12421",
};

const LARGE_GLYPHS = {
  A: "ehhvhhh", B: "uhhuhhu", C: "ehggghe", D: "uhhhhhu", E: "vgguggv", F: "vgguggg", G: "ehgnhhf", H: "hhhvhhh",
  I: "e44444e", J: "72222ic", K: "hikokih", L: "ggggggv", M: "hrllhhh", N: "hpljhhh", O: "ehhhhhe", P: "uhhuggg",
  Q: "ehhhlid", R: "uhhukih", S: "fgge11u", T: "v444444", U: "hhhhhhe", V: "hhhhha4", W: "hhhllla", X: "hha4ahh",
  Y: "hha4444", Z: "v1248gv", 0: "ehjlphe", 1: "4c4444e", 2: "eh1248v", 3: "v2421he", 4: "26aiv22", 5: "vgu11he",
  6: "68guhhe", 7: "v124888", 8: "ehhehhe", 9: "ehhf12c", " ": "0000000", ".": "00000cc", ",": "0000c48",
  ":": "0cc0cc0", "!": "4444404", "?": "eh12404", "'": "4480000", "-": "000e000", "+": "044v440", "/": "11248gg", "%": "pq248bj",
  x: "00ha4ah",
};

export const SMALL = { glyphs: SMALL_GLYPHS, w: 3, h: 5, line: 6 };
export const LARGE = { glyphs: LARGE_GLYPHS, w: 5, h: 7, line: 10 };
export const LINE_HEIGHT = SMALL.line;

export const textWidth = (text, scale = 1, font = SMALL) => (text.length * (font.w + 1) - 1) * scale;

export function drawText(ctx, text, x, y, color, shadow, scale = 1, font = SMALL) {
  if (shadow) drawText(ctx, text, x + scale, y + scale, shadow, null, scale, font);
  ctx.fillStyle = color;
  [...text.toUpperCase()].forEach((ch, i) => {
    const rows = font.glyphs[ch] ?? font.glyphs[ch.toLowerCase()] ?? font.glyphs["?"];
    for (let row = 0; row < font.h; row++) {
      const bits = parseInt(rows[row], 32);
      for (let col = 0; col < font.w; col++) {
        if (bits & (1 << (font.w - 1 - col))) ctx.fillRect(x + (i * (font.w + 1) + col) * scale, y + row * scale, scale, scale);
      }
    }
  });
}
