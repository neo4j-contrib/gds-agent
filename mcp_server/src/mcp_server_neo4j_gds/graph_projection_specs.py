from mcp import types

graph_projection_tool_definitions = [
    types.Tool(
        name="project_graph_cypher",
        description="""Project a graph using a custom Cypher query for use with GDS algorithms.

The graph will persist in memory until explicitly dropped with drop_graph.
Use this to create a graph projection, then reference it by name when running algorithms.

Plugin (on-prem) mode — call gds.graph.project() with $graph_name as the first argument:
MATCH (n:Station)-[r:CONNECTED]->(m:Station)
RETURN gds.graph.project(
    $graph_name,
    n,
    m,
    {
        sourceNodeLabels: labels(n),
        targetNodeLabels: labels(m),
        relationshipType: type(r),
        relationshipProperties: {distance: toFloat(r.distance)}
    }
)

Aura Graph Analytics (session) mode — call gds.graph.project.remote() with NO graph_name argument:
MATCH (n:Station)-[r:CONNECTED]->(m:Station)
RETURN gds.graph.project.remote(
    n,
    m,
    {
        sourceNodeLabels: labels(n),
        targetNodeLabels: labels(m),
        relationshipType: type(r),
        relationshipProperties: {distance: toFloat(r.distance)}
    }
)

References:
- Plugin: https://neo4j.com/docs/graph-data-science/current/management-ops/graph-creation/graph-project-cypher-projection/
- Sessions: https://neo4j.com/docs/graph-data-science-client/current/aura-graph-analytics/#_projecting_graphs_into_a_gds_session
""",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Unique name for the projected graph (e.g., 'my_graph', 'station_network'). This name will be used to reference the graph in algorithm tools.",
                },
                "cypherQuery": {
                    "type": "string",
                    "description": "Cypher query that matches nodes and relationships, then returns the graph projection call. In plugin mode, call gds.graph.project() with $graph_name as the first argument. In Aura session mode, call gds.graph.project.remote() with exactly three arguments: source node, target node, and data config; do not pass graph name or a fourth config argument.",
                },
            },
            "required": ["graphName", "cypherQuery"],
        },
    ),
    types.Tool(
        name="drop_graph",
        description="""Drop a projected graph from memory.

This frees up memory and removes the graph projection. The graph must be dropped before a new graph with the same name can be created.
This does not affect the underlying data in the Neo4j database - only the in-memory projection.
""",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the graph to drop. This should be the name used when projecting the graph with project_graph_cypher.",
                }
            },
            "required": ["graphName"],
        },
    ),
    types.Tool(
        name="list_graphs",
        description="""List all projected graphs currently in memory with their metadata.

Returns information about each graph including node count, relationship count, memory usage, and schema.
Use this to see what graphs are available for running algorithms on.
""",
        inputSchema={"type": "object", "properties": {}},
    ),
    types.Tool(
        name="get_graph_info",
        description="""Inspect one projected graph in the GDS graph catalog.

Returns graph object metadata including counts, labels, relationship types, projected properties, degree distribution, density, memory usage, configuration, and timestamps.
Use this before running mutate/stream algorithms to understand the graph schema and available in-memory properties.
""",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to inspect.",
                }
            },
            "required": ["graphName"],
        },
    ),
    types.Tool(
        name="stream_node_properties",
        description="""Stream node properties from a projected GDS graph.

Use this after running algorithms in mutate mode to inspect mutated node properties, or to inspect properties included during graph projection. This reads from the in-memory GDS graph, not directly from Neo4j, except for optional dbNodeProperties.
""",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph.",
                },
                "nodeProperties": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Projected node property or properties to stream, such as a mutateProperty written by an algorithm.",
                },
                "nodeLabels": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Optional node label or labels to stream from. Defaults to all labels.",
                },
                "dbNodeProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional Neo4j database node properties to include alongside projected properties, such as name or identifier fields.",
                },
            },
            "required": ["graphName", "nodeProperties"],
        },
    ),
    types.Tool(
        name="stream_relationship_properties",
        description="""Stream relationship properties from a projected GDS graph.

Use this after mutate mode algorithms that write relationship properties, or to inspect relationship properties included during projection.
""",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph.",
                },
                "relationshipProperties": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Projected relationship property or properties to stream.",
                },
                "relationshipTypes": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Optional relationship type or types to stream from. Defaults to all types.",
                },
            },
            "required": ["graphName", "relationshipProperties"],
        },
    ),
    types.Tool(
        name="stream_relationships",
        description="""Stream relationship topology from a projected GDS graph.

Returns source node id, target node id, and relationship type rows from the in-memory graph. Use this to inspect projected topology by relationship type.
""",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph.",
                },
                "relationshipTypes": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Optional relationship type or types to stream. Defaults to all types.",
                },
            },
            "required": ["graphName"],
        },
    ),
]
