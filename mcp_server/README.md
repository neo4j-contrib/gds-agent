

# GDS Agent

This MCP Server includes toolings from Neo4j Graph Data Science (GDS) library, which allows you to run all common graph algorithms, node embeddings, and machine learning pipelines.

Once set up, you can **ask any graph question about your Neo4j graph** and get answers. You can collaborate with the agent as a graph data scientist to solve complex tasks. LLMs equipped with GDS agent can decide and execute the appropriate parameterised graph algorithms over the graph you have in your Neo4j database.

# Usage guide

If you have `uvx` [installed](https://docs.astral.sh/uv/getting-started/installation/), add the following config to your `claude_desktop_config.json`

```
{
    "mcpServers": {
      "neo4j-gds": {
      "command": "/opt/homebrew/bin/uvx",
      "args": [ "gds-agent" ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": ""
      }
    }
    }
}
```

Replace command with your `uvx` location. Find out by running `which uvx` in the command line.
Replace `NEOJ_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` with your database login details. You can also optionally specify `NEO4J_DATABASE`.

By default the server uses STDIO transport. For HTTP-native clients, run:

```bash
gds-agent --transport http --host 127.0.0.1 --port 8000 --path /mcp
```

You can also set `GDS_AGENT_TRANSPORT`, `GDS_AGENT_HOST`, `GDS_AGENT_PORT`, and `GDS_AGENT_PATH`. The Neo4j MCP-style `NEO4J_TRANSPORT` and `NEO4J_MCP_SERVER_*` names are also supported.

## GDS Aura Graph Analytics (sessions)

The server detects whether the connected Neo4j has the GDS plugin installed or whether to use a GDS Aura Graph Analytics session. Detection runs `gds.session.list()` on startup; if it succeeds, session mode is used and graph projections fall back to `gds.graph.project.remote`.

Session mode requires Aura API credentials. Add them to the same `env` block (or `.env` file) used for the database credentials:

```
"AURA_API_CLIENT_ID": "...",
"AURA_API_CLIENT_SECRET": "...",
"AURA_API_PROJECT_ID": "...",
"SESSION_MEMORY_GB": "8",
"SESSION_TTL_HOURS": "24"
```

`AURA_API_PROJECT_ID` is optional (needed only if your Aura API client has access to multiple projects), as are `SESSION_MEMORY_GB` (default 8) and `SESSION_TTL_HOURS` (default 24). Sessions are managed explicitly by the agent: three extra tools become available in session mode (`list_sessions`, `create_session`, and `delete_session`). A session must first be created with `create_session`, `project_graph_cypher` then projects each graph into the session named by its required `sessionName` parameter, and algorithm calls are routed to the right session automatically by `graphName`. Most workflows need a single session holding all graphs; multiple sessions allow running analyses in parallel. To resize a session (e.g. after an OOM), delete it and create it again with a larger `memoryGB`. All sessions created by the server are named with an `mcp_` prefix.

# Other clients and the graph-analysis skill

This package is one half of the GDS Agent: the repository also ships a `neo4j-graph-data-scientist` Agent Skill and one-step installers for Claude Code (plugin), Claude Desktop (MCPB bundle), OpenAI Codex, Cursor, VS Code/Copilot, and Gemini CLI. See the per-harness setup guides: [https://github.com/neo4j-contrib/gds-agent#install](https://github.com/neo4j-contrib/gds-agent#install).

# Full documentation

For complete documentation and development guidelines, please refer to: [https://github.com/neo4j-contrib/gds-agent](https://github.com/neo4j-contrib/gds-agent).