from mcp import types

from .common_specs import (
    GRAPH_NAME_DESCRIPTION,
    MAX_ITERATIONS_DESCRIPTION,
    MODE_DESCRIPTION,
    MUTATE_NODE_PROPERTY_DESCRIPTION,
    NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
    NODES_FILTER_DESCRIPTION,
    PARTITIONING_DESCRIPTION,
    RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
    SCALER_DESCRIPTION,
    TOLERANCE_DESCRIPTION,
)

centrality_tool_definitions = [
    types.Tool(
        name="article_rank",
        description="Calculate ArticleRank centrality for nodes (a PageRank variant that lowers the influence of high-out-degree nodes by normalizing by average out-degree).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "damping_factor": {
                    "type": "number",
                    "description": "Damping factor in [0, 1).",
                },
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "tolerance": TOLERANCE_DESCRIPTION,
                "source_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Bias nodes for Personalized ArticleRank (requires node_identifier_property).",
                },
                "scaler": SCALER_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="articulation_points",
        description="Find all articulation points (nodes whose removal increases the number of connected components).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="betweenness_centrality",
        description="Calculate betweenness centrality for nodes (how often a node lies on shortest paths between other nodes).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "sampling_size": {
                    "type": "integer",
                    "description": "Number of source nodes to sample for approximate computation.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="bridges",
        description="Find all bridges in the graph (relationships whose removal increases the number of connected components).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="CELF",
        description="Find seedSetSize nodes that maximize expected influence spread using Cost-Effective Lazy Forward (CELF) influence maximization.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "seed_set_size": {
                    "type": "integer",
                    "description": "Number of seed nodes to select.",
                },
                "monte_carlo_simulations": {
                    "type": "integer",
                    "description": "Number of Monte Carlo simulations to estimate spread.",
                },
                "propagation_probability": {
                    "type": "number",
                    "description": "Probability of influence propagating across a relationship.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "seed_set_size"],
        },
    ),
    types.Tool(
        name="closeness_centrality",
        description="Calculate closeness centrality for nodes (inverse of average shortest-path distance to all reachable nodes).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "use_wasserman_faust": {
                    "type": "boolean",
                    "description": "Use the Wasserman-Faust formula to normalize for disconnected graphs.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="degree_centrality",
        description="Calculate degree centrality (number or weighted sum of incident relationships per node).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "orientation": {
                    "type": "string",
                    "description": "NATURAL (out-degree), REVERSE (in-degree), or UNDIRECTED (both). On an undirected projection, UNDIRECTED counts each neighbor twice; use NATURAL instead.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="eigenvector_centrality",
        description="Calculate eigenvector centrality for nodes (transitive influence via the principal eigenvector using power iteration).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "tolerance": TOLERANCE_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "source_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Bias nodes for Personalized Eigenvector Centrality (requires node_identifier_property).",
                },
                "scaler": SCALER_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="pagerank",
        description="Calculate PageRank centrality for nodes.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "damping_factor": {
                    "type": "number",
                    "description": "Damping factor in [0, 1).",
                },
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "tolerance": TOLERANCE_DESCRIPTION,
                "source_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Bias nodes for Personalized PageRank (requires node_identifier_property).",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="harmonic_centrality",
        description="Calculate harmonic centrality for nodes (a closeness centrality variant that naturally handles disconnected graphs by summing inverse distances).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="HITS",
        description="Calculate HITS hub and authority scores for nodes; mutate mode writes auth and hub node properties.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "hits_iterations": {
                    "type": "integer",
                    "description": "Number of HITS iterations to run (total Pregel iterations = hitsIterations * 4).",
                },
                "partitioning": PARTITIONING_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
]
