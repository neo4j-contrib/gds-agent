# Neo4j GDS Agent

This extension connects the `neo4j-gds` MCP server: ~70 tools running Neo4j
Graph Data Science algorithms (centrality, community detection, path finding,
similarity, node embeddings, and ML pipelines) against the Neo4j database
configured in the extension settings.

Key points:

- Algorithms run on named in-memory graph projections, never on the database
  directly, and nothing ever writes to the database.
- Follow the `neo4j-graph-data-scientist` skill bundled with this extension for the
  full workflow: inspect schema → project a graph → select the algorithm →
  run (stream or mutate mode) → interpret results → drop the projection.
- Database credentials come from the extension settings (`NEO4J_URI`,
  `NEO4J_USERNAME`, `NEO4J_PASSWORD`; optional `NEO4J_DATABASE` and
  `AURA_API_*` for Aura Graph Analytics session mode).
- If session tools (`create_session`, `list_sessions`, `delete_session`) are
  available, create a session before projecting graphs.
