# Changelog - [1.0.0] - 2026-07-10


### Breaking Changes
1. Added new graph projection tools: project_graph_cypher, drop_graph and list_graphs. 
As a result, all graph projection related parameters (e.g nodeLabels, relTypes) in all algorithms are removed. 
Instead, all algorithm tools now accepte a graphName required parameter.
This allows the LLMs to use Cypher project to manage a catalog of projected graphs and use different algorithm tools on different graphs.

### New Features
1. Add new maxflow path algorithm tool.
2. Support mutate mode for all algorithm tools.
3. Support GDS sessions (Aura Graph Analytics) on Aura DB.
4. Support HTTP transport mode.
5. Add graph accessor tools: get_graph_info, stream_node_properties, stream_relationship_properties and stream_relationships.
6. Add node embedding tools: fast_rp, node2vec, hashgnn, graph_sage_train and graph_sage_predict.
7. Add ML pipeline tools that train and apply models via the GDS model catalog: train_node_classification_model, predict_node_classification, train_link_prediction_model, predict_link_prediction, train_node_regression_model and predict_node_regression.
8. Add model catalog tools: list_models and drop_model.
9. Support multiple explicitly managed GDS sessions per server: sessions are created with the create_session tool, project_graph_cypher requires a sessionName in session mode, and tool calls are routed to the right session by graphName.
10. Add the neo4j-graph-data-scientist Agent Skill (skills/) teaching agents the projection, algorithm-selection, and session workflow, following the agentskills.io open standard.
11. Distribute as a Claude Code plugin and marketplace (.claude-plugin/, mcp.json), a Claude Desktop MCPB bundle plus uploadable skill zip (mcp_server/manifest.json), a Gemini CLI extension (gemini-extension.json), and an MCP registry manifest (server.json), with per-harness setup guides in doc/setup/ and release scaffolding (RELEASING.md, scripts/bump_version.py, validate/release workflows).
12. Bundle the read-only mcp-neo4j-cypher server in the Claude Code plugin and Gemini CLI extension so one install provides GDS algorithms plus Cypher reads with shared credentials.

### Bug Fixes
1. Limit oversized tool outputs, post-process only returned rows, and batch node lookups to keep stream results from making the MCP server unresponsive.
2. Add regex checks in query parameters to avoid query injection for path algorithm tools.
3. Treat empty-string values of optional environment variables (NEO4J_DATABASE, AURA_API_*, SESSION_*) as unset, as injected by harness configuration forms.
4. Read the server version from package metadata instead of a hard-coded constant.
5. Correct the plugin-mode undirected projection guidance to the 5th (configuration) argument of gds.graph.project and show the placement in the tool description example.

### Other Changes
1. Load the example dataset with uv (inline script dependencies in import_data.py) instead of requiring pip install -r requirements.txt.

