# Am I Cooked — Implementation Plan

**Last updated:** 2026-04-03

## Progress

| Step | Status | Output |
|---|---|---|
| 1. Desktop results mockup | Done | `mockups/results-desktop-v1.html` |
| 2. Design spec | Done | `docs/design-spec.md` |
| 3. Validator tool | Done | `tools/validate_jobs.py` + `workflows/validate-job-data.md` |
| 4. Sample dataset (10 jobs) | Done | `data/jobs-sample.json` — passed rule-based validation |
| 5. Full dataset (~200 jobs) | Done | `data/jobs.json` — 219 jobs, all pass rule-based validation, searchTerms added |
| 6. Fact-check dataset | Done | 15 Perplexity category queries, 12 jobs corrected, all 219 pass validation |
| 7. Build the site | Done | `index.html` — all features wired up, tested on desktop + mobile |
| 8. Growth setup | **Next** | Affiliate signup, OG tags, watermark — see `docs/growth-strategy.md` |
| 9. Launch | Pending | Reddit + Hacker News — see `docs/growth-strategy.md` section 4 |

## Step 5: Build Full Dataset (~200 jobs)

- Compile from AI automation research (Oxford/Frey & Osborne, McKinsey, Goldman Sachs, WEF)
- Each entry follows schema in `docs/design-spec.md` section 7
- Verdict scale: Raw → Rare → Lightly Toasted → Half Baked → Well Done → Extra Crispy → Fully Cooked
- Each verdict gets a one-liner (`verdictQuip`)
- Quips must punch at the tech/situation, never the worker (enforced by validator)
- Run `python tools/validate_jobs.py check data/jobs.json` after generating

## Step 6: Fact-Check Dataset

- Follow `workflows/validate-job-data.md`
- 3-pass loop: rule checks → Perplexity fact-checks → fix or flag
- After 3 fails → human review queue
- Output: validated `data/jobs.json` + `data/jobs-human-review.json` (if any)

## Step 7: Build the Site

- Single HTML file (static, hostable anywhere)
- Wire up landing page → results page flow
- Load job data from JSON
- Fuzzy search / autocomplete for job input
- html-to-image for downloadable PNG — **must include "amicooked.me" watermark** (growth feature)
- Share button: copy `amicooked.me/?job=job-id` to clipboard + Web Share API on mobile
- `?job=` URL parameter: read on page load, show result directly if valid (enables shareable links + SEO)
- Open Graph / Twitter Card meta tags (title, description, preview image)
- Frictionless "try another" loop — no page reload, clear result and focus input (each extra check = another screenshot)
- Coursera affiliate link below action buttons (small muted text, placeholder href until signup)
- Disclaimer: `*for entertainment — not career advice`
- Full growth feature specs in `docs/growth-strategy.md` section 2

## Step 8: Growth Setup (before launch)

- Sign up for Coursera affiliate program via Impact.com (see `docs/growth-strategy.md` for steps)
- Replace placeholder affiliate href with real tracking link
- Create Hacker News account at news.ycombinator.com
- Point domain amicooked.me to hosting
- Test OG tags with Twitter Card Validator

## Step 9: Launch

- Full launch plan with exact post copy in `docs/growth-strategy.md` section 4
- Reddit: r/SideProject → r/cscareerquestions → optionally r/technology (stagger by 3-4 hrs)
- Hacker News: Show HN post
- Reply to comments for first couple of hours, then walk away

## Verification

- Validate JSON dataset loads and covers common job titles
- Test the full flow: type job → see results → download PNG
- Test on mobile and desktop
- Screenshot test: does the results card look good as a PNG?
- Watermark visible on downloaded PNG
- `?job=marketing-manager` URL loads result directly
- OG preview looks correct when URL is pasted into Twitter Card Validator
- Affiliate link visible but subtle on results page
