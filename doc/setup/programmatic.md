# Programmatic use (build your own agent)

The server is a standard MCP stdio/HTTP server, consumable from any agent framework. The skill is a directory of markdown; frameworks without native skill support can inject `skills/neo4j-graph-data-scientist/SKILL.md` as system-prompt text.

## Claude Agent SDK (Python)

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    mcp_servers={
        "neo4j-gds": {
            "command": "uvx",
            "args": ["gds-agent"],
            "env": {"NEO4J_URI": "neo4j://localhost:7687",
                    "NEO4J_USERNAME": "neo4j",
                    "NEO4J_PASSWORD": "..."},
        }
    },
    # Loads skills from <cwd>/.claude/skills — copy or `npx skills add` ours there
    setting_sources=["project"],
)
```

## LangChain / LangGraph

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "neo4j_gds": {
        "transport": "stdio",
        "command": "uvx",
        "args": ["gds-agent"],
        "env": {"NEO4J_URI": "neo4j://localhost:7687",
                "NEO4J_USERNAME": "neo4j",
                "NEO4J_PASSWORD": "..."},
    }
})
tools = await client.get_tools()
```

## OpenAI Agents SDK

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(params={
    "command": "uvx",
    "args": ["gds-agent"],
    "env": {"NEO4J_URI": "neo4j://localhost:7687",
            "NEO4J_USERNAME": "neo4j",
            "NEO4J_PASSWORD": "..."},
}) as server:
    agent = Agent(name="graph-analyst", mcp_servers=[server],
                  instructions=open("skills/neo4j-graph-data-scientist/SKILL.md").read())
```

## HTTP transport

For frameworks preferring HTTP, run `gds-agent --transport http --port 8000 --path /mcp` and point a streamable-HTTP MCP client at `http://127.0.0.1:8000/mcp`.
