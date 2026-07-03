# Graph projection cookbook

Algorithms run on named in-memory projections created by `project_graph_cypher`.
The Cypher idiom differs by server mode. If session tools (`create_session`, ...)
are available, the server is in **session mode**; otherwise **plugin mode**.

## Plugin (on-prem) mode

Call `gds.graph.project()` with `$graph_name` as first argument:

```cypher
MATCH (n:Station)-[r:CONNECTED]->(m:Station)
RETURN gds.graph.project(
    $graph_name,
    n,
    m,
    {
        sourceNodeLabels: labels(n),
        targetNodeLabels: labels(m),
        relationshipType: type(r),
        relationshipProperties: {distance: toFloat(r.distance)}
    }
)
```

- Do not pass `sessionName` (it is rejected in plugin mode).
- Undirected relationships are declared inside the query, as the 4th argument:
  `{ undirectedRelationshipTypes: ['CONNECTED'] }`.

## Aura session mode

`sessionName` is required (session must already exist via `create_session`).
Call `gds.graph.project.remote()` with NO graph name and exactly three
arguments — source node, target node, data config:

```cypher
MATCH (n:Station)-[r:CONNECTED]->(m:Station)
RETURN gds.graph.project.remote(
    n,
    m,
    {
        sourceNodeLabels: labels(n),
        targetNodeLabels: labels(m),
        relationshipType: type(r),
        relationshipProperties: {distance: toFloat(r.distance)}
    }
)
```

- Undirected relationships: use the tool's top-level
  `undirectedRelationshipTypes` parameter (e.g. `["CONNECTED"]`). Do NOT put
  `undirectedRelationshipTypes` or `orientation` inside the remote data config
  map — the remote projection rejects them there.

## Rules for both modes

- **Only numeric properties project.** Node/relationship properties must be
  numeric or numeric lists; wrap with `toFloat(...)` where needed. Strings
  cannot be projected — keep them in the database and use
  `nodeIdentifierProperty` (or `dbNodeProperties` on `stream_node_properties`)
  to attach them to results.
- **Project what the analysis needs.** Include the weight property if any
  algorithm will be weighted; algorithms cannot use properties that were not
  projected.
- **Undirected is a projection-time decision.** Needed by `triangle_count`,
  `local_clustering_coefficient`, link prediction training, and whenever the
  relationship is semantically symmetric (e.g. road networks for
  louvain/node_similarity). To switch orientation, drop and re-project.
- **Node properties for property-based tools** (`k_means_clustering`,
  `HDBSCAN`, `k_nearest_neighbors`, ML features): either project them from the
  database (nodeProperties in the data config map) or produce them in-memory
  with a mutate-mode algorithm (e.g. `fast_rp`).
- Graph names must be unique; `drop_graph` before re-projecting under the same
  name.

## Inspecting a projection

- `list_graphs` — all projections (with `sessionName` tags in session mode).
- `get_graph_info` — counts, schema, degree distribution, density, memory; use
  it to confirm which properties exist in-memory before running algorithms.
- `stream_node_properties` / `stream_relationship_properties` /
  `stream_relationships` — read projected or mutated values; supports label
  and type filters, and `dbNodeProperties` to join database properties (e.g.
  names) onto results.
