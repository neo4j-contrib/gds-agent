# Troubleshooting

## Truncated results

Streamed results are capped (defaults: 500 rows, 100,000 chars, 200 chars per
cell; configurable via `GDS_AGENT_MAX_RESULT_ROWS`, `GDS_AGENT_MAX_RESULT_CHARS`,
`GDS_AGENT_MAX_CELL_CHARS` on the server). A truncation warning in a result
means: do not retry the same call. Instead:

- Re-run in `mode: "mutate"` and read back selectively with
  `stream_node_properties` (filter by `nodeLabels`) or the other accessors.
- Or narrow the algorithm itself (`nodes` filter, `top_k`/`top_n`, higher
  `similarity_cutoff`, `min_community_size`, ...).

## Out-of-memory errors

If a call fails with out-of-memory or `Memory required to run … exceeds available memory`, do not retry the same parameters. Instead:
- Shrink the projection with node or relationship filters.
- Split the task into smaller subproblems.
- If the failing call was Cypher, rewrite that query (a smaller GDS projection will not fix it).
- If shrinking or splitting is not enough and the question can be answered without an exact full-graph result, compute an estimate and report it as an estimate. Do not substitute an estimate when an exact result is required.

## Common errors

| Error | Cause -> Fix |
|---|---|
|Algorithm requires UNDIRECTED graphs|The algorithm received a directed projection -> Re-project the graph as undirected, following the mode-specific `project_graph_cypher` schema.|
|Node/relationship has wrong label/type or properties|The requested schema element does not exist -> Inspect it with `get_neo4j_schema`, the property-key tools, or `read_neo4j_cypher`, then correct the call.|