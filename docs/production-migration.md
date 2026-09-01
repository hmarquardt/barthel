# Production Migration Notes

Checklist for taking this prototype from demo to the agency's real website.
Written against the current site's known behavior (August 2026).

## 1. HTTPS / TLS

The current site serves over plain HTTP on `www.thebarthelagency.com`.
Modern browsers that auto-upgrade the request get
`ERR_SSL_VERSION_OR_CIPHER_MISMATCH` — a certificate/handshake problem, not
a redirect problem — meaning some visitors see an error page instead of the
site.

Requirements:

- [ ] Valid certificate covering **all** hostnames served:
      `www.thebarthelagency.com`, `thebarthelagency.com` (and any legacy
      bare-domain aliases that still resolve).
- [ ] TLS 1.2+ only; modern cipher suites (the current host fails the
      handshake entirely — likely an old/absent cert, not just a version
      gap).
- [ ] **HTTP → HTTPS 301 redirects** on every hostname (not meta-refresh,
      not JS).
- [ ] **Canonical host:** choose `https://www.thebarthelagency.com/`;
      301 `thebarthelagency.com` → `www` (or vice versa — but pick one and
      match canonical tags, currently set to `www`).
- [ ] **HSTS** header once redirects are stable:
      `Strict-Transport-Security: max-age=31536000; includeSubDomains`
      (start with a short `max-age` during rollout, raise after verification).
- [ ] No mixed content (the new site is fully self-hosted except the Google
      Maps iframe and outbound quote links — both HTTPS).

## 2. Redirects (legacy URL map)

| Legacy URL (old site) | New URL | Notes |
| --------------------- | ------- | ----- |
| `/` | `/` | Homepage replacement |
| `/team.htm` | `/team/` | Old "Our Associates" |
| `/Chris-S--Barthel,-CFP,-ChFC.e544777.htm` | `/team/#chris-barthel` | Profile pages fold into team cards |
| `/Susan-Farmer.e544775.htm` | `/team/#susan-farmer` | |
| `/Jennifer-MacKay-CISR-Elite.e544776.htm` | `/team/#jennifer-mackay` | |
| `/contact_us/`, `/contact_us.cfm` | `/contact/` | |
| `/location.htm` | `/contact/` | Old "Our Location" |
| `/Our-Firm.2.htm` | `/about/` | |
| `/Our-Mission-Statement.1.htm` | `/about/` | |
| `/Our-Qualifications.4.htm` | `/about/` | |
| `/request_quote.htm`, `/request_quote.cfm` | `/contact/#quote` | Quote center |
| `/Quote-Forms.5.htm` | `/contact/#quote` | |
| `/client_forms.cfm` | `/claims-service/` | Service-request forms |
| `/learning_center/articles/`, `/research.cfm` | `/resources/` | Syndicated library retired |
| `/learning_center/calculators/`, `/calculators.cfm` | `/resources/#calculators` | |
| `/learning_center/faqs/`, `/faqs.cfm` | `/resources/` | |
| `/learning_center/glossary/`, `/glossary.cfm` | `/resources/` | |
| `/learning_center/tax_library/` | `/resources/` | |
| Individual article URLs (`*.cNNN.htm`) | `/resources/` | ~40 syndicated articles; 301 to Resources, not one-to-one |
| `/sitemap.htm` | `/sitemap.xml` | |
| `/tellafriend.cfm` | drop (410 or to `/`) | Legacy Broadridge feature |

Notes:

- Static-host implementation: a `sitemap.xml`-adjacent `_redirects` file
  (Netlify/Cloudflare Pages) or server config (nginx `map`, Apache
  `RewriteMap`) generated from the table above.
- Keep redirects in place **indefinitely** (they carry whatever local search
  equity the old pages earned).
- The Broadridge `learning_center` deep-links that appear in Google should
  consolidate to `/resources/`; expect temporary ranking churn.

## 3. DNS

- [ ] Confirm A/AAAA (or CNAME) records for the chosen static host.
- [ ] Lower TTL to 300s a day before cutover.
- [ ] Keep the old host reachable until redirects are verified on the new
      host.
- [ ] Verify `thebarthelagency.com` (bare) actually resolves today; if it
      doesn't, register/point it and 301 to `www`.

## 4. Forms

- [ ] **Contact form needs a real backend.** The prototype validates
      client-side and explicitly does not transmit. Options: Netlify Forms,
      Cloudflare Pages Functions, Formspree/Basin, or a small serverless
      function emailing `info@thebarthelagency.com`. Add spam protection
      (honeypot minimum; reCAPTCHA/Turnstile if needed — the old site used
      reCAPTCHA).
- [ ] Quote/service forms: keep the existing Emerald Connect/Emerald Secure,
      CoverWallet, and HealthSherpa links until/unless the owner wants them
      replaced. They are data (`src/data/content.json`), not markup.
- [ ] Add success/error states + notification email routing.

## 5. Analytics

- [ ] The current site runs GTM (`GTM-P7LM8CD`). Decide: carry the existing
      GA/GTM container into the new site (one snippet in the head), or start
      clean with GA4 or a privacy-friendly option.
- [ ] Configure conversion events: quote-link clicks, phone-number taps,
      contact-form submits.
- [ ] Register the new sitemap in Google Search Console and Bing Webmaster
      Tools; monitor legacy-URL 404s after cutover.

## 6. Compliance

- [ ] **LPL Enterprise disclosure wording** must be confirmed with LPL
      compliance before production (footer + financial-services page + team
      page currently use standard-form wording derived from public records).
- [ ] Confirm which states Chris is registered/licensed in if the compliance
      language requires a state list ("may only discuss/transact business
      with residents of the following states…").
- [ ] Privacy policy page: not present in the prototype. Required if forms
      collect PII and recommended for analytics. Draft and add at
      `/privacy/` before launch.
- [ ] Accessibility: prototype targets WCAG 2.1 AA practices (semantic
      markup, labels, contrast, keyboard support, reduced-motion); a formal
      audit pass is recommended post-launch.

## 7. Content handoff

- [ ] Owner reviews `docs/content-verification.md` and confirms/corrects
      each row (founding year, hours, bios, staff, LPL wording).
- [ ] Higher-resolution team photos + any additional office photography.
- [ ] Decide whether any legacy Learning Center articles should be
      rewritten as owned Resources content (recommended: 3–5 evergreen
      pieces instead of 40 syndicated ones).

## 8. Technical cutover checklist

- [ ] `build.py` output (`dist/`) deployed to the chosen host.
      - GitHub Pages: the committed workflow (`.github/workflows/
        deploy-pages.yml`) builds with `--base /barthel --noindex` for the
        project-URL prototype. For a production deploy on the agency's own
        domain (custom domain or user site), build with **no flags** —
        base `/`, indexable, canonical URLs unchanged — and switch the
        Pages source to "GitHub Actions" (`gh api -X PUT repos/…/pages -f
        build_type=workflow`) if it is still set to "deploy from branch".
- [ ] Security headers (host config or `_headers` file):
      - `Strict-Transport-Security` (after redirect verification)
      - `X-Content-Type-Options: nosniff`
      - `Referrer-Policy: strict-origin-when-cross-origin`
      - `X-Frame-Options: SAMEORIGIN` (or frame-ancestors in CSP)
      - `Content-Security-Policy`: start report-only, e.g.
        `default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-src https://maps.google.com https://www.google.com; form-action 'self' https://admin.emeraldconnect.com https://www.emeraldsecure.com https://app.coverwallet.com https://www.healthsherpa.com`
- [ ] Caching: long-lived immutable for fingerprinted `site.*.css/js` and
      images; short TTL for HTML.
- [ ] Verify: all legacy URLs 301 correctly; canonical host enforced;
      CSP report clean; forms deliver; Lighthouse pass on mobile.
