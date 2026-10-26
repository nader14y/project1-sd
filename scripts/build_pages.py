"""Build a static GitHub Pages site; never modify the original engine."""

import argparse
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parent.parent


def build(destination):
    destination = Path(destination).resolve()
    if destination == ROOT or ROOT in destination.parents and destination.parts[-2:] != ("dist", "pages"):
        raise ValueError("Use dist/pages or a directory outside the source checkout")
    destination.mkdir(parents=True, exist_ok=True)
    environment = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape())
    html = environment.get_template("index.html").render(url_for=lambda endpoint, filename: f"./static/{filename}")
    html = html.replace('href="/"', 'href="./"')
    html = html.replace('<script src="./static/app.js"', '<script src="./static/pages-bridge.js" defer></script>\n  <script src="./static/app.js"')
    html = html.replace("در حال آماده‌سازی زمین بازی…", "در حال دریافت موتور بازی؛ بار اول ممکن است کمی طول بکشد…")
    html = html.replace("رتبه‌بندی بر اساس تعداد برد، سپس امتیاز", "امتیازها فقط در همین مرورگر ذخیره می‌شوند")
    html = html.replace("</ul>\n    <button", "<li>در این نسخه، زمان و امتیازها در مرورگر محاسبه می‌شوند و جدول قهرمان‌ها فقط روی همین مرورگر ذخیره می‌شود.</li></ul>\n    <button")
    (destination / "index.html").write_text(html, encoding="utf-8")
    (destination / ".nojekyll").touch()
    assets = destination / "static"
    assets.mkdir(exist_ok=True)
    for name in ("app.js", "style.css", "favicon.svg", "pages-bridge.js"):
        shutil.copy2(ROOT / "static" / name, assets / name)
    for name in ("engine.py", "storage.py", "web_game.py", "pages_runtime.py", "questions.json"):
        shutil.copy2(ROOT / name, destination / name)
    print(f"GitHub Pages build ready: {destination}")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "pages")
    build(parser.parse_args().output)
