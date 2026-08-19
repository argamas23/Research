from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

import fitz


BASE_DIR = Path(__file__).resolve().parent.parent
BOOKS_DIR = BASE_DIR / "Books"
DEFAULT_EDGES = BASE_DIR / "Mine" / "outputs" / "edge_validation.csv"
OUT_DIR = BASE_DIR / "Mine" / "outputs" / "citations"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def useful_parts(evidence: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"\|+|…|\.{3,}", evidence or "") if len(part.strip()) >= 35]
    return sorted(parts, key=len, reverse=True)


def pdf_for(book: str) -> Path | None:
    exact = BOOKS_DIR / f"{book}.pdf"
    if exact.exists():
        return exact
    cleaned = re.sub(r"_20\d{6}_\d{6}$", "", book)
    fallback = BOOKS_DIR / f"{cleaned}.pdf"
    return fallback if fallback.exists() else None


def page_texts(pdf: Path) -> list[str]:
    with fitz.open(pdf) as doc:
        return [norm(page.get_text("text")) for page in doc]


def find_pages(evidence: str, pages: list[str]) -> tuple[str, str]:
    parts = [norm(part) for part in useful_parts(evidence)]
    if not parts:
        return "", "no_evidence"
    hits: list[int] = []
    for page_num, text in enumerate(pages, start=1):
        if any(part in text for part in parts):
            hits.append(page_num)
    if hits:
        return "|".join(map(str, hits)), "verified"
    # ponytail: word-overlap fallback only flags candidates; use page-image review if this becomes publication-critical.
    tokens = [set(re.findall(r"[a-z0-9]{4,}", part)) for part in parts[:2]]
    candidates = []
    for page_num, text in enumerate(pages, start=1):
        page_tokens = set(re.findall(r"[a-z0-9]{4,}", text))
        if any(len(toks & page_tokens) / max(1, len(toks)) >= 0.8 for toks in tokens):
            candidates.append(page_num)
    return "|".join(map(str, candidates[:5])), "candidate" if candidates else "not_found"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def verify(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    cache: dict[Path, list[str]] = {}
    out = []
    for idx, row in enumerate(rows, start=1):
        book_pages = []
        statuses = []
        pdfs = []
        for book in [item.strip() for item in row.get("Books", "").split("|") if item.strip()]:
            pdf = pdf_for(book)
            if not pdf:
                statuses.append(f"{book}:pdf_missing")
                continue
            pdfs.append(pdf.name)
            if pdf not in cache:
                cache[pdf] = page_texts(pdf)
            pages, status = find_pages(row.get("Evidence", ""), cache[pdf])
            statuses.append(f"{book}:{status}")
            if pages:
                book_pages.append(f"{book}:{pages}")
        out.append(
            {
                "edge_id": idx,
                "Source": row.get("Source", ""),
                "MappedRelation": row.get("MappedRelation", ""),
                "Target": row.get("Target", ""),
                "Books": row.get("Books", ""),
                "PDFs": "|".join(sorted(set(pdfs))),
                "CitationPages": "|".join(book_pages),
                "CitationStatus": "|".join(statuses) if statuses else "no_book",
                "ValidationCategory": row.get("ValidationCategory", ""),
                "Evidence": row.get("Evidence", ""),
            }
        )
    return out


def markdown_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")).replace("|", "<br>") for field in fields) + " |")
    return "\n".join(lines)


def write_report(out_dir: Path, rows: list[dict[str, object]]) -> None:
    counts = Counter()
    for row in rows:
        statuses = str(row["CitationStatus"]).split("|")
        if any(status.endswith(":verified") for status in statuses):
            counts["verified"] += 1
        elif any(status.endswith(":candidate") for status in statuses):
            counts["candidate"] += 1
        elif any(status.endswith(":pdf_missing") for status in statuses):
            counts["pdf_missing"] += 1
        elif any(status.endswith(":no_evidence") for status in statuses):
            counts["no_evidence"] += 1
        else:
            counts["not_found"] += 1
    summary = [{"status": key, "edges": counts[key]} for key in ["verified", "candidate", "not_found", "pdf_missing", "no_evidence"]]
    flagged = [row for row in rows if "verified" not in str(row["CitationStatus"])][:25]
    text = [
        "# Citation Verification",
        "",
        "Page numbers are one-indexed PDF page numbers from files in `Books/`.",
        "",
        "## Summary",
        "",
        markdown_table(summary, ["status", "edges"]),
        "",
        "## First Rows Needing Review",
        "",
        markdown_table(flagged, ["edge_id", "Source", "MappedRelation", "Target", "Books", "CitationStatus", "CitationPages"]),
    ]
    (out_dir / "CITATION_VERIFICATION.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def self_check() -> None:
    assert useful_parts("abc. " * 20)
    assert pdf_for("Definitely_Not_A_Book") is None


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify relation evidence against PDFs and add page-number candidates.")
    parser.add_argument("--edges", type=Path, default=DEFAULT_EDGES)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_check()
        print("self-test passed")
        return
    rows = verify(read_csv(args.edges))
    write_csv(args.output_dir / "citation_verification.csv", rows, list(rows[0]) if rows else [])
    write_report(args.output_dir, rows)
    print(f"Wrote citation verification to {args.output_dir}")


if __name__ == "__main__":
    main()
