# OpenAI Codex

## Tools: MCP server

1. Prerequisite: [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.
2. Either run:
   ```bash
   codex mcp add neo4j-gds \
     --env NEO4J_URI=neo4j://localhost:7687 \
     --env NEO4J_USERNAME=neo4j \
     --env NEO4J_PASSWORD=your-password \
     -- uvx gds-agent
   ```
   or add to `~/.codex/config.toml`:
   ```toml
   [mcp_servers.neo4j-gds]
   command = "uvx"
   args = ["gds-agent"]

   [mcp_servers.neo4j-gds.env]
   NEO4J_URI = "neo4j://localhost:7687"
   NEO4J_USERNAME = "neo4j"
   NEO4J_PASSWORD = "your-password"
   ```
   Add `AURA_API_CLIENT_ID` / `AURA_API_CLIENT_SECRET` entries for Aura Graph Analytics session mode.
3. Verify: `codex mcp list` shows `neo4j-gds`.

## Knowledge: skill

Codex reads Agent Skills from `.agents/skills/` (repo) and `~/.agents/skills/` (user). Install ours with:

```bash
npx skills add neo4j-contrib/gds-agent -a codex
```

Verify inside Codex with `/skills` — `neo4j-graph-analysis` should be listed.
