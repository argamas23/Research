#!/usr/bin/env python3
import spacy
import sys
from pathlib import Path

# 1. load the transformer‑based NER model
#    (make sure you’ve run: python3 -m spacy download en_core_web_trf)
try:
    nlp = spacy.load("en_core_web_trf")
except OSError:
    print(
        "Model en_core_web_trf not found. Please run:\n"
        "    python3 -m spacy download en_core_web_trf",
        file=sys.stderr,
    )
    sys.exit(1)

# 2. label mapping
LABEL_MAP = {
    "PERSON": "Name",
    "GPE":    "Place",
    "LOC":    "Place",
    "DATE":   "Time",
    "TIME":   "Time",
}

def extract_entities_with_context(doc, window=100):
    """
    Given a spaCy Doc, return a list of (entity_text, category, context_snippet).
    """
    results = []
    for ent in doc.ents:
        if ent.label_ not in LABEL_MAP:
            continue
        category = LABEL_MAP[ent.label_]
        start = max(ent.start - window, 0)
        end   = min(ent.end + window, len(doc))
        context = doc[start:end].text.replace("\n", " ").strip()
        results.append((ent.text, category, context))
    return results

def main():
    # 3a. Prompt for corpus path
    corpus_input = input("Enter full path to your .txt corpus file: ").strip()
    corpus_path = Path(corpus_input)
    if not corpus_path.is_file():
        print(f"Error: file not found: {corpus_path}", file=sys.stderr)
        sys.exit(1)

    # 3b. Prompt for output path
    output_input = input("Enter path for results output file (will overwrite): ").strip()
    output_path = Path(output_input)

    # Read and split into “documents” on blank lines
    text = corpus_path.read_text(encoding="utf-8")
    raw_docs = [d.strip() for d in text.split("\n\n") if d.strip()]
    if not raw_docs:
        print("No documents found in the file.", file=sys.stderr)
        sys.exit(1)

    # Open output file
    with output_path.open("w", encoding="utf-8") as out_f:
        for idx, doc_text in enumerate(raw_docs, 1):
            out_f.write(f"=== Document #{idx} ===\n")
            doc = nlp(doc_text)
            ents = extract_entities_with_context(doc, window=100)
            if not ents:
                out_f.write("No Name/Place/Time entities found.\n\n")
                continue
            for ent_text, category, snippet in ents:
                out_f.write(f"\nEntity: {ent_text}\n")
                out_f.write(f"Category: {category}\n")
                out_f.write(f"Context (±100 tokens): …{snippet}…\n")
            out_f.write("\n")

    print(f"Done! Results written to {output_path}")

if __name__ == "__main__":
    main()
