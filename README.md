# Historical NLP Knowledge Graphs for Himalayan Trade Networks

This repository is an active research pipeline for turning historical PDFs into evidence-backed knowledge graphs about Himalayan salt routes, commodity circulation, and frontier governance.

The core question is whether salt functioned as a structural backbone for multi-commodity trade and political economy in the Western Himalayas. The pipeline extracts text, entities, co-occurrences, relation triples, cleaned graph outputs, validation tables, interactive visualizations, and salt-specific network metrics.

## Repository Layout

```text
.
├── Books/                         # Input PDFs for pipeline runs
├── corpus/                        # Extracted text files, one per PDF
├── pipeline/
│   ├── pipeline.py                # Orchestrates one PDF through the main pipeline
│   ├── extract_text.py            # PDF text extraction with PyMuPDF
│   ├── extract_entities.py        # TextRazor entity/topic extraction
│   ├── deduplicate_topics.py      # Deduplicates extracted topics
│   ├── extract_cooccurrences.py   # Topic-anchored entity co-occurrence mining
│   ├── extract_relations.py       # Ollama/Llama relation extraction
│   ├── classify_entities.py       # Rebuilds entity type review/corrections
│   ├── rebuild_graph.py           # Rebuilds cleaned graph and HTML visualizations
│   ├── validate_evidence.py       # Checks extracted edges against corpus text
│   ├── analyze_network.py         # General graph diagnostics/community analysis
│   ├── analyze_salt.py            # Salt centrality, robustness, and brokerage metrics
│   ├── audit_salt_recall.py       # Audits research-circuit sentence coverage
│   ├── audit_corpus.py            # Corpus statistics and related-work writeup
│   ├── verify_citations.py        # Finds PDF page candidates for edge evidence
│   ├── graph_rules.py             # Entity aliases, relation rules, visual styling
│   ├── selected_topics.txt        # Manually curated topic anchors
│   ├── results/                   # Per-source extraction outputs
│   └── outputs/                   # Aggregated graph, validation, and analysis outputs
├── bibliography/                  # Bibliographic PDFs
└── figures/                       # Diagrams, maps, and paper figures
```

Main data flow:

```text
Books/*.pdf
  -> corpus/*.txt
  -> pipeline/results/<book>[_timestamp]/
  -> pipeline/outputs/
```

## Prerequisites

Use Python 3.10+.

```bash
pip install pymupdf textrazor ollama spacy networkx pandas numpy tqdm
python3 -m spacy download en_core_web_sm
```

Ollama must be installed separately:

```bash
ollama pull llama3
ollama serve
```

TextRazor requires an API key. Keep credentials out of committed files before publishing or sharing this repository.

## Quick Start

Put a PDF in `Books/`, then run:

```bash
make run BOOK=book.pdf
```

Use fewer Ollama workers on a smaller machine:

```bash
make run BOOK=book.pdf WORKERS=1
```

Open the graph:

```bash
xdg-open pipeline/outputs/network_visualization.html
```

The visualization is also copied to `pipeline/network_visualization.html`.

## Pipeline Stages

| Step | Script | Output |
| --- | --- | --- |
| 1 | `pipeline/extract_text.py` | `corpus/<book>.txt` |
| 2 | `pipeline/extract_entities.py` | `pipeline/results/<book>/ner_results.txt` |
| 3 | `pipeline/deduplicate_topics.py` | `pipeline/unique_topics.txt` |
| 4 | `pipeline/extract_cooccurrences.py` | `pipeline/results/<book>/entity_cooccurrences.txt` |
| 5 | `pipeline/extract_relations.py` | `pipeline/results/<book>/weighted_knowledge_graph.csv` |
| 6 | `pipeline/classify_entities.py` | `pipeline/outputs/cleaned_entities.json`, `entity_type_review.csv` |
| 7 | `pipeline/rebuild_graph.py` | cleaned edge tables and HTML graphs |
| 8 | `pipeline/audit_salt_recall.py` | `salt_recall_audit.csv`, `salt_recall_summary.csv` |

`pipeline/pipeline.py` resumes completed steps when its `.pipeline_state.json` and expected outputs are present.

## Common Commands

```bash
make help
make run BOOK=book.pdf WORKERS=4
make graph
make validation-auto
make network-analysis
make salt-analysis
make corpus-audit
make citation-verify
make research-outputs
make delete-preview BOOK=book.pdf
make delete BOOK=book.pdf
```

Manual equivalents:

```bash
python3 pipeline/pipeline.py --book book.pdf --workers 4
python3 pipeline/rebuild_graph.py
python3 pipeline/validate_evidence.py
python3 pipeline/analyze_network.py
python3 pipeline/analyze_salt.py
python3 pipeline/audit_corpus.py
python3 pipeline/verify_citations.py
```

## Important Outputs

- `pipeline/outputs/cleaned_aggregated_edges.csv`: cleaned relation table used by later checks
- `pipeline/outputs/cleaned_entities.json`: current entity list and inferred types
- `pipeline/outputs/edge_validation.csv`: edge rows classified as `Validated`, `Probable`, or `Missing`
- `pipeline/outputs/network_visualization.html`: vis-network browser graph
- `pipeline/outputs/network_cytoscape.html`: Cytoscape browser graph
- `pipeline/outputs/network_analysis/NETWORK_ANALYSIS.md`: general network metrics
- `pipeline/outputs/network_analysis/NETWORK_INTERPRETATION.md`: generated interpretation scaffold
- `pipeline/outputs/salt_analysis/SALT_METRICS.md`: salt-specific metric tables
- `pipeline/outputs/salt_analysis/SALT_INTERPRETATION.md`: generated salt interpretation scaffold
- `pipeline/outputs/corpus/CORPUS_STATISTICS.md`: corpus totals and source table
- `pipeline/outputs/citations/CITATION_VERIFICATION.md`: PDF page verification summary
- `pipeline/outputs/research_writeup/DH_RELATED_WORK.md`: digital humanities related-work note

## Research Model

The current graph code keeps five broad entity types:

- `PERSON`
- `GROUP`
- `COMMODITY`
- `LOCATION`
- `CONCEPT`

Relations are normalized through `pipeline/graph_rules.py`. The active allowed relation set is:

- `trades_with`
- `extracts_from`
- `taxes`
- `licenses`
- `controls`
- `governs`
- `supplies`
- `depends_on`
- `transports_via`
- `monopolizes`
- `disputes`
- `negotiates_with`

The current research focus node is `salt`.

## Validation And Analysis

The repository separates graph construction from research claims:

- `validate_evidence.py` checks whether evidence snippets or entity pairs can be found in extracted corpus text.
- `verify_citations.py` maps evidence snippets back to one-indexed PDF page candidates.
- `analyze_network.py` writes general graph diagnostics, community summaries, and interpretation scaffolds.
- `analyze_salt.py` tests salt centrality, removal effect, commodity-label nulls, source-drop robustness, community membership, and shortest paths through salt.
- `audit_salt_recall.py` scans corpus sentences for research-circuit coverage against final graph evidence.

Treat the graph as an extracted, evidence-weighted model of the corpus, not a complete reconstruction of the historical economy.

## Troubleshooting

If a PDF is not found, confirm the file is inside `Books/` and pass the exact filename:

```bash
make run BOOK=book.pdf
```

If relation extraction is slow or unstable, lower worker count:

```bash
make run BOOK=book.pdf WORKERS=1
```

If Ollama fails, check the service and model:

```bash
ollama list
ollama pull llama3
ollama serve
```

If TextRazor fails, check the API key, internet access, and quota.

If the graph looks noisy, review `pipeline/graph_rules.py`, `pipeline/selected_topics.txt`, `pipeline/outputs/entity_type_review.csv`, and `pipeline/outputs/edge_validation.csv`.

## Status

This is an active research codebase. The current production path is the `pipeline/` pipeline plus the validation and analysis scripts listed above. Older geoparser outputs and domain-adaptive NER experiments are kept for comparison and research history.
