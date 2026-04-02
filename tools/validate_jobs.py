"""
Job Data Validator — Am I Cooked?

Reads a jobs JSON file, runs rule-based validation checks, and manages
a 3-pass validation loop. Web-based fact-checking is done externally
(via Perplexity MCP in Claude Code) and results are fed back in.

Usage:
  python tools/validate_jobs.py check data/jobs-sample.json
  python tools/validate_jobs.py report data/validation-state.json
  python tools/validate_jobs.py update data/validation-state.json --job-id plumber --field score --status pass
  python tools/validate_jobs.py update data/validation-state.json --job-id plumber --field score --status fail --reason "Score too low per Oxford study"
  python tools/validate_jobs.py finalize data/validation-state.json
"""

import json
import sys
import os
from datetime import datetime

# ── Controversial / sensitive topic flags ──────────────────────────

CONTROVERSIAL_KEYWORDS = [
    "lazy", "stupid", "incompetent", "worthless", "useless", "pathetic",
    "dead-end", "waste of time", "joke of a job", "not a real job",
    "anyone could do", "brainless", "mindless", "monkey could",
    "third world", "sweatshop", "slave", "illegal",
    "race", "gender", "religion", "political",
]

SENSITIVE_JOB_CATEGORIES = [
    "sex worker", "stripper", "escort", "adult",
    "pastor", "priest", "imam", "rabbi", "minister",
    "soldier", "military", "police", "prison guard",
]

# Quips that punch at the worker instead of the tech/situation.
# Pattern: phrases that imply the person or their work is lesser.
PUNCH_DOWN_PATTERNS = [
    "killed this",          # "OCR killed this years ago" — rubbing it in
    "already dead",         # mocking a dying role
    "half-dead",            # same
    "you're done",          # addressing the worker directly in a harsh way
    "good luck",            # sarcastic dismissal
    "RIP",                  # mocking job death
    "no one needs",         # dismissing the role
    "why do you still",     # questioning their existence
    "just quit",            # telling them to leave
    "give up",              # same
    "not even",             # dismissive
    "literally what bots were built for",  # implies the person is a bot substitute
]

# ── Rule-based checks ─────────────────────────────────────────────

def check_score_consistency(job):
    """Score should roughly align with automatable % and timeline."""
    issues = []
    score = job["score"]

    # Parse automatable percentage
    auto_str = job.get("automatable", "0%").replace("%", "")
    try:
        auto_pct = int(auto_str)
    except ValueError:
        issues.append({
            "field": "automatable",
            "type": "format",
            "severity": "error",
            "message": f"Can't parse automatable value: {job['automatable']}"
        })
        return issues

    # Parse timeline
    timeline_str = job.get("timeline", "~5").replace("~", "").replace("+", "")
    try:
        timeline_yrs = int(timeline_str)
    except ValueError:
        issues.append({
            "field": "timeline",
            "type": "format",
            "severity": "error",
            "message": f"Can't parse timeline value: {job['timeline']}"
        })
        return issues

    # High score but low automation = suspicious
    if score > 70 and auto_pct < 40:
        issues.append({
            "field": "score",
            "type": "consistency",
            "severity": "warning",
            "message": f"Score {score} is high but automatable is only {auto_pct}%"
        })

    # Low score but high automation = suspicious
    if score < 30 and auto_pct > 60:
        issues.append({
            "field": "score",
            "type": "consistency",
            "severity": "warning",
            "message": f"Score {score} is low but automatable is {auto_pct}%"
        })

    # Very short timeline but low score = suspicious
    if timeline_yrs <= 2 and score < 40:
        issues.append({
            "field": "timeline",
            "type": "consistency",
            "severity": "warning",
            "message": f"Timeline is only ~{timeline_yrs} yrs but score is just {score}"
        })

    # Very long timeline but high score = suspicious
    if timeline_yrs >= 15 and score > 60:
        issues.append({
            "field": "timeline",
            "type": "consistency",
            "severity": "warning",
            "message": f"Timeline is ~{timeline_yrs} yrs but score is {score}"
        })

    return issues


def check_verdict_matches_score(job):
    """Verify the verdict label matches the score range."""
    score = job["score"]
    verdict = job["verdict"]

    verdict_map = {
        (0, 15): "Raw",
        (16, 30): "Rare",
        (31, 45): "Lightly Toasted",
        (46, 60): "Half Baked",
        (61, 75): "Well Done",
        (76, 90): "Extra Crispy",
        (91, 100): "Fully Cooked",
    }

    expected = None
    for (low, high), label in verdict_map.items():
        if low <= score <= high:
            expected = label
            break

    if expected and verdict != expected:
        return [{
            "field": "verdict",
            "type": "consistency",
            "severity": "error",
            "message": f"Score {score} should map to '{expected}' but verdict is '{verdict}'"
        }]
    return []


def check_controversial_content(job):
    """Flag text or quips containing controversial language."""
    issues = []

    # Check all text fields
    fields_to_check = []
    fields_to_check.append(("verdictQuip", job.get("verdictQuip", "")))

    for i, item in enumerate(job.get("savingGraces", [])):
        fields_to_check.append((f"savingGraces[{i}].text", item.get("text", "")))
        if item.get("quip"):
            fields_to_check.append((f"savingGraces[{i}].quip", item["quip"]))

    for i, item in enumerate(job.get("gettingCooked", [])):
        fields_to_check.append((f"gettingCooked[{i}].text", item.get("text", "")))
        if item.get("quip"):
            fields_to_check.append((f"gettingCooked[{i}].quip", item["quip"]))

    for field_name, text in fields_to_check:
        text_lower = text.lower()
        for keyword in CONTROVERSIAL_KEYWORDS:
            if keyword in text_lower:
                issues.append({
                    "field": field_name,
                    "type": "controversial",
                    "severity": "fail",
                    "message": f"Contains potentially controversial term: '{keyword}' in \"{text}\""
                })

    # Check if the job title itself is sensitive
    title_lower = job.get("title", "").lower()
    for sensitive in SENSITIVE_JOB_CATEGORIES:
        if sensitive in title_lower:
            issues.append({
                "field": "title",
                "type": "sensitive_category",
                "severity": "warning",
                "message": f"Job title falls in sensitive category: '{sensitive}'"
            })

    return issues


def check_punch_down_quips(job):
    """Flag quips that punch at the worker rather than the tech/situation.

    Good quip: "Copilot says hi" — laughs at the tech
    Bad quip: "OCR killed this years ago" — rubs it in the worker's face

    Rule: quips should mock the technology or the absurdity of the situation,
    never the person doing the job.
    """
    issues = []

    # Collect all quips
    quip_fields = []
    for i, item in enumerate(job.get("savingGraces", [])):
        if item.get("quip"):
            quip_fields.append((f"savingGraces[{i}].quip", item["quip"]))
    for i, item in enumerate(job.get("gettingCooked", [])):
        if item.get("quip"):
            quip_fields.append((f"gettingCooked[{i}].quip", item["quip"]))

    for field_name, quip in quip_fields:
        quip_lower = quip.lower()
        for pattern in PUNCH_DOWN_PATTERNS:
            if pattern.lower() in quip_lower:
                issues.append({
                    "field": field_name,
                    "type": "punch_down",
                    "severity": "fail",
                    "message": f"Quip punches at the worker, not the tech: \"{quip}\" (matched: '{pattern}')"
                })
                break  # One flag per quip is enough

    return issues


def check_structure(job):
    """Verify all required fields exist and have valid types."""
    issues = []
    required = ["id", "title", "score", "verdict", "verdictQuip", "timeline",
                 "timelineUnit", "automatable", "pivotPotential", "savingGraces", "gettingCooked"]

    for field in required:
        if field not in job:
            issues.append({
                "field": field,
                "type": "missing",
                "severity": "error",
                "message": f"Missing required field: {field}"
            })

    if "score" in job and not (0 <= job["score"] <= 100):
        issues.append({
            "field": "score",
            "type": "range",
            "severity": "error",
            "message": f"Score {job['score']} is outside 0-100 range"
        })

    if "savingGraces" in job and len(job["savingGraces"]) < 2:
        issues.append({
            "field": "savingGraces",
            "type": "content",
            "severity": "warning",
            "message": "Should have at least 2 saving graces"
        })

    if "gettingCooked" in job and len(job["gettingCooked"]) < 2:
        issues.append({
            "field": "gettingCooked",
            "type": "content",
            "severity": "warning",
            "message": "Should have at least 2 items getting cooked"
        })

    if "pivotPotential" in job and job["pivotPotential"] not in ["LOW", "MED", "HIGH"]:
        issues.append({
            "field": "pivotPotential",
            "type": "enum",
            "severity": "error",
            "message": f"pivotPotential must be LOW, MED, or HIGH — got '{job['pivotPotential']}'"
        })

    return issues


def generate_fact_check_queries(job):
    """Generate questions that need web-based fact-checking."""
    queries = []
    title = job["title"]

    # Core claim: automation risk score
    queries.append({
        "field": "score",
        "query": f"What percentage of {title} tasks can be automated by AI? Cite specific studies (Oxford, McKinsey, Goldman Sachs, World Economic Forum).",
        "context": f"We scored {title} at {job['score']}/100 cooked (higher = more replaceable) with {job['automatable']} automatable"
    })

    # Timeline claim
    queries.append({
        "field": "timeline",
        "query": f"How many years until AI significantly impacts {title} jobs? What do major reports say?",
        "context": f"We estimated {job['timeline']} {job['timelineUnit']}"
    })

    # Saving graces — are these actually hard to automate?
    for i, grace in enumerate(job.get("savingGraces", [])):
        queries.append({
            "field": f"savingGraces[{i}]",
            "query": f"Is '{grace['text']}' genuinely difficult for AI to replicate for {title} roles?",
            "context": grace["text"]
        })

    # Getting cooked — are these actually being automated?
    for i, cooked in enumerate(job.get("gettingCooked", [])):
        queries.append({
            "field": f"gettingCooked[{i}]",
            "query": f"Is '{cooked['text']}' actually being automated right now for {title} roles? Any evidence?",
            "context": cooked["text"]
        })

    return queries


# ── Validation state management ───────────────────────────────────

def run_rule_checks(jobs_file):
    """Run all rule-based checks and create initial validation state."""
    with open(jobs_file) as f:
        jobs = json.load(f)

    state = {
        "source_file": jobs_file,
        "created": datetime.now().isoformat(),
        "current_pass": 1,
        "max_passes": 3,
        "jobs": {}
    }

    for job in jobs:
        job_id = job["id"]
        all_issues = []
        all_issues.extend(check_structure(job))
        all_issues.extend(check_verdict_matches_score(job))
        all_issues.extend(check_score_consistency(job))
        all_issues.extend(check_controversial_content(job))
        all_issues.extend(check_punch_down_quips(job))

        fact_checks = generate_fact_check_queries(job)

        rule_status = "pass"
        for issue in all_issues:
            if issue["severity"] in ("error", "fail"):
                rule_status = "fail"
                break
            if issue["severity"] == "warning":
                rule_status = "review"

        state["jobs"][job_id] = {
            "title": job["title"],
            "score": job["score"],
            "rule_issues": all_issues,
            "rule_status": rule_status,
            "fact_checks": fact_checks,
            "fact_check_results": [],
            "passes": [],
            "final_status": "pending"
        }

    return state


def print_report(state):
    """Print a human-readable validation report."""
    print(f"\n{'='*60}")
    print(f"  VALIDATION REPORT — Pass {state['current_pass']}/{state['max_passes']}")
    print(f"{'='*60}\n")

    counts = {"pass": 0, "fail": 0, "review": 0, "pending": 0}

    for job_id, job_state in state["jobs"].items():
        status = job_state["final_status"]
        counts[status] = counts.get(status, 0) + 1

        icon = {"pass": "OK", "fail": "FAIL", "review": "FLAG", "pending": "..."}
        print(f"  [{icon.get(status, '?')}] {job_state['title']} (score: {job_state['score']})")

        # Show rule issues
        for issue in job_state["rule_issues"]:
            sev = issue["severity"].upper()
            print(f"        {sev}: {issue['message']}")

        # Show fact-check results
        for fc in job_state.get("fact_check_results", []):
            fc_status = fc.get("status", "pending").upper()
            print(f"        FACT [{fc_status}]: {fc.get('field', '?')} — {fc.get('summary', 'no summary')}")

        print()

    print(f"{'─'*60}")
    print(f"  PASS: {counts.get('pass', 0)}  |  FAIL: {counts.get('fail', 0)}  |  FLAG: {counts.get('review', 0)}  |  PENDING: {counts.get('pending', 0)}")
    print(f"{'─'*60}")

    # Show what needs web fact-checking
    pending_checks = []
    for job_id, job_state in state["jobs"].items():
        if job_state["final_status"] in ("pending", "review"):
            for fc in job_state["fact_checks"]:
                if not any(r["field"] == fc["field"] for r in job_state.get("fact_check_results", [])):
                    pending_checks.append((job_id, fc))

    if pending_checks:
        print(f"\n  PENDING FACT-CHECKS ({len(pending_checks)} queries):")
        print(f"  Use Perplexity MCP to verify, then feed results back with:")
        print(f"  python tools/validate_jobs.py update <state-file> --job-id <id> --field <field> --status pass|fail\n")
        for job_id, fc in pending_checks[:5]:
            print(f"  [{job_id}] {fc['field']}:")
            print(f"    Q: {fc['query']}")
            print(f"    Context: {fc['context']}")
            print()
        if len(pending_checks) > 5:
            print(f"  ... and {len(pending_checks) - 5} more\n")


def update_fact_check(state, job_id, field, status, reason="", sources=""):
    """Record a fact-check result for a specific field."""
    if job_id not in state["jobs"]:
        print(f"Error: job '{job_id}' not found")
        return state

    result = {
        "field": field,
        "status": status,
        "summary": reason,
        "sources": sources,
        "pass_number": state["current_pass"],
        "timestamp": datetime.now().isoformat()
    }

    state["jobs"][job_id]["fact_check_results"].append(result)
    return state


def finalize_pass(state):
    """Evaluate all results for current pass and advance or flag for human review."""
    current_pass = state["current_pass"]

    for job_id, job_state in state["jobs"].items():
        if job_state["final_status"] == "pass":
            continue

        # Check rule status
        has_errors = any(i["severity"] in ("error", "fail") for i in job_state["rule_issues"])

        # Check fact-check results
        fc_results = job_state.get("fact_check_results", [])
        has_fc_fails = any(r["status"] == "fail" for r in fc_results)
        all_fc_done = len(fc_results) >= len(job_state["fact_checks"])

        if has_errors or has_fc_fails:
            if current_pass >= state["max_passes"]:
                job_state["final_status"] = "review"  # Human review after 3 fails
            else:
                job_state["final_status"] = "fail"
        elif all_fc_done:
            job_state["final_status"] = "pass"
        else:
            job_state["final_status"] = "pending"

        job_state["passes"].append({
            "pass_number": current_pass,
            "status": job_state["final_status"],
            "timestamp": datetime.now().isoformat()
        })

    # Advance pass counter
    if current_pass < state["max_passes"]:
        has_non_pass = any(j["final_status"] != "pass" for j in state["jobs"].values())
        if has_non_pass:
            state["current_pass"] = current_pass + 1

    return state


# ── CLI ───────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python tools/validate_jobs.py check <jobs.json>")
        print("  python tools/validate_jobs.py report <state.json>")
        print("  python tools/validate_jobs.py update <state.json> --job-id <id> --field <field> --status pass|fail [--reason '...'] [--sources '...']")
        print("  python tools/validate_jobs.py finalize <state.json>")
        sys.exit(1)

    command = sys.argv[1]
    filepath = sys.argv[2]

    if command == "check":
        state = run_rule_checks(filepath)
        state_file = filepath.replace(".json", "-validation-state.json")
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        print(f"Validation state saved to: {state_file}")
        print_report(state)

    elif command == "report":
        with open(filepath) as f:
            state = json.load(f)
        print_report(state)

    elif command == "update":
        with open(filepath) as f:
            state = json.load(f)

        # Parse args
        args = sys.argv[3:]
        job_id = field = status = reason = sources = ""
        i = 0
        while i < len(args):
            if args[i] == "--job-id" and i + 1 < len(args):
                job_id = args[i + 1]; i += 2
            elif args[i] == "--field" and i + 1 < len(args):
                field = args[i + 1]; i += 2
            elif args[i] == "--status" and i + 1 < len(args):
                status = args[i + 1]; i += 2
            elif args[i] == "--reason" and i + 1 < len(args):
                reason = args[i + 1]; i += 2
            elif args[i] == "--sources" and i + 1 < len(args):
                sources = args[i + 1]; i += 2
            else:
                i += 1

        if not all([job_id, field, status]):
            print("Error: --job-id, --field, and --status are required")
            sys.exit(1)

        state = update_fact_check(state, job_id, field, status, reason, sources)
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
        print(f"Updated {job_id}.{field} → {status}")

    elif command == "finalize":
        with open(filepath) as f:
            state = json.load(f)
        state = finalize_pass(state)
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
        print_report(state)

        # Export human review queue
        review_jobs = {k: v for k, v in state["jobs"].items() if v["final_status"] == "review"}
        if review_jobs:
            review_file = filepath.replace("-validation-state.json", "-human-review.json")
            with open(review_file, "w") as f:
                json.dump(review_jobs, f, indent=2)
            print(f"\n  Human review queue saved to: {review_file}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
