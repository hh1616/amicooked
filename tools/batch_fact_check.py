"""
Batch Fact-Check Tool — Am I Cooked?

Batches jobs into groups and fact-checks automation risk scores via Perplexity.
Designed to work with Claude Code's Perplexity MCP tool.

Usage:
  python tools/batch_fact_check.py prepare data/jobs.json
  python tools/batch_fact_check.py record <batch_num> '<json_results>'
  python tools/batch_fact_check.py status
  python tools/batch_fact_check.py report
"""

import json
import sys
import os
from datetime import datetime

STATE_FILE = "data/fact-check-state.json"
RESULTS_FILE = "data/fact-check-results.json"
BATCH_SIZE = 15
# Flag jobs where Perplexity score differs by more than this
SCORE_THRESHOLD = 15


def prepare(jobs_file):
    """Read jobs.json, group into batches, generate prompts, create state file."""
    with open(jobs_file) as f:
        jobs = json.load(f)

    batches = []
    for i in range(0, len(jobs), BATCH_SIZE):
        batch_jobs = jobs[i:i + BATCH_SIZE]
        batch_num = len(batches) + 1

        # Build the job list for the prompt
        job_lines = []
        for j, job in enumerate(batch_jobs, 1):
            job_lines.append(
                f"{j}. {job['id']} — \"{job['title']}\" "
                f"(our score: {job['score']}/100, {job['automatable']} automatable)"
            )

        prompt = f"""I'm fact-checking an AI job automation risk dataset. For each job below, assess the AI automation risk on a 0-100 scale where:
- 0-15 = Raw (very safe from AI)
- 16-30 = Rare (mostly safe)
- 31-45 = Lightly Toasted (some tasks at risk)
- 46-60 = Half Baked (significant portions automatable)
- 61-75 = Well Done (majority of tasks at risk)
- 76-90 = Extra Crispy (heavily automatable)
- 91-100 = Fully Cooked (almost entirely replaceable)

Consider CURRENT AI capabilities as of 2026 (LLMs, computer vision, robotics, coding agents, etc). Not theoretical future — what's real now.

I'll show our current score. Tell me if you agree or disagree.

IMPORTANT: Format each response as exactly one line per job:
job_id | your_score | AGREE or DISAGREE | brief reason

Jobs to assess:
{chr(10).join(job_lines)}"""

        batches.append({
            "batch_num": batch_num,
            "job_ids": [j["id"] for j in batch_jobs],
            "prompt": prompt,
            "status": "pending",
            "results": []
        })

    state = {
        "source_file": jobs_file,
        "created": datetime.now().isoformat(),
        "batch_size": BATCH_SIZE,
        "total_jobs": len(jobs),
        "total_batches": len(batches),
        "batches": batches
    }

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Prepared {len(batches)} batches of ~{BATCH_SIZE} jobs each ({len(jobs)} total)")
    print(f"State saved to: {STATE_FILE}")
    print(f"\nNext step: For each batch, call Perplexity with the prompt, then record results with:")
    print(f"  python tools/batch_fact_check.py record <batch_num> '<json_results>'")
    print(f"\nBatch 1 prompt preview:")
    print(f"{'─' * 60}")
    print(batches[0]["prompt"][:500] + "...")


def get_prompt(batch_num):
    """Print the prompt for a specific batch."""
    with open(STATE_FILE) as f:
        state = json.load(f)

    batch_num = int(batch_num)
    if batch_num < 1 or batch_num > len(state["batches"]):
        print(f"Error: batch_num must be 1-{len(state['batches'])}")
        sys.exit(1)

    batch = state["batches"][batch_num - 1]
    print(batch["prompt"])


def record(batch_num, results_json):
    """Record Perplexity results for a batch.

    results_json is a JSON array of objects:
    [{"id": "arborist", "perplexity_score": 5, "agree": true, "reason": "..."}, ...]
    """
    with open(STATE_FILE) as f:
        state = json.load(f)

    batch_num = int(batch_num)
    if batch_num < 1 or batch_num > len(state["batches"]):
        print(f"Error: batch_num must be 1-{len(state['batches'])}")
        sys.exit(1)

    batch = state["batches"][batch_num - 1]

    try:
        results = json.loads(results_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    batch["results"] = results
    batch["status"] = "done"
    batch["completed"] = datetime.now().isoformat()

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    done = sum(1 for b in state["batches"] if b["status"] == "done")
    print(f"Batch {batch_num} recorded ({len(results)} jobs)")
    print(f"Progress: {done}/{state['total_batches']} batches done")


def record_bulk(results_json):
    """Record results directly to a flat results file, bypassing batch structure.
    Used when querying by sector rather than by original batch order.

    results_json is a JSON array of objects:
    [{"id": "admin-assistant", "perplexity_score": 85, "agree": false, "reason": "..."}, ...]
    """
    try:
        new_results = json.loads(results_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    # Load existing results or start fresh
    existing = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            existing = json.load(f)

    # Merge (update existing, add new)
    existing_ids = {r["id"]: i for i, r in enumerate(existing)}
    for r in new_results:
        if r["id"] in existing_ids:
            existing[existing_ids[r["id"]]] = r
        else:
            existing.append(r)

    with open(RESULTS_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Recorded {len(new_results)} results ({len(existing)} total in {RESULTS_FILE})")


def status():
    """Show progress."""
    with open(STATE_FILE) as f:
        state = json.load(f)

    done = sum(1 for b in state["batches"] if b["status"] == "done")
    pending = sum(1 for b in state["batches"] if b["status"] == "pending")
    total_results = sum(len(b["results"]) for b in state["batches"])

    print(f"\nFact-Check Progress")
    print(f"{'─' * 40}")
    print(f"Total jobs: {state['total_jobs']}")
    print(f"Batches: {done} done / {pending} pending / {state['total_batches']} total")
    print(f"Jobs checked: {total_results}/{state['total_jobs']}")

    if pending > 0:
        next_batch = next(b for b in state["batches"] if b["status"] == "pending")
        print(f"\nNext batch: #{next_batch['batch_num']} ({len(next_batch['job_ids'])} jobs)")


def report():
    """Compare Perplexity results against jobs.json and flag discrepancies."""
    with open(STATE_FILE) as f:
        state = json.load(f)

    with open(state["source_file"]) as f:
        jobs = json.load(f)

    jobs_by_id = {j["id"]: j for j in jobs}

    # Collect all results from batches
    all_results = {}
    for batch in state["batches"]:
        for result in batch["results"]:
            all_results[result["id"]] = result

    # Also load from flat results file (sector-based queries)
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            bulk_results = json.load(f)
        for result in bulk_results:
            all_results[result["id"]] = result

    if not all_results:
        print("No results recorded yet. Run some batches first.")
        return

    # Compare and flag
    flagged = []
    agreed = []
    missing = []

    for job_id, job in jobs_by_id.items():
        if job_id not in all_results:
            missing.append(job_id)
            continue

        result = all_results[job_id]
        our_score = job["score"]
        their_score = result["perplexity_score"]
        delta = abs(our_score - their_score)

        entry = {
            "id": job_id,
            "title": job["title"],
            "our_score": our_score,
            "perplexity_score": their_score,
            "delta": delta,
            "agree": result.get("agree", False),
            "reason": result.get("reason", ""),
        }

        if delta > SCORE_THRESHOLD or not result.get("agree", True):
            flagged.append(entry)
        else:
            agreed.append(entry)

    # Sort flagged by delta (biggest discrepancy first)
    flagged.sort(key=lambda x: x["delta"], reverse=True)

    # Print report
    print(f"\n{'=' * 70}")
    print(f"  FACT-CHECK REPORT")
    print(f"{'=' * 70}")
    print(f"  Checked: {len(all_results)} / {len(jobs_by_id)} jobs")
    print(f"  Agreed:  {len(agreed)}")
    print(f"  Flagged: {len(flagged)} (delta > {SCORE_THRESHOLD} or explicit disagree)")
    if missing:
        print(f"  Missing: {len(missing)} (not yet checked)")
    print()

    if flagged:
        print(f"  {'─' * 66}")
        print(f"  FLAGGED JOBS (need review)")
        print(f"  {'─' * 66}")
        for f in flagged:
            direction = "↑" if f["perplexity_score"] > f["our_score"] else "↓"
            print(f"  {direction} {f['title']}")
            print(f"    Ours: {f['our_score']}  |  Perplexity: {f['perplexity_score']}  |  Delta: {f['delta']}")
            print(f"    Reason: {f['reason']}")
            print()

    # Save flagged jobs to file for easy reference
    if flagged:
        flagged_file = "data/fact-check-flagged.json"
        with open(flagged_file, "w") as fout:
            json.dump(flagged, fout, indent=2)
        print(f"  Flagged jobs saved to: {flagged_file}")

    # Save full report
    report_data = {
        "generated": datetime.now().isoformat(),
        "total_checked": len(all_results),
        "total_agreed": len(agreed),
        "total_flagged": len(flagged),
        "total_missing": len(missing),
        "threshold": SCORE_THRESHOLD,
        "flagged": flagged,
        "agreed": agreed,
        "missing": missing
    }
    report_file = "data/fact-check-report.json"
    with open(report_file, "w") as fout:
        json.dump(report_data, fout, indent=2)
    print(f"  Full report saved to: {report_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tools/batch_fact_check.py prepare <jobs.json>")
        print("  python tools/batch_fact_check.py prompt <batch_num>")
        print("  python tools/batch_fact_check.py record <batch_num> '<json_results>'")
        print("  python tools/batch_fact_check.py status")
        print("  python tools/batch_fact_check.py report")
        sys.exit(1)

    command = sys.argv[1]

    if command == "prepare":
        if len(sys.argv) < 3:
            print("Error: provide jobs file path")
            sys.exit(1)
        prepare(sys.argv[2])

    elif command == "prompt":
        if len(sys.argv) < 3:
            print("Error: provide batch number")
            sys.exit(1)
        get_prompt(sys.argv[2])

    elif command == "record":
        if len(sys.argv) < 4:
            print("Error: provide batch_num and json_results")
            sys.exit(1)
        record(sys.argv[2], sys.argv[3])

    elif command == "record-bulk":
        if len(sys.argv) < 3:
            print("Error: provide json_results")
            sys.exit(1)
        record_bulk(sys.argv[2])

    elif command == "status":
        status()

    elif command == "report":
        report()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
