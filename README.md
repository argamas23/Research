# Historical NLP Knowledge Graphs for Himalayan Trade Networks

This repository contains a research pipeline for studying salt routes, commodity circulation, and frontier governance in the Western Himalayas. It combines historical source processing, named entity recognition, relation extraction, geospatial parsing, graph analytics, and interactive visualization to convert books and archival-style PDFs into structured knowledge graphs.

## Research Focus

The project investigates whether salt routes in the Western Himalayas functioned as a structural backbone for multi-commodity trade networks and as part of the political economy of frontier governance in Colonial North India.

Key themes include:

- Salt, pashm, wool, barley, tea, grain, livestock, and other traded commodities
- Ladakh, Tibet, Rupshu, Changthang, Kashmir, and related frontier regions
- Trade routes, barter networks, taxation, licensing, sovereignty, and administration
- Pastoral communities, merchants, colonial records, gazetteers, travel accounts, and historical monographs

## What This Repository Does

The main pipeline converts raw PDF books into weighted knowledge graphs:

1. Extract text from historical PDFs.
2. Run NER and topic extraction.
3. Deduplicate and manually filter research-relevant topics.
4. Detect entity co-occurrences in local text windows.
5. Extract subject-relation-object triples using a local LLM.
6. Aggregate triples into weighted graph CSVs.
7. Clean, classify, and export graph data.
8. Generate network metrics, GraphML files, geotagged outputs, maps, timelines, and interactive HTML visualizations.

## Repository Structure

```text
.
├── Books/                         # Source PDFs used as the historical corpus
├── corpus/                        # Extracted plain-text versions of PDFs
├── Mine/                          # Main NLP and graph pipeline
│   ├── pipeline.py                # Orchestrates PDF -> text -> NER -> topics -> co-occurrence -> relations
│   ├── script.py                  # PDF text extraction using PyMuPDF
│   ├── Textrazor.py               # TextRazor NER/topic extraction
│   ├── Topics.py                  # Topic extraction and deduplication
│   ├── process2.py                # Entity co-occurrence mining
│   ├── relation.py                # LLM-based relation extraction with Ollama/Llama 3
│   ├── aggregate_graph.py         # Graph aggregation, cleaning, metrics, GraphML, and HTML visualization
│   ├── View.py                    # Simple GraphML-to-HTML visualization helper
│   ├── Results/                   # Per-document NER, co-occurrence, relation, map, and timeline outputs
│   └── outputs/                   # Aggregated graph outputs and cleaned network artifacts
├── Domain-Adaptive-NER-main/      # Experimental custom NER model training pipeline
│   ├── pretraining/               # Domain-adaptive BERT masked-language pretraining
│   └── finetuning/                # BERT/BiLSTM token-classification experiments
├── geoparser-1.3/                 # Edinburgh Geoparser tooling for geotagging/maps/timelines
├── Bibliography/                  # Research bibliography and diagrams
├── References/                    # Reports and reference material
└── agents.md                      # Research schema, entity categories, relation categories, and validation rules
```

## Main Pipeline

Run the full pipeline for one book:

```bash
python3 Mine/pipeline.py --book <book_name>.pdf
```

The PDF should exist inside `Books/`. The pipeline creates a timestamped output directory under `Mine/Results/`.

Pipeline stages:

| Step | Script | Purpose | Main Output |
| --- | --- | --- | --- |
| 1 | `Mine/script.py` | Converts PDF pages to plain text using PyMuPDF | `corpus/<book>.txt` |
| 2 | `Mine/Textrazor.py` | Runs TextRazor entity and topic extraction in chunks | `ner_results.txt` |
| 3 | `Mine/Topics.py` | Extracts and deduplicates topic labels | `Mine/unique_topics.txt` |
| 4 | `Mine/process2.py` | Finds nearby entities around selected anchor entities | `entity_cooccurrences.txt` |
| 5 | `Mine/relation.py` | Uses Ollama/Llama 3 to extract S-R-O triples | `weighted_knowledge_graph.csv` |
| 6 | `Mine/aggregate_graph.py` | Aggregates, cleans, scores, exports, and visualizes graphs | `Mine/outputs/*` |

## Graph Aggregation and Visualization

After generating per-book weighted graph CSVs, run:

```bash
python3 Mine/aggregate_graph.py
```

This scans `Mine/Results/` for weighted knowledge graph CSVs and creates aggregated outputs in `Mine/outputs/`, including:

- `aggregated_edges.csv`
- `network_metrics.csv`
- `network.graphml`
- `cleaned_entities.json`
- `cleaned_relations.jsonl`
- `cleaned_aggregated_edges.csv`
- `cleaned_network_metrics.csv`
- `cleaned_network.graphml`
- `network_visualization.html`

The generated HTML visualization uses `vis-network` to inspect graph nodes, edges, entity types, relation labels, and weights interactively.

## Domain-Adaptive NER

The `Domain-Adaptive-NER-main/` directory contains an experimental custom NER workflow for historical documents.

It includes:

- PDF-to-text preprocessing for a domain corpus
- BERT masked-language pretraining on historical text
- Prodigy-style annotation cleaning
- JSONL-to-token-label dataset parsing
- BERT/BiLSTM token-classification models
- Evaluation with accuracy, F1 score, and classification reports

Entity labels used in the custom NER experiments include:

- `GEO`: geographical entities
- `PEO`: people
- `CMD`: commodities
- `O`: non-entity tokens

Example commands from that module:

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

## Geospatial Outputs

The repository also includes outputs from the Edinburgh Geoparser. These produce:

- geotagged HTML files
- gazetteer XML
- NER-tagged XML
- event XML
- timeline HTML
- map/display HTML

Examples are stored under document-specific directories such as:

```text
Mine/Results/Ladakh/Edinburg/
Mine/Results/1820/Edinburg/
Mine/Results/1825/Edinburgh/
Mine/Results/Becoming India/Edinburg/
```

## Tech Stack

Core stack:

- Python
- PyMuPDF / `fitz`
- TextRazor API
- Ollama with Llama 3
- spaCy
- NetworkX
- PyVis / vis-network
- CSV, JSON, JSONL, GraphML, XML, HTML

Machine learning and NER experiments:

- PyTorch
- Hugging Face Transformers
- BERT
- BiLSTM
- CRF experiments
- pandas
- NumPy
- NLTK
- scikit-learn
- tqdm
- Prodigy-style annotations

Geospatial tooling:

- Edinburgh Geoparser
- Gazetteer-based place resolution
- Leaflet-style map outputs
- OpenStreetMap/Mapbox-compatible visualization outputs

## Installation Notes

There is currently no single `requirements.txt`, so install dependencies according to the pipeline section you want to run.

For the main pipeline, typical Python dependencies include:

```bash
pip install pymupdf textrazor ollama spacy networkx pyvis pandas numpy tqdm
python3 -m spacy download en_core_web_sm
```

For the domain-adaptive NER experiments:

```bash
pip install torch transformers pandas numpy nltk scikit-learn tqdm jsonlines regex torchcrf pytorch-transformers
```

Ollama must be installed separately and the `llama3` model should be available locally:

```bash
ollama pull llama3
```

## API Keys and Security

TextRazor requires an API key. Avoid committing API keys to the repository. Prefer loading secrets from environment variables or a local ignored config file.

If this repository is pushed publicly, rotate any API keys that were previously committed.

## Outputs and Artifacts

The repository already contains generated artifacts from multiple documents, including:

- text corpora in `corpus/`
- NER and topic outputs in `Mine/Results/`
- entity co-occurrence outputs
- filtered relation CSVs
- weighted knowledge graph CSVs
- geotagged maps and timelines
- cleaned graph entities and relations
- network metrics
- GraphML files for graph tools such as Gephi
- browser-ready HTML graph visualizations

## Current Status

This is an active research codebase. Some scripts are production pipeline components, while others are experiments or older model attempts kept for reference. The most important current path is:

```text
Books/*.pdf
  -> corpus/*.txt
  -> Mine/Results/<book>/ner_results.txt
  -> Mine/Results/<book>/entity_cooccurrences.txt
  -> Mine/Results/<book>/weighted_knowledge_graph.csv
  -> Mine/outputs/
```

## Resume Summary

This project can be summarized as an end-to-end historical NLP and knowledge-graph system for extracting, analyzing, and visualizing trade, commodity, and governance relations from Himalayan historical texts.
