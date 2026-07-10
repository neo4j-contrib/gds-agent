# VS Code / GitHub Copilot

## Tools: MCP server

One-click (then edit the password in the generated config):

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=neo4j-gds&config=%7B%22command%22%3A%20%22uvx%22%2C%20%22args%22%3A%20%5B%22gds-agent%22%5D%2C%20%22env%22%3A%20%7B%22NEO4J_URI%22%3A%20%22neo4j%3A//localhost%3A7687%22%2C%20%22NEO4J_USERNAME%22%3A%20%22neo4j%22%2C%20%22NEO4J_PASSWORD%22%3A%20%22YOUR_PASSWORD%22%2C%20%22NEO4J_DATABASE%22%3A%20%22neo4j%22%7D%7D)

Or the secure manual setup — `.vscode/mcp.json` in your workspace, with the password prompted and never stored in plaintext:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "neo4j-password",
      "description": "Neo4j password",
      "password": true
    }
  ],
  "servers": {
    "neo4j-gds": {
      "command": "uvx",
      "args": ["gds-agent"],
      "env": {
        "NEO4J_URI": "neo4j://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "${input:neo4j-password}"
      }
    }
  }
}
```

Note VS Code uses a `servers` key (not `mcpServers`). Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). Verify: agent mode → tools icon → `neo4j-gds` listed.

## Knowledge: skill

Copilot reads Agent Skills from `.github/skills/`, `.agents/skills/` (project) or `~/.copilot/skills/`, `~/.agents/skills/` (personal):

```bash
npx skills add neo4j-contrib/gds-agent -a copilot
```
