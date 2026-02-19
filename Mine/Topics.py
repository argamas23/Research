import re
import os

def extract_topics_from_ner_file(ner_file_path):
    topics = set()
    
    with open(ner_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            match = re.match(r'^\/(.+)', line)
            if match:
                topic = match.group(1).strip()
                topics.add(topic)
    
    return topics

def load_existing_topics(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip().lstrip("/") for line in f if line.strip())

def save_topics_to_file(topics, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for topic in sorted(topics):
            f.write(f"/{topic}\n")

import argparse

def main():
    parser = argparse.ArgumentParser(description="Extract and update unique topics from NER results.")
    parser.add_argument("--ner_file", required=True, help="Path to NER results file.")
    parser.add_argument("--output_file", required=True, help="Path to output unique topics file.")
    args = parser.parse_args()

    ner_path = args.ner_file
    output_path = args.output_file

    print("\n[1] Extracting new topics from NER...")
    new_topics = extract_topics_from_ner_file(ner_path)
    print(f"  ↳ Found {len(new_topics)} new topics.")

    print("\n[2] Loading existing topic list...")
    existing_topics = load_existing_topics(output_path)
    print(f"  ↳ Found {len(existing_topics)} existing topics.")

    combined_topics = existing_topics.union(new_topics)
    print(f"\n[3] Combined total (deduplicated): {len(combined_topics)}")

    print(f"\n[4] Saving sorted topic list to: {output_path}")
    save_topics_to_file(combined_topics, output_path)

    print(f"\n✔️ Done. Alphabetically sorted unique topics written to '{output_path}'.")

if __name__ == "__main__":
    main()
