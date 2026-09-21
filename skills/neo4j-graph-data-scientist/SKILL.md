---
name: neo4j-graph-data-scientist
description: Use for graph realted tasks on Neo4j via GDS Agent and Cypher tools. Covers the workflow and a troubleshooting guide for errors.
compatibility: Requires the gds-agent MCP server (PyPI package gds-agent) and cypher MCP server (PyPI package mcp-neo4j-cypher) connected to a Neo4j database with the GDS plugin, or a Neo4j AuraDB with Aura Graph Analytics.
---

## Workflow

1. **Inspect the database schema first.** Never guess labels, types, or property names.
2. **Project a graph.** Plugin and session mode have different projection syntax and parameters. Check the graph projection tool description and parameters. For session mode, you need to first create sessions to project graphs onto.
3. **Clean up.** `drop_graph` when a projection is no longer needed. `delete_session` when a session is no longer needed, and this will automatically drop all graphs projected to this session.
4. **When you see errors, inspect the message and consult [references/troubleshooting.md](references/troubleshooting.md).** Then make necessary corrections.
5. **Independently verify key results.**
    Verify the key results using a genuinely different method if the problem allows. If the two methods disagree, investigate the discrepancy and resolve it first if it can be resolved. Otherwise, say so explicitly in the answer. This step is not satisfied by sanity checking the logic mentally.


## Best Practices
1. **Large graphs.** When the graph in the DB is large, you might want to consider projecting subgraphs at the start for analysis.
2. **Long running tools.** Certain algorithms (or Cypher queries) are long running. For exploratory work, consider trying them out on smaller projected graphs before executing them on a desirable large projected graph.
3. **Follow general data science best practice.** Understand if the task is transductive (over the fixed data) or inductive. For predictive tasks, ensure there is no data leakage.
Formulate hypothesis and design metrics appropriately. Remember all the basic statistics best practices.
4. **Perform additional analysis when needed.** You do not need to use solely the Cypher and GDS tools. 
For complex data science task, feel free to use other tools or coding capabilities and write ad-hoc scripts that use other libraries, such as pytorch, scikit-learn, pandas, matplotlib, when necessary.