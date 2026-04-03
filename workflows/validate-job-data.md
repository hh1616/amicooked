# Workflow: Validate Job Data

**Objective:** Ensure every job entry in the dataset is factually defensible, tonally appropriate, and internally consistent before it goes live.

**Trigger:** Run after generating or updating `data/jobs.json` (or any jobs JSON file).

---

## Overview

3-pass validation loop. Each pass:
1. Run rule-based checks (script handles this automatically)
2. Fact-check key claims using Perplexity MCP (agent does this)
3. Fix or flag issues
4. After 3 failed passes → drop to human review queue

---

## Step 1: Run Rule-Based Checks

```bash
python tools/validate_jobs.py check data/jobs-sample.json
```

This creates `data/jobs-sample-validation-state.json` and prints a report showing:
- **Structural issues** — missing fields, invalid ranges, bad enums
- **Consistency issues** — score vs automation %, score vs timeline mismatches
- **Controversial content** — flagged keywords in text or quips
- **Pending fact-checks** — claims that need web verification

---

## Step 2: Fact-Check with Perplexity

For each pending fact-check, use Perplexity MCP (`mcp__perplexity__perplexity_ask`) to verify:

### What to check:
1. **Score & automation %** — "What percentage of [job title] tasks can be automated by AI?" Look for Oxford/Frey-Osborne, McKinsey, WEF, Goldman Sachs reports.
2. **Timeline** — "How many years until AI significantly impacts [job title] roles?"
3. **Saving graces** — "Is [skill] genuinely difficult for AI to replicate?"
4. **Getting cooked items** — "Is [task] actually being automated right now?"

### What counts as a pass:
- Claim is supported by **2+ credible sources** (academic papers, major consulting firms, government reports, reputable news)
- Score is within **15 points** of what research suggests
- Timeline is within **3 years** of consensus estimates
- No major source directly contradicts the claim

### What counts as a fail:
- Claim contradicts multiple credible sources
- Score is wildly off from research consensus
- A "saving grace" is actually already automated
- A "getting cooked" item isn't actually being automated
- Text could be read as offensive to the people in that profession

### Recording results:

```bash
# Pass example
python tools/validate_jobs.py update data/jobs-sample-validation-state.json \
  --job-id plumber --field score --status pass \
  --reason "Oxford study rates plumbing at 0.0035 automation probability" \
  --sources "Frey & Osborne 2013, McKinsey 2023"

# Fail example  
python tools/validate_jobs.py update data/jobs-sample-validation-state.json \
  --job-id accountant --field score --status fail \
  --reason "Multiple sources suggest higher automation risk than 52" \
  --sources "WEF Future of Jobs 2025, PwC UK study"
```

---

## Step 3: Finalize Pass

After checking all pending items:

```bash
python tools/validate_jobs.py finalize data/jobs-sample-validation-state.json
```

This evaluates results and either:
- **Passes** jobs with no issues
- **Fails** jobs with issues (loops back to Step 2 on next pass)
- **Flags for human review** if still failing after pass 3

---

## Step 4: Fix & Retry (Passes 2-3)

For failed jobs:
1. Read the fail reasons from the report
2. Update the job data in the JSON to fix the issue
3. Re-run from Step 1

**Important:** Each fix should cite the source that informed the correction. Don't just adjust numbers — understand why they were wrong.

---

## Step 5: Human Review Queue

After 3 passes, any remaining failures get exported to `data/jobs-sample-human-review.json`. 

Tell Haylie:
- Which jobs failed and why
- What the sources said vs what we had
- Recommended fixes (let her decide)

---

## Quip-Specific Rules

Quips need extra scrutiny because they're the most likely source of controversy:

- **No punching down** — don't mock the people, mock the situation
- **No gendered/racial assumptions** about who does a job
- **No implying a job is worthless** — even fully cooked jobs have dignity
- **Sarcasm should be self-aware** — "update your LinkedIn" lands because it's advice, not mockery
- **When in doubt, drop the quip** — set it to null, not every item needs one

---

## Batch Fact-Checking at Scale (Learned 2026-04-03)

When fact-checking the full dataset (300+ jobs), a one-by-one Perplexity approach is too slow and expensive. Use the batch approach instead:

### Score Fact-Check

**Tool:** `tools/batch_fact_check.py`

1. Group jobs by sector (healthcare, trades, tech, admin/clerical, creative, education, etc.)
2. Run batches of ~30 jobs per Perplexity query, asking for estimated automation scores
3. Compare Perplexity's scores against ours
4. Flag jobs where the delta exceeds a threshold (we used >15 points; in practice this was too strict — Perplexity scores averaged +10.8 points higher than ours, likely due to AI-bullish bias)
5. Results land in `data/fact-check-results.json` and flagged items in `data/fact-check-flagged.json`

**Key finding:** Perplexity consistently scores ~10 points higher (more AI-bullish). We decided NOT to do blanket score corrections because we don't fully trust Perplexity's numbers as ground truth. Use the comparison as a sanity check, not an auto-correction.

### Timeline Fact-Check

**Tool:** `tools/timeline_fact_check.py`

1. Split all jobs into 4 batches (~80 each)
2. Run 4 parallel subagents, each using AI research knowledge (McKinsey, WEF, Oxford, Goldman Sachs) to assess timelines
3. Each subagent writes results to `data/timeline-results-batchN.json`
4. Merge results and identify disagreements

**Key finding:** 98.7% agreement (312/316 jobs). The 4 disagreements were all defensible adjustments, not errors. This approach is fast (minutes vs hours) and reliable.

### What We Learned

- **Sector grouping** works well — similar jobs get more accurate comparisons when batched together
- **Parallel subagents** are effective for splitting large datasets across independent workers
- **Perplexity has AI-bullish bias** — don't blindly accept its scores, but timeline estimates are solid
- **Threshold for flagging** should be ~20 points, not 15 — the natural bias inflates deltas

---

## Edge Cases

- **Jobs with no clear research:** Flag for human review. Don't guess.
- **Conflicting sources:** Use the more conservative (lower) score. Note the conflict.
- **Very new jobs (AI prompt engineer, etc.):** Flag as uncertain. These are inherently speculative.
- **Sensitive professions (military, religious, care workers):** Extra pass on tone. Check quips twice.
