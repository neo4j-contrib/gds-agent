# Claude Code

The plugin installs the MCP server and the `neo4j-graph-analysis` skill together — this is the recommended path.

## Plugin install (tools + skill)

1. Prerequisite: [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (`which uvx`).
2. In Claude Code:
   ```
   /plugin marketplace add neo4j-contrib/gds-agent
   /plugin install gds-agent@neo4j-gds
   ```
3. When prompted by the plugin's configuration form, enter your Neo4j URI, username, and password (stored in the OS keychain), plus the optional database name and Aura API credentials (needed only for Aura Graph Analytics session mode on AuraDB).
4. Verify: `/mcp` should list `neo4j-gds` as connected, and asking e.g. *"Which are the most central nodes in my graph?"* should trigger the `neo4j-graph-analysis` skill and call the schema tools first.

## MCP server only (no skill)

```bash
claude mcp add --scope user \
  --env NEO4J_URI=neo4j://localhost:7687 \
  --env NEO4J_USERNAME=neo4j \
  --env NEO4J_PASSWORD=your-password \
  --transport stdio neo4j-gds -- uvx gds-agent
```

Add `--env AURA_API_CLIENT_ID=... --env AURA_API_CLIENT_SECRET=...` for Aura Graph Analytics session mode. To get the skill without the plugin: `npx skills add neo4j-contrib/gds-agent -a claude-code`.
