import os
import csv
import glob
import json
import re
import math
import networkx as nx
from collections import Counter, defaultdict

try:
    import spacy
    NLP = spacy.load('en_core_web_sm')
except Exception:
    NLP = None

RESULTS_ROOT = os.path.join(os.path.dirname(__file__), 'Results')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'outputs')

ALLOWED_RELATIONS = {
    'trades_with',
    'extracts_from',
    'taxes',
    'licenses',
    'controls',
    'governs',
    'supplies',
    'depends_on',
    'transports_via',
    'monopolizes',
    'disputes',
    'negotiates_with',
}

COMMODITY_KEYWORDS = {
    'salt', 'barley', 'tea', 'rice', 'wool', 'pashm', 'butter', 'tsampa', 'grain', 'musk',
    'porcelain', 'leather', 'cloth', 'vegetables', 'sugar', 'spices', 'horses', 'mules',
    'sheep', 'goats', 'livestock', 'yak', 'minerals', 'skins', 'skins', 'cashmere', 'oil',
}

LOCATION_KEYWORDS = {
    'valley', 'lake', 'pass', 'river', 'plateau', 'district', 'province', 'region', 'country',
    'border', 'road', 'trail', 'market', 'village', 'town', 'city', 'state', 'plateau', 'mountain',
    'himalaya', 'tibet', 'ladakh', 'kashmir', 'china', 'nepal', 'bhutan', 'sikkim', 'amdo',
    'yunnan', 'sichuan', 'india', 'mustang', 'dolpo', 'zanskar', 'leh', 'rupshu', 'tso kar',
}

PERSON_INDICATORS = {
    'mr', 'mrs', 'ms', 'dr', 'bishop', 'chief', 'lama', 'nawab', 'ruler', 'king', 'queen',
    'son', 'daughter', 'father', 'mother', 'prince', 'princess', 'official',
}

BAD_PERSON_TOKENS = {
    'village', 'villages', 'world', 'services', 'information', 'accounts', 'road', 'roads',
    'change', 'service', 'population', 'modern', 'movement', 'supply', 'goods', 'prices',
    'market', 'trail', 'lake', 'river', 'pass', 'plateau', 'district', 'province', 'region',
    'town', 'city', 'state', 'border', 'mountain', 'group', 'team', 'people', 'community',
    'nomads', 'shepherds', 'traders', 'mission', 'travels', 'labour', 'work', 'history', 'accounts',
}

KEEP_ENTITY_TYPES = {'PERSON', 'COMMODITY', 'LOCATION'}

RELATION_PATTERNS = [
    (r'\b(tax|fine|levy|tariff|duty|tribute|excise|collect\s+tax|paid\s+tax)\b', 'taxes'),
    (r'\b(license|licen[sc]e|permit|allow|allowed|grant\s+leave|authorize|authorise)\b', 'licenses'),
    (r'\b(monopol|dominat|monopolizes)\b', 'monopolizes'),
    (r'\b(disput|claim|encroach|contest|oppose|fight|attack|seized|seize|claim\s+ownership)\b', 'disputes'),
    (r'\b(negotiate|mediate|agree|settle|mediated|reached\s+agreement|broker)\b', 'negotiates_with'),
    (r'\b(depend|need|require|rely|reliant)\b', 'depends_on'),
    (r'\b(transport|carry|haul|convey|ship|move|bring|cart|carted|draw|carry\s+forward)\b', 'transports_via'),
    (r'\b(supply|provide|deliver|offer|furnish|feed|give\s+salt|give\s+tea)\b', 'supplies'),
    (r'\b(extract|collect|remove|withdraw|harvest|mine|gather|fetch|draw|take\s+salt|take\s+from)\b', 'extracts_from'),
    (r'\b(trade|barter|exchange|sell|buy|deal|swap|pay|market|purchase|vend|deal\s+in|trade\s+with)\b', 'trades_with'),
    (r'\b(govern|rule|administer|manage|supervise|oversee|subordinate|subordinated|regulate|control|dominate|claim|authorit)\b', 'governs'),
    (r'\b(control|dominate|own|possess|claim|rule|manage|administer)\b', 'controls'),
]

STOP_WORDS = {
    'the', 'and', 'of', 'in', 'on', 'for', 'to', 'from', 'by', 'as', 'with', 'at', 'a',
    'an', 'that', 'this', 'these', 'those', 'is', 'are', 'was', 'were', 'have', 'has',
    'had', 'be', 'being', 'been', 'which', 'not', 'but', 'or', 'if', 'their', 'its',
}


def normalize(text):
    if text is None:
        return ''
    return ' '.join(text.strip().lower().split())


def find_weighted_csvs(root):
    paths = []
    for path in glob.glob(os.path.join(root, '**', '*weighted*knowledge*graph*.csv'), recursive=True):
        paths.append(path)
    return sorted(paths)


def load_edges(files):
    edges = []
    for path in files:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = normalize(row.get('Source', ''))
                target = normalize(row.get('Target', ''))
                relation = normalize(row.get('Relation', ''))
                try:
                    weight = float(row.get('Weight', 1) or 1)
                except ValueError:
                    weight = 1.0

                if not source or not target or target == 'none' or source == 'none':
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
        G.add_edge(source, target, weight=weight, relation='|'.join(relations), relations='|'.join(relations))
    return G


def compute_metrics(G):
    metrics = {}
    metrics['weighted_degree'] = dict(G.degree(weight='weight'))
    metrics['weighted_in_degree'] = dict(G.in_degree(weight='weight'))
    metrics['weighted_out_degree'] = dict(G.out_degree(weight='weight'))
    for _, _, data in G.edges(data=True):
        weight = float(data.get('weight', 1) or 1)
        data['distance'] = 1.0 / max(weight, 1e-9)
    metrics['betweenness'] = nx.betweenness_centrality(G, weight='distance', normalized=True)
    metrics['closeness'] = nx.closeness_centrality(G, distance='distance')
    try:
        metrics['pagerank'] = nx.pagerank(G, weight='weight')
    except Exception:
        metrics['pagerank'] = {node: 0.0 for node in G.nodes()}
    try:
        metrics['eigenvector'] = nx.eigenvector_centrality_numpy(G, weight='weight')
    except Exception:
        try:
            metrics['eigenvector'] = nx.eigenvector_centrality(nx.Graph(G.to_undirected()), weight='weight', max_iter=200, tol=1e-06)
        except Exception:
            metrics['eigenvector'] = {node: 0.0 for node in G.nodes()}
    return metrics


def minmax(values, log=False):
    if not values:
        return {}
    prepared = {}
    for key, value in values.items():
        value = float(value or 0)
        prepared[key] = math.log1p(value) if log else value
    low = min(prepared.values())
    high = max(prepared.values())
    if math.isclose(low, high):
        return {key: 0.0 for key in prepared}
    return {key: (value - low) / (high - low) for key, value in prepared.items()}


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def relation_value(relations):
    text = normalize(relations)
    if not text:
        return 0.35
    if any(term in text for term in ['tax', 'license', 'monopol', 'govern', 'control', 'dispute', 'negotiate']):
        return 0.9
    if any(term in text for term in ['extract', 'supply', 'depend', 'transport']):
        return 0.75
    if any(term in text for term in ['trade', 'barter', 'exchange', 'sell', 'buy']):
        return 0.65
    if any(term in text for term in ['be', 'have', 'made', 'give']):
        return 0.4
    return 0.55


def sparse_cosine(left, right):
    if not left or not right:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = sum(value * right.get(key, 0.0) for key, value in left.items())
    if dot == 0:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def build_context_embeddings(G):
    """Create small graph-context embeddings without requiring external model downloads."""
    embeddings = {node: defaultdict(float) for node in G.nodes()}
    for source, target, data in G.edges(data=True):
        weight = math.log1p(float(data.get('weight', 1) or 1))
        relation = normalize(data.get('relation') or data.get('relations') or '')
        relation_parts = [part for part in relation.split('|') if part]

        embeddings[source][f'out_node:{target}'] += weight
        embeddings[target][f'in_node:{source}'] += weight
        for rel in relation_parts:
            embeddings[source][f'out_rel:{rel}'] += weight
            embeddings[target][f'in_rel:{rel}'] += weight
            embeddings[source][f'touches_rel:{rel}'] += weight * 0.5
            embeddings[target][f'touches_rel:{rel}'] += weight * 0.5

    return {node: dict(vector) for node, vector in embeddings.items()}


def apply_visual_attributes(G, metrics):
    if G.number_of_nodes() == 0:
        return

    degree_norm = minmax(metrics.get('weighted_degree', {}), log=True)
    pagerank_norm = minmax(metrics.get('pagerank', {}))
    betweenness_norm = minmax(metrics.get('betweenness', {}))
    eigenvector_norm = minmax(metrics.get('eigenvector', {}))

    prominence = {}
    for node in G.nodes():
        score = (
            0.38 * degree_norm.get(node, 0.0)
            + 0.27 * pagerank_norm.get(node, 0.0)
            + 0.20 * betweenness_norm.get(node, 0.0)
            + 0.15 * eigenvector_norm.get(node, 0.0)
        )
        prominence[node] = clamp(score)

    if max(prominence.values(), default=0.0) == 0.0:
        fallback = minmax(dict(G.degree()), log=True)
        prominence.update(fallback)

    type_colors = {
        'PERSON': '#d95f02',
        'COMMODITY': '#1b9e77',
        'LOCATION': '#386cb0',
        'INSTITUTION': '#7570b3',
        '': '#777777',
    }

    for node, data in G.nodes(data=True):
        node_type = data.get('type', '')
        score = prominence.get(node, 0.0)
        weighted_degree = float(metrics.get('weighted_degree', {}).get(node, 0.0) or 0.0)
        size = 8 + 34 * math.sqrt(score)
        if weighted_degree > 0 and size < 10:
            size = 10
        data['label'] = str(data.get('label') or node)
        data['prominence'] = round(score, 4)
        data['size'] = round(size, 2)
        data['weighted_degree'] = round(weighted_degree, 4)
        data['pagerank'] = round(float(metrics.get('pagerank', {}).get(node, 0.0) or 0.0), 6)
        data['betweenness'] = round(float(metrics.get('betweenness', {}).get(node, 0.0) or 0.0), 6)
        data['group'] = node_type or 'ENTITY'
        data['color'] = type_colors.get(node_type, '#777777')
        data['title'] = (
            f'{node}<br>'
            f'Type: {node_type or "ENTITY"}<br>'
            f'Prominence: {score:.3f}<br>'
            f'Weighted degree: {weighted_degree:.2f}<br>'
            f'PageRank: {data["pagerank"]:.6f}'
        )

    embeddings = build_context_embeddings(G)
    weights = [float(data.get('weight', 1) or 1) for _, _, data in G.edges(data=True)]
    max_weight = max(weights, default=1.0)
    relation_counts = Counter(normalize(data.get('relation') or data.get('relations') or '') for _, _, data in G.edges(data=True))
    total_edges = max(G.number_of_edges(), 1)
    max_relation_idf = max((math.log(total_edges / count) for count in relation_counts.values()), default=1.0) or 1.0

    for source, target, data in G.edges(data=True):
        observed = math.log1p(float(data.get('weight', 1) or 1)) / math.log1p(max_weight)
        relation = normalize(data.get('relation') or data.get('relations') or '')
        relation_idf = math.log(total_edges / max(relation_counts.get(relation, 1), 1)) / max_relation_idf
        embedded = sparse_cosine(embeddings.get(source, {}), embeddings.get(target, {}))
        endpoint_score = math.sqrt(prominence.get(source, 0.0) * prominence.get(target, 0.0))
        reciprocal_bonus = 0.08 if G.has_edge(target, source) else 0.0
        semantic_strength = clamp(
            0.42 * observed
            + 0.22 * endpoint_score
            + 0.18 * embedded
            + 0.10 * relation_idf
            + 0.08 * relation_value(relation)
            + reciprocal_bonus
        )
        width = 0.4 + 7.6 * (semantic_strength ** 1.4)
        data['semantic_strength'] = round(semantic_strength, 4)
        data['embedded_similarity'] = round(embedded, 4)
        data['endpoint_prominence'] = round(endpoint_score, 4)
        data['relation_rarity'] = round(relation_idf, 4)
        data['width'] = round(width, 2)
        data['value'] = round(semantic_strength * 10, 2)
        data['arrows'] = 'to'
        data['title'] = (
            f'{source} -> {target}<br>'
            f'Relation: {relation or data.get("relations", "")}<br>'
            f'Observed weight: {float(data.get("weight", 1) or 1):.2f}<br>'
            f'Semantic strength: {semantic_strength:.3f}<br>'
            f'Embedding similarity: {embedded:.3f}'
        )


def map_relation(relation_text, source, target):
    text = normalize(relation_text)
    for pattern, mapped in RELATION_PATTERNS:
        if re.search(pattern, text):
            if mapped == 'governs' and re.search(r'\b(control|dominate|own|possess|claim|rule|manage|administer)\b', text):
                if re.search(r'\b(government|state|administration|authority|office|bureau|commission|monastery|association|governmental)\b', source + ' ' + target):
                    return 'governs'
                return 'controls'
            if mapped == 'controls' and re.search(r'\b(government|state|administration|authority|office|bureau|commission|monastery|association|governmental)\b', source + ' ' + target):
                return 'governs'
            return mapped
    return None


def is_too_noisy_entity(entity_text):
    if not entity_text:
        return True
    if len(entity_text.split()) > 7:
        return True
    if re.search(r'\d', entity_text):
        return True
    if any(ch in entity_text for ch in ['\"', "'", '[', ']', '(', ')', ':', ';', '—', '–']):
        if len(entity_text.split()) > 3:
            return True
    if entity_text.startswith('none '):
        return True
    if entity_text.count(' ') > 6:
        return True
    return False


BAD_COMMODITY_TERMS = {
    'various', 'other', 'several', 'some', 'many', 'best', 'all', 'more', 'total', 'many',
}

BAD_LOCATION_TERMS = {
    'one of', 'best', 'valuable', 'recent', 'modern', 'northerly direction', 'information',
    'insights', 'famous', 'ancient', 'heavy', 'seasonal', 'main', 'general', 'large', 'small',
    'other', 'various', 'almost', 'nearby', 'farther', 'farther', 'early', 'late', 'central', 'new',
}


def classify_node(node):
    node = normalize(node)
    if not node or is_too_noisy_entity(node):
        return None, 0.0

    if NLP is not None:
        doc = NLP(node)
        for ent in doc.ents:
            if ent.text and ent.text.lower() == node:
                if ent.label_ == 'PERSON':
                    return 'PERSON', 1.0
                if ent.label_ in {'GPE', 'LOC', 'FAC'}:
                    return 'LOCATION', 1.0
                if ent.label_ == 'ORG':
                    return 'INSTITUTION', 1.0
                if ent.label_ in {'PRODUCT', 'WORK_OF_ART', 'NORP'}:
                    return 'COMMODITY', 1.0

    tokens = node.split()

    if any(term in node for term in COMMODITY_KEYWORDS):
        if ',' in node or ' or ' in node or ' and ' in node or len(tokens) > 4 or any(term in node for term in BAD_COMMODITY_TERMS):
            return None, 0.0
        return 'COMMODITY', 0.8

    if any(term in node for term in LOCATION_KEYWORDS):
        if ',' in node or len(tokens) > 7 or any(term in node for term in BAD_LOCATION_TERMS):
            return None, 0.0
        return 'LOCATION', 0.8

    if len(tokens) <= 4 and all(re.fullmatch(r"[a-z\-]+", token) for token in tokens):
        if any(token in PERSON_INDICATORS for token in tokens) and not any(token in LOCATION_KEYWORDS or token in COMMODITY_KEYWORDS for token in tokens):
            return 'PERSON', 0.7
        if len(tokens) <= 3 and sum(1 for token in tokens if token in STOP_WORDS) <= 1 and not any(token in LOCATION_KEYWORDS or token in COMMODITY_KEYWORDS or token in BAD_PERSON_TOKENS for token in tokens):
            if ',' not in node and ' or ' not in node and ' and ' not in node and ' of ' not in node and ' to ' not in node:
                return 'PERSON', 0.5

    return None, 0.0


def build_clean_graph(aggregated, relation_attrs):
    entity_types = {}
    cleaned_edges = []
    for (source, target), weight in aggregated.items():
        raw_relations = '|'.join(sorted(relation_attrs[(source, target)]))
        mapped = map_relation(raw_relations, source, target)
        if mapped is None:
            continue

        source_type, source_conf = classify_node(source)
        target_type, target_conf = classify_node(target)
        if source_type not in KEEP_ENTITY_TYPES or target_type not in KEEP_ENTITY_TYPES:
            continue

        entity_types[source] = {'type': source_type, 'confidence': source_conf}
        entity_types[target] = {'type': target_type, 'confidence': target_conf}
        cleaned_edges.append({
            'source': source,
            'target': target,
            'relation': mapped,
            'weight': weight,
            'raw_relations': raw_relations,
            'source_type': source_type,
            'target_type': target_type,
        })

    G_clean = nx.DiGraph()
    for node, attrs in entity_types.items():
        G_clean.add_node(node, type=attrs['type'], confidence=attrs['confidence'])
    for edge in cleaned_edges:
        G_clean.add_edge(
            edge['source'],
            edge['target'],
            weight=edge['weight'],
            relation=edge['relation'],
            relations=edge['relation'],
            raw_relations=edge['raw_relations'],
        )
    return G_clean, entity_types, cleaned_edges


def save_clean_entities(entity_types, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entities = []
    for node, attrs in sorted(entity_types.items()):
        entities.append({
            'entity': node,
            'type': attrs['type'],
            'confidence': round(attrs['confidence'], 2),
            'relevance': 1.0,
            'source': 'aggregated_graph',
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entities, f, indent=2, ensure_ascii=False)


def save_clean_relations(edges, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for edge in edges:
            item = {
                'subject': edge['source'],
                'relation': edge['relation'],
                'object': edge['target'],
                'confidence': round(edge.get('semantic_strength', min(edge['weight'] / 10.0, 1.0)), 2),
                'evidence': edge['raw_relations'],
                'document': 'aggregated_csvs',
                'weight': edge['weight'],
                'semantic_strength': edge.get('semantic_strength', ''),
                'embedded_similarity': edge.get('embedded_similarity', ''),
            }
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def save_clean_edges_csv(edges, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Source',
            'Target',
            'MappedRelation',
            'Weight',
            'SemanticStrength',
            'EmbeddedSimilarity',
            'VisualWidth',
            'RawRelations',
            'SourceType',
            'TargetType',
        ])
        for edge in sorted(edges, key=lambda x: (-x.get('semantic_strength', 0), -x['weight'])):
            writer.writerow([
                edge['source'],
                edge['target'],
                edge['relation'],
                edge['weight'],
                edge.get('semantic_strength', ''),
                edge.get('embedded_similarity', ''),
                edge.get('width', ''),
                edge['raw_relations'],
                edge['source_type'],
                edge['target_type'],
            ])


def save_metrics(metrics, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['node', 'weighted_degree', 'weighted_in_degree', 'weighted_out_degree', 'pagerank', 'betweenness', 'closeness', 'eigenvector']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        nodes = set()
        for metric in metrics.values():
            nodes.update(metric.keys())
        for node in sorted(nodes):
            writer.writerow({
                'node': node,
                'weighted_degree': metrics['weighted_degree'].get(node, 0),
                'weighted_in_degree': metrics['weighted_in_degree'].get(node, 0),
                'weighted_out_degree': metrics['weighted_out_degree'].get(node, 0),
                'pagerank': metrics['pagerank'].get(node, 0),
                'betweenness': metrics['betweenness'].get(node, 0),
                'closeness': metrics['closeness'].get(node, 0),
                'eigenvector': metrics['eigenvector'].get(node, 0),
            })


import xml.etree.ElementTree as ET
from xml.dom import minidom


def sanitize_graphml_id(value, existing_ids, fallback_prefix='n'):
    name = normalize(value)
    name = re.sub(r'[^a-z0-9_\-\.]+', '_', name)
    name = re.sub(r'^([^a-z_]+)', 'n_', name)
    if not name:
        name = fallback_prefix
    base = name
    suffix = 1
    while name in existing_ids:
        name = f'{base}_{suffix}'
        suffix += 1
    existing_ids.add(name)
    return name


def save_graphml(G, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    graphml = ET.Element('graphml', {
        'xmlns': 'http://graphml.graphdrawing.org/xmlns',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd',
    })

    key_specs = [
        ('d0', 'edge', 'weight', 'double'),
        ('d1', 'edge', 'relations', 'string'),
        ('d2', 'node', 'label', 'string'),
        ('d3', 'node', 'type', 'string'),
        ('d4', 'node', 'confidence', 'double'),
        ('d5', 'node', 'weighted_degree', 'double'),
        ('d6', 'node', 'pagerank', 'double'),
        ('d7', 'node', 'betweenness', 'double'),
        ('d8', 'node', 'prominence', 'double'),
        ('d9', 'node', 'size', 'double'),
        ('d10', 'node', 'title', 'string'),
        ('d11', 'node', 'group', 'string'),
        ('d12', 'node', 'color', 'string'),
        ('d13', 'edge', 'relation', 'string'),
        ('d14', 'edge', 'raw_relations', 'string'),
        ('d15', 'edge', 'semantic_strength', 'double'),
        ('d16', 'edge', 'embedded_similarity', 'double'),
        ('d17', 'edge', 'endpoint_prominence', 'double'),
        ('d18', 'edge', 'relation_rarity', 'double'),
        ('d19', 'edge', 'width', 'double'),
        ('d20', 'edge', 'value', 'double'),
        ('d21', 'edge', 'title', 'string'),
        ('d22', 'edge', 'arrows', 'string'),
    ]
    keys_by_scope_name = {}
    for key_id, scope, name, attr_type in key_specs:
        ET.SubElement(graphml, 'key', id=key_id, **{'for': scope, 'attr.name': name, 'attr.type': attr_type})
        keys_by_scope_name[(scope, name)] = key_id

    graph = ET.SubElement(graphml, 'graph', edgedefault='directed')
    node_id_map = {}
    existing_ids = set()
    for node in G.nodes():
        nid = sanitize_graphml_id(node, existing_ids)
        node_id_map[node] = nid
        node_elem = ET.SubElement(graph, 'node', id=nid)
        node_attrs = {'label': str(node)}
        node_attrs.update(G.nodes[node])
        for name, value in node_attrs.items():
            key_id = keys_by_scope_name.get(('node', name))
            if key_id is None or value is None:
                continue
            ET.SubElement(node_elem, 'data', key=key_id).text = str(value)

    for u, v, data in G.edges(data=True):
        edge_elem = ET.SubElement(graph, 'edge', source=node_id_map[u], target=node_id_map[v])
        edge_attrs = dict(data)
        edge_attrs.setdefault('relations', edge_attrs.get('relation', ''))
        for name, value in edge_attrs.items():
            key_id = keys_by_scope_name.get(('edge', name))
            if key_id is None or value is None:
                continue
            ET.SubElement(edge_elem, 'data', key=key_id).text = str(value)

    rough_string = ET.tostring(graphml, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent='  ')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(pretty)


def save_aggregated_edges(aggregated, relation_attrs, path, graph=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Source', 'Target', 'TotalWeight', 'SemanticStrength', 'EmbeddedSimilarity', 'VisualWidth', 'Relations'])
        rows = []
        for (source, target), weight in aggregated.items():
            data = graph.get_edge_data(source, target, default={}) if graph is not None else {}
            rows.append((
                source,
                target,
                weight,
                data.get('semantic_strength', ''),
                data.get('embedded_similarity', ''),
                data.get('width', ''),
                '|'.join(sorted(relation_attrs[(source, target)])),
            ))
        for row in sorted(rows, key=lambda x: (-(x[3] or 0), -x[2])):
            writer.writerow(row)


if __name__ == '__main__':
    weighted_files = find_weighted_csvs(RESULTS_ROOT)
    print('Found weighted graph files:', weighted_files)
    edges = load_edges(weighted_files)
    aggregated, relation_attrs, source_paths = aggregate_edges(edges)

    G = build_graph(aggregated, relation_attrs)
    metrics = compute_metrics(G)
    apply_visual_attributes(G, metrics)
    save_metrics(metrics, os.path.join(OUTPUT_DIR, 'network_metrics.csv'))
    save_graphml(G, os.path.join(OUTPUT_DIR, 'network.graphml'))
    save_aggregated_edges(aggregated, relation_attrs, os.path.join(OUTPUT_DIR, 'aggregated_edges.csv'), graph=G)

    G_clean, entity_types, cleaned_edges = build_clean_graph(aggregated, relation_attrs)
    if cleaned_edges:
        cleaned_metrics = compute_metrics(G_clean)
        apply_visual_attributes(G_clean, cleaned_metrics)
        for edge in cleaned_edges:
            data = G_clean.get_edge_data(edge['source'], edge['target'], default={})
            edge['semantic_strength'] = data.get('semantic_strength', '')
            edge['embedded_similarity'] = data.get('embedded_similarity', '')
            edge['width'] = data.get('width', '')
        save_metrics(cleaned_metrics, os.path.join(OUTPUT_DIR, 'cleaned_network_metrics.csv'))
        save_graphml(G_clean, os.path.join(OUTPUT_DIR, 'cleaned_network.graphml'))
        save_clean_entities(entity_types, os.path.join(OUTPUT_DIR, 'cleaned_entities.json'))
        save_clean_relations(cleaned_edges, os.path.join(OUTPUT_DIR, 'cleaned_relations.jsonl'))
        save_clean_edges_csv(cleaned_edges, os.path.join(OUTPUT_DIR, 'cleaned_aggregated_edges.csv'))
    else:
        print('No cleaned edges matched PERSON/COMMODITY/LOCATION and allowed relation mapping.')

    print('Saved outputs to', OUTPUT_DIR)
