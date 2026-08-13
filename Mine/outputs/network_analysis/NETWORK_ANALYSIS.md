# Network Analysis

This file is generated from `Mine/outputs/edge_validation.csv`. Rerun `make validation-auto` and `make network-analysis` after adding sources.

## Graph Views
| view | nodes | edges | components | largest_component_nodes | density | average_degree | node_types |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validated | 501 | 420 | 96 | 272 | 0.0033532934131736527 | 1.6766467065868262 | CONCEPT:157<br>LOCATION:128<br>GROUP:117<br>COMMODITY:86<br>PERSON:13 |
| validated_probable | 590 | 496 | 109 | 319 | 0.002854594112399643 | 1.6813559322033897 | CONCEPT:179<br>LOCATION:151<br>GROUP:143<br>COMMODITY:102<br>PERSON:15 |
| validated_no_concept | 293 | 221 | 79 | 108 | 0.005166206928795175 | 1.5085324232081911 | LOCATION:106<br>GROUP:103<br>COMMODITY:72<br>PERSON:12 |
| validated_probable_no_concept | 357 | 272 | 92 | 130 | 0.004280363830925628 | 1.5238095238095237 | GROUP:128<br>LOCATION:127<br>COMMODITY:89<br>PERSON:13 |
| validated_trade_only | 299 | 240 | 68 | 137 | 0.005387084464995174 | 1.605351170568562 | CONCEPT:89<br>COMMODITY:69<br>GROUP:69<br>LOCATION:68<br>PERSON:4 |
| validated_probable_trade_only | 361 | 284 | 86 | 157 | 0.004370575561711296 | 1.5734072022160666 | CONCEPT:101<br>GROUP:90<br>COMMODITY:84<br>LOCATION:82<br>PERSON:4 |

## Salt Centrality
| view | degree | strength | betweenness_lcc | pagerank | in_lcc |
| --- | --- | --- | --- | --- | --- |
| validated | 27 | 29.0 | 0.46468042458202347 | 0.02168572156843536 | True |
| validated_probable | 27 | 29.0 | 0.46078606432156893 | 0.018528475675603614 | True |
| validated_no_concept | 22 | 24.0 | 0.5922529830129901 | 0.031474346753016386 | True |
| validated_probable_no_concept | 22 | 24.0 | 0.5601582687338501 | 0.025896894055638244 | True |
| validated_trade_only | 21 | 22.0 | 0.660838779956427 | 0.02856453509578701 | True |
| validated_probable_trade_only | 21 | 22.0 | 0.6469120485249518 | 0.02381628477386878 | True |

## Commodity Removal
| view | degree | strength | largest_component_nodes | components | global_efficiency_loss |
| --- | --- | --- | --- | --- | --- |
| validated | 27 | 29.0 | 230 | 116 | 0.018657567977864137 |
| validated_probable | 27 | 29.0 | 271 | 129 | 0.017586496026815814 |
| validated_no_concept | 22 | 24.0 | 72 | 97 | 0.018993236942081246 |
| validated_probable_no_concept | 22 | 24.0 | 90 | 110 | 0.016516538136510283 |
| validated_trade_only | 21 | 22.0 | 114 | 83 | 0.01893592206040956 |
| validated_probable_trade_only | 21 | 22.0 | 133 | 101 | 0.015793786082117556 |

## Commodity-Label Permutation Null
| view | metric | salt_observed | null_median | null_max | p_ge_salt |
| --- | --- | --- | --- | --- | --- |
| validated | degree | 27 | 1.0 | 5.0 | 0.009900990099009901 |
| validated | strength | 29.0 | 1.0 | 5.0 | 0.009900990099009901 |
| validated | betweenness_lcc | 0.46468042458202347 | 0.0 | 0.038622386223862236 | 0.009900990099009901 |
| validated | pagerank | 0.02168572156843536 | 0.0019900053462732297 | 0.0042746062042423065 | 0.009900990099009901 |
| validated | global_efficiency_loss | 0.018657567977864137 | -0.0002121410038754025 | 0.0018730137211597914 | 0.009900990099009901 |
| validated_probable | degree | 27 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_probable | strength | 29.0 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_probable | betweenness_lcc | 0.46078606432156893 | 0.0 | 0.15866780416509604 | 0.009900990099009901 |
| validated_probable | pagerank | 0.018528475675603614 | 0.0016873123943843258 | 0.0032489258998568246 | 0.009900990099009901 |
| validated_probable | global_efficiency_loss | 0.017586496026815814 | -0.0001639587457171708 | 0.002969913299494281 | 0.009900990099009901 |
| validated_no_concept | degree | 22 | 1.0 | 4.0 | 0.009900990099009901 |
| validated_no_concept | strength | 24.0 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_no_concept | betweenness_lcc | 0.5922529830129901 | 0.0 | 0.101686945277141 | 0.009900990099009901 |
| validated_no_concept | pagerank | 0.031474346753016386 | 0.003412969283276451 | 0.006544499747025523 | 0.009900990099009901 |
| validated_no_concept | global_efficiency_loss | 0.018993236942081246 | -0.00021641409040416143 | 0.0026933025744314415 | 0.009900990099009901 |
| validated_probable_no_concept | degree | 22 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_probable_no_concept | strength | 24.0 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_probable_no_concept | betweenness_lcc | 0.5601582687338501 | 0.0 | 0.11809593023255814 | 0.009900990099009901 |
| validated_probable_no_concept | pagerank | 0.025896894055638244 | 0.0025243156194805776 | 0.0060630373393349086 | 0.009900990099009901 |
| validated_probable_no_concept | global_efficiency_loss | 0.016516538136510283 | -0.00016461506347285534 | 0.003489105009774583 | 0.009900990099009901 |
| validated_trade_only | degree | 21 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_trade_only | strength | 22.0 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_trade_only | betweenness_lcc | 0.660838779956427 | 0.0 | 0.25119825708061 | 0.009900990099009901 |
| validated_trade_only | pagerank | 0.02856453509578701 | 0.00334448160535117 | 0.0071194195655356705 | 0.009900990099009901 |
| validated_trade_only | global_efficiency_loss | 0.01893592206040956 | -0.0002569001957173564 | 0.003166700924648949 | 0.009900990099009901 |
| validated_probable_trade_only | degree | 21 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_probable_trade_only | strength | 22.0 | 1.0 | 5.0 | 0.009900990099009901 |
| validated_probable_trade_only | betweenness_lcc | 0.6469120485249518 | 0.0 | 0.27351805900193 | 0.009900990099009901 |
| validated_probable_trade_only | pagerank | 0.02381628477386878 | 0.002770083102493075 | 0.005918436399116861 | 0.009900990099009901 |
| validated_probable_trade_only | global_efficiency_loss | 0.015793786082117556 | -0.00017671669497686116 | 0.003721916524686085 | 0.009900990099009901 |

## Louvain Community Stability
| view | metric | median | min | max |
| --- | --- | --- | --- | --- |
| validated | modularity | 0.8331213543265646 | 0.8317179071093372 | 0.8331213543265646 |
| validated | communities | 15.0 | 14.0 | 15.0 |
| validated | salt_community_size | 39.0 | 39.0 | 39.0 |
| validated | salt_participation | 0.37860082304526743 | 0.37860082304526743 | 0.37860082304526743 |
| validated | salt_community_jaccard_vs_seed0 | 1.0 | 1.0 | 1.0 |
| validated_probable | modularity | 0.8454557998717543 | 0.8448470385792324 | 0.846222839100332 |
| validated_probable | communities | 15.0 | 15.0 | 16.0 |
| validated_probable | salt_community_size | 47.0 | 42.0 | 47.0 |
| validated_probable | salt_participation | 0.37860082304526743 | 0.37860082304526743 | 0.4334705075445817 |
| validated_probable | salt_community_jaccard_vs_seed0 | 1.0 | 0.8936170212765957 | 1.0 |
| validated_no_concept | modularity | 0.731008 | 0.723744 | 0.73376 |
| validated_no_concept | communities | 11.5 | 10.0 | 14.0 |
| validated_no_concept | salt_community_size | 26.5 | 24.0 | 27.0 |
| validated_no_concept | salt_participation | 0.3925619834710744 | 0.3223140495867768 | 0.44628099173553715 |
| validated_no_concept | salt_community_jaccard_vs_seed0 | 0.8888888888888888 | 0.7666666666666667 | 1.0 |
| validated_probable_no_concept | modularity | 0.7548243787310843 | 0.7500809847748623 | 0.7583414318108196 |
| validated_probable_no_concept | communities | 12.0 | 11.0 | 13.0 |
| validated_probable_no_concept | salt_community_size | 26.0 | 26.0 | 30.0 |
| validated_probable_no_concept | salt_participation | 0.5082644628099173 | 0.4545454545454546 | 0.5165289256198348 |
| validated_probable_no_concept | salt_community_jaccard_vs_seed0 | 1.0 | 0.7666666666666667 | 1.0 |
| validated_trade_only | modularity | 0.776012811634349 | 0.776012811634349 | 0.7768568213296398 |
| validated_trade_only | communities | 12.0 | 12.0 | 13.0 |
| validated_trade_only | salt_community_size | 22.0 | 22.0 | 22.0 |
| validated_trade_only | salt_participation | 0.3945578231292518 | 0.3945578231292518 | 0.3945578231292518 |
| validated_trade_only | salt_community_jaccard_vs_seed0 | 1.0 | 1.0 | 1.0 |
| validated_probable_trade_only | modularity | 0.7963933207138995 | 0.7948384261763115 | 0.7963933207138995 |
| validated_probable_trade_only | communities | 13.0 | 11.0 | 13.0 |
| validated_probable_trade_only | salt_community_size | 26.0 | 26.0 | 26.0 |
| validated_probable_trade_only | salt_participation | 0.40362811791383235 | 0.3945578231292518 | 0.40362811791383235 |
| validated_probable_trade_only | salt_community_jaccard_vs_seed0 | 1.0 | 1.0 | 1.0 |

## Source Drop Check
| dropped_source | dropped_source_edges | edges | salt_degree | salt_betweenness_lcc | salt_pagerank |
| --- | --- | --- | --- | --- | --- |
| CentralAsia_Tibet_Vol1 | 79 | 345 | 23 | 0.5516636367479808 | 0.02205804700647256 |
| TransHimalayan_Traders_Fisher | 77 | 344 | 20 | 0.30068946109469535 | 0.020449331945366578 |
| Becoming_India | 49 | 371 | 27 | 0.47694812475017784 | 0.02550438962720058 |
| Ladakh | 46 | 375 | 24 | 0.47073597371438003 | 0.021346638311420342 |
| J&K_Gazatteer_1909 | 45 | 376 | 26 | 0.6274866569626387 | 0.022734253453217664 |
| Memo_Relations_with_Tibet | 34 | 389 | 27 | 0.5310173377643815 | 0.022899468839940727 |
| Santiago_Lazcano | 27 | 394 | 23 | 0.4169960474308298 | 0.019069316501072093 |
| Report_On_Tibet_1903 | 17 | 404 | 27 | 0.49215847650400607 | 0.022267865973339233 |
| Mandi_Gazatteer | 14 | 407 | 27 | 0.4719617395548796 | 0.022405340358119825 |
| Rupshu | 12 | 409 | 23 | 0.3922624570465103 | 0.01918199190213845 |

## Editable Notes

- Add interpretation here.
- Add figure/table decisions here.
- Add reviewer caveats here.
