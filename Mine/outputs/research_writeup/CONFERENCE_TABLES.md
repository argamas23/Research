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

Compact version for the results section. LCC = largest connected component; Louvain reports median community count and modularity.

| Graph view | Nodes | Edges | Components | LCC size | Density | Avg. degree | Louvain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Validated | 999 | 958 | 135 | 692 | 0.0019 | 1.92 | 22 communities; Q = 0.815 |
| Concept-excluded | 509 | 422 | 112 | 229 | 0.0033 | 1.66 | 13 communities; Q = 0.762 |
| Trade-oriented | 637 | 591 | 103 | 384 | 0.0029 | 1.86 | 17 communities; Q = 0.786 |

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
