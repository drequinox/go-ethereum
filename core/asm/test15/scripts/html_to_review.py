#!/usr/bin/env python3
"""Convert design HTML pages into clean Markdown review inputs.

Keeps what a security review needs and drops page noise:
  - headings, paragraphs, lists, tables, code blocks
  - collapsed <details> sections, always expanded
  - inline SVG diagrams: every text label, in document order, plus title and aria-label
  - Mermaid source blocks, kept as ```mermaid fences
  - embedded base64 images saved as files next to the output, so they can be attached
  - external images listed by path
Drops: <script> (except Mermaid), <style>, <noscript>, navigation chrome.

Standard library only. Usage:
  python3 html_to_review.py page.html [more.html ...] [-o OUTPUT_DIR]
Writes OUTPUT_DIR/<name>.review.md (default: next to each input).
"""
import argparse
import base64
import html
import os
import re
import sys
from html.parser import HTMLParser

BLOCK = {"p", "div", "section", "article", "header", "footer", "main", "aside",
         "figure", "figcaption", "blockquote", "br", "hr", "dt", "dd"}
SKIP = {"script", "style", "noscript", "template", "nav"}
DIAGRAM_HINT = re.compile(r"(diagram|flow|state|sequence|swim|lane|lifeline|chart|graph|machine|fsm|uml)", re.I)
HEADINGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


class Converter(HTMLParser):
    def __init__(self, media_dir, media_prefix):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.buf = []
        self.skip_depth = 0
        self.pre_depth = 0
        self.mermaid = None
        self.svg_depth = 0
        self.svg_labels = []
        self.svg_title = ""
        self.svg_count = 0
        self.svg_text_on = 0
        self.in_svg_title = False
        self.table = None
        self.row = None
        self.cell = None
        self.list_stack = []
        self.heading = None
        self.media_dir = media_dir
        self.media_prefix = media_prefix
        self.img_count = 0
        self.title = ""
        self.in_title = False
        self.region = None
        self.region_count = 0

    # helpers
    def flush(self, prefix=""):
        text = squash("".join(self.buf))
        self.buf = []
        if text:
            self.out.append(prefix + text)

    def emit(self, line=""):
        self.flush()
        self.out.append(line)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if tag == "title" and self.svg_depth == 0:
            self.in_title = True
            return
        if self.skip_depth:
            if tag in SKIP:
                self.skip_depth += 1
            return
        is_mermaid = "mermaid" in cls or (tag == "script" and "mermaid" in (a.get("type") or ""))
        if is_mermaid and self.mermaid is None:
            self.flush()
            self.mermaid = {"tag": tag, "depth": 1, "text": []}
            return
        if self.mermaid is not None:
            if tag == self.mermaid["tag"]:
                self.mermaid["depth"] += 1
            return
        if tag in SKIP:
            self.skip_depth = 1
            return
        if tag == "svg":
            if self.svg_depth == 0:
                self.flush()
                self.svg_count += 1
                self.svg_labels = []
                self.svg_title = a.get("aria-label", "") or ""
            self.svg_depth += 1
            return
        if self.svg_depth:
            if tag in ("text", "tspan"):
                if tag == "text":
                    self.svg_labels.append("")
                self.svg_text_on += 1
            elif tag in ("title", "desc"):
                self.in_svg_title = True
            return
        if self.region is None and tag not in ("svg",) and DIAGRAM_HINT.search((a.get("class") or "") + " " + (a.get("id") or "")):
            self.flush()
            self.region = [tag, 1]
            self.region_count += 1
            self.out += ["", f"[Diagram region {self.region_count} drawn in HTML/CSS ({a.get('class') or a.get('id')}). "
                         "Text below is in source order; arrows are not captured here. Run extract_diagrams.py "
                         "or the browser Console method for its connections, and attach a screenshot.]"]
        elif self.region is not None and tag == self.region[0]:
            self.region[1] += 1
        if tag in HEADINGS:
            self.flush()
            self.heading = HEADINGS[tag]
        elif tag == "summary":
            self.flush()
            self.buf.append("**")
        elif tag == "details":
            self.flush()
            self.out.append("")
        elif tag in ("ul", "ol"):
            self.flush()
            self.list_stack.append([tag, 0])
        elif tag == "li":
            self.flush()
            if self.list_stack:
                self.list_stack[-1][1] += 1
        elif tag == "table":
            self.flush()
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "pre":
            self.flush()
            self.pre_depth += 1
            self.out.append("```")
        elif tag == "img":
            self.handle_img(a)
        elif tag in BLOCK:
            self.flush()

    def handle_endtag(self, tag):
        if tag == "title" and self.in_title:
            self.in_title = False
            return
        if self.skip_depth:
            if tag in SKIP:
                self.skip_depth -= 1
            return
        if self.mermaid is not None:
            if tag == self.mermaid["tag"]:
                self.mermaid["depth"] -= 1
                if self.mermaid["depth"] == 0:
                    src = html.unescape("".join(self.mermaid["text"])).strip("\n")
                    self.out += ["", "```mermaid", src, "```", ""]
                    self.mermaid = None
            return
        if self.svg_depth:
            if tag in ("text", "tspan"):
                self.svg_text_on = max(0, self.svg_text_on - 1)
            elif tag in ("title", "desc"):
                self.in_svg_title = False
            elif tag == "svg":
                self.svg_depth -= 1
                if self.svg_depth == 0:
                    self.emit_svg()
            return
        if self.region is not None and tag == self.region[0]:
            self.region[1] -= 1
            if self.region[1] == 0:
                self.flush()
                self.out += ["[End of diagram region]", ""]
                self.region = None
        if tag in HEADINGS and self.heading:
            self.out.append("")
            self.flush(self.heading + " ")
            self.out.append("")
            self.heading = None
        elif tag == "summary":
            self.buf.append("**")
            self.flush()
        elif tag in ("ul", "ol"):
            self.flush()
            if self.list_stack:
                self.list_stack.pop()
        elif tag == "li":
            depth = max(len(self.list_stack) - 1, 0)
            kind, n = self.list_stack[-1] if self.list_stack else ("ul", 0)
            marker = f"{n}." if kind == "ol" else "-"
            self.flush("  " * depth + marker + " ")
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(squash("".join(self.cell)).replace("|", "\\|"))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.emit_table()
        elif tag == "pre":
            self.out.append("".join(self.buf).rstrip("\n"))
            self.buf = []
            self.out.append("```")
            self.pre_depth = max(0, self.pre_depth - 1)
        elif tag in BLOCK:
            self.flush()

    def handle_data(self, data):
        if self.in_title:
            self.title += data
            return
        if self.skip_depth:
            return
        if self.mermaid is not None:
            self.mermaid["text"].append(data)
            return
        if self.svg_depth:
            if self.svg_text_on and self.svg_labels:
                self.svg_labels[-1] += data
            elif self.in_svg_title and squash(data) and squash(data) not in self.svg_title:
                self.svg_title = (self.svg_title + " " + squash(data)).strip()
            return
        if self.cell is not None:
            self.cell.append(data)
        else:
            self.buf.append(data)

    def handle_img(self, a):
        self.flush()
        alt = a.get("alt", "") or "no alt text"
        src = a.get("src", "") or ""
        m = re.match(r"data:image/([a-zA-Z0-9.+-]+);base64,(.*)", src, re.S)
        if m:
            self.img_count += 1
            ext = {"svg+xml": "svg", "jpeg": "jpg"}.get(m.group(1), m.group(1))
            os.makedirs(self.media_dir, exist_ok=True)
            name = f"image{self.img_count}.{ext}"
            with open(os.path.join(self.media_dir, name), "wb") as fh:
                fh.write(base64.b64decode(m.group(2)))
            self.out.append(f"[Image {self.img_count}: {alt}. Saved as {self.media_prefix}/{name}. Attach it to the review.]")
        else:
            self.out.append(f"[Image: {alt}. Source: {src}. Attach it to the review.]")

    def emit_svg(self):
        labels = [squash(x) for x in self.svg_labels if squash(x)]
        head = f"[Diagram {self.svg_count}, inline SVG"
        head += f": {squash(self.svg_title)}]" if self.svg_title else "]"
        self.out += ["", head, "Labels in document order:"]
        self.out += [f"- {x}" for x in labels] if labels else ["- (no text labels; attach a screenshot of this diagram)"]
        self.out.append("")

    def emit_table(self):
        rows = [r for r in self.table if any(c for c in r)]
        self.table = None
        if not rows:
            return
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        self.out.append("")
        self.out.append("| " + " | ".join(rows[0]) + " |")
        self.out.append("|" + " --- |" * width)
        for r in rows[1:]:
            self.out.append("| " + " | ".join(r) + " |")
        self.out.append("")

    def result(self, source_name):
        self.flush()
        text = "\n".join(self.out)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        header = f"<!-- Converted from {source_name} for security review. Diagrams: {self.svg_count} inline SVG, {self.region_count} HTML/CSS regions, {self.img_count} embedded images. -->\n"
        if self.title.strip():
            header += f"# {squash(self.title)}\n\n"
        return header + text + "\n"


def convert(path, out_dir):
    with open(path, encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    base = os.path.splitext(os.path.basename(path))[0]
    target_dir = out_dir or os.path.dirname(os.path.abspath(path))
    os.makedirs(target_dir, exist_ok=True)
    media_prefix = f"{base}_media"
    conv = Converter(os.path.join(target_dir, media_prefix), media_prefix)
    conv.feed(raw)
    conv.close()
    out_path = os.path.join(target_dir, f"{base}.review.md")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(conv.result(os.path.basename(path)))
    return out_path, conv.svg_count, conv.img_count


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help="HTML files to convert")
    ap.add_argument("-o", "--out", help="output directory (default: next to each input)")
    args = ap.parse_args()
    for f in args.files:
        try:
            out, svgs, imgs = convert(f, args.out)
            print(f"{f} -> {out}  ({svgs} SVG diagrams, {imgs} embedded images)")
        except Exception as exc:  # keep going on other files
            print(f"{f}: failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
