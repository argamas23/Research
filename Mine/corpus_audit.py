from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import fitz


BASE_DIR = Path(__file__).resolve().parent.parent
BOOKS_DIR = BASE_DIR / "Books"
CORPUS_DIR = BASE_DIR / "corpus"
RESULTS_DIR = BASE_DIR / "Mine" / "Results"
VALIDATION_CSV = BASE_DIR / "Mine" / "outputs" / "edge_validation.csv"
OUT_DIR = BASE_DIR / "Mine" / "outputs" / "corpus"
WRITEUP_DIR = BASE_DIR / "Mine" / "outputs" / "research_writeup"


def words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", text)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def pdf_pages(pdf: Path | None) -> int:
    if not pdf or not pdf.exists():
        return 0
    with fitz.open(pdf) as doc:
        return doc.page_count


def result_dirs(stem: str) -> list[Path]:
    return sorted(path for path in RESULTS_DIR.glob(f"{stem}*") if path.is_dir())


def graph_source_ids(validation: list[dict[str, str]]) -> list[str]:
    return sorted({book.strip() for row in validation for book in row.get("Books", "").split("|") if book.strip()})


def corpus_rows() -> list[dict[str, object]]:
    validation = read_csv(VALIDATION_CSV)
    by_book = Counter(book.strip() for row in validation for book in row.get("Books", "").split("|") if book.strip())
    validated_by_book = Counter(
        book.strip()
        for row in validation
        if row.get("ValidationCategory") == "Validated"
        for book in row.get("Books", "").split("|")
        if book.strip()
    )
    rows = []
    for stem in graph_source_ids(validation):
        txt = CORPUS_DIR / f"{stem}.txt"
        if not txt.exists():
            continue
        text = txt.read_text(encoding="utf-8", errors="ignore")
        pdf = BOOKS_DIR / f"{stem}.pdf"
        dirs = result_dirs(stem)
        rows.append(
            {
                "source_id": stem,
                "text_file": txt.as_posix(),
                "pdf_file": pdf.as_posix() if pdf.exists() else "",
                "pdf_pages": pdf_pages(pdf if pdf.exists() else None),
                "characters": len(text),
                "words": len(words(text)),
                "paragraphs": sum(1 for part in re.split(r"\n\s*\n", text) if part.strip()),
                "result_dirs": "|".join(path.name for path in dirs),
                "source_linked_relation_rows": by_book[stem],
                "source_linked_validated_rows": validated_by_book[stem],
            }
        )
    return rows


def markdown_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict[str, object]]) -> None:
    totals = {
        "sources": len(rows),
        "pdf_pages": sum(int(row["pdf_pages"]) for row in rows),
        "words": sum(int(row["words"]) for row in rows),
        "characters": sum(int(row["characters"]) for row in rows),
        "edge_rows": len(read_csv(VALIDATION_CSV)),
        "validated_edge_rows": sum(1 for row in read_csv(VALIDATION_CSV) if row.get("ValidationCategory") == "Validated"),
        "source_linked_relation_rows": sum(int(row["source_linked_relation_rows"]) for row in rows),
        "source_linked_validated_rows": sum(int(row["source_linked_validated_rows"]) for row in rows),
    }
    write_csv(OUT_DIR / "corpus_statistics.csv", [totals], list(totals))
    write_csv(OUT_DIR / "corpus_table.csv", rows, list(rows[0]) if rows else [])

    top_sources = sorted(rows, key=lambda row: int(row["words"]), reverse=True)[:10]
    text = [
        "# Corpus Statistics",
        "",
        "## Final Totals",
        "",
        markdown_table([totals], list(totals)),
        "",
        "## Corpus Table",
        "",
        markdown_table(
            rows,
            ["source_id", "pdf_pages", "words", "paragraphs", "source_linked_relation_rows", "source_linked_validated_rows"],
        ),
        "",
        "## Largest Sources By Word Count",
        "",
        markdown_table(top_sources, ["source_id", "words", "pdf_pages", "source_linked_validated_rows"]),
    ]
    (OUT_DIR / "CORPUS_STATISTICS.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def write_dh_related_work() -> None:
    WRITEUP_DIR.mkdir(parents=True, exist_ok=True)
    text = """# Computational History And Digital Humanities Related Work

This project sits in the digital-history tradition that treats digitized historical sources as evidence to be structured, queried, and returned to close reading, rather than as a replacement for interpretation. Its method follows a common DH movement from text to data: printed books and reports are first converted into machine-readable text, then entities, relations, and network structures are extracted from that text. The important methodological point is that the graph is not the past itself. It is a reproducible model of relations that survived OCR, named-entity recognition, relation extraction, cleaning, and validation.

Historical network research provides the closest methodological frame. Work in this area stresses that network analysis becomes historically meaningful only when nodes, edges, and weights are explicitly defined and when quantitative metrics are interpreted against the source-making process. This project therefore treats edges as evidence-backed claims, separates validated from probable relations, reports graph sparsity and connected components, and avoids claiming total coverage of Himalayan political economy.

The project also draws on knowledge-graph and information-extraction work in cultural heritage. Knowledge graphs are useful here because they preserve typed entities, typed relations, evidence snippets, confidence scores, and source documents in the same table. That structure makes it possible to move between macro-level network metrics and individual source passages. The workflow uses automated extraction for scale, but keeps a validation layer because historical language, OCR noise, colonial terminology, and transliterated place names all create predictable extraction errors.

For the salt-backbone hypothesis, the relevant DH contribution is not simply visualization. The graph is used as a testable representation: salt's degree, weighted strength, betweenness, PageRank, community membership, removal effect, and commodity-label permutation results are compared against other commodities and against stricter graph views. This makes the argument falsifiable within the extracted corpus while preserving a historian's caveat: the result demonstrates structure in the constructed corpus graph, not the complete structure of the historical economy.

## Works To Cite

- Shawn Graham, Ian Milligan, and Scott Weingart, *Exploring Big Historical Data: The Historian's Macroscope* (2015).
- Marten During, Florian Kerschbaumer, Linda von Keyserlingk-Rehbein, and Martin Stark, eds., *The Power of Networks: Prospects of Historical Network Research* (2016).
- Malte Rehbein, \"Historical Network Research, Digital History, Digital Humanities,\" in *The Routledge Companion to Digital Humanities and Art History*. https://www.taylorfrancis.com/chapters/edit/10.4324/9781315189062-16/historical-network-research-digital-history-digital-humanities-malte-rehbein
- Deryc T. Painter, Bryan C. Daniels, and Jurgen Jost, \"Network Analysis for the Digital Humanities: Principles, Problems, Extensions,\" *Isis* 110, no. 3 (2019): 538-554. https://www.journals.uchicago.edu/doi/full/10.1086/705532
- Lea Weiss et al., \"Past, Present, and Future of HNR,\" *Journal of Historical Network Research* 11, no. 1 (2025): 42-70. https://jhnr.net/articles/10.25517/jhnr.v11i1.103
- Patrick Jentsch and Stephan Porada, \"From Text to Data: Digitization, Text Analysis and Corpus Linguistics,\" in *Digital Methods in the Humanities* (2021), 89-128. https://www.jstor.org/stable/j.ctv2f9xskk.6
"""
    (WRITEUP_DIR / "DH_RELATED_WORK.md").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Write final corpus statistics, corpus table, and DH related-work note.")
    parser.parse_args()
    rows = corpus_rows()
    write_report(rows)
    write_dh_related_work()
    print(f"Wrote corpus outputs to {OUT_DIR}")
    print(f"Wrote DH related work to {WRITEUP_DIR / 'DH_RELATED_WORK.md'}")


if __name__ == "__main__":
    main()
