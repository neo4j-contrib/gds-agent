from mcp import types

from .common_specs import GRAPH_NAME_SCHEMA

graph_projection_tool_definitions = [
    types.Tool(
        name="project_graph_cypher",
        description="""Project an in-memory GDS graph using a Cypher query. Persists until dropped with drop_graph.
Only nodes in result rows are projected; use MATCH (n) OPTIONAL MATCH (n)-[r]->(m) to include degree-0 nodes.
sourceNodeProperties and targetNodeProperties map property names to numeric Cypher expressions.

Plugin (on-prem) mode — call gds.graph.project() with $graph_name as 1st arg, and optional 5th config map for undirected relationships:
MATCH (n:Station)-[r:CONNECTED]->(m:Station)
RETURN gds.graph.project(
    $graph_name, n, m,
    {
        sourceNodeLabels: labels(n),
        targetNodeLabels: labels(m),
        sourceNodeProperties: {latitude: toFloat(n.latitude)},
        targetNodeProperties: {latitude: toFloat(m.latitude)},
        relationshipType: type(r),
        relationshipProperties: {distance: toFloat(r.distance)}
    },
    { undirectedRelationshipTypes: ['CONNECTED'] }
)

Aura session mode — requires session_name (from create_session). Call gds.graph.project.remote(n, m, dataConfig) with NO $graph_name and NO 4th config map; pass undirected types via the undirected_relationship_types tool parameter instead:
MATCH (n:Station)-[r:CONNECTED]->(m:Station)
RETURN gds.graph.project.remote(
    n, m,
    {
        sourceNodeLabels: labels(n),
        targetNodeLabels: labels(m),
        sourceNodeProperties: {latitude: toFloat(n.latitude)},
        targetNodeProperties: {latitude: toFloat(m.latitude)},
        relationshipType: type(r),
        relationshipProperties: {distance: toFloat(r.distance)}
    }
)""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_SCHEMA,
                "cypher_query": {
                    "type": "string",
                    "description": "Cypher projection query returning gds.graph.project($graph_name, ...) in plugin mode or gds.graph.project.remote(...) in session mode.",
                },
                "undirected_relationship_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Aura session mode only: relationship types to project as UNDIRECTED, e.g. ['LINK']. In plugin mode, omit this and set undirectedRelationshipTypes in the 5th argument of gds.graph.project().",
                },
                "session_name": {
                    "type": "string",
                    "description": "Required in Aura session mode (not allowed in plugin mode). Existing GDS session name (from create_session); 'mcp_' is prepended if missing.",
                },
            },
            "required": ["graph_name", "cypher_query"],
        },
    ),
    types.Tool(
        name="drop_graph",
        description="Drop a projected graph from memory to free resources (does not affect the Neo4j database).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_SCHEMA,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="list_graphs",
        description="List all projected graphs currently in memory with node/relationship counts, memory usage, and schema.",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="get_graph_info",
        description="Inspect a projected graph's metadata, counts, labels, relationship types, in-memory properties, degree distribution, and memory usage.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_SCHEMA,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="stream_node_properties",
        description="Stream projected or mutated node properties from an in-memory GDS graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_SCHEMA,
                "node_properties": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Projected or mutated node property name(s) to stream.",
                },
                "node_labels": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Optional node label(s) to filter by (defaults to all labels).",
                },
                "db_node_properties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional Neo4j database node properties to join alongside projected properties (e.g., 'name').",
                },
            },
            "required": ["graph_name", "node_properties"],
        },
    ),
    types.Tool(
        name="stream_relationship_properties",
        description="Stream projected or mutated relationship properties from an in-memory GDS graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_SCHEMA,
                "relationship_properties": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Projected or mutated relationship property name(s) to stream.",
                },
                "relationship_types": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Optional relationship type(s) to filter by (defaults to all types).",
                },
            },
            "required": ["graph_name", "relationship_properties"],
        },
    ),
    types.Tool(
        name="stream_relationships",
        description="Stream relationship topology (source node ID, target node ID, relationship type) from an in-memory GDS graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_SCHEMA,
                "relationship_types": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Optional relationship type(s) to filter by (defaults to all types).",
                },
            },
            "required": ["graph_name"],
        },
    ),
]
