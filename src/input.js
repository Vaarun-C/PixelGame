const held = new Set();
const pressed = new Set();
export const mouse = { x: -1, y: -1 };
let click = null;

addEventListener("keydown", (e) => {
  if (e.code === "Tab" || e.code === "Space") e.preventDefault();
  if (!e.repeat) pressed.add(e.code);
  held.add(e.code);
});
addEventListener("keyup", (e) => held.delete(e.code));
addEventListener("blur", () => held.clear());
addEventListener("mousedown", (e) => {
  click = { x: e.clientX, y: e.clientY, shift: e.shiftKey, button: e.button };
});
addEventListener("mousemove", (e) => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
});

const any = (...codes) => codes.some((code) => held.has(code));
const tapped = (...codes) => codes.some((code) => pressed.has(code));

export function readInput() {
  const input = {
    x: any("KeyD", "ArrowRight") - any("KeyA", "ArrowLeft"),
    y: any("KeyS", "ArrowDown") - any("KeyW", "ArrowUp"),
    run: any("ShiftLeft", "ShiftRight"),
    interact: tapped("KeyE"),
    inventory: tapped("KeyI", "Tab"),
    close: tapped("Escape"),
    dodge: tapped("Space"),
    click,
  };
  pressed.clear();
  click = null;
  return input;
}
