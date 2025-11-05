import os
import nltk
import torch
from transformers import BartForConditionalGeneration, BartTokenizer

nltk.download('punkt')
from nltk.tokenize import word_tokenize

# Load BART model and tokenizer
model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

def load_text(file_path):
    """Load text from a given file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def find_context(text, keyword, window_size=100):
    """Extracts 100 words before and after the keyword for context."""
    words = word_tokenize(text)
    keyword_indices = [i for i, word in enumerate(words) if word.lower() == keyword.lower()]
    
    if not keyword_indices:
        print(f"Keyword '{keyword}' not found in the text.")
        return None
    
    # Taking the first occurrence
    idx = keyword_indices[0]
    start = max(0, idx - window_size)
    end = min(len(words), idx + window_size)
    return ' '.join(words[start:end])

def summarize_text(text):
    """Generates a summary using BART."""
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    
    with torch.no_grad():
        summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def process_file(file_path, keyword):
    """Processes a single text file for summarization."""
    text = load_text(file_path)
    context = find_context(text, keyword)

    if context:
        summary = summarize_text(context)
        print(f"\nSummary of {file_path}:\n", summary)

def main():
    path = input("Enter the folder or file path: ").strip()
    keyword = input("Enter the keyword to search for: ").strip()

    if os.path.isdir(path):  # If it's a directory, process all text files
        for filename in os.listdir(path):
            if filename.endswith(".txt"):
                process_file(os.path.join(path, filename), keyword)
    elif os.path.isfile(path):  # If it's a single file, process just that one
        process_file(path, keyword)
    else:
        print("Invalid path. Please enter a valid file or directory.")

if __name__ == "__main__":
    main()
