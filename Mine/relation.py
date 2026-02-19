import ollama
import json
import csv
import re
import time
from collections import defaultdict

# --- Configuration ---
CORPUS_FILE = "/home/samagra-bharti/Desktop/Research/corpus/Santiago_Lazcano.txt"
COOCC_FILE = "/home/samagra-bharti/Desktop/Research/Mine/entity_cooccurrences.txt"
TOPICS_FILE = "Selected_Topics.txt"
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

# --- 3. Main Pipeline ---

def main():
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

    print(f"Step 2: Processing {len(relevant_chunks)} chunks via {MODEL_NAME}...")
    master_graph = defaultdict(int)

    for i, chunk in enumerate(relevant_chunks):
        print(f"Processing chunk {i+1}/{len(relevant_chunks)}...")
        triples = extract_triples_ollama(chunk, topics)
        
        for t in triples:
            if not isinstance(t, dict): continue
            
            # Robust extraction to avoid 'list has no attribute strip'
            s = get_safe_str(t, 'subject').strip().lower()
            r = get_safe_str(t, 'relation').strip().upper()
            o = get_safe_str(t, 'object').strip().lower()
            
            if s and r and o:
                master_graph[(s, r, o)] += 1

    print("Step 3: Saving weighted graph...")
    with open("weighted_knowledge_graph.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Relation", "Target", "Weight"])
        for (s, r, o), weight in sorted(master_graph.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([s, r, o, weight])

if __name__ == "__main__":
    main()