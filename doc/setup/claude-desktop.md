# Claude Desktop

Two artifacts: the `.mcpb` bundle provides the tools, the skill zip provides the how-to knowledge. Install both.

## Tools: MCPB bundle

1. Prerequisite: none — the bundle uses Claude Desktop's managed `uv` runtime.
2. Download `gds-agent-<version>.mcpb` from the [GitHub releases page](https://github.com/neo4j-contrib/gds-agent/releases).
3. Double-click the file (or drag it into Claude Desktop → Settings → Extensions) and click **Install**.
4. Fill in the configuration form: Neo4j URI, username, password (stored in the OS keychain), optional database name, and optional Aura API credentials for Aura Graph Analytics session mode.
5. Verify: in a new chat, the tools menu should list `gds-agent` tools such as `count_nodes`.

## Knowledge: skill upload

1. Prerequisite: Settings → Capabilities → enable **Code execution and file creation** (skills require it). On Team/Enterprise an admin must enable skills for the organization first.
2. Download `neo4j-graph-data-scientist-skill-<version>.zip` from the same release.
3. Settings → **Customize** → **Skills** → **+** → upload the zip.
4. Toggle the skill on. Verify by asking a graph question — the response should follow the schema → project → algorithm workflow.

## Manual config alternative

Instead of the `.mcpb`, you can add the server to `claude_desktop_config.json` by hand (use the absolute path from `which uvx` as the `command`):

```json
{
  "mcpServers": {
    "neo4j-gds": {
      "command": "/opt/homebrew/bin/uvx",
      "args": ["gds-agent"],
      "env": {
        "NEO4J_URI": "neo4j://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "<your-password>"
      }
    }
  }
}
```
