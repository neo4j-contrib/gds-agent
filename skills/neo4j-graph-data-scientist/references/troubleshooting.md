# Troubleshooting

## Truncated results

Streamed results are capped (defaults: 500 rows, 100,000 chars, 200 chars per
cell; configurable via `GDS_AGENT_MAX_RESULT_ROWS`, `GDS_AGENT_MAX_RESULT_CHARS`,
`GDS_AGENT_MAX_CELL_CHARS` on the server). A truncation warning in a result
means: do not retry the same call. Instead:

- Re-run in `mode: "mutate"` and read back selectively with
  `stream_node_properties` (filter by `nodeLabels`) or the other accessors.
- Or narrow the algorithm itself (`nodes` filter, `topK`/`topN`, higher
  `similarityCutoff`, `minCommunitySize`, ...).

## Common errors

| Error | Cause -> Fix |
|---|---|
|Algorithm requires UNDIRECTED graphs|The selected algorithm can only run on undirected graphs but you supplied a directed graph projection -> Project another graph that is undirected by setting undirectedRelationshipTypes. |