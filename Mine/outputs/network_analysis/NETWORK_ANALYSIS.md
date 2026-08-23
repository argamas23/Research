# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 1028 | 993 | 132 | 731 | 0.0018811164700934687 | 1.9319066147859922 | CONCEPT:456<br>LOCATION:212<br>GROUP:199<br>COMMODITY:140<br>PERSON:21 |
| validated_probable | 1173 | 1123 | 150 | 827 | 0.0016337444608352319 | 1.9147485080988917 | CONCEPT:497<br>LOCATION:247<br>GROUP:239<br>COMMODITY:167<br>PERSON:23 |
| validated_no_concept | 438 | 347 | 105 | 196 | 0.0036258006541069767 | 1.5844748858447488 | LOCATION:158<br>GROUP:155<br>COMMODITY:107<br>PERSON:18 |
| validated_probable_no_concept | 522 | 414 | 123 | 228 | 0.003044542987623271 | 1.5862068965517242 | GROUP:188<br>LOCATION:188<br>COMMODITY:127<br>PERSON:19 |
| validated_trade_only | 656 | 609 | 105 | 399 | 0.0028346676596536957 | 1.8567073170731707 | CONCEPT:297<br>GROUP:137<br>COMMODITY:112<br>LOCATION:103<br>PERSON:7 |
| validated_probable_trade_only | 753 | 687 | 125 | 443 | 0.002426464355344579 | 1.8247011952191234 | CONCEPT:319<br>GROUP:165<br>COMMODITY:136<br>LOCATION:126<br>PERSON:7 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.8191125383326155 | 0.8171657473757401 | 0.8200864202655652 |
| validated | communities | 24.5 | 22.0 | 27.0 |
| validated_probable | modularity | 0.8307843086214077 | 0.8280216576426489 | 0.8328082049146189 |
| validated_probable | communities | 26.0 | 24.0 | 28.0 |
| validated_no_concept | modularity | 0.756578947368421 | 0.7515774084333641 | 0.7615420129270545 |
| validated_no_concept | communities | 12.0 | 11.0 | 13.0 |
| validated_probable_no_concept | modularity | 0.7778878759853789 | 0.7725958221400155 | 0.7803981151186858 |
| validated_probable_no_concept | communities | 15.0 | 12.0 | 16.0 |
| validated_trade_only | modularity | 0.7888554420904672 | 0.7834467984216498 | 0.7900832359565784 |
| validated_trade_only | communities | 18.0 | 16.0 | 21.0 |
| validated_probable_trade_only | modularity | 0.8004038526768047 | 0.7954449092656453 | 0.8020273899033297 |
| validated_probable_trade_only | communities | 18.0 | 16.0 | 20.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
