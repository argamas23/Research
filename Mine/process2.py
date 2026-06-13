import re
import os
from collections import defaultdict, Counter

BUFFER_SIZE = 50
OUTPUT_FILE = "entity_cooccurrences.txt"

def parse_ner_file(ner_file_path):
    topic_entities = {}
    current_topic = None
    with open(ner_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("/"):
                current_topic = line
                topic_entities.setdefault(current_topic, [])
            elif "Relevance" in line and current_topic:
                match = re.match(r'^(.*?)\s+\(Relevance ([\d.]+) \| Confidence ([\d.]+)\)', line)
                if match:
                    entity = match.group(1).strip().lower()
                    topic_entities[current_topic].append(entity)
    return topic_entities

def load_topic_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def get_corpus_words(corpus_file):
    with open(corpus_file, 'r', encoding='utf-8') as f:
        text = f.read()
        words = text.split()
    return words

import string

def aggregate_cooccurrences(corpus_words, selected_entities, selected_topic_map, all_entities, all_topic_map):
    """Scan corpus and aggregate co-occurring entities by anchor entity."""
    anchor_data = defaultdict(lambda: {
        "topic": "",
        "co_counts": Counter(),
        "example_contexts": []
    })

    # Strip punctuation from both ends of the corpus words for matching
    cleaned_words = [w.strip(string.punctuation).lower() for w in corpus_words]

    # Pre-process entities into first-word buckets, with longest phrases checked first.
    sel_ent_tuples = defaultdict(list)
    for ent in selected_entities:
        ent_tuple = tuple(ent.split())
        if ent_tuple:
            sel_ent_tuples[ent_tuple[0]].append((ent_tuple, ent))
    all_ent_tuples = defaultdict(list)
    for ent in all_entities:
        ent_tuple = tuple(ent.split())
        if ent_tuple:
            all_ent_tuples[ent_tuple[0]].append((ent_tuple, ent))

    for ent_list in sel_ent_tuples.values():
        ent_list.sort(key=lambda x: len(x[0]), reverse=True)
    for ent_list in all_ent_tuples.values():
        ent_list.sort(key=lambda x: len(x[0]), reverse=True)

    i = 0
    while i < len(cleaned_words):
        matched = False
        for ent_tuple, orig_ent in sel_ent_tuples.get(cleaned_words[i], []):
            n = len(ent_tuple)
            if i + n <= len(cleaned_words) and tuple(cleaned_words[i:i+n]) == ent_tuple:
                anchor_entity = orig_ent
                anchor_topic = selected_topic_map[anchor_entity]

                start = max(0, i - BUFFER_SIZE)
                end = min(len(corpus_words), i + n + BUFFER_SIZE)
                window_words = corpus_words[start:end]
                window_cleaned = cleaned_words[start:end]
                window_text = " ".join(window_words)

                found_entities = set()
                j = 0
                while j < len(window_cleaned):
                    found_co = False
                    for a_ent_tuple, a_orig_ent in all_ent_tuples.get(window_cleaned[j], []):
                        an = len(a_ent_tuple)
                        if j + an <= len(window_cleaned) and tuple(window_cleaned[j:j+an]) == a_ent_tuple:
                            if a_orig_ent != anchor_entity:
                                found_entities.add(a_orig_ent)
                            j += an
                            found_co = True
                            break
                    if not found_co:
                        j += 1

                if found_entities:
                    anchor_data[anchor_entity]["topic"] = anchor_topic
                    anchor_data[anchor_entity]["example_contexts"].append(window_text)
                    for ent in found_entities:
                        anchor_data[anchor_entity]["co_counts"][ent] += 1
                
                i += n
                matched = True
                break

        if not matched:
            i += 1

    return anchor_data

import argparse

def main():
    parser = argparse.ArgumentParser(description="Aggregate entity co-occurrences.")
    parser.add_argument("--corpus_file", required=True, help="Path to corpus text file.")
    parser.add_argument("--ner_file", required=True, help="Path to NER results file.")
    parser.add_argument("--selected_topics", required=True, help="Path to selected topics file.")
    parser.add_argument("--all_topics", required=True, help="Path to all unique topics file.")
    parser.add_argument("--output_file", required=True, help="Path to output entity co-occurrences file.")
    args = parser.parse_args()

    corpus_file = args.corpus_file
    ner_file = args.ner_file
    output_file = args.output_file

    selected_topics = load_topic_list(args.selected_topics)
    all_topics = load_topic_list(args.all_topics)

    print("\nParsing NER file...")
    topic_entities_map = parse_ner_file(ner_file)

    selected_entities = set()
    selected_entity_topic_map = {}
    all_entities = set()
    all_entity_topic_map = {}

    for topic, entities in topic_entities_map.items():
        for ent in entities:
            all_entities.add(ent)
            all_entity_topic_map[ent] = topic
            if topic in selected_topics:
                selected_entities.add(ent)
                selected_entity_topic_map[ent] = topic

    print(f"Selected entities: {len(selected_entities)} / All entities: {len(all_entities)}")
    print("Reading and scanning corpus...")

    corpus_words = get_corpus_words(corpus_file)
    anchor_data = aggregate_cooccurrences(
        corpus_words,
        selected_entities,
        selected_entity_topic_map,
        all_entities,
        all_entity_topic_map
    )

    print(f"\nWriting results to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as out:
        for anchor, data in anchor_data.items():
            out.write(f"Anchor Entity: {anchor} [{data['topic']}]\n")
            out.write("Example Context:\n")
            out.write(f"...{data['example_contexts'][0]}...\n\n")

            out.write("Co-occurring Entities (sorted by frequency):\n")
            for entity, count in data["co_counts"].most_common():
                topic = all_entity_topic_map.get(entity, "Unknown")
                out.write(f"  ↳ {entity} [{topic}] — {count} times\n")
            out.write("-" * 80 + "\n")

    print(f"✔ Done. Results saved to '{output_file}'.")

if __name__ == "__main__":
    main()
