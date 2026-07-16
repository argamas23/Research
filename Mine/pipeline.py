import os
import subprocess
import glob
import datetime
import shutil
import sys
import argparse
import json
import re

def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def load_state(path):
    if not os.path.exists(path):
        return {"steps": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(path, state):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)

def output_ready(path):
    return os.path.exists(path) and os.path.getsize(path) > 0

def step_done(state, step_key, outputs):
    saved = state.get("steps", {}).get(step_key) == "completed"
    return saved and all(output_ready(path) for path in outputs)

def run_step(step_key, title, command, state_path, state, outputs=()):
    print(f"\n--- {title} ---")
    if step_done(state, step_key, outputs):
        print(f"Skipping {step_key}; completed output already exists.")
        return

    run_command(command)
    missing = [path for path in outputs if not output_ready(path)]
    if missing:
        print(f"Error: {step_key} finished but did not create usable output: {', '.join(missing)}")
        sys.exit(1)

    state.setdefault("steps", {})[step_key] = "completed"
    save_state(state_path, state)

def latest_results_dir(results_root, book_basename):
    candidates = []
    for path in glob.glob(os.path.join(results_root, "*")):
        name = os.path.basename(path)
        timestamped = re.fullmatch(re.escape(book_basename) + r"_\d{8}_\d{6}", name)
        if os.path.isdir(path) and (name == book_basename or timestamped):
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)

def main():
    parser = argparse.ArgumentParser(description="Run NLP pipeline on a single book.")
    parser.add_argument("--book", required=True, help="Name of the PDF file in Research/Books directory (e.g., '1910.pdf').")
    parser.add_argument("--delete", action="store_true", help="Delete this book and all generated pipeline data.")
    parser.add_argument("--dry-run", action="store_true", help="With --delete, show what would be deleted.")
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(4, (os.cpu_count() or 2))),
        help="Concurrent workers for parallel-capable stages, especially relation extraction.",
    )
    args = parser.parse_args()
    book_name = args.book

    if args.delete:
        from delete_book import delete_book

        delete_book(book_name, dry_run=args.dry_run)
        if not args.dry_run:
            print(f"Deleted '{book_name}' and rebuilt graph outputs.")
        return

    # Base directories
    base_dir = "/home/samagra-bharti/Desktop/Research"
    mine_dir = os.path.join(base_dir, "Mine")
    books_dir = os.path.join(base_dir, "Books")
    # External corpus directory as requested
    corpus_dir = os.path.join(base_dir, "corpus")
    
    # Validation
    pdf_path = os.path.join(books_dir, book_name)
    if not os.path.exists(pdf_path):
        print(f"Error: Book '{book_name}' not found in {books_dir}")
        sys.exit(1)
        
    print(f"Pipeline started for book: {book_name}")

    book_basename = os.path.splitext(book_name)[0]
    results_root = os.path.join(mine_dir, "Results")
    os.makedirs(results_root, exist_ok=True)

    results_dir = latest_results_dir(results_root, book_basename)
    if results_dir:
        print(f"Resuming existing results directory: {results_dir}")
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir_name = f"{book_basename}_{timestamp}"
        results_dir = os.path.join(results_root, results_dir_name)
        print(f"Results will be saved to: {results_dir}")
    os.makedirs(results_dir, exist_ok=True)
    state_path = os.path.join(results_dir, ".pipeline_state.json")
    state = load_state(state_path)

    # Ensure corpus directory exists
    os.makedirs(corpus_dir, exist_ok=True)

    # 1. Translate Book to TXT
    txt_filename = book_basename + ".txt"
    txt_path = os.path.join(corpus_dir, txt_filename)
    
    # script.py usage: python script.py input.pdf output.txt
    run_step(
        "step_1_txt",
        f"Step 1: Translating '{book_name}' to TXT",
        ["python3", os.path.join(mine_dir, "script.py"), pdf_path, txt_path],
        state_path,
        state,
        [txt_path],
    )

    # No merging step as per request ("Stick to the single file")

    # 3. NER (Textrazor.py)
    ner_output_path = os.path.join(results_dir, "ner_results.txt")
    # Textrazor.py usage: --input <file> --output <file>
    run_step(
        "step_3_ner",
        "Step 3: Running NER (Textrazor.py)",
        [
            "python3", os.path.join(mine_dir, "Textrazor.py"),
            "--input", txt_path,
            "--output", ner_output_path
        ],
        state_path,
        state,
        [ner_output_path],
    )

    # 4. Topics (Topics.py)
    unique_topics_path = os.path.join(mine_dir, "unique_topics.txt")
    # Usage: --ner_file <file> --output_file <file>
    run_step(
        "step_4_topics",
        "Step 4: Extracting Topics (Topics.py)",
        [
            "python3", os.path.join(mine_dir, "Topics.py"),
            "--ner_file", ner_output_path,
            "--output_file", unique_topics_path
        ],
        state_path,
        state,
        [unique_topics_path],
    )

    # 5. Co-occurrence (process2.py)
    coocc_output_path = os.path.join(results_dir, "entity_cooccurrences.txt")
    selected_topics_path = os.path.join(mine_dir, "Selected_Topics.txt")
    
    # Usage: --corpus_file --ner_file --selected_topics --all_topics --output_file
    run_step(
        "step_5_cooccurrence",
        "Step 5: Entity Co-occurrence (process2.py)",
        [
            "python3", os.path.join(mine_dir, "process2.py"),
            "--corpus_file", txt_path,  # Use the single book text file
            "--ner_file", ner_output_path,
            "--selected_topics", selected_topics_path,
            "--all_topics", unique_topics_path,
            "--output_file", coocc_output_path
        ],
        state_path,
        state,
        [coocc_output_path],
    )

    # 6. Relation Extraction (relation.py)
    relation_output_path = os.path.join(results_dir, "weighted_knowledge_graph.csv")
    
    # Usage: --corpus_file --coocc_file --topics_file --output_file
    run_step(
        "step_6_relations",
        "Step 6: Relation Extraction (relation.py)",
        [
            "python3", os.path.join(mine_dir, "relation.py"),
            "--corpus_file", txt_path, # Use the single book text file
            "--coocc_file", coocc_output_path,
            "--topics_file", selected_topics_path,
            "--output_file", relation_output_path,
            "--workers", str(max(1, args.workers)),
        ],
        state_path,
        state,
        [relation_output_path],
    )

    # 7. Update Config (update_config.py)
    run_step(
        "step_7_update_config",
        "Step 7: Updating Configuration (update_config.py)",
        ["python3", os.path.join(mine_dir, "update_config.py")],
        state_path,
        state,
    )

    # 8. Correct Entity Types using TextRazor NER (correct_entity_types.py)
    run_step(
        "step_8_correct_entity_types",
        "Step 8: Correcting Entity Types via NER (correct_entity_types.py)",
        ["python3", os.path.join(mine_dir, "correct_entity_types.py")],
        state_path,
        state,
    )

    # 9. Rebuild HTML Visualization from all Mine/Results graph CSVs
    run_step(
        "step_9_rebuild_graph",
        "Step 9: Rebuilding HTML Visualization (rebuild_graph.py)",
        ["python3", os.path.join(mine_dir, "rebuild_graph.py")],
        state_path,
        state,
    )

    print(f"\nPipeline completed successfully! Results are in: {results_dir}")

if __name__ == "__main__":
    main()
