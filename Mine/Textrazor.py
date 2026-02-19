# import textrazor
# import os
# from collections import defaultdict

# # === CONFIGURATION ===
# textrazor.api_key = "864276b8fd6c183c43d0244bf5926cb31275c7d30097228a089a0e25"
# input_file = "/home/samagra/Desktop/Research/corpus/1897.txt"
# output_file = "textrazor_results.txt"
# chunk_size_bytes = 190 * 1024  # 190 KB

# # === Initialize TextRazor client ===
# client = textrazor.TextRazor(extractors=["entities", "topics"])

# # === Helper to safely write unique lines ===
# def safe_write(out_file, line, last_written_line):
#     line = line.strip()
#     if line != last_written_line[0]:
#         out_file.write(line + "\n")
#         last_written_line[0] = line

# # === Helper to process a single chunk ===
# def process_chunk(chunk_text, chunk_num, chunk_size_kb):
#     print(f"Processing chunk {chunk_num} ({chunk_size_kb:.2f} KB)...")
#     try:
#         response = client.analyze(chunk_text)
#         if not response.ok:
#             print(f"Chunk {chunk_num}: Response not OK!")
#             return

#         with open(output_file, "a", encoding="utf-8") as out:
#             last_written_line = [""]
#             safe_write(out, f"\n=== CHUNK {chunk_num} ({chunk_size_kb:.2f} KB) ===", last_written_line)

#             # --- Group entities by Freebase type ---
#             type_to_entities = defaultdict(set)
#             for entity in response.entities():
#                 for t in entity.freebase_types:
#                     type_to_entities[t].add(entity.id)

#             # --- Write each type group ---
#             for ftype, values in sorted(type_to_entities.items()):
#                 safe_write(out, f"\n{ftype}", last_written_line)
#                 for val in sorted(values):
#                     safe_write(out, val, last_written_line)

#             # --- Write topics as well ---
#             safe_write(out, "\nTopics", last_written_line)
#             seen_topics = set()
#             for topic in response.topics():
#                 if topic.label not in seen_topics:
#                     safe_write(out, topic.label, last_written_line)
#                     seen_topics.add(topic.label)

#             out.write("\n")

#     except textrazor.TextRazorAnalysisException as ex:
#         print(f"Chunk {chunk_num}: Failed with error: {ex}")

# # === Main loop: paragraph-based chunking ===
# with open(input_file, "r", encoding="utf-8") as f:
#     paragraphs = f.read().split("\n\n")

# chunk_num = 1
# current_chunk = ""
# current_chunk_size = 0

# # Remove old output
# if os.path.exists(output_file):
#     os.remove(output_file)

# for para in paragraphs:
#     para = para.strip()
#     if not para:
#         continue

#     para_size = len(para.encode("utf-8"))
#     if current_chunk_size + para_size <= chunk_size_bytes:
#         current_chunk += para + "\n\n"
#         current_chunk_size += para_size
#     else:
#         process_chunk(current_chunk, chunk_num, current_chunk_size / 1024.0)
#         chunk_num += 1
#         current_chunk = para + "\n\n"
#         current_chunk_size = para_size

# # Process final chunk
# if current_chunk.strip():
#     process_chunk(current_chunk, chunk_num, current_chunk_size / 1024.0)

# print("=== All chunks processed. Output saved to:", output_file)

import textrazor
import os
import argparse
import sys
from collections import defaultdict

# === CONFIGURATION ===
textrazor.api_key = "864276b8fd6c183c43d0244bf5926cb31275c7d30097228a089a0e25"
chunk_size_bytes = 190 * 1024                      # ≈ 190 KB

def parse_args():
    parser = argparse.ArgumentParser(description="Run TextRazor NER on a text file.")
    parser.add_argument("--input", required=True, help="Path to input text file.")
    parser.add_argument("--output", required=True, help="Path to output results file.")
    return parser.parse_args()

# === Initialise client ===
client = textrazor.TextRazor(extractors=["entities", "topics"])

# === Utility: write line only if last line differs ===
def safe_write(out_fh, text, last_line_holder):
    text = text.rstrip()
    if text != last_line_holder[0]:
        out_fh.write(text + "\n")
        last_line_holder[0] = text

# === Process one chunk ===
def process_chunk(text, num, size_kb):
    print(f"Processing chunk {num} ({size_kb:.2f} KB)…")
    try:
        resp = client.analyze(text)
        if not resp.ok:
            print(f"Chunk {num}: response not OK!")
            return
    except textrazor.TextRazorAnalysisException as exc:
        print(f"Chunk {num}: failed – {exc}")
        return

    # ——— gather entities by Freebase type ———
    type_to_entities: dict[str, dict[str, tuple[float, float]]] = defaultdict(dict)
    for ent in resp.entities():
        for fb_type in ent.freebase_types:
            # Keep the best (highest relevance) score if a duplicate entity re-appears
            current = type_to_entities[fb_type].get(ent.id)
            if current is None or ent.relevance_score > current[0]:
                type_to_entities[fb_type][ent.id] = (
                    ent.relevance_score,
                    ent.confidence_score,
                )

    with open(output_file, "a", encoding="utf-8") as out:
        last = [""]
        safe_write(out, f"\n=== CHUNK {num} ({size_kb:.2f} KB) ===", last)

        # ——— Emit entities, grouped & demarcated ———
        for fb_type in sorted(type_to_entities):
            safe_write(out, "", last)                       # blank line before each group
            safe_write(out, fb_type, last)
            safe_write(out, "──────────", last)
            for eid, (rel, conf) in sorted(type_to_entities[fb_type].items()):
                safe_write(
                    out,
                    f"{eid}  (Relevance {rel:.3f} | Confidence {conf:.3f})",
                    last,
                )

        # ——— Emit topics ———
        safe_write(out, "\nTopics", last)
        safe_write(out, "──────", last)
        for topic in resp.topics():
            safe_write(out, f"{topic.label}  (Score {topic.score:.3f})", last)

# === Main execution ===
if __name__ == "__main__":
    args = parse_args()
    input_file = args.input
    output_file = args.output

    if os.path.exists(output_file):
        os.remove(output_file)
    
    # Ensure output file exists even if no text is processed
    open(output_file, 'a').close()

    # === Paragraph-safe chunking loop ===
    with open(input_file, encoding="utf-8") as fh:
        paragraphs = fh.read().split("\n\n")

    chunk_text, chunk_size, chunk_num = "", 0, 1
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        p_bytes = len(p.encode("utf-8"))
        if chunk_size + p_bytes <= chunk_size_bytes:
            chunk_text += p + "\n\n"
            chunk_size += p_bytes
        else:
            process_chunk(chunk_text, chunk_num, chunk_size / 1024)
            chunk_num += 1
            chunk_text, chunk_size = p + "\n\n", p_bytes

    # final leftover
    if chunk_text.strip():
        process_chunk(chunk_text, chunk_num, chunk_size / 1024)

    print("=== All chunks processed – results saved to", output_file)
