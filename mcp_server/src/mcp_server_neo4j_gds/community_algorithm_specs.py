from mcp import types

from .common_specs import (
    CONSECUTIVE_IDS_DESCRIPTION,
    GRAPH_NAME_DESCRIPTION,
    MAX_ITERATIONS_DESCRIPTION,
    MIN_COMMUNITY_SIZE_DESCRIPTION,
    MODE_DESCRIPTION,
    MUTATE_NODE_PROPERTY_DESCRIPTION,
    NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
    NODES_FILTER_DESCRIPTION,
    PARTITIONING_DESCRIPTION,
    RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
    SEED_PROPERTY_DESCRIPTION,
    TOLERANCE_DESCRIPTION,
)

_COMMUNITY_PROPERTY_SCHEMA = {
    "type": "string",
    "description": "Node property holding non-negative integer community IDs.",
}

community_tool_definitions = [
    types.Tool(
        name="conductance",
        description="Calculate the conductance metric (ratio of external to total relationship volume) for each community.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "community_property": _COMMUNITY_PROPERTY_SCHEMA,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "community_property"],
        },
    ),
    types.Tool(
        name="HDBSCAN",
        description="Cluster nodes of varying densities based on a float-array node property using HDBSCAN (assigns noise nodes to a separate cluster).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "node_property": {
                    "type": "string",
                    "description": "Float-array node property used to compute clusters.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "min_cluster_size": {
                    "type": "integer",
                    "description": "Minimum number of nodes in a cluster.",
                },
                "samples": {
                    "type": "integer",
                    "description": "Number of neighbors considered when computing core distances.",
                },
                "leaf_size": {
                    "type": "integer",
                    "description": "Leaf size of the supporting KD-tree.",
                },
            },
            "required": ["graph_name", "node_property"],
        },
    ),
    types.Tool(
        name="k_core_decomposition",
        description="Compute each node's k-core value (largest k such that the node belongs to a maximal subgraph where all nodes have degree >= k). Requires an UNDIRECTED graph projection.",
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
        name="k_1_coloring",
        description="""Greedily assign colors to nodes so adjacent nodes have different colors using as few colors as possible. 
        We use a greedy approximation algorithm, which means the resulting coloring may not be optimal and may not be a valid coloring.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "min_community_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="k_means_clustering",
        description="Cluster nodes into k communities by Euclidean distance on a float-array nodeProperty (ignores relationships).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "node_property": {
                    "type": "string",
                    "description": "Float-array node property used to cluster nodes.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "k": {
                    "type": "integer",
                    "description": "Number of clusters to create.",
                },
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "delta_threshold": {
                    "type": "number",
                    "description": "Early stopping threshold in (0, 1]: stops when the fraction of nodes changing cluster is below this value.",
                },
                "number_of_restarts": {
                    "type": "integer",
                    "description": "Number of K-Means runs with different initial centroids; returns the best clustering.",
                },
                "initial_sampler": {
                    "type": "string",
                    "enum": ["uniform", "kmeans++"],
                    "description": "Method to sample initial k centroids.",
                },
                "seed_centroids": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "Explicit initial centroids (cannot be combined with non-default numberOfRestarts).",
                },
                "compute_silhouette": {
                    "type": "boolean",
                    "description": "Whether to compute silhouette clustering quality scores.",
                },
            },
            "required": ["graph_name", "node_property"],
        },
    ),
    types.Tool(
        name="label_propagation",
        description="Fast community detection that propagates labels across network edges without a predefined objective function.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "node_weight_property": {
                    "type": "string",
                    "description": "Node property containing node weights.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "seed_property": SEED_PROPERTY_DESCRIPTION,
                "consecutive_ids": CONSECUTIVE_IDS_DESCRIPTION,
                "min_community_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="leiden",
        description="Hierarchical community detection that optimizes modularity while guaranteeing well-connected communities (faster and higher quality than louvain). Requires an UNDIRECTED graph projection.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "max_levels": {
                    "type": "integer",
                    "description": "Maximum number of hierarchical clustering levels.",
                },
                "gamma": {
                    "type": "number",
                    "description": "Modularity resolution parameter (higher values produce more, smaller communities).",
                },
                "theta": {
                    "type": "number",
                    "description": "Randomness parameter when refining communities.",
                },
                "tolerance": TOLERANCE_DESCRIPTION,
                "include_intermediate_communities": {
                    "type": "boolean",
                    "description": "Whether to return community assignments from intermediate hierarchical levels.",
                },
                "seed_property": SEED_PROPERTY_DESCRIPTION,
                "min_community_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="local_clustering_coefficient",
        description="Compute the local clustering coefficient for each node (fraction of a node's neighbors that form a triangle). Requires an UNDIRECTED graph projection.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "triangle_count_property": {
                    "type": "string",
                    "description": "Optional node property containing precomputed triangle counts.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="louvain",
        description="Hierarchical community detection that greedily maximizes modularity across condensed graph levels.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "seed_property": SEED_PROPERTY_DESCRIPTION,
                "max_levels": {
                    "type": "integer",
                    "description": "Maximum number of hierarchical clustering levels.",
                },
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "tolerance": TOLERANCE_DESCRIPTION,
                "include_intermediate_communities": {
                    "type": "boolean",
                    "description": "Whether to return community assignments from intermediate hierarchical levels.",
                },
                "consecutive_ids": {
                    "type": "boolean",
                    "description": "Whether to map community IDs into a consecutive ID space (cannot be combined with includeIntermediateCommunities).",
                },
                "min_community_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="modularity_metric",
        description="Calculate modularity scores to evaluate the quality of an existing community assignment.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "community_property": _COMMUNITY_PROPERTY_SCHEMA,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "community_property"],
        },
    ),
    types.Tool(
        name="modularity_optimization",
        description="Detect communities by iteratively reassigning nodes to neighboring communities to maximize modularity.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "tolerance": TOLERANCE_DESCRIPTION,
                "seed_property": SEED_PROPERTY_DESCRIPTION,
                "consecutive_ids": CONSECUTIVE_IDS_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "min_community_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="strongly_connected_components",
        description="Find strongly connected components (maximal node sets where every node can reach every other node via directed paths).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "consecutive_ids": CONSECUTIVE_IDS_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="triangle_count",
        description="Count the number of triangles (3-cliques) each node participates in. Requires an UNDIRECTED graph projection.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "max_degree": {
                    "type": "integer",
                    "description": "Skip nodes with degree above this value (their triangle count is set to -1).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "nodes": NODES_FILTER_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="weakly_connected_components",
        description="Find weakly connected components (maximal sets of nodes connected by paths ignoring relationship direction).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "seed_property": SEED_PROPERTY_DESCRIPTION,
                "threshold": {
                    "type": "number",
                    "description": "Minimum relationship weight required to consider an edge (when relationship_weight_property is set).",
                },
                "consecutive_ids": CONSECUTIVE_IDS_DESCRIPTION,
                "min_component_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="approximate_maximum_k_cut",
        description="""Partition nodes into k disjoint communities to maximize the total weight of relationships crossing between different communities.
        It uses an approximate heuristic algorithm which is a parallelized GRASP style algorithm optionally enhanced (via config) with variable neighborhood search (VNS).""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "k": {
                    "type": "integer",
                    "description": "Number of disjoint communities to partition into.",
                },
                "iterations": {
                    "type": "integer",
                    "description": "Number of GRASP iterations to run before returning the best partition.",
                },
                "vns_max_neighborhood_order": {
                    "type": "integer",
                    "description": "Maximum number of nodes Variable Neighborhood Search (VNS) swaps when perturbing solutions.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "min_community_size": MIN_COMMUNITY_SIZE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="speaker_listener_label_propagation",
        description="""Detect overlapping communities (multiple communities per node) using randomized Speaker-Listener Label Propagation (SLLPA).
        The GDS implementation is based on the SLPA: Uncovering Overlapping Communities in Social Networks via A Speaker-listener Interaction Dynamic Process.
        The algorithm is randomized and will not produce deterministic results. We recommend using a higher number of iterations.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "max_iterations": MAX_ITERATIONS_DESCRIPTION,
                "min_association_strength": {
                    "type": "number",
                    "description": "Minimum association strength required for a community to retain a node.",
                },
                "partitioning": PARTITIONING_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
]
