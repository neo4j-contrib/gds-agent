---
name: neo4j-graph-data-scientist
description: Use when analyzing Neo4j graph data with GDS Agent tools, including projection, graph algorithms, ML pipelines, result interpretation, and troubleshooting.
compatibility: Requires the gds-agent MCP server (PyPI package gds-agent) connected to a Neo4j database with the GDS plugin, or a Neo4j AuraDB with Aura Graph Analytics.
---

## Workflow

1. **Inspect the database schema first.** Never guess labels, types, or property names. Use `get_neo4j_schema`.
2. **Project a graph.** All GDS algorithms run on an in-memory projected graph (`graph_name`) created with `project_graph_cypher` (use `get_graph_info` or `list_graphs` to inspect existing projections). Plugin and session mode have different projection syntax and parameters. For session mode, first create a session with `create_session` to project graphs onto.
3. **Run algorithms (`stream` vs `mutate`) and map node identifiers.**
   - **`mode` (`'stream'` vs `'mutate'`):** `'stream'` (default) returns results as a table. `'mutate'` writes results back to the in-memory projected graph under `mutate_property` (and `mutate_relationship_type` for relationship-producing tools). Prefer `'mutate'` when chaining algorithms on the same projected graph (e.g., computing node embeddings or centrality scores to use as input features for clustering, `k_nearest_neighbors`, or ML pipelines), or when results are large (then read back selectively with `stream_node_properties` or `stream_relationship_properties`).
   - **`node_identifier_property`:** Specify a database node property (e.g., `'name'` or `'title'`) to translate readable identifier values in algorithm inputs and streamed results. Similarity filters may alternatively accept node labels.
   - **Graph orientation:** Choose projection orientation deliberately and follow each algorithm tool's stated requirements.
4. **Clean up.** `drop_graph` when a projection is no longer needed, and `drop_model` when a trained ML model is no longer needed. `delete_session` when a session is no longer needed, which automatically drops all graphs projected to this session.
5. **When you see errors, inspect the message and consult [references/troubleshooting.md](references/troubleshooting.md).** Then make necessary corrections.
6. **Independently verify key results.**
    Verify the key results using a genuinely different method if the problem allows. If the two methods disagree, investigate the discrepancy and resolve it first if it can be resolved. Otherwise, say so explicitly in the answer. This step is not satisfied by sanity checking the logic mentally.


## Best Practices
1. **Large graphs.** When the graph in the DB is large, you might want to consider projecting subgraphs at the start for analysis.
2. **Long running tools.** Certain algorithms (or Cypher queries) are long running. For exploratory work, try them on smaller projected graphs before executing them on the full desired graph.
3. **Follow general data science best practice.** Understand if the task is transductive (over the fixed data) or inductive. For predictive tasks, ensure there is no data leakage.
   Formulate hypotheses and design metrics appropriately. Follow standard statistical best practices.
4. **Perform additional analysis when needed.** You do not need to use solely the Cypher and GDS tools. 
   For complex data science tasks, use other tools or ad-hoc scripts with libraries such as PyTorch, scikit-learn, pandas, or Matplotlib when necessary.
