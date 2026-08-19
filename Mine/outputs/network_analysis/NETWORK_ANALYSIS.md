# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 501 | 420 | 96 | 272 | 0.0033532934131736527 | 1.6766467065868262 | CONCEPT:157<br>LOCATION:128<br>GROUP:117<br>COMMODITY:86<br>PERSON:13 |
| validated_probable | 590 | 496 | 109 | 319 | 0.002854594112399643 | 1.6813559322033897 | CONCEPT:179<br>LOCATION:151<br>GROUP:143<br>COMMODITY:102<br>PERSON:15 |
| validated_no_concept | 293 | 221 | 79 | 108 | 0.005166206928795175 | 1.5085324232081911 | LOCATION:106<br>GROUP:103<br>COMMODITY:72<br>PERSON:12 |
| validated_probable_no_concept | 357 | 272 | 92 | 130 | 0.004280363830925628 | 1.5238095238095237 | GROUP:128<br>LOCATION:127<br>COMMODITY:89<br>PERSON:13 |
| validated_trade_only | 299 | 240 | 68 | 137 | 0.005387084464995174 | 1.605351170568562 | CONCEPT:89<br>COMMODITY:69<br>GROUP:69<br>LOCATION:68<br>PERSON:4 |
| validated_probable_trade_only | 361 | 284 | 86 | 157 | 0.004370575561711296 | 1.5734072022160666 | CONCEPT:101<br>GROUP:90<br>COMMODITY:84<br>LOCATION:82<br>PERSON:4 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.8331213543265646 | 0.8317179071093372 | 0.8331213543265646 |
| validated | communities | 15.0 | 14.0 | 15.0 |
| validated_probable | modularity | 0.8454557998717543 | 0.8448470385792324 | 0.846222839100332 |
| validated_probable | communities | 15.0 | 15.0 | 16.0 |
| validated_no_concept | modularity | 0.728352 | 0.723744 | 0.73376 |
| validated_no_concept | communities | 12.0 | 10.0 | 13.0 |
| validated_probable_no_concept | modularity | 0.7548243787310843 | 0.7493868295617566 | 0.7583414318108196 |
| validated_probable_no_concept | communities | 12.0 | 11.0 | 13.0 |
| validated_trade_only | modularity | 0.776012811634349 | 0.7758613227146814 | 0.7768568213296398 |
| validated_trade_only | communities | 12.0 | 12.0 | 13.0 |
| validated_probable_trade_only | modularity | 0.7963933207138995 | 0.7938750676041104 | 0.7963933207138995 |
| validated_probable_trade_only | communities | 13.0 | 11.0 | 13.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
