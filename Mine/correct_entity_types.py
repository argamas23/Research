"""
Correct entity types using TextRazor NER results.

Parses all ner_results.txt files found under RESULTS_ROOT, builds a mapping
of entity -> best type with confidence/relevance scores, then updates
cleaned_entities.json and generates new ENTITY_TYPE_OVERRIDES for config.py.

New books added to Results/ are automatically picked up — no hardcoded paths.
"""

import json
import os
import re
import glob
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import RESULTS_ROOT, OUTPUT_DIR

CLEANED_ENTITIES_PATH = os.path.join(OUTPUT_DIR, "cleaned_entities.json")


def find_ner_files():
    """Auto-discover all ner_results.txt files under RESULTS_ROOT."""
    pattern = os.path.join(RESULTS_ROOT, "**", "ner_results.txt")
    return sorted(glob.glob(pattern, recursive=True))

# TextRazor Freebase category prefixes → graph entity types
CATEGORY_TO_TYPE = {
    # PERSON
    "/people/person": "PERSON",
    "/people/deceased_person": "PERSON",
    "/film/actor": "PERSON",
    "/music/artist": "PERSON",
    "/government/politician": "PERSON",
    "/book/author": "PERSON",
    "/military/military_person": "PERSON",
    "/royalty/monarch": "PERSON",
    "/royalty/noble_person": "PERSON",
    # LOCATION
    "/location/location": "LOCATION",
    "/location/country": "LOCATION",
    "/location/citytown": "LOCATION",
    "/location/administrative_division": "LOCATION",
    "/geography/river": "LOCATION",
    "/geography/lake": "LOCATION",
    "/geography/mountain": "LOCATION",
    "/geography/geographical_feature": "LOCATION",
    "/travel/travel_destination": "LOCATION",
    "/location/statistical_region": "LOCATION",
    "/location/hud_county_place": "LOCATION",
    "/protected_sites/listed_site": "LOCATION",
    "/architecture/building": "LOCATION",
    "/architecture/structure": "LOCATION",
    "/architecture/venue": "LOCATION",
    # GROUP
    "/people/ethnicity": "GROUP",
    "/people/family": "GROUP",
    "/people/group": "GROUP",
    "/organization/organization": "GROUP",
    "/government/government": "GROUP",
    "/military/military_unit": "GROUP",
    "/religion/religion": "GROUP",
    "/business/business_operation": "GROUP",
    # COMMODITY
    "/food/food": "COMMODITY",
    "/food/ingredient": "COMMODITY",
    "/biology/animal": "COMMODITY",
    "/biology/domesticated_animal": "COMMODITY",
    "/biology/organism": "COMMODITY",
    "/biology/plant": "COMMODITY",
    "/distilled_spirits/blended_spirit": "COMMODITY",
    "/chemistry/chemical_compound": "COMMODITY",
    "/medicine/drug": "COMMODITY",
    "/textiles/fiber": "COMMODITY",
    "/textiles/textile": "COMMODITY",
    "/award/award_discipline": "CONCEPT",
    # CONCEPT
    "/event/event": "CONCEPT",
    "/time/event": "CONCEPT",
    "/law/legal_subject": "CONCEPT",
    "/education/field_of_study": "CONCEPT",
    "/religion/religious_practice": "CONCEPT",
}

# Priority order for type resolution when multiple categories match
TYPE_PRIORITY = {"PERSON": 4, "LOCATION": 3, "GROUP": 2, "COMMODITY": 1, "CONCEPT": 0}

# Rule-based classification for entities not found in NER
# These are common-sense mappings for generic terms
MANUAL_TYPE_RULES = {
    # CONCEPT: abstract nouns, processes, states, temporal expressions
    "CONCEPT": [
        "a situation", "a trade", "agricultural cycle", "area", "at present",
        "baggage", "basis", "begar", "begar conscription", "cash dues",
        "changes", "clan deity", "demands", "deity", "deities",
        "divine functionaries", "donations", "facts", "having no credibility",
        "his patron god", "imprisoned", "land revenue", "land settlements",
        "local habitations", "migratory strategy", "natural products",
        "new law", "obstacles", "prior interventions", "produce",
        "productive resources", "products", "revenue demand",
        "special circumstances", "specimens", "storage facilities",
        "support", "surplus", "the corn", "throughout the year",
        "british rule",
    ],
    # GROUP: collective nouns, peoples, organizations
    "GROUP": [
        "british officers", "consumers", "drokpas", "gurkhas", "kanets",
        "khash-kanet peasantry", "khash-kanet peasants", "loaded men",
        "loggers", "outsiders", "pastoral groups", "pastoralists",
        "peasant family", "peasantry", "peasants", "servile groups",
        "the bethus", "the british", "the crown", "the khumri",
        "the raja", "the subbas", "wazeers", "women", "jada family",
    ],
    # LOCATION: places, geographical features
    "LOCATION": [
        "civilisational centres", "dabusun nor", "garu", "mahasu", "mandi",
        "marts", "monasteries", "pe customs house", "rampur", "tsakalho",
        "chasralu",
    ],
    # COMMODITY: goods, resources, plants
    "COMMODITY": [
        "european plant", "saffron",
    ],
    # PERSON: actual named individuals
    "PERSON": [
        "padam dev gautam", "strachey", "tika ruder sen", "bethus", "poorzee",
    ],
}


def parse_ner_file(filepath):
    """
    Parse a TextRazor ner_results.txt file.
    Returns dict: entity_name_lower -> list of (category, relevance, confidence)
    """
    entity_records = defaultdict(list)
    current_category = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("/"):
                current_category = line
            elif "Relevance" in line and current_category:
                match = re.match(
                    r"^(.*?)\s+\(Relevance ([\d.]+) \| Confidence ([\d.]+)\)", line
                )
                if match:
                    entity_name = match.group(1).strip()
                    relevance = float(match.group(2))
                    confidence = float(match.group(3))
                    entity_lower = entity_name.lower()
                    # Remove disambiguation suffixes like " (actor)"
                    entity_lower = re.sub(r"\s*\([^)]*\)\s*$", "", entity_lower).strip()
                    entity_records[entity_lower].append(
                        (current_category, relevance, confidence)
                    )
    return entity_records


def resolve_type(records):
    """
    Given a list of (category, relevance, confidence) for an entity,
    determine the best type and aggregate scores.
    """
    type_scores = defaultdict(lambda: {"relevance": 0.0, "confidence": 0.0, "count": 0})

    for category, relevance, confidence in records:
        # Match category to type using prefix matching
        matched_type = None
        for cat_prefix, entity_type in CATEGORY_TO_TYPE.items():
            if category.startswith(cat_prefix) or category == cat_prefix:
                matched_type = entity_type
                break

        # Broader prefix matching for categories not explicitly listed
        if matched_type is None:
            if category.startswith("/people"):
                matched_type = "PERSON"
            elif category.startswith("/location") or category.startswith("/geography"):
                matched_type = "LOCATION"
            elif category.startswith(("/organization", "/government", "/military")):
                matched_type = "GROUP"
            elif category.startswith(("/food", "/biology", "/textiles", "/chemistry")):
                matched_type = "COMMODITY"

        if matched_type:
            ts = type_scores[matched_type]
            ts["relevance"] = max(ts["relevance"], relevance)
            ts["confidence"] = max(ts["confidence"], confidence)
            ts["count"] += 1

    if not type_scores:
        return None, 0.0, 0.0

    # Pick the type with highest confidence, breaking ties by count then priority
    best_type = max(
        type_scores.keys(),
        key=lambda t: (
            type_scores[t]["confidence"],
            type_scores[t]["count"],
            TYPE_PRIORITY.get(t, 0),
        ),
    )
    return best_type, type_scores[best_type]["relevance"], type_scores[best_type]["confidence"]


def build_ner_lookup():
    """Parse all NER results files and build entity -> type lookup."""
    all_records = defaultdict(list)
    ner_files = find_ner_files()

    if not ner_files:
        print(f"  WARNING: No ner_results.txt found under {RESULTS_ROOT}")
        return {}

    for ner_path in ner_files:
        print(f"  Parsing: {ner_path}")
        records = parse_ner_file(ner_path)
        for entity, recs in records.items():
            all_records[entity].extend(recs)

    # Resolve each entity to its best type
    lookup = {}
    for entity, records in all_records.items():
        best_type, relevance, confidence = resolve_type(records)
        if best_type:
            lookup[entity] = {
                "type": best_type,
                "relevance": round(relevance, 4),
                "confidence": round(confidence, 4),
            }
    return lookup


def normalize_confidence(raw_confidence):
    """
    Normalize TextRazor confidence (which can be >1) to 0-1 range.
    Uses a sigmoid-like mapping.
    """
    if raw_confidence >= 10:
        return 1.0
    elif raw_confidence >= 5:
        return 0.95
    elif raw_confidence >= 2:
        return 0.9
    elif raw_confidence >= 1:
        return 0.85
    elif raw_confidence >= 0.5:
        return 0.7
    else:
        return 0.5


def main():
    print("Building NER lookup from TextRazor results...")
    ner_lookup = build_ner_lookup()
    print(f"  Found {len(ner_lookup)} entities in NER data.\n")

    # Load current entities
    with open(CLEANED_ENTITIES_PATH, "r", encoding="utf-8") as f:
        entities = json.load(f)

    # Build reverse lookup from manual rules
    manual_lookup = {}
    for mtype, names in MANUAL_TYPE_RULES.items():
        for n in names:
            manual_lookup[n] = mtype

    corrections = []
    unchanged = []
    not_found_in_ner = []

    for ent in entities:
        name = ent["entity"]
        current_type = ent["type"]
        current_conf = ent["confidence"]

        # First check manual override rules (highest priority for known misclassifications)
        if name in manual_lookup and current_conf <= 0.5:
            new_type = manual_lookup[name]
            new_conf = 0.8  # Manual rule confidence
            corrections.append({
                "entity": name,
                "old_type": current_type,
                "new_type": new_type,
                "old_confidence": current_conf,
                "new_confidence": new_conf,
                "ner_relevance": 0.0,
                "ner_raw_confidence": 0.0,
                "source": "manual_rule",
            })
            ent["type"] = new_type
            ent["confidence"] = new_conf
            ent["source"] = "manual_rule"
            continue

        if name in ner_lookup:
            ner_info = ner_lookup[name]
            ner_type = ner_info["type"]
            ner_conf = normalize_confidence(ner_info["confidence"])
            ner_rel = ner_info["relevance"]

            # Apply manual override if NER gives a clearly wrong type
            # (e.g., "women" → LOCATION from NER is wrong)
            if name in manual_lookup:
                ner_type = manual_lookup[name]
                ner_conf = max(ner_conf, 0.8)

            # Only override if:
            # 1. Current confidence is low (0.5 = default/unknown), or
            # 2. NER gives a different type with higher confidence
            should_correct = False
            if current_conf <= 0.5 and ner_conf > current_conf:
                should_correct = True
            elif ner_type != current_type and ner_conf > current_conf:
                should_correct = True

            if should_correct:
                corrections.append({
                    "entity": name,
                    "old_type": current_type,
                    "new_type": ner_type,
                    "old_confidence": current_conf,
                    "new_confidence": ner_conf,
                    "ner_relevance": ner_rel,
                    "ner_raw_confidence": ner_info["confidence"],
                    "source": "textrazor",
                })
                ent["type"] = ner_type
                ent["confidence"] = ner_conf
                ent["relevance"] = ner_rel
                ent["source"] = "textrazor_corrected"
            else:
                unchanged.append(name)
        else:
            if current_conf <= 0.5:
                not_found_in_ner.append(name)

    # Save corrected entities
    corrected_path = os.path.join(OUTPUT_DIR, "cleaned_entities.json")
    with open(corrected_path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)
    print(f"Updated {corrected_path}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"CORRECTION SUMMARY")
    print(f"{'='*60}")
    print(f"  Total entities:      {len(entities)}")
    print(f"  Corrected:           {len(corrections)}")
    print(f"  Unchanged:           {len(unchanged)}")
    print(f"  Not in NER (low conf): {len(not_found_in_ner)}")

    print(f"\n{'─'*60}")
    print("CORRECTIONS APPLIED:")
    print(f"{'─'*60}")
    for c in sorted(corrections, key=lambda x: x["entity"]):
        print(
            f"  {c['entity']:40s} {c['old_type']:10s} → {c['new_type']:10s} "
            f"(conf: {c['old_confidence']:.2f} → {c['new_confidence']:.2f}, "
            f"NER raw conf: {c['ner_raw_confidence']:.3f})"
        )

    if not_found_in_ner:
        print(f"\n{'─'*60}")
        print("NOT FOUND IN NER (still low confidence - need manual review):")
        print(f"{'─'*60}")
        for name in sorted(not_found_in_ner):
            print(f"  {name}")

    # Generate ENTITY_TYPE_OVERRIDES updates
    print(f"\n{'─'*60}")
    print("SUGGESTED config.py ENTITY_TYPE_OVERRIDES updates:")
    print(f"{'─'*60}")
    for c in sorted(corrections, key=lambda x: x["entity"]):
        print(f'    "{c["entity"]}": ("{c["new_type"]}", {c["new_confidence"]}),')

    # Save corrections log
    log_path = os.path.join(OUTPUT_DIR, "entity_corrections_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "corrections": corrections,
                "not_found_in_ner": not_found_in_ner,
                "total_entities": len(entities),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\nCorrections log saved to: {log_path}")


if __name__ == "__main__":
    main()
