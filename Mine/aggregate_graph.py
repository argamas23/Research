import os
import csv
import glob
import json
import math
import re
import networkx as nx
from collections import defaultdict

try:
    import spacy

    NLP = spacy.load("en_core_web_sm")
except Exception:
    NLP = None

RESULTS_ROOT = os.path.join(os.path.dirname(__file__), "Results")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

ALLOWED_RELATIONS = {
    "trades_with",
    "extracts_from",
    "taxes",
    "licenses",
    "controls",
    "governs",
    "supplies",
    "depends_on",
    "transports_via",
    "monopolizes",
    "disputes",
    "negotiates_with",
}

COMMODITY_KEYWORDS = {
    "salt",
    "barley",
    "tea",
    "rice",
    "wool",
    "pashm",
    "butter",
    "tsampa",
    "grain",
    "musk",
    "porcelain",
    "leather",
    "cloth",
    "vegetables",
    "sugar",
    "spices",
    "horses",
    "mules",
    "sheep",
    "goats",
    "livestock",
    "yak",
    "minerals",
    "skins",
    "skins",
    "cashmere",
    "oil",
}

LOCATION_KEYWORDS = {
    "valley",
    "lake",
    "pass",
    "river",
    "plateau",
    "district",
    "province",
    "region",
    "country",
    "border",
    "road",
    "trail",
    "market",
    "village",
    "town",
    "city",
    "state",
    "plateau",
    "mountain",
    "himalaya",
    "tibet",
    "ladakh",
    "kashmir",
    "china",
    "nepal",
    "bhutan",
    "sikkim",
    "amdo",
    "yunnan",
    "sichuan",
    "india",
    "mustang",
    "dolpo",
    "zanskar",
    "leh",
    "rupshu",
    "tso kar",
}

PERSON_INDICATORS = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "bishop",
    "chief",
    "lama",
    "nawab",
    "ruler",
    "king",
    "queen",
    "son",
    "daughter",
    "father",
    "mother",
    "prince",
    "princess",
    "official",
}

BAD_PERSON_TOKENS = {
    "village",
    "villages",
    "world",
    "services",
    "information",
    "accounts",
    "road",
    "roads",
    "change",
    "service",
    "population",
    "modern",
    "movement",
    "supply",
    "goods",
    "prices",
    "market",
    "trail",
    "lake",
    "river",
    "pass",
    "plateau",
    "district",
    "province",
    "region",
    "town",
    "city",
    "state",
    "border",
    "mountain",
    "group",
    "team",
    "people",
    "community",
    "nomads",
    "shepherds",
    "traders",
    "mission",
    "travels",
    "labour",
    "work",
    "history",
    "accounts",
}

KEEP_ENTITY_TYPES = {"PERSON", "COMMODITY", "LOCATION"}

RELATION_PATTERNS = [
    (
        r"\b(tax|fine|levy|tariff|duty|tribute|excise|collect\s+tax|paid\s+tax)\b",
        "taxes",
    ),
    (
        r"\b(license|licen[sc]e|permit|allow|allowed|grant\s+leave|authorize|authorise)\b",
        "licenses",
    ),
    (r"\b(monopol|dominat|monopolizes)\b", "monopolizes"),
    (
        r"\b(disput|claim|encroach|contest|oppose|fight|attack|seized|seize|claim\s+ownership)\b",
        "disputes",
    ),
    (
        r"\b(negotiate|mediate|agree|settle|mediated|reached\s+agreement|broker)\b",
        "negotiates_with",
    ),
    (r"\b(depend|need|require|rely|reliant)\b", "depends_on"),
    (
        r"\b(transport|carry|haul|convey|ship|move|bring|cart|carted|draw|carry\s+forward)\b",
        "transports_via",
    ),
    (
        r"\b(supply|provide|deliver|offer|furnish|feed|give\s+salt|give\s+tea)\b",
        "supplies",
    ),
    (
        r"\b(extract|collect|remove|withdraw|harvest|mine|gather|fetch|draw|take\s+salt|take\s+from)\b",
        "extracts_from",
    ),
    (
        r"\b(trade|barter|exchange|sell|buy|deal|swap|pay|market|purchase|vend|deal\s+in|trade\s+with)\b",
        "trades_with",
    ),
    (
        r"\b(govern|rule|administer|manage|supervise|oversee|subordinate|subordinated|regulate|control|dominate|claim|authorit)\b",
        "governs",
    ),
    (r"\b(control|dominate|own|possess|claim|rule|manage|administer)\b", "controls"),
]

STOP_WORDS = {
    "the",
    "and",
    "of",
    "in",
    "on",
    "for",
    "to",
    "from",
    "by",
    "as",
    "with",
    "at",
    "a",
    "an",
    "that",
    "this",
    "these",
    "those",
    "is",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "be",
    "being",
    "been",
    "which",
    "not",
    "but",
    "or",
    "if",
    "their",
    "its",
}

COLOR_BY_TYPE = {
    "PERSON": "#4c72b0",
    "LOCATION": "#55a868",
    "COMMODITY": "#c44e52",
}
SHAPE_BY_TYPE = {
    "PERSON": "dot",
    "LOCATION": "triangle",
    "COMMODITY": "square",
}
DEFAULT_COLOR = "#888888"
DEFAULT_SHAPE = "dot"


def normalize(text):
    if text is None:
        return ""
    return " ".join(text.strip().lower().split())


def find_weighted_csvs(root):
    paths = []
    for path in glob.glob(
        os.path.join(root, "**", "*weighted*knowledge*graph*.csv"), recursive=True
    ):
        paths.append(path)
    return sorted(paths)


def load_edges(files):
    edges = []
    for path in files:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = normalize(row.get("Source", ""))
                target = normalize(row.get("Target", ""))
                relation = normalize(row.get("Relation", ""))
                try:
                    weight = float(row.get("Weight", 1) or 1)
                except ValueError:
                    weight = 1.0

                if not source or not target or target == "none" or source == "none":
                    continue
                if source == target:
                    continue

                edges.append((source, target, relation, weight, path))
    return edges


def aggregate_edges(edges):
    aggregated = defaultdict(float)
    relation_attrs = defaultdict(set)
    sources_by_edge = defaultdict(set)
    targets_by_edge = defaultdict(set)
    for source, target, relation, weight, path in edges:
        aggregated[(source, target)] += weight
        relation_attrs[(source, target)].add(relation)
        sources_by_edge[(source, target)].add(path)
        targets_by_edge[(source, target)].add(path)
    return aggregated, relation_attrs, sources_by_edge


def build_graph(aggregated, relation_attrs):
    G = nx.DiGraph()
    for (source, target), weight in aggregated.items():
        relations = sorted(relation_attrs[(source, target)])
        G.add_edge(source, target, weight=weight, relations="|".join(relations))
    return G


def compute_metrics(G):
    metrics = {}
    metrics["weighted_degree"] = dict(G.degree(weight="weight"))
    metrics["weighted_in_degree"] = dict(G.in_degree(weight="weight"))
    metrics["weighted_out_degree"] = dict(G.out_degree(weight="weight"))
    metrics["betweenness"] = nx.betweenness_centrality(
        G, weight="weight", normalized=True
    )
    metrics["closeness"] = nx.closeness_centrality(G, distance="weight")
    try:
        metrics["eigenvector"] = nx.eigenvector_centrality_numpy(G, weight="weight")
    except Exception:
        try:
            metrics["eigenvector"] = nx.eigenvector_centrality(
                nx.Graph(G.to_undirected()), weight="weight", max_iter=200, tol=1e-06
            )
        except Exception:
            metrics["eigenvector"] = {node: 0.0 for node in G.nodes()}
    return metrics


def map_relation(relation_text, source, target):
    text = normalize(relation_text)
    for pattern, mapped in RELATION_PATTERNS:
        if re.search(pattern, text):
            if mapped == "governs" and re.search(
                r"\b(control|dominate|own|possess|claim|rule|manage|administer)\b", text
            ):
                if re.search(
                    r"\b(government|state|administration|authority|office|bureau|commission|monastery|association|governmental)\b",
                    source + " " + target,
                ):
                    return "governs"
                return "controls"
            if mapped == "controls" and re.search(
                r"\b(government|state|administration|authority|office|bureau|commission|monastery|association|governmental)\b",
                source + " " + target,
            ):
                return "governs"
            return mapped
    return None


def is_too_noisy_entity(entity_text):
    if not entity_text:
        return True
    if len(entity_text.split()) > 7:
        return True
    if re.search(r"\d", entity_text):
        return True
    if any(
        ch in entity_text for ch in ['"', "'", "[", "]", "(", ")", ":", ";", "—", "–"]
    ):
        if len(entity_text.split()) > 3:
            return True
    if entity_text.startswith("none "):
        return True
    if entity_text.count(" ") > 6:
        return True
    return False


BAD_COMMODITY_TERMS = {
    "various",
    "other",
    "several",
    "some",
    "many",
    "best",
    "all",
    "more",
    "total",
    "many",
}

BAD_LOCATION_TERMS = {
    "one of",
    "best",
    "valuable",
    "recent",
    "modern",
    "northerly direction",
    "information",
    "insights",
    "famous",
    "ancient",
    "heavy",
    "seasonal",
    "main",
    "general",
    "large",
    "small",
    "other",
    "various",
    "almost",
    "nearby",
    "farther",
    "farther",
    "early",
    "late",
    "central",
    "new",
}


def classify_node(node):
    node = normalize(node)
    if not node or is_too_noisy_entity(node):
        return None, 0.0

    if NLP is not None:
        doc = NLP(node)
        for ent in doc.ents:
            if ent.text and ent.text.lower() == node:
                if ent.label_ == "PERSON":
                    return "PERSON", 1.0
                if ent.label_ in {"GPE", "LOC", "FAC"}:
                    return "LOCATION", 1.0
                if ent.label_ == "ORG":
                    return "INSTITUTION", 1.0
                if ent.label_ in {"PRODUCT", "WORK_OF_ART", "NORP"}:
                    return "COMMODITY", 1.0

    tokens = node.split()

    if any(term in node for term in COMMODITY_KEYWORDS):
        if (
            "," in node
            or " or " in node
            or " and " in node
            or len(tokens) > 4
            or any(term in node for term in BAD_COMMODITY_TERMS)
        ):
            return None, 0.0
        return "COMMODITY", 0.8

    if any(term in node for term in LOCATION_KEYWORDS):
        if (
            "," in node
            or len(tokens) > 7
            or any(term in node for term in BAD_LOCATION_TERMS)
        ):
            return None, 0.0
        return "LOCATION", 0.8

    if len(tokens) <= 4 and all(re.fullmatch(r"[a-z\-]+", token) for token in tokens):
        if any(token in PERSON_INDICATORS for token in tokens) and not any(
            token in LOCATION_KEYWORDS or token in COMMODITY_KEYWORDS
            for token in tokens
        ):
            return "PERSON", 0.7
        if (
            len(tokens) <= 3
            and sum(1 for token in tokens if token in STOP_WORDS) <= 1
            and not any(
                token in LOCATION_KEYWORDS
                or token in COMMODITY_KEYWORDS
                or token in BAD_PERSON_TOKENS
                for token in tokens
            )
        ):
            if (
                "," not in node
                and " or " not in node
                and " and " not in node
                and " of " not in node
                and " to " not in node
            ):
                return "PERSON", 0.5

    return None, 0.0


def build_clean_graph(aggregated, relation_attrs):
    entity_types = {}
    cleaned_edges = []
    for (source, target), weight in aggregated.items():
        raw_relations = "|".join(sorted(relation_attrs[(source, target)]))
        mapped = map_relation(raw_relations, source, target)
        if mapped is None:
            continue

        source_type, source_conf = classify_node(source)
        target_type, target_conf = classify_node(target)
        if source_type not in KEEP_ENTITY_TYPES or target_type not in KEEP_ENTITY_TYPES:
            continue

        entity_types[source] = {"type": source_type, "confidence": source_conf}
        entity_types[target] = {"type": target_type, "confidence": target_conf}
        cleaned_edges.append(
            {
                "source": source,
                "target": target,
                "relation": mapped,
                "weight": weight,
                "raw_relations": raw_relations,
                "source_type": source_type,
                "target_type": target_type,
            }
        )

    G_clean = nx.DiGraph()
    for edge in cleaned_edges:
        G_clean.add_edge(
            edge["source"],
            edge["target"],
            weight=edge["weight"],
            relation=edge["relation"],
            raw_relations=edge["raw_relations"],
        )
    return G_clean, entity_types, cleaned_edges


def save_clean_entities(entity_types, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entities = []
    for node, attrs in sorted(entity_types.items()):
        entities.append(
            {
                "entity": node,
                "type": attrs["type"],
                "confidence": round(attrs["confidence"], 2),
                "relevance": 1.0,
                "source": "aggregated_graph",
            }
        )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)


def save_clean_relations(edges, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for edge in edges:
            item = {
                "subject": edge["source"],
                "relation": edge["relation"],
                "object": edge["target"],
                "confidence": round(min(edge["weight"] / 10.0, 1.0), 2),
                "evidence": edge["raw_relations"],
                "document": "aggregated_csvs",
                "weight": edge["weight"],
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def save_clean_edges_csv(edges, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Source",
                "Target",
                "MappedRelation",
                "Weight",
                "RawRelations",
                "SourceType",
                "TargetType",
            ]
        )
        for edge in sorted(edges, key=lambda x: -x["weight"]):
            writer.writerow(
                [
                    edge["source"],
                    edge["target"],
                    edge["relation"],
                    edge["weight"],
                    edge["raw_relations"],
                    edge["source_type"],
                    edge["target_type"],
                ]
            )


def calculate_node_size(weight):
    return min(32, max(14, 10 + math.log1p(weight) * 8))


def build_visualization_data(entity_types, edges):
    node_weights = defaultdict(float)
    node_degrees = defaultdict(int)
    for edge in edges:
        node_weights[edge["source"]] += edge["weight"]
        node_weights[edge["target"]] += edge["weight"]
        node_degrees[edge["source"]] += 1
        node_degrees[edge["target"]] += 1

    node_items = []
    for node, attrs in sorted(entity_types.items()):
        node_type = attrs.get("type", "UNKNOWN")
        color = COLOR_BY_TYPE.get(node_type, DEFAULT_COLOR)
        shape = SHAPE_BY_TYPE.get(node_type, DEFAULT_SHAPE)
        weight = node_weights.get(node, 0.0)
        degree = node_degrees.get(node, 0)
        node_items.append(
            {
                "id": node,
                "label": node,
                "type": node_type,
                "color": color,
                "shape": shape,
                "size": calculate_node_size(weight),
                "weight": weight,
                "degree": degree,
                "title": f"<strong>{node}</strong><br>Type: {node_type}<br>Degree: {degree}<br>Weighted degree: {weight:.1f}",
            }
        )

    edge_items = []
    for edge in edges:
        edge_items.append(
            {
                "from": edge["source"],
                "to": edge["target"],
                "label": edge["relation"],
                "width": max(1, min(5, edge["weight"])),
                "arrows": "to",
                "title": f"Relation: {edge['relation']}<br>Weight: {edge['weight']:.1f}<br>Evidence: {edge['raw_relations']}",
            }
        )

    return node_items, edge_items


def generate_graph_html(node_items, edge_items):
    nodes_json = json.dumps(node_items, ensure_ascii=False)
    edges_json = json.dumps(edge_items, ensure_ascii=False)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cleaned Graph Visualization</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.css" integrity="sha512-WgxfT5LWjfszlPHXRmBWHkV2eceiWTOBvrKCNbdgDYTHrT2AeLCGbF4sZlZw3UMN3WtL0tGUoIAKsu8mllg/XA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js" integrity="sha512-LnvoEWDFrqGHlHmDD2101OrLcbsfkrzoSpvtSQtxK3RMnRV0eOkhhBN2dXHKRrUU8p2DGRTk35n4O8mWSVe1mQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background: #fafafa; }
    #toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; padding: 12px; background: #fff; border-bottom: 1px solid #ddd; }
    #toolbar label { font-weight: 600; }
    #controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
    #mynetwork { width: 100%; height: calc(100vh - 140px); background-color: #fff; }
    #legend { padding: 12px; font-size: 14px; color: #333; background: #fff; border: 1px solid #ddd; margin: 12px; border-radius: 8px; max-width: 360px; }
    .legend-item { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .legend-swatch { display: inline-block; width: 16px; height: 16px; border-radius: 4px; }
    #info { padding: 12px; background: #fff; border-top: 1px solid #ddd; font-size: 14px; color: #333; }
    #reset-button { padding: 6px 12px; border: 1px solid #888; border-radius: 6px; background: #f5f5f5; cursor: pointer; }
  </style>
</head>
<body>
  <div id="toolbar">
    <div id="controls">
      <label for="filter-type">Filter type</label>
      <select id="filter-type">
        <option value="ALL">All</option>
        <option value="PERSON">Person</option>
        <option value="LOCATION">Location</option>
        <option value="COMMODITY">Commodity</option>
        <option value="UNKNOWN">Unknown</option>
      </select>
      <label for="search-node">Search node</label>
      <input id="search-node" type="search" placeholder="Type a node label" style="min-width:200px; padding:6px; border-radius:6px; border:1px solid #ccc;" />
      <button id="reset-button">Reset view</button>
    </div>
    <div id="legend">
      <div class="legend-item"><span class="legend-swatch" style="background:#4c72b0"></span> PERSON</div>
      <div class="legend-item"><span class="legend-swatch" style="background:#55a868"></span> LOCATION</div>
      <div class="legend-item"><span class="legend-swatch" style="background:#c44e52"></span> COMMODITY</div>
      <div class="legend-item"><span class="legend-swatch" style="background:#888"></span> UNKNOWN</div>
    </div>
  </div>
  <div id="mynetwork"></div>
  <div id="info">Click a node to inspect it. Hover edges to read relation labels. Use filters and search to focus the graph.</div>
  <script>
    const nodesData = __NODES_JSON__;
    const edgesData = __EDGES_JSON__;

    const nodes = new vis.DataSet(nodesData);
    const edges = new vis.DataSet(edgesData);

    const container = document.getElementById('mynetwork');
    const data = { nodes: nodes, edges: edges };

    const options = {
      physics: {
        enabled: true,
        stabilization: { iterations: 500, fit: true },
        barnesHut: { gravitationalConstant: -18000, springLength: 200, springConstant: 0.04 },
      },
      interaction: { hover: true, tooltipDelay: 100, dragNodes: true, multiselect: false },
      edges: { color: { inherit: true }, smooth: { enabled: true, type: 'dynamic' }, arrows: { to: { enabled: true, scaleFactor: 0.6 } }, font: { align: 'middle' } },
      nodes: { font: { multi: 'html', size: 14 }, borderWidth: 2, chosen: { node: function(values, id, selected, hovering) { values.color = '#ffdd57'; } } },
      layout: { improvedLayout: true },
      manipulation: false,
    };

    const network = new vis.Network(container, data, options);

    function resetHighlight() {
      nodes.forEach(function(node) {
        nodes.update({ id: node.id, color: node.color, hidden: false });
      });
      edges.forEach(function(edge) { edges.update({ id: edge.id, hidden: false }); });
      network.fit({ animation: true });
    }

    function highlightNode(nodeId) {
      const connected = network.getConnectedNodes(nodeId);
      nodes.forEach(function(node) {
        const hidden = node.id !== nodeId && !connected.includes(node.id);
        nodes.update({ id: node.id, hidden: hidden });
      });
      edges.forEach(function(edge) {
        const show = edge.from === nodeId || edge.to === nodeId || connected.includes(edge.from) || connected.includes(edge.to);
        edges.update({ id: edge.id, hidden: !show });
      });
      network.focus(nodeId, { scale: 1.2, animation: { duration: 500 } });
    }

    network.on('click', function(params) {
      if (params.nodes.length === 1) {
        highlightNode(params.nodes[0]);
      }
    });

    document.getElementById('reset-button').addEventListener('click', resetHighlight);

    document.getElementById('filter-type').addEventListener('change', function(event) {
      const type = event.target.value;
      nodes.forEach(function(node) {
        nodes.update({ id: node.id, hidden: type !== 'ALL' && node.type !== type });
      });
    });

    document.getElementById('search-node').addEventListener('input', function(event) {
      const query = event.target.value.trim().toLowerCase();
      if (!query) {
        nodes.forEach(function(node) { nodes.update({ id: node.id, hidden: false }); });
        edges.forEach(function(edge) { edges.update({ id: edge.id, hidden: false }); });
        return;
      }
      nodes.forEach(function(node) {
        const match = node.label.toLowerCase().includes(query);
        nodes.update({ id: node.id, hidden: !match });
      });
      edges.forEach(function(edge) {
        const from = nodes.get(edge.from);
        const to = nodes.get(edge.to);
        edges.update({ id: edge.id, hidden: from.hidden || to.hidden });
      });
    });
  </script>
</body>
</html>"""
    return html.replace("__NODES_JSON__", nodes_json).replace("__EDGES_JSON__", edges_json)


def save_graph_html(node_items, edge_items, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(generate_graph_html(node_items, edge_items))


def save_metrics(metrics, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "node",
            "weighted_degree",
            "weighted_in_degree",
            "weighted_out_degree",
            "betweenness",
            "closeness",
            "eigenvector",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        nodes = set()
        for metric in metrics.values():
            nodes.update(metric.keys())
        for node in sorted(nodes):
            writer.writerow(
                {
                    "node": node,
                    "weighted_degree": metrics["weighted_degree"].get(node, 0),
                    "weighted_in_degree": metrics["weighted_in_degree"].get(node, 0),
                    "weighted_out_degree": metrics["weighted_out_degree"].get(node, 0),
                    "betweenness": metrics["betweenness"].get(node, 0),
                    "closeness": metrics["closeness"].get(node, 0),
                    "eigenvector": metrics["eigenvector"].get(node, 0),
                }
            )


import xml.etree.ElementTree as ET
from xml.dom import minidom


def sanitize_graphml_id(value, existing_ids, fallback_prefix="n"):
    name = normalize(value)
    name = re.sub(r"[^a-z0-9_\-\.]+", "_", name)
    name = re.sub(r"^([^a-z_]+)", "n_", name)
    if not name:
        name = fallback_prefix
    base = name
    suffix = 1
    while name in existing_ids:
        name = f"{base}_{suffix}"
        suffix += 1
    existing_ids.add(name)
    return name


def save_graphml(G, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    graphml = ET.Element(
        "graphml",
        {
            "xmlns": "http://graphml.graphdrawing.org/xmlns",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
        },
    )

    ET.SubElement(
        graphml,
        "key",
        id="d0",
        **{"for": "edge", "attr.name": "weight", "attr.type": "double"},
    )
    ET.SubElement(
        graphml,
        "key",
        id="d1",
        **{"for": "edge", "attr.name": "relations", "attr.type": "string"},
    )
    ET.SubElement(
        graphml,
        "key",
        id="d2",
        **{"for": "node", "attr.name": "label", "attr.type": "string"},
    )
    ET.SubElement(
        graphml,
        "key",
        id="d3",
        **{"for": "node", "attr.name": "type", "attr.type": "string"},
    )

    graph = ET.SubElement(graphml, "graph", edgedefault="directed")
    node_id_map = {}
    existing_ids = set()
    for node in G.nodes():
        nid = sanitize_graphml_id(node, existing_ids)
        node_id_map[node] = nid
        node_elem = ET.SubElement(graph, "node", id=nid)
        ET.SubElement(node_elem, "data", key="d2").text = str(node)
        ET.SubElement(node_elem, "data", key="d3").text = str(
            G.nodes[node].get("type", "")
        )

    for u, v, data in G.edges(data=True):
        edge_elem = ET.SubElement(
            graph, "edge", source=node_id_map[u], target=node_id_map[v]
        )
        ET.SubElement(edge_elem, "data", key="d0").text = str(data.get("weight", 1))
        ET.SubElement(edge_elem, "data", key="d1").text = str(data.get("relations", ""))

    rough_string = ET.tostring(graphml, "utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent="  ")
    with open(path, "w", encoding="utf-8") as f:
        f.write(pretty)


def save_aggregated_edges(aggregated, relation_attrs, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target", "TotalWeight", "Relations"])
        for (source, target), weight in sorted(aggregated.items(), key=lambda x: -x[1]):
            writer.writerow(
                [
                    source,
                    target,
                    weight,
                    "|".join(sorted(relation_attrs[(source, target)])),
                ]
            )


if __name__ == "__main__":
    weighted_files = find_weighted_csvs(RESULTS_ROOT)
    print("Found weighted graph files:", weighted_files)
    edges = load_edges(weighted_files)
    aggregated, relation_attrs, source_paths = aggregate_edges(edges)

    G = build_graph(aggregated, relation_attrs)
    metrics = compute_metrics(G)
    save_metrics(metrics, os.path.join(OUTPUT_DIR, "network_metrics.csv"))
    save_graphml(G, os.path.join(OUTPUT_DIR, "network.graphml"))
    save_aggregated_edges(
        aggregated, relation_attrs, os.path.join(OUTPUT_DIR, "aggregated_edges.csv")
    )

    G_clean, entity_types, cleaned_edges = build_clean_graph(aggregated, relation_attrs)
    if cleaned_edges:
        cleaned_metrics = compute_metrics(G_clean)
        save_metrics(
            cleaned_metrics, os.path.join(OUTPUT_DIR, "cleaned_network_metrics.csv")
        )
        save_graphml(G_clean, os.path.join(OUTPUT_DIR, "cleaned_network.graphml"))
        save_clean_entities(
            entity_types, os.path.join(OUTPUT_DIR, "cleaned_entities.json")
        )
        save_clean_relations(
            cleaned_edges, os.path.join(OUTPUT_DIR, "cleaned_relations.jsonl")
        )
        save_clean_edges_csv(
            cleaned_edges, os.path.join(OUTPUT_DIR, "cleaned_aggregated_edges.csv")
        )
        node_items, edge_items = build_visualization_data(entity_types, cleaned_edges)
        output_vis_path = os.path.join(OUTPUT_DIR, "network_visualization.html")
        root_vis_path = os.path.join(os.path.dirname(__file__), "network_visualization.html")
        save_graph_html(node_items, edge_items, output_vis_path)
        save_graph_html(node_items, edge_items, root_vis_path)
        print("Saved HTML visualization to", output_vis_path)
        print("Also updated root visualization file at", root_vis_path)
    else:
        print(
            "No cleaned edges matched PERSON/COMMODITY/LOCATION and allowed relation mapping."
        )

    print("Saved outputs to", OUTPUT_DIR)
