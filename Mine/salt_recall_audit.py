from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from graph_rules import (
    COMMODITY_KEYWORDS,
    OUTPUT_DIR,
    POLITICAL_ECONOMY_TERMS,
    RESULTS_ROOT,
    ROUTE_PLACE_TERMS,
    SALT_TERMS,
    SOCIAL_ACTOR_TERMS,
)

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DIR = BASE_DIR / "corpus"
EDGES_PATH = Path(OUTPUT_DIR) / "cleaned_aggregated_edges.csv"
AUDIT_PATH = Path(OUTPUT_DIR) / "salt_recall_audit.csv"
SUMMARY_PATH = Path(OUTPUT_DIR) / "salt_recall_summary.csv"

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
CIRCUIT_TERMS = {
    "Salt anchor": SALT_TERMS,
    "Commodity circuits": COMMODITY_KEYWORDS,
    "Political economy": POLITICAL_ECONOMY_TERMS,
    "Route/place circuits": ROUTE_PLACE_TERMS,
    "Social actors": SOCIAL_ACTOR_TERMS,
}
CIRCUIT_RES = {
    circuit: re.compile(
        r"\b(" + "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True)) + r")\b",
        re.IGNORECASE,
    )
    for circuit, terms in CIRCUIT_TERMS.items()
}
TRADE_RE = re.compile(
    r"\b(trade|trades|trader|traders|barter|exchange|market|caravan|transport|tax|taxes|revenue|license|permit|monopoly|commodity|commodities)\b",
    re.IGNORECASE,
)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def book_key(path: Path) -> str:
    return re.sub(r"_\d{8}_\d{6}$", "", path.stem)


def sentence_circuits(sentence: str) -> list[str]:
    return [circuit for circuit, pattern in CIRCUIT_RES.items() if pattern.search(sentence)]


def is_research_circuit_sentence(sentence: str, circuits: list[str]) -> bool:
    if "Salt anchor" in circuits or "Commodity circuits" in circuits:
        return True
    if TRADE_RE.search(sentence):
        return True
    return "Political economy" in circuits and (
        "Route/place circuits" in circuits or "Social actors" in circuits
    )


def research_sentences(text: str) -> list[tuple[int, str, list[str]]]:
    return [
        (index, sentence.strip(), circuits)
        for index, sentence in enumerate(SENTENCE_RE.split(text), start=1)
        if (circuits := sentence_circuits(sentence)) and is_research_circuit_sentence(sentence, circuits)
    ]


def load_edges() -> dict[str, list[dict[str, str]]]:
    by_book = defaultdict(list)
    if not EDGES_PATH.exists():
        return by_book

    with EDGES_PATH.open(newline="", encoding="utf-8") as f:
        for edge in csv.DictReader(f):
            edge_text = " ".join(
                [
                    edge.get("Source", ""),
                    edge.get("Target", ""),
                    edge.get("Evidence", ""),
                ]
            )
            for book in (edge.get("Books") or "").split("|"):
                if book:
                    by_book[book].append(edge)
    return by_book


def onboarded_books(edges_by_book: dict[str, list[dict[str, str]]]) -> set[str]:
    books = set(edges_by_book)
    for csv_path in Path(RESULTS_ROOT).glob("**/weighted_knowledge_graph.csv"):
        books.add(re.sub(r"_\d{8}_\d{6}$", "", csv_path.parent.name))
    return books


def edge_label(edge: dict[str, str]) -> str:
    return f"{edge.get('Source', '')} -[{edge.get('MappedRelation', '')}/{edge.get('Circuit', '')}]-> {edge.get('Target', '')}"


def sentence_matches(sentence: str, edge: dict[str, str]) -> tuple[bool, bool]:
    text = clean(sentence)
    evidence = clean(edge.get("Evidence", ""))
    evidence_match = bool(evidence and (evidence in text or text in evidence))

    node_match = False
    for key in ("Source", "Target"):
        node = clean(edge.get(key, ""))
        if len(node) > 4 and node in text:
            node_match = True

    return evidence_match, node_match


def main() -> None:
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    edges_by_book = load_edges()
    allowed_books = onboarded_books(edges_by_book)
    summary_rows = []

    with AUDIT_PATH.open("w", newline="", encoding="utf-8") as audit_file:
        writer = csv.writer(audit_file)
        writer.writerow(
            [
                "Book",
                "SentenceIndex",
                "CircuitTags",
                "InFinalEvidence",
                "MentionsFinalGraphNode",
                "MatchedEdges",
                "Sentence",
            ]
        )

        for corpus_path in sorted(CORPUS_DIR.glob("*.txt")):
            book = book_key(corpus_path)
            if allowed_books and book not in allowed_books:
                continue
            sentences = research_sentences(corpus_path.read_text(encoding="utf-8", errors="ignore"))
            edges = edges_by_book.get(book, [])
            evidence_hits = 0
            node_hits = 0
            salt_edges = 0
            sentence_counts = defaultdict(int)
            edge_counts = defaultdict(int)
            for edge in edges:
                edge_counts[edge.get("Circuit") or "Unclassified"] += 1
                edge_text = " ".join([edge.get("Source", ""), edge.get("Target", ""), edge.get("Evidence", "")])
                salt_edges += int(bool(CIRCUIT_RES["Salt anchor"].search(edge_text)))

            for index, sentence, circuits in sentences:
                for circuit in circuits:
                    sentence_counts[circuit] += 1
                matched = []
                evidence_match = False
                node_match = False
                for edge in edges:
                    edge_evidence_match, edge_node_match = sentence_matches(sentence, edge)
                    if edge_evidence_match or edge_node_match:
                        matched.append(edge_label(edge))
                    evidence_match = evidence_match or edge_evidence_match
                    node_match = node_match or edge_node_match

                evidence_hits += int(evidence_match)
                node_hits += int(node_match)
                writer.writerow(
                    [
                        book,
                        index,
                        "|".join(circuits),
                        "yes" if evidence_match else "no",
                        "yes" if node_match else "no",
                        " | ".join(sorted(set(matched))[:5]),
                        sentence,
                    ]
                )

            summary_rows.append(
                {
                    "Book": book,
                    "ResearchCircuitSentences": len(sentences),
                    "SaltSentences": sentence_counts["Salt anchor"],
                    "CommodityCircuitSentences": sentence_counts["Commodity circuits"],
                    "PoliticalEconomySentences": sentence_counts["Political economy"],
                    "RoutePlaceSentences": sentence_counts["Route/place circuits"],
                    "SocialActorSentences": sentence_counts["Social actors"],
                    "FinalCircuitEdges": len(edges),
                    "FinalSaltEdges": salt_edges,
                    "FinalCommodityCircuitEdges": edge_counts["Commodity circuits"],
                    "FinalPoliticalEconomyEdges": edge_counts["Political economy"],
                    "FinalRoutePlaceEdges": edge_counts["Route/place circuits"],
                    "FinalSocialActorEdges": edge_counts["Social actors"],
                    "EvidenceCoveredSentences": evidence_hits,
                    "NodeCoveredSentences": node_hits,
                }
            )

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as summary_file:
        writer = csv.DictWriter(
            summary_file,
            fieldnames=[
                "Book",
                "ResearchCircuitSentences",
                "SaltSentences",
                "CommodityCircuitSentences",
                "PoliticalEconomySentences",
                "RoutePlaceSentences",
                "SocialActorSentences",
                "FinalCircuitEdges",
                "FinalSaltEdges",
                "FinalCommodityCircuitEdges",
                "FinalPoliticalEconomyEdges",
                "FinalRoutePlaceEdges",
                "FinalSocialActorEdges",
                "EvidenceCoveredSentences",
                "NodeCoveredSentences",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Wrote {AUDIT_PATH}")
    print(f"Wrote {SUMMARY_PATH}")
    for row in summary_rows:
        if row["ResearchCircuitSentences"] or row["FinalCircuitEdges"]:
            print(
                f"{row['Book']}: {row['ResearchCircuitSentences']} research-circuit sentences, "
                f"{row['FinalCircuitEdges']} final circuit edges, "
                f"{row['EvidenceCoveredSentences']} evidence-covered, "
                f"{row['NodeCoveredSentences']} node-covered"
            )


if __name__ == "__main__":
    main()
