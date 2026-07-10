# Cursor

## Tools: MCP server

One-click (then replace `YOUR_PASSWORD` in Cursor's MCP settings):

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](cursor://anysphere.cursor-deeplink/mcp/install?name=neo4j-gds&config=eyJjb21tYW5kIjogInV2eCIsICJhcmdzIjogWyJnZHMtYWdlbnQiXSwgImVudiI6IHsiTkVPNEpfVVJJIjogIm5lbzRqOi8vbG9jYWxob3N0Ojc2ODciLCAiTkVPNEpfVVNFUk5BTUUiOiAibmVvNGoiLCAiTkVPNEpfUEFTU1dPUkQiOiAiWU9VUl9QQVNTV09SRCIsICJORU80Sl9EQVRBQkFTRSI6ICJuZW80aiJ9fQ==)

Or manually in `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):

```json
{
  "mcpServers": {
    "neo4j-gds": {
      "command": "uvx",
      "args": ["gds-agent"],
      "env": {
        "NEO4J_URI": "neo4j://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). Verify under Cursor Settings → MCP: `neo4j-gds` should show its tools.

## Knowledge: skill

```bash
npx skills add neo4j-contrib/gds-agent -a cursor
```
