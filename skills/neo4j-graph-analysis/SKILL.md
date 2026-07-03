---
name: neo4j-graph-analysis
description: Select and run Neo4j Graph Data Science (GDS) algorithms through the
  gds-agent MCP tools. Use when analysing a Neo4j graph, e.g. finding important or
  influential nodes (centrality), detecting communities or clusters, computing
  shortest paths or routes, measuring similarity, generating node embeddings, or
  training ML models for node classification, link prediction, or node regression.
  Covers graph projection, Aura Graph Analytics sessions, algorithm selection, and
  interpreting results.
license: MIT
compatibility: Requires the gds-agent MCP server (PyPI package gds-agent) connected
  to a Neo4j database with the GDS plugin, or a Neo4j AuraDB with Aura Graph Analytics.
metadata:
  author: neo4j-contrib
  source: https://github.com/neo4j-contrib/gds-agent
---

# Neo4j graph analysis with GDS

The gds-agent MCP server exposes ~70 tools that run Neo4j Graph Data Science
algorithms. Algorithms never run on the database directly: they run on named
in-memory **graph projections**. Follow this workflow for every analysis.

## Core workflow

1. **Inspect the database schema first.** Use `get_node_labels`,
   `get_relationship_types`, `get_node_properties_keys`,
   `get_relationship_properties_keys`, and `count_nodes` to learn what exists.
   Never guess labels, types, or property names.
2. **Check for an existing projection.** `list_graphs` shows projected graphs.
   Reuse a suitable one instead of re-projecting.
3. **Project a graph** with `project_graph_cypher`, giving it a descriptive
   `graphName`. Project only the labels, relationships, and properties the
   analysis needs. Only numeric (or numeric-list) properties can be projected.
   See [references/projections.md](references/projections.md) for the exact
   Cypher idioms — they differ between plugin and session mode, and undirected
   relationships need special handling.
4. **Pick the algorithm.** Match the user's question to an algorithm using
   [references/algorithm-selection.md](references/algorithm-selection.md).
   Don't default to PageRank; e.g. "bottlenecks" → betweenness or
   articulation_points, "groups" → louvain/leiden, "alternatives to the best
   route" → yens_shortest_paths.
5. **Run it.** Every algorithm takes the `graphName`. Two result modes:
   - `mode: "stream"` (default) returns rows directly. Fine for small results.
   - `mode: "mutate"` + `mutateProperty` writes results to the in-memory graph
     (never to the database). Use it when results are large, or when a later
     step consumes them (embeddings → kNN, community → conductance, features
     for ML training). Read mutated values back with `stream_node_properties`.
6. **Interpret results with real identifiers.** Pass `nodeIdentifierProperty`
   (e.g. `"name"`) so inputs and outputs use human-readable node identifiers
   instead of internal ids. Path algorithms require it.
7. **Clean up.** `drop_graph` when a projection is no longer needed; it never
   touches the underlying database.

## Plugin mode vs Aura session mode

The server auto-detects its mode at startup:

- **Plugin mode** (on-prem/self-managed Neo4j with the GDS plugin): projections
  live in the database's GDS graph catalog. Do not pass `sessionName` anywhere.
- **Session mode** (AuraDB + Aura Graph Analytics): the `create_session`,
  `list_sessions`, and `delete_session` tools exist — their presence tells you
  the server is in session mode. You must `create_session` before the first
  projection, and `project_graph_cypher` requires a `sessionName`. All other
  tools find the right session automatically from `graphName`. See
  [references/aura-sessions.md](references/aura-sessions.md).

## Universal parameters

- `graphName` (required everywhere): the projection to run on.
- `mode` / `mutateProperty` (or `mutateRelationshipType` for path algorithms):
  stream vs mutate, as above.
- `nodeIdentifierProperty`: property used to reference nodes by value in inputs
  (`sourceNode`, `targetNodes`, `nodes`, ...) and to translate result ids back.
- `nodes`: optional filter to restrict streamed centrality results to specific
  nodes.
- `relationshipWeightProperty`: name of a projected numeric relationship
  property; required whenever the question implies weights/distances/costs.
  The property must have been included in the projection.

## Rules of thumb

- Weighted questions need weighted projections: include the weight property in
  the projection *and* pass `relationshipWeightProperty` to the algorithm.
- Algorithms that treat the graph as undirected (triangle_count,
  local_clustering_coefficient, link prediction training, often
  louvain/leiden/node_similarity for symmetric relations) need the
  relationships projected as UNDIRECTED — this is a projection-time decision;
  see [references/projections.md](references/projections.md).
- Large graphs: prefer `mode: "mutate"`, then inspect with
  `stream_node_properties` using filters. Results streamed to you are truncated
  (default 500 rows / 100k chars) — a truncation warning in a result means
  switch to mutate + accessors, not retry.
- Embeddings and ML pipelines have their own multi-step workflows:
  [references/ml-pipelines.md](references/ml-pipelines.md).
- Errors, out-of-memory, and empty results:
  [references/troubleshooting.md](references/troubleshooting.md).

## Worked example (plugin mode)

User asks: "Which underground stations are the biggest interchange bottlenecks?"

1. `get_node_labels` → `UndergroundStation`; `get_relationship_types` → `LINK`.
2. `project_graph_cypher` with graphName `tube`:
   `MATCH (n:UndergroundStation)-[r:LINK]->(m:UndergroundStation) RETURN gds.graph.project($graph_name, n, m)`
3. Bottleneck ⇒ `betweenness_centrality` on `tube` with
   `nodeIdentifierProperty: "name"`.
4. Report the top stations by score, by name.
5. `drop_graph` `tube` if no follow-up analysis is expected.
