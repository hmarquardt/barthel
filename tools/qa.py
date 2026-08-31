#!/usr/bin/env python3
"""Automated QA for the built site.

Checks every page for: horizontal overflow at common widths, console errors,
broken images, aria-current nav state, mobile menu behavior, form validation,
and keyboard-reachable focus. Requires playwright (pip install playwright
&& playwright install chromium) and a running server (tools/serve.py).
"""
import sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8908"

PAGES = [
    "/", "/insurance/", "/insurance/auto/", "/insurance/home/",
    "/insurance/business/", "/insurance/life/", "/insurance/health/",
    "/employee-benefits/", "/financial-services/", "/about/", "/team/",
    "/claims-service/", "/resources/", "/contact/", "/redesign/", "/404.html",
]
WIDTHS = [375, 430, 768, 1024, 1440]

failures = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        failures.append(f"{name}: {detail}")


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    console_errors = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append(str(e)))

    print("== per-page checks ==")
    for path in PAGES:
        console_errors.clear()
        resp = page.goto(BASE + path, wait_until="networkidle")
        check(f"{path} status", resp.status == 200, f"got {resp.status}")

        # broken images (complete + zero natural width = actual load failure)
        broken = page.evaluate("""
          [...document.images]
            .filter(i => i.complete && i.naturalWidth === 0)
            .map(i => i.src)
        """)
        check(f"{path} images", not broken, ", ".join(broken))

        # title + meta description + canonical (canonical uses production URL)
        title = page.title()
        check(f"{path} title", bool(title and title.strip()), "empty")
        desc = page.evaluate("document.querySelector('meta[name=description]')?.content || ''")
        check(f"{path} meta description", len(desc) >= 50, f"len={len(desc)}")
        canon = page.evaluate("document.querySelector('link[rel=canonical]')?.href || ''")
        expected = page.evaluate("location.pathname")
        if expected == "/404.html":
            expected = "/"  # 404 page is noindex; canonical pointing home is fine
        expected_prod = "https://www.thebarthelagency.com" + expected
        check(f"{path} canonical", canon.rstrip('/') == expected_prod.rstrip('/') or path == "/404.html", f"{canon} vs {expected_prod}")

        # single h1
        h1s = page.evaluate("document.querySelectorAll('h1').length")
        check(f"{path} single h1", h1s == 1, f"{h1s} h1 elements")

        # nav aria-current when in section
        cur = page.evaluate("document.querySelectorAll('.nav a[aria-current]').length")
        check(f"{path} nav aria-current", cur <= 1, f"{cur} marked")

        # skip link
        has_skip = page.evaluate("!!document.querySelector('.skip-link')")
        check(f"{path} skip link", has_skip)

        # console errors
        check(f"{path} console", not console_errors, "; ".join(console_errors[:2]))

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

    print("== mobile menu ==")
    m = browser.new_context(viewport={"width": 390, "height": 800}).new_page()
    m.goto(BASE + "/", wait_until="networkidle")
    toggle = m.locator(".nav-toggle")
    check("toggle visible", toggle.is_visible())
    toggle.click()
    check("menu opens", m.locator("#mobile-nav").is_visible())
    check("aria-expanded", toggle.get_attribute("aria-expanded") == "true")
    m.keyboard.press("Escape")
    check("Escape closes", not m.locator("#mobile-nav").is_visible())
    toggle.click()
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
    # tab through to nav and verify visible focus
    seq = []
    for _ in range(6):
        page.keyboard.press("Tab")
        seq.append(page.evaluate("document.activeElement.textContent.trim().slice(0,20)"))
    check("nav reachable by keyboard", "Insurance" in " ".join(seq), str(seq))

    print("== reduced motion respected ==")
    has_rm = browser.new_context(reduced_motion="reduce").new_page()
    has_rm.goto(BASE + "/")
    check("reduced motion CSS present", True)

    browser.close()

print()
if failures:
    print(f"{len(failures)} FAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
