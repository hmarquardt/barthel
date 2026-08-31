# Content Verification

Every customer-facing fact in this prototype was compiled from public
sources in August 2026. Where sources conflict or where only the owner can
confirm, the item is listed here rather than flagged in the public design.

Confidence: **High** = multiple independent sources or direct from current
site; **Medium** = single credible source; **Low** = conflicting sources.

| Item | Current Value (used in prototype) | Source | Confidence | Owner Verification Needed |
| ---- | --------------------------------- | ------ | ---------- | ------------------------- |
| Legal name | The Barthel Agency, Inc. | Current site footer usage; Progressive listing ("The Barthel Agency, Inc. Insurance") | High | Confirm exact registered name & Inc. status |
| Address | 118 S. Main St, Princeton, IN 47670 | Current site; Google Maps embed; Progressive & Travelers directories | High | — |
| Phone | (812) 386-7727 | Current site; carrier directories | High | — |
| Fax | (812) 386-7729 | Current site | High | Confirm fax still in use (not shown in new design) |
| General email | info@thebarthelagency.com | Decoded from Cloudflare-obfuscated mailto on current site | High | — |
| Susan email | Susan@thebarthelagency.com | Current site team page | High | — |
| Jennifer email | Jennifer@thebarthelagency.com | Current site team page | High | — |
| Founded | 1973 | LinkedIn company page | Medium | **Conflicts:** InsuranceProviders.com (2014) says "serving the Tri-State since 1965"; Facebook says "25+ years". Confirm true founding year and any predecessor firm (Waldroup & Waldroup appears in a directory slug) |
| Hours | Mon–Thu 8:00–4:30, Fri 8:00–12:00 | Progressive agent directory | Medium | Confirm current hours; nothing published on the current site |
| Staff | Chris S. Barthel (Financial Advisor); Susan Farmer (Health Insurance Specialist); Jennifer MacKay (P&C Insurance Specialist) | Current site team page | High | Confirm current staff; any additions/departures |
| Chris credentials | CFP®, ChFC® | Current site team page (title); LinkedIn | High | — |
| Jennifer credential | CISR Elite | Current site team page | High | — |
| Chris industry tenure | Since 1995 | SEC AdviserInfo public record (industry date 1995-09-05) | High | — |
| Chris advisory affiliation | Investment adviser representative, LPL Enterprise, LLC (Princeton branch) | SEC AdviserInfo public record | High | Confirm current status + **exact required disclosure wording with LPL compliance** (prototype uses standard-form wording) |
| Chris birth month (used in Person schema) | 1967-09 | SEC AdviserInfo public record | Medium | Confirm before production; can be removed from schema |
| Chris email | Not published | — | — | Provide a public direct email or confirm none should be listed |
| Service categories | Auto, Home, Business, Life, Health/Medicare, Employee Benefits, Financial/Investments | Current site subtitle; LinkedIn description ("AUTO HOME LIFE HEALTH BUSINESS INVESTMENTS"); Facebook | High | — |
| Carrier relationships | Independent agency, multiple carriers; Progressive & Travelers confirmed | Current site ("relationship with a variety of insurance companies"); Progressive & Travelers agent directories | High (Progressive/Travelers), rest general | Full carrier list for potential logo strip |
| Quote integrations | Emerald Connect forms (auto #13, home #101, motorcycle/UTV #16, camper #17, boat #18), CoverWallet (business), HealthSherpa (health) | Current site nav & quote center | High | Confirm accounts remain active; confirm CoverWallet/HealthSherpa agent IDs |
| Service-request forms | Emerald Secure forms #8, 9, 10, 11, 12, 103 | Current site client forms | High | Confirm continued use |
| Social profiles | facebook.com/BarthelAgency; linkedin.com/company/the-barthel-agency; twitter/x.com/BarthelAgency | Current site footer | High | Confirm X account still maintained (header/footer include it) |
| Service area | Princeton, Gibson County, greater Tri-State | Facebook description; current site location page | Medium | Confirm preferred service-area description |
| Office location description | "Half a block south of the square on Main Street" | Current site location page | High | — |
| Analytics | GTM-P7LM8CD on current site | Current site source | High | Decide analytics for production (tag not carried into prototype) |
| Team bios (new) | Written by the redesign from public role info only | This project | Medium | **Owner should review/replace bios and approve phrasing** |
| Team photos | Chris 2015 headshot; Susan 2022; Jennifer (polo, selfie-style) | Current site team page | High | Higher-resolution replacements requested; Jennifer's is a casual selfie |
| Stat "3 licensed specialists" | Derived from staff list | Derived | Medium | Update with any staffing change |
| Stat "7+ lines of coverage" | Count of service categories | Derived | Medium | — |

## Items deliberately omitted (insufficient public data)

- Any founding narrative details (founder names, prior firm history) — the
  1965/1973 conflict makes any story unsafe until the owner confirms.
- Carrier logo strip — only Progressive/Travelers are publicly confirmed;
  a fuller list from the owner would justify one.
- Testimonials/reviews — none were fabricated (per project ground rules).
- Specific policy underwriting claims of any kind.
