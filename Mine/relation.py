import ollama
import json
import csv
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# --- Configuration ---
# Global defaults (can be overridden by args)
MODEL_NAME = "llama3"
ALLOWED_RELATIONS = {
    "trades_with",
    "exchanges_for",
    "extracts_from",
    "transports_via",
    "taxes",
    "regulates",
    "governs",
    "controls",
    "disputes",
    "licenses",
    "monopolizes",
    "supplies",
    "depends_on",
    "connects_to",
    "migrates_through",
    "administers",
    "negotiates_with",
}

RELATION_ALIASES = {
    "trade": "trades_with",
    "trades": "trades_with",
    "trade_with": "trades_with",
    "trade with": "trades_with",
    "traded_in": "trades_with",
    "barter": "exchanges_for",
    "exchange": "exchanges_for",
    "exchanges": "exchanges_for",
    "collect": "extracts_from",
    "extract": "extracts_from",
    "remove": "extracts_from",
    "harvest": "extracts_from",
    "bring": "transports_via",
    "carry": "transports_via",
    "haul": "transports_via",
    "transport": "transports_via",
    "tax": "taxes",
    "license": "licenses",
    "permit": "licenses",
    "supply": "supplies",
    "provide": "supplies",
    "control": "controls",
    "claim": "disputes",
    "dispute": "disputes",
    "settle": "negotiates_with",
    "negotiate": "negotiates_with",
}

# --- 1. Helper Functions ---

def load_topics(filepath):
    """Loads the research topics to guide LLM extraction."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def load_anchor_pairs(filepath):
    """Parses your entity_cooccurrences.txt to find validated pairs."""
    pairs = set()
    current_anchor = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "Anchor Entity:" in line:
                current_anchor = line.split("Anchor Entity:")[1].split("[")[0].strip().lower()
            elif "↳" in line and current_anchor:
                co_ent = line.split("↳")[1].split("[")[0].strip().lower()
                pairs.add(tuple(sorted((current_anchor, co_ent))))
    return pairs

def get_safe_str(data, key):
    """Prevents AttributeError by converting list outputs to strings."""
    val = data.get(key, "")
    if isinstance(val, list):
        return " ".join([str(item) for item in val]) #
    return str(val)


def normalize_relation(value):
    relation = get_safe_str({"relation": value}, "relation").strip().lower()
    relation = relation.replace("-", "_").replace(" ", "_")
    relation = re.sub(r"[^a-z_]", "", relation)
    relation = RELATION_ALIASES.get(relation, relation)
    if relation in ALLOWED_RELATIONS:
        return relation
    return ""


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# --- 2. Triple Extraction Logic ---

def extract_triples_ollama(chunk, topics):
    """Extracts schema-constrained S-P-O triples using local Llama 3."""
    relation_list = ", ".join(sorted(ALLOWED_RELATIONS))
    prompt = f"""
    Analyze the text and extract historically meaningful Subject-Relation-Object triples.
    RESEARCH TOPICS: {', '.join(topics)}
    ALLOWED RELATIONS: {relation_list}
    
    RULES:
    1. Use ONLY one relation from ALLOWED RELATIONS.
    2. Subject, relation, object, and evidence_sentence must be SINGLE strings, not lists.
    3. evidence_sentence must be copied from the provided text and must justify the relation.
    4. confidence must be a number from 0.0 to 1.0.
    5. Do not infer relations from co-occurrence alone. If the text does not support a relation, omit it.
    6. Output ONLY valid JSON:
       {{"triples": [{{"subject": "...", "relation": "trades_with", "object": "...", "evidence_sentence": "...", "confidence": 0.80}}]}}
    
    TEXT: {chunk}
    """
    try:
        # Use latest ollama chat method
        response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'user', 'content': prompt}])
        content = response['message']['content']
        
        # Regex to find JSON block in case of conversational filler
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group()).get("triples", [])
    except Exception as e:
        print(f"Ollama Error: {e}")
    return []


def process_chunk(index, total, chunk, topics):
    """Run one LLM extraction job and keep enough metadata for ordered logging."""
    triples = extract_triples_ollama(chunk, topics)
    return index, total, triples


def sidecar_jsonl_path(csv_path):
    root, _ = os.path.splitext(csv_path)
    return root + ".jsonl"

# --- 3. Main Pipeline ---

import argparse

def main():
    parser = argparse.ArgumentParser(description="Extract triples using LLM.")
    parser.add_argument("--corpus_file", required=True, help="Path to corpus text file.")
    parser.add_argument("--coocc_file", required=True, help="Path to entity co-occurrences file.")
    parser.add_argument("--topics_file", required=True, help="Path to selected topics file.")
    parser.add_argument("--output_file", required=True, help="Path to output CSV file.")
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(4, (os.cpu_count() or 2))),
        help="Number of concurrent Ollama requests. Use 1 for sequential processing.",
    )
    args = parser.parse_args()

    CORPUS_FILE = args.corpus_file
    COOCC_FILE = args.coocc_file
    TOPICS_FILE = args.topics_file
    OUTPUT_FILE = args.output_file

    print("Step 1: Loading resources...")
    topics = load_topics(TOPICS_FILE)
    anchor_pairs = load_anchor_pairs(COOCC_FILE)
    
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        corpus = f.read()

    # Chunking corpus based on relevant anchor pairs to save context window
    sentences = re.split(r'(?<=[.!?])\s+', corpus)
    relevant_chunks = []
    current_chunk = ""
    for sent in sentences:
        if any(p[0] in sent.lower() and p[1] in sent.lower() for p in anchor_pairs):
            if len(current_chunk) + len(sent) < 3000:
                current_chunk += sent + " "
            else:
                relevant_chunks.append(current_chunk)
                current_chunk = sent + " "
    if current_chunk: relevant_chunks.append(current_chunk)

    workers = max(1, args.workers)
    print(f"Step 2: Processing {len(relevant_chunks)} chunks via {MODEL_NAME} with {workers} worker(s)...")
    master_graph = defaultdict(int)
    evidence_by_triple = defaultdict(list)

    chunk_results = {}
    if workers == 1 or len(relevant_chunks) <= 1:
        for i, chunk in enumerate(relevant_chunks):
            print(f"Processing chunk {i+1}/{len(relevant_chunks)}...")
            _, _, triples = process_chunk(i, len(relevant_chunks), chunk, topics)
            chunk_results[i] = triples
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(process_chunk, i, len(relevant_chunks), chunk, topics)
                for i, chunk in enumerate(relevant_chunks)
            ]
            for future in as_completed(futures):
                i, total, triples = future.result()
                print(f"Finished chunk {i+1}/{total} ({len(triples)} triples).")
                chunk_results[i] = triples

    for i in sorted(chunk_results):
        for t in chunk_results[i]:
            if not isinstance(t, dict):
                continue

            # Robust extraction to avoid 'list has no attribute strip'
            s = get_safe_str(t, 'subject').strip().lower()
            r = normalize_relation(t.get('relation', ''))
            o = get_safe_str(t, 'object').strip().lower()
            evidence = get_safe_str(t, 'evidence_sentence').strip()
            confidence = safe_float(t.get('confidence'), 0.0)

            if s and r and o:
                master_graph[(s, r, o)] += 1
                evidence_by_triple[(s, r, o)].append(
                    {
                        "sentence": evidence,
                        "confidence": confidence,
                        "chunk_index": i,
                    }
                )

    print("Step 3: Saving weighted graph and evidence sidecar...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Relation", "Target", "Weight", "Evidence", "Confidence"])
        for (s, r, o), weight in sorted(master_graph.items(), key=lambda x: x[1], reverse=True):
            evidence_items = evidence_by_triple.get((s, r, o), [])
            sentences = [item["sentence"] for item in evidence_items if item["sentence"]]
            avg_confidence = 0.0
            if evidence_items:
                avg_confidence = sum(item["confidence"] for item in evidence_items) / len(evidence_items)
            writer.writerow([s, r, o, weight, " | ".join(sentences[:3]), round(avg_confidence, 3)])

    with open(sidecar_jsonl_path(OUTPUT_FILE), "w", encoding="utf-8") as f:
        for (s, r, o), weight in sorted(master_graph.items(), key=lambda x: x[1], reverse=True):
            for item in evidence_by_triple.get((s, r, o), []):
                f.write(
                    json.dumps(
                        {
                            "subject": s,
                            "relation": r,
                            "object": o,
                            "weight": weight,
                            "confidence": round(item["confidence"], 3),
                            "evidence_sentence": item["sentence"],
                            "chunk_index": item["chunk_index"],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

if __name__ == "__main__":
    main()
