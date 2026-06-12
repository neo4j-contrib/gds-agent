# Changelog - [1.0.0] - yyyy-MM-dd


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

### Bug Fixes
1. Limit oversized tool outputs, post-process only returned rows, and batch node lookups to keep stream results from making the MCP server unresponsive.

### Other Changes

