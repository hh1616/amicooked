"""
Timeline Fact-Check Tool — Am I Cooked?

Groups jobs by sector and fact-checks timeline estimates via Perplexity.
Designed to work with Claude Code's Perplexity MCP tool.

Usage:
  python tools/timeline_fact_check.py prepare data/jobs.json
  python tools/timeline_fact_check.py record <batch_name> '<json_results>'
  python tools/timeline_fact_check.py status
  python tools/timeline_fact_check.py report
  python tools/timeline_fact_check.py apply [--dry-run]
"""

import json
import sys
import os
from datetime import datetime

STATE_FILE = "data/timeline-check-state.json"
RESULTS_FILE = "data/timeline-check-results.json"
REPORT_FILE = "data/timeline-check-report.json"

# Timeline tolerance: flag if Perplexity estimate differs by more than this many years
TIMELINE_THRESHOLD = 3

# Sector assignments for each job
SECTORS = {
    "healthcare": [
        "aged-care-nurse", "aged-care-worker", "anaesthesiologist", "audiologist",
        "chiropractor", "clinic-manager", "dental-assistant", "dental-hygienist",
        "dentist", "dermatologist", "disability-support-worker", "doctor-gp",
        "emergency-medicine-doctor", "massage-therapist", "medical-coder",
        "medical-lab-technician", "medical-transcriptionist", "mental-health-nurse",
        "midwife", "nurse", "nurse-practitioner", "occupational-therapist",
        "optician", "optometrist", "orthotist", "paediatrician", "paramedic",
        "pathologist", "pharmacist", "pharmacy-technician", "physical-therapist",
        "physiotherapy-assistant", "psychiatrist", "psychologist", "radiologist",
        "sonographer", "speech-pathologist", "surgeon", "veterinarian",
        "veterinary-nurse", "nutritionist",
    ],
    "tech_engineering": [
        "backend-developer", "cloud-architect", "cybersecurity-analyst",
        "data-scientist", "database-administrator", "devops-engineer",
        "electrical-engineer", "frontend-developer", "machine-learning-engineer",
        "mechanical-engineer", "mobile-app-developer", "network-administrator",
        "penetration-tester", "quality-assurance-tester", "robotics-engineer",
        "software-engineer", "systems-administrator", "web-developer",
        "it-manager", "it-support-specialist", "technical-support-specialist",
    ],
    "trades_construction": [
        "air-conditioning-installer", "arborist", "auto-electrician",
        "auto-mechanic", "boilermaker", "bricklayer", "building-inspector",
        "cabinet-maker", "carpenter", "concreter", "construction-manager",
        "construction-worker", "crane-operator", "diesel-mechanic",
        "electrician", "elevator-installer", "fitter-and-turner", "glazier",
        "house-painter", "hvac-technician", "landscaper", "locksmith",
        "plasterer", "plumber", "pool-technician", "roofer", "scaffolder",
        "tiler", "welder",
    ],
    "office_admin_clerical": [
        "accounts-payable-clerk", "accounts-receivable-clerk",
        "administrative-assistant", "billing-specialist", "bookkeeper",
        "basic-bookkeeper", "call-centre-agent", "cashier",
        "check-processing-clerk", "classified-ad-taker", "correspondence-clerk",
        "data-entry-clerk", "desktop-publisher", "document-scanner",
        "executive-assistant", "file-clerk", "front-desk-receptionist",
        "invoice-processor", "library-catalog-clerk", "mail-room-clerk",
        "medical-transcriptionist", "meter-reader", "office-administrator",
        "office-manager", "order-clerk", "payroll-specialist",
        "postal-sorter", "print-shop-operator", "proofreader",
        "receptionist", "scheduling-coordinator", "switchboard-operator",
        "telephone-operator", "title-examiner", "toll-booth-operator",
        "transcriptionist", "typist", "word-processor-operator",
    ],
    "finance_insurance_legal": [
        "accountant", "actuary", "auditor", "claims-adjuster",
        "claims-processor", "compliance-officer", "conveyancer",
        "credit-analyst", "financial-analyst", "financial-planner",
        "freight-broker", "insurance-agent", "insurance-underwriter",
        "lawyer", "legal-secretary", "loan-officer", "loan-processor",
        "mortgage-broker", "mortgage-processor", "paralegal",
        "patent-examiner", "risk-analyst", "stock-analyst",
        "tax-preparer",
    ],
    "creative_media": [
        "animator", "copywriter", "content-writer", "fashion-designer",
        "film-director", "game-designer", "graphic-designer", "illustrator",
        "influencer", "journalist", "makeup-artist", "music-producer",
        "musician", "news-anchor", "photo-retoucher", "photographer",
        "podcast-producer", "radio-broadcaster", "screenwriter",
        "social-media-manager", "sound-engineer", "sports-journalist",
        "tattoo-artist", "technical-writer", "video-editor",
        "voice-actor",
    ],
    "education": [
        "art-teacher", "corporate-trainer", "education-coordinator",
        "esl-teacher", "high-school-teacher", "kindergarten-teacher",
        "librarian", "library-assistant", "primary-school-teacher",
        "school-counselor", "special-education-teacher",
        "teaching-assistant", "tutor", "university-professor",
        "daycare-director",
    ],
    "food_hospitality": [
        "baker", "barista", "bartender", "butcher", "chef",
        "concierge", "fast-food-cook", "florist", "hotel-manager",
        "housekeeper", "pastry-chef", "restaurant-manager",
        "sommelier", "sous-chef", "waiter", "wedding-planner",
    ],
    "transport_logistics": [
        "air-traffic-controller", "bus-driver", "courier",
        "drone-operator", "flight-attendant", "flight-dispatcher",
        "food-delivery-driver", "forklift-operator",
        "logistics-coordinator", "pilot", "rideshare-driver",
        "supply-chain-analyst", "truck-driver", "warehouse-manager",
        "warehouse-picker",
    ],
    "management_business": [
        "advertising-executive", "branch-manager", "business-analyst",
        "business-manager", "ceo", "customer-service-manager",
        "event-planner", "general-manager", "hr-manager",
        "immigration-consultant", "inventory-manager",
        "management-consultant", "marketing-manager", "migration-agent",
        "operations-manager", "procurement-manager", "product-manager",
        "project-manager", "property-manager", "public-relations-specialist",
        "purchasing-agent", "real-estate-agent", "recruitment-consultant",
        "regional-manager", "retail-manager", "sales-manager",
        "scrum-master", "store-manager", "sustainability-consultant",
    ],
    "science_research": [
        "archaeologist", "economist", "environmental-scientist",
        "forensic-scientist", "geologist", "lab-technician",
        "marine-biologist", "market-researcher", "research-scientist",
        "survey-researcher", "statistical-assistant", "urban-planner",
    ],
    "service_personal_care": [
        "auto-detailer", "barber", "childcare-worker", "cleaner",
        "community-development-officer", "dog-groomer", "farmer",
        "firefighter", "fitness-instructor", "funeral-director",
        "hair-stylist", "housewife", "nail-technician", "park-ranger",
        "personal-trainer", "pest-control-technician", "police-officer",
        "security-guard", "social-worker", "youth-worker",
    ],
    "sports_entertainment": [
        "athletic-trainer", "choreographer", "sports-coach",
        "sports-coach-head", "sports-scorekeeper", "video-game-tester",
        "museum-curator",
    ],
    "obsolete_automated": [
        "assembly-line-worker", "directory-assistance-operator",
        "factory-quality-inspector", "map-drafter", "drafter",
        "parking-lot-attendant", "photo-lab-technician",
        "production-planner", "telemarketer", "telephone-survey-interviewer",
        "textile-worker", "ticket-agent", "travel-agent",
        "travel-booking-agent", "quantity-surveyor",
    ],
    "transport_misc": [
        "diplomat", "interior-designer", "mining-worker",
        "architect", "civil-engineer", "translator",
        "ux-designer", "bank-teller", "retail-sales-assistant",
    ],
}


def prepare(jobs_file):
    """Read jobs.json, group into sector batches, generate timeline prompts."""
    with open(jobs_file) as f:
        jobs = json.load(f)

    jobs_by_id = {j["id"]: j for j in jobs}

    # Verify all jobs are assigned to a sector
    all_assigned = set()
    for sector_jobs in SECTORS.values():
        all_assigned.update(sector_jobs)

    missing = set(jobs_by_id.keys()) - all_assigned
    extra = all_assigned - set(jobs_by_id.keys())

    if missing:
        print(f"WARNING: {len(missing)} jobs not assigned to any sector:")
        for m in sorted(missing):
            print(f"  - {m} ({jobs_by_id[m]['title']})")
        print()
    if extra:
        print(f"WARNING: {len(extra)} sector assignments don't match any job:")
        for e in sorted(extra):
            print(f"  - {e}")
        print()

    batches = []
    for sector_name, job_ids in SECTORS.items():
        valid_ids = [jid for jid in job_ids if jid in jobs_by_id]
        if not valid_ids:
            continue

        job_lines = []
        for jid in valid_ids:
            job = jobs_by_id[jid]
            job_lines.append(
                f"- {job['title']} (our estimate: {job['timeline']} years)"
            )

        prompt = f"""I'm fact-checking the timeline estimates in an AI job automation dataset. For each job below, estimate how many years until AI significantly disrupts this role (meaning AI handles 50%+ of core tasks, not full replacement).

Consider:
- Current AI capabilities as of 2026 (LLMs, computer vision, robotics, autonomous vehicles, etc.)
- Industry adoption speed and regulatory barriers
- Physical vs cognitive task mix
- How quickly the technology is actually being deployed, not just demonstrated

Our current estimates are shown. Tell me if each is reasonable or needs adjustment.

IMPORTANT: Format each response as exactly one line per job:
job_title | your_estimate_years | AGREE or ADJUST | brief reason

Jobs in {sector_name.replace('_', ' ')}:
{chr(10).join(job_lines)}"""

        batches.append({
            "sector": sector_name,
            "job_ids": valid_ids,
            "prompt": prompt,
            "status": "pending",
            "results": [],
        })

    state = {
        "source_file": jobs_file,
        "created": datetime.now().isoformat(),
        "total_jobs": len(jobs),
        "total_batches": len(batches),
        "timeline_threshold": TIMELINE_THRESHOLD,
        "batches": batches,
    }

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Prepared {len(batches)} sector batches covering {len(all_assigned & set(jobs_by_id.keys()))} jobs")
    print(f"State file: {STATE_FILE}")
    print()
    for b in batches:
        print(f"  {b['sector']}: {len(b['job_ids'])} jobs")


def record(sector_name, results_json):
    """Record Perplexity results for a sector batch."""
    with open(STATE_FILE) as f:
        state = json.load(f)

    # Find the batch
    batch = None
    for b in state["batches"]:
        if b["sector"] == sector_name:
            batch = b
            break

    if not batch:
        print(f"ERROR: No batch found for sector '{sector_name}'")
        sys.exit(1)

    # Parse results - expect list of dicts with title, years, agree, reason
    if isinstance(results_json, str):
        results = json.loads(results_json)
    else:
        results = results_json

    batch["results"] = results
    batch["status"] = "done"
    batch["completed"] = datetime.now().isoformat()

    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Recorded {len(results)} results for {sector_name}")


def status():
    """Show current progress."""
    with open(STATE_FILE) as f:
        state = json.load(f)

    done = sum(1 for b in state["batches"] if b["status"] == "done")
    total = state["total_batches"]
    total_results = sum(len(b["results"]) for b in state["batches"])

    print(f"Progress: {done}/{total} batches done ({total_results} results)")
    print()
    for b in state["batches"]:
        status_icon = "done" if b["status"] == "done" else "pending"
        print(f"  [{status_icon}] {b['sector']}: {len(b['job_ids'])} jobs, {len(b['results'])} results")


def report():
    """Generate comparison report between our timelines and Perplexity's."""
    with open(STATE_FILE) as f:
        state = json.load(f)

    source_file = state["source_file"]
    with open(source_file) as f:
        jobs = json.load(f)
    jobs_by_id = {j["id"]: j for j in jobs}

    flagged = []
    all_results = []

    for batch in state["batches"]:
        if batch["status"] != "done":
            continue
        for result in batch["results"]:
            job_id = result.get("job_id")
            if not job_id or job_id not in jobs_by_id:
                continue

            job = jobs_by_id[job_id]
            our_years = int(job["timeline"].replace("~", ""))
            their_years = result.get("years", our_years)
            delta = abs(our_years - their_years)
            agree = result.get("agree", True)

            entry = {
                "id": job_id,
                "title": job["title"],
                "our_timeline": our_years,
                "perplexity_timeline": their_years,
                "delta": delta,
                "agree": agree,
                "reason": result.get("reason", ""),
                "sector": batch["sector"],
            }
            all_results.append(entry)

            if delta > state["timeline_threshold"] or not agree:
                flagged.append(entry)

    # Sort flagged by delta descending
    flagged.sort(key=lambda x: -x["delta"])

    report_data = {
        "generated": datetime.now().isoformat(),
        "total_checked": len(all_results),
        "total_flagged": len(flagged),
        "threshold_years": state["timeline_threshold"],
        "avg_delta": round(sum(r["delta"] for r in all_results) / max(len(all_results), 1), 1),
        "flagged": flagged,
        "all_results": all_results,
    }

    with open(REPORT_FILE, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"Report: {len(all_results)} checked, {len(flagged)} flagged (threshold: >{state['timeline_threshold']} years)")
    print(f"Average delta: {report_data['avg_delta']} years")
    print(f"Saved to: {REPORT_FILE}")

    if flagged:
        print(f"\nTop 10 biggest discrepancies:")
        for f_item in flagged[:10]:
            direction = "too low" if f_item["our_timeline"] < f_item["perplexity_timeline"] else "too high"
            print(f"  {f_item['title']}: ours ~{f_item['our_timeline']}y vs Perplexity ~{f_item['perplexity_timeline']}y ({direction}, delta {f_item['delta']})")


def apply_fixes(dry_run=False):
    """Apply timeline corrections from report to jobs.json."""
    if not os.path.exists(REPORT_FILE):
        print("ERROR: No report file. Run 'report' first.")
        sys.exit(1)

    with open(REPORT_FILE) as f:
        report_data = json.load(f)

    source_file = "data/jobs.json"
    with open(source_file) as f:
        jobs = json.load(f)
    jobs_by_id = {j["id"]: j for j in jobs}

    changes = []
    for item in report_data["flagged"]:
        job_id = item["id"]
        if job_id not in jobs_by_id:
            continue

        our = item["our_timeline"]
        theirs = item["perplexity_timeline"]
        # Split the difference — don't fully trust either side
        new_timeline = round((our + theirs) / 2)

        if new_timeline != our:
            changes.append({
                "id": job_id,
                "title": item["title"],
                "old": f"~{our}",
                "new": f"~{new_timeline}",
                "reason": item["reason"],
            })

    if dry_run:
        print(f"DRY RUN: Would change {len(changes)} timelines:")
        for c in changes:
            print(f"  {c['title']}: {c['old']} → {c['new']}")
    else:
        for c in changes:
            job = jobs_by_id[c["id"]]
            job["timeline"] = c["new"]

        with open(source_file, "w") as f:
            json.dump(jobs, f, indent=2)
        print(f"Applied {len(changes)} timeline changes to {source_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "prepare":
        prepare(sys.argv[2] if len(sys.argv) > 2 else "data/jobs.json")
    elif cmd == "record":
        if len(sys.argv) < 4:
            print("Usage: python tools/timeline_fact_check.py record <sector_name> '<json>'")
            sys.exit(1)
        record(sys.argv[2], sys.argv[3])
    elif cmd == "status":
        status()
    elif cmd == "report":
        report()
    elif cmd == "apply":
        dry_run = "--dry-run" in sys.argv
        apply_fixes(dry_run)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
