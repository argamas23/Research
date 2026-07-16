from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path

from graph_rules import (
    BAD_COMMODITY_TERMS,
    BAD_LOCATION_TERMS,
    BAD_PERSON_TOKENS,
    CIRCUIT_COLORS,
    COLOR_BY_TYPE,
    COMMODITY_KEYWORDS,
    DEFAULT_COLOR,
    DEFAULT_SHAPE,
    EDGE_COLOR_BY_RELATION,
    ENTITY_ALIASES,
    ENTITY_TYPE_OVERRIDES,
    GROUP_KEYWORDS,
    KEEP_ENTITY_TYPES,
    LOCATION_KEYWORDS,
    NOISY_ENTITIES,
    OUTPUT_DIR,
    PERSON_INDICATORS,
    RELATION_PATTERNS,
    RESULTS_ROOT,
    RESEARCH_FOCUS_NODE,
    ROUTE_PLACE_TERMS,
    SALT_TERMS,
    SHAPE_BY_TYPE,
    SOCIAL_ACTOR_TERMS,
    POLITICAL_ECONOMY_TERMS,
)

MINE_DIR = Path(__file__).resolve().parent
HTML_PATHS = [
    MINE_DIR / "network_visualization.html",
    Path(OUTPUT_DIR) / "network_visualization.html",
]
ENTITIES_PATH = Path(OUTPUT_DIR) / "cleaned_entities.json"


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def clean_entity(value: str) -> str:
    entity = clean(value).strip(" .,/\\'\"")
    return ENTITY_ALIASES.get(entity, entity)


def is_noise(entity: str) -> bool:
    words = entity.split()
    # ponytail: phrase-length filter is a cheap guard; replace with NER spans if precision matters.
    return entity in NOISY_ENTITIES or len(words) > 12 or entity in {"none", "true", "you", "i"}


def has_any(entity: str, terms: set[str]) -> bool:
    return any(term in entity for term in terms)


def circuit_for_node(entity: str, node_type: str) -> str:
    words = set(re.findall(r"[a-z]+", entity))
    if has_any(entity, SALT_TERMS):
        return "Salt anchor"
    if has_any(entity, POLITICAL_ECONOMY_TERMS):
        return "Political economy"
    if node_type == "COMMODITY" or has_any(entity, COMMODITY_KEYWORDS):
        return "Commodity circuits"
    if node_type == "LOCATION" or has_any(entity, ROUTE_PLACE_TERMS):
        return "Route/place circuits"
    if node_type in {"GROUP", "PERSON"} or words & SOCIAL_ACTOR_TERMS:
        return "Social actors"
    return "Conceptual context"


def circuit_for_edge(source: str, relation: str, target: str, evidence: list[str]) -> str:
    text = " ".join([source, relation, target, *evidence])
    if relation in {"taxes", "licenses", "controls", "governs", "monopolizes", "disputes", "negotiates_with"}:
        return "Political economy"
    if relation in {"trades_with", "supplies", "extracts_from", "depends_on"}:
        return "Commodity circuits"
    if relation == "transports_via":
        return "Route/place circuits"
    if has_any(text, SALT_TERMS):
        return "Salt anchor"
    if has_any(text, ROUTE_PLACE_TERMS):
        return "Route/place circuits"
    return "Conceptual context"


def book_name(path: Path) -> str:
    return re.sub(r"_\d{8}_\d{6}$", "", path.parent.name)


def mapped_relation(raw: str) -> str:
    relation = clean(raw).replace("-", "_").replace(" ", "_")
    if relation in EDGE_COLOR_BY_RELATION:
        return relation
    raw_text = clean(raw)
    for pattern, mapped in RELATION_PATTERNS:
        if re.search(pattern, raw_text):
            return mapped
    return ""


def load_entity_types() -> dict[str, str]:
    if not ENTITIES_PATH.exists():
        return {}
    with ENTITIES_PATH.open(encoding="utf-8") as f:
        return {clean_entity(row["entity"]): row.get("type", "CONCEPT") for row in json.load(f)}


def classify_entity(entity: str, entity_types: dict[str, str]) -> str:
    words = set(re.findall(r"[a-z]+", entity))
    is_group = bool(
        words & GROUP_KEYWORDS
        or words & {
            "association",
            "authorities",
            "baqals",
            "bhotias",
            "callers",
            "champas",
            "collectors",
            "communities",
            "community",
            "devotees",
            "government",
            "governments",
            "men",
            "merchants",
            "monasteries",
            "nomads",
            "officials",
            "pastoralists",
            "peasants",
            "people",
            "peoples",
            "shepherds",
            "society",
            "tribe",
            "tribes",
            "women",
            "zanskaris",
        }
    )
    if is_group:
        return "GROUP"
    if entity in ENTITY_TYPE_OVERRIDES:
        return ENTITY_TYPE_OVERRIDES[entity][0]
    known = entity_types.get(entity)
    if known in KEEP_ENTITY_TYPES and known != "CONCEPT":
        return known
    if has_any(
        entity,
        COMMODITY_KEYWORDS
        | {
            "buckwheat",
            "bucket",
            "buckets",
            "capital",
            "cash",
            "charas",
            "cloth",
            "collections",
            "corn",
            "crops",
            "goods",
            "grains",
            "pashm",
            "pastoral products",
            "raw silk",
            "rice",
            "silk",
            "tea",
            "vegetables",
            "wells",
            "wheat",
            "wood",
        },
    ) and not words & BAD_COMMODITY_TERMS:
        return "COMMODITY"
    if has_any(
        entity,
        LOCATION_KEYWORDS
        | {
            "bathang",
            "borders",
            "country",
            "department",
            "forest",
            "nyoma",
            "plains",
            "sichuan",
            "spot",
            "tibetan countries",
            "tsakalho",
        },
    ) and not words & BAD_LOCATION_TERMS:
        return "LOCATION"
    if words & PERSON_INDICATORS and not words & BAD_PERSON_TOKENS:
        return "PERSON"
    return known if known in KEEP_ENTITY_TYPES else "CONCEPT"


def replace_html_data(html: str, data_id: str, rows: list[dict]) -> str:
    payload = json.dumps(rows, ensure_ascii=False)
    return re.sub(
        rf'(<script type="application/json" id="{data_id}">)\s*\n.*?\n(</script><!-- [A-Z_]+_END -->)',
        rf"\1\n{payload}\n\2",
        html,
        flags=re.S,
    )


def support(score: float, mean: float, stdev: float) -> tuple[str, str]:
    if not stdev:
        return "medium", "Medium connection"
    if score >= mean + stdev * 0.6:
        return "strong", "Strong connection"
    if score <= mean - stdev * 0.6:
        return "weak", "Weak connection"
    return "medium", "Medium connection"


def edge_score(source: str, target: str, item: dict, degree: dict[str, int]) -> float:
    return (
        float(item["confidence"]) * 3
        + math.log1p(float(item["weight"]))
        + len(item["books"]) * 0.3
        + (degree[source] + degree[target]) * 0.05
        + (0.5 if RESEARCH_FOCUS_NODE in {source, target} else 0)
    )


def reachable_from_focus(edge_rows: dict[tuple[str, str, str], dict]) -> set[str]:
    graph = defaultdict(set)
    for source, _, target in edge_rows:
        graph[source].add(target)
        graph[target].add(source)
    seen = {RESEARCH_FOCUS_NODE} if RESEARCH_FOCUS_NODE in graph else set()
    stack = list(seen)
    while stack:
        node = stack.pop()
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return seen


def component_sizes(edge_rows: dict[tuple[str, str, str], dict]) -> dict[str, int]:
    graph = defaultdict(set)
    for source, _, target in edge_rows:
        graph[source].add(target)
        graph[target].add(source)
    sizes = {}
    seen = set()
    for start in graph:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        for node in component:
            sizes[node] = len(component)
    return sizes


def graph_stats(edge_rows: dict[tuple[str, str, str], dict]) -> tuple[dict[str, int], dict[str, float]]:
    degree = defaultdict(int)
    weighted = defaultdict(float)
    for source, _, target in edge_rows:
        weight = edge_rows[(source, _, target)]["weight"]
        degree[source] += 1
        degree[target] += 1
        weighted[source] += weight
        weighted[target] += weight
    return degree, weighted


def main() -> None:
    entity_types = load_entity_types()
    edge_rows: dict[tuple[str, str, str], dict] = {}

    for csv_path in sorted(Path(RESULTS_ROOT).glob("**/weighted_knowledge_graph.csv")):
        with csv_path.open(newline="", encoding="utf-8", errors="ignore") as f:
            for row in csv.DictReader(f):
                source = clean_entity(row.get("Source", ""))
                target = clean_entity(row.get("Target", ""))
                relation = mapped_relation(row.get("Relation", ""))
                if (
                    not source
                    or not target
                    or source == target
                    or not relation
                    or is_noise(source)
                    or is_noise(target)
                ):
                    continue
                key = (source, relation, target)
                item = edge_rows.setdefault(
                    key,
                    {"weight": 0.0, "confidence": 0.0, "books": set(), "evidence": set(), "raw": set()},
                )
                try:
                    item["weight"] += float(row.get("Weight") or 1)
                except ValueError:
                    item["weight"] += 1
                try:
                    item["confidence"] = max(item["confidence"], float(row.get("Confidence") or 0))
                except ValueError:
                    pass
                item["books"].add(book_name(csv_path))
                if row.get("Evidence"):
                    item["evidence"].add(row["Evidence"].strip())
                if row.get("Relation"):
                    item["raw"].add(row["Relation"].strip())

    degree, weighted = graph_stats(edge_rows)
    focus_component = reachable_from_focus(edge_rows)
    node_types = {node: classify_entity(node, entity_types) for node in degree}
    trimmed_nodes = {
        node for node, node_type in node_types.items()
        if node_type == "CONCEPT" and node not in focus_component and degree[node] <= 1
    }
    edge_rows = {
        key: item
        for key, item in edge_rows.items()
        if key[0] not in trimmed_nodes and key[2] not in trimmed_nodes
    }

    degree, weighted = graph_stats(edge_rows)
    focus_component = reachable_from_focus(edge_rows)
    component_size = component_sizes(edge_rows)

    nodes = []
    for node in sorted(degree):
        node_type = node_types.get(node) or classify_entity(node, entity_types)
        node_weight = weighted[node]
        node_degree = degree[node]
        is_focus = RESEARCH_FOCUS_NODE in node
        is_core = node in focus_component
        circuit = circuit_for_node(node, node_type)
        fill_color = "#ffcc00" if is_focus else COLOR_BY_TYPE.get(node_type, DEFAULT_COLOR)
        border_color = CIRCUIT_COLORS.get(circuit, DEFAULT_COLOR)
        size = 10 + math.sqrt(max(node_weight, 1)) * 3 + math.sqrt(max(node_degree, 1)) * 2
        if is_core:
            size = max(size, 22)
        title = f"<strong>{node}</strong><br>Type: {node_type}<br>Circuit: {circuit}<br>Degree: {node_degree}<br>Weighted degree: {node_weight:.1f}"
        if is_focus:
            title = title.replace("<br>Type:", "<br>Research focus<br>Type:")
        item = {
            "id": node,
            "label": node,
            "type": node_type,
            "circuit": circuit,
            "color": {"background": fill_color, "border": border_color},
            "borderWidth": 3 if circuit != "Conceptual context" else 1.5,
            "shape": SHAPE_BY_TYPE.get(node_type, DEFAULT_SHAPE),
            "size": size,
            "weight": node_weight,
            "degree": node_degree,
            "core": is_core,
            "title": title,
        }
        if is_core:
            item["mass"] = 2.6
        if is_focus:
            item["font"] = {"color": "#d62728", "size": 14, "bold": True}
        nodes.append(item)

    support_by_key = {}
    for default_visible in (True, False):
        grouped_edges = [
            row for row in edge_rows.items()
            if ((component_size.get(row[0][0], 1) > 2 and component_size.get(row[0][2], 1) > 2) == default_visible)
        ]
        ranked_edges = sorted(
            grouped_edges,
            key=lambda row: (
                edge_score(row[0][0], row[0][2], row[1], degree),
                row[1]["confidence"],
                row[1]["weight"],
                row[0],
            ),
            reverse=True,
        )
        scores = [edge_score(key[0], key[2], item, degree) for key, item in ranked_edges]
        mean = sum(scores) / len(scores) if scores else 0
        stdev = math.sqrt(sum((score - mean) ** 2 for score in scores) / len(scores)) if scores else 0
        support_by_key.update(
            {
                key: support(edge_score(key[0], key[2], item, degree), mean, stdev)
                for key, item in ranked_edges
            }
        )

    edges = []
    for index, ((source, relation, target), item) in enumerate(sorted(edge_rows.items())):
        weight = item["weight"]
        confidence = item["confidence"]
        score = edge_score(source, target, item, degree)
        support_key, support_label = support_by_key[(source, relation, target)]
        color = EDGE_COLOR_BY_RELATION.get(relation, "#999999")
        books = sorted(item["books"])
        evidence = sorted(item["evidence"])
        raw = sorted(item["raw"])
        circuit = circuit_for_edge(source, relation, target, evidence)
        edges.append(
            {
                "id": f"e{index}",
                "from": source,
                "to": target,
                "label": relation,
                "relation": relation,
                "circuit": circuit,
                "support": support_key,
                "supportLabel": support_label,
                "color": {"color": color, "highlight": color},
                "width": max(3.2, min(8.0, 2.5 + weight * 1.1)),
                "dashes": False,
                "opacity": 1.0 if support_key == "strong" else 0.72,
                "weight": weight,
                "confidence": confidence,
                "score": round(score, 4),
                "books": books,
                "evidence": evidence,
                "arrows": "to",
                "font": {"size": 10, "align": "middle", "strokeWidth": 3, "strokeColor": "#ffffff"},
                "title": (
                    f"{source} -> {target}<br>Relation: {relation}<br>Support: {support_label}"
                    f"<br>Circuit: {circuit}"
                    f"<br>Score: {score:.2f}<br>Weight: {weight:.1f}<br>Confidence: {confidence:.2f}<br>Books: {', '.join(books)}"
                    f"<br>Evidence: {'|'.join(evidence)}<br>Raw relations: {'|'.join(raw)}"
                ),
            }
        )

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    for html_path in HTML_PATHS:
        html = html_path.read_text(encoding="utf-8")
        html = html.replace(
            '<label class="toggle"><input id="large-components-only" type="checkbox" /> Components &gt; 2</label>',
            '<label class="toggle"><input id="large-components-only" type="checkbox" checked /> Components &gt; 2</label>',
        )
        html = html.replace(
            "document.getElementById('large-components-only').checked = false;",
            "document.getElementById('large-components-only').checked = true;",
        )
        html = replace_html_data(html, "graph-nodes-data", nodes)
        html = replace_html_data(html, "graph-edges-data", edges)
        html_path.write_text(html, encoding="utf-8")

    css_src = MINE_DIR / "network_visualization.css"
    if css_src.exists():
        shutil.copyfile(css_src, Path(OUTPUT_DIR) / "network_visualization.css")

    with ENTITIES_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "entity": node["id"],
                    "type": node["type"],
                    "circuit": node["circuit"],
                    "confidence": 1.0 if node["core"] else 0.8,
                }
                for node in nodes
            ],
            f,
            indent=2,
            ensure_ascii=False,
        )

    with (Path(OUTPUT_DIR) / "cleaned_aggregated_edges.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target", "MappedRelation", "Circuit", "Weight", "Confidence", "Score", "RawRelations", "SourceType", "TargetType", "Books", "Evidence"])
        type_by_node = {node["id"]: node["type"] for node in nodes}
        for edge in edges:
            writer.writerow([
                edge["from"],
                edge["to"],
                edge["relation"],
                edge["circuit"],
                edge["weight"],
                edge["confidence"],
                edge["score"],
                edge["label"],
                type_by_node.get(edge["from"], ""),
                type_by_node.get(edge["to"], ""),
                "|".join(edge["books"]),
                "|".join(edge["evidence"]),
            ])

    print(f"Rebuilt graph: {len(nodes)} nodes, {len(edges)} edges, {len(focus_component)} salt-core nodes")


if __name__ == "__main__":
    main()
