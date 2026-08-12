from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BASE_DIR / "corpus"
OUTPUT_DIR = BASE_DIR / "Mine" / "outputs"
DEFAULT_EDGES = OUTPUT_DIR / "cleaned_aggregated_edges.csv"
DEFAULT_OUTPUT = OUTPUT_DIR / "edge_validation.csv"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "her",
    "his",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "our",
    "than",
    "that",
    "the",
    "their",
    "these",
    "this",
    "those",
    "to",
    "was",
    "were",
    "with",
}


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def word_norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (text or "").lower())).strip()


def terms(text: str) -> list[str]:
    return [word for word in word_norm(text).split() if len(word) > 2 and word not in STOPWORDS]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def corpus_windows(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 30]
    windows = sentences + [" ".join(sentences[i : i + 2]) for i in range(max(0, len(sentences) - 1))]
    return [norm(window) for window in windows if len(window) <= 900]


def load_corpus() -> dict[str, dict[str, object]]:
    corpus = {}
    for path in CORPUS_DIR.glob("*.txt"):
        raw = path.read_text(encoding="utf-8", errors="ignore")
        corpus[path.stem] = {"text": norm(raw), "windows": corpus_windows(raw)}
    return corpus


def evidence_found(row: dict[str, str], corpus: dict[str, dict[str, object]]) -> bool:
    evidence = row.get("Evidence", "")
    snippets = [snippet.strip() for snippet in evidence.split("|") if snippet.strip()]
    if not snippets:
        return False
    cleaned_snippets = [norm(snippet) for snippet in snippets]
    for book in row.get("Books", "").split("|"):
        text = corpus.get(book.strip(), {}).get("text", "")
        if text and any(snippet and snippet in text for snippet in cleaned_snippets):
            return True
    shortened = [
        norm(part)
        for snippet in snippets
        for part in re.split(r"\.\.\.+|…", snippet)
        if len(norm(part)) >= 35
    ]
    for book in row.get("Books", "").split("|"):
        text = corpus.get(book.strip(), {}).get("text", "")
        if text and any(part in text for part in shortened):
            return True
    return False


def phrase_pair_found(row: dict[str, str], corpus: dict[str, dict[str, object]]) -> bool:
    source, target = norm(row.get("Source", "")), norm(row.get("Target", ""))
    if not source or not target:
        return False
    for book in row.get("Books", "").split("|"):
        for window in corpus.get(book.strip(), {}).get("windows", []):
            if source in window and target in window:
                return True
    return False


def term_pair_found(row: dict[str, str], corpus: dict[str, dict[str, object]]) -> bool:
    source_terms, target_terms = terms(row.get("Source", "")), terms(row.get("Target", ""))
    if not source_terms or not target_terms:
        return False
    for book in row.get("Books", "").split("|"):
        for window in corpus.get(book.strip(), {}).get("windows", []):
            source_hits = sum(term in window for term in source_terms) / len(source_terms)
            target_hits = sum(term in window for term in target_terms) / len(target_terms)
            if source_hits >= 0.6 and target_hits >= 0.6:
                return True
    return False


def validation_category(row: dict[str, str], corpus: dict[str, dict[str, object]]) -> str:
    if evidence_found(row, corpus) or phrase_pair_found(row, corpus):
        return "Validated"
    if term_pair_found(row, corpus):
        return "Probable"
    return "Missing"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [*rows[0].keys(), "ValidationCategory"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def self_check() -> None:
    text = "Rupshu produces salt from the lake. Ladakh wool trade grows across the mountain market."
    corpus = {"Book": {"text": norm(text), "windows": corpus_windows(text)}}
    assert validation_category({"Source": "Rupshu", "Target": "salt", "Evidence": "Rupshu produces salt.", "Books": "Book"}, corpus) == "Validated"
    assert validation_category({"Source": "Ladakh wool", "Target": "trade", "Evidence": "", "Books": "Book"}, corpus) == "Validated"
    assert validation_category({"Source": "Ladakh wool cloth", "Target": "trade market goods", "Evidence": "", "Books": "Book"}, corpus) == "Probable"
    assert validation_category({"Source": "tea", "Target": "tax", "Evidence": "", "Books": "Book"}, corpus) == "Missing"


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify graph edges as Validated, Probable, or Missing.")
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_check()
        print("self-test passed")
        return

    rows = read_csv(args.edges)
    corpus = load_corpus()
    for row in rows:
        row["ValidationCategory"] = validation_category(row, corpus)
    write_csv(args.output, rows)

    counts = Counter(row["ValidationCategory"] for row in rows)
    print(f"Wrote {args.output}")
    print(f"Validated: {counts['Validated']}")
    print(f"Probable: {counts['Probable']}")
    print(f"Missing: {counts['Missing']}")


if __name__ == "__main__":
    main()
