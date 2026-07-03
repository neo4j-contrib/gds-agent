# claude.ai (web)

claude.ai supports the skill, but it cannot start local MCP servers — tool access requires a remote MCP endpoint.

## Skill upload

Same flow as Claude Desktop: enable code execution (Settings → Capabilities), then Settings → **Customize** → **Skills** → upload `neo4j-graph-analysis-skill-<version>.zip` from the [releases page](https://github.com/neo4j-contrib/gds-agent/releases). Skills are per-user; Team/Enterprise admins can provision them org-wide.

## Tools (remote MCP)

To use the tools from claude.ai you must expose the server over HTTP where claude.ai can reach it, then add it as a custom connector (Settings → Connectors):

```bash
gds-agent --transport http --host 0.0.0.0 --port 8000 --path /mcp
```

The server has no built-in authentication — only expose it behind a gateway you control (VPN, reverse proxy with auth). For local-only experimentation, prefer Claude Desktop or Claude Code instead.
