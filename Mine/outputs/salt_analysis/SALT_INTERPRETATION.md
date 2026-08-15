# Salt Interpretation

This file interprets only salt-specific metrics and evidence.

## Main Claim

Salt is the most structurally central commodity in the validated graph, but the claim should remain commodity-specific rather than network-total.

## Centrality

In the validated graph, salt has degree 27, strength 29.0, betweenness 0.46468042458202347, and PageRank 0.02168572156843536.

In stricter views it remains central: no-CONCEPT degree 22 with betweenness 0.59225298301299; trade-only degree 21 with betweenness 0.6608387799564269.

## Removal And Null Model

Removing salt leaves the validated graph's largest component with 230 nodes and causes global efficiency loss 0.018657567977864137.

The commodity-label null gives p_ge_salt 0.009900990099009901 for degree and 0.009900990099009901 for removal impact.

Interpretation: salt is unusual among commodity labels, not necessarily stronger than all places or institutions.

## All-Node Baseline

The strongest degree/strength-matched all-node comparison is tibet (LOCATION), with removal efficiency loss 0.019967217557851136.

## Community And Brokerage

Salt's validated Louvain community has median size 39.0, with participation 0.37860082304526743.

The most common shortest-path class through salt is CONCEPT--CONCEPT, with 3185 pair paths.

Interpretation: salt works best as a brokerage claim: it connects commodity, place, and actor relations inside the extracted graph.

## Evidence Audit

The validated graph has 28 salt edges; 16 are flagged for manual review because of generic entities, missing evidence, or zero confidence.

Interpretation: review the flagged rows before using edge-level examples in prose.

## Source Robustness

Salt remains present after dropping the largest sources. The largest listed betweenness reduction occurs when dropping TransHimalayan_Traders_Fisher, where salt betweenness is 0.30068946109469535.

## Defensible Wording

> Salt is the most structurally central commodity in the validated Himalayan trade knowledge graph, combining high commodity degree, high brokerage, and unusually large removal impact across robustness views.

Avoid: salt is the single backbone of the entire Himalayan economy.

## Editable Notes

<!-- EDITABLE_NOTES_START -->
- Add historical interpretation notes here.
- Add caveats from new sources here.
- Add paper wording decisions here.
<!-- EDITABLE_NOTES_END -->
