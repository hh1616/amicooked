# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**Directory layout:**
```
mockups/        # Final approved mockups (4 HTML files)
data/           # Job dataset (jobs.json) — the core data powering the site
docs/           # Design spec, implementation plan, and reference docs
archive/        # Old files kept for reference
  mockups/      # Previous mockup iterations (31 HTML files)
  amicooked-progress.md  # Original brainstorming progress notes
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
brand_assets/   # Logos, icons (currently empty)
.env            # API keys and environment variables (NEVER store secrets anywhere else)
```

**Final mockups (in `mockups/`):**
- `landing-barlow-final.html` — Desktop landing page
- `landing-mobile-v2.html` — Mobile landing page
- `results-desktop-v1.html` — Desktop results page
- `results-mobile-v15.html` — Mobile results page

**Key docs (in `docs/`):**
- `design-spec.md` — Single source of truth for all design decisions
- `plan.md` — Implementation plan and progress tracker

**Tools (in `tools/`):**
- `validate_jobs.py` — Job data validator (rule-based checks + fact-check state management)
- `add_search_terms.py` — Adds/updates searchTerms field on all jobs for fuzzy matching

**Workflows (in `workflows/`):**
- `validate-job-data.md` — SOP for 3-pass validation loop (rule checks → Perplexity fact-checks → human review)

**Data (in `data/`):**
- `jobs-sample.json` — 10-job test batch (original sample, kept for reference)
- `jobs.json` — Full dataset (219 jobs, rule-based validation passes, searchTerms included)
- `jobs-validation-state.json` — Validation state from rule checks (fact-checks still pending)

**Current status:** Dataset generated (219 jobs). Rule-based validation passes. Next step is batched Perplexity fact-checking (~15 category queries), then building the site.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
