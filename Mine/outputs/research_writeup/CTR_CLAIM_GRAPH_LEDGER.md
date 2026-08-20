# CTR Report Claim-Graph Ledger

Source checked: `References/CTR Report.pdf`  
Graph checked: `Mine/outputs/cleaned_aggregated_edges.csv` and `Mine/outputs/cleaned_entities.json`  
Last checked: 2026-08-21

Use this as a living ledger. When new books are added, update `Support`, add new edge rows, and move claims from `Missing / weak` to `Partial` or `Strong` only when the graph itself contains matching nodes/edges.

Support scale:

- `Strong`: graph has direct nodes/edges and usable evidence text.
- `Partial`: graph supports the broader idea, but lacks a key term, chronology, or institution.
- `Weak / missing`: graph currently does not support the claim directly.

## Verdict

The graph supports the CTR Report's broad argument that Himalayan salt belonged to an embedded multi-commodity political economy that later intersected with state taxation, licensing, revenue, and administrative control.

The graph does not yet fully support the report's more specific claims about netsang, gamgya, India Salt Act 1882, permit/checkpoint regimes, goba/kotwal authority, or the full "gift into contract into constraint" sequence.

## How the Graph Supports the Theoretical Argument

The graph should be used as evidence for patterns, not as a substitute for the theorists. It does not contain theory as theory. Instead, it contains historical relations that can be interpreted through Polanyi, Scott, Thompson, and related writers on colonial political economy.

### Polanyi: Embedded Economy Versus Formal Market Logic

Polanyi's claim is useful when the graph shows that salt exchange was not isolated from society, ecology, religion, or power. The graph supports this best where commodity edges and political-economy edges overlap.

The strongest Polanyian evidence is the repeated linkage between salt and subsistence commodities: `bhotias --supplies--> salt`, `salt --trades_with--> barley`, `zanskaris --trades_with--> grain with rupshu chang-pa for salt`, and `rupshu nomads --trades_with--> barley, wooden wares and other basic necessities`. These edges show salt moving through provisioning circuits rather than appearing only as a cash commodity.

The graph also supports Polanyi because salt sits inside institutions of authority: `tibetan government --licenses--> rupshu nomads`, `lhagong monastery --governs--> salt`, `government --governs--> the mandi salt mines`, and `punjab salt mines --governs--> inland customs department`. This lets you argue that salt was embedded first in local/regional social and religious authority, and later increasingly in administrative and state authority.

Current limit: the graph does not yet contain explicit nodes for `reciprocity`, `redistribution`, `gift trade`, `substantivism`, or `formalism`. So the Polanyi argument is supported by structure, not by direct theory labels.

### James C. Scott: Moral Economy and Subsistence Security

Scott's argument is strongest when the graph shows communities using trade to secure basic survival rather than maximize profit. The graph supports this through subsistence-oriented edges: `the rupshu people --depends_on--> their cattle, on their sheep and goats`, `grain --supplies--> clothes to wear`, `himalayan farmers --depends_on--> chinu millet`, and `rupshu nomads --trades_with--> barley, wooden wares and other basic necessities`.

These edges help frame salt exchange as a risk-management system. Salt, grain, barley, animals, and basic goods are not luxury market objects in the graph; they are tied to livelihood, seasonal movement, and household survival. That supports Scott's "safety first" reading at the level of economic behavior.

Scott also helps interpret the colonial/state edges as a moral rupture: `kashmir --governs--> land revenue levied`, `state --taxes--> landholders`, `government --licenses--> contractors`, and `british government --taxes--> raja balbir sen`. These show extraction and administrative control, but the graph does not yet prove that this pushed communities below subsistence or caused resistance.

Current limit: the graph lacks direct evidence for `safety first`, `moral economy`, `subsistence threshold`, `smuggling`, `tax evasion`, and everyday resistance. Use Scott for interpretation, but do not claim the graph proves all Scottian mechanisms yet.

### E. P. Thompson: Custom, Dispossession, and Way of Life

Thompson is useful where the graph shows conflict over customary access and the reorganization of rights. The strongest evidence is `kharnak --disputes--> ownership of tso kar`, `assistant commissioner of nyoma --governs--> agreement between kharnak and rupshu`, and `british --disputes--> village sites or farmlands, local pastures or forests`.

The graph also supports a Thompsonian "way of life" reading through livelihood dependence: `rupshu --extracts_from--> salt`, `the rupshu people --depends_on--> their cattle, on their sheep and goats`, and `traders --transports_via--> salt and livestock products`. These do not merely show goods moving; they point to a working social world organized around animals, routes, salt lakes, and customary access.

The administrative counterpoint appears in edges like `government --governs--> all rivers`, where the evidence mentions government property and settlement agreements. That is useful for arguing a move from customary use toward legally defined property and state-mediated rights.

Current limit: the graph does not directly contain `way of life`, `dispossession`, `customary law`, `environmental authority`, `gamgya`, `goba`, or `kotwal`. Thompson is therefore partially supported, especially for contestation and loss of autonomy, but the strongest cultural claims need more sources.

### Parthasarathi / Colonial Political Economy Lens

The current CTR Report PDF does not explicitly name Parthasarathi/Parthasarathy in the extracted text. If you intend to use him or related writers on colonial political economy, the graph can still help, but this should be marked as an added interpretive lens rather than a claim already made in the PDF.

The relevant graph pattern is the movement from regional production and exchange into state-centered fiscal and administrative systems: `british government --governs--> trade`, `british government --governs--> trade between india and tibet`, `government --governs--> the mandi salt mines`, `government of india --governs--> mandi salt sources`, `punjab salt mines --governs--> inland customs department`, and `kashmir --governs--> land revenue levied`.

This can support arguments about colonial restructuring of economic life, fiscal extraction, and administrative control. It does not yet support a detailed Parthasarathi-specific claim unless the future writeup names the exact concept being used.

### Other Writers in the CTR Report

The PDF's main named writers are Polanyi, James C. Scott, and E. P. Thompson. The graph currently supports them at different strengths:

| Writer | What the graph supports well | What remains weak |
|---|---|---|
| Polanyi | Embedded salt exchange across commodities, routes, authority, monasteries, taxation, and licensing. | Explicit reciprocity/redistribution/gift-trade vocabulary. |
| Scott | Subsistence-oriented trade involving salt, grain, barley, animals, clothing, and basic goods. | Direct evidence of moral violation, subsistence crisis, and everyday resistance. |
| Thompson | Contestation over Tso Kar, changing access/property regimes, livelihood-world around salt and animals. | Direct evidence of gamgya, customary law, environmental authority, and dispossession language. |
| Parthasarathi / colonial political economy | State fiscal-administrative control over trade, salt mines, revenue, licensing, and customs. | Exact author-specific concept and direct textual linkage. |

## Claims and Current Graph Support

| Claim from CTR Report | Support | Current graph evidence | What is missing / next evidence needed |
|---|---:|---|---|
| Himalayan salt was not only a commodity for money exchange, but part of subsistence and social reproduction. | Strong | `bhotias --supplies--> salt`; evidence says salt was received in exchange for grain and distributed through upper Garhwal. `salt --trades_with--> barley`. `rupshu nomads --trades_with--> barley, wooden wares and other basic necessities`. | More explicit social-obligation terms would strengthen this. |
| Rupshu / Chang-pa groups extracted salt from high-altitude salt lakes. | Strong | `chang-pa --extracts_from--> salt`; `rupshu --extracts_from--> salt`; `nomads --trades_with--> the salt from tso kar`; `salt mines --extracts_from--> water of salt lakes`. | Add stronger evidence naming Tso Kar extraction procedures if future sources provide it. |
| Salt moved through a multi-commodity circuit involving grain, barley, pashm, wool, apricots, tea, sugar, spices, rice, and livestock products. | Strong | `chang-pa goats --supplies--> pashm`; `farmers from lower ladakh (or sham) --transports_via--> apricots, grain, walnuts, and white radish to trade for salt`; `rupshu --trades_with--> tea, sugar, spices, rice, and other food products at dozum fair`; `traders --transports_via--> salt and livestock products`; `salt --trades_with--> grain-salt-rice circuit`. | Good enough now. Add edge weights/centrality if making a quantitative claim. |
| Salt was exchanged for grain/barley rather than simply sold in a cash market. | Strong | `bhotia traders --trades_with--> tibetan villagers`; evidence says one measure of grain generally brought three of salt. `consumers --trades_with--> grain for salt`. `zanskaris --trades_with--> grain with rupshu chang-pa for salt`. | Add price/cash contrast only if graph has explicit cash-market edges. |
| Polanyi's substantivist "embedded economy" reading fits the graph. | Partial | The graph shows commodity exchange tied to governance, taxation, routes, monasteries, credit, and community actors. Relevant relation families: `trades_with`, `supplies`, `depends_on`, `governs`, `taxes`, `licenses`. | The graph does not contain `Polanyi`, `substantivist`, `embedded economy`, `reciprocity`, or `redistribution` as explicit nodes. |
| Pre-colonial exchange worked through netsang / fictive kinship relations. | Weak / missing | No current graph hits for `netsang`, `fictive`, or `kinship`. | Add source passages and extraction rules/entities for netsang. |
| Exchange was based on trust, obligation, reciprocity, and gift trade rather than legal contract. | Partial | The graph supports barter/exchange through edges around Bhotias, Tarangpurians, Rupshu, salt, grain, and barley. | It lacks explicit `trust`, `obligation`, `reciprocity`, and `gift trade` nodes/edges. |
| Monasteries participated in redistribution and authority around salt. | Partial | `lhagong monastery --governs--> salt`; evidence says Lhagong administered salt trade. `monasteries --supplies--> agricultural advances, chiefly seed-grain`. `tibet --governs--> monasteries`. | Karzok/Thugji salt delivery is not present. Need direct edges for monastery redistribution. |
| Goba/kotwal organized Tso Kar extraction and common-resource allocation. | Weak / missing | No current graph support for `goba`, `kotwal`, `chu lag`, `chu dpon`, lots, or sector allocation. | Add those entities and relations from Rupshu-specific sources. |
| Tibetan salt taxes / tsasho / Yarlung Tsangpo ferry duties shaped redistribution. | Weak / missing | Only irrelevant ferry hits and general tax/governance edges. | Need direct nodes: `tsasho`, `Yarlung Tsangpo`, `salt-tax officials`, ferry duties. |
| British/government rule formalized trade through administration, taxation, settlement, and regulation. | Strong | `british government --governs--> trade`; `british government --governs--> trade between india and tibet`; `british government --taxes--> raja balbir sen`; `government --governs--> all rivers`; `government --licenses--> contractors`; `kashmir --governs--> land revenue levied`. | Add chronology fields if arguing a before/after transformation. |
| Settlement agreements and legal property claims replaced flexible/customary access. | Partial | `government --governs--> all rivers`; evidence says rivers are government property and fishing rights are conveyed by settlement agreements. `british --disputes--> village sites or farmlands, local pastures or forests`. | Need more direct edges comparing customary access with legal settlement. |
| India Salt Act 1882 transformed salt into a government monopoly. | Weak / missing | No current graph hits for `India Salt Act`, `Salt Act`, or `1882`. | Add sources about the Act and extract edges for monopoly, authorized depots, taxation per maund. |
| Inland Customs Line / Inland Customs Department shaped salt administration. | Partial | `punjab salt mines --governs--> inland customs department`; evidence says the Punjab Salt Mines were administered originally by the Inland Customs Department. | No graph edge for the Inland Customs Line as a barrier/checkpoint system. |
| Licensing, quotas, inspection checkpoints, and permits eroded barter routes. | Partial | `government --licenses--> contractors`; `chinese authorities --licenses--> salt`; `tibetan government --licenses--> rupshu nomads`. | `quota`, `checkpoint`, and `permit` are missing. Need direct evidence of erosion/disruption. |
| Mandi salt mines came under government administration/licensing. | Strong | `mandi --controls--> salt mines`; `mandi --governs--> salt quarries`; `government --governs--> the mandi salt mines`; `government of india --governs--> mandi salt sources`. | If the report claims early colonial licensing specifically, add date-specific edges. |
| Scott's moral economy / subsistence ethic fits Rupshu and Changpa livelihoods. | Partial | `the rupshu people --depends_on--> their cattle, on their sheep and goats`; `rupshu nomads --trades_with--> barley, wooden wares and other basic necessities`; `grain --supplies--> clothes to wear`; `himalayan farmers --depends_on--> chinu millet`. | The graph lacks `moral economy`, `safety first`, `subsistence threshold`, and explicit risk-management nodes. |
| Colonial extraction lacked reciprocal obligation and pushed communities below subsistence. | Weak / missing | The graph has taxes/revenue/licensing edges, but not this moral claim directly. | Need evidence for subsistence stress, coercive extraction, or loss of reciprocal obligations. |
| Communities resisted through smuggling, tax evasion, informal networks, and route changes. | Weak / missing | No current graph hits for `smuggling`, `evasion`, or `informal routes`. | Add source passages and relations for resistance practices. |
| Rupshu-Kharnak dispute over Tso Kar access/ownership shows contestation. | Strong | `kharnak --disputes--> ownership of tso kar`; `kharnak --disputes--> rupshu's land from the west`; `assistant commissioner of nyoma --governs--> agreement between kharnak and rupshu`. | Add evidence text where blank fields exist. |
| Gamgya / Shipki oath shows customary law persisting beyond colonial administration. | Weak / missing | No current graph hits for `gamgya` or `shipki`. | Add direct source and extraction rules. |
| 1950 Tibet annexation and 1962-1968 border closure disrupted older trade routes. | Weak / missing | Some border/China edges exist, but no direct support for annexation or 1962-1968 closure. | Add date-specific nodes/edges for Tibet annexation, border closure, and route disruption. |
| Thompson's "way of life" / dispossession argument applies to loss of autonomy, custom, and environmental authority. | Partial | Graph has commons/governance hints: `government --governs--> all rivers`, `kharnak --disputes--> ownership of tso kar`, `rupshu --extracts_from--> salt`, `the rupshu people --depends_on--> their cattle, on their sheep and goats`. | The graph lacks `way of life`, `dispossession`, `environmental authority`, and direct loss-of-autonomy edges. |
| Leh worked as an intermediate market linking regional circuits. | Strong | `india --trades_with--> chinese turkistan and tibet`; evidence says via Leh through Kashmir. `kashmir --trades_with--> central asia`; evidence says trade via Leh. `more enterprising men --transports_via--> their salt onward to leh`. | Add more Leh commodity-specific links if making Leh centrality claims. |
| Shipki worked as a gateway to lower Himalayan regions. | Weak / missing | No current graph hit for `Shipki`. | Add Shipki/Spiti route sources. |
| Final thesis: gift into contract, contract into constraint. | Partial | Broadly supported by barter/exchange plus government/tax/license/settlement edges. | Not explicit enough yet. Needs theme nodes or direct evidence for `gift`, `contract`, `constraint`, `permit system`, and chronology. |

## High-Value Existing Edges

These are the strongest current graph rows to cite in discussion.

| Row | Edge | Why it matters |
|---:|---|---|
| 34 | `bhotia traders --trades_with--> tibetan villagers` | Direct grain-for-salt ratio before fuller Chinese authority. |
| 36 | `bhotias --supplies--> salt` | Salt received in exchange for grain and distributed through upper Garhwal. |
| 79 | `chang-pa --extracts_from--> salt` | Direct Chang-pa salt extraction. |
| 81 | `chang-pa goats --supplies--> pashm, or 'cashmere` | Links salt world to pashm/luxury-fiber circuit. |
| 159 | `farmers from lower ladakh (or sham) --transports_via--> apricots, grain, walnuts, and white radish to trade for salt` | Strong multi-commodity support. |
| 184 | `government --governs--> all rivers` | Shows formal property/settlement logic. |
| 194 | `government --licenses--> contractors` | Good evidence for contractual/administrative economy. |
| 283 | `kashmir --governs--> land revenue levied` | Revenue-state evidence. |
| 307 | `kharnak --disputes--> ownership of tso kar` | Direct contestation over salt resource. |
| 381 | `mandi --controls--> salt mines` | Administrative control over salt mines. |
| 468 | `punjab salt mines --governs--> inland customs department` | Salt administration and customs connection. |
| 489 | `rupshu --extracts_from--> salt` | Direct Rupshu salt extraction. |
| 492 | `rupshu --trades_with--> tea, sugar, spices, rice, and other food products at dozum fair` | Multi-commodity circuit. |
| 494 | `rupshu nomads --trades_with--> barley, wooden wares and other basic necessities` | Subsistence exchange. |
| 506 | `salt --trades_with--> barley` | Simple salt/barley barter support. |
| 507 | `salt --trades_with--> grain-salt-rice circuit` | Names the circuit directly. |
| 700 | `tibetan government --licenses--> rupshu nomads` | Licensing/permission around salt access. |
| 815 | `zanskaris --trades_with--> grain with rupshu chang-pa for salt` | Strong support for Rupshu-Zanskar exchange. |

## Missing Terms to Watch For

When adding books, search for and preserve these as entities or evidence phrases:

- `netsang`
- `gamgya`
- `Shipki`
- `goba`
- `kotwal`
- `chu lag`
- `chu dpon`
- `tsasho`
- `Yarlung Tsangpo`
- `India Salt Act`
- `1882`
- `Inland Customs Line`
- `permit`
- `quota`
- `checkpoint`
- `smuggling`
- `tax evasion`
- `reciprocity`
- `redistribution`
- `gift trade`
- `moral economy`
- `subsistence`
- `dispossession`
- `customary law`

## Update Template

Copy this row when a new source adds evidence:

| New claim or existing claim | Strong / Partial / Weak | `source --relation--> target`; row number if stable; short evidence phrase | What still needs checking |
