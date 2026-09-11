# Himalayan Salt as Political Infrastructure: A Computational Historical Network Study of Commodity Circulation and Frontier Governance

## 1. Abstract

Salt has been a pillar of Himalayan and Tibetan life, sustaining economies, shaping rituals, supporting multi-commodity networks, and serving as an exchange token among nomads (Ahmed, 1999; Fisher, 1986; Rizvi, 1996, 1999). This proposed thesis examines the politics of the Himalayan salt economy by asking how salt negotiated power, territorial control, pastoral mobility, taxation, and commercial exchange across the Western Himalayas and adjoining Tibetan regions (Alam, 2007; Bergmann, 2016; Marshall, 2004). Rather than treating salt as only a tradable object, the thesis conceptualises it as a keystone commodity and an infrastructure of governance (Field, 1959).

The study will use historical archives, colonial gazetteers, administrative reports, travel accounts, treaties, and ethnographic sources to build a source-based computational representation of Himalayan salt relations (Aggarwal, 1956; Government of Punjab, 1918; Thomson, 1852; Walton, 1910). Named Entity Recognition, co-occurrence analysis, relation extraction, manual validation, and network analysis will be used to construct a knowledge graph linking salt with commodities, communities, routes, places, and administrative institutions (Ehrmann et al., 2023; Graham et al., 2015; Painter et al., 2019).

Preliminary work indicates that salt emerges as a structural connector rather than merely as a commodity. Its position remains stable after validation and trade-oriented filtering, suggesting that salt bridged subsistence exchange, administrative control, and multi-commodity circulation. Network measures such as degree, weighted degree, betweenness centrality, Louvain community detection, and node-removal analysis provide evidence that salt functioned as a broker entity in the corpus-derived graph (Blondel et al., 2008; Freeman, 1977; Newman, 2010).

The thesis will argue that salt circulation was not merely commerce, but an infrastructure of control, contestation, sovereignty, dependency, and reordering along the Himalayan frontier. British regulation through monopoly, taxation, contracts, measurement, and surveillance transformed long-standing mobility and exchange systems into more bureaucratic and imperial circuits of extraction (Aggarwal, 1956; Alam, 2007; Emerson, 1920; Foreign Department, Political Branch-A, 1874). The computational graph will be treated as a source-based representation of recoverable historical relations, not as a complete reconstruction of Himalayan trade (Painter et al., 2019; Wetherell, 1998).

## 2. Introduction

The Himalayan frontier, especially Ladakh and Tibet, has long been a zone of political contestation involving the Namgyal Dynasty, the Dogras, the British administration, the Ganden Phodrang government, and the Chinese state (Bergmann, 2016; Marshall, 2004). Yet goods such as salt, pashm, tea, wool, grain, barley, borax, apricots, and spices moved through the region with relative ease and persistence (Rizvi, 1995, 1996, 1999). These goods acted as strategic connectors between local economies and imperial governance, enabling both economic sustenance and political negotiation (Alam, 2007).

This thesis focuses on salt because Himalayan salt was not simply one commodity among many. Salt from the Changthang lakes supported pastoral communities such as the Rupshu, Drokpas, Changpas, Jada, and Khompas, who exchanged it for grain, barley, apricots, and other low-altitude commodities (Ahmed, 1999; Dollfus, 2013; Rizvi, 1999). Before colonial interventions intensified questions of access, taxation, territorial jurisdiction, monopoly, and administrative control, salt circulated through reciprocal circuits. Successive bartering was tied to climatic conditions, seasonal calendars, regulated trade routes, and social relationships such as netsang, or fictive trade kinship (Fisher, 1986; Rizvi, 1996).

The main research problem is that Himalayan salt has often been described as important, but its relational and political structure has not been systematically tested across a broader corpus of historical sources. The proposed thesis asks whether salt held a connective structural position within the commodity layer of Himalayan commerce and whether its circulation helped organise relations among communities, routes, markets, monasteries, treaties, and states. The thesis therefore studies salt both as a commodity and as a political infrastructure through which Himalayan relations were arranged.

The problem has wider applications for historical research, digital humanities, and political economy. Historical sources related to Himalayan trade contain extensive information on commodities, communities, routes, and political institutions, but such knowledge is embedded primarily in narrative prose rather than structured representation. A computational knowledge graph can complement close reading by translating evidence spread across textual sources into a relational representation (Graham et al., 2015; Painter et al., 2019). This makes it possible to examine associations between human and non-human actors without assuming that historical agency belongs exclusively to individuals or institutions (Latour, 2005).

The central thesis question is: Did salt function as a structural backbone of Himalayan multi-commodity exchange and frontier governance in the corpus-derived historical network? Supporting questions include: How did salt connect pastoral communities, agricultural valleys, markets, monasteries, and political authorities? How did embedded forms of reciprocity coexist with, or transform into, colonial systems of taxation, monopoly, licensing, and surveillance? What can network measures reveal about salt's brokerage role, and where must those measures be checked through source criticism?

## 3. Related Work

The proposed thesis is situated at the intersection of Himalayan history, economic anthropology, frontier studies, and computational historical network analysis. Historical scholarship on Ladakh, Tibet, and the Western Himalayas has shown that the region was shaped by overlapping sovereignties, mobile pastoralism, seasonal trade, customary authority, and imperial administration (Alam, 2007; Bergmann, 2016; Marshall, 2004). Rizvi's work on Ladakh and trans-Himalayan caravans highlights the role of merchant networks, routes, and exchange relations (Rizvi, 1995, 1996, 1999). Ahmed's study of Rupshu's annual trek to Tso Kar provides a detailed account of salt extraction, pastoral labour, kinship, and exchange (Ahmed, 1999). Fisher and von Furer-Haimendorf show how Himalayan traders operated through long-distance barter systems, risk-sharing, and regional interdependence (Fisher, 1986; von Furer-Haimendorf, 1975).

Anthropological theory provides an important framework for interpreting these exchanges. Mauss's theory of gift and obligation helps explain why Himalayan barter cannot be reduced to price calculation alone (Mauss, 2001). Polanyi's idea of the embedded economy is especially useful because the sources do not show a strict division between market and non-market activities (Polanyi, 1957). At Tso Kar, salt extraction followed annual pastoral cycles; harvesting was organised through male work teams known as chu lag, led by chu dpon, tied to pha shun or patri-fraternal groups, and supervised through local figures such as the kotwal and goba (Ahmed, 1999). Scott's work on subsistence ethics foregrounds risk avoidance, food security, and household survival, while his later work on state legibility helps explain how colonial administration transformed salt into something priced, measured, taxed, recorded, and controlled (Scott, 1976, 1999).

Frontier and political history also frame the research gap. The Treaty of Tingmosgang regulated commercial privileges between Ladakh and Tibet, including trade access and obligations (Rizvi, 1996; Treaty of Tingmosgang, 1684). Later administrative sources on Mandi salt mines show specialised departments, inspectors, mine officials, weighing personnel, attendance registers, fixed prices, duties, revenue sharing, and British sanctions (Emerson, 1920; Foreign Department, Political Branch-A, 1874). These examples suggest that political regulation did not begin with colonialism; rather, colonial rule altered the institutional form of operation, shifting from royal privileges, customary authority, patronage, monasteries, and reciprocal obligations toward standardised bureaucratic contracts (Alam, 2007).

Digital humanities and historical network analysis offer the methodological foundation. Named Entity Recognition, relation extraction, and network reconstruction have been used to extract people, places, organisations, and relationships from large-scale textual collections (Ehrmann et al., 2023; Graham et al., 2015; Painter et al., 2019). Projects such as Six Degrees of Francis Bacon and Beyond 2022 combine computational inference with human validation, demonstrating that computational extraction can support historical assessment without replacing source criticism (Beyond 2022 Project, n.d.; Warren et al., 2016). Historical network scholars also warn that partial information, uneven documentation, and source survivability shape the resulting graph (Wetherell, 1998).

The research gap is therefore twofold. First, existing Himalayan trade scholarship provides rich qualitative evidence, but does not systematically test salt's connective position across a broader source corpus using network metrics. Second, computational network studies often demonstrate method but risk treating extracted relations as historical reality unless they are grounded in close reading and validation. This thesis addresses both gaps by combining automated extraction, human-guided filtering, manual validation, and historically contextual interpretation.

## 4. Proposed Work

The objective of the proposed thesis is to investigate whether Himalayan salt functioned as a keystone commodity and political infrastructure in the Western Himalayas and adjoining Tibetan regions (Field, 1959; Rizvi, 1999). The thesis will reconstruct a source-based knowledge graph from historical and ethnographic texts and analyse whether salt occupies a distinctive structural position among commodities, communities, routes, markets, and institutions (Graham et al., 2015; Painter et al., 2019).

The first objective is corpus preparation. The corpus will comprise historical sources concerning salt, commodity circulation, trade routes, political relations, Western Himalayan frontier administration, pastoral production, and Tibetan-Himalayan exchange. It will include gazetteers, administrative reports, travelogues, treaties, and ethnographic accounts from the nineteenth and twentieth centuries (Aggarwal, 1956; Government of Punjab, 1918; Thomson, 1852; Walton, 1910). Sources will be converted into machine-readable text using PyMuPDF, with OCR fallback for image-based pages where required. Preprocessing will be kept minimal to preserve historical names, variant spellings, and regional terminology.

The second objective is entity identification and topic filtering. The study will use Named Entity Recognition and topic detection to identify people, places, commodities, communities, organisations, jurisdictions, and concepts. Since automated topic identification can produce many unrelated semantic categories, a human-in-the-loop filtering stage will reduce these to research-selected categories covering geographical features, commodities, jurisdictions, organisations, transport, trade, economy, governance, and pastoral communities. Entity confidence and relevance scores will help distinguish core trade-related entities from peripheral mentions.

The third objective is relation extraction. The thesis will identify relations in Subject-Relation-Object form, such as "Rupshu nomads - extract salt from - Tso Kar" (Ahmed, 1999), "Mandi State - imposes tax on - salt caravans" (Foreign Department, Political Branch-A, 1874), and "Ladakh royal trader - permitted entry to - Rudok" (Rizvi, 1996; Treaty of Tingmosgang, 1684). A symmetric co-occurrence window of approximately 50 words around anchor entities such as salt, wool, Rupshu, Changthang, Tso Kar, grain, and pashm will identify possible relational segments. A local Llama 3 model through Ollama will be used for relation extraction, limited to semantic categories such as trades_with, exchanges_for, extracts_from, transports_via, taxes, controls, governs, licenses, supplies, depends_on, and migrates_through.

The fourth objective is graph refinement and validation. Extracted relations will be consolidated into directed triples, with duplicate triples merged and their frequency recorded as edge weight. The graph will be refined by correcting spelling variants, duplicate names, label inconsistencies, and entity-type errors. Interactive graph visualisation will support the detection of isolated instances, impossible relationships, duplicate entities, and category conflicts. Validation will classify relations as Validated, Probable, or Missing/Unsupported according to source evidence. This stage is essential because relation extraction can misidentify ambiguous historical relations, and proximity-based methods may miss relations that span longer passages.

The fifth objective is network analysis. Validated triples will be combined into a weighted network in which entities are nodes and labelled relations are edges. The network will be analysed through degree, weighted degree, betweenness centrality, PageRank, Louvain community detection, participation coefficient, robustness checks, permutation tests, and node-removal analysis. Degree and weighted degree will measure breadth and recurrence of connections. Betweenness centrality will indicate brokerage (Freeman, 1977; Newman, 2010). Louvain community detection will identify relational clusters (Blondel et al., 2008). Node-removal analysis will test whether removing salt increases fragmentation or lowers network efficiency.

Preliminary results already provide evidence of feasibility. Relation extraction generated 1,475 edges, of which 1,227 were validated against source documents, while 138 were classified as probable and 110 as missing or unsupported. The aggregated graph contained 1,171 nodes and 973 distinct edges with 141 connected components. In the validated graph, salt emerged as the most prominent commodity-labelled node, with high degree, weighted strength, betweenness centrality, and PageRank. Salt's observed degree, strength, betweenness, PageRank, and removal effect exceeded commodity-label permutation distributions with p = 0.0099. Removing the salt node increased the number of connected components and lowered global efficiency, suggesting that salt functioned as a broker entity binding the network better than any other commodity node.

The thesis will also include a focused Rupshu-Tso Kar case study. The Rupshu-Tso Kar region offers a concrete setting for examining how the computational network aligns with historically documented exchange relations. Historical sources identify Tso Kar as an important salt-production site embedded in pastoral mobility and multi-commodity exchange, where salt, wool, and pashm were traded for barley, grain, and other necessities (Ahmed, 1999; Dollfus, 2013; Rizvi, 1996, 1999; Thomson, 1852). The case study will examine extraction, seasonal labour, mobility, local authority through goba and kotwal, exchange with adjacent areas, and disputes over lake resources (Ahmed, 1999; Dollfus, 2013).

The expected challenge is not only technical but interpretive. The reconstructed network is conditioned by corpus composition, source survivability, colonial documentation practices, OCR quality, NER limitations, and the interpretive choices built into human-guided filtering (Ehrmann et al., 2023; Painter et al., 2019; Wetherell, 1998). The thesis will therefore avoid claiming that the graph is an exhaustive representation of Himalayan trade. Network metrics will be treated as characteristics of the computational representation of source material, not as direct indicators of historical economic reality. The final interpretation will combine network evidence with close reading.

Expected outputs include a cleaned corpus, an entity and relation dataset, a validated knowledge graph, network visualisations, centrality and robustness tables, a Rupshu-Tso Kar case study, and a thesis explaining how salt linked ecological zones, commodities, communities, institutions, and mechanisms of control. The thesis will argue that salt's importance lies not only in its prevalence but in its ability to connect subsistence exchange, pastoral mobility, administrative control, and multi-commodity circulation.

## 5. Timeline and Milestones

| Period | Milestone | Output |
|---|---|---|
| June 2025 | Began corpus search and tool exploration | Resource list and NER tool notes |
| July 2025 | Developed early computational workflow | Topic filters and LLM workflow notes |
| August-September 2025 | Built historical and theoretical foundation | Bibliography and source classification |
| October 2025 | Drafted conference abstract | Revised abstract and paper skeleton |
| November-December 2025 | Organised project and early paper structure | Git repository and early drafts |
| January-February 2026 | Strengthened theory and relation extraction | Theory notes, relational CSV, poster draft |
| March-May 2026 | Presented and extended literature base | RnD poster, one-pager, CTR report |
| June-July 2026 | Built knowledge graph and thesis roadmap | Knowledge graph and chapter plan |
| August-September 2026 | Completed publication draft and chapter groundwork | iConference draft and revisions |
| October 2026 | Finalise computational pipeline | Frozen method and Chapter 3 draft |
| November 2026 | Build and analyse final knowledge graph | Network statistics and visualisations |
| December 2026 | Complete historical interpretation | Chapter 4 draft |
| January 2027 | Thesis integration and submission-ready draft | Final thesis draft |

## 6. References

Aggarwal, S. C. (1956). *The salt industry in India* (2nd ed.). Manager of Publications, Government of India. https://archive.org/details/in.ernet.dli.2015.276075

Ahmed, M. (1999). The salt trade: Rupshu's annual trek to Tso Kar. In M. van Beek, K. B. Bertelsen, & P. Pedersen (Eds.), *Ladakh: Culture, history, and development between Himalaya and Karakoram* (pp. 32-48). Aarhus University Press. https://ladakhstudies.org/ladakh-culture-history-and-development-between-himalaya-and-karakoram/

Alam, A. (2007). *Becoming India: Western Himalayas under British rule*. Foundation Books. https://doi.org/10.1017/UPO9788175968387

Bergmann, C. (2016). Confluent territories and overlapping sovereignties: Britain's nineteenth-century Indian empire in the Kumaon Himalaya. *Journal of Historical Geography, 51*, 88-98. https://doi.org/10.1016/j.jhg.2015.06.015

Beyond 2022 Project. (n.d.). *Beyond 2022: Ireland's virtual record treasury*. https://beyond2022.ie

Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment, 2008*(10), Article P10008. https://doi.org/10.1088/1742-5468/2008/10/P10008

Dollfus, P. (2013). Transformation processes in nomadic pastoralism in Ladakh. *Himalaya, 32*(1), 61-72. https://digitalcommons.macalester.edu/himalaya/vol32/iss1/15/

Ehrmann, M., Hamdi, A., Pontes, E. L., Romanello, M., & Doucet, A. (2023). Named entity recognition and classification in historical documents: A survey. *ACM Computing Surveys, 56*(2), Article 58. https://doi.org/10.1145/3604931

Emerson, H. W. (1920). *Gazetteer of the Mandi State* (Vol. 12A). Superintendent, Government Printing, Punjab. https://archive.org/details/in.gov.ignca.30735

Field, A. (1959). Himalayan salt: A political barometer. *Modern Review, 105*(6), 460-463.

Fisher, J. F. (1986). *Trans-Himalayan traders: Economy, society, and culture in Northwest Nepal*. University of California Press. https://archive.org/details/transhimalayantr0000fish

Foreign Department, Political Branch-A. (1874, November). *Mandi salt mines*. National Archives of India.

Freeman, L. C. (1977). A set of measures of centrality based on betweenness. *Sociometry, 40*(1), 35-41. https://doi.org/10.2307/3033543

Government of Punjab. (1918). *Punjab district gazetteers: Kangra District, 1917--Parts II-IV: Kulu and Saraj, Lahul, and Spiti* (Vol. 30A). Superintendent, Government Printing, Punjab. https://archive.org/details/dli.csl.2896

Graham, S., Milligan, I., & Weingart, S. (2015). *Exploring big historical data: The historian's macroscope*. Imperial College Press. https://doi.org/10.1142/p981

Latour, B. (2005). *Reassembling the social: An introduction to actor-network-theory*. Oxford University Press. https://global.oup.com/academic/product/reassembling-the-social-9780199256051

Marshall, J. G. (Ed.). (2004). *Britain and Tibet, 1765-1947: A select annotated bibliography of British relations with Tibet and the Himalayan states including Nepal, Sikkim and Bhutan: Revised and updated to 2003*. Routledge. https://doi.org/10.4324/9780203009086

Mauss, M. (2001). *The gift: The form and reason for exchange in archaic societies* (W. D. Halls, Trans.; 2nd ed.). Routledge. (Original work published 1925) https://www.routledge.com/The-Gift/Mauss/p/book/9780415267496

Newman, M. E. J. (2010). *Networks: An introduction*. Oxford University Press. https://doi.org/10.1093/acprof:oso/9780199206650.001.0001

Painter, D. T., Daniels, B. C., & Jost, J. (2019). Network analysis for the digital humanities: Principles, problems, extensions. *Isis, 110*(3), 538-554. https://doi.org/10.1086/705532

Polanyi, K. (1957). The economy as instituted process. In K. Polanyi, C. M. Arensberg, & H. W. Pearson (Eds.), *Trade and market in the early empires: Economies in history and theory* (pp. 243-270). Free Press. https://archive.org/details/in.gov.ignca.36501

Rizvi, J. (1995). Merchants and mountains: The trade routes of Northwest India. *Himalayan Journal, 51*. https://www.himalayanclub.org/hj/51/13/merchants-and-mountains/

Rizvi, J. (1996). *Ladakh: Crossroads of High Asia* (2nd ed.). Oxford University Press. https://books.google.com/books?id=xoluAAAAMAAJ

Rizvi, J. (1999). *Trans-Himalayan caravans: Merchant princes and peasant traders in Ladakh*. Oxford University Press. https://books.google.com/books?id=Og-3AAAAIAAJ

Scott, J. C. (1976). *The moral economy of the peasant: Rebellion and subsistence in Southeast Asia*. Yale University Press. https://www.jstor.org/stable/j.ctt1bh4cdk

Scott, J. C. (1999). *Seeing like a state: How certain schemes to improve the human condition have failed*. Yale University Press. https://yalebooks.yale.edu/book/9780300078152/seeing-like-a-state/

Thomson, T. (1852). *Western Himalaya and Tibet: A narrative of a journey through the mountains of northern India, during the years 1847-8*. Reeve and Co. https://www.gutenberg.org/ebooks/42146

Treaty of Tingmosgang. (1684). *Historical treaty document*.

von Furer-Haimendorf, C. (1975). *Himalayan traders: Life in highland Nepal*. John Murray. https://books.google.com/books?id=Az0KAQAAIAAJ

Walton, H. G. (1910). *British Garhwal: A gazetteer*. Superintendent, Government Press. https://archive.org/details/in.ernet.dli.2015.181556

Warren, C. N., Shore, D., Otis, J., Wang, L., Finegold, M., & Shalizi, C. (2016). Six degrees of Francis Bacon: A statistical method for reconstructing large historical social networks. *Digital Humanities Quarterly, 10*(3). https://www.digitalhumanities.org/dhq/vol/10/3/000244/000244.html

Wetherell, C. (1998). Historical social network analysis. *International Review of Social History, 43*(S6), 125-144. https://doi.org/10.1017/S0020859000115123
