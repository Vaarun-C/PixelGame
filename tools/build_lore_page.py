"""Bundle every lore/**/*.md file into one HTML page (tools/lore_page.html is the template)."""
import base64
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LORE = ROOT / "lore"


def embed_images(md_path):
    def data_uri(m):
        image = (md_path.parent / m[2]).resolve()
        return f"![{m[1]}](data:image/png;base64,{base64.b64encode(image.read_bytes()).decode()})"
    return re.sub(r"!\[([^\]]*)\]\(([^)]+\.png)\)", data_uri, md_path.read_text())


def build(out):
    files = {p.relative_to(LORE).as_posix(): embed_images(p) for p in sorted(LORE.rglob("*.md"))}
    data = json.dumps(files).replace("</", "<\\/")
    template = (ROOT / "tools" / "lore_page.html").read_text()
    Path(out).write_text(template.replace("/*LORE_DATA*/", data))
    print(f"{len(files)} files -> {out}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "lore_page.html")
