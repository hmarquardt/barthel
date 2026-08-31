#!/usr/bin/env python3
"""Static site builder for The Barthel Agency spec redesign.

Zero dependencies. Renders src/pages/**/*.html through shared partials,
injects config/data values, minifies CSS/JS, and emits a clean dist/ tree.
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

CONFIG = json.loads((ROOT / "site.config.json").read_text())
DATA = json.loads((SRC / "data" / "content.json").read_text())

INCLUDE_RE = re.compile(r"\{\{\s*include\s+['\"]([^'\"]+)['\"]\s*\}\}")
VAR_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")
IF_RE = re.compile(r"\{\{#if\s+([a-zA-Z0-9_.! ]+?)\}\}(.*?)\{\{/if\}\}", re.S)
EACH_RE = re.compile(r"\{\{#each\s+([a-zA-Z0-9_.]+)\}\}(.*?)\{\{/each\}\}", re.S)
META_RE = re.compile(r"<!--meta\s*(.*?)-->", re.S)

_page_ctx = {}
_item_stack = []


def _walk(node, parts):
    for p in parts:
        try:
            node = node[int(p)] if isinstance(node, list) else node[p]
        except (KeyError, IndexError, TypeError, ValueError):
            return ""
    return node


def resolve(path):
    """Resolve a dotted path against: current each-item, page ctx, cfg, data."""
    if _item_stack:
        val = _walk(_item_stack[-1], path.split("."))
        if val not in ("", None) or path in _item_stack[-1]:
            return val
    if path.startswith("page."):
        return _page_ctx.get(path[5:], "")
    if path.startswith("cfg."):
        return _walk(CONFIG, path[4:].split("."))
    if path.startswith("d."):
        return _walk(DATA, path[2:].split("."))
    return ""


# alias kept for clarity in non-loop contexts
def lookup(path):
    return resolve(path)


def render_partial(rel_path):
    f = SRC / rel_path
    if not f.exists():
        sys.exit(f"missing partial: {rel_path}")
    return render_text(f.read_text())


def render_text(text):
    def _if(m):
        cond, body = m.group(1).strip(), m.group(2)
        neg = cond.startswith("!")
        val = resolve(cond.lstrip("!").strip())
        truthy = bool(val) and str(val) not in ("False", "None", "")
        return body if (not truthy if neg else truthy) else ""

    def _each(m):
        key, body = m.group(1), m.group(2)
        items = resolve(key)
        if not isinstance(items, list):
            return ""
        out = []
        for item in items:
            _item_stack.append(item)
            try:
                out.append(render_text(body))
            finally:
                _item_stack.pop()
        return "".join(out)

    def _inc(m):
        return render_partial(m.group(1))

    def _var(m):
        val = resolve(m.group(1))
        if isinstance(val, bool):
            return "true" if val else "false"
        return "" if val is None else str(val)

    prev = None
    while prev != text:
        prev = text
        text = EACH_RE.sub(_each, text)
        text = IF_RE.sub(_if, text)
        text = INCLUDE_RE.sub(_inc, text)

    return VAR_RE.sub(_var, text)


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};:,>~])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def minify_js(js):
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    js = re.sub(r"^\s*//.*$", "", js, flags=re.M)
    return re.sub(r"\n\s*", "\n", js).strip()


def sha(s):
    return hashlib.sha1(s.encode()).hexdigest()[:10]


def parse_meta(raw):
    m = META_RE.search(raw)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, raw


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # static assets (skip unused master files; pages reference webp variants)
    SKIP_IMG = {"logo.png", "logo-alpha.png", "logo-white.png"}
    (DIST / "img").mkdir()
    for img in (SRC / "img").iterdir():
        if img.name not in SKIP_IMG:
            shutil.copy(img, DIST / "img" / img.name)
    (DIST / "icons").mkdir()
    for icon in (ROOT / "assets" / "icons").glob("*"):
        shutil.copy(icon, DIST / "icons" / icon.name)
    shutil.copy(ROOT / "robots.txt", DIST / "robots.txt")

    # css / js
    css = minify_css((SRC / "css" / "site.css").read_text())
    js = minify_js((SRC / "js" / "site.js").read_text())
    (DIST / f"site.{sha(css)}.css").write_text(css)
    (DIST / f"site.{sha(js)}.js").write_text(js)
    css_name = f"site.{sha(css)}.css"
    js_name = f"site.{sha(js)}.js"

    pages = sorted(SRC.glob("pages/**/*.html"))
    sitemap_entries = []
    for page in pages:
        rel = page.relative_to(SRC / "pages")
        page_url = str(rel.with_suffix("")).replace("\\", "/")
        if page_url.endswith("/index"):
            page_url = page_url[: -len("/index")]
        elif page_url == "index":
            page_url = ""
        out_path = DIST / rel
        if page_url == "404":
            out_path = DIST / "404.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        raw = page.read_text()
        meta, _ = parse_meta(raw)
        raw = META_RE.sub("", raw, count=1)

        _page_ctx.clear()
        _page_ctx.update(meta)
        _page_ctx["url"] = page_url
        _page_ctx["cssName"] = css_name
        _page_ctx["jsName"] = js_name

        body = render_text(raw)
        _page_ctx["body"] = body

        doc = render_text((SRC / "partials" / "document.html").read_text())
        out_path.write_text(doc)
        out_rel = out_path.relative_to(DIST)
        print(f"  {out_rel}")
        if meta.get("noindex") != "true":
            sitemap_entries.append("/" + page_url if page_url else "/")

    # sitemap.xml
    base = CONFIG["site"]["url"].rstrip("/") + "/"
    urls = []
    for u in sorted(set(sitemap_entries)):
        loc = base + u.lstrip("/")
        if not loc.endswith("/"):
            loc += "/"
        urls.append(
            f"  <url><loc>{loc}</loc><changefreq>monthly</changefreq></url>"
        )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    print("build complete -> dist/")


if __name__ == "__main__":
    build()
