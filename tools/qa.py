#!/usr/bin/env python3
"""Automated QA for the built site.

Checks every page for: horizontal overflow at common widths, console errors,
failed/404 asset requests, broken images, canonical/robots meta, nav
aria-current state, internal links staying under the deployment base path,
mobile menu behavior, form validation, and keyboard-reachable focus.

Usage:
    python3 tools/qa.py [--base URL] [--root PATH] [--expect-noindex]

    --base            server origin (default http://127.0.0.1:8908)
    --root            deployment base path the build used (default '/')
    --expect-noindex  assert every page carries robots noindex (Pages build)

Requires playwright and a running server (tools/serve.py).
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

cli = argparse.ArgumentParser()
cli.add_argument("--base", default="http://127.0.0.1:8908")
cli.add_argument("--root", default="/")
cli.add_argument("--expect-noindex", action="store_true")
args = cli.parse_args()
ORIGIN = args.base.rstrip("/")
ROOTPATH = args.root if args.root != "/" else ""
BASE = ORIGIN + ROOTPATH

PAGES = [
    "/", "/insurance/", "/insurance/auto/", "/insurance/home/",
    "/insurance/business/", "/insurance/life/", "/insurance/health/",
    "/employee-benefits/", "/financial-services/", "/about/", "/team/",
    "/claims-service/", "/resources/", "/contact/", "/redesign/", "/404.html",
]
WIDTHS = [375, 430, 768, 1024, 1440]
PROD = "https://www.thebarthelagency.com"

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        failures.append(f"{name}: {detail}")


def track(page):
    """Attach console/request trackers; return the shared log list."""
    log = {"console": [], "bad": []}
    page.on("console", lambda m: log["console"].append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: log["console"].append(str(e)))
    page.on("requestfailed", lambda r: log["bad"].append(f"{r.url} ({r.failure})"))
    page.on("response", lambda r: log["bad"].append(f"{r.url} -> {r.status}") if r.status >= 400 else None)
    return log


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    log = track(page)

    print("== per-page checks ==")
    for path in PAGES:
        log["console"].clear()
        log["bad"].clear()
        resp = page.goto(BASE + path, wait_until="networkidle")
        check(f"{path} status", resp.status == 200, f"got {resp.status}")

        # broken images
        broken = page.evaluate("""
          [...document.images]
            .filter(i => i.complete && i.naturalWidth === 0)
            .map(i => i.src)
        """)
        check(f"{path} images", not broken, ", ".join(broken))

        # title + meta description
        title = page.title()
        check(f"{path} title", bool(title and title.strip()), "empty")
        desc = page.evaluate("document.querySelector('meta[name=description]')?.content || ''")
        check(f"{path} meta description", len(desc) >= 50, f"len={len(desc)}")

        # canonical: always the production domain, independent of deploy base
        canon = page.evaluate("document.querySelector('link[rel=canonical]')?.href || ''")
        if path == "/404.html":
            check(f"{path} canonical", canon.rstrip("/") == PROD, canon)
        else:
            check(f"{path} canonical", canon.rstrip("/") == (PROD + path).rstrip("/"),
                  f"{canon} vs {PROD + path}")

        # robots meta (page-level or global prototype noindex)
        robots = page.evaluate("document.querySelector('meta[name=robots]')?.content || ''")
        if args.expect_noindex:
            check(f"{path} robots noindex", "noindex" in robots, robots)
        elif path == "/redesign/":
            check("/redesign/ noindex", "noindex" in robots, robots)

        # single h1
        h1s = page.evaluate("document.querySelectorAll('h1').length")
        check(f"{path} single h1", h1s == 1, f"{h1s} h1 elements")

        # nav aria-current
        cur = page.evaluate("document.querySelectorAll('.nav a[aria-current]').length")
        check(f"{path} nav aria-current", cur <= 1, f"{cur} marked")

        # skip link
        has_skip = page.evaluate("!!document.querySelector('.skip-link')")
        check(f"{path} skip link", has_skip)

        # internal URLs stay under the deployment base path
        offsite = page.evaluate("""
          (root) => {
            const urls = [];
            document.querySelectorAll('a[href], img[src], link[href], script[src], iframe[src]')
              .forEach(el => {
                const v = el.getAttribute('href') || el.getAttribute('src');
                if (v && v.startsWith('/') && !v.startsWith('//') && root && !v.startsWith(root + '/')) {
                  urls.push(v);
                }
              });
            return urls;
          }
        """, ROOTPATH)
        check(f"{path} internal urls under base", not offsite, ", ".join(offsite[:4]))

        # console errors / failed or 404 requests
        check(f"{path} console", not log["console"], "; ".join(log["console"][:2]))
        check(f"{path} requests ok", not log["bad"], "; ".join(log["bad"][:3]))

    print("== responsive overflow checks ==")
    for width in WIDTHS:
        pg = browser.new_context(viewport={"width": width, "height": 900}).new_page()
        for path in ["/", "/team/", "/contact/", "/insurance/auto/", "/redesign/"]:
            pg.goto(BASE + path, wait_until="networkidle")
            over = pg.evaluate(
                "document.documentElement.scrollWidth - document.documentElement.clientWidth"
            )
            check(f"{path} @{width} no h-overflow", over <= 0, f"{over}px overflow")
        pg.context.close()

    print("== navigation under base path ==")
    page.goto(BASE + "/", wait_until="networkidle")
    page.click(".nav >> text=Insurance")
    page.wait_for_load_state("networkidle")
    check("desktop nav routes under base",
          page.url == BASE + "/insurance/", page.url)
    page.click(".nav >> text=Financial Services")
    page.wait_for_load_state("networkidle")
    check("desktop nav second click", page.url == BASE + "/financial-services/", page.url)
    check("financial page renders", "Straightforward financial guidance" in page.content())

    print("== mobile menu ==")
    m = browser.new_context(viewport={"width": 390, "height": 800}).new_page()
    m.goto(BASE + "/", wait_until="networkidle")
    toggle = m.locator(".nav-toggle")
    check("toggle visible", toggle.is_visible())
    toggle.click()
    check("menu opens", m.locator("#mobile-nav").is_visible())
    check("aria-expanded", toggle.get_attribute("aria-expanded") == "true")
    m.click(".mobile-nav__links a:has-text('Our Team')")
    m.wait_for_load_state("networkidle")
    check("mobile nav routes under base", m.url == BASE + "/team/", m.url)
    m.goto(BASE + "/", wait_until="networkidle")
    m.locator(".nav-toggle").click()
    m.keyboard.press("Escape")
    check("Escape closes", not m.locator("#mobile-nav").is_visible())
    m.locator(".nav-toggle").click()
    m.locator(".mobile-nav__close").click()
    check("close button closes", not m.locator("#mobile-nav").is_visible())

    print("== contact form validation ==")
    page.goto(BASE + "/contact/", wait_until="networkidle")
    page.click("#contact-form button[type=submit]")
    err = page.locator(".form-field .error").first.inner_text()
    check("empty submit shows error", bool(err.strip()), "no error shown")
    page.fill("#cf-name", "Test User")
    page.fill("#cf-email", "not-an-email")
    page.fill("#cf-message", "Hello from QA")
    page.click("#contact-form button[type=submit]")
    email_err = page.locator(".form-field:has(#cf-email) .error").inner_text()
    check("bad email flagged", "valid email" in email_err, email_err)
    page.fill("#cf-email", "test@example.org")
    page.click("#contact-form button[type=submit]")
    ok = page.locator("#form-success").is_visible()
    check("valid submit shows honest notice", ok)
    note = page.locator(".form-note").inner_text()
    check("form does not claim to send", "does not" in note, note)

    print("== keyboard flow ==")
    page.goto(BASE + "/", wait_until="networkidle")
    page.keyboard.press("Tab")
    focused = page.evaluate("document.activeElement.className")
    check("first tab = skip link", "skip-link" in focused, focused)
    seq = []
    for _ in range(6):
        page.keyboard.press("Tab")
        seq.append(page.evaluate("document.activeElement.textContent.trim().slice(0,20)"))
    check("nav reachable by keyboard", "Insurance" in " ".join(seq), str(seq))

    browser.close()

print()
if failures:
    print(f"{len(failures)} FAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
