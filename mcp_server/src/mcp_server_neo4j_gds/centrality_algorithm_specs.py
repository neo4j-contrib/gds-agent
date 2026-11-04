from mcp import types

centrality_tool_definitions = [
    types.Tool(
        name="article_rank",
        description="""Calculate ArticleRank for nodes in the graph.
    ArticleRank is similar to PageRank but normalizes by the number of outgoing references.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node to filter return the ArticleRank for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "damping_factor": {
                    "type": "number",
                    "description": "The damping factor of the ArticleRank calculation. Must be in [0, 1).",
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum number of iterations for ArticleRank",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Minimum change in scores between iterations.",
                },
                "relationship_weight_property": {
                    "type": "string",
                    "description": "Property of the relationship to use for weighting. If not specified, all relationships are treated equally.",
                },
                "source_nodes": {
                    "description": "The nodes to use for computing Personalized Article Rank.",
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                },
                "scaler": {
                    "type": "string",
                    "description": "The name of the scaler applied for the final scores. "
                    "Supported values are None, MinMax, Max, Mean, Log, and StdScore. "
                    "To apply scaler-specific configuration, use the Map syntax: {scaler: 'name', ...}.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="articulation_points",
        description="Find all the articulation points. Given a graph, an articulation point is a node whose removal increases the number of connected components in the graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="betweenness_centrality",
        description="""Calculate betweenness centrality for nodes in the graph.  Betweenness centrality is a measure of the number of times a node acts as a bridge along the shortest path between two other nodes.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter betweenness centrality results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "sampling_size": {
                    "type": "integer",
                    "description": "The number of source nodes to consider for computing centrality scores.",
                },
                "relationship_weight_property": {
                    "type": "string",
                    "description": "Property of the relationship to use for weighting. If not specified, all relationships are treated equally.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="bridges",
        description="""Find all the bridges in the graph. A bridge is an edge whose removal increases the number of connected components in the graph.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="CELF",
        description="""Calculate the Cost-Effective Lazy Forward (CELF) algorithm for influence maximization in the graph.
        For a given k, the algorithm finds the set of k nodes that maximize the expected spread of influence in the network.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "seed_set_size": {
                    "type": "integer",
                    "description": "The number of nodes that maximize the expected spread in the network.",
                },
                "monte_carlo_simulations": {
                    "type": "integer",
                    "description": "The number of Monte Carlo simulations to run for estimating the expected spread.",
                },
                "propagation_probability": {
                    "type": "number",
                    "description": "The probability of propagating influence from a node to its neighbors.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
            },
            "required": ["graph_name", "seed_set_size"],
        },
    ),
    types.Tool(
        name="closeness_centrality",
        description="""Calculate closeness centrality for all nodes in the graph.
        The closeness centrality of a node measures its average farness (inverse distance) to all other nodes.
        Nodes with a high closeness score have the shortest distances to all other nodes.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter closeness centrality results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "use_wasserman_faust": {
                    "type": "boolean",
                    "description": "If true, uses the Wasserman-Faust formula for closeness centrality. ",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="degree_centrality",
        description="""Calculate degree centrality for all nodes in the graph""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter degree centrality results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "orientation": {
                    "type": "string",
                    "description": "The orientation used to compute node degrees. Supported orientations are NATURAL (for out-degree), REVERSE (for in-degree) and UNDIRECTED (for both in-degree and out-degree). If the projection used undirectedRelationshipTypes, each relationship is already stored in both directions, so UNDIRECTED counts every neighbor twice. Use NATURAL on that projection, or divide the score by 2.",
                },
                "relationship_weight_property": {
                    "type": "string",
                    "description": "Property of the relationship to use for weighting. If not specified, all relationships are treated equally.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="eigenvector_centrality",
        description="""Calculate eigenvector centrality for all nodes in the graph.
    Eigenvector Centrality is an algorithm that measures the transitive influence of nodes.
    Relationships originating from high-scoring nodes contribute more to the score of a node than connections from low-scoring nodes.
    A high eigenvector score means that a node is connected to many nodes who themselves have high scores.
    The algorithm computes the eigenvector associated with the largest absolute eigenvalue.
    To compute that eigenvalue, the algorithm applies the power iteration approach.
    Within each iteration, the centrality score for each node is derived from the scores of its incoming neighbors.
    In the power iteration method, the eigenvector is L2-normalized after each iteration, leading to normalized results by default.
    The PageRank algorithm is a variant of Eigenvector Centrality with an additional jump probability.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter eigenvector centrality results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum number of iterations for Eigenvector Centrality",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Minimum change in scores between iterations. If all scores change less than the tolerance value the result is considered stable and the algorithm returns.",
                },
                "relationship_weight_property": {
                    "type": "string",
                    "description": "Property of the relationship to use for weighting. If not specified, all relationships are treated equally.",
                },
                "source_nodes": {
                    "description": "The nodes to use for computing Personalized Eigenvector Centrality.",
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                },
                "scaler": {
                    "type": "string",
                    "description": "The name of the scaler applied for the final scores. "
                    "Supported values are None, MinMax, Max, Mean, Log, and StdScore. "
                    "To apply scaler-specific configuration, use the Map syntax: {scaler: 'name', ...}.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="pagerank",
        description="""Calculate PageRank for all nodes in the graph""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter PageRank results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "damping_factor": {
                    "type": "number",
                    "description": "The damping factor of the Page Rank calculation. Must be in [0, 1).",
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum number of iterations for PageRank",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Minimum change in scores between iterations. If all scores change less than the tolerance value the result is considered stable and the algorithm returns.",
                },
                "source_nodes": {
                    "description": "The nodes to use for computing Personalized PageRank.",
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="harmonic_centrality",
        description="""Calculate harmonic centrality for all nodes in the graph.
        Harmonic centrality is a variant of closeness centrality that is more robust to disconnected graphs.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write the algorithm results to.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter harmonic centrality results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="HITS",
        description="""Calculate HITS (Hyperlink-Induced Topic Search) scores for nodes in the graph.
        The Hyperlink-Induced Topic Search (HITS) is a link analysis algorithm that rates nodes based on two scores, a hub score and an authority score.
        The authority score estimates the importance of the node within the network. The hub score estimates the value of its relationships to other nodes.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Create a graph first using project_graph_cypher.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns results as a table, 'mutate' writes results to the in-memory graph as node properties. Default is 'stream'.",
                },
                "mutate_property": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. Used as a prefix for the two properties written: {mutateProperty}_auth and {mutateProperty}_hub.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "List of node names to filter HITS results for.",
                },
                "node_identifier_property": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "hits_iterations": {
                    "type": "integer",
                    "description": "The number of hits iterations to run. The number of pregel iterations will be equal to hitsIterations * 4.",
                },
                "partitioning": {
                    "type": "string",
                    "enum": ["AUTO", "RANGE", "DEGREE"],
                    "description": "The partitioning scheme used to divide the work between threads. Available options are AUTO, RANGE, DEGREE.",
                },
            },
            "required": ["graph_name"],
        },
    ),
]
