# Historical NLP Knowledge Graphs for Himalayan Trade Networks

This repository contains a reproducible research pipeline for converting historical PDFs into evidence-backed knowledge graphs of Himalayan trade networks. It was built for a digital-history project on Himalayan salt routes, commodity circulation, frontier governance, and the political economy of exchange across Ladakh, Tibet, Kashmir, Garhwal, Kumaon, Nepal, and related mountain regions.

The central research question is whether salt functioned as a structural backbone for multi-commodity trade and governance in the Western Himalayas. The pipeline extracts text from historical sources, identifies entities and topics, mines co-occurrences, asks a local LLM to extract relation triples, cleans and normalizes the graph, validates extracted edges against the corpus, and produces network-analysis outputs and browser-based visualizations.

The graph should be read as a computational model of the deposited corpus, not as a complete reconstruction of Himalayan political economy. Each edge is an extracted claim that depends on OCR quality, named-entity recognition, relation extraction, cleaning rules, and later validation.

## Repository Contents

```text
.
├── Makefile                       # Convenience commands for running the pipeline
├── README.md                      # Project documentation
├── Books/                         # Input PDFs for new runs; ignored by git
├── corpus/                        # Extracted plain text from PDFs; ignored by git
├── bibliography/                  # Bibliographic/source PDFs, if supplied separately
├── figures/
│   ├── *.png, *.svg, *.pdf        # Maps, diagrams, and paper/conference figures
│   ├── maps/                      # Map-building script and geographic assets
│   └── paper_pngs/                # Final PNG figures and legend-building helper
└── pipeline/
    ├── pipeline.py                # Main one-book orchestrator
    ├── extract_text.py            # PDF text extraction; uses OCR fallback if available
    ├── extract_entities.py        # TextRazor entity/topic extraction
    ├── deduplicate_topics.py      # Deduplicates extracted topics
    ├── extract_cooccurrences.py   # Topic-anchored entity co-occurrence mining
    ├── extract_relations.py       # Local Ollama/Llama relation extraction
    ├── classify_entities.py       # Entity type inference and correction table
    ├── rebuild_graph.py           # Cleaned graph tables and HTML visualizations
    ├── validate_evidence.py       # Checks extracted edges against corpus text
    ├── verify_citations.py        # Finds PDF page candidates for edge evidence
    ├── analyze_network.py         # General graph metrics and communities
    ├── analyze_salt.py            # Salt-specific centrality and robustness metrics
    ├── audit_salt_recall.py       # Salt-circuit sentence coverage audit
    ├── audit_corpus.py            # Corpus statistics and related-work output
    ├── delete_source.py           # Removes one source and rebuilds graph outputs
    ├── graph_rules.py             # Entity aliases, allowed relations, colors, rules
    ├── selected_topics.txt        # Manually curated topic anchors
    ├── unique_topics.txt          # Deduplicated topic list from TextRazor outputs
    ├── API_KEYS.example           # Template for local API credentials
    ├── results/                   # Per-source extraction outputs
    └── outputs/                   # Aggregated graph, validation, analysis, visualizations
```

Main data flow:

```text
Books/*.pdf
  -> corpus/*.txt
  -> pipeline/results/<source>/
  -> pipeline/outputs/
```

In this checkout, `Books/`, `corpus/`, and `bibliography/` may be absent because the source PDFs and extracted text are ignored by git. A Zenodo deposit can include them separately if redistribution rights permit it. The generated graph and analysis outputs live under `pipeline/results/` and `pipeline/outputs/`.

## Requirements

Use Python 3.10 or newer.

Python packages:

```bash
pip install pymupdf textrazor ollama spacy networkx pandas numpy tqdm matplotlib pillow
python3 -m spacy download en_core_web_sm
```

System tools:

- `make`, for the convenience commands in the `Makefile`
- `ollama`, required for local LLM relation extraction
- `tesseract`, optional but recommended for scanned PDFs or pages with weak embedded text

Install and prepare Ollama separately:

```bash
ollama pull llama3
ollama serve
```

The relation-extraction script currently uses the local Ollama model name `llama3` in `pipeline/extract_relations.py`.

## API Keys

The current pipeline requires a TextRazor API key for `pipeline/extract_entities.py`.

Preferred setup, using an environment variable:

```bash
export TEXTRAZOR_API_KEY="your_textrazor_key_here"
```

Alternative setup, using a local key file:

```bash
cp pipeline/API_KEYS.example pipeline/API_KEYS.txt
```

Then edit `pipeline/API_KEYS.txt` and keep only the keys you need:

```text
OpenAI = YOUR_OPENAI_API_KEY
TextRazor = your_textrazor_key_here
```

`pipeline/API_KEYS.txt` is ignored by git and should not be uploaded to Zenodo or committed to a public repository.

The current production pipeline does not use the OpenAI API; relation extraction is done locally through Ollama. Keep an OpenAI key only if you add your own OpenAI-based scripts or experiments.

## Quick Start

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pymupdf textrazor ollama spacy networkx pandas numpy tqdm matplotlib pillow
python3 -m spacy download en_core_web_sm
```

Start Ollama in another terminal if it is not already running:

```bash
ollama serve
```

Place a PDF in `Books/`, then run the full pipeline for that source:

```bash
make run BOOK=book.pdf
```

Use fewer workers on a smaller machine:

```bash
make run BOOK=book.pdf WORKERS=1
```

Open the generated graph in a browser:

```bash
xdg-open pipeline/outputs/network_visualization.html
```

The main visualization is also copied to `pipeline/network_visualization.html`.

## Pipeline Stages

| Step | Script | Purpose | Main output |
| --- | --- | --- | --- |
| 1 | `pipeline/extract_text.py` | Extract text from a PDF, with optional Tesseract OCR fallback | `corpus/<book>.txt` |
| 2 | `pipeline/extract_entities.py` | Run TextRazor entity and topic extraction | `pipeline/results/<book>/ner_results.txt` |
| 3 | `pipeline/deduplicate_topics.py` | Build a deduplicated topic list | `pipeline/unique_topics.txt` |
| 4 | `pipeline/extract_cooccurrences.py` | Find entity co-occurrences around selected topics | `pipeline/results/<book>/entity_cooccurrences.txt` |
| 5 | `pipeline/extract_relations.py` | Extract relation triples with local Ollama/Llama | `pipeline/results/<book>/weighted_knowledge_graph.csv` |
| 6 | `pipeline/classify_entities.py` | Infer and review entity types | `pipeline/outputs/cleaned_entities.json`, `pipeline/outputs/entity_type_review.csv` |
| 7 | `pipeline/rebuild_graph.py` | Aggregate, clean, score, and visualize the graph | `pipeline/outputs/cleaned_aggregated_edges.csv`, HTML graphs |
| 8 | `pipeline/audit_salt_recall.py` | Audit salt-related sentence coverage | `pipeline/outputs/salt_recall_audit.csv`, `pipeline/outputs/salt_recall_summary.csv` |

`pipeline/pipeline.py` can resume a partly completed source if `.pipeline_state.json` and the expected output files exist in that source's result directory.

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
python3 pipeline/audit_salt_recall.py
python3 pipeline/validate_evidence.py
python3 pipeline/analyze_network.py
python3 pipeline/analyze_salt.py
python3 pipeline/audit_corpus.py
python3 pipeline/verify_citations.py
```

To preview removal of one source and its generated data:

```bash
make delete-preview BOOK=book.pdf
```

To remove it and rebuild graph outputs:

```bash
make delete BOOK=book.pdf
```

## Important Outputs

- `pipeline/outputs/cleaned_aggregated_edges.csv`: cleaned relation table used by validation and analysis.
- `pipeline/outputs/cleaned_entities.json`: current entity list and inferred entity types.
- `pipeline/outputs/entity_type_review.csv`: review table for entity classifications.
- `pipeline/outputs/edge_validation.csv`: edge rows classified as `Validated`, `Probable`, or `Missing`.
- `pipeline/outputs/network_visualization.html`: vis-network browser graph, also copied to `pipeline/network_visualization.html`.
- `pipeline/outputs/network_cytoscape.html`: Cytoscape browser graph, also copied to `pipeline/network_cytoscape.html`.
- `pipeline/outputs/network_visualization.css`: shared visualization stylesheet, also copied to `pipeline/network_visualization.css`.
- `pipeline/outputs/network_analysis/NETWORK_ANALYSIS.md`: general network metrics.
- `pipeline/outputs/network_analysis/NETWORK_INTERPRETATION.md`: interpretation scaffold generated from graph metrics.
- `pipeline/outputs/network_analysis/*.csv`: graph diagnostics and Louvain community tables.
- `pipeline/outputs/salt_analysis/SALT_METRICS.md`: salt-specific centrality, robustness, community, and path metrics.
- `pipeline/outputs/salt_analysis/SALT_INTERPRETATION.md`: salt-focused interpretation scaffold.
- `pipeline/outputs/salt_analysis/*.csv`: salt centrality, removal, null-model, community, source-drop, evidence, and path tables.
- `pipeline/outputs/corpus/CORPUS_STATISTICS.md`: corpus totals, source table, and related corpus measures.
- `pipeline/outputs/corpus/corpus_statistics.csv`: machine-readable corpus totals.
- `pipeline/outputs/corpus/corpus_table.csv`: machine-readable source-level corpus table.
- `pipeline/outputs/citations/CITATION_VERIFICATION.md`: page-candidate verification summary.
- `pipeline/outputs/citations/citation_verification.csv`: machine-readable citation verification table.
- `pipeline/outputs/research_writeup/DH_RELATED_WORK.md`: digital-humanities related-work note.
- `pipeline/outputs/research_writeup/CONFERENCE_TABLES.md`: tables prepared for conference/paper use.
- `pipeline/outputs/research_writeup/CONFERENCE_TABLES.tex`: LaTeX version of the conference tables.
- `pipeline/outputs/research_writeup/CTR_CLAIM_GRAPH_LEDGER.md`: claim-to-graph support ledger.
- `pipeline/outputs/entity_corrections_log.json`: log of entity-type corrections.
- `pipeline/outputs/strict_legacy_edge_review.csv`: review table for filtered legacy relation labels.
- `pipeline/outputs/cleaned_entities.json.*.bak`: timestamped backups from entity-cleaning runs.

Per-source outputs are stored in `pipeline/results/<source>/`:

- `ner_results.txt`
- `entity_cooccurrences.txt`
- `weighted_knowledge_graph.csv`
- `weighted_knowledge_graph.jsonl`, when available
- `weighted_knowledge_graph.ollama_errors.jsonl`, when Ollama parsing failures are logged
- `.pipeline_state.json`, when the source was run through the orchestrator

Some older exploratory source folders may contain extra geoparsing outputs such as maps, coordinates, tagged XML, or filtered relation tables. These are retained for comparison but are not required by the current pipeline.

## Research Model

The cleaned graph uses five broad entity types:

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

The current research focus node is `salt`. Salt variants and aliases are handled in `pipeline/graph_rules.py`, along with relation mapping, entity aliases, visual colors, and pruning rules.

## Validation And Analysis

The repository separates extraction from historical interpretation.

`validate_evidence.py` checks whether evidence snippets or entity pairs can be found in the extracted corpus text.

`verify_citations.py` maps evidence snippets back to one-indexed PDF page candidates in `Books/`.

`analyze_network.py` writes general graph diagnostics, Louvain community summaries, and interpretation scaffolds.

`analyze_salt.py` tests salt centrality, salt removal effects, commodity-label nulls, source-drop robustness, community membership, and shortest paths through salt.

`audit_salt_recall.py` scans corpus sentences for salt-related trade, taxation, transport, licensing, monopoly, and commodity-circuit language, then compares those sentences with final graph evidence.

## Reproducibility Notes

To reproduce the full pipeline, users need the source PDFs or extracted corpus text, the files in `pipeline/results/` and `pipeline/outputs/`, the software requirements listed above, a TextRazor API key, and a local Ollama installation with the `llama3` model.

Private credentials, paid API keys, and non-redistributable PDFs are not included. If source PDFs are absent, users can inspect the generated graph outputs and figures but cannot fully rerun text extraction or citation verification.

For anonymous review, exclude `.git/` history and any local source-PDF folders from the shared archive unless those files have been checked separately for identifying metadata and redistribution rights.

## Citation

If you use this repository or archived dataset, cite the Zenodo record for this release:

```text
Author(s). Historical NLP Knowledge Graphs for Himalayan Trade Networks. Zenodo. DOI: <add DOI>
```

## License And Rights

Code, generated outputs, figures, and source PDFs may have different rights status. Check redistribution rights before including PDFs in the archive.
