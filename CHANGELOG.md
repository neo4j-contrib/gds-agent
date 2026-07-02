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
6. Add node embedding tools: fast_rp, node2vec, hashgnn, graph_sage_train and graph_sage_predict.
7. Add ML pipeline tools that train and apply models via the GDS model catalog: train_node_classification_model, predict_node_classification, train_link_prediction_model, predict_link_prediction, train_node_regression_model and predict_node_regression.
8. Add model catalog tools: list_models and drop_model.

### Bug Fixes
1. Limit oversized tool outputs, post-process only returned rows, and batch node lookups to keep stream results from making the MCP server unresponsive.
2. Add regex checks in query parameters to avoid query injection for path algorithm tools.

### Other Changes

