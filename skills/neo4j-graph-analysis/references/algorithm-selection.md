# Algorithm selection guide

Match the user's question to a tool. Tool names below are exact.

## Centrality — "important", "influential", "critical" nodes

| Question | Tool | Notes |
|---|---|---|
| Most connected nodes | `degree_centrality` | `orientation` for in/out-degree; supports weights |
| Overall importance/influence (link structure) | `pagerank` | classic default for directed influence |
| Importance normalised by out-links (citations) | `article_rank` | PageRank variant |
| Bridges/bottlenecks on shortest paths | `betweenness_centrality` | `samplingSize` for large graphs |
| Nodes closest to everything (spread quickly) | `closeness_centrality` | use `harmonic_centrality` if the graph is disconnected |
| Robust closeness on disconnected graphs | `harmonic_centrality` | |
| Influence via well-connected neighbours | `eigenvector_centrality` | |
| Hubs vs authorities (directed) | `HITS` | returns both scores |
| Best k seed nodes to maximise spread | `CELF` | requires `seedSetSize` |
| Single points of failure (nodes) | `articulation_points` | structural, no scores |
| Single points of failure (edges) | `bridges` | structural, no scores |

## Community detection — "groups", "clusters", "segments"

| Question | Tool | Notes |
|---|---|---|
| Communities (default choice) | `louvain` | modularity-based, hierarchical |
| Communities, higher quality/guaranteed connected | `leiden` | prefer over louvain when quality matters |
| Very fast community detection | `label_propagation` | non-deterministic |
| Overlapping communities (node in several) | `speaker_listener_label_propagation` | randomized; raise `maxIterations` |
| Connected components (ignore direction) | `weakly_connected_components` | good first structural check |
| Strongly connected components (directed cycles) | `strongly_connected_components` | |
| Dense cores / peeling by degree | `k_core_decomposition` | |
| Triangles per node | `triangle_count` | needs UNDIRECTED projection |
| How clique-like each node's neighbourhood is | `local_clustering_coefficient` | needs UNDIRECTED projection |
| Cluster by node property vectors (k clusters) | `k_means_clustering` | requires `nodeProperty` (float array, e.g. embedding) |
| Density-based clustering of property vectors | `HDBSCAN` | requires `nodeProperty`; no k needed |
| Colour nodes so neighbours differ | `k_1_coloring` | scheduling/conflict problems |
| Split into k parts maximising cross-part edges | `approximate_maximum_k_cut` | |
| Evaluate an existing community assignment | `conductance`, `modularity_metric` | require `communityProperty` (mutate a community algorithm first) |

## Path finding — "route", "distance", "reachable", "flow"

| Question | Tool | Notes |
|---|---|---|
| Shortest path between two nodes | `find_shortest_path` | Dijkstra; `relationship_property` for weights |
| k alternative shortest paths | `yens_shortest_paths` | `k` paths between source and target |
| Shortest paths from one node to all | `dijkstra_single_source_shortest_path` | `delta_stepping_shortest_path` is the parallel alternative |
| Shortest paths between all pairs | `all_pairs_shortest_paths` | returns Infinity for unreachable pairs |
| Shortest path with geo coordinates | `a_star_shortest_path` | requires `latitudeProperty`/`longitudeProperty` |
| Negative weights allowed | `bellman_ford_single_source_shortest_path` | detects negative cycles |
| Cheapest tree connecting everything reachable | `minimum_weight_spanning_tree` | `objective` can also maximise |
| Cheapest tree from source to specific targets | `minimum_directed_steiner_tree` | |
| Most valuable subtree (node prizes vs edge costs) | `prize_collecting_steiner_tree` | requires `prizeProperty` |
| Layer-by-layer exploration / hops | `breadth_first_search` | `maxDepth`, `targetNodes` termination |
| Deep exploration | `depth_first_search` | |
| Longest path (DAGs) | `longest_path` | cyclic components are excluded |
| Maximum throughput with capacities | `max_flow` | requires `capacityProperty` |
| Random paths (sampling, simulation) | `random_walk` | second-order walks via `inOutFactor`/`returnFactor` |

Path tools take node references via `sourceNode`/`targetNode(s)`/`start_node`/
`end_node` values of `nodeIdentifierProperty`, which is required. In mutate
mode they use `mutateRelationshipType` instead of `mutateProperty`.

## Similarity — "similar", "alike", "recommend"

| Question | Tool | Notes |
|---|---|---|
| Similar nodes by shared neighbours | `node_similarity` | Jaccard/Overlap/Cosine via `similarityMetric`; `topK` per node, `topN` overall |
| Nearest neighbours by property vectors | `k_nearest_neighbors` | requires `nodeProperties` (typically an embedding); ignores topology |

Recommendation pattern: embeddings (mutate) → `k_nearest_neighbors` on the
embedding property.

## Embeddings & ML

See [ml-pipelines.md](ml-pipelines.md): `fast_rp`, `node2vec`, `hashgnn`,
`graph_sage_train`/`graph_sage_predict`, and the train/predict pipelines for
node classification, link prediction, and node regression, plus `list_models`
and `drop_model`.
