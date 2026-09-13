# Salt Interpretation

This file interprets only salt-specific metrics and evidence.

## Main Claim

Salt is the most structurally central commodity in the validated graph, but the claim should remain commodity-specific rather than network-total.

## Centrality

In the validated graph, salt has degree None, strength None, betweenness None, and PageRank None.

In stricter views it remains central: no-CONCEPT degree None with betweenness None; trade-only degree None with betweenness None.

## Removal And Null Model

Removing salt leaves the validated graph's largest component with 3 nodes and causes global efficiency loss 0.0.

The commodity-label null gives p_ge_salt None for degree and None for removal impact.

Interpretation: salt is unusual among commodity labels, not necessarily stronger than all places or institutions.

## All-Node Baseline

The strongest degree/strength-matched all-node comparison is None (None), with removal efficiency loss None.

## Community And Brokerage

Salt's validated Louvain community has median size None, with participation None.

The most common shortest-path class through salt is None, with None pair paths.

Interpretation: salt works best as a brokerage claim: it connects commodity, place, and actor relations inside the extracted graph.

## Evidence Audit

The validated graph has 0 salt edges; 0 are flagged for manual review because of generic entities, missing evidence, or zero confidence.

Interpretation: review the flagged rows before using edge-level examples in prose.

## Source Robustness

Salt remains present after dropping the largest sources. The largest listed betweenness reduction occurs when dropping Commodity, where salt betweenness is 0.

## Defensible Wording

> Salt is the most structurally central commodity in the validated Himalayan trade knowledge graph, combining high commodity degree, high brokerage, and unusually large removal impact across robustness views.

Avoid: salt is the single backbone of the entire Himalayan economy.

## Editable Notes

<!-- EDITABLE_NOTES_START -->
- Add historical interpretation notes here.
- Add caveats from new sources here.
- Add paper wording decisions here.
<!-- EDITABLE_NOTES_END -->
