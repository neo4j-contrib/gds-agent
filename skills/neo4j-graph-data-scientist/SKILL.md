---
name: neo4j-graph-data-scientist
description: Use for graph realted tasks on Neo4j via GDS Agent and Cypher tools. Covers the workflow and a troubleshooting guide for errors.
compatibility: Requires the gds-agent MCP server (PyPI package gds-agent) and cypher MCP server (PyPI package mcp-neo4j-cypher) connected to a Neo4j database with the GDS plugin, or a Neo4j AuraDB with Aura Graph Analytics.
---

## Workflow

1. **Inspect the database schema first.** Never guess labels, types, or property names.
2. **Project a graph.** Plugin and session mode have different projection syntax and parameters. Check the graph projection tool description and parameters. For session mode, you need to first create sessions to project graphs onto.
3. **Clean up.** `drop_graph` when a projection is no longer needed. `delete_session` when a session is no longer needed, and this will automatically drop all graphs projected to this session.
4. **When you see errors, inspect the message and make necessary corrections.** If you cannot fix it, consult the detailed [references/troubleshooting.md](references/troubleshooting.md) guide.
5. **MANDATORY before any final answer independently verify.**
   Re-derive the key result using a genuinely different method before reporting it as final.
   - If the two methods disagree, do NOT report a result. Investigate the discrepancy
     (data modeling, edge direction/dedup, projection filters, off-by-one hop counts) and resolve
     it first.
   - If a discrepancy cannot be resolved, say so explicitly in the answer rather than silently
     picking one number.
   - State in the final answer which independent check was performed and that it matched.
   This step is not optional and is not satisfied by sanity checking the logic mentally.


## Best Practices
1. **Large graphs.** When the graph in the DB is large, you might want to consider projecting subgraphs at the start for analysis.
When the projected graph is large, consider `mode: "mutate"` to store the computed results in the projected graph. Narrow the results before using `stream_node_properties`, `stream_relationship_properties`, or `stream_relationships`, as repeating an unfiltered stream can produce another truncated response. Alternatively, run the algorithm's stream procedure in a Cypher query and filter its yielded rows.
2. **Long running tools.** Certain algorithms (or Cypher queries) are long running. For exploratory work, consider trying them out on smaller projected graphs before executing them on a desirable large projected graph.
3. **Follow general data science best practice.** Understand if the task is transductive (over the fixed data) or inductive. For predictive tasks, ensure there is no data leakage.
Formulate hypothesis and design metrics appropriately. Remember all the basic statistics best practices.
4. **Perform additional analysis when needed.** You do not need to use solely the Cypher and GDS tools. 
For complex data science task, feel free to use other tools or coding capabilities and write ad-hoc scripts that use other libraries, such as pytorch, scikit-learn, pandas, matplotlib, when necessary.