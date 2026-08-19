# Historical NLP Knowledge Graphs for Himalayan Trade Networks

This repository is an active research pipeline for turning historical PDFs into evidence-backed knowledge graphs about Himalayan salt routes, commodity circulation, and frontier governance.

The core question is whether salt functioned as a structural backbone for multi-commodity trade and political economy in the Western Himalayas. The pipeline extracts text, entities, co-occurrences, relation triples, cleaned graph outputs, validation tables, interactive visualizations, and salt-specific network metrics.

## Repository Layout

```text
.
├── Books/                         # Input PDFs for pipeline runs
├── corpus/                        # Extracted text files, one per PDF
├── Mine/
│   ├── pipeline.py                # Orchestrates one PDF through the main pipeline
│   ├── script.py                  # PDF text extraction with PyMuPDF
│   ├── Textrazor.py               # TextRazor entity/topic extraction
│   ├── Topics.py                  # Deduplicates extracted topics
│   ├── process2.py                # Topic-anchored entity co-occurrence mining
│   ├── relation.py                # Ollama/Llama relation extraction
│   ├── correct_entity_types.py    # Rebuilds entity type review/corrections
│   ├── rebuild_graph.py           # Rebuilds cleaned graph and HTML visualizations
│   ├── evidence_validate.py       # Checks extracted edges against corpus text
│   ├── network_analysis.py        # General graph diagnostics/community analysis
│   ├── salt_analysis.py           # Salt centrality, robustness, and brokerage metrics
│   ├── salt_recall_audit.py       # Audits research-circuit sentence coverage
│   ├── corpus_audit.py            # Corpus statistics and related-work writeup
│   ├── citation_verify.py         # Finds PDF page candidates for edge evidence
│   ├── graph_rules.py             # Entity aliases, relation rules, visual styling
│   ├── Selected_Topics.txt        # Manually curated topic anchors
│   ├── Results/                   # Per-source extraction outputs
│   └── outputs/                   # Aggregated graph, validation, and analysis outputs
├── Bibliography/                  # Bibliographic PDFs and figures
├── References/                    # Reports and reference material
├── Domain-Adaptive-NER-main/      # Experimental custom NER work
└── geoparser-1.3/                 # Older geospatial/geoparser tooling
```

Main data flow:

```text
Books/*.pdf
  -> corpus/*.txt
  -> Mine/Results/<book>[_timestamp]/
  -> Mine/outputs/
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
xdg-open Mine/outputs/network_visualization.html
```

The visualization is also copied to `Mine/network_visualization.html`.

## Pipeline Stages

| Step | Script | Output |
| --- | --- | --- |
| 1 | `Mine/script.py` | `corpus/<book>.txt` |
| 2 | `Mine/Textrazor.py` | `Mine/Results/<book>/ner_results.txt` |
| 3 | `Mine/Topics.py` | `Mine/unique_topics.txt` |
| 4 | `Mine/process2.py` | `Mine/Results/<book>/entity_cooccurrences.txt` |
| 5 | `Mine/relation.py` | `Mine/Results/<book>/weighted_knowledge_graph.csv` |
| 6 | `Mine/correct_entity_types.py` | `Mine/outputs/cleaned_entities.json`, `entity_type_review.csv` |
| 7 | `Mine/rebuild_graph.py` | cleaned edge tables and HTML graphs |
| 8 | `Mine/salt_recall_audit.py` | `salt_recall_audit.csv`, `salt_recall_summary.csv` |

`Mine/pipeline.py` resumes completed steps when its `.pipeline_state.json` and expected outputs are present.

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
python3 Mine/pipeline.py --book book.pdf --workers 4
python3 Mine/rebuild_graph.py
python3 Mine/evidence_validate.py
python3 Mine/network_analysis.py
python3 Mine/salt_analysis.py
python3 Mine/corpus_audit.py
python3 Mine/citation_verify.py
```

## Important Outputs

- `Mine/outputs/cleaned_aggregated_edges.csv`: cleaned relation table used by later checks
- `Mine/outputs/cleaned_entities.json`: current entity list and inferred types
- `Mine/outputs/edge_validation.csv`: edge rows classified as `Validated`, `Probable`, or `Missing`
- `Mine/outputs/network_visualization.html`: vis-network browser graph
- `Mine/outputs/network_cytoscape.html`: Cytoscape browser graph
- `Mine/outputs/network_analysis/NETWORK_ANALYSIS.md`: general network metrics
- `Mine/outputs/network_analysis/NETWORK_INTERPRETATION.md`: generated interpretation scaffold
- `Mine/outputs/salt_analysis/SALT_METRICS.md`: salt-specific metric tables
- `Mine/outputs/salt_analysis/SALT_INTERPRETATION.md`: generated salt interpretation scaffold
- `Mine/outputs/corpus/CORPUS_STATISTICS.md`: corpus totals and source table
- `Mine/outputs/citations/CITATION_VERIFICATION.md`: PDF page verification summary
- `Mine/outputs/research_writeup/DH_RELATED_WORK.md`: digital humanities related-work note

## Research Model

The current graph code keeps five broad entity types:

- `PERSON`
- `GROUP`
- `COMMODITY`
- `LOCATION`
- `CONCEPT`

Relations are normalized through `Mine/graph_rules.py`. The active allowed relation set is:

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

- `evidence_validate.py` checks whether evidence snippets or entity pairs can be found in extracted corpus text.
- `citation_verify.py` maps evidence snippets back to one-indexed PDF page candidates.
- `network_analysis.py` writes general graph diagnostics, community summaries, and interpretation scaffolds.
- `salt_analysis.py` tests salt centrality, removal effect, commodity-label nulls, source-drop robustness, community membership, and shortest paths through salt.
- `salt_recall_audit.py` scans corpus sentences for research-circuit coverage against final graph evidence.

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

If the graph looks noisy, review `Mine/graph_rules.py`, `Mine/Selected_Topics.txt`, `Mine/outputs/entity_type_review.csv`, and `Mine/outputs/edge_validation.csv`.

## Status

This is an active research codebase. The current production path is the `Mine/` pipeline plus the validation and analysis scripts listed above. Older geoparser outputs and domain-adaptive NER experiments are kept for comparison and research history.
