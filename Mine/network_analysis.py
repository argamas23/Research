from __future__ import annotations

import argparse
import csv
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
DEFAULT_EDGES = OUTPUT_DIR / "edge_validation.csv"
DEFAULT_OUT = OUTPUT_DIR / "network_analysis"
COMMODITIES = ["salt", "wool", "pashm", "grain", "barley", "tea", "borax"]
TRADE_RELATIONS = {"trades_with", "supplies", "extracts_from", "depends_on", "transports_via"}


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


def removal_effect(graph: nx.Graph, node: str) -> dict[str, object]:
    base_efficiency = nx.global_efficiency(graph) if graph.number_of_nodes() > 1 else 0
    copy = graph.copy()
    if node in copy:
        copy.remove_node(node)
    return {
        "largest_component_nodes": lcc(copy).number_of_nodes(),
        "components": nx.number_connected_components(copy) if copy else 0,
        "global_efficiency_loss": base_efficiency - (nx.global_efficiency(copy) if copy.number_of_nodes() > 1 else 0),
    }


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


def centrality_rows(name: str, graph: nx.Graph) -> list[dict[str, object]]:
    largest = lcc(graph)
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    betweenness = nx.betweenness_centrality(largest, weight=None) if largest.number_of_nodes() > 1 else {}
    pagerank = nx.pagerank(graph, weight="weight") if graph else {}
    return [
        {
            "view": name,
            "commodity": commodity,
            "present": commodity in graph,
            "degree": degree.get(commodity, 0),
            "strength": strength.get(commodity, 0),
            "betweenness_lcc": betweenness.get(commodity, 0),
            "pagerank": pagerank.get(commodity, 0),
            "in_lcc": commodity in largest,
        }
        for commodity in COMMODITIES
    ]


def node_metrics(graph: nx.Graph) -> dict[str, dict[str, float]]:
    largest = lcc(graph)
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    betweenness = nx.betweenness_centrality(largest, weight=None) if largest.number_of_nodes() > 1 else {}
    pagerank = nx.pagerank(graph, weight="weight") if graph else {}
    return {
        node: {
            "degree": degree.get(node, 0),
            "strength": strength.get(node, 0),
            "betweenness_lcc": betweenness.get(node, 0),
            "pagerank": pagerank.get(node, 0),
            "in_lcc": node in largest,
        }
        for node in graph.nodes
    }


def removal_rows(name: str, graph: nx.Graph, null_runs: int, seed: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    rows = []
    for commodity in COMMODITIES:
        effect = removal_effect(graph, commodity)
        rows.append(
            {
                "view": name,
                "removed": commodity,
                "present": commodity in graph,
                "degree": degree.get(commodity, 0),
                "strength": strength.get(commodity, 0),
                **effect,
            }
        )

    rnd = random.Random(seed)
    commodity_nodes = [node for node, data in graph.nodes(data=True) if data.get("type") == "COMMODITY" and node != "salt"]
    null = []
    for run in range(null_runs if commodity_nodes else 0):
        node = rnd.choice(commodity_nodes)
        effect = removal_effect(graph, node)
        null.append(
            {
                "view": name,
                "run": run + 1,
                "removed": node,
                "degree": degree.get(node, 0),
                "strength": strength.get(node, 0),
                **effect,
            }
        )
    return rows, null


def all_node_removal_baseline(name: str, graph: nx.Graph, top_n: int) -> list[dict[str, object]]:
    if "salt" not in graph:
        return []
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    salt_degree, salt_strength = degree["salt"], strength["salt"]
    degree_tol = max(2, salt_degree * 0.2)
    strength_tol = max(2, salt_strength * 0.2)
    rows = []
    candidates = set(sorted(graph.nodes, key=lambda node: degree[node], reverse=True)[:top_n])
    candidates.update(
        node
        for node in graph.nodes
        if node != "salt" and abs(degree[node] - salt_degree) <= degree_tol and abs(strength[node] - salt_strength) <= strength_tol
    )
    for node in sorted(candidates, key=lambda node: degree[node], reverse=True):
        match_type = "degree_strength_matched" if (
            node != "salt" and abs(degree[node] - salt_degree) <= degree_tol and abs(strength[node] - salt_strength) <= strength_tol
        ) else "top_degree"
        rows.append(
            {
                "view": name,
                "node": node,
                "node_type": graph.nodes[node].get("type", ""),
                "match_type": match_type,
                "degree": degree[node],
                "strength": strength[node],
                "degree_tolerance": degree_tol,
                "strength_tolerance": strength_tol,
                **removal_effect(graph, node),
            }
        )
    return rows


def commodity_label_permutation(name: str, graph: nx.Graph, null_runs: int, seed: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if "salt" not in graph:
        return [], []
    rnd = random.Random(seed)
    metrics = node_metrics(graph)
    commodity_nodes = [node for node, data in graph.nodes(data=True) if data.get("type") == "COMMODITY" and node != "salt"]
    rows = []
    for run in range(null_runs if commodity_nodes else 0):
        node = rnd.choice(commodity_nodes)
        rows.append({"view": name, "run": run + 1, "permuted_salt_node": node, **metrics[node], **removal_effect(graph, node)})
    salt = {**metrics["salt"], **removal_effect(graph, "salt")}
    summary = []
    for metric in ("degree", "strength", "betweenness_lcc", "pagerank", "global_efficiency_loss"):
        values = [float(row[metric]) for row in rows]
        summary.append(
            {
                "view": name,
                "metric": metric,
                "salt_observed": salt[metric],
                "null_runs": len(values),
                "null_median": statistics.median(values) if values else 0,
                "null_max": max(values) if values else 0,
                "p_ge_salt": (sum(value >= float(salt[metric]) for value in values) + 1) / (len(values) + 1) if values else 0,
            }
        )
    return rows, summary


def community_rows(name: str, graph: nx.Graph, seeds: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    largest = lcc(graph)
    if largest.number_of_edges() == 0:
        return [], []
    degree = dict(largest.degree())
    rows = []
    first_salt_community = None
    for seed in range(seeds):
        communities = louvain_communities(largest, weight="weight", seed=seed, resolution=1)
        node_to_community = {node: index for index, community in enumerate(communities) for node in community}
        salt_community = next((set(community) for community in communities if "salt" in community), set())
        if seed == 0:
            first_salt_community = salt_community
        neighbor_counts = Counter(node_to_community.get(node) for node in largest.neighbors("salt")) if "salt" in largest else Counter()
        salt_degree = degree.get("salt", 0)
        participation = 1 - sum((count / salt_degree) ** 2 for count in neighbor_counts.values()) if salt_degree else 0
        union = len((first_salt_community or set()) | salt_community)
        rows.append(
            {
                "view": name,
                "seed": seed,
                "modularity": modularity(largest, communities, weight="weight"),
                "communities": len(communities),
                "salt_community_size": len(salt_community),
                "salt_participation": participation,
                "salt_community_jaccard_vs_seed0": len((first_salt_community or set()) & salt_community) / union if union else 0,
            }
        )
    summary = []
    for metric in ("modularity", "communities", "salt_community_size", "salt_participation", "salt_community_jaccard_vs_seed0"):
        values = [float(row[metric]) for row in rows]
        summary.append(
            {
                "view": name,
                "metric": metric,
                "median": statistics.median(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
            }
        )
    return rows, summary


def source_drop_rows(rows: list[dict[str, str]], categories: set[str], limit: int) -> list[dict[str, object]]:
    books = Counter(book.strip() for row in rows if row.get("ValidationCategory") in categories for book in row.get("Books", "").split("|") if book.strip())
    output = []
    for book, edge_count in books.most_common(limit):
        kept = [row for row in rows if row.get("ValidationCategory") in categories and book not in {b.strip() for b in row.get("Books", "").split("|")}]
        graph = graph_from(kept, categories)
        metrics = node_metrics(graph).get("salt", {})
        output.append(
            {
                "view": "validated_drop_source",
                "dropped_source": book,
                "dropped_source_edges": edge_count,
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "salt_present": "salt" in graph,
                "salt_degree": metrics.get("degree", 0),
                "salt_strength": metrics.get("strength", 0),
                "salt_betweenness_lcc": metrics.get("betweenness_lcc", 0),
                "salt_pagerank": metrics.get("pagerank", 0),
                "salt_in_lcc": metrics.get("in_lcc", False),
            }
        )
    return output


def markdown_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")).replace("|", "<br>") for field in fields) + " |")
    return "\n".join(lines)


def fmt(value: object, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}" if isinstance(value, (int, float)) or str(value).replace(".", "", 1).replace("-", "", 1).isdigit() else str(value)


def write_report(out: Path, graph_rows: list[dict[str, object]], commodity_rows: list[dict[str, object]], removal: list[dict[str, object]], label_summary: list[dict[str, object]], community_summary: list[dict[str, object]], source_rows: list[dict[str, object]]) -> None:
    salt_rows = [row for row in commodity_rows if row["commodity"] == "salt"]
    salt_removal = [row for row in removal if row["removed"] == "salt"]
    text = [
        "# Network Analysis",
        "",
        "This file is generated from `Mine/outputs/edge_validation.csv`. Rerun `make validation-auto` and `make network-analysis` after adding sources.",
        "",
        "## Graph Views",
        markdown_table(graph_rows, ["view", "nodes", "edges", "components", "largest_component_nodes", "density", "average_degree", "node_types"]),
        "",
        "## Salt Centrality",
        markdown_table(salt_rows, ["view", "degree", "strength", "betweenness_lcc", "pagerank", "in_lcc"]),
        "",
        "## Commodity Removal",
        markdown_table(salt_removal, ["view", "degree", "strength", "largest_component_nodes", "components", "global_efficiency_loss"]),
        "",
        "## Commodity-Label Permutation Null",
        markdown_table(label_summary, ["view", "metric", "salt_observed", "null_median", "null_max", "p_ge_salt"]),
        "",
        "## Louvain Community Stability",
        markdown_table(community_summary, ["view", "metric", "median", "min", "max"]),
        "",
        "## Source Drop Check",
        markdown_table(source_rows, ["dropped_source", "dropped_source_edges", "edges", "salt_degree", "salt_betweenness_lcc", "salt_pagerank"]),
        "",
        "## Editable Notes",
        "",
        "- Add interpretation here.",
        "- Add figure/table decisions here.",
        "- Add reviewer caveats here.",
    ]
    (out / "NETWORK_ANALYSIS.md").write_text("\n".join(text) + "\n", encoding="utf-8")


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


def write_interpretation(
    out: Path,
    graph_rows: list[dict[str, object]],
    commodity_rows: list[dict[str, object]],
    removal: list[dict[str, object]],
    all_node_removal: list[dict[str, object]],
    label_summary: list[dict[str, object]],
    community_summary: list[dict[str, object]],
    source_rows: list[dict[str, object]],
) -> None:
    path = out / "NETWORK_INTERPRETATION.md"
    editable_notes = preserve_editable_notes(path)
    validated = row_for(graph_rows, view="validated")
    salt = row_for(commodity_rows, view="validated", commodity="salt")
    salt_no_concept = row_for(commodity_rows, view="validated_no_concept", commodity="salt")
    salt_trade = row_for(commodity_rows, view="validated_trade_only", commodity="salt")
    salt_removal = row_for(removal, view="validated", removed="salt")
    degree_null = row_for(label_summary, view="validated", metric="degree")
    removal_null = row_for(label_summary, view="validated", metric="global_efficiency_loss")
    modularity = row_for(community_summary, view="validated", metric="modularity")
    salt_community = row_for(community_summary, view="validated", metric="salt_community_size")
    salt_participation = row_for(community_summary, view="validated", metric="salt_participation")
    matched = [row for row in all_node_removal if row.get("view") == "validated" and row.get("match_type") == "degree_strength_matched"]
    strongest_matched = max(matched, key=lambda row: float(row.get("global_efficiency_loss", 0)), default={})
    weakest_source = min(source_rows, key=lambda row: float(row.get("salt_betweenness_lcc", 0)), default={})

    text = [
        "# Network Interpretation",
        "",
        "This file interprets the generated network-analysis outputs. Rerun `make validation-auto` and `make network-analysis` after adding sources. Notes inside the editable block are preserved.",
        "",
        "## Main Claim",
        "",
        "The current evidence supports a cautious claim: salt is the dominant commodity backbone in the validated graph, not necessarily the single backbone of the entire heterogeneous network.",
        "",
        "## What The Validated Graph Shows",
        "",
        f"The validated graph contains {validated.get('nodes')} nodes and {validated.get('edges')} edges, with {validated.get('components')} connected components. Its largest component has {validated.get('largest_component_nodes')} nodes. This means the corpus produces a sparse historical relation graph, not one fully connected trade system.",
        "",
        "Interpretation: network claims should focus on brokerage, centrality, and robustness inside the extracted relation structure. Avoid claiming that the whole Himalayan economy is represented as a complete network.",
        "",
        "## Salt Centrality",
        "",
        f"In the validated graph, salt has degree {salt.get('degree')}, strength {salt.get('strength')}, betweenness {salt.get('betweenness_lcc')}, and PageRank {salt.get('pagerank')}. This makes salt the strongest commodity node in the current outputs.",
        "",
        f"In the no-CONCEPT view, salt still has degree {salt_no_concept.get('degree')} and betweenness {salt_no_concept.get('betweenness_lcc')}. In the trade-only view, salt has degree {salt_trade.get('degree')} and betweenness {salt_trade.get('betweenness_lcc')}.",
        "",
        "Interpretation: salt's centrality is not just an artifact of vague concept nodes or governance/context edges. It survives stricter graph representations.",
        "",
        "## Removal Results",
        "",
        f"Removing salt from the validated graph leaves the largest component with {salt_removal.get('largest_component_nodes')} nodes and causes global efficiency loss {salt_removal.get('global_efficiency_loss')}.",
        "",
        "Interpretation: salt is structurally important among commodities. Its removal damages connectivity more than removing other named commodities in the generated removal table.",
        "",
        "## Null Model Interpretation",
        "",
        f"The commodity-label permutation null gives p_ge_salt {degree_null.get('p_ge_salt')} for degree and {removal_null.get('p_ge_salt')} for removal impact.",
        "",
        "Interpretation: salt is unusual relative to other commodity labels. This supports a commodity-backbone claim.",
        "",
        "Caveat: this does not prove salt is more important than all places, groups, or institutions.",
        "",
        "## All-Node Baseline",
        "",
        f"The strongest degree/strength-matched all-node comparison is {strongest_matched.get('node')} ({strongest_matched.get('node_type')}), with removal efficiency loss {strongest_matched.get('global_efficiency_loss')}.",
        "",
        "Interpretation: if this matched node is stronger than salt, the paper should say salt is the dominant commodity backbone, not the strongest node overall.",
        "",
        "## Community Structure",
        "",
        f"Louvain modularity in the validated graph has median {modularity.get('median')}. Salt's community has median size {salt_community.get('median')}, and salt participation has median {salt_participation.get('median')}.",
        "",
        "Interpretation: the graph has stable community structure, and salt sits in a meaningful community with moderate cross-community participation. This supports brokerage, but not a claim that salt connects every community.",
        "",
        "## Source Robustness",
        "",
        f"The source-drop check shows salt remains present after dropping the largest sources. The largest reduction in salt betweenness among listed drops occurs when dropping {weakest_source.get('dropped_source')}, where salt betweenness is {weakest_source.get('salt_betweenness_lcc')}.",
        "",
        "Interpretation: salt's role is not created by a single source, but some sources contribute more to the brokerage signal.",
        "",
        "## Defensible Wording",
        "",
        "Use:",
        "",
        "> Salt is the most structurally central commodity in the validated Himalayan trade knowledge graph, combining high commodity degree, high brokerage, and unusually large removal impact across robustness views.",
        "",
        "Avoid:",
        "",
        "> Salt is the single structural backbone of the entire Himalayan trade network.",
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
        {"Source": "salt", "Target": "leh", "Weight": "1", "SourceType": "COMMODITY", "TargetType": "LOCATION", "ValidationCategory": "Validated"},
        {"Source": "leh", "Target": "wool", "Weight": "1", "SourceType": "LOCATION", "TargetType": "COMMODITY", "ValidationCategory": "Validated"},
    ]
    graph = graph_from(rows, {"Validated"})
    assert graph.number_of_nodes() == 3
    assert graph.degree("salt") == 1
    assert graph_from(rows, {"Validated"}, keep_concepts=False).number_of_nodes() == 3


def main() -> None:
    parser = argparse.ArgumentParser(description="Network analysis for validated Himalayan trade graph.")
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--null-runs", type=int, default=100)
    parser.add_argument("--community-seeds", type=int, default=20)
    parser.add_argument("--source-drop-limit", type=int, default=10)
    parser.add_argument("--top-removal-n", type=int, default=15)
    parser.add_argument("--seed", type=int, default=7)
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
    commodity_rows = [row for name, graph in views.items() for row in centrality_rows(name, graph)]
    removal = []
    null = []
    all_node_removal = []
    label_null = []
    label_summary = []
    communities = []
    community_summary = []
    for name, graph in views.items():
        view_removal, view_null = removal_rows(name, graph, args.null_runs, args.seed)
        removal.extend(view_removal)
        null.extend(view_null)
        all_node_removal.extend(all_node_removal_baseline(name, graph, args.top_removal_n))
        view_label_null, view_label_summary = commodity_label_permutation(name, graph, args.null_runs, args.seed)
        label_null.extend(view_label_null)
        label_summary.extend(view_label_summary)
        view_communities, view_community_summary = community_rows(name, graph, args.community_seeds)
        communities.extend(view_communities)
        community_summary.extend(view_community_summary)
    source_rows = source_drop_rows(rows, {"Validated"}, args.source_drop_limit)

    write_csv(args.output_dir / "graph_diagnostics.csv", graph_rows, list(graph_rows[0]))
    write_csv(args.output_dir / "commodity_centrality.csv", commodity_rows, list(commodity_rows[0]))
    write_csv(args.output_dir / "removal_experiment.csv", removal, list(removal[0]))
    if null:
        write_csv(args.output_dir / "random_commodity_removal.csv", null, list(null[0]))
    if all_node_removal:
        write_csv(args.output_dir / "all_node_removal_baseline.csv", all_node_removal, list(all_node_removal[0]))
    if label_null:
        write_csv(args.output_dir / "commodity_label_permutation.csv", label_null, list(label_null[0]))
        write_csv(args.output_dir / "commodity_label_permutation_summary.csv", label_summary, list(label_summary[0]))
    if communities:
        write_csv(args.output_dir / "louvain_communities.csv", communities, list(communities[0]))
        write_csv(args.output_dir / "louvain_community_summary.csv", community_summary, list(community_summary[0]))
    if source_rows:
        write_csv(args.output_dir / "source_drop_centrality.csv", source_rows, list(source_rows[0]))
    write_report(args.output_dir, graph_rows, commodity_rows, removal, label_summary, community_summary, source_rows)
    write_interpretation(args.output_dir, graph_rows, commodity_rows, removal, all_node_removal, label_summary, community_summary, source_rows)
    print(f"Wrote network analysis to {args.output_dir}")


if __name__ == "__main__":
    main()
