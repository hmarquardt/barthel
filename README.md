# The Barthel Agency — Website Refresh Concept

A speculative redesign of the public website for **The Barthel Agency**
(Princeton, Indiana), built as a sales prototype: it demonstrates what the
agency's online presence could become, using only the agency's real public
information, imagery, and history.

> This is not the agency's current website and is not published on their
> behalf. It is a design prototype for discussion.

---

## What's in the box

| Path | Purpose |
| ---- | ------- |
| `src/` | Site source: pages, partials, CSS, JS, images, data |
| `build.py` | Zero-dependency static site generator (Python 3 stdlib only) |
| `tools/process_assets.py` | Regenerates optimized images from `assets/original/` (requires Pillow) |
| `tools/serve.py` | Serves `dist/` locally for preview |
| `tools/qa.py` | Playwright QA suite (overflow, SEO tags, console, menu, form, keyboard) |
| `assets/original/` | Original downloaded public assets (provenance) |
| `assets/icons/` | Generated favicon set |
| `dist/` | Generated site — the deployable artifact |
| `docs/` | Content verification + production migration notes |

## Architecture

Deliberately boring, on purpose:

- **Static HTML output.** Every page is pre-rendered HTML + one CSS file +
  one small JS file. No SPA, no runtime APIs, no CDN dependencies.
- **Micro-SSG (`build.py`).** Pages live in `src/pages/**/*.html` with a
  small `<!--meta ... -->` front-matter block (title, description, nav
  section, noindex). Shared chrome lives in `src/partials/`. A tiny template
  engine provides includes, `{{#if}}`, `{{#each}}`, and variable injection
  from `site.config.json` (business facts) and `src/data/content.json`
  (team, quote links, service forms).
- **Design system** in `src/css/site.css`: navy/gold palette sampled from the
  agency's existing logo, Georgia serif display type, system sans body,
  consistent card/grid/spacing primitives.
- **No runtime JavaScript framework.** `site.js` is ~2 KB: mobile menu,
  client-side form validation (honest: validates but does not transmit), and
  a character counter.
- **Fingerprinted assets.** CSS/JS filenames include a content hash;
  images are pre-optimized (WebP/JPEG) by `tools/process_assets.py`.

### Adding or editing a page

1. Create `src/pages/<path>/index.html` with a `<!--meta ... -->` block.
2. Use partials (`{{ include 'partials/header.html' }}` is pulled in by the
   document shell automatically).
3. Run `python3 build.py`.

Business facts (phone, address, hours, social) live in `site.config.json`;
team bios and quote/service-form links live in `src/data/content.json`.
Those two files are the intended future CMS surface.

## Local development

```bash
python3 build.py            # regenerate dist/
python3 tools/serve.py      # http://127.0.0.1:8908  (Ctrl-C to stop)
```

Regenerate image assets (only needed after changing originals):

```bash
python3 tools/process_assets.py   # requires Pillow
```

Run the QA suite (requires `pip install playwright && playwright install chromium`):

```bash
python3 tools/serve.py &     # in one shell
python3 tools/qa.py          # in another
```

## Deployment

`dist/` is plain static files — deployable to any static host (Netlify,
Cloudflare Pages, GitHub Pages, S3+, or an Apache/nginx vhost).

- Serve over **HTTPS only**; see `docs/production-migration.md` for the
  certificate/host/redirect/HSTS checklist.
- Legacy URLs (`team.htm`, `contact_us/`, etc.) should receive 301
  redirects — a complete map is in `docs/production-migration.md`.
- A Netlify-style `_redirects` file can be generated from that table; none
  is committed because the production host is not yet chosen.

## Asset sources

All imagery is sourced from the agency's own public web presence (current
site and public listings) and stored locally in `assets/original/`:

| Asset | Source |
| ----- | ------ |
| `logo.jpg` | Current site masthead (`/files/72258/Barthel Agency Combo Logo.jpg`) |
| `building.jpg` | Current site (`/files/72258/Building Photo Lage~001.jpg`) |
| `chris.jpg`, `susan.jpg`, `jennifer.jpg` | Current site team page |
| Before-screenshots (`old-*.png`) | Captured from the live current site for the `/redesign/` concept page |
| Favicon set, OG image | Generated from the logo/brand palette by `tools/process_assets.py` |

No third-party or stock photography is used anywhere. Team photos are low
resolution (the originals are ~300px); replacement originals should be
requested from the agency.

## Public sources used for factual content

- **Current site** (`www.thebarthelagency.com`): address, phone, fax, email
  addresses, staff names/titles/credentials, service categories, quote and
  service-form integrations, social links.
- **LinkedIn company page** (`linkedin.com/company/the-barthel-agency`):
  founded 1973, industry, headquarters.
- **Progressive agent directory**: office hours (M–Th 8:00–4:30, F 8:00–12:00).
- **Travelers agent directory**: carrier relationship, product list.
- **FINRA BrokerCheck / SEC AdviserInfo public records**: Chris Barthel
  active since 1995; investment adviser representative of LPL Enterprise, LLC
  (Princeton, IN branch).
- **Wikipedia**: TMMI/Gibson County context (used lightly, on the homepage).

## Known assumptions & verification needed

Anything uncertain is kept out of the customer-facing pages and tracked in
**`docs/content-verification.md`** — the short version:

- Founding year 1973 comes from LinkedIn; an older directory listing says
  "since 1965" and Facebook says "25+ years". Owner should confirm.
- Office hours come from a third-party (Progressive) directory listing.
- The exact LPL disclosure language must be confirmed with LPL compliance.
- Team bios were written from public role information only; the owner should
  replace/approve them.
- No public photo of Chris exists beyond a 2015 headshot; newer photos
  should be supplied.

## Integrations status

- **Retained (live links):** Emerald Connect quote forms (auto, home,
  motorcycle/UTV, camper/RV, boat), Emerald Secure service-request forms
  (policy change, ID card, loss notices, renewal reminder, homeowners
  service), CoverWallet (business), HealthSherpa (health).
- **Represented, not implemented:** contact form (validates client-side,
  does not transmit — labeled honestly on the page), Google Maps embed
  (standard iframe, unchanged).
- **Intentionally deferred:** form backend, analytics (legacy GTM tag not
  carried over), appointment scheduling, live chat.

The architecture intentionally does not couple to Broadridge AdvisorSites
(the current platform): resources/calculators are represented as a light
Resources page, and quote links are data, not markup — they can be swapped
or dropped in `src/data/content.json`.

## Legacy URL preservation

The old site's URLs should 301 to the new structure. Full mapping in
`docs/production-migration.md`; highlights:

| Old | New |
| --- | --- |
| `/` (homepage) | `/` |
| `team.htm` | `/team/` |
| `contact_us/`, `location.htm` | `/contact/` |
| `Our-Firm.2.htm`, `Our-Mission-Statement.1.htm`, `Our-Qualifications.4.htm` | `/about/` |
| `request_quote.htm`, `Quote-Forms.5.htm` | `/contact/#quote` |
| `client_forms.cfm` | `/claims-service/` |
| `learning_center/*` | `/resources/` |
| Chris/Susan/Jennifer profile pages | `/team/` (anchor per person) |

## License / rights

Site content and imagery belong to The Barthel Agency, Inc. This prototype
was prepared for presentation to the agency and should not be published or
reused elsewhere.
