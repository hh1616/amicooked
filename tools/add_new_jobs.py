"""One-off script to add 16 new jobs to jobs.json and re-sort by score."""
import json

JOBS_FILE = "data/jobs.json"

NEW_JOBS = [
    {
        "id": "paediatrician",
        "title": "Paediatrician",
        "score": 16,
        "verdict": "Rare",
        "verdictQuip": "AI's circling but hasn't landed.",
        "timeline": "~15",
        "timelineUnit": "YRS",
        "automatable": "18%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Physical examination of uncooperative toddlers", "quip": "good luck getting a two-year-old to hold still for a sensor"},
            {"text": "Developmental milestone assessment", "quip": None},
            {"text": "Communicating with anxious parents", "quip": None},
            {"text": "Reading nonverbal cues in kids who can't describe symptoms", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Growth chart tracking and flagging", "quip": "software already does this"},
            {"text": "Vaccination schedule management", "quip": None},
            {"text": "Clinical documentation", "quip": None}
        ],
        "searchTerms": ["pediatrician", "children's doctor", "child doctor", "kids doctor", "baby doctor", "child specialist"]
    },
    {
        "id": "housewife",
        "title": "Housewife",
        "score": 18,
        "verdict": "Rare",
        "verdictQuip": "AI's circling but hasn't landed.",
        "timeline": "~15",
        "timelineUnit": "YRS",
        "automatable": "20%",
        "pivotPotential": "MED",
        "savingGraces": [
            {"text": "Managing a household of unpredictable humans", "quip": "no algorithm survives a toddler meltdown at 6am"},
            {"text": "Emotional regulation and conflict mediation", "quip": None},
            {"text": "Physical caregiving for sick kids or elderly parents", "quip": None},
            {"text": "Real-time multitasking across competing demands", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Meal planning and grocery lists", "quip": "ChatGPT's been doing this since day one"},
            {"text": "Household budgeting", "quip": None},
            {"text": "Scheduling and calendar management", "quip": None}
        ],
        "searchTerms": ["stay-at-home mum", "stay-at-home mom", "stay-at-home parent", "homemaker", "sahm", "domestic worker", "stay at home mum", "stay at home mom", "stay at home parent"]
    },
    {
        "id": "lawyer",
        "title": "Lawyer",
        "score": 52,
        "verdict": "Half Baked",
        "verdictQuip": "it's a coin flip. better have a plan B.",
        "timeline": "~8",
        "timelineUnit": "YRS",
        "automatable": "44%",
        "pivotPotential": "MED",
        "savingGraces": [
            {"text": "Courtroom advocacy and persuasion", "quip": "judges still prefer humans who can read the room"},
            {"text": "Client counseling through emotional decisions", "quip": None},
            {"text": "Negotiation strategy under uncertainty", "quip": None},
            {"text": "Interpreting ambiguous case law", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Legal research and case discovery", "quip": "AI reads case law faster than any associate"},
            {"text": "Contract review and due diligence", "quip": None},
            {"text": "Document drafting from templates", "quip": None}
        ],
        "searchTerms": ["solicitor", "barrister", "attorney", "legal counsel", "legal advisor", "corporate lawyer", "criminal lawyer", "family lawyer", "litigation lawyer"]
    },
    {
        "id": "farmer",
        "title": "Farmer",
        "score": 25,
        "verdict": "Rare",
        "verdictQuip": "AI's circling but hasn't landed.",
        "timeline": "~12",
        "timelineUnit": "YRS",
        "automatable": "24%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Responding to unpredictable weather and terrain", "quip": "seasons don't follow a sprint schedule"},
            {"text": "Animal husbandry and welfare judgment", "quip": None},
            {"text": "Equipment repair in the field", "quip": None},
            {"text": "Land management across variable conditions", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Crop monitoring and yield prediction", "quip": "drones and satellites are already on it"},
            {"text": "Irrigation scheduling", "quip": None},
            {"text": "Market price tracking and sell timing", "quip": None}
        ],
        "searchTerms": ["grazier", "rancher", "crop farmer", "dairy farmer", "cattle farmer", "agriculture worker", "pastoralist", "station hand"]
    },
    {
        "id": "retail-sales-assistant",
        "title": "Retail Sales Assistant",
        "score": 62,
        "verdict": "Well Done",
        "verdictQuip": "the robots are warming up your seat.",
        "timeline": "~7",
        "timelineUnit": "YRS",
        "automatable": "58%",
        "pivotPotential": "MED",
        "savingGraces": [
            {"text": "Styling advice and personal recommendations", "quip": "algorithms suggest, but can't read your vibe"},
            {"text": "Handling difficult or emotional customers", "quip": None},
            {"text": "Visual merchandising and store layout", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Checkout and payment processing", "quip": "self-checkout says hi"},
            {"text": "Inventory checks and stock queries", "quip": None},
            {"text": "Product information lookups", "quip": None}
        ],
        "searchTerms": ["shop assistant", "retail worker", "sales associate", "store clerk", "shop worker", "retail associate", "sales clerk"]
    },
    {
        "id": "childcare-worker",
        "title": "Childcare Worker",
        "score": 10,
        "verdict": "Raw",
        "verdictQuip": "you're untouchable. for now.",
        "timeline": "~20",
        "timelineUnit": "YRS",
        "automatable": "8%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Supervising small children in chaotic environments", "quip": "a room of toddlers defeats any algorithm"},
            {"text": "Emotional co-regulation and attachment", "quip": None},
            {"text": "Nappy changes, feeding, and physical care", "quip": None},
            {"text": "Recognising developmental red flags", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Activity planning and curriculum prep", "quip": "Pinterest was already doing this"},
            {"text": "Parent communication updates", "quip": None},
            {"text": "Attendance tracking", "quip": None}
        ],
        "searchTerms": ["daycare worker", "early childhood educator", "ECE", "nursery worker", "creche worker", "child carer", "nanny", "au pair"]
    },
    {
        "id": "aged-care-worker",
        "title": "Aged Care Worker",
        "score": 12,
        "verdict": "Raw",
        "verdictQuip": "you're untouchable. for now.",
        "timeline": "~20",
        "timelineUnit": "YRS",
        "automatable": "10%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Physical assistance with mobility and personal care", "quip": "robots can't help someone shower with dignity"},
            {"text": "Companionship and emotional support", "quip": None},
            {"text": "Responding to falls and medical emergencies", "quip": None},
            {"text": "Managing dementia-related behaviours", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Medication reminders and scheduling", "quip": "apps already handle this"},
            {"text": "Care plan documentation", "quip": None},
            {"text": "Vitals monitoring", "quip": None}
        ],
        "searchTerms": ["elderly care worker", "nursing home worker", "care assistant", "personal care assistant", "PCA", "support worker", "home care worker", "aged care nurse"]
    },
    {
        "id": "security-guard",
        "title": "Security Guard",
        "score": 55,
        "verdict": "Half Baked",
        "verdictQuip": "it's a coin flip. better have a plan B.",
        "timeline": "~8",
        "timelineUnit": "YRS",
        "automatable": "48%",
        "pivotPotential": "MED",
        "savingGraces": [
            {"text": "Physical intervention and de-escalation", "quip": "cameras can watch but they can't tackle"},
            {"text": "Judgment calls in ambiguous situations", "quip": None},
            {"text": "Crowd management at live events", "quip": None}
        ],
        "gettingCooked": [
            {"text": "CCTV monitoring and anomaly detection", "quip": "AI never blinks"},
            {"text": "Access control and ID verification", "quip": None},
            {"text": "Patrol route logging", "quip": None}
        ],
        "searchTerms": ["security officer", "bouncer", "door staff", "loss prevention", "security personnel", "night watchman"]
    },
    {
        "id": "bus-driver",
        "title": "Bus Driver",
        "score": 45,
        "verdict": "Lightly Toasted",
        "verdictQuip": "some parts of your job are already on borrowed time.",
        "timeline": "~10",
        "timelineUnit": "YRS",
        "automatable": "42%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Navigating chaotic urban traffic in real time", "quip": "autonomous buses exist \u2014 in controlled loops"},
            {"text": "Passenger safety and de-escalation", "quip": None},
            {"text": "Adapting to roadworks, detours, and weather", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Fixed-route navigation", "quip": "GPS solved this decades ago"},
            {"text": "Fare collection", "quip": None},
            {"text": "Schedule adherence tracking", "quip": None}
        ],
        "searchTerms": ["coach driver", "transit driver", "public transport driver", "shuttle driver", "school bus driver"]
    },
    {
        "id": "cleaner",
        "title": "Cleaner",
        "score": 35,
        "verdict": "Lightly Toasted",
        "verdictQuip": "some parts of your job are already on borrowed time.",
        "timeline": "~12",
        "timelineUnit": "YRS",
        "automatable": "32%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Deep cleaning irregular spaces", "quip": "Roombas can't scrub a shower"},
            {"text": "Handling hazardous or biohazard materials", "quip": None},
            {"text": "Adapting to different layouts every shift", "quip": None},
            {"text": "Spotting maintenance issues while cleaning", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Floor vacuuming and mopping on flat surfaces", "quip": "robot vacuums already own this"},
            {"text": "Supply inventory tracking", "quip": None},
            {"text": "Scheduling and task checklists", "quip": None}
        ],
        "searchTerms": ["janitor", "custodian", "office cleaner", "commercial cleaner", "house cleaner", "domestic cleaner", "cleaning lady", "sanitation worker"]
    },
    {
        "id": "rideshare-driver",
        "title": "Rideshare Driver",
        "score": 58,
        "verdict": "Half Baked",
        "verdictQuip": "it's a coin flip. better have a plan B.",
        "timeline": "~8",
        "timelineUnit": "YRS",
        "automatable": "52%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Navigating unpredictable urban conditions", "quip": "self-driving still panics at construction zones"},
            {"text": "Passenger assistance and safety judgment", "quip": None},
            {"text": "Handling drunk, distressed, or difficult riders", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Route optimisation", "quip": "the app already tells you where to go"},
            {"text": "Fare calculation and surge pricing", "quip": None},
            {"text": "Ride matching and dispatch", "quip": None}
        ],
        "searchTerms": ["uber driver", "lyft driver", "taxi driver", "cab driver", "ola driver", "ride-hail driver", "private hire driver"]
    },
    {
        "id": "mining-worker",
        "title": "Mining Worker",
        "score": 40,
        "verdict": "Lightly Toasted",
        "verdictQuip": "some parts of your job are already on borrowed time.",
        "timeline": "~10",
        "timelineUnit": "YRS",
        "automatable": "38%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Underground work in unpredictable geology", "quip": "rocks don't follow a script"},
            {"text": "Emergency response in confined spaces", "quip": None},
            {"text": "Equipment operation in extreme conditions", "quip": None},
            {"text": "On-site safety judgment", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Autonomous haul trucks on surface mines", "quip": "Pilbara trucks already drive themselves"},
            {"text": "Drilling pattern optimisation", "quip": None},
            {"text": "Geological survey data processing", "quip": None}
        ],
        "searchTerms": ["miner", "mine worker", "FIFO worker", "underground miner", "open cut miner", "pit worker", "drill operator", "mining operator"]
    },
    {
        "id": "nail-technician",
        "title": "Nail Technician",
        "score": 16,
        "verdict": "Rare",
        "verdictQuip": "AI's circling but hasn't landed.",
        "timeline": "~15",
        "timelineUnit": "YRS",
        "automatable": "14%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Precision work on ten different-shaped fingers", "quip": "every hand is a different canvas"},
            {"text": "Client conversation and relationship building", "quip": None},
            {"text": "Custom nail art design on the spot", "quip": None},
            {"text": "Cuticle and skin care judgment", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Design inspiration and reference lookups", "quip": "Instagram already runs this"},
            {"text": "Appointment booking", "quip": None},
            {"text": "Inventory ordering", "quip": None}
        ],
        "searchTerms": ["nail artist", "manicurist", "nail tech", "pedicurist", "nail salon worker"]
    },
    {
        "id": "makeup-artist",
        "title": "Makeup Artist",
        "score": 18,
        "verdict": "Rare",
        "verdictQuip": "AI's circling but hasn't landed.",
        "timeline": "~15",
        "timelineUnit": "YRS",
        "automatable": "16%",
        "pivotPotential": "MED",
        "savingGraces": [
            {"text": "Application on real skin with real texture", "quip": "foundation doesn't apply itself \u2014 yet"},
            {"text": "Reading a client's features and bone structure", "quip": None},
            {"text": "Adapting to lighting conditions on set", "quip": None},
            {"text": "Calming nervous brides and performers", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Virtual try-on and colour matching", "quip": "AR filters are eating this alive"},
            {"text": "Product recommendation engines", "quip": None},
            {"text": "Tutorial content generation", "quip": None}
        ],
        "searchTerms": ["MUA", "beauty therapist", "cosmetologist", "beauty consultant", "bridal makeup artist", "film makeup artist", "special effects makeup"]
    },
    {
        "id": "electrical-engineer",
        "title": "Electrical Engineer",
        "score": 38,
        "verdict": "Lightly Toasted",
        "verdictQuip": "some parts of your job are already on borrowed time.",
        "timeline": "~10",
        "timelineUnit": "YRS",
        "automatable": "35%",
        "pivotPotential": "MED",
        "savingGraces": [
            {"text": "Designing systems for novel constraints", "quip": "every site is a new puzzle"},
            {"text": "On-site troubleshooting of complex installations", "quip": None},
            {"text": "Safety-critical judgment under regulation", "quip": None},
            {"text": "Cross-discipline coordination on builds", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Circuit simulation and modelling", "quip": "SPICE has been doing this for decades"},
            {"text": "CAD drafting of standard layouts", "quip": None},
            {"text": "Compliance documentation", "quip": None}
        ],
        "searchTerms": ["EE", "electronics engineer", "power engineer", "electrical designer", "circuit engineer", "power systems engineer"]
    },
    {
        "id": "primary-school-teacher",
        "title": "Primary School Teacher",
        "score": 12,
        "verdict": "Raw",
        "verdictQuip": "you're untouchable. for now.",
        "timeline": "~20",
        "timelineUnit": "YRS",
        "automatable": "10%",
        "pivotPotential": "LOW",
        "savingGraces": [
            {"text": "Managing a classroom of 25 seven-year-olds", "quip": "this is a superpower, not a job task"},
            {"text": "Emotional scaffolding and social skill development", "quip": None},
            {"text": "Recognising learning difficulties early", "quip": None},
            {"text": "Building trust with kids and parents", "quip": None}
        ],
        "gettingCooked": [
            {"text": "Lesson plan generation", "quip": "teachers already use ChatGPT for this"},
            {"text": "Marking standardised worksheets", "quip": None},
            {"text": "Report card comment writing", "quip": None}
        ],
        "searchTerms": ["elementary school teacher", "grade school teacher", "primary teacher", "year 1 teacher", "year 2 teacher", "year 3 teacher", "year 4 teacher", "year 5 teacher", "year 6 teacher"]
    }
]

def main():
    with open(JOBS_FILE) as f:
        jobs = json.load(f)

    existing_ids = {j["id"] for j in jobs}
    added = []
    skipped = []

    for new_job in NEW_JOBS:
        if new_job["id"] in existing_ids:
            skipped.append(new_job["id"])
        else:
            jobs.append(new_job)
            added.append(new_job["id"])

    # Sort by score ascending (matching existing order)
    jobs.sort(key=lambda j: j["score"])

    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"Added {len(added)} jobs: {', '.join(added)}")
    if skipped:
        print(f"Skipped {len(skipped)} (already exist): {', '.join(skipped)}")
    print(f"Total jobs: {len(jobs)}")

if __name__ == "__main__":
    main()
