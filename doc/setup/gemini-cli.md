# Gemini CLI

The extension bundles the MCP server, the `neo4j-graph-data-scientist` skill, and a context file in one install.

1. Prerequisite: [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
2. Install the extension:
   ```bash
   gemini extensions install https://github.com/neo4j-contrib/gds-agent
   ```
3. Provide credentials via the extension settings when prompted (sensitive values go to the OS keychain). Only variables declared in the extension's `settings` are forwarded to the server: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, optional `NEO4J_DATABASE` and `AURA_API_*`.
4. Verify: `gemini skills list --all` shows `neo4j-graph-data-scientist`, and `/mcp` inside a session shows the `neo4j-gds` server.

Update later with `gemini extensions update gds-agent`.
