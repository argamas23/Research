# Network Interpretation

This file interprets the generated network-analysis outputs. Rerun `make validation-auto` and `make network-analysis` after adding sources. Notes inside the editable block are preserved.

## Main Claim

The current evidence supports a cautious claim: salt is the dominant commodity backbone in the validated graph, not necessarily the single backbone of the entire heterogeneous network.

## What The Validated Graph Shows

The validated graph contains 501 nodes and 420 edges, with 96 connected components. Its largest component has 272 nodes. This means the corpus produces a sparse historical relation graph, not one fully connected trade system.

Interpretation: network claims should focus on brokerage, centrality, and robustness inside the extracted relation structure. Avoid claiming that the whole Himalayan economy is represented as a complete network.

## Salt Centrality

In the validated graph, salt has degree 27, strength 29.0, betweenness 0.46468042458202347, and PageRank 0.02168572156843536. This makes salt the strongest commodity node in the current outputs.

In the no-CONCEPT view, salt still has degree 22 and betweenness 0.5922529830129901. In the trade-only view, salt has degree 21 and betweenness 0.660838779956427.

Interpretation: salt's centrality is not just an artifact of vague concept nodes or governance/context edges. It survives stricter graph representations.

## Removal Results

Removing salt from the validated graph leaves the largest component with 230 nodes and causes global efficiency loss 0.018657567977864137.

Interpretation: salt is structurally important among commodities. Its removal damages connectivity more than removing other named commodities in the generated removal table.

## Null Model Interpretation

The commodity-label permutation null gives p_ge_salt 0.009900990099009901 for degree and 0.009900990099009901 for removal impact.

Interpretation: salt is unusual relative to other commodity labels. This supports a commodity-backbone claim.

Caveat: this does not prove salt is more important than all places, groups, or institutions.

## All-Node Baseline

The strongest degree/strength-matched all-node comparison is tibet (LOCATION), with removal efficiency loss 0.019967217557851136.

Interpretation: if this matched node is stronger than salt, the paper should say salt is the dominant commodity backbone, not the strongest node overall.

## Community Structure

Louvain modularity in the validated graph has median 0.8331213543265646. Salt's community has median size 39.0, and salt participation has median 0.37860082304526743.

Interpretation: the graph has stable community structure, and salt sits in a meaningful community with moderate cross-community participation. This supports brokerage, but not a claim that salt connects every community.

## Source Robustness

The source-drop check shows salt remains present after dropping the largest sources. The largest reduction in salt betweenness among listed drops occurs when dropping TransHimalayan_Traders_Fisher, where salt betweenness is 0.30068946109469535.

Interpretation: salt's role is not created by a single source, but some sources contribute more to the brokerage signal.

## Defensible Wording

Use:

> Salt is the most structurally central commodity in the validated Himalayan trade knowledge graph, combining high commodity degree, high brokerage, and unusually large removal impact across robustness views.

Avoid:

> Salt is the single structural backbone of the entire Himalayan trade network.

## Editable Notes

<!-- EDITABLE_NOTES_START -->
- Add historical interpretation notes here.
- Add caveats from new sources here.
- Add paper wording decisions here.
<!-- EDITABLE_NOTES_END -->
