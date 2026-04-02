# Am I Cooked? — Brainstorming Progress

**Last updated:** 2026-03-26

---

## Concept

**"Am I Cooked?"** — an AI Job Risk Calculator at **amicooked.com**. Users enter their job title and get a "cooked score" showing how likely AI is to replace them. Designed to be fun, shareable, and go viral on Reddit (r/cscareerquestions, r/technology, r/jobs) and social media.

---

## Design Decisions (Locked In)

### Visual Style
- **Brutalist web design** — thick borders, black/white, bold typography, opinionated layout
- Anti-AI aesthetic (asymmetry, personality in copy, texture, cultural references)
- Screenshot-optimized for mobile sharing + downloadable PNG

### Fonts
- **Barlow Black** (900) — display headings ("AM I COOKED?", "CHECK", verdict)
- **Space Mono** — body text, labels, monospace elements
- **Instrument Serif italic** — score number only (the big "34")

### Colors
- Background: cream `#f8f6f1`
- Text: black `#000`
- Muted text: `#999` (job label, numbers 01-04)
- List text: `#444`
- Quip text: `#aaa` at 7px
- Red accents: `#ff0000` (live dot), `#cc0000` (crosses)
- Dark background page: `#0a0a0a`

### Data Approach
- **Curated JSON dataset** (~200 jobs with pre-researched risk scores)
- Static site (single HTML file, hostable anywhere)
- Potential future AI fallback for jobs not in dataset

### Sharing
- Both screenshot-optimized design AND downloadable PNG (using html-to-image library)

---

## Landing Page (Done)

Mockups completed and approved:
- Desktop: `landing-barlow-final.html`
- Mobile: `landing-mobile-v2.html` (tagline letter-spacing still slightly off but moved on)

Key elements:
- "AM I COOKED?" in Barlow Black, large
- Tagline: "find out if AI is coming for your job." in Space Mono
- Input field + CHECK button
- Red live dot indicator
- Footer: AMICOOKED.COM / ABOUT

---

## Results Page — Mobile (In Progress)

**Latest mockup:** `results-mobile-v14.html`

### Layout (top to bottom)
1. **Phone frame** — 260px wide, rounded corners, cream background
2. **Header bar** — black, "AM I COOKED?" left, red dot right
3. **Score** — `34` in Instrument Serif 60px italic + `/100` in 22px with hair spaces (`&#8202;`), color `#999`
4. **Verdict** — "Lightly Toasted" in Barlow 900 24px uppercase
5. **Job label** — "JOB: Marketing Manager" in Space Mono 9px, color `#999`
6. **Three stat boxes** (flex row, 2px black borders):
   - `~5 YEARS` / TILL ROBOTS TAKE OVER
   - `62%` / AUTOMATABLE
   - `HIGH` / PIVOT POTENTIAL
7. **Your Saving Graces** — numbered list (01-04) with selective quips
8. **What's Getting Cooked First** — red cross list (✕) with selective quips
9. **Download / Share buttons** — SVG icons (download tray, chain link)
10. **Footer bar** — black, AMICOOKED.COM / TRY ANOTHER

### Typography Details for Stat Boxes
- `~5` at 18px, `YEARS` at 13px with `letter-spacing: -0.3px`, `scaleY(1.15)`, `margin-left: 4px`
- `62%` and `HIGH` at 18px
- Sub-labels in Space Mono 6px, color `#888`

### List Styling
- Flexbox rows with 22px marker columns for alignment
- Numbers (`01.` etc) in `#999`
- Red crosses (`✕`) in `#cc0000`, 9px, bold (700)
- Quips only on select items, in `#aaa` 7px with `word-spacing: -1px`
- Main list text in Space Mono 8px, `#444`, `word-spacing: -2px`

### Still To Do on Mobile Results
- [ ] Confirm ~5 YEARS spacing looks right (v14 added margin-left: 4px)
- [ ] Red crosses mid-aligned with 01 02 03 04 numbers (not counting full stops)
- [ ] Cross size slightly increased

---

## Results Page — Desktop (Not Started)

Needs to be created to match all mobile design decisions.

---

## All Mockup Files

Located in: `.superpowers/brainstorm/19370-1774446994/`

| File | What it is |
|---|---|
| `ideas.html`, `ideas-v2.html` | Initial concept explorations |
| `concepts-detail.html` | Detailed concept breakdowns |
| `anti-ai-styles.html` | Anti-AI design approaches |
| `more-concepts.html`, `visual-styles.html` | Additional visual explorations |
| `font-options.html` | Font comparison sheet |
| `syne-spacing.html`, `tall-fonts.html`, `sharp-fonts.html` | Font iteration |
| `landing-mockup.html` through `landing-barlow-final.html` | Landing page iterations |
| `landing-mobile.html`, `landing-mobile-v2.html` | Mobile landing |
| `mobile-tagline-fix.html`, `tagline-letterspace.html` | Tagline fixes |
| `results-page.html`, `results-v2.html` | Early results concepts |
| `results-mobile-v3.html` through `results-mobile-v14.html` | Mobile results iterations |

---

## Remaining Brainstorming Steps

1. Finalize mobile results page (the ~5 YEARS spacing, cross alignment)
2. Create desktop results mockup
3. Write full design spec document → `docs/superpowers/specs/`
4. Run spec review loop
5. User reviews spec
6. Transition to implementation planning (writing-plans skill)

---

## Key Learnings from Iteration

- User strongly dislikes AI-looking design (gradient, symmetric, generic fonts)
- Round fonts don't pair well with angular Space Mono
- Syne looks "squashed" — Barlow Black solved this
- Less is more with humor — selective quips, not on every item
- Apple emojis are banned — use SVG icons
- Monospace spacing needs negative word-spacing to look right at small sizes
- Results page must stay compact on mobile — no separate lines for quips
