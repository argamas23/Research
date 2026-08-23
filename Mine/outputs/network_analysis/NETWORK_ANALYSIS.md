# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 1056 | 1009 | 144 | 731 | 0.0018113600459572024 | 1.9109848484848484 | CONCEPT:402<br>GROUP:238<br>LOCATION:220<br>COMMODITY:154<br>PERSON:42 |
| validated_probable | 1213 | 1146 | 167 | 827 | 0.0015590182266371731 | 1.8895300906842538 | CONCEPT:441<br>GROUP:284<br>LOCATION:255<br>COMMODITY:187<br>PERSON:46 |
| validated_no_concept | 525 | 434 | 116 | 233 | 0.0031552162849872775 | 1.6533333333333333 | GROUP:194<br>LOCATION:176<br>COMMODITY:120<br>PERSON:35 |
| validated_probable_no_concept | 622 | 512 | 136 | 271 | 0.00265105032335565 | 1.6463022508038585 | GROUP:230<br>LOCATION:209<br>COMMODITY:145<br>PERSON:38 |
| validated_trade_only | 663 | 613 | 108 | 399 | 0.002793308817833431 | 1.8491704374057316 | CONCEPT:253<br>GROUP:158<br>COMMODITY:129<br>LOCATION:111<br>PERSON:12 |
| validated_probable_trade_only | 767 | 695 | 131 | 443 | 0.002365868852570627 | 1.8122555410691004 | CONCEPT:269<br>GROUP:187<br>COMMODITY:160<br>LOCATION:137<br>PERSON:14 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.8191125383326155 | 0.8171657473757401 | 0.8200864202655652 |
| validated | communities | 24.5 | 22.0 | 27.0 |
| validated_probable | modularity | 0.8307843086214077 | 0.8280216576426489 | 0.8328082049146189 |
| validated_probable | communities | 26.0 | 24.0 | 28.0 |
| validated_no_concept | modularity | 0.7635672652804033 | 0.7577649128334384 | 0.7660089792060492 |
| validated_no_concept | communities | 13.0 | 13.0 | 13.0 |
| validated_probable_no_concept | modularity | 0.7841672965482489 | 0.7785840262030739 | 0.7846258503401361 |
| validated_probable_no_concept | communities | 14.0 | 13.0 | 15.0 |
| validated_trade_only | modularity | 0.7888554420904672 | 0.7834467984216498 | 0.7900832359565784 |
| validated_trade_only | communities | 18.0 | 16.0 | 21.0 |
| validated_probable_trade_only | modularity | 0.8004038526768047 | 0.7954449092656453 | 0.8020273899033297 |
| validated_probable_trade_only | communities | 18.0 | 16.0 | 20.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
