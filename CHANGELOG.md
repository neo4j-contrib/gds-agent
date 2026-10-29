# Changelog - [1.2.0] - 2026-10-29


### Breaking Changes

- The Claude Code plugin and the Gemini extension no longer start a separate `mcp-neo4j-cypher` server. `read_neo4j_cypher`, `write_neo4j_cypher`, and `get_neo4j_schema` are tools on `gds-agent`.

### New Features

- `read_neo4j_cypher` runs a read query, `write_neo4j_cypher` runs a write query and returns the update counts, and `get_neo4j_schema` returns the APOC schema sample.

### Bug Fixes
1. Warn that truncated results are incomplete and must not drive decisions.
2. Change `failIfMissing=True` in `drop_graph` as otherwise the function throws an uninformative 'NoneType' object has no attribute 'get' error instead.
3. Note that UNDIRECTED degree on an undirectedRelationshipTypes projection counts each neighbor twice.
