# Historical NLP Knowledge Graphs for Himalayan Trade Networks

This repository contains an end-to-end research pipeline for turning historical PDFs into knowledge graphs about salt routes, commodity circulation, and frontier governance in the Western Himalayas. It combines PDF text extraction, TextRazor NER/topic extraction, entity co-occurrence mining, LLM-assisted relation extraction, graph cleaning, network analysis, GraphML export, and interactive HTML visualization.

The main research question is whether salt routes in the Western Himalayas functioned as a structural backbone for multi-commodity trade networks and as part of the political economy of frontier governance in Colonial North India.

## Research Scope

The project focuses on:

- Salt, pashm, wool, barley, tea, grain, livestock, musk, butter, rice, and related commodities
- Ladakh, Tibet, Rupshu, Changthang, Kashmir, Humla, Dolpo, Zanskar, and neighboring Himalayan regions
- Trade routes, barter networks, taxation, licensing, sovereignty, administration, monopolies, and political control
- Pastoral communities, merchants, colonial officials, frontier states, monasteries, and local institutions
- Gazetteers, travel accounts, administrative records, reports, historical monographs, and research PDFs

The schema and validation principles are summarized in `agents.md`. In short: co-occurrence alone is not treated as a relation; relation edges should have textual evidence and should be historically meaningful.

## Repository Layout

```text
.
├── Books/                         # Input PDFs for the main pipeline
├── corpus/                        # Extracted text files generated from PDFs
├── Mine/                          # Main NLP and graph pipeline
│   ├── pipeline.py                # Full PDF -> graph pipeline
│   ├── script.py                  # PDF text extraction using PyMuPDF
│   ├── Textrazor.py               # TextRazor entity/topic extraction
│   ├── Topics.py                  # Topic extraction and deduplication
│   ├── process2.py                # Entity co-occurrence mining
│   ├── relation.py                # Ollama/Llama 3 relation extraction
│   ├── aggregate_graph.py         # Graph aggregation, cleaning, metrics, HTML export
│   ├── config.py                  # Entity aliases, type overrides, relation mappings
│   ├── Selected_Topics.txt        # Manually selected research-relevant topic anchors
│   ├── Results/                   # Per-document pipeline outputs
│   └── outputs/                   # Aggregated graph outputs
├── Bibliography/                  # Bibliographic PDFs and diagrams
├── References/                    # Reports and reference material
├── Mine/Older Results/            # Earlier experiments and generated artifacts
├── Mine/Trial Results/            # Trial extraction outputs
└── agents.md                      # Research schema and validation guidance
```

Some older or experimental folders may be present for reference. The current main path is:

```text
Books/*.pdf
  -> corpus/*.txt
  -> Mine/Results/<book_timestamp>/
  -> Mine/outputs/
```

## Prerequisites

Use Python 3.10+ if possible.

Install the main pipeline dependencies:

```bash
pip install pymupdf textrazor ollama spacy networkx pyvis pandas numpy tqdm
python3 -m spacy download en_core_web_sm
```

Install and prepare Ollama separately:

```bash
ollama pull llama3
ollama serve
```

TextRazor requires an API key. The current script contains a hard-coded key, but for a public or shared version you should move it to an environment variable or local ignored config file before publishing the repository.

## Quick Start

1. Put a PDF inside `Books/`.

```bash
mkdir -p Books
cp /path/to/book.pdf Books/
```

2. Run the full pipeline.

```bash
python3 Mine/pipeline.py --book book.pdf --workers 4
```

3. Open the generated graph.

```bash
xdg-open Mine/outputs/network_visualization.html
```

If `xdg-open` is not available, open `Mine/outputs/network_visualization.html` manually in a browser.

## Full Pipeline Command

Run the complete pipeline for one PDF:

```bash
python3 Mine/pipeline.py --book <book_name>.pdf --workers 4
```

The PDF must be inside `Books/`. The pipeline creates a timestamped result directory under `Mine/Results/`, for example:

```text
Mine/Results/Rupshu_20260702_143000/
```

Pipeline stages:

| Step | Script | Purpose | Main output |
| --- | --- | --- | --- |
| 1 | `Mine/script.py` | Extract PDF text with PyMuPDF | `corpus/<book>.txt` |
| 2 | `Mine/Textrazor.py` | Extract entities and topics | `ner_results.txt` |
| 3 | `Mine/Topics.py` | Merge and deduplicate topic labels | `Mine/unique_topics.txt` |
| 4 | `Mine/process2.py` | Find nearby entities around selected topic anchors | `entity_cooccurrences.txt` |
| 5 | `Mine/relation.py` | Extract subject-relation-object triples with Ollama/Llama 3 | `weighted_knowledge_graph.csv` |
| 6 | `Mine/aggregate_graph.py` | Aggregate all per-book graphs and build visual outputs | `Mine/outputs/*` |
| 7 | `Mine/update_config.py` | Add newly classified entities to `config.py` | updated `Mine/config.py` |

The `--workers` flag controls concurrent Ollama relation-extraction calls. Use fewer workers if Ollama becomes slow or runs out of memory:

```bash
python3 Mine/pipeline.py --book book.pdf --workers 1
```

## Run Stages Manually

You can run each stage by hand when debugging or reusing intermediate files.

Extract PDF text:

```bash
python3 Mine/script.py Books/book.pdf corpus/book.txt
```

Run TextRazor NER/topic extraction:

```bash
python3 Mine/Textrazor.py \
  --input corpus/book.txt \
  --output Mine/Results/book/ner_results.txt
```

Extract and merge topic labels:

```bash
python3 Mine/Topics.py \
  --ner_file Mine/Results/book/ner_results.txt \
  --output_file Mine/unique_topics.txt
```

Run entity co-occurrence mining:

```bash
python3 Mine/process2.py \
  --corpus_file corpus/book.txt \
  --ner_file Mine/Results/book/ner_results.txt \
  --selected_topics Mine/Selected_Topics.txt \
  --all_topics Mine/unique_topics.txt \
  --output_file Mine/Results/book/entity_cooccurrences.txt
```

Run relation extraction with Ollama:

```bash
python3 Mine/relation.py \
  --corpus_file corpus/book.txt \
  --coocc_file Mine/Results/book/entity_cooccurrences.txt \
  --topics_file Mine/Selected_Topics.txt \
  --output_file Mine/Results/book/weighted_knowledge_graph.csv \
  --workers 4
```

Regenerate the aggregate graph and visualization from all result folders:

```bash
python3 Mine/aggregate_graph.py
```

Update entity type overrides after aggregation:

```bash
python3 Mine/update_config.py
```

## Graph Outputs

`Mine/aggregate_graph.py` scans `Mine/Results/` for files matching `*weighted*knowledge*graph*.csv` and writes aggregated outputs to `Mine/outputs/`.

Important files:

- `Mine/outputs/aggregated_edges.csv`: raw aggregated directed edges
- `Mine/outputs/network_metrics.csv`: metrics for the uncleaned graph
- `Mine/outputs/network.graphml`: uncleaned GraphML export
- `Mine/outputs/cleaned_entities.json`: cleaned entity list with inferred types
- `Mine/outputs/cleaned_relations.jsonl`: cleaned relation triples with evidence and source books
- `Mine/outputs/cleaned_aggregated_edges.csv`: cleaned edge table
- `Mine/outputs/cleaned_network_metrics.csv`: metrics for the cleaned graph
- `Mine/outputs/cleaned_network.graphml`: cleaned GraphML export for Gephi or other graph tools
- `Mine/outputs/incoming_nodes.csv`: report of newly appearing nodes by source book
- `Mine/outputs/island_components.csv`: disconnected component report for graph review
- `Mine/outputs/network_visualization.html`: browser-ready interactive graph

The same visualization is also copied to:

```text
Mine/network_visualization.html
```

## Interactive Visualization

Open:

```bash
xdg-open Mine/outputs/network_visualization.html
```

The visualization supports:

- Filtering by entity type
- Filtering by relation type
- Searching node labels
- Focusing the first matching search result
- Clicking nodes to highlight their neighborhood
- Filtering edges by minimum weight
- Toggling edge labels
- Toggling graph physics
- Hovering nodes and edges to inspect metadata, weights, source books, and relation evidence

The current visualization uses `vis-network` in the browser and is generated by `Mine/aggregate_graph.py`.

## Research Schema

Entity categories used in the broader research design include:

- `PERSON`
- `COMMUNITY`
- `COMMODITY`
- `LOCATION`
- `TRADE_ROUTE`
- `ADMINISTRATIVE_UNIT`
- `INSTITUTION`
- `TREATY`
- `TAXATION_MECHANISM`
- `GOVERNANCE_PRACTICE`
- `ECONOMIC_ACTIVITY`
- `INFRASTRUCTURE`

The current cleaned graph code primarily keeps:

- `PERSON`
- `GROUP`
- `COMMODITY`
- `LOCATION`
- `CONCEPT`

Relation categories include:

- `trades_with`
- `exchanges_for`
- `extracts_from`
- `transports_via`
- `taxes`
- `regulates`
- `governs`
- `controls`
- `disputes`
- `licenses`
- `monopolizes`
- `supplies`
- `depends_on`
- `connects_to`
- `migrates_through`
- `administers`
- `negotiates_with`

The active relation mapping is configured in `Mine/config.py`.

## Configuration Files

`Mine/Selected_Topics.txt`

This file controls which TextRazor topic groups are treated as anchor topics for co-occurrence mining. Edit it when you want to focus the extraction on a narrower research theme.

`Mine/unique_topics.txt`

This is generated and updated by `Mine/Topics.py`. It contains all deduplicated topic labels found across processed NER outputs.

`Mine/config.py`

This contains:

- Entity aliases
- Entity type overrides
- Relation mapping patterns
- Entity-type color and shape settings for visualization
- Output directory paths
- The research focus node, currently `salt`

## Common Commands

Show help for the full pipeline:

```bash
python3 Mine/pipeline.py --help
```

Show help for relation extraction:

```bash
python3 Mine/relation.py --help
```

Regenerate only the HTML graph and aggregate reports:

```bash
python3 Mine/aggregate_graph.py
```

Run with conservative single-thread relation extraction:

```bash
python3 Mine/pipeline.py --book book.pdf --workers 1
```

Run with faster relation extraction:

```bash
python3 Mine/pipeline.py --book book.pdf --workers 4
```

Check which weighted graph CSVs will be aggregated:

```bash
find Mine/Results -name '*weighted*knowledge*graph*.csv' -print
```

Inspect the strongest cleaned edges:

```bash
head -n 30 Mine/outputs/cleaned_aggregated_edges.csv
```

Inspect disconnected components:

```bash
head -n 30 Mine/outputs/island_components.csv
```

## Troubleshooting

If the PDF is not found:

```text
Error: Book '<name>.pdf' not found in Books/
```

Make sure the file exists inside `Books/` and that the name passed to `--book` matches exactly.

If Ollama relation extraction fails, check that Ollama is running and that the model exists:

```bash
ollama list
ollama pull llama3
ollama serve
```

If relation extraction is too slow or unstable, reduce concurrency:

```bash
python3 Mine/relation.py ... --workers 1
```

If spaCy model loading fails:

```bash
python3 -m spacy download en_core_web_sm
```

If TextRazor fails, check the API key, internet access, and API quota.

If the graph looks noisy, review:

- `Mine/config.py` for entity aliases and type overrides
- `Mine/Selected_Topics.txt` for anchor-topic selection
- `Mine/outputs/island_components.csv` for small disconnected graph islands
- `Mine/outputs/cleaned_aggregated_edges.csv` for suspicious extracted relations

## Domain-Adaptive NER Experiments

The repository may include a `Domain-Adaptive-NER-main/` directory for experimental custom NER training.

Typical commands:

```bash
cd Domain-Adaptive-NER-main/pretraining
python preprocessing_pretraining_docs.py
python adaptive_pretraining.py
```

```bash
cd Domain-Adaptive-NER-main/finetuning
python ner_model_1.py --lr 0.0001 --eps 50 --bs 8 --d1 128 --d2 32
python ner_model_2.py --lr 0.0001 --eps 200 --bs 8 --d1 128 --d2 32
```

These experiments are separate from the main `Mine/` pipeline.

## Geospatial and Older Outputs

The repository also stores outputs from geospatial and earlier experiments, including Edinburgh Geoparser artifacts:

- geotagged HTML files
- gazetteer XML
- NER-tagged XML
- event XML
- timeline HTML
- map/display HTML

Examples may appear under directories such as:

```text
Mine/Results/Ladakh/Edinburg/
Mine/Older Results/1820/Edinburg/
Mine/Older Results/1825/Edinburgh/
Mine/Older Results/Becoming India/Edinburg/
```

## Current Status

This is an active research codebase. The most important production path is the `Mine/` pipeline. Older outputs, trial outputs, geospatial exports, and NER training experiments are kept because they preserve research history and may be useful for comparison.

The expected final result is a cleaned, inspectable knowledge graph that helps evaluate whether salt operated as:

- a commodity
- an infrastructural system
- a governance mechanism
- a backbone of multi-commodity circulation across the Himalayan frontier
