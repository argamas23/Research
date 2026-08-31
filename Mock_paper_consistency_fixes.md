# Mock Paper Consistency Fixes

Source checked: `/home/samagra-bharti/Downloads/Mock .pdf`

Analysis rerun:

- `make graph`
- `make validation-auto`
- `make network-analysis`
- `make corpus-audit`
- `make citation-verify`
- `Mine/salt_analysis.py` full report run was interrupted after several silent minutes; current salt core metrics and validated-graph permutation were recomputed directly from `Mine/outputs/edge_validation.csv`.

## Current Numbers To Use

| Item | Correct value |
| --- | ---: |
| Corpus sources | 19 |
| PDF pages | 4,114 |
| Words | 1,824,483 |
| Relation rows / extracted edges subjected to validation | 1,475 |
| Validated rows | 1,227 |
| Probable rows | 138 |
| Missing / Unsupported rows | 110 |
| Validated percentage | 83.2% |
| Probable percentage | 9.4% |
| Missing percentage | 7.5% |
| Validated graph nodes | 1,171 |
| Validated graph unique edges | 1,184 |
| Connected components | 141 |
| Largest component nodes | 836 |
| Density | 0.00173 |
| Average degree | 2.02 |
| Louvain communities, validated median | 22 |
| Louvain modularity, validated median | 0.799 |
| Salt degree, validated | 44 |
| Salt weighted degree / strength, validated | 52 |
| Salt betweenness, validated | 0.2173 |
| Salt PageRank, validated | 0.0135 |
| Components after removing salt | 157 |
| Largest component after removing salt | 805 |
| Global efficiency loss after removing salt | 0.0101 |
| Salt participation, validated median | 0.510 |
| Salt permutation p_ge_salt, 100-run validated graph | 0.0099 |

## Replace These In The PDF Text

### Methodology: Corpus and Data Preparation

Replace:

> The corpus comprises 18 sources concerning salt, commodity circulation, trade routes, political relations across Western Himalayas and adjoining Tibetan regions.

With:

> The corpus comprises 19 sources concerning salt, commodity circulation, trade routes, and political relations across the Western Himalayas and adjoining Tibetan regions.

### Validation and Network Analysis

Replace:

> The final product from 18 sources turns out to be 818 relation rows, out of which 654 were classified as Validated, 98 as Probable and 67 as Missing / Unsupported.

With:

> The final product from 19 sources contains 1,475 extracted relation rows, of which 1,227 were classified as Validated, 138 as Probable, and 110 as Missing / Unsupported.

### Results: Extraction and Network Characteristics

Replace the opening paragraph with:

> The final corpus is composed of 19 sources, including colonial gazetteers, travel accounts, administrative reports, and later historical or ethnographic accounts concerning Himalayan trade, especially salt circulation. Of the 1,475 relation rows generated through relation extraction, 1,227 are validated, where relations can be linked back to individual source documents. The remaining 138 and 110 rows are probable and missing respectively. After aggregation, the final validated graph has 1,171 nodes and 1,184 unique edges across 141 connected components. The largest component comprises 836 nodes, with network density of 0.00173 and average degree 2.02.

Replace:

> Several iterations of Louvain community detection revealed a median number of 24.5 communities as well as a median modularity of 0.819.

With:

> Several iterations of Louvain community detection revealed a median number of 22 communities as well as a median modularity of 0.799 in the validated graph.

### Results: Multi Commodity Network

Replace:

> The validated graph suggests salt as a node to have a degree of 32, a weighted degree of 87 alongside 0.1914 and 0.0131 betweenness, centrality and page rank respectively.

With:

> The validated graph suggests salt as a node with degree 44, weighted degree 52, betweenness centrality 0.2173, and PageRank 0.0135.

Replace:

> Removing the salt node from the graph results in breaking the single huge component into 18 parts (132 to 150 in the whole graph) and also lowers global network efficiency.

With:

> Removing the salt node increases the number of connected components from 141 to 157, leaves the largest component with 805 nodes, and lowers global network efficiency by 0.0101.

Replace:

> Salt's participation coefficient of approximately 0.468 signifies it to be distributed across relational communities.

With:

> Salt's median participation coefficient of approximately 0.510 signifies that it is distributed across relational communities.

### Limitations

Replace:

> Of [N] extracted relations subjected to validation, [V] ([V%]) were classified as Validated, [P] ([P%]) as Probable, and [M] ([M%]) as Missing/Unsupported.

With:

> Of 1,475 extracted relations subjected to validation, 1,227 (83.2%) were classified as Validated, 138 (9.4%) as Probable, and 110 (7.5%) as Missing/Unsupported.

### Citation Placeholders

Replace:

> [CITE: network-analysis reference]

With a citation to a standard centrality/network-analysis source, e.g. Freeman (1977) for centrality.

Replace:

> [CITE: Louvain]

With Blondel et al. (2008), the standard Louvain community detection citation.

Add to references if missing:

> Freeman, L. C. (1977). A set of measures of centrality based on betweenness. Sociometry, 40(1), 35-41.

> Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics: Theory and Experiment, 2008(10), P10008.

## Other Consistency Edits

- Change future tense in the abstract/method from "will be employed" to past tense, because the results section reports completed analysis.
- Use one corpus count everywhere: 19 sources.
- Use one relation count everywhere: 1,475 relation rows.
- Use "validated graph" when reporting the 1,171-node / 1,184-edge network.
- Avoid "the network collapses without salt"; the updated removal result supports "brokerage" or "reduced efficiency," not collapse.
