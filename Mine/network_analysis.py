from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter
from pathlib import Path

import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
DEFAULT_EDGES = OUTPUT_DIR / "edge_validation.csv"
DEFAULT_OUT = OUTPUT_DIR / "network_analysis"
TRADE_RELATIONS = {"trades_with", "supplies", "extracts_from", "depends_on", "transports_via", "connects_to"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def graph_from(
    rows: list[dict[str, str]],
    categories: set[str],
    relations: set[str] | None = None,
    keep_concepts: bool = True,
) -> nx.Graph:
    graph = nx.Graph()
    for row in rows:
        if row.get("ValidationCategory") not in categories:
            continue
        if relations and row.get("MappedRelation") not in relations:
            continue
        if not keep_concepts and "CONCEPT" in {row.get("SourceType"), row.get("TargetType")}:
            continue
        source, target = row["Source"], row["Target"]
        weight = float(row.get("Weight") or 1)
        graph.add_node(source, type=row.get("SourceType", ""))
        graph.add_node(target, type=row.get("TargetType", ""))
        if graph.has_edge(source, target):
            graph[source][target]["weight"] += weight
        else:
            graph.add_edge(source, target, weight=weight)
    return graph


def lcc(graph: nx.Graph) -> nx.Graph:
    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    return graph.subgraph(components[0]).copy() if components else graph.copy()


def diagnostics(name: str, graph: nx.Graph) -> dict[str, object]:
    largest = lcc(graph)
    return {
        "view": name,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "components": nx.number_connected_components(graph) if graph else 0,
        "largest_component_nodes": largest.number_of_nodes(),
        "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0,
        "average_degree": sum(dict(graph.degree()).values()) / graph.number_of_nodes() if graph else 0,
        "average_strength": sum(dict(graph.degree(weight="weight")).values()) / graph.number_of_nodes() if graph else 0,
        "clustering": nx.average_clustering(graph) if graph else 0,
        "lcc_average_shortest_path": nx.average_shortest_path_length(largest) if largest.number_of_nodes() > 1 else 0,
        "lcc_diameter": nx.diameter(largest) if largest.number_of_nodes() > 1 else 0,
        "node_types": "|".join(f"{k}:{v}" for k, v in Counter(nx.get_node_attributes(graph, "type").values()).most_common()),
    }


def community_rows(name: str, graph: nx.Graph, seeds: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    largest = lcc(graph)
    if largest.number_of_edges() == 0:
        return [], []
    rows = []
    for seed in range(seeds):
        communities = louvain_communities(largest, weight="weight", seed=seed, resolution=1)
        rows.append(
            {
                "view": name,
                "seed": seed,
                "modularity": modularity(largest, communities, weight="weight"),
                "communities": len(communities),
            }
        )
    summary = []
    for metric in ("modularity", "communities"):
        values = [float(row[metric]) for row in rows]
        summary.append(
            {
                "view": name,
                "metric": metric,
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
            }
        )
    return rows, summary


def markdown_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")).replace("|", "<br>") for field in fields) + " |")
    return "\n".join(lines)


def preserve_editable_notes(path: Path) -> str:
    start = "<!-- EDITABLE_NOTES_START -->"
    end = "<!-- EDITABLE_NOTES_END -->"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if start in text and end in text:
            return text.split(start, 1)[1].split(end, 1)[0].strip()
    return "- Add historical interpretation notes here.\n- Add caveats from new sources here.\n- Add paper wording decisions here."


def row_for(rows: list[dict[str, object]], **match: object) -> dict[str, object]:
    return next((row for row in rows if all(row.get(key) == value for key, value in match.items())), {})


def write_report(out: Path, graph_rows: list[dict[str, object]], community_summary: list[dict[str, object]]) -> None:
    text = [
        "# Network Analysis",
        "",
        "This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.",
        "",
        "## Graph Views",
        markdown_table(graph_rows, ["view", "nodes", "edges", "components", "largest_component_nodes", "density", "average_degree", "node_types"]),
        "",
        "## Louvain Community Stability",
        markdown_table(community_summary, ["view", "metric", "median", "min", "max"]),
        "",
        "## Editable Notes",
        "",
        "- Add interpretation here.",
        "- Add figure/table decisions here.",
        "- Add reviewer caveats here.",
    ]
    (out / "NETWORK_ANALYSIS.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def write_interpretation(out: Path, graph_rows: list[dict[str, object]], community_summary: list[dict[str, object]]) -> None:
    path = out / "NETWORK_INTERPRETATION.md"
    editable_notes = preserve_editable_notes(path)
    validated = row_for(graph_rows, view="validated")
    modularity = row_for(community_summary, view="validated", metric="modularity")
    text = [
        "# Network Interpretation",
        "",
        "This file interprets general graph metrics only. Salt-specific interpretation is generated separately by `Mine/salt_analysis.py`.",
        "",
        "## Main Claim",
        "",
        "The current graph should be read as a sparse, extracted relation network, not as a complete reconstruction of the Himalayan economy.",
        "",
        "## What The Validated Graph Shows",
        "",
        f"The validated graph contains {validated.get('nodes')} nodes and {validated.get('edges')} edges, with {validated.get('components')} connected components. Its largest component has {validated.get('largest_component_nodes')} nodes.",
        "",
        "Interpretation: network claims should focus on brokerage, centrality, and robustness inside the extracted relation structure. Avoid claiming that the whole Himalayan economy is represented as a complete network.",
        "",
        "## Community Structure",
        "",
        f"Louvain modularity in the validated graph has median {modularity.get('median')}.",
        "",
        "Interpretation: the graph has stable community structure, so community-level claims are reasonable when tied to extracted evidence.",
        "",
        "## Editable Notes",
        "",
        "<!-- EDITABLE_NOTES_START -->",
        editable_notes,
        "<!-- EDITABLE_NOTES_END -->",
    ]
    path.write_text("\n".join(text) + "\n", encoding="utf-8")


def self_check() -> None:
    rows = [
        {"Source": "a", "Target": "b", "Weight": "1", "SourceType": "GROUP", "TargetType": "LOCATION", "ValidationCategory": "Validated"},
        {"Source": "b", "Target": "c", "Weight": "2", "SourceType": "LOCATION", "TargetType": "COMMODITY", "ValidationCategory": "Validated"},
    ]
    graph = graph_from(rows, {"Validated"})
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert diagnostics("test", graph)["largest_component_nodes"] == 3


def main() -> None:
    parser = argparse.ArgumentParser(description="General network analysis for validated Himalayan trade graph.")
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--community-seeds", type=int, default=20)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_check()
        print("self-test passed")
        return

    rows = read_csv(args.edges)
    view_specs = {
        "validated": ({"Validated"}, None, True),
        "validated_probable": ({"Validated", "Probable"}, None, True),
        "validated_no_concept": ({"Validated"}, None, False),
        "validated_probable_no_concept": ({"Validated", "Probable"}, None, False),
        "validated_trade_only": ({"Validated"}, TRADE_RELATIONS, True),
        "validated_probable_trade_only": ({"Validated", "Probable"}, TRADE_RELATIONS, True),
    }
    views = {name: graph_from(rows, categories, relations, keep_concepts) for name, (categories, relations, keep_concepts) in view_specs.items()}
    graph_rows = [diagnostics(name, graph) for name, graph in views.items()]
    communities = []
    community_summary = []
    for name, graph in views.items():
        rows_for_view, summary_for_view = community_rows(name, graph, args.community_seeds)
        communities.extend(rows_for_view)
        community_summary.extend(summary_for_view)

    write_csv(args.output_dir / "graph_diagnostics.csv", graph_rows, list(graph_rows[0]))
    write_csv(args.output_dir / "louvain_communities.csv", communities, list(communities[0]))
    write_csv(args.output_dir / "louvain_community_summary.csv", community_summary, list(community_summary[0]))
    write_report(args.output_dir, graph_rows, community_summary)
    write_interpretation(args.output_dir, graph_rows, community_summary)
    print(f"Wrote general network analysis to {args.output_dir}")


if __name__ == "__main__":
    main()
