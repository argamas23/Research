# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 999 | 958 | 135 | 692 | 0.001921761440799517 | 1.917917917917918 | CONCEPT:374<br>GROUP:231<br>LOCATION:203<br>COMMODITY:150<br>PERSON:41 |
| validated_probable | 1146 | 1086 | 157 | 780 | 0.0016552733258647888 | 1.8952879581151831 | CONCEPT:408<br>GROUP:276<br>LOCATION:237<br>COMMODITY:180<br>PERSON:45 |
| validated_no_concept | 509 | 422 | 112 | 229 | 0.003264081184350974 | 1.6581532416502947 | GROUP:189<br>LOCATION:168<br>COMMODITY:118<br>PERSON:34 |
| validated_probable_no_concept | 602 | 497 | 131 | 265 | 0.0027473590527415546 | 1.6511627906976745 | GROUP:225<br>LOCATION:199<br>COMMODITY:141<br>PERSON:37 |
| validated_trade_only | 637 | 591 | 103 | 384 | 0.0029175676075945617 | 1.8555729984301412 | CONCEPT:239<br>GROUP:155<br>COMMODITY:125<br>LOCATION:106<br>PERSON:12 |
| validated_probable_trade_only | 735 | 669 | 124 | 426 | 0.0024801201134404716 | 1.8204081632653062 | CONCEPT:254<br>GROUP:184<br>COMMODITY:153<br>LOCATION:130<br>PERSON:14 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.814725877586145 | 0.8124737351644018 | 0.8161554734841694 |
| validated | communities | 22.0 | 19.0 | 24.0 |
| validated_probable | modularity | 0.8263115541440094 | 0.8251363492580306 | 0.8275400589311516 |
| validated_probable | communities | 24.0 | 23.0 | 25.0 |
| validated_no_concept | modularity | 0.7619552876297577 | 0.7559810229238754 | 0.7634826448961938 |
| validated_no_concept | communities | 13.0 | 13.0 | 13.0 |
| validated_probable_no_concept | modularity | 0.7798881452854495 | 0.7743320660654999 | 0.7812496727097538 |
| validated_probable_no_concept | communities | 14.0 | 13.0 | 16.0 |
| validated_trade_only | modularity | 0.7859687641466727 | 0.7801856043458578 | 0.7872883657763694 |
| validated_trade_only | communities | 17.0 | 16.0 | 20.0 |
| validated_probable_trade_only | modularity | 0.797161955517873 | 0.7925101061333253 | 0.7986513800360339 |
| validated_probable_trade_only | communities | 18.0 | 15.0 | 20.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
