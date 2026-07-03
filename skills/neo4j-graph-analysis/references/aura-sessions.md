# Aura Graph Analytics sessions

In session mode (AuraDB without the GDS plugin), computation happens in
dedicated GDS sessions. The server is in session mode when the
`list_sessions`, `create_session`, and `delete_session` tools are available.

## Lifecycle

1. **Create explicitly.** Sessions are never created implicitly. Call
   `create_session` with a `sessionName` before the first projection.
   Optional `memoryGB` (default 8, or the server's `SESSION_MEMORY_GB`).
2. **Project into it.** `project_graph_cypher` requires `sessionName` in
   session mode. Every other tool routes automatically: it finds the graph's
   session from `graphName`.
3. **Reuse.** Calling `create_session` with an existing name reconnects to it.
   `list_sessions` shows what's active.
4. **Delete when done.** `delete_session` frees the compute. Dropping a graph
   (`drop_graph`) keeps the session alive.

## Conventions and behavior

- Session names get an `mcp_` prefix if missing; the returned `sessionName` is
  the actual name — use it in follow-up calls.
- Most workflows need exactly ONE session holding all projected graphs.
  Create additional sessions only to isolate independent analyses on separate
  compute (e.g. to parallelize).
- Sessions expire after a TTL (server default 24h).
- `list_graphs` and `list_models` span all active sessions and tag each row
  with its `sessionName`.

## Resizing after an out-of-memory failure

Sessions cannot be resized in place: `delete_session`, then `create_session`
with the same name and a larger `memoryGB`. This drops all graphs projected
into the session — re-project them afterwards.
