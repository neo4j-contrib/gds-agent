from mcp import types

from .common_specs import (
    GRAPH_NAME_SCHEMA,
    MAX_ITERATIONS_SCHEMA,
    MODE_SCHEMA,
    MUTATE_REL_PROPERTY_SCHEMA,
    MUTATE_REL_TYPE_SCHEMA,
    NODE_IDENTIFIER_PROPERTY_SCHEMA,
    RELATIONSHIP_WEIGHT_PROPERTY_SCHEMA,
)

_NODE_FILTER_SCHEMA = {
    "anyOf": [
        {
            "type": "array",
            "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
        },
        {"type": "string"},
        {"type": "number"},
    ],
}

similarity_tool_definitions = [
    types.Tool(
        name="node_similarity",
        description="Compute pairwise node similarity based on shared neighbors (JACCARD, OVERLAP, or COSINE). Use k_nearest_neighbors for similarity based on node properties.",
        inputSchema={
            "type": "object",
            "properties": {
                "source_node_filter": {
                    **_NODE_FILTER_SCHEMA,
                    "description": "Source label, or identifier value(s) when node_identifier_property is set.",
                },
                "target_node_filter": {
                    **_NODE_FILTER_SCHEMA,
                    "description": "Target label, or identifier value(s) when node_identifier_property is set.",
                },
                "similarity_cutoff": {
                    "type": "number",
                    "description": "Minimum similarity score in [0, 1] to include in results.",
                },
                "degree_cutoff": {
                    "type": "integer",
                    "description": "Minimum node degree (>= 1) required for comparison.",
                },
                "upper_degree_cutoff": {
                    "type": "integer",
                    "description": "Maximum node degree (>= 1) allowed for comparison.",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Maximum number of highest-scoring neighbors returned per node (>= 1).",
                },
                "bottom_k": {
                    "type": "integer",
                    "description": "Maximum number of lowest-scoring neighbors returned per node (>= 1).",
                },
                "top_n": {
                    "type": "integer",
                    "description": "Global limit on highest-scoring node pairs returned across the graph (0 = unlimited).",
                },
                "bottom_n": {
                    "type": "integer",
                    "description": "Global limit on lowest-scoring node pairs returned across the graph (0 = unlimited).",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_SCHEMA,
                "similarity_metric": {
                    "type": "string",
                    "enum": ["JACCARD", "OVERLAP", "COSINE"],
                    "description": "Similarity metric to compute.",
                },
                "use_components": {
                    "anyOf": [{"type": "boolean"}, {"type": "string"}],
                    "description": "true computes WCC first; false compares all nodes; a string names a precomputed component node property.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_SCHEMA,
                "graph_name": GRAPH_NAME_SCHEMA,
                "mode": MODE_SCHEMA,
                "mutate_property": MUTATE_REL_PROPERTY_SCHEMA,
                "mutate_relationship_type": MUTATE_REL_TYPE_SCHEMA,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="k_nearest_neighbors",
        description="Find each node's top_k most similar neighbors based on node properties (ignores existing relationships; use node_similarity for shared-neighbor topology similarity).",
        inputSchema={
            "type": "object",
            "properties": {
                "source_node_filter": {
                    **_NODE_FILTER_SCHEMA,
                    "description": "Source label, or identifier value(s) when node_identifier_property is set.",
                },
                "target_node_filter": {
                    **_NODE_FILTER_SCHEMA,
                    "description": "Target label, or identifier value(s) when node_identifier_property is set.",
                },
                "node_properties": {
                    "type": "object",
                    "description": "Map of node property names to similarity metrics, e.g. {embedding: 'COSINE', age: 'DEFAULT', tags: 'OVERLAP'}.",
                },
                "top_k": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of nearest neighbors to find per node (>= 1).",
                },
                "sample_rate": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "maximum": 1,
                    "description": "Fraction of neighbors sampled per iteration in (0, 1] (default: 0.5).",
                },
                "delta_threshold": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "maximum": 1,
                    "description": "Early stopping threshold in (0, 1] on the fraction of neighbor updates.",
                },
                "max_iterations": MAX_ITERATIONS_SCHEMA,
                "random_joins": {
                    "type": "integer",
                    "description": "Number of random neighbor connection attempts per node per iteration.",
                },
                "initial_sampler": {
                    "type": "string",
                    "enum": ["uniform", "random_walk"],
                    "description": "Method to sample initial k neighbors per node.",
                },
                "similarity_cutoff": {
                    "type": "number",
                    "description": "Minimum similarity threshold to retain a neighbor.",
                },
                "perturbation_rate": {
                    "type": "number",
                    "description": "Probability of replacing the least similar neighbor with an equally similar candidate.",
                },
                "seed_target_nodes": {
                    "type": "boolean",
                    "description": "Seed initial candidates from target_node_filter to avoid empty results (requires target_node_filter).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_SCHEMA,
                "graph_name": GRAPH_NAME_SCHEMA,
                "mode": MODE_SCHEMA,
                "mutate_property": MUTATE_REL_PROPERTY_SCHEMA,
                "mutate_relationship_type": MUTATE_REL_TYPE_SCHEMA,
            },
            "required": ["node_properties", "graph_name"],
        },
    ),
]
