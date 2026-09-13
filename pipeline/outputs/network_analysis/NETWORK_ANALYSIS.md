# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `pipeline/analyze_salt.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 15 | 8 | 7 | 3 | 0.0761904761904762 | 1.0666666666666667 | CONCEPT:6<br>LOCATION:5<br>GROUP:3<br>COMMODITY:1 |
| validated_probable | 15 | 8 | 7 | 3 | 0.0761904761904762 | 1.0666666666666667 | CONCEPT:6<br>LOCATION:5<br>GROUP:3<br>COMMODITY:1 |
| validated_no_concept | 4 | 2 | 2 | 2 | 0.3333333333333333 | 1.0 | GROUP:2<br>LOCATION:2 |
| validated_probable_no_concept | 4 | 2 | 2 | 2 | 0.3333333333333333 | 1.0 | GROUP:2<br>LOCATION:2 |
| validated_trade_only | 10 | 5 | 5 | 2 | 0.1111111111111111 | 1.0 | LOCATION:5<br>CONCEPT:4<br>COMMODITY:1 |
| validated_probable_trade_only | 10 | 5 | 5 | 2 | 0.1111111111111111 | 1.0 | LOCATION:5<br>CONCEPT:4<br>COMMODITY:1 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.0 | 0.0 | 0.0 |
| validated | communities | 1.0 | 1.0 | 1.0 |
| validated_probable | modularity | 0.0 | 0.0 | 0.0 |
| validated_probable | communities | 1.0 | 1.0 | 1.0 |
| validated_no_concept | modularity | 0.0 | 0.0 | 0.0 |
| validated_no_concept | communities | 1.0 | 1.0 | 1.0 |
| validated_probable_no_concept | modularity | 0.0 | 0.0 | 0.0 |
| validated_probable_no_concept | communities | 1.0 | 1.0 | 1.0 |
| validated_trade_only | modularity | 0.0 | 0.0 | 0.0 |
| validated_trade_only | communities | 1.0 | 1.0 | 1.0 |
| validated_probable_trade_only | modularity | 0.0 | 0.0 | 0.0 |
| validated_probable_trade_only | communities | 1.0 | 1.0 | 1.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
