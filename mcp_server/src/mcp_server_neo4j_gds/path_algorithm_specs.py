from mcp import types

path_tool_definitions = [
    types.Tool(
        name="find_shortest_path",
        description="Find the shortest path between two nodes using Dijkstra's algorithm",
        inputSchema={
            "type": "object",
            "properties": {
                "start_node": {
                    "type": "string",
                    "description": "Name of the starting node",
                },
                "end_node": {
                    "type": "string",
                    "description": "Name of the ending node",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "relationship_property": {
                    "type": "string",
                    "description": "Property of the relationship to use for path finding",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Dijkstra on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Dijkstra on on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["start_node", "end_node", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="delta_stepping_shortest_path",
        description="The Delta-Stepping Shortest Path algorithm computes all shortest paths between a source node and all reachable nodes in the graph. "
        "The algorithm supports weighted graphs with positive relationship weights. To compute the shortest path between a source and a single target node, Dijkstra Source-Target can be used. "
        "In contrast to Dijkstra Single-Source, the Delta-Stepping algorithm is a distance correcting algorithm. "
        "This property allows it to traverse the graph in parallel. The algorithm is guaranteed to always find the shortest path between a source node and a target node. "
        "However, if multiple shortest paths exist between two nodes, the algorithm is not guaranteed to return the same path in each computation.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the source node to find shortest paths from.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "delta": {
                    "type": "number",
                    "description": "The bucket width for grouping nodes with the same tentative distance to the source node.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Delta-Stepping on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Delta-Stepping on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="dijkstra_single_source_shortest_path",
        description="The Dijkstra Shortest Path algorithm computes the shortest path between nodes. "
        "The algorithm supports weighted graphs with positive relationship weights. "
        "The Dijkstra Single-Source algorithm computes the shortest paths between a source node and all nodes reachable from that node. "
        "To compute the shortest path between a source and a target node, Dijkstra Source-Target can be used.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the source node to find shortest paths from.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Dijkstra on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Dijkstra on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="a_star_shortest_path",
        description='The A* (pronounced "A-Star") Shortest Path algorithm computes the shortest path between two nodes. '
        "A* is an informed search algorithm as it uses a heuristic function to guide the graph traversal. "
        "The algorithm supports weighted graphs with positive relationship weights. "
        "Unlike Dijkstra's shortest path algorithm, the next node to search from is not solely picked on the already computed distance. "
        "Instead, the algorithm combines the already computed distance with the result of a heuristic function. "
        "That function takes a node as input and returns a value that corresponds to the cost to reach the target node from that node. "
        "In each iteration, the graph traversal is continued from the node with the lowest combined cost. "
        "In GDS, the A* algorithm is based on the Dijkstra's shortest path algorithm. "
        "The heuristic function is the haversine distance, which defines the distance between two points on a sphere. "
        "Here, the sphere is the earth and the points are geo-coordinates stored on the nodes in the graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the source node to find shortest path from.",
                },
                "targetNode": {
                    "type": "string",
                    "description": "Name of the target node to find shortest path to.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "latitudeProperty": {
                    "type": "string",
                    "description": "The node property that stores the latitude value.",
                },
                "longitudeProperty": {
                    "type": "string",
                    "description": "The node property that stores the longitude value.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run A* on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run A* on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": [
                "sourceNode",
                "targetNode",
                "nodeIdentifierProperty",
                "latitudeProperty",
                "longitudeProperty",
            ],
        },
    ),
    types.Tool(
        name="yens_shortest_paths",
        description="Yen's Shortest Path algorithm computes a number of shortest paths between two nodes. "
        "The algorithm is often referred to as Yen's k-Shortest Path algorithm, where k is the number of shortest paths to compute. "
        "The algorithm supports weighted graphs with positive relationship weights. "
        "It also respects parallel relationships between the same two nodes when computing multiple shortest paths. "
        "For k = 1, the algorithm behaves exactly like Dijkstra's shortest path algorithm and returns the shortest path. "
        "For k = 2, the algorithm returns the shortest path and the second shortest path between the same source and target node. "
        "Generally, for k = n, the algorithm computes at most n paths which are discovered in the order of their total cost. "
        "The GDS implementation is based on the original description. "
        "For the actual path computation, Yen's algorithm uses Dijkstra's shortest path algorithm. "
        "The algorithm makes sure that an already discovered shortest path will not be traversed again.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the source node to find shortest paths from.",
                },
                "targetNode": {
                    "type": "string",
                    "description": "Name of the target node to find shortest paths to.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "k": {
                    "type": "integer",
                    "description": "The number of shortest paths to compute between source and target node.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Yens on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Yens on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "targetNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="minimum_weight_spanning_tree",
        description="The Minimum Weight Spanning Tree (MST) starts from a given node, finds all its reachable nodes and returns the set of relationships that connect these nodes together having the minimum possible weight. "
        "Prim's algorithm is one of the simplest and best-known minimum spanning tree algorithms. "
        "It operates similarly to Dijkstra's shortest path algorithm, but instead of minimizing the total length of a path ending at each relationship, it minimizes the length of each relationship individually. "
        "This allows the algorithm to work on graphs with negative weights. "
        "The MST algorithm provides meaningful results only when run on a graph where relationships have different weights. "
        "If the graph has no weights (or all relationships have the same weight), then any spanning tree is also a minimum spanning tree. "
        "The algorithm implementation is executed using a single thread. Altering the concurrency configuration has no effect.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the starting source node.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "objective": {
                    "type": "string",
                    "enum": ["minimum", "maximum"],
                    "description": "If specified, the parameter dictates whether to find the minimum or the maximum weight spanning tree. By default, a minimum weight spanning tree is returned. Permitted values are 'minimum' and 'maximum'.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Prim on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Prim on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="minimum_directed_steiner_tree",
        description="Given a source node and a list of target nodes, a directed spanning tree in which there exists a path from the source node to each of the target nodes is called a Directed Steiner Tree. "
        "The Minimum Directed Steiner Tree problem asks for the steiner tree that minimizes the sum of all relationship weights in tree. "
        "The Minimum Directed Steiner Tree problem is known to be NP-Complete and no efficient exact algorithms have been proposed in the literature. "
        "The Neo4j GDS Library offers an efficient implementation of a well-known heuristic for Steiner Tree related problems. "
        "The implemented algorithm works on a number of steps. At each step, the shortest path from the source to one of the undiscovered targets is found and added to the result. "
        "Following that, the weights in the relationships in this path are reduced to zero, and the algorithm continues similarly by finding the next closest unvisited target node. "
        "With a careful implementation, the above heuristic can run efficiently even for graphs of large size. In addition, the parallel shortest path algorithm of Delta-Stepping is used to further speed-up computations. "
        "As the Minimum Directed Steiner Tree algorithm relies on shortest-paths, it will not work for graphs with negative relationship weights. "
        "The Minimum Directed Steiner Tree problem is a variant of the more general Minimum Steiner Tree problem defined for undirected graphs. "
        "The Minimum Steiner Tree problem accepts as input only a set of target nodes. The aim is then to find a spanning tree of minimum weight connecting these target nodes. "
        "It is possible to use the GDS implementation to find a solution for Minimum Steiner Tree problem by arbitrarily selecting one of the target nodes to fill the role of the source node.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the starting source node.",
                },
                "targetNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of target node names to connect in the steiner tree.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "delta": {
                    "type": "number",
                    "description": "The bucket width for grouping nodes with the same tentative distance to the source node. Look into the Delta-Stepping documentation for more information.",
                },
                "applyRerouting": {
                    "type": "boolean",
                    "description": "If specified, the algorithm will try to improve the outcome via an additional post-processing heuristic.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Steiner-Tree on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Steiner-Tree on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "targetNodes", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="prize_collecting_steiner_tree",
        description="A spanning tree is a graph such that there is exactly one path between any two nodes in the set. A graph can have many possible spanning tree subsets depending on the set of nodes/relationships selected. "
        "Given a weighted graph where each node has a prize, the Prize-Collecting Steiner Tree problem asks for the spanning tree that satisfies the following conditions: "
        "1. the sum of prizes for the nodes in the graph is maximized. "
        "2. the sum of weights of relationships and prizes for nodes not in the tree is minimized. "
        "The two constraints can combined to form a single maximization problem by simply subtracting the second constraint from the former. "
        "The Prize-Collecting Steiner Tree is NP-Complete and no efficient exact algorithms is known. The Neo4j GDS Library implements a practical 2-approximate algorithm from the literature. "
        "This means that the returned answer should be at least half as good as the optimal answer. "
        "By default, the Prize-Collecting Steiner Tree problem considers prizes only for nodes. In some cases, however, it can be useful to also consider prizes on relationships. "
        "The GDS implementation can handle prizes for relationships through the following transformation: Given a relationship with weight w and prize p, we suggest to replace w with w' = w - p. "
        "This should be done as a pre-processing step prior to projecting the in-memory graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "prizeProperty": {
                    "type": "string",
                    "description": "The name of node property that denotes a node's prize.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Prize Collecting Steiner Tree on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Prize Collecting Steiner Tree on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["prizeProperty"],
        },
    ),
    types.Tool(
        name="all_pairs_shortest_paths",
        description="The All Pairs Shortest Path (APSP) calculates the shortest (weighted) path between all pairs of nodes. "
        "This algorithm has optimizations that make it quicker than calling the Single Source Shortest Path algorithm for every pair of nodes in the graph. "
        "Some pairs of nodes might not be reachable between each other, so no shortest path exists between these pairs. "
        "In this scenario, the algorithm will return Infinity value as a result between these pairs of nodes. "
        "GDS includes functions such as gds.util.isFinite to help filter infinity values from results. "
        "Starting with Neo4j 5, the Infinity literal is now included in Cypher too.",
        inputSchema={
            "type": "object",
            "properties": {
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run APSP on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run APSP on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="random_walk",
        description="Random Walk is an algorithm that provides random paths in a graph. "
        "A random walk simulates a traversal of the graph in which the traversed relationships are chosen at random. "
        "In a classic random walk, each relationship has the same, possibly weighted, probability of being picked. "
        "This probability is not influenced by the previously visited nodes. "
        "The random walk implementation of the Neo4j Graph Data Science library supports the concept of second order random walks. "
        "This method tries to model the transition probability based on the currently visited node v, the node t visited before the current one, and the node x which is the target of a candidate relationship. "
        "Random walks are thus influenced by two parameters: the returnFactor and the inOutFactor: "
        "The returnFactor is used if t equals x, i.e., the random walk returns to the previously visited node. "
        "The inOutFactor is used if the distance from t to x is equal to 2, i.e., the walk traverses further away from the node t. "
        "The probabilities for traversing a relationship during a random walk can be further influenced by specifying a relationshipWeightProperty. "
        "A relationship property value greater than 1 will increase the likelihood of a relationship being traversed, a property value between 0 and 1 will decrease that probability.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The list of nodes from which to do a random walk.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "walkLength": {
                    "type": "integer",
                    "description": "The number of steps in a single random walk.",
                },
                "walksPerNode": {
                    "type": "integer",
                    "description": "The number of random walks generated for each node.",
                },
                "inOutFactor": {
                    "type": "number",
                    "description": "Tendency of the random walk to stay close to the start node or fan out in the graph. Higher value means stay local.",
                },
                "returnFactor": {
                    "type": "number",
                    "description": "Tendency of the random walk to return to the last visited node. A value below 1.0 means a higher tendency.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights to influence the probabilities of the random walks. The weights need to be >= 0. If unspecified, the algorithm runs unweighted.",
                },
                "walkBufferSize": {
                    "type": "integer",
                    "description": "The number of random walks to complete before starting training.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Random Walk on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Random Walk on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="breadth_first_search",
        description="The Breadth First Search algorithm is a graph traversal algorithm that given a start node visits nodes in order of increasing distance, see https://en.wikipedia.org/wiki/Breadth-first_search. "
        "A related algorithm is the Depth First Search algorithm, Depth First Search. "
        "This algorithm is useful for searching when the likelihood of finding the node searched for decreases with distance. "
        "There are multiple termination conditions supported for the traversal, based on either reaching one of several target nodes, reaching a maximum depth, exhausting a given budget of traversed relationship cost, or just traversing the whole graph. "
        "The output of the procedure contains information about which nodes were visited and in what order.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the starting source node.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "targetNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Names of target nodes. Traversal terminates when any target node is visited.",
                },
                "maxDepth": {
                    "type": "integer",
                    "description": "The maximum distance from the source node at which nodes are visited.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run BFS on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run BFS on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="depth_first_search",
        description="The Depth First Search algorithm is a graph traversal that starts at a given node and explores as far as possible along each branch before backtracking, see https://en.wikipedia.org/wiki/Depth-first_search. "
        "A related algorithm is the Breadth First Search algorithm, Breadth First Search. "
        "This algorithm can be preferred over Breadth First Search for example if one wants to find a target node at a large distance and exploring a random path has decent probability of success. "
        "There are multiple termination conditions supported for the traversal, based on either reaching one of several target nodes, reaching a maximum depth, exhausting a given budget of traversed relationship cost, or just traversing the whole graph. "
        "The output of the procedure contains information about which nodes were visited and in what order.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the starting source node.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "targetNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Names of target nodes. Traversal terminates when any target node is visited.",
                },
                "maxDepth": {
                    "type": "integer",
                    "description": "The maximum distance from the source node at which nodes are visited.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run DFS on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run DFS on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="bellman_ford_single_source_shortest_path",
        description="The Bellman-Ford Path algorithm computes the shortest path between nodes. "
        "In contrast to the Dijkstra algorithm which works only for graphs with non-negative relationship weights, Bellman-Ford can also handle graphs with negative weights provided that the source cannot reach any node involved in a negative cycle. "
        "A cycle in a graph is a path starting and ending at the same node. A negative cycle is a cycle for which the sum of the relationship weights is negative. "
        "When negative cycles exist, shortest paths cannot easily be defined. That is so because we can traverse a negative cycle multiple times to get smaller and smaller costs each time. "
        "When the Bellman-Ford algorithm detects negative cycles, it will try to return negative cycles instead of shortest paths. "
        "Note that in some situations the implementation might not be able to enumerate them due to modifying the algorithm to support a parallel implementation. "
        "As the full set of negative cycles can be too large to enumerate, each node will be included in at most one returned negative cycle. "
        "The ability to handle negative weights makes Bellman-Ford more versatile than Dijkstra, but also slower in practice. "
        "The Neo4j GDS Library provides an adaptation of the original Bellman-Ford algorithm called Shortest-Path Faster Algorithm (SPFA). "
        "SPFA significantly reduces the computational time of Bellman-Ford by working only on a subset of the nodes rather than iterating over the set of nodes at each step. "
        "In addition, the computations are parallelized to further speed-up computations.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNode": {
                    "type": "string",
                    "description": "Name of the starting source node.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Bellman-Ford on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Bellman-Ford on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["sourceNode", "nodeIdentifierProperty"],
        },
    ),
    types.Tool(
        name="longest_path",
        description="Finding the longest path that leads to a node in a graph is possible to do in linear time for the special case of DAGs, that is graphs which do not contain cycles. "
        "The GDS implementation for this problem is based on topological sort and operates in linear time. "
        "When the graph is not a DAG, any node that belongs to component containing at least one cycle will be excluded from the results. "
        "That is, the implementation will only give results for those components of the graph that form DAGs. "
        "You can use topological sort to make sure the graph is a DAG. "
        "The algorithm supports weighted and unweighted graphs. Negative weights are currently unsupported.",
        inputSchema={
            "type": "object",
            "properties": {
                "targetNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of target node names to filter results. Only paths ending at these nodes will be returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties. Required when targetNodes is specified.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run longest path on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run longest path on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="max_flow",
        description="Given source nodes, target nodes and relationships with capacity constraints, the max-flow algorithm assigns a flow to each relationship to achieve maximal transport from source to target. "
        "The flow is a scalar property for each relationship and must satisfy 1) Flow into a node equals flow out of a node (preservation). 2) Flow is restricted by the capacity of a relationship",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of source node names from which flow originates.",
                },
                "targetNodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of target node names to which flow is sent.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "capacityProperty": {
                    "type": "string",
                    "description": "Name of the relationship property that specifies the maximum flow capacity for each edge.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run max flow on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run max flow on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": [
                "sourceNodes",
                "targetNodes",
                "nodeIdentifierProperty",
                "capacityProperty",
            ],
        },
    ),
]
