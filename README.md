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
| `.github/workflows/deploy-pages.yml` | GitHub Pages deployment workflow |
| `assets/original/` | Original downloaded public assets (provenance) |
| `assets/icons/` | Generated favicon set |
| `dist/` | Generated site — the deployable artifact (gitignored, built on deploy) |
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

For a build made with `--base /barthel --noindex`, verify it like this
(serve the build under a matching path prefix, then point the suite at it):

```bash
python3 build.py --base /barthel --noindex
mkdir -p /tmp/qa_root && ln -sfn "$PWD/dist" /tmp/qa_root/barthel
python3 -m http.server 8909 --directory /tmp/qa_root &
python3 tools/qa.py --base http://127.0.0.1:8909 --root /barthel --expect-noindex
```

## Deployment & base-path behavior

All internal URLs in the source are root-absolute (`/insurance/`,
`/img/...`). The build rewrites them in one central place — `build.py`'s
`--base` option — so templates never hardcode a deployment prefix:

| Target | Command | Result |
| ------ | ------- | ------ |
| Production / custom domain (default) | `python3 build.py` | URLs stay `/...`; canonical + sitemap use `site.url` from `site.config.json`; site is indexable |
| GitHub project Pages | `python3 build.py --base /barthel --noindex` | Every internal URL becomes `/barthel/...`; every page gets `<meta name="robots" content="noindex, nofollow">`; `robots.txt` becomes `Disallow: /` |
| Any other subpath | `python3 build.py --base /somepath` | Same prefixing, indexing unchanged |

Rules the rewrite follows (enforced by the QA suite):

- Only internal root-absolute `href`/`src`/`content`/`action` attributes are
  prefixed. External URLs (`https://…`), protocol-relative (`//…`),
  mailto/tel links, and fragment anchors (`#quote`) are untouched.
- Canonical URLs, Open Graph URLs, JSON-LD, and `sitemap.xml` always use the
  canonical production URL from `site.config.json` (or `--site-url`) —
  independent of `--base`. The production-domain strategy never changes.
- `--noindex` (or `NOINDEX=1`) additionally empties the sitemap and emits
  `Disallow: /` robots.txt — intended for private prototype deploys. The
  `/redesign/` page is page-level noindexed in every build regardless.
- A `.nojekyll` file is emitted so GitHub Pages serves paths verbatim.
- There is no JavaScript involved in navigation — the site is plain links,
  so base-path routing cannot drift out of sync with the build.

### GitHub Pages

`.github/workflows/deploy-pages.yml` deploys on every push to `main`
(and manual dispatch): checkout → `python3 build.py --base /barthel
--noindex` → upload `dist/` as the Pages artifact → official
`actions/deploy-pages`. No `dist/` is ever committed; the build needs
nothing beyond the Python stdlib.

- Intended live URL: `https://hmarquardt.github.io/barthel/`
- The prototype is intentionally noindexed there (private-ish sales
  collateral). To index it anyway, drop `--noindex` from the workflow.

> **One-time setting required:** the repository's Pages source is currently
> *"deploy from branch"* (a leftover from the initial README test), so a
> legacy Jekyll build re-publishes the README over the workflow's artifact
> after every push. To hand Pages to the workflow, switch the source once —
> either **Settings → Pages → Build and deployment → Source: "GitHub
> Actions"**, or:
>
> ```bash
> gh api -X PUT repos/hmarquardt/barthel/pages -f build_type=workflow
> ```
>
> Then re-run the workflow (Actions → "Deploy to GitHub Pages" → Run
> workflow, or just push). The workflow itself needs no changes.

### Production / custom domain

Build with no flags (`python3 build.py`) and upload `dist/` to any static
host serving the agency's domain (Netlify, Cloudflare Pages, S3+, Apache/
nginx). HTTPS, redirects (including every legacy URL), HSTS, and security
headers are covered in `docs/production-migration.md`. If deploying under a
subpath on some other host, pass it via `--base` — no template changes.

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
