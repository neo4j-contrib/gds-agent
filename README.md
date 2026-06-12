# GDS Agent

Neither LLMs nor any existing toolings (MCP Servers) are capable of complex reasoning on graphs at the moment.

This MCP Server includes toolings from Neo4j Graph Data Science (GDS) library, which allows you to run all common graph algorithms, node embeddings (FastRP, Node2Vec, HashGNN, GraphSAGE), and machine learning pipelines (node classification, link prediction, node regression).

Once the server is running, you are able to **ask any graph questions about your Neo4j graph** and get answers. LLMs equipped with GDS agent can decide and accurately execute the appropriate parameterised graph algorithms over the graph you have in your Neo4j database.

An example where an LLM with GDS Agent is able to pick shortest path and Yen's algorithm to answer my question about travel plan:
![gds-agent-example](doc/gds-agent-london-underground-example.png)

# Table of Contents

## For Users
- [Use GDS Agent](#use-gds-agent)

## For Developers
- [Example dataset](#example-dataset)
- [Start the server](#start-the-server)
- [How to contribute](#how-to-contribute)
- [Feature request and bug reports](#feature-request-and-bug-reports)
- [Additional resource](#additional-resources)

# Use GDS Agent
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

By default the server uses STDIO transport for local MCP clients. For HTTP-native clients, run the server with streamable HTTP:
```bash
gds-agent --transport http --host 127.0.0.1 --port 8000 --path /mcp
```
The equivalent environment variables are `GDS_AGENT_TRANSPORT`, `GDS_AGENT_HOST`, `GDS_AGENT_PORT`, and `GDS_AGENT_PATH`. The Neo4j MCP-style `NEO4J_TRANSPORT` and `NEO4J_MCP_SERVER_*` names are also supported.

## GDS Aura Graph Analytics (sessions)
The server detects whether the connected Neo4j has the GDS plugin installed or whether to use a GDS Aura Graph Analytics session. Detection runs `gds.session.list()` on startup; if it succeeds, session mode is used and graph projections fall back to `gds.graph.project.remote`.

Session mode requires Aura API credentials. Add them to the same `.env` file (or `env` block in your MCP config) used for the database credentials:
```bash
AURA_API_CLIENT_ID=...
AURA_API_CLIENT_SECRET=...
# optional, needed if your Aura API client has access to multiple projects
AURA_API_PROJECT_ID=...
# optional
SESSION_MEMORY_GB=8
SESSION_NAME=mcp_gds_session
SESSION_TTL_HOURS=24
```
The session is created lazily on the first algorithm/projection call. Three extra tools become available in session mode: `list_sessions`, `delete_session`, and `recreate_session` (the last is useful to bump memory after an OOM).


# Example dataset
To load the London underground example dataset:
1. Fork and clone the repository
2. Install necessary packages in your python environment with `pip install -r requirements.txt`
3. Install the Neo4j database with GDS plugin:
   Download the Neo4j Desktop from [Neo4j Download Center](https://neo4j.com/download/)
   Install the GDS plugin from the Neo4j Desktop
   Create a new database and start it
4. Populate .env file with necessary credentials:
   ```bash
   NEO4J_URI=bolt://localhost:7687  # or your database URI
   NEO4J_USERNAME=neo4j  # or your db username
   NEO4J_PASSWORD=your_password
   ```
5. Load the London Underground dataset with the following command:
   ```bash
   python import_data.py --undirected
   ```
Connect to your DB and querying the graph from [Neo4j workspace](https://workspace-preview.neo4j.io/workspace/), 
you should see:
![London Underground Graph](dataset/london-underground-graph.png)


# Start the server for dev
1. When inside the `/mcp_server` directory, run `uv sync --dev` and run `uv run gds-agent` to start the MCP server standalone, or run `claude` to start claude-cli with the agent.


# How to contribute
Open a pull request from a branch of your forked repository into the main branch of this repo, for example `mygithubid:add-new-algo -> neo4j-contrib:main`.

The CI build in github action requires all codestyle checks and tests to pass.

To run and fix codestyle checks locally, in the `/mcp_server` directory, run:
```bash
uv sync --dev
```
to setup the python environment. And then,
```bash
uv run pytest tests -v -s
uv run ruff check
uv run ruff format
```
for all tests and codestyle fixes.

# Feature request and bug reports
To report a bug or a new feature request, raise an issue.
If it is a bug, include the full stacktrace and errors.
When available, attach relevant logs in `mcp_server_neo4j_gds.log`. This file is located inside the `/mcp_server/src_mcp_server_neo4j_gds` directory if the gds agent is running from source, or inside the logging path for Claude (e.g `/Library/Logs/Claude` for Claude Desktop on Mac). Include relevant minimal dataset that can be used to reproduce the issue if possible.

# Additional resources
The GDS agent can be used with other MCP servers, such as those that provide additional Neo4j toolings: https://github.com/neo4j-contrib/mcp-neo4j

Arxiv paper including details about the architecture and benchmark results: https://arxiv.org/abs/2508.20637.
