# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 706 | 636 | 105 | 457 | 0.0025556024350551505 | 1.801699716713881 | CONCEPT:295<br>LOCATION:158<br>GROUP:132<br>COMMODITY:103<br>PERSON:18 |
| validated_probable | 809 | 725 | 119 | 520 | 0.002218237893010562 | 1.792336217552534 | CONCEPT:325<br>LOCATION:184<br>GROUP:160<br>COMMODITY:120<br>PERSON:20 |
| validated_no_concept | 338 | 263 | 84 | 130 | 0.004617842782645339 | 1.5562130177514792 | LOCATION:127<br>GROUP:112<br>COMMODITY:82<br>PERSON:17 |
| validated_probable_no_concept | 402 | 314 | 97 | 152 | 0.003895733303557028 | 1.5621890547263682 | LOCATION:148<br>GROUP:137<br>COMMODITY:99<br>PERSON:18 |
| validated_trade_only | 422 | 352 | 87 | 211 | 0.003962580630635702 | 1.6682464454976302 | CONCEPT:174<br>COMMODITY:83<br>GROUP:82<br>LOCATION:77<br>PERSON:6 |
| validated_probable_trade_only | 486 | 401 | 102 | 235 | 0.0034024861058079845 | 1.6502057613168724 | CONCEPT:189<br>GROUP:101<br>COMMODITY:99<br>LOCATION:91<br>PERSON:6 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.8399223312594233 | 0.835139119080845 | 0.8417443291717953 |
| validated | communities | 19.0 | 17.0 | 22.0 |
| validated_probable | modularity | 0.8511649602626328 | 0.8470613242640026 | 0.853317154969828 |
| validated_probable | communities | 20.0 | 19.0 | 22.0 |
| validated_no_concept | modularity | 0.7268979430726723 | 0.7197929915354591 | 0.7284768211920529 |
| validated_no_concept | communities | 12.0 | 10.0 | 14.0 |
| validated_probable_no_concept | modularity | 0.7500918841257643 | 0.7429917471348859 | 0.7529152327174313 |
| validated_probable_no_concept | communities | 13.0 | 12.0 | 15.0 |
| validated_trade_only | modularity | 0.7974631028882141 | 0.7972865616834969 | 0.80034955158534 |
| validated_trade_only | communities | 14.0 | 13.0 | 14.0 |
| validated_probable_trade_only | modularity | 0.8120156168055475 | 0.8095390711496999 | 0.8133267292115844 |
| validated_probable_trade_only | communities | 14.0 | 13.0 | 14.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
