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
                topic_entities[current_topic] = []
            elif "Relevance" in line and current_topic:
                match = re.match(r'^([\w\s\-]+)\s+\(Relevance ([\d.]+) \| Confidence ([\d.]+)\)', line)
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

def aggregate_cooccurrences(corpus_words, selected_entities, selected_topic_map, all_entities, all_topic_map):
    """Scan corpus and aggregate co-occurring entities by anchor entity."""
    anchor_data = defaultdict(lambda: {
        "topic": "",
        "co_counts": Counter(),
        "example_contexts": []
    })

    for idx, word in enumerate(corpus_words):
        word_lower = word.lower()
        if word_lower in selected_entities:
            anchor_entity = word_lower
            anchor_topic = selected_topic_map[anchor_entity]

            start = max(0, idx - BUFFER_SIZE)
            end = min(len(corpus_words), idx + BUFFER_SIZE + 1)
            window = corpus_words[start:end]
            window_text = " ".join(window)

            found_entities = set()
            for w in window:
                w_l = w.lower()
                if w_l in all_entities and w_l != anchor_entity:
                    found_entities.add(w_l)

            if found_entities:
                anchor_data[anchor_entity]["topic"] = anchor_topic
                anchor_data[anchor_entity]["example_contexts"].append(window_text)
                for ent in found_entities:
                    anchor_data[anchor_entity]["co_counts"][ent] += 1

    return anchor_data

def main():
    corpus_file = input("Enter path to corpus TXT file: ").strip()
    ner_file = input("Enter path to NER file: ").strip()

    selected_topics = load_topic_list("Selected_Topis.txt")
    all_topics = load_topic_list("unique_topics.txt")

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

    print(f"\nWriting results to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for anchor, data in anchor_data.items():
            out.write(f"Anchor Entity: {anchor} [{data['topic']}]\n")
            out.write("Example Context:\n")
            out.write(f"...{data['example_contexts'][0]}...\n\n")

            out.write("Co-occurring Entities (sorted by frequency):\n")
            for entity, count in data["co_counts"].most_common():
                topic = all_entity_topic_map.get(entity, "Unknown")
                out.write(f"  ↳ {entity} [{topic}] — {count} times\n")
            out.write("-" * 80 + "\n")

    print("✔ Done. Results saved to 'entity_cooccurrences.txt'.")

if __name__ == "__main__":
    main()
