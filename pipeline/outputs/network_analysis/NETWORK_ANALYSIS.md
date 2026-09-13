# Network Analysis

This file contains general graph metrics only. Salt-specific analysis is generated separately by `Mine/salt_analysis.py`.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 1171 | 1184 | 141 | 836 | 0.0017283788419569803 | 2.022203245089667 | CONCEPT:487<br>LOCATION:258<br>GROUP:239<br>COMMODITY:146<br>PERSON:41 |
| validated_probable | 1322 | 1319 | 163 | 928 | 0.0015105688282269082 | 1.9954614220877458 | CONCEPT:523<br>LOCATION:300<br>GROUP:283<br>COMMODITY:171<br>PERSON:45 |
| validated_no_concept | 541 | 500 | 105 | 279 | 0.0034230163620182106 | 1.8484288354898337 | LOCATION:200<br>GROUP:194<br>COMMODITY:113<br>PERSON:34 |
| validated_probable_no_concept | 633 | 577 | 123 | 318 | 0.0028845961565380847 | 1.8230647709320695 | LOCATION:236<br>GROUP:229<br>COMMODITY:131<br>PERSON:37 |
| validated_trade_only | 805 | 799 | 108 | 543 | 0.002469021352863014 | 1.9850931677018633 | CONCEPT:349<br>GROUP:162<br>LOCATION:159<br>COMMODITY:122<br>PERSON:13 |
| validated_probable_trade_only | 909 | 884 | 131 | 589 | 0.002142064426706988 | 1.944994499449945 | CONCEPT:368<br>LOCATION:191<br>GROUP:190<br>COMMODITY:145<br>PERSON:15 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.7986386651498458 | 0.7954569661731629 | 0.7998002235848947 |
| validated | communities | 22.0 | 20.0 | 25.0 |
| validated_probable | modularity | 0.809716554657694 | 0.8074463594846693 | 0.8118838387906013 |
| validated_probable | communities | 24.0 | 21.0 | 27.0 |
| validated_no_concept | modularity | 0.7120316620774334 | 0.7061050123146446 | 0.7166106029453433 |
| validated_no_concept | communities | 14.0 | 12.0 | 15.0 |
| validated_probable_no_concept | modularity | 0.7291404065217009 | 0.7247712069602331 | 0.7325803633720078 |
| validated_probable_no_concept | communities | 15.0 | 13.0 | 16.0 |
| validated_trade_only | modularity | 0.7857485428739572 | 0.7773722933477981 | 0.7911833141004564 |
| validated_trade_only | communities | 17.0 | 16.0 | 19.0 |
| validated_probable_trade_only | modularity | 0.7961222491844726 | 0.7902369206849703 | 0.7997744131472454 |
| validated_probable_trade_only | communities | 18.5 | 17.0 | 20.0 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
