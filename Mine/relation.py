import ollama
import json
import csv
import re
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# --- Configuration ---
# Global defaults (can be overridden by args)
MODEL_NAME = "llama3"

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

# --- 2. Triple Extraction Logic ---

def extract_triples_ollama(chunk, topics):
    """Extracts S-P-O triples using local Llama 3 with JSON enforcement."""
    prompt = f"""
    Analyze the text and extract Subject-Relation-Object triples.
    RESEARCH TOPICS: {', '.join(topics)}
    
    RULES:
    1. Normalize 'Relation' (e.g., TAXATION, TRADE, GOVERNANCE).
    2. Ensure Subject, Relation, and Object are SINGLE strings, not lists.
    3. Output ONLY valid JSON: {{"triples": [{{"subject": "...", "relation": "...", "object": "..."}}]}}
    
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
            r = get_safe_str(t, 'relation').strip().upper()
            o = get_safe_str(t, 'object').strip().lower()

            if s and r and o:
                master_graph[(s, r, o)] += 1

    print("Step 3: Saving weighted graph...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Relation", "Target", "Weight"])
        for (s, r, o), weight in sorted(master_graph.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([s, r, o, weight])

if __name__ == "__main__":
    main()
