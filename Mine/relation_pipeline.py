# import spacy
# import re
# import csv
# from collections import defaultdict, Counter
# import os

# # -----------------------------
# # Load spaCy model
# # -----------------------------
# nlp = spacy.load("en_core_web_sm")

# # -----------------------------
# # Basic cleaning
# # -----------------------------
# def clean_text(text):
#     text = re.sub(r"\s+", " ", text)
#     return text.strip()

# def clean_entity(text):
#     text = text.strip()
#     text = re.sub(r"[^\w\s\-]", "", text)
#     return text.lower()

# # -----------------------------
# # Extract SVO relations
# # -----------------------------
# def extract_triples(text, doc_id="doc"):
#     triples = []
#     doc = nlp(text)

#     for sent in doc.sents:
#         sentence_doc = nlp(sent.text)

#         if len(sentence_doc.ents) < 2:
#             continue

#         for token in sentence_doc:
#             if token.pos_ == "VERB":

#                 subject = None
#                 obj = None

#                 for child in token.children:
#                     if child.dep_ == "nsubj":
#                         subject = clean_entity(child.text)

#                 for child in token.children:
#                     if child.dep_ in ["dobj", "attr"]:
#                         obj = clean_entity(child.text)

#                 for child in token.children:
#                     if child.dep_ == "prep":
#                         for subchild in child.children:
#                             if subchild.dep_ == "pobj":
#                                 obj = clean_entity(subchild.text)

#                 if subject and obj:
#                     triples.append({
#                         "subject": subject,
#                         "relation": token.lemma_.lower(),
#                         "object": obj,
#                         "sentence": sent.text.strip(),
#                         "doc_id": doc_id
#                     })

#     return triples


# # -----------------------------
# # Load anchor entity pairs
# # -----------------------------
# def load_anchor_pairs(filepath):
#     pairs = set()
#     current_anchor = None

#     with open(filepath, "r", encoding="utf-8") as f:
#         for line in f:
#             line = line.strip()

#             if line.startswith("Anchor Entity:"):
#                 current_anchor = clean_entity(
#                     line.split("Anchor Entity:")[1].split("[")[0]
#                 )

#             elif line.startswith("↳") and current_anchor:
#                 entity = clean_entity(
#                     line.split("↳")[1].split("[")[0]
#                 )
#                 pairs.add((current_anchor, entity))

#     return pairs


# # -----------------------------
# # Extract relevant sentences from FULL corpus
# # -----------------------------
# def extract_sentences_from_corpus(corpus_text, anchor_pairs):
#     candidate_text = ""
#     doc = nlp(corpus_text)

#     for sent in doc.sents:
#         sent_lower = sent.text.lower()

#         for subj, obj in anchor_pairs:
#             if subj in sent_lower and obj in sent_lower:
#                 candidate_text += sent.text + " "
#                 break

#     return candidate_text


# # -----------------------------
# # Aggregate triples (add weight)
# # -----------------------------
# def aggregate_triples(triples):
#     triple_dict = defaultdict(lambda: {"count": 0, "sentence": "", "doc_id": ""})

#     for triple in triples:
#         key = (triple["subject"], triple["relation"], triple["object"])

#         triple_dict[key]["count"] += 1
#         triple_dict[key]["sentence"] = triple["sentence"]
#         triple_dict[key]["doc_id"] = triple["doc_id"]

#     aggregated = []

#     for (sub, rel, obj), data in triple_dict.items():
#         aggregated.append({
#             "subject": sub,
#             "relation": rel,
#             "object": obj,
#             "weight": data["count"],
#             "example_sentence": data["sentence"],
#             "doc_id": data["doc_id"]
#         })

#     return aggregated


# # -----------------------------
# # Filter obvious noise
# # -----------------------------
# def filter_triples(triples):

#     NOISE_VERBS = {
#         "write", "publish", "say", "describe",
#         "mention", "argue", "note", "report",
#         "include", "appear"
#     }

#     filtered = []

#     for t in triples:

#         if t["relation"] in NOISE_VERBS:
#             continue

#         if len(t["subject"]) < 3 or len(t["object"]) < 3:
#             continue

#         if t["subject"] == t["object"]:
#             continue

#         filtered.append(t)

#     return filtered


# # -----------------------------
# # Save CSV
# # -----------------------------
# def save_csv(data, filename, fieldnames):
#     with open(filename, "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         for row in data:
#             writer.writerow(row)


# # -----------------------------
# # MAIN
# # -----------------------------
# if __name__ == "__main__":

#     FULL_CORPUS_FILE = "/home/samagra-bharti/Desktop/Research/corpus/Santiago_Lazcano.txt"
#     COOCC_FILE = "/home/samagra-bharti/Desktop/Research/Mine/entity_cooccurrences.txt"

#     print("Loading anchor entity pairs...")
#     anchor_pairs = load_anchor_pairs(COOCC_FILE)
#     print("Total anchor pairs:", len(anchor_pairs))

#     print("Loading full corpus...")
#     with open(FULL_CORPUS_FILE, "r", encoding="utf-8") as f:
#         corpus_text = f.read()

#     print("Extracting relevant sentences from corpus...")
#     filtered_text = extract_sentences_from_corpus(corpus_text, anchor_pairs)

#     print("Extracting triples from filtered corpus...")
#     raw_triples = extract_triples(filtered_text, doc_id="full_corpus")

#     print("Total raw triples:", len(raw_triples))

#     save_csv(
#         raw_triples,
#         "all_triples_raw.csv",
#         ["subject", "relation", "object", "sentence", "doc_id"]
#     )

#     aggregated = aggregate_triples(raw_triples)
#     print("Unique triples after aggregation:", len(aggregated))

#     verb_counter = Counter([t["relation"] for t in raw_triples])
#     verb_data = [{"verb": k, "frequency": v} for k, v in verb_counter.items()]
#     verb_data = sorted(verb_data, key=lambda x: x["frequency"], reverse=True)

#     save_csv(verb_data, "verb_frequency.csv", ["verb", "frequency"])

#     print("Top 20 verbs:")
#     for v in verb_data[:20]:
#         print(v)

#     filtered = filter_triples(aggregated)
#     print("Final filtered triples:", len(filtered))

#     save_csv(
#         filtered,
#         "knowledge_graph_triples_filtered.csv",
#         ["subject", "relation", "object", "weight", "example_sentence", "doc_id"]
#     )

#     print("Pipeline complete.")

import json
import csv
import re
from collections import defaultdict
from openai import OpenAI

# Initialize LLM Client
client = OpenAI(api_key="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")

def load_topics(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def load_anchor_pairs(file_path):
    """Parses your co-occurrence file to find confirmed entity pairs."""
    pairs = set()
    current_anchor = None
    with open(file_path, 'r') as f:
        for line in f:
            if "Anchor Entity:" in line:
                current_anchor = line.split("Anchor Entity:")[1].split("[")[0].strip().lower()
            elif "↳" in line and current_anchor:
                co_ent = line.split("↳")[1].split("[")[0].strip().lower()
                pairs.add(tuple(sorted((current_anchor, co_ent))))
    return pairs

def extract_triples_llm(context_text, topics):
    """Uses LLM to extract normalized triples based on research topics."""
    prompt = f"""
    You are an expert historian. Extract knowledge graph triples (Subject, Relation, Object) from the text.
    
    RESEARCH TOPICS TO PRIORITIZE: {", ".join(topics)}
    
    INSTRUCTIONS:
    1. Normalize 'Relation' to a concise, capitalized category (e.g., 'TRADE_IN', 'TAXED_BY', 'LOCATED_IN').
    2. Focus on historical and economic connections.
    3. Output ONLY valid JSON: {{"triples": [{{"subject": "...", "relation": "...", "object": "..."}}]}}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Text: {context_text}"}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content).get("triples", [])
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return []

def main():
    # File Paths
    CORPUS_FILE = "/home/samagra-bharti/Desktop/Research/corpus/Santiago_Lazcano.txt"
    COOCC_FILE = "entity_cooccurrences.txt"
    TOPICS_FILE = "Selected_Topics.txt"

    print("Loading data...")
    topics = load_topics(TOPICS_FILE)
    anchor_pairs = load_anchor_pairs(COOCC_FILE)
    
    with open(CORPUS_FILE, 'r') as f:
        corpus = f.read()

    # Find relevant sentences from the corpus using anchor pairs
    # This reduces noise and token cost
    sentences = re.split(r'(?<=[.!?])\s+', corpus)
    relevant_chunks = []
    current_chunk = ""
    
    for sent in sentences:
        sent_lower = sent.lower()
        if any(p[0] in sent_lower and p[1] in sent_lower for p in anchor_pairs):
            current_chunk += sent + " "
            if len(current_chunk) > 3000: # Batch into 3k char chunks for LLM
                relevant_chunks.append(current_chunk)
                current_chunk = ""

    print(f"Processing {len(relevant_chunks)} context-rich chunks...")
    
    all_triples = []
    for chunk in relevant_chunks:
        triples = extract_triples_llm(chunk, topics)
        all_triples.extend(triples)

    # Weighted Aggregation
    weighted_graph = defaultdict(int)
    for t in all_triples:
        key = (t['subject'].lower(), t['relation'].upper(), t['object'].lower())
        weighted_graph[key] += 1

    # Save Results
    with open("weighted_knowledge_graph.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Relation", "Object", "Weight"])
        for (s, r, o), weight in weighted_graph.items():
            writer.writerow([s, r, o, weight])

    print("Success: weighted_knowledge_graph.csv created.")

if __name__ == "__main__":
    main()