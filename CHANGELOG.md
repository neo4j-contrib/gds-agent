# Changelog - [1.2.0] - 2026-11-09


### Breaking Changes

- The Claude Code plugin and the Gemini extension no longer start a separate `mcp-neo4j-cypher` server. `read_neo4j_cypher`, `write_neo4j_cypher`, and `get_neo4j_schema` are tools on `gds-agent`.
- `get_neo4j_schema` no longer uses APOC and has a slightly different output format, and replaces the older `get_node_labels`, `get_relationship_types`, `get_node_properties_keys`, and `get_relationship_properties_keys` tools.
- All tool parameter names are now `snake_case` (e.g. `graphName` → `graph_name`, `dampingFactor` → `damping_factor`).

### New Features

1. `read_neo4j_cypher` runs a read query (with a configurable 120-second timeout via `--read-timeout` / `NEO4J_READ_TIMEOUT`), `write_neo4j_cypher` runs a write query and returns the update counts, and `get_neo4j_schema` returns node and relationship types with their properties, indexes, connections, and counts.
2. Upgraded `graphdatascience` client from 1.22 to 2.3.
3. Simplify MCP tool schemas and consolidate workflow guidance in server instructions and `SKILL.md` to reduce input token usage.

### Bug Fixes
1. Warn that truncated results are incomplete and must not drive decisions.
2. Change `failIfMissing=True` in `drop_graph` as otherwise the function throws an uninformative 'NoneType' object has no attribute 'get' error instead.
3. Note that UNDIRECTED degree on an undirectedRelationshipTypes projection counts each neighbor twice.
