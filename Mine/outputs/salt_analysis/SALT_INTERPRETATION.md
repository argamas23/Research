# Salt Interpretation

This file interprets only salt-specific metrics and evidence.

## Main Claim

Salt is the most structurally central commodity in the validated graph, but the claim should remain commodity-specific rather than network-total.

## Centrality

In the validated graph, salt has degree 44, strength 52.0, betweenness 0.21727716925822377, and PageRank 0.013513438641294088.

In stricter views it remains central: no-CONCEPT degree 33 with betweenness 0.3913041498518692; trade-only degree 35 with betweenness 0.23839239046595082.

## Removal And Null Model

Removing salt leaves the validated graph's largest component with 805 nodes and causes global efficiency loss 0.010121104330435546.

The commodity-label null gives p_ge_salt 0.009900990099009901 for degree and 0.009900990099009901 for removal impact.

Interpretation: salt is unusual among commodity labels, not necessarily stronger than all places or institutions.

## All-Node Baseline

The strongest degree/strength-matched all-node comparison is tibetans (GROUP), with removal efficiency loss 0.017430925379907564.

## Community And Brokerage

Salt's validated Louvain community has median size 79.0, with participation 0.5103305785123968.

The most common shortest-path class through salt is CONCEPT--GROUP, with 17419 pair paths.

Interpretation: salt works best as a brokerage claim: it connects commodity, place, and actor relations inside the extracted graph.

## Evidence Audit

The validated graph has 49 salt edges; 20 are flagged for manual review because of generic entities, missing evidence, or zero confidence.

Interpretation: review the flagged rows before using edge-level examples in prose.

## Source Robustness

Salt remains present after dropping the largest sources. The largest listed betweenness reduction occurs when dropping CentralAsia_Tibet_Vol1, where salt betweenness is 0.21159045017850056.

## Defensible Wording

> Salt is the most structurally central commodity in the validated Himalayan trade knowledge graph, combining high commodity degree, high brokerage, and unusually large removal impact across robustness views.

Avoid: salt is the single backbone of the entire Himalayan economy.

## Editable Notes

<!-- EDITABLE_NOTES_START -->
- Add historical interpretation notes here.
- Add caveats from new sources here.
- Add paper wording decisions here.
<!-- EDITABLE_NOTES_END -->
