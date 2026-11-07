from mcp import types

from .common_specs import (
    GRAPH_NAME_DESCRIPTION,
    MODE_DESCRIPTION,
    MUTATE_NODE_PROPERTY_DESCRIPTION,
    MUTATE_REL_PROPERTY_DESCRIPTION,
    MUTATE_REL_TYPE_DESCRIPTION,
    NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
    RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
    SOURCE_NODE_DESCRIPTION,
    TARGET_NODE_DESCRIPTION,
)

path_tool_definitions = [
    types.Tool(
        name="find_shortest_path",
        description="Find the shortest path between start_node and end_node using Dijkstra's algorithm (non-negative weights).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "start_node": {
                    "anyOf": [{"type": "string"}, {"type": "number"}],
                    "description": "Identifier of the starting node (use a JSON number if the identifier property is numeric).",
                },
                "end_node": {
                    "anyOf": [{"type": "string"}, {"type": "number"}],
                    "description": "Identifier of the ending node (use a JSON number if the identifier property is numeric).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "relationship_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": [
                "graph_name",
                "start_node",
                "end_node",
                "node_identifier_property",
            ],
        },
    ),
    types.Tool(
        name="delta_stepping_shortest_path",
        description="Compute shortest paths from a source_node to all reachable nodes in parallel using Delta-Stepping (non-negative weights).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "delta": {
                    "type": "number",
                    "description": "Bucket width for grouping nodes with similar tentative distances.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "source_node", "node_identifier_property"],
        },
    ),
    types.Tool(
        name="dijkstra_single_source_shortest_path",
        description="Compute shortest paths from a source_node to all reachable nodes using Dijkstra's algorithm (non-negative weights). Use find_shortest_path for a single target.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "source_node", "node_identifier_property"],
        },
    ),
    types.Tool(
        name="a_star_shortest_path",
        description="Find the shortest path between source_node and target_node using A* with a Haversine geo-distance heuristic (requires latitude and longitude node properties).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "target_node": TARGET_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "latitude_property": {
                    "type": "string",
                    "description": "Node property storing latitude.",
                },
                "longitude_property": {
                    "type": "string",
                    "description": "Node property storing longitude.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": [
                "graph_name",
                "source_node",
                "target_node",
                "node_identifier_property",
                "latitude_property",
                "longitude_property",
            ],
        },
    ),
    types.Tool(
        name="yens_shortest_paths",
        description="Compute the k shortest paths between source_node and target_node using Yen's algorithm (non-negative weights).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "target_node": TARGET_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "k": {
                    "type": "integer",
                    "description": "Number of shortest paths to compute.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": [
                "graph_name",
                "source_node",
                "target_node",
                "node_identifier_property",
            ],
        },
    ),
    types.Tool(
        name="minimum_weight_spanning_tree",
        description="Compute the minimum (or maximum) weight spanning tree of all nodes reachable from source_node using Prim's algorithm (supports negative weights).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_REL_PROPERTY_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "objective": {
                    "type": "string",
                    "enum": ["minimum", "maximum"],
                    "description": "Whether to compute the 'minimum' (default) or 'maximum' weight spanning tree.",
                },
            },
            "required": ["graph_name", "source_node", "node_identifier_property"],
        },
    ),
    types.Tool(
        name="minimum_directed_steiner_tree",
        description="""Compute an approximate minimum-weight directed subtree rooted at source_node that reaches all target_nodes (non-negative weights).
        It is possible to use the tool to find a solution for the more general Minimum Steiner Tree problem by arbitrarily selecting one of the target nodes to fill the role of the source node.
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "target_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Target node identifiers to connect in the Steiner tree.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "delta": {
                    "type": "number",
                    "description": "Delta-Stepping bucket width for shortest-path substeps.",
                },
                "apply_rerouting": {
                    "type": "boolean",
                    "description": "Whether to apply a post-processing rerouting heuristic to reduce tree weight.",
                },
            },
            "required": [
                "graph_name",
                "source_node",
                "target_nodes",
                "node_identifier_property",
            ],
        },
    ),
    types.Tool(
        name="prize_collecting_steiner_tree",
        description="""Compute an approximate spanning subtree that maximizes node prizes (prizeProperty) minus relationship weights.
        The tool implements a practical 2-approximate algorithm from the literature for the prize collecting Steiner tree problem.
        The tool can handle prizes for relationships through the following transformation: Given a relationship with weight w and prize p, we suggest to replace w with w' = w - p.
        If needed, this should be done as a pre-processing step prior to projecting the in-memory graph.
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "prize_property": {
                    "type": "string",
                    "description": "Node property holding non-negative node prizes.",
                },
            },
            "required": ["graph_name", "prize_property"],
        },
    ),
    types.Tool(
        name="all_pairs_shortest_paths",
        description="Compute shortest-path distances between all pairs of nodes (returns Infinity for unreachable pairs).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="random_walk",
        description="Generate second-order random walk paths across the graph, controlled by returnFactor and inOutFactor.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "source_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Nodes to start random walks from (requires node_identifier_property).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "walk_length": {
                    "type": "integer",
                    "description": "Number of steps in each random walk.",
                },
                "walks_per_node": {
                    "type": "integer",
                    "description": "Number of random walks per starting node.",
                },
                "in_out_factor": {
                    "type": "number",
                    "description": "Second-order walk parameter q (higher values stay closer to the previous node).",
                },
                "return_factor": {
                    "type": "number",
                    "description": "Second-order walk parameter p (values < 1.0 increase probability of returning to the previous node).",
                },
                "relationship_weight_property": {
                    "type": "string",
                    "description": "Non-negative relationship weight property to bias walk transitions (unweighted if omitted).",
                },
                "walk_buffer_size": {
                    "type": "integer",
                    "description": "Number of walks buffered in memory at once.",
                },
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="breadth_first_search",
        description="Traverse the graph in breadth-first order (increasing distance) from source_node, optionally stopping at target_nodes or max_depth.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "target_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Target node identifiers; traversal stops when any target is visited.",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum hop distance from source_node to visit.",
                },
            },
            "required": ["graph_name", "source_node", "node_identifier_property"],
        },
    ),
    types.Tool(
        name="depth_first_search",
        description="Traverse the graph in depth-first order from source_node, optionally stopping at target_nodes or max_depth.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "target_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Target node identifiers; traversal stops when any target is visited.",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum hop distance from source_node to visit.",
                },
            },
            "required": ["graph_name", "source_node", "node_identifier_property"],
        },
    ),
    types.Tool(
        name="bellman_ford_single_source_shortest_path",
        description="Compute shortest paths from source_node to all reachable nodes using Bellman-Ford (supports negative relationship weights and detects negative cycles; slower than Dijkstra).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_node": SOURCE_NODE_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "source_node", "node_identifier_property"],
        },
    ),
    types.Tool(
        name="longest_path",
        description="Compute longest paths ending at each node in a Directed Acyclic Graph (DAG). Excludes components with cycles; does not support negative weights.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "target_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Filter results to paths ending at these target nodes (requires node_identifier_property).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="max_flow",
        description="Compute maximum flow from source_nodes to target_nodes subject to relationship capacity_property constraints.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_REL_PROPERTY_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "source_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Source node identifiers where flow originates.",
                },
                "target_nodes": {
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "number"}]},
                    "description": "Target node identifiers where flow terminates.",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "capacity_property": {
                    "type": "string",
                    "description": "Relationship property specifying maximum flow capacity per edge.",
                },
            },
            "required": [
                "graph_name",
                "source_nodes",
                "target_nodes",
                "node_identifier_property",
                "capacity_property",
            ],
        },
    ),
]
