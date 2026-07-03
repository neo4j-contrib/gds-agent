SERVER_INSTRUCTIONS = """Neo4j Graph Data Science (GDS) tools. Algorithms never run on the database directly; they run on named in-memory graph projections.

Workflow:
1. Inspect the schema first (get_node_labels, get_relationship_types, get_node_properties_keys, get_relationship_properties_keys, count_nodes). Never guess labels or property names.
2. Check list_graphs for an existing projection to reuse; otherwise create one with project_graph_cypher. Only numeric properties can be projected; include the weight property if a weighted algorithm will run. Relationships that algorithms treat as undirected (triangle_count, local_clustering_coefficient, link prediction training) must be projected undirected.
3. Match the question to the right algorithm: importance/influence -> centrality tools (pagerank, betweenness_centrality, degree_centrality, ...); groups/clusters -> community tools (louvain, leiden, weakly_connected_components, ...); routes/distances -> path tools (find_shortest_path, yens_shortest_paths, ...); similar nodes/recommendations -> node_similarity or embeddings + k_nearest_neighbors; predictions -> ML pipeline tools.
4. Run with mode 'stream' for small results. For large graphs or when a later step consumes the output (embeddings -> kNN, communities -> conductance, ML features), use mode 'mutate' with mutateProperty and read back via stream_node_properties. Mutate writes only to the in-memory projection, never to the database.
5. Pass nodeIdentifierProperty (e.g. 'name') so node inputs and outputs use human-readable identifiers; path tools require it.
6. Drop projections with drop_graph when finished.

Session mode: if create_session/list_sessions/delete_session tools are present, the server uses Aura Graph Analytics sessions. Create a session before the first projection; project_graph_cypher then requires sessionName. All other tools locate the session automatically from graphName. To recover from a session out-of-memory, delete_session and create_session again with a larger memoryGB, then re-project.

If a result carries a truncation warning, do not retry the same call: re-run in mutate mode and inspect selectively with the stream_* accessor tools, or narrow the query (nodes filter, topK/topN).
"""
