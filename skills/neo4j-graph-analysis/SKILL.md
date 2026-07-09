---
name: neo4j-graph-data-scientist
description: Best practices for data science work on graphs using the available tools.
compatibility: Requires the gds-agent MCP server (PyPI package gds-agent) connected
  to a Neo4j database with the GDS plugin, or a Neo4j AuraDB with Aura Graph Analytics.
---

## Workflow best practices

1. **Inspect the database schema first.** Never guess labels, types, or property names.
2. **Project a graph.** See [references/projections.md](references/projections.md) for the exact
   Cypher idioms — they differ between plugin and sessions.
3. **Clean up.** `drop_graph` when a projection is no longer needed. 
`drop_graph` when a session is no longer needed, and this will automatically drop all graphs projected to this session.
4. **Large graphs.** When the graph in the DB large, you might want to consider projecting subgraphs at the start for analysis.
When the projected graph is large, consider `mode: "mutate"` to store the computed results in the projected graph and then use 
`stream_node_properties` or `stream_relationship_properties` to inspect the data.


## Rules of thumb
- Errors, out-of-memory, and empty results:
  [references/troubleshooting.md](references/troubleshooting.md).
