import os
import subprocess
import glob
import datetime
import shutil
import sys
import argparse

def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run NLP pipeline on a single book.")
    parser.add_argument("--book", required=True, help="Name of the PDF file in Research/Books directory (e.g., '1910.pdf').")
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(4, (os.cpu_count() or 2))),
        help="Concurrent workers for parallel-capable stages, especially relation extraction.",
    )
    args = parser.parse_args()
    book_name = args.book

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

    # Create results directory with book name and timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    book_basename = os.path.splitext(book_name)[0]
    results_dir_name = f"{book_basename}_{timestamp}"
    results_dir = os.path.join(mine_dir, "Results", results_dir_name)
    os.makedirs(results_dir, exist_ok=True)
    print(f"Results will be saved to: {results_dir}")

    # Ensure corpus directory exists
    os.makedirs(corpus_dir, exist_ok=True)

    # 1. Translate Book to TXT
    print(f"\n--- Step 1: Translating '{book_name}' to TXT ---")
    txt_filename = book_basename + ".txt"
    txt_path = os.path.join(corpus_dir, txt_filename)
    
    # script.py usage: python script.py input.pdf output.txt
    run_command(["python3", os.path.join(mine_dir, "script.py"), pdf_path, txt_path])

    # No merging step as per request ("Stick to the single file")

    # 3. NER (Textrazor.py)
    print("\n--- Step 3: Running NER (Textrazor.py) ---")
    ner_output_path = os.path.join(results_dir, "ner_results.txt")
    # Textrazor.py usage: --input <file> --output <file>
    run_command([
        "python3", os.path.join(mine_dir, "Textrazor.py"),
        "--input", txt_path,
        "--output", ner_output_path
    ])

    # 4. Topics (Topics.py)
    print("\n--- Step 4: Extracting Topics (Topics.py) ---")
    unique_topics_path = os.path.join(mine_dir, "unique_topics.txt")
    # Usage: --ner_file <file> --output_file <file>
    run_command([
        "python3", os.path.join(mine_dir, "Topics.py"),
        "--ner_file", ner_output_path,
        "--output_file", unique_topics_path
    ])

    # 5. Co-occurrence (process2.py)
    print("\n--- Step 5: Entity Co-occurrence (process2.py) ---")
    coocc_output_path = os.path.join(results_dir, "entity_cooccurrences.txt")
    selected_topics_path = os.path.join(mine_dir, "Selected_Topics.txt")
    
    # Usage: --corpus_file --ner_file --selected_topics --all_topics --output_file
    run_command([
        "python3", os.path.join(mine_dir, "process2.py"),
        "--corpus_file", txt_path,  # Use the single book text file
        "--ner_file", ner_output_path,
        "--selected_topics", selected_topics_path,
        "--all_topics", unique_topics_path,
        "--output_file", coocc_output_path
    ])

    # 6. Relation Extraction (relation.py)
    print("\n--- Step 6: Relation Extraction (relation.py) ---")
    relation_output_path = os.path.join(results_dir, "weighted_knowledge_graph.csv")
    
    # Usage: --corpus_file --coocc_file --topics_file --output_file
    run_command([
        "python3", os.path.join(mine_dir, "relation.py"),
        "--corpus_file", txt_path, # Use the single book text file
        "--coocc_file", coocc_output_path,
        "--topics_file", selected_topics_path,
        "--output_file", relation_output_path,
        "--workers", str(max(1, args.workers)),
    ])

    # 7. Aggregate Graph (aggregate_graph.py)
    print("\n--- Step 7: Generating Aggregate Graph (aggregate_graph.py) ---")
    run_command(["python3", os.path.join(mine_dir, "aggregate_graph.py")])

    # 8. Update Config (update_config.py)
    print("\n--- Step 8: Updating Configuration (update_config.py) ---")
    run_command(["python3", os.path.join(mine_dir, "update_config.py")])

    print(f"\nPipeline completed successfully! Results are in: {results_dir}")

if __name__ == "__main__":
    main()
