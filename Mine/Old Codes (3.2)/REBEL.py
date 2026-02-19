
import re
import csv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load REBEL model
tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

# Generator to stream a huge txt file in chunks
def stream_text_file(filepath, chunk_size=10000):
    with open(filepath, "r", encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Improved sentence splitter
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]

# Batch extractor with filtering
def batch_extract_relations(sentences, batch_size=2):
    relations = []

    # Define relations of interest
    interesting_relations = {
        "traded for", "brought from", "carried to", "crossed via", "harvested at",
        "owned by", "owner of", "controlled by", "product of", "located in", "subclass of"
    }

    # Define commodities of interest
    commodities = {
        "salt", "wool", "pashm", "barley", "rice", "tea", "apricots",
        "ghee", "pashmina", "honey", "sheep", "copper", "silk", "opium",
        "maize", "millet", "wheat", "borax", "natron", "horse", "yak",
        "indigo", "dyes", "butter", "tea", "grain", "textiles"
    }

    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model.generate(**inputs, max_length=512)
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        for d in decoded:
            rels = d.split(",")
            for r in rels:
                # Apply relation filter first
                if any(rel in r for rel in interesting_relations):
                    # Apply commodity filter second
                    if any(c in r.lower() for c in commodities):
                        # Try to parse into (subject, relation, object)
                        parts = r.strip().split(" ", 2)
                        if len(parts) == 3:
                            subj, rel, obj = parts
                            relations.append((subj.strip(), rel.strip(), obj.strip()))
    return relations

# Main processing
all_relations = []

# Path to your large text file
file_path = "/home/samagra/Desktop/Research/corpus/1897.txt"

# Process file in chunks
for chunk in stream_text_file(file_path, chunk_size=20000):
    sentences = split_sentences(chunk)
    print(f"Processing {len(sentences)} sentences...")
    rels = batch_extract_relations(sentences)
    all_relations.extend(rels)

# Final result
print(f"\nTotal filtered relations extracted: {len(all_relations)}\n")

# Save to CSV
csv_output_path = "filtered_relations.csv"
with open(csv_output_path, mode="w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Subject", "Relation", "Object"])  # Header row
    for (subj, rel, obj) in all_relations:
        writer.writerow([subj, rel, obj])

print(f"Filtered relations saved to {csv_output_path} ✅")


# import re
# import csv
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# # Load REBEL model
# tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
# model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")

# # Generator to stream a huge txt file in chunks
# def stream_text_file(filepath, chunk_size=10000):
#     with open(filepath, "r", encoding="utf-8") as f:
#         while True:
#             chunk = f.read(chunk_size)
#             if not chunk:
#                 break
#             yield chunk

# # Improved sentence splitter
# def split_sentences(text):
#     sentences = re.split(r'(?<=[.!?]) +', text)
#     return [s.strip() for s in sentences if s.strip()]

# # Batch extractor — now prints and logs full REBEL output
# def batch_extract_relations(sentences, batch_size=2):
#     relations = []

#     # Define commodities of interest
#     commodities = {
#         "salt", "wool", "pashm", "barley", "rice", "tea", "apricots",
#         "ghee", "pashmina", "honey", "sheep", "copper", "silk", "opium",
#         "maize", "millet", "wheat", "borax", "natron", "horse", "yak",
#         "indigo", "dyes", "butter", "tea", "grain", "textiles"
#     }

#     for i in range(0, len(sentences), batch_size):
#         batch = sentences[i:i+batch_size]
#         inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
#         outputs = model.generate(**inputs, max_length=512)
#         decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

#         print("\n🟡 Decoded batch output:")
#         for d in decoded:
#             print("🔹", d)  # Print full REBEL output
#             rels = d.split(",")
#             for r in rels:
#                 r = r.strip()
#                 if not r:
#                     continue
#                 # Try to parse into subject-relation-object format
#                 parts = r.strip().split(" ", 2)
#                 if len(parts) == 3:
#                     subj, rel, obj = parts
#                     triplet_text = f"{subj} → {rel} → {obj}"
#                     # Filter by commodities
#                     if any(c in r.lower() for c in commodities):
#                         relations.append((subj.strip(), rel.strip(), obj.strip()))
#                         print(f"✅ Kept: {triplet_text}")
#                     else:
#                         print(f"⚠️  Skipped (not commodity-related): {triplet_text}")
#                 else:
#                     print(f"❌ Could not parse relation: {r}")
#     return relations

# # Main processing
# all_relations = []

# # Path to your large text file
# file_path = "/home/samagra/Desktop/Research/corpus/1897.txt"

# # Process file in chunks
# for chunk in stream_text_file(file_path, chunk_size=20000):
#     sentences = split_sentences(chunk)
#     print(f"\n🔵 Processing {len(sentences)} sentences...")
#     rels = batch_extract_relations(sentences)
#     all_relations.extend(rels)

# # Final result
# print(f"\n✅ Total filtered commodity-related relations extracted: {len(all_relations)}")

# # Save to CSV
# csv_output_path = "filtered_relations.csv"
# with open(csv_output_path, mode="w", encoding="utf-8", newline="") as csv_file:
#     writer = csv.writer(csv_file)
#     writer.writerow(["Subject", "Relation", "Object"])  # Header row
#     for (subj, rel, obj) in all_relations:
#         writer.writerow([subj, rel, obj])

# print(f"\n📁 Filtered relations saved to {csv_output_path} ✅")
