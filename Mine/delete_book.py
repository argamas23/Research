from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

MINE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = MINE_DIR / "outputs"
RESULTS_ROOT = MINE_DIR / "Results"
HTML_PATHS = [
    MINE_DIR / "network_visualization.html",
    OUTPUT_DIR / "network_visualization.html",
]


def norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", Path(text).stem.lower()).strip("_")


def result_dirs_for(book: str) -> list[Path]:
    wanted = norm_key(book)
    return sorted(
        path
        for path in RESULTS_ROOT.iterdir()
        if path.is_dir()
        and (norm_key(path.name) == wanted or norm_key(path.name).startswith(wanted + "_"))
    )


def graph_book_name(path: Path) -> str:
    return re.sub(r"_\d{8}_\d{6}$", "", path.name)


def read_html_data(html: str, data_id: str) -> list[dict]:
    match = re.search(
        rf'<script type="application/json" id="{data_id}">\s*\n(.*?)\n</script><!--',
        html,
        re.S,
    )
    if not match:
        raise SystemExit(f"Could not find {data_id} in network visualization HTML.")
    return json.loads(match.group(1))


def replace_html_data(html: str, data_id: str, rows: list[dict]) -> str:
    payload = json.dumps(rows, ensure_ascii=False)
    return re.sub(
        rf'(<script type="application/json" id="{data_id}">)\s*\n.*?\n(</script><!-- [A-Z_]+_END -->)',
        rf"\1\n{payload}\n\2",
        html,
        flags=re.S,
    )


def filter_graph_outputs(deleted_books: set[str]) -> None:
    html = HTML_PATHS[0].read_text(encoding="utf-8")
    nodes = read_html_data(html, "graph-nodes-data")
    edges = read_html_data(html, "graph-edges-data")

    kept_edges = []
    for edge in edges:
        books = [book for book in edge.get("books", []) if book not in deleted_books]
        if not books:
            continue
        edge["books"] = books
        kept_edges.append(edge)

    used_nodes = {edge["from"] for edge in kept_edges} | {edge["to"] for edge in kept_edges}
    degree = defaultdict(int)
    weight = defaultdict(float)
    for edge in kept_edges:
        edge_weight = float(edge.get("weight") or 1)
        degree[edge["from"]] += 1
        degree[edge["to"]] += 1
        weight[edge["from"]] += edge_weight
        weight[edge["to"]] += edge_weight

    kept_nodes = []
    for node in nodes:
        if node["id"] not in used_nodes:
            continue
        node["degree"] = degree[node["id"]]
        node["weight"] = weight[node["id"]]
        node["core"] = node["degree"] >= 3
        kept_nodes.append(node)

    for html_path in HTML_PATHS:
        html = html_path.read_text(encoding="utf-8")
        html = replace_html_data(html, "graph-nodes-data", kept_nodes)
        html = replace_html_data(html, "graph-edges-data", kept_edges)
        html_path.write_text(html, encoding="utf-8")

    with open(OUTPUT_DIR / "cleaned_entities.json", "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "entity": node["id"],
                    "type": node.get("type", "CONCEPT"),
                    "confidence": 1.0 if node.get("core") else 0.5,
                }
                for node in kept_nodes
            ],
            f,
            indent=2,
            ensure_ascii=False,
        )

    with open(OUTPUT_DIR / "cleaned_aggregated_edges.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target", "MappedRelation", "Weight", "RawRelations", "SourceType", "TargetType", "Books", "Evidence"])
        type_by_node = {node["id"]: node.get("type", "") for node in kept_nodes}
        for edge in kept_edges:
            writer.writerow([
                edge["from"],
                edge["to"],
                edge.get("relation", ""),
                edge.get("weight", 1),
                edge.get("label", ""),
                type_by_node.get(edge["from"], ""),
                type_by_node.get(edge["to"], ""),
                "|".join(edge.get("books", [])),
                "",
            ])


def delete_book(book: str, dry_run: bool = False) -> list[Path]:
    result_dirs = result_dirs_for(book)
    targets = result_dirs
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
        deleted_books = {path.name for path in result_dirs} | {graph_book_name(path) for path in result_dirs}
        filter_graph_outputs(deleted_books)
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Delete one book's generated data and remove it from the visible graph."
    )
    parser.add_argument("--book", required=True, help="Book file/name, e.g. 1897.pdf or Becoming_India.pdf")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    deleted = delete_book(args.book, args.dry_run)
    print(f"{'Matched' if args.dry_run else 'Deleted'} {len(deleted)} path(s).")
    if not args.dry_run:
        print("Removed the book from the visible network graph.")


if __name__ == "__main__":
    main()
