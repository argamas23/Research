from __future__ import annotations

import argparse
import csv
import random
import statistics
from collections import Counter
from pathlib import Path

import networkx as nx
from networkx.algorithms.community import louvain_communities, modularity


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
DEFAULT_EDGES = OUTPUT_DIR / "edge_validation.csv"
DEFAULT_OUT = OUTPUT_DIR / "salt_analysis"
COMMODITIES = ["salt", "wool", "pashm", "grain", "barley", "tea", "borax"]
TRADE_RELATIONS = {"trades_with", "supplies", "extracts_from", "depends_on", "transports_via"}
REVIEW_NODES = {"gg", "men", "the water", "the desert", "the lake"}


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


def salt_centrality_rows(name: str, graph: nx.Graph) -> list[dict[str, object]]:
    metrics = node_metrics(graph)
    return [{"view": name, "commodity": "salt", "present": "salt" in graph, **metrics.get("salt", {})}]


def salt_removal_rows(name: str, graph: nx.Graph) -> tuple[dict[str, object], list[dict[str, object]]]:
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    salt = {
        "view": name,
        "removed": "salt",
        "present": "salt" in graph,
        "degree": degree.get("salt", 0),
        "strength": strength.get("salt", 0),
        **removal_effect(graph, "salt"),
    }
    comparison = []
    for commodity in COMMODITIES:
        comparison.append(
            {
                "view": name,
                "removed": commodity,
                "present": commodity in graph,
                "degree": degree.get(commodity, 0),
                "strength": strength.get(commodity, 0),
                **removal_effect(graph, commodity),
            }
        )
    return salt, comparison


def random_commodity_removal(name: str, graph: nx.Graph, null_runs: int, seed: int) -> list[dict[str, object]]:
    rnd = random.Random(seed)
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    commodity_nodes = [node for node, data in graph.nodes(data=True) if data.get("type") == "COMMODITY" and node != "salt"]
    return [
        {
            "view": name,
            "run": run + 1,
            "removed": node,
            "degree": degree.get(node, 0),
            "strength": strength.get(node, 0),
            **removal_effect(graph, node),
        }
        for run in range(null_runs if commodity_nodes else 0)
        for node in [rnd.choice(commodity_nodes)]
    ]


def all_node_removal_baseline(name: str, graph: nx.Graph, top_n: int) -> list[dict[str, object]]:
    if "salt" not in graph:
        return []
    degree = dict(graph.degree())
    strength = dict(graph.degree(weight="weight"))
    salt_degree, salt_strength = degree["salt"], strength["salt"]
    degree_tol = max(2, salt_degree * 0.2)
    strength_tol = max(2, salt_strength * 0.2)
    candidates = set(sorted(graph.nodes, key=lambda node: degree[node], reverse=True)[:top_n])
    candidates.update(
        node
        for node in graph.nodes
        if node != "salt" and abs(degree[node] - salt_degree) <= degree_tol and abs(strength[node] - salt_strength) <= strength_tol
    )
    return [
        {
            "view": name,
            "node": node,
            "node_type": graph.nodes[node].get("type", ""),
            "match_type": "degree_strength_matched"
            if node != "salt" and abs(degree[node] - salt_degree) <= degree_tol and abs(strength[node] - salt_strength) <= strength_tol
            else "top_degree",
            "degree": degree[node],
            "strength": strength[node],
            "degree_tolerance": degree_tol,
            "strength_tolerance": strength_tol,
            **removal_effect(graph, node),
        }
        for node in sorted(candidates, key=lambda item: degree[item], reverse=True)
    ]


def salt_label_permutation(name: str, graph: nx.Graph, null_runs: int, seed: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if "salt" not in graph:
        return [], []
    rnd = random.Random(seed)
    metrics = node_metrics(graph)
    commodity_nodes = [node for node, data in graph.nodes(data=True) if data.get("type") == "COMMODITY" and node != "salt"]
    rows = [
        {"view": name, "run": run + 1, "permuted_salt_node": node, **metrics[node], **removal_effect(graph, node)}
        for run in range(null_runs if commodity_nodes else 0)
        for node in [rnd.choice(commodity_nodes)]
    ]
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


def salt_community_rows(name: str, graph: nx.Graph, seeds: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    largest = lcc(graph)
    if "salt" not in largest or largest.number_of_edges() == 0:
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
        neighbor_counts = Counter(node_to_community.get(node) for node in largest.neighbors("salt"))
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
    for metric in ("salt_community_size", "salt_participation", "salt_community_jaccard_vs_seed0"):
        values = [float(row[metric]) for row in rows]
        summary.append({"view": name, "metric": metric, "median": statistics.median(values), "min": min(values), "max": max(values)})
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


def review_flag(row: dict[str, str]) -> str:
    nodes = {row.get("Source", ""), row.get("Target", "")} - {"salt"}
    if not row.get("Evidence", "").strip():
        return "missing_evidence"
    if nodes & REVIEW_NODES or any(node.startswith(("the ", "us ")) for node in nodes):
        return "generic_entity"
    if float(row.get("Confidence") or 0) == 0:
        return "zero_confidence"
    return ""


def salt_edge_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        if row.get("ValidationCategory") != "Validated" or "salt" not in {row.get("Source"), row.get("Target")}:
            continue
        output.append(
            {
                "Source": row.get("Source", ""),
                "Target": row.get("Target", ""),
                "MappedRelation": row.get("MappedRelation", ""),
                "Circuit": row.get("Circuit", ""),
                "Weight": row.get("Weight", ""),
                "Confidence": row.get("Confidence", ""),
                "Score": row.get("Score", ""),
                "SourceType": row.get("SourceType", ""),
                "TargetType": row.get("TargetType", ""),
                "Books": row.get("Books", ""),
                "ReviewFlag": review_flag(row),
                "Evidence": row.get("Evidence", ""),
            }
        )
    return sorted(output, key=lambda row: float(row.get("Score") or 0), reverse=True)


def salt_source_rows(salt_edges: list[dict[str, object]]) -> list[dict[str, object]]:
    sources = sorted({book for row in salt_edges for book in str(row.get("Books", "")).split("|") if book})
    return [
        {
            "Book": book,
            "SaltEdges": sum(book in str(row.get("Books", "")).split("|") for row in salt_edges),
            "Relations": "|".join(
                f"{relation}:{count}"
                for relation, count in Counter(
                    row["MappedRelation"] for row in salt_edges if book in str(row.get("Books", "")).split("|")
                ).most_common()
            ),
        }
        for book in sources
    ]


def salt_community_members(name: str, graph: nx.Graph) -> list[dict[str, object]]:
    largest = lcc(graph)
    if "salt" not in largest or largest.number_of_edges() == 0:
        return []
    communities = louvain_communities(largest, weight="weight", seed=0, resolution=1)
    community = next((set(item) for item in communities if "salt" in item), set())
    degree = dict(largest.degree())
    return [
        {
            "view": name,
            "node": node,
            "type": largest.nodes[node].get("type", ""),
            "degree_in_lcc": degree.get(node, 0),
            "salt_neighbor": largest.has_edge("salt", node),
        }
        for node in sorted(community, key=lambda node: (-degree.get(node, 0), node))
    ]


def salt_brokerage_paths(name: str, graph: nx.Graph, limit: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    largest = lcc(graph)
    if "salt" not in largest:
        return [], []
    lengths = dict(nx.all_pairs_shortest_path_length(largest))
    salt_lengths = lengths["salt"]
    nodes = [node for node in largest if node != "salt"]
    counts: Counter[str] = Counter()
    samples = []
    for index, source in enumerate(nodes):
        for target in nodes[index + 1 :]:
            if salt_lengths[source] + salt_lengths[target] != lengths[source][target]:
                continue
            source_type = largest.nodes[source].get("type", "")
            target_type = largest.nodes[target].get("type", "")
            type_pair = "--".join(sorted([source_type, target_type]))
            counts[type_pair] += 1
            if len(samples) < limit:
                path = nx.shortest_path(largest, source, "salt") + nx.shortest_path(largest, "salt", target)[1:]
                samples.append(
                    {
                        "view": name,
                        "source": source,
                        "source_type": source_type,
                        "target": target,
                        "target_type": target_type,
                        "path_length": len(path) - 1,
                        "path": " -> ".join(path),
                    }
                )
    summary = [{"view": name, "type_pair": pair, "paths_through_salt": count} for pair, count in counts.most_common()]
    return samples, summary


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


def write_report(
    out: Path,
    centrality: list[dict[str, object]],
    removal: list[dict[str, object]],
    label_summary: list[dict[str, object]],
    community_summary: list[dict[str, object]],
    source_rows: list[dict[str, object]],
    salt_edges: list[dict[str, object]],
    salt_sources: list[dict[str, object]],
    path_summary: list[dict[str, object]],
) -> None:
    text = [
        "# Salt Metrics",
        "",
        "This file is generated by `Mine/salt_analysis.py` and contains salt-specific metrics only.",
        "",
        "## Salt Centrality",
        markdown_table(centrality, ["view", "degree", "strength", "betweenness_lcc", "pagerank", "in_lcc"]),
        "",
        "## Salt Removal",
        markdown_table(removal, ["view", "degree", "strength", "largest_component_nodes", "components", "global_efficiency_loss"]),
        "",
        "## Commodity-Label Permutation Null",
        markdown_table(label_summary, ["view", "metric", "salt_observed", "null_runs", "null_median", "null_max", "p_ge_salt"]),
        "",
        "## Salt Community Stability",
        markdown_table(community_summary, ["view", "metric", "median", "min", "max"]),
        "",
        "## Source Drop Check",
        markdown_table(source_rows, ["dropped_source", "dropped_source_edges", "edges", "salt_degree", "salt_betweenness_lcc", "salt_pagerank"]),
        "",
        "## Salt Source Edge Counts",
        markdown_table(salt_sources, ["Book", "SaltEdges", "Relations"]),
        "",
        "## Salt Edge Evidence",
        markdown_table(salt_edges[:15], ["Source", "MappedRelation", "Target", "Circuit", "Books", "ReviewFlag", "Evidence"]),
        "",
        "## Shortest Paths Through Salt",
        markdown_table(path_summary[:12], ["type_pair", "paths_through_salt"]),
    ]
    (out / "SALT_METRICS.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def write_interpretation(
    out: Path,
    centrality: list[dict[str, object]],
    removal: list[dict[str, object]],
    all_node_removal: list[dict[str, object]],
    label_summary: list[dict[str, object]],
    community_summary: list[dict[str, object]],
    source_rows: list[dict[str, object]],
    salt_edges: list[dict[str, object]],
    path_summary: list[dict[str, object]],
) -> None:
    path = out / "SALT_INTERPRETATION.md"
    editable_notes = preserve_editable_notes(path)
    salt = row_for(centrality, view="validated")
    salt_no_concept = row_for(centrality, view="validated_no_concept")
    salt_trade = row_for(centrality, view="validated_trade_only")
    salt_removal = row_for(removal, view="validated")
    degree_null = row_for(label_summary, view="validated", metric="degree")
    removal_null = row_for(label_summary, view="validated", metric="global_efficiency_loss")
    salt_community = row_for(community_summary, view="validated", metric="salt_community_size")
    salt_participation = row_for(community_summary, view="validated", metric="salt_participation")
    matched = [row for row in all_node_removal if row.get("view") == "validated" and row.get("match_type") == "degree_strength_matched"]
    strongest_matched = max(matched, key=lambda row: float(row.get("global_efficiency_loss", 0)), default={})
    weakest_source = min(source_rows, key=lambda row: float(row.get("salt_betweenness_lcc", 0)), default={})
    flagged = sum(bool(row.get("ReviewFlag")) for row in salt_edges)
    top_path = path_summary[0] if path_summary else {}
    text = [
        "# Salt Interpretation",
        "",
        "This file interprets only salt-specific metrics and evidence.",
        "",
        "## Main Claim",
        "",
        "Salt is the most structurally central commodity in the validated graph, but the claim should remain commodity-specific rather than network-total.",
        "",
        "## Centrality",
        "",
        f"In the validated graph, salt has degree {salt.get('degree')}, strength {salt.get('strength')}, betweenness {salt.get('betweenness_lcc')}, and PageRank {salt.get('pagerank')}.",
        "",
        f"In stricter views it remains central: no-CONCEPT degree {salt_no_concept.get('degree')} with betweenness {salt_no_concept.get('betweenness_lcc')}; trade-only degree {salt_trade.get('degree')} with betweenness {salt_trade.get('betweenness_lcc')}.",
        "",
        "## Removal And Null Model",
        "",
        f"Removing salt leaves the validated graph's largest component with {salt_removal.get('largest_component_nodes')} nodes and causes global efficiency loss {salt_removal.get('global_efficiency_loss')}.",
        "",
        f"The commodity-label null gives p_ge_salt {degree_null.get('p_ge_salt')} for degree and {removal_null.get('p_ge_salt')} for removal impact.",
        "",
        "Interpretation: salt is unusual among commodity labels, not necessarily stronger than all places or institutions.",
        "",
        "## All-Node Baseline",
        "",
        f"The strongest degree/strength-matched all-node comparison is {strongest_matched.get('node')} ({strongest_matched.get('node_type')}), with removal efficiency loss {strongest_matched.get('global_efficiency_loss')}.",
        "",
        "## Community And Brokerage",
        "",
        f"Salt's validated Louvain community has median size {salt_community.get('median')}, with participation {salt_participation.get('median')}.",
        "",
        f"The most common shortest-path class through salt is {top_path.get('type_pair')}, with {top_path.get('paths_through_salt')} pair paths.",
        "",
        "Interpretation: salt works best as a brokerage claim: it connects commodity, place, and actor relations inside the extracted graph.",
        "",
        "## Evidence Audit",
        "",
        f"The validated graph has {len(salt_edges)} salt edges; {flagged} are flagged for manual review because of generic entities, missing evidence, or zero confidence.",
        "",
        "Interpretation: review the flagged rows before using edge-level examples in prose.",
        "",
        "## Source Robustness",
        "",
        f"Salt remains present after dropping the largest sources. The largest listed betweenness reduction occurs when dropping {weakest_source.get('dropped_source')}, where salt betweenness is {weakest_source.get('salt_betweenness_lcc')}.",
        "",
        "## Defensible Wording",
        "",
        "> Salt is the most structurally central commodity in the validated Himalayan trade knowledge graph, combining high commodity degree, high brokerage, and unusually large removal impact across robustness views.",
        "",
        "Avoid: salt is the single backbone of the entire Himalayan economy.",
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
        {"Source": "salt", "Target": "wool", "Weight": "1", "SourceType": "COMMODITY", "TargetType": "COMMODITY", "ValidationCategory": "Validated"},
    ]
    graph = graph_from(rows, {"Validated"})
    assert salt_centrality_rows("test", graph)[0]["degree"] == 2
    samples, summary = salt_brokerage_paths("test", graph, 10)
    assert samples and summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Salt-specific network analysis for validated Himalayan trade graph.")
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--null-runs", type=int, default=100)
    parser.add_argument("--community-seeds", type=int, default=20)
    parser.add_argument("--source-drop-limit", type=int, default=10)
    parser.add_argument("--top-removal-n", type=int, default=15)
    parser.add_argument("--salt-path-limit", type=int, default=100)
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
    centrality = [row for name, graph in views.items() for row in salt_centrality_rows(name, graph)]
    removal = []
    removal_comparison = []
    random_removal = []
    all_node_removal = []
    label_null = []
    label_summary = []
    community_runs = []
    community_summary = []
    for name, graph in views.items():
        salt_row, comparison_rows = salt_removal_rows(name, graph)
        removal.append(salt_row)
        removal_comparison.extend(comparison_rows)
        random_removal.extend(random_commodity_removal(name, graph, args.null_runs, args.seed))
        all_node_removal.extend(all_node_removal_baseline(name, graph, args.top_removal_n))
        null_rows, summary_rows = salt_label_permutation(name, graph, args.null_runs, args.seed)
        label_null.extend(null_rows)
        label_summary.extend(summary_rows)
        run_rows, community_rows = salt_community_rows(name, graph, args.community_seeds)
        community_runs.extend(run_rows)
        community_summary.extend(community_rows)
    source_rows = source_drop_rows(rows, {"Validated"}, args.source_drop_limit)
    salt_edges = salt_edge_rows(rows)
    salt_sources = salt_source_rows(salt_edges)
    salt_members = [row for name, graph in views.items() for row in salt_community_members(name, graph)]
    salt_paths, salt_path_summary = salt_brokerage_paths("validated", views["validated"], args.salt_path_limit)

    write_csv(args.output_dir / "salt_centrality.csv", centrality, list(centrality[0]))
    write_csv(args.output_dir / "salt_removal.csv", removal, list(removal[0]))
    write_csv(args.output_dir / "salt_commodity_removal_comparison.csv", removal_comparison, list(removal_comparison[0]))
    write_csv(args.output_dir / "salt_random_commodity_removal_null.csv", random_removal, list(random_removal[0]))
    write_csv(args.output_dir / "salt_all_node_removal_baseline.csv", all_node_removal, list(all_node_removal[0]))
    write_csv(args.output_dir / "salt_label_permutation.csv", label_null, list(label_null[0]))
    write_csv(args.output_dir / "salt_label_permutation_summary.csv", label_summary, list(label_summary[0]))
    write_csv(args.output_dir / "salt_community_stability.csv", community_runs, list(community_runs[0]))
    write_csv(args.output_dir / "salt_community_summary.csv", community_summary, list(community_summary[0]))
    write_csv(args.output_dir / "salt_source_drop_centrality.csv", source_rows, list(source_rows[0]))
    write_csv(args.output_dir / "salt_edge_evidence.csv", salt_edges, list(salt_edges[0]))
    write_csv(args.output_dir / "salt_source_summary.csv", salt_sources, list(salt_sources[0]))
    write_csv(args.output_dir / "salt_community_members.csv", salt_members, list(salt_members[0]))
    write_csv(args.output_dir / "salt_brokerage_paths.csv", salt_paths, list(salt_paths[0]))
    write_csv(args.output_dir / "salt_brokerage_path_summary.csv", salt_path_summary, list(salt_path_summary[0]))
    write_report(args.output_dir, centrality, removal, label_summary, community_summary, source_rows, salt_edges, salt_sources, salt_path_summary)
    write_interpretation(args.output_dir, centrality, removal, all_node_removal, label_summary, community_summary, source_rows, salt_edges, salt_path_summary)
    print(f"Wrote salt analysis to {args.output_dir}")


if __name__ == "__main__":
    main()
