#!/usr/bin/env python3
"""Extract diagrams drawn in HTML/CSS or SVG from design pages, using a real browser layout.

For each HTML file, writes:
  <name>.diagrams.md      boxes, connections (from -> to : label) and unresolved items per diagram
  <name>_diagrams/diagram-N.png   a screenshot of each diagram, for the reviewer to attach

Needs Playwright with Chromium:  pip install playwright && playwright install chromium
If Playwright is not available, use the no-install method instead: open the page in Chrome or
Edge, press F12, paste scripts/diagram_extract.js into the Console, run extractAllDiagrams(),
and screenshot each diagram yourself.

Usage: python3 extract_diagrams.py page.html [more.html ...] [-o OUTPUT_DIR] [--width 1600]
"""
import argparse
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
JS = (HERE / "diagram_extract.js").read_text(encoding="utf-8")


def run(files, out_dir, width):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed. Use the browser Console method described in the docstring,", file=sys.stderr)
        print("or install it with: pip install playwright && playwright install chromium", file=sys.stderr)
        return 2
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 1000}, device_scale_factor=2)
        for f in files:
            path = pathlib.Path(f).resolve()
            target = pathlib.Path(out_dir).resolve() if out_dir else path.parent
            target.mkdir(parents=True, exist_ok=True)
            shots = target / f"{path.stem}_diagrams"
            try:
                page.goto(path.as_uri(), wait_until="networkidle")
                page.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")
                page.add_script_tag(content=JS)
                roots = page.evaluate_handle("window.__findDiagramRoots()")
                count = page.evaluate("r => r.length", roots)
                parts, n = [], 0
                for i in range(count):
                    el = page.evaluate_handle("([r, i]) => r[i]", [roots, i]).as_element()
                    res = page.evaluate("el => { const md = window.extractDiagram(el); return md; }", el)
                    boxes = page.evaluate(
                        "el => [...el.querySelectorAll('*')].length", el)
                    if "Extraction summary: 0 boxes" in res or "Extraction summary: 1 boxes" in res or boxes == 0:
                        continue
                    n += 1
                    shots.mkdir(parents=True, exist_ok=True)
                    png = shots / f"diagram-{n}.png"
                    el.scroll_into_view_if_needed()
                    el.screenshot(path=str(png))
                    res = res.replace("### Diagram 1 ", f"### Diagram {n} ", 1)
                    parts.append(res + f"Screenshot: {shots.name}/{png.name}\n")
                md = f"<!-- Diagrams extracted from {path.name} by rendering it in a browser. Check each against its screenshot. -->\n\n"
                md += "\n".join(parts) if parts else ("No diagrams found automatically. Open the page in Chrome or Edge, select the diagram in the Elements panel, "
                                                       "paste diagram_extract.js into the Console and run extractDiagram($0); or screenshot it.\n")
                out = target / f"{path.stem}.diagrams.md"
                out.write_text(md, encoding="utf-8")
                print(f"{f} -> {out}  ({n} diagrams)")
            except Exception as exc:
                print(f"{f}: failed: {exc}", file=sys.stderr)
        browser.close()
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("-o", "--out")
    ap.add_argument("--width", type=int, default=1600, help="browser width in pixels")
    a = ap.parse_args()
    sys.exit(run(a.files, a.out, a.width))


if __name__ == "__main__":
    main()
