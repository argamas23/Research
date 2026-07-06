"""
Regenerate network_visualization.html with corrected entity types.

Reads corrected cleaned_entities.json and re-embeds the node data
into the HTML template with proper types, colors, and labels.
"""

import json
import math
import os
import re
import shutil

import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import (
    COLOR_BY_TYPE,
    DEFAULT_COLOR,
    SHAPE_BY_TYPE,
    DEFAULT_SHAPE,
    RESEARCH_FOCUS_NODE,
    OUTPUT_DIR,
)

HTML_PATH = os.path.join(os.path.dirname(__file__), "network_visualization.html")
OUTPUT_HTML_PATH = os.path.join(OUTPUT_DIR, "network_visualization.html")
ENTITIES_PATH = os.path.join(OUTPUT_DIR, "cleaned_entities.json")


def calculate_node_size(weight, degree):
    base = 10
    weight_factor = math.sqrt(weight) * 3
    degree_factor = math.sqrt(degree) * 2
    return base + weight_factor + degree_factor


def regenerate_html():
    # Load corrected entities
    with open(ENTITIES_PATH, "r", encoding="utf-8") as f:
        entities = json.load(f)
    entity_types = {e["entity"]: e for e in entities}

    # Read current HTML
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Parse existing node data to preserve weights/degrees/edges
    nodes_match = re.search(
        r'<script type="application/json" id="graph-nodes-data">\s*\n(.*?)\n</script><!-- GRAPH_NODES_END -->',
        html,
        re.DOTALL,
    )
    edges_match = re.search(
        r'<script type="application/json" id="graph-edges-data">\s*\n(.*?)\n</script><!-- GRAPH_EDGES_END -->',
        html,
        re.DOTALL,
    )

    if not nodes_match or not edges_match:
        print("ERROR: Could not find node/edge data markers in HTML")
        return

    old_nodes = json.loads(nodes_match.group(1))
    old_edges = json.loads(edges_match.group(1))

    # Rebuild nodes with corrected types
    new_nodes = []
    for node in old_nodes:
        node_id = node["id"]
        if node_id in entity_types:
            ent = entity_types[node_id]
            node_type = ent["type"]
        else:
            node_type = node.get("type", "CONCEPT")

        color = COLOR_BY_TYPE.get(node_type, DEFAULT_COLOR)
        shape = SHAPE_BY_TYPE.get(node_type, DEFAULT_SHAPE)

        weight = node.get("weight", 1.0)
        degree = node.get("degree", 1)
        is_focus = RESEARCH_FOCUS_NODE in node_id
        is_core = node.get("core", False)

        size = calculate_node_size(weight, degree)
        if is_core:
            size = max(size, 22)

        # Build title tooltip
        if is_focus:
            title = (
                f"<strong>{node_id}</strong><br>Research focus<br>"
                f"Type: {node_type}<br>Degree: {degree}<br>"
                f"Weighted degree: {weight:.1f}"
            )
        else:
            title = (
                f"<strong>{node_id}</strong><br>"
                f"Type: {node_type}<br>Degree: {degree}<br>"
                f"Weighted degree: {weight:.1f}"
            )

        new_node = {
            "id": node_id,
            "label": node_id,
            "type": node_type,
            "color": color,
            "shape": shape,
            "size": size,
            "weight": weight,
            "degree": degree,
            "core": is_core,
            "title": title,
        }
        if is_core:
            new_node["mass"] = 2.6
        if is_focus:
            new_node["color"] = "#ffcc00"
            new_node["font"] = {"color": "#d62728", "size": 14, "bold": True}

        new_nodes.append(new_node)

    # Also update edge tooltips that mention entity types
    new_edges = []
    for edge in old_edges:
        # Update edge title if it references old types
        new_edges.append(edge)

    # Rebuild the HTML
    nodes_json = json.dumps(new_nodes, ensure_ascii=False)
    edges_json = json.dumps(new_edges, ensure_ascii=False)

    # Replace nodes section
    html = re.sub(
        r'(<script type="application/json" id="graph-nodes-data">)\s*\n.*?\n(</script><!-- GRAPH_NODES_END -->)',
        rf'\1\n{nodes_json}\n\2',
        html,
        flags=re.DOTALL,
    )

    # Replace edges section
    html = re.sub(
        r'(<script type="application/json" id="graph-edges-data">)\s*\n.*?\n(</script><!-- GRAPH_EDGES_END -->)',
        rf'\1\n{edges_json}\n\2',
        html,
        flags=re.DOTALL,
    )

    # Save updated HTML
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Updated: {HTML_PATH}")

    # Also save to outputs directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Updated: {OUTPUT_HTML_PATH}")

    # Copy CSS and vendor files if needed
    css_src = os.path.join(os.path.dirname(__file__), "network_visualization.css")
    css_dst = os.path.join(OUTPUT_DIR, "network_visualization.css")
    if os.path.exists(css_src):
        shutil.copyfile(css_src, css_dst)

    vis_src = os.path.join(os.path.dirname(__file__), "lib", "vis-9.1.2")
    vis_dst = os.path.join(OUTPUT_DIR, "lib", "vis-9.1.2")
    if os.path.exists(vis_src) and not os.path.exists(vis_dst):
        os.makedirs(os.path.dirname(vis_dst), exist_ok=True)
        shutil.copytree(vis_src, vis_dst)

    # Summary
    from collections import Counter
    type_counts = Counter(n["type"] for n in new_nodes)
    print(f"\nNode type distribution in visualization:")
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}")
    print(f"Total nodes: {len(new_nodes)}, Total edges: {len(new_edges)}")


if __name__ == "__main__":
    regenerate_html()
