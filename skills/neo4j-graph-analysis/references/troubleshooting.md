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

| Symptom | Cause → fix |
|---|---|
| `Graph 'X' was not found in any active session` | Session mode without projection. `create_session`, then `project_graph_cypher` with `sessionName`. |
| `sessionName is required in Aura session mode` | Create/name a session first; pass it to `project_graph_cypher`. |
| `sessionName is only available in Aura session mode` | Plugin mode: omit `sessionName`. |
| `Session 'X' is no longer available` | Expired/deleted (TTL). Recreate with `create_session` and re-project. |
| Graph already exists | `drop_graph` first, or pick a new `graphName`. |
| Property not found when running an algorithm | It wasn't projected. Check `get_graph_info`, re-project including the property (numeric only, `toFloat(...)`). |
| Weighted algorithm ignores weights | `relationshipWeightProperty` not passed, or property missing from projection. |
| Node not found for `sourceNode`/`start_node` | Wrong `nodeIdentifierProperty` or value; verify with `get_node_properties_keys` and the database value. |
| Triangle count / clustering coefficient returns 0 everywhere | Graph projected as directed. Re-project UNDIRECTED. |
| Link prediction training rejects the graph | Target relationship type must be projected UNDIRECTED (session mode: `undirectedRelationshipTypes` parameter). |
| Session out-of-memory | Delete and recreate the session with larger `memoryGB`; re-project graphs (see aura-sessions.md). |
| Empty algorithm result | Check the projection isn't empty (`get_graph_info` node/relationship counts) and filters aren't too strict. |

## Where results live

- Stream mode: in the tool response only.
- Mutate mode: in the in-memory projection only — never in the Neo4j database.
  Nothing gds-agent does writes to the database.
- Models: in the GDS model catalog (`list_models`), per session in session mode.
