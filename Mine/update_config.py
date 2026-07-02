import ast
import csv
import json
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.py")
CLEANED_ENTITIES_PATH = os.path.join(OUTPUT_DIR, "cleaned_entities.json")
REVIEW_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entity_type_review.csv")


def load_existing_overrides():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=CONFIG_PATH)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ENTITY_TYPE_OVERRIDES":
                    value = ast.literal_eval(node.value)
                    return set(value.keys())
    return set()


def main():
    if not os.path.exists(CLEANED_ENTITIES_PATH):
        print("No cleaned_entities.json found. Run aggregate_graph.py first.")
        return

    with open(CLEANED_ENTITIES_PATH, "r", encoding="utf-8") as f:
        entities = json.load(f)

    existing_keys = load_existing_overrides()
    review_rows = []
    for ent in entities:
        name = ent["entity"]
        if name in existing_keys:
            continue
        review_rows.append(
            {
                "ReviewStatus": "pending",
                "Entity": name,
                "SuggestedType": ent["type"],
                "Confidence": ent["confidence"],
                "AddToEntityTypeOverrides": "",
                "CorrectedType": "",
                "CanonicalEntity": "",
                "Notes": "",
            }
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
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
        writer.writerows(review_rows)

    print(
        f"Wrote {len(review_rows)} entity review candidates to {REVIEW_OUTPUT_PATH}. "
        "config.py was not modified."
    )


if __name__ == "__main__":
    main()
