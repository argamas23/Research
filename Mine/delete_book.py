from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path

from config import (
    BAD_PERSON_TOKENS,
    COLOR_BY_TYPE,
    COMMODITY_KEYWORDS,
    DEFAULT_COLOR,
    DEFAULT_SHAPE,
    ENTITY_ALIASES,
    ENTITY_TYPE_OVERRIDES,
    KEEP_ENTITY_TYPES,
    LOCATION_KEYWORDS,
    OUTPUT_DIR,
    PERSON_INDICATORS,
    RESEARCH_FOCUS_NODE,
    RESULTS_ROOT,
    SHAPE_BY_TYPE,
)

MINE_DIR = Path(__file__).resolve().parent
BASE_DIR = MINE_DIR.parent
CORPUS_DIR = BASE_DIR / "corpus"
HTML_PATHS = [MINE_DIR / "network_visualization.html", Path(OUTPUT_DIR) / "network_visualization.html"]


def norm(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return ENTITY_ALIASES.get(text.strip(" .,/\\'\""), text.strip(" .,/\\'\""))


def key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", norm(Path(text).stem)).strip("_")


def result_dirs_for(book: str) -> list[Path]:
    wanted = key(book)
    matches = []
    for path in Path(RESULTS_ROOT).iterdir():
        if path.is_dir() and (key(path.name) == wanted or key(path.name).startswith(wanted + "_")):
            matches.append(path)
    return sorted(matches)


def generated_files_for(book: str) -> list[Path]:
    stem = Path(book).stem
    return [CORPUS_DIR / f"{stem}.txt"]


def classify(entity: str) -> tuple[str, float]:
    if entity in ENTITY_TYPE_OVERRIDES:
        return ENTITY_TYPE_OVERRIDES[entity]
    words = set(re.findall(r"[a-z]+", entity))
    if words & BAD_PERSON_TOKENS:
        return "CONCEPT", 0.6
    if any(k in entity for k in COMMODITY_KEYWORDS):
        return "COMMODITY", 0.8
    if any(k in entity for k in LOCATION_KEYWORDS):
        return "LOCATION", 0.8
    if words & PERSON_INDICATORS:
        return "PERSON", 0.6
    return "CONCEPT", 0.5


def remaining_edges() -> tuple[dict[tuple[str, str], float], dict[tuple[str, str], set[str]], dict[tuple[str, str], set[str]]]:
    weights = defaultdict(float)
    relations = defaultdict(set)
    books = defaultdict(set)
    for csv_path in sorted(Path(RESULTS_ROOT).glob("**/*weighted*knowledge*graph*.csv")):
        book = csv_path.parent.name
        with csv_path.open(newline="", encoding="utf-8", errors="ignore") as f:
            for row in csv.DictReader(f):
                source, target = norm(row.get("Source", "")), norm(row.get("Target", ""))
                if not source or not target or source == target or "none" in (source, target):
                    continue
                try:
                    weight = float(row.get("Weight") or 1)
                except ValueError:
                    weight = 1.0
                relation = norm(row.get("Relation", "")).replace(" ", "_") or "related_to"
                edge = (source, target)
                weights[edge] += weight
                relations[edge].add(relation)
                books[edge].add(book)
    return weights, relations, books


def write_graph_outputs() -> None:
    weights, relations, books = remaining_edges()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(Path(OUTPUT_DIR) / "aggregated_edges.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target", "TotalWeight", "Relations", "Books"])
        for (source, target), weight in sorted(weights.items(), key=lambda item: -item[1]):
            writer.writerow([source, target, weight, "|".join(sorted(relations[(source, target)])), "|".join(sorted(books[(source, target)]))])

    nodes = sorted({node for edge in weights for node in edge})
    degree = defaultdict(int)
    weighted_degree = defaultdict(float)
    for (source, target), weight in weights.items():
        degree[source] += 1
        degree[target] += 1
        weighted_degree[source] += weight
        weighted_degree[target] += weight

    entities = []
    node_items = []
    for node in nodes:
        node_type, confidence = classify(node)
        if node_type not in KEEP_ENTITY_TYPES:
            node_type = "CONCEPT"
        entities.append({"entity": node, "type": node_type, "confidence": confidence})
        size = 10 + math.sqrt(max(weighted_degree[node], 1)) * 3 + math.sqrt(max(degree[node], 1)) * 2
        title = f"<strong>{node}</strong><br>Type: {node_type}<br>Degree: {degree[node]}<br>Weighted degree: {weighted_degree[node]:.1f}"
        item = {
            "id": node,
            "label": node,
            "type": node_type,
            "color": COLOR_BY_TYPE.get(node_type, DEFAULT_COLOR),
            "shape": SHAPE_BY_TYPE.get(node_type, DEFAULT_SHAPE),
            "size": size,
            "weight": weighted_degree[node],
            "degree": degree[node],
            "core": degree[node] >= 3,
            "title": title,
        }
        if RESEARCH_FOCUS_NODE in node:
            item["color"] = "#ffcc00"
            item["font"] = {"color": "#d62728", "size": 14, "bold": True}
        node_items.append(item)

    edge_items = []
    for i, ((source, target), weight) in enumerate(sorted(weights.items(), key=lambda item: -item[1])):
        rels = sorted(relations[(source, target)])
        edge_items.append({
            "id": f"e{i}",
            "from": source,
            "to": target,
            "label": rels[0],
            "relation": rels[0],
            "width": max(1, min(8, weight)),
            "weight": weight,
            "books": sorted(books[(source, target)]),
            "arrows": "to",
            "title": f"{source} -> {target}<br>Relation: {rels[0]}<br>Weight: {weight:.1f}<br>Books: {', '.join(sorted(books[(source, target)]))}",
        })

    with open(Path(OUTPUT_DIR) / "cleaned_entities.json", "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)
    shutil.copyfile(Path(OUTPUT_DIR) / "aggregated_edges.csv", Path(OUTPUT_DIR) / "cleaned_aggregated_edges.csv")

    nodes_json = json.dumps(node_items, ensure_ascii=False)
    edges_json = json.dumps(edge_items, ensure_ascii=False)
    for html_path in HTML_PATHS:
        html = html_path.read_text(encoding="utf-8")
        html = re.sub(r'(<script type="application/json" id="graph-nodes-data">)\s*\n.*?\n(</script><!-- GRAPH_NODES_END -->)', rf"\1\n{nodes_json}\n\2", html, flags=re.S)
        html = re.sub(r'(<script type="application/json" id="graph-edges-data">)\s*\n.*?\n(</script><!-- GRAPH_EDGES_END -->)', rf"\1\n{edges_json}\n\2", html, flags=re.S)
        html_path.write_text(html, encoding="utf-8")


def delete_book(book: str, dry_run: bool = False) -> list[Path]:
    targets = [p for p in generated_files_for(book) if p.exists()] + result_dirs_for(book)
    if not targets:
        raise SystemExit(f"No generated files found for {book!r}")
    for path in targets:
        print(("Would delete: " if dry_run else "Deleting: ") + str(path))
        if dry_run:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    if not dry_run:
        write_graph_outputs()
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete one book's generated data and rebuild graph outputs from remaining books.")
    parser.add_argument("--book", required=True, help="Book file/name, e.g. 1897.pdf or Becoming_India.pdf")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    deleted = delete_book(args.book, args.dry_run)
    print(f"{'Matched' if args.dry_run else 'Deleted'} {len(deleted)} path(s).")
    if not args.dry_run:
        print("Rebuilt graph outputs from remaining Mine/Results books.")


if __name__ == "__main__":
    main()
