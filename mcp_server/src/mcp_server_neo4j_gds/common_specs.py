GRAPH_NAME_SCHEMA = {
    "type": "string",
    "description": "Name of an in-memory projected graph; inspect with list_graphs or create with project_graph_cypher.",
}

MODE_SCHEMA = {
    "type": "string",
    "enum": ["stream", "mutate"],
    "description": "Execution mode (default: 'stream').",
}

MUTATE_NODE_PROPERTY_SCHEMA = {
    "type": "string",
    "description": "Node property name to write results to (required when mode is 'mutate').",
}

MUTATE_REL_PROPERTY_SCHEMA = {
    "type": "string",
    "description": "Relationship property name to write results to (required when mode is 'mutate').",
}

MUTATE_REL_TYPE_SCHEMA = {
    "type": "string",
    "description": "Relationship type for new relationships written to the projected graph (required when mode is 'mutate').",
}

NODE_IDENTIFIER_PROPERTY_SCHEMA = {
    "type": "string",
    "pattern": "^[A-Za-z_][A-Za-z0-9_]*$",
    "description": "Node property used for readable identifiers; inspect with get_node_properties_keys or get_neo4j_schema.",
}

NODES_FILTER_SCHEMA = {
    "type": "array",
    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
    "description": "List of node identifiers to filter results (requires node_identifier_property).",
}

RELATIONSHIP_WEIGHT_PROPERTY_SCHEMA = {
    "type": "string",
    "description": "Relationship property to use as weights (unweighted if omitted).",
}

MAX_ITERATIONS_SCHEMA = {
    "type": "integer",
    "description": "Maximum number of iterations to run.",
}

TOLERANCE_SCHEMA = {
    "type": "number",
    "description": "Minimum change in scores between iterations for early convergence.",
}

MIN_COMMUNITY_SIZE_SCHEMA = {
    "type": "integer",
    "description": "Only return nodes in communities at least this size.",
}

CONSECUTIVE_IDS_SCHEMA = {
    "type": "boolean",
    "description": "Whether to map component/community IDs into a consecutive ID space.",
}

SEED_PROPERTY_SCHEMA = {
    "type": "string",
    "description": "Node property defining initial numeric community/component IDs.",
}

SOURCE_NODE_SCHEMA = {
    "anyOf": [{"type": "string"}, {"type": "number"}],
    "description": "Identifier of the source node.",
}

TARGET_NODE_SCHEMA = {
    "anyOf": [{"type": "string"}, {"type": "number"}],
    "description": "Identifier of the target node.",
}

RANDOM_SEED_SCHEMA = {
    "type": "integer",
    "description": "Random seed; improves repeatability, but parallel algorithms may not be fully deterministic.",
}

PARTITIONING_SCHEMA = {
    "type": "string",
    "enum": ["AUTO", "RANGE", "DEGREE"],
    "description": "Partitioning scheme used to divide work between threads.",
}

SCALER_SCHEMA = {
    "anyOf": [
        {
            "type": "string",
            "enum": ["None", "MinMax", "Max", "Mean", "Log", "StdScore"],
        },
        {
            "type": "object",
            "properties": {"scaler": {"type": "string"}},
            "required": ["scaler"],
        },
    ],
    "description": "Score scaler name or config map {scaler: 'name', ...}.",
}
