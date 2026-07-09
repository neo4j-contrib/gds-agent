---
name: neo4j-graph-data-scientist
description: Best practices for data science work on graphs using the available tools.
compatibility: Requires the gds-agent MCP server (PyPI package gds-agent) connected
  to a Neo4j database with the GDS plugin, or a Neo4j AuraDB with Aura Graph Analytics.
---

## Workflow best practices

1. **Inspect the database schema first.** Never guess labels, types, or property names.
2. **Project a graph.** Plugin and session mode have different projection syntax and parameters. Check the graph projection tool description and parameters..
3. **Clean up.** `drop_graph` when a projection is no longer needed. 
`delete_session` when a session is no longer needed, and this will automatically drop all graphs projected to this session.
4. **Large graphs.** When the graph in the DB large, you might want to consider projecting subgraphs at the start for analysis.
When the projected graph is large, consider `mode: "mutate"` to store the computed results in the projected graph and then use 
`stream_node_properties` or `stream_relationship_properties` to inspect the data.
5. **When you see errors, inspect the message and make necessary corrections.** If you cannot fix it, consult the detailed [references/troubleshooting.md](references/troubleshooting.md) guide.
