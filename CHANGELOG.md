# Changelog - [1.0.0] - yyyy-MM-dd


### Breaking Changes
1. Added new graph projection tools: project_graph_cypher, drop_graph and list_graphs. 
As a result, all graph projection related parameters (e.g nodeLabels, relTypes) in all algorithms are removed. 
Instead, all algorithm tools now accepte a graphName required parameter.
This allows the LLMs to use Cypher project to manage a catalog of projected graphs and use different algorithm tools on different graphs.

### New Features
1. Add new maxflow path algorithm tool.

### Bug Fixes

### Other Changes

