# Conference Tables

Note: Table 1 summarizes the 19 source-linked corpus files in `Mine/outputs/corpus/corpus_table.csv`. Years and source classifications are taken from repository filenames/PDF title pages where visible, otherwise marked `n.d.` or inferred conservatively from the source title.

## Table 1. Corpus Summary

| Source | Year | Source type | Region | Classification |
| --- | ---: | --- | --- | --- |
| Becoming India | n.d. | Historical monograph | Western Himalayas | Secondary |
| British Garhwal | 1910 | District gazetteer | Garhwal | Primary |
| Central Asia and Tibet, Vol. 1 | 1903 | Travelogue / expedition account | Central Asia, Tibet | Primary |
| Central Asia and Tibet, Vol. 2 | 1903 | Travelogue / expedition account | Central Asia, Tibet | Primary |
| Western Himalaya and Tibet (Gutenberg) | n.d. | Travelogue / digitized book | Western Himalaya, Tibet | Primary |
| Adaptation to a Changing Salt Trade: Humla | 1983 | Journal article | Humla, Nepal | Secondary |
| Himalayan Gazetteer | 1882 | Gazetteer | Western Himalayas | Primary |
| Kashmir and Jammu Gazetteer | 1909 | Imperial gazetteer | Kashmir, Jammu | Primary |
| Ladakh | n.d. | Regional historical source | Ladakh | Primary |
| Mandi State Gazetteer | 1904 | State gazetteer | Mandi | Primary |
| Memo: Relations with Tibet | n.d. | Administrative memorandum | Tibet frontier | Primary |
| Report on Tibet | 1903 | Administrative report | Tibet | Primary |
| Rupshu: Annual Trek to Tso Kar | 1990 | Ethnographic article | Rupshu, Ladakh | Secondary |
| Salt Industry in India | n.d. | Administrative / industry report | India | Primary |
| Salt Routes and Barter Caravans | n.d. | Book chapter | Tibet, Nepal Himalaya | Secondary |
| The Salt Trips in Tibet and the Himalayas | 2022 | Journal article | Tibet, Himalayas | Secondary |
| Himalayan Traders: Life in Highland Nepal | n.d. | Ethnography / monograph | Highland Nepal | Secondary |
| Trans-Himalayan Traders | n.d. | Ethnographic source | Himalayan trade regions | Secondary |
| Transformation Processes in Nomadic Pastoralism | 2013 | Journal article | Ladakh | Secondary |

## Table 2. Network Characteristics

Graph views from `Mine/outputs/network_analysis/graph_diagnostics.csv` and Louvain medians from `louvain_community_summary.csv`.

| View | Nodes | Edges | Components | Largest component | Density | Avg. degree | Avg. strength | Clustering | LCC path length | LCC diameter | Louvain communities | Modularity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Validated | 999 | 958 | 135 | 692 | 0.0019 | 1.92 | 2.02 | 0.0069 | 5.64 | 15 | 22 | 0.815 |
| Validated + probable | 1146 | 1086 | 157 | 780 | 0.0017 | 1.90 | 1.99 | 0.0062 | 5.78 | 19 | 24 | 0.826 |
| Validated, concepts excluded | 509 | 422 | 112 | 229 | 0.0033 | 1.66 | 1.74 | 0.0096 | 4.73 | 11 | 13 | 0.762 |
| Validated + probable, concepts excluded | 602 | 497 | 131 | 265 | 0.0027 | 1.65 | 1.73 | 0.0090 | 4.88 | 11 | 14 | 0.780 |
| Validated trade relations only | 637 | 591 | 103 | 384 | 0.0029 | 1.86 | 1.96 | 0.0098 | 5.59 | 14 | 17 | 0.786 |
| Validated + probable trade only | 735 | 669 | 124 | 426 | 0.0025 | 1.82 | 1.91 | 0.0079 | 5.65 | 14 | 18 | 0.797 |

## Table 3. Commodity Centrality Comparison

Strict validated graph view; betweenness is calculated within the largest connected component.

| Commodity | Degree | Strength | Betweenness | PageRank |
| --- | ---: | ---: | ---: | ---: |
| Salt | 31 | 36.0 | 0.194 | 0.0120 |
| Yak | 13 | 14.0 | 0.090 | 0.0047 |
| Grain | 12 | 12.0 | 0.071 | 0.0041 |
| Tea | 7 | 7.0 | 0.025 | 0.0028 |
| Wool | 5 | 5.0 | 0.027 | 0.0017 |
| Pashm | 4 | 5.0 | 0.012 | 0.0017 |
| Barley | 4 | 4.0 | 0.007 | 0.0014 |
