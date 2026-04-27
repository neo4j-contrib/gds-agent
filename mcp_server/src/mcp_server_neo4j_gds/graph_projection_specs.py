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
                    "description": "Cypher query that calls gds.graph.project(). Must use $graph_name as the graph name parameter. The query should match nodes and relationships, then return the gds.graph.project() call with appropriate configuration.",
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
]
