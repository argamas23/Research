"""
Correct entity types using TextRazor NER results.

Parses all ner_results.txt files found under RESULTS_ROOT, builds a mapping
of entity -> best type with confidence/relevance scores, then updates
cleaned_entities.json and writes entity_type_review.csv.

New books added to Results/ are automatically picked up — no hardcoded paths.
"""

from __future__ import annotations

import json
import os
import re
import glob
import shutil
import logging
import argparse
import csv
from collections import defaultdict
from datetime import datetime
from math import exp
from typing import Optional

import sys

MINE_DIR = os.path.dirname(__file__)
RESULTS_ROOT = os.path.join(MINE_DIR, "Results")
OUTPUT_DIR = os.path.join(MINE_DIR, "outputs")
CLEANED_ENTITIES_PATH = os.path.join(OUTPUT_DIR, "cleaned_entities.json")
REVIEW_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entity_type_review.csv")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def find_ner_files() -> list[str]:
    """Auto-discover all ner_results.txt files under RESULTS_ROOT."""
    pattern = os.path.join(RESULTS_ROOT, "**", "ner_results.txt")
    return sorted(glob.glob(pattern, recursive=True))


# Mapping from Freebase category prefix → graph entity type.
# Used as a fallback for categories NOT listed in Selected_Topics.txt.
_EXTRA_CATEGORY_MAPPINGS = {
    "/people/deceased_person": "PERSON",
    "/film/actor": "PERSON",
    "/music/artist": "PERSON",
    "/government/politician": "PERSON",
    "/book/author": "PERSON",
    "/military/military_person": "PERSON",
    "/royalty/monarch": "PERSON",
    "/royalty/noble_person": "PERSON",
    "/location/statistical_region": "LOCATION",
    "/location/hud_county_place": "LOCATION",
    "/protected_sites/listed_site": "LOCATION",
    "/architecture/venue": "LOCATION",
    "/people/family": "GROUP",
    "/people/group": "GROUP",
    "/government/government": "GROUP",
    "/military/military_unit": "GROUP",
    "/business/business_operation": "GROUP",
    "/biology/domesticated_animal": "COMMODITY",
    "/biology/organism": "COMMODITY",
    "/distilled_spirits/blended_spirit": "COMMODITY",
    "/chemistry/chemical_compound": "COMMODITY",
    "/medicine/drug": "COMMODITY",
    "/award/award_discipline": "CONCEPT",
    "/time/event": "CONCEPT",
    "/law/legal_subject": "CONCEPT",
    "/education/field_of_study": "CONCEPT",
}

# Rules to derive entity type from a Freebase category path.
# Order matters — first match wins.
_PREFIX_TYPE_RULES: list[tuple[tuple[str, ...], str]] = [
    # PERSON
    (("/people/person",), "PERSON"),
    (("/religion/religious_leader",), "PERSON"),
    # LOCATION
    (("/location/", "/geography/", "/geology/",
      "/architecture/building", "/architecture/structure",
      "/meteorology/", "/metropolitan_transit/",
      "/government/governmental_jurisdiction", "/government/political_district",
      "/religion/monastery", "/religion/place_of_worship",
      "/transportation/", "/rail/", "/travel/transport_terminus",
      "/travel/travel_destination", "/business/business_location"), "LOCATION"),
    # GROUP
    (("/organization/", "/people/ethnicity",), "GROUP"),
    # COMMODITY
    (("/food/", "/biology/", "/fashion/", "/textiles/",
      "/business/consumer_product", "/business/product_category",
      "/business/product_ingredient", "/business/product_line",
      "/economy/livestock", "/boats/ship_type"), "COMMODITY"),
    # CONCEPT
    (("/event/", "/people/profession", "/religion/religious_practice",
      "/religion/religion", "/travel/transportation_mode"), "CONCEPT"),
]


def _infer_type_from_category(category: str) -> Optional[str]:
    """Derive entity type from a single Freebase category path using prefix rules."""
    for prefixes, entity_type in _PREFIX_TYPE_RULES:
        for prefix in prefixes:
            if category == prefix or category.startswith(prefix):
                return entity_type
    return None


def load_selected_topics(path: Optional[str] = None) -> dict[str, str]:
    """
    Load Selected_Topics.txt and map each topic to an entity type.

    Returns dict: category_path -> entity_type (e.g., "/food/food" -> "COMMODITY")
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "Selected_Topics.txt")

    topic_type_map: dict[str, str] = {}
    if not os.path.exists(path):
        logger.warning("Selected_Topics.txt not found at %s", path)
        return topic_type_map

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            topic = line.strip()
            if not topic or not topic.startswith("/"):
                continue
            inferred = _infer_type_from_category(topic)
            if inferred:
                topic_type_map[topic] = inferred
            else:
                logger.debug("Could not map topic to type: %s", topic)

    return topic_type_map


def build_category_to_type() -> dict[str, str]:
    """
    Build the unified category → type mapping by merging:
      1. Selected_Topics.txt (domain-relevant, auto-mapped)
      2. _EXTRA_CATEGORY_MAPPINGS (hardcoded extras for categories not in Selected_Topics)

    This means adding a new topic to Selected_Topics.txt automatically extends
    the entity classification without touching code.
    """
    mapping = load_selected_topics()
    # Layer extras underneath (don't overwrite topics-derived mappings)
    for cat, etype in _EXTRA_CATEGORY_MAPPINGS.items():
        mapping.setdefault(cat, etype)
    logger.info("  Category→Type mapping: %d entries (%d from Selected_Topics)",
                len(mapping), len(mapping) - len(_EXTRA_CATEGORY_MAPPINGS))
    return mapping


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


def parse_ner_file(filepath: str) -> dict[str, list[tuple[str, float, float]]]:
    """
    Parse a TextRazor ner_results.txt file.
    Returns dict: entity_name_lower -> list of (category, relevance, confidence)
    """
    entity_records: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    current_category: Optional[str] = None

    try:
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
    except OSError as e:
        logger.warning("Could not read %s: %s", filepath, e)

    return entity_records


def resolve_type(
    records: list[tuple[str, float, float]],
    category_map: dict[str, str],
) -> tuple[Optional[str], float, float]:
    """
    Given a list of (category, relevance, confidence) for an entity,
    determine the best type and aggregate scores.

    Uses `category_map` (built from Selected_Topics + extras) for exact matches,
    then falls back to prefix-based inference.
    """
    type_scores: dict[str, dict] = defaultdict(lambda: {"relevance": 0.0, "confidence": 0.0, "count": 0})

    for category, relevance, confidence in records:
        # 1. Exact match in unified category map
        matched_type = category_map.get(category)

        # 2. Prefix match against the map keys
        if matched_type is None:
            for cat_prefix, entity_type in category_map.items():
                if category.startswith(cat_prefix):
                    matched_type = entity_type
                    break

        # 3. Fallback: infer from prefix rules (catches categories not in map)
        if matched_type is None:
            matched_type = _infer_type_from_category(category)

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


def build_ner_lookup() -> dict[str, dict]:
    """Parse all NER results files and build entity -> type lookup."""
    all_records: dict[str, list[tuple[str, float, float]]] = defaultdict(list)
    ner_files = find_ner_files()

    if not ner_files:
        logger.warning("No ner_results.txt found under %s", RESULTS_ROOT)
        return {}

    for ner_path in ner_files:
        logger.info("  Parsing: %s", ner_path)
        records = parse_ner_file(ner_path)
        for entity, recs in records.items():
            # Deduplicate: skip records already accumulated for this entity
            existing = set(all_records[entity])
            all_records[entity].extend(r for r in recs if r not in existing)

    # Build the category→type mapping from Selected_Topics + extras
    category_map = build_category_to_type()

    # Resolve each entity to its best type
    lookup: dict[str, dict] = {}
    for entity, records in all_records.items():
        best_type, relevance, confidence = resolve_type(records, category_map)
        if best_type:
            lookup[entity] = {
                "type": best_type,
                "relevance": round(relevance, 4),
                "confidence": round(confidence, 4),
            }
    return lookup


def normalize_confidence(raw_confidence: float) -> float:
    """
    Normalize TextRazor confidence (which can be >1) to 0-1 range.
    Uses sigmoid σ(k·x) with k=0.8, mapping 0→0.50, 1→0.69, 5→0.98.
    """
    return round(1.0 / (1.0 + exp(-0.8 * raw_confidence)), 4)


def _backup_file(path: str) -> Optional[str]:
    """Create a timestamped backup of a file. Returns backup path or None on failure."""
    if not os.path.exists(path):
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{path}.{timestamp}.bak"
    try:
        shutil.copy2(path, backup_path)
        logger.info("Backup created: %s", backup_path)
        return backup_path
    except OSError as e:
        logger.warning("Could not create backup for %s: %s", path, e)
        return None


def write_entity_review(entities: list[dict]) -> None:
    manual_names = {
        name.lower()
        for names in MANUAL_TYPE_RULES.values()
        for name in names
    }
    rows = [
        {
            "ReviewStatus": "pending",
            "Entity": ent.get("entity", ""),
            "SuggestedType": ent.get("type", ""),
            "Confidence": ent.get("confidence", ""),
            "AddToEntityTypeOverrides": "",
            "CorrectedType": "",
            "CanonicalEntity": "",
            "Notes": "",
        }
        for ent in entities
        if ent.get("entity", "").lower() not in manual_names
    ]
    with open(REVIEW_OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "ReviewStatus",
            "Entity",
            "SuggestedType",
            "Confidence",
            "AddToEntityTypeOverrides",
            "CorrectedType",
            "CanonicalEntity",
            "Notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Entity review saved to: %s", REVIEW_OUTPUT_PATH)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Correct entity types using TextRazor NER results."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview corrections without writing any files.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable DEBUG-level logging."
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.dry_run:
        logger.info("DRY-RUN mode: no files will be written.")

    logger.info("Building NER lookup from TextRazor results...")
    ner_lookup = build_ner_lookup()
    logger.info("Found %d entities in NER data.", len(ner_lookup))

    # Load current entities
    try:
        with open(CLEANED_ENTITIES_PATH, "r", encoding="utf-8") as f:
            entities = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error("Failed to load %s: %s", CLEANED_ENTITIES_PATH, e)
        sys.exit(1)

    # Build case-insensitive reverse lookup from manual rules
    manual_lookup: dict[str, str] = {
        n.lower(): mtype
        for mtype, names in MANUAL_TYPE_RULES.items()
        for n in names
    }

    corrections = []
    unchanged = []
    not_found_in_ner = []

    for ent in entities:
        name: str = ent.get("entity", "")
        current_type: str = ent.get("type", "UNKNOWN")
        current_conf: float = ent.get("confidence", 0.0)
        name_lower = name.lower()

        # Skip entities already corrected in a previous run (idempotency)
        if ent.get("source") in ("manual_rule", "textrazor_corrected"):
            unchanged.append(name)
            continue

        # First check manual override rules (highest priority for known misclassifications)
        if name_lower in manual_lookup and current_conf <= 0.5:
            new_type = manual_lookup[name_lower]
            new_conf = 0.8
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
            if not args.dry_run:
                ent["type"] = new_type
                ent["confidence"] = new_conf
                ent["source"] = "manual_rule"
            continue

        if name_lower in ner_lookup:
            ner_info = ner_lookup[name_lower]
            ner_type = ner_info["type"]
            ner_conf = normalize_confidence(ner_info["confidence"])
            ner_rel = ner_info["relevance"]

            # Apply manual override if NER gives a clearly wrong type
            # (e.g., "women" → LOCATION from NER is wrong)
            if name_lower in manual_lookup:
                ner_type = manual_lookup[name_lower]
                ner_conf = max(ner_conf, 0.8)

            should_correct = (current_conf <= 0.5 and ner_conf > current_conf) or (
                ner_type != current_type and ner_conf > current_conf
            )

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
                if not args.dry_run:
                    ent["type"] = ner_type
                    ent["confidence"] = ner_conf
                    ent["relevance"] = ner_rel
                    ent["source"] = "textrazor_corrected"
            else:
                unchanged.append(name)
        else:
            if current_conf <= 0.5:
                not_found_in_ner.append(name)

    # --- Output ---
    sep = "=" * 60
    thin = "─" * 60
    logger.info("\n%s", sep)
    logger.info("CORRECTION SUMMARY")
    logger.info(sep)
    logger.info("  Total entities:        %d", len(entities))
    logger.info("  Corrected:             %d", len(corrections))
    logger.info("  Unchanged / skipped:   %d", len(unchanged))
    logger.info("  Not in NER (low conf): %d", len(not_found_in_ner))

    logger.info("\n%s", thin)
    logger.info("CORRECTIONS APPLIED:")
    logger.info(thin)
    for c in sorted(corrections, key=lambda x: x["entity"]):
        logger.info(
            "  %-40s %-10s → %-10s (conf: %.2f → %.2f, NER raw conf: %.3f)",
            c["entity"], c["old_type"], c["new_type"],
            c["old_confidence"], c["new_confidence"], c["ner_raw_confidence"],
        )

    if not_found_in_ner:
        logger.info("\n%s", thin)
        logger.info("NOT FOUND IN NER (still low confidence - need manual review):")
        logger.info(thin)
        for n in sorted(not_found_in_ner):
            logger.info("  %s", n)

    if args.dry_run:
        logger.info("\nDRY-RUN complete. No files were written.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save corrected entities (backup first, then atomic write)
    _backup_file(CLEANED_ENTITIES_PATH)
    tmp_path = CLEANED_ENTITIES_PATH + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(entities, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, CLEANED_ENTITIES_PATH)
        logger.info("Updated %s", CLEANED_ENTITIES_PATH)
    except OSError as e:
        logger.error("Failed to write %s: %s", CLEANED_ENTITIES_PATH, e)
        sys.exit(1)

    # Save corrections log
    log_path = os.path.join(OUTPUT_DIR, "entity_corrections_log.json")
    try:
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
        logger.info("Corrections log saved to: %s", log_path)
    except OSError as e:
        logger.error("Failed to write corrections log: %s", e)

    write_entity_review(entities)


if __name__ == "__main__":
    main()
