from mcp import types

similarity_tool_definitions = [
    types.Tool(
        name="node_similarity",
        description="The Node Similarity algorithm compares a set of nodes based on the nodes they are connected to. "
        "Two nodes are considered similar if they share many of the same neighbors. "
        "Node Similarity computes pair-wise similarities based on the Jaccard metric, also known as the Jaccard Similarity Score, the Overlap coefficient, also known as the Szymkiewicz–Simpson coefficient, and the Cosine Similarity score. "
        "The first two are most frequently associated with unweighted sets, whereas Cosine with weighted input."
        "Filters on source nodes, target nodes, or both can additionally be provided to compute results for subset of nodes.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNodeFilter": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        {
                            "type": "string",
                        },
                    ],
                    "description": "The source node filter to apply. Accepts a List of node names, or a single label.",
                },
                "targetNodeFilter": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        {
                            "type": "string",
                        },
                    ],
                    "description": "The target node filter to apply. Accepts a List of node names, or a single label.",
                },
                "similarityCutoff": {
                    "type": "number",
                    "description": "Lower limit for the similarity score to be present in the result. Values must be between 0 and 1.",
                },
                "degreeCutoff": {
                    "type": "integer",
                    "description": "Inclusive lower bound on the node degree for a node to be considered in the comparisons. This value can not be lower than 1.",
                },
                "upperDegreeCutoff": {
                    "type": "integer",
                    "description": "Inclusive upper bound on the node degree for a node to be considered in the comparisons. This value can not be lower than 1.",
                },
                "topK": {
                    "type": "integer",
                    "description": "Limit on the number of scores per node. The K largest results are returned. This value cannot be lower than 1. Use this instead of topN whenever the sourceNode consists of a single node, or it is specifically stated that results are to be computed for each source node",
                },
                "bottomK": {
                    "type": "integer",
                    "description": "Limit on the number of scores per node. The K smallest results are returned. This value cannot be lower than 1.",
                },
                "topN": {
                    "type": "integer",
                    "description": "Global limit on the number of scores computed. The N largest total results are returned. This value cannot be negative, a value of 0 means no global limit.",
                },
                "bottomN": {
                    "type": "integer",
                    "description": "Global limit on the number of scores computed. The N smallest total results are returned. This value cannot be negative, a value of 0 means no global limit.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "similarityMetric": {
                    "type": "string",
                    "enum": ["JACCARD", "OVERLAP", "COSINE"],
                    "description": "The metric used to compute similarity.",
                },
                "useComponents": {
                    "type": "boolean",
                    "description": "If enabled, Node Similarity will use components to improve the performance of the computation, skipping comparisons of nodes in different components. Set to false (Default): the algorithm does not use components, but computes similarity across the entire graph. Set to true: the algorithm uses components, and will compute these components before computing similarity. Set to String: use pre-computed components stored in graph, String is the key for a node property representing components.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Node Similarity on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run Node Similarity on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
        },
    ),
    types.Tool(
        name="k_nearest_neighbors",
        description="The K-Nearest Neighbors algorithm computes a distance value for all node pairs in the graph and creates new relationships between each node and its k nearest neighbors. "
        "The distance is calculated based on node properties. "
        "The input of this algorithm is a homogeneous graph; any node label or relationships type information in the graph is ignored. "
        "The graph does not need to be connected, in fact, existing relationships between nodes will be ignored - apart from random walk sampling if that that initial sampling option is used. "
        "New relationships are created between each node and its k nearest neighbors. "
        "The K-Nearest Neighbors algorithm compares given properties of each node. The k nodes where these properties are most similar are the k-nearest neighbors. "
        "The initial set of neighbors is picked at random and verified and refined in multiple iterations. The number of iterations is limited by the configuration parameter maxIterations. "
        "The algorithm may stop earlier if the neighbor lists only change by a small amount, which can be controlled by the configuration parameter deltaThreshold. "
        "The particular implementation is based on Efficient k-nearest neighbor graph construction for generic similarity measures by Wei Dong et al. "
        "Instead of comparing every node with every other node, the algorithm selects possible neighbors based on the assumption, that the neighbors-of-neighbors of a node are most likely already the nearest one. "
        "The algorithm scales quasi-linear with respect to the node count, instead of being quadratic. "
        "Furthermore, the algorithm only compares a sample of all possible neighbors on each iteration, assuming that eventually all possible neighbors will be seen. "
        "This can be controlled with the configuration parameter sampleRate: A valid sample rate must be in between 0 (exclusive) and 1 (inclusive). "
        "The default value is 0.5. The parameter is used to control the trade-off between accuracy and runtime-performance. "
        "A higher sample rate will increase the accuracy of the result. The algorithm will also require more memory and will take longer to compute. "
        "A lower sample rate will increase the runtime-performance. Some potential nodes may be missed in the comparison and may not be included in the result. "
        "When encountered neighbors have equal similarity to the least similar already known neighbor, randomly selecting which node to keep can reduce the risk of some neighborhoods not being explored. "
        "This behavior is controlled by the configuration parameter perturbationRate. "
        "The output of the algorithm are new relationships between nodes and their k-nearest neighbors. Similarity scores are expressed via relationship properties."
        "Filters on source nodes, target nodes, or both can additionally be provided to compute results for subset of nodes.",
        inputSchema={
            "type": "object",
            "properties": {
                "sourceNodeFilter": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        {
                            "type": "string",
                        },
                    ],
                    "description": "The source node filter to apply. Accepts a List of node names, or a single label.",
                },
                "targetNodeFilter": {
                    "anyOf": [
                        {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        {
                            "type": "string",
                        },
                    ],
                    "description": "The target node filter to apply. Accepts a List of node names, or a single label.",
                },
                "nodeProperties": {
                    "type": "object",
                    "description": "The node properties to use for similarity computation along with their selected similarity metrics. Accepts a Map of property keys to metrics. For example: {embedding: 'COSINE',age: 'DEFAULT',lotteryNumbers: 'OVERLAP'}. DEFAULT refers to COSINE.",
                },
                "topK": {
                    "type": "integer",
                    "description": "The number of neighbors to find for each node. The K-nearest neighbors are returned. This value cannot be lower than 1.",
                },
                "sampleRate": {
                    "type": "number",
                    "description": "Sample rate to limit the number of comparisons per node. Value must be between 0 (exclusive) and 1 (inclusive).",
                },
                "deltaThreshold": {
                    "type": "number",
                    "description": "Value as a percentage to determine when to stop early. If fewer updates than the configured value happen, the algorithm stops. Value must be between 0 (exclusive) and 1 (inclusive).",
                },
                "maxIterations": {
                    "type": "integer",
                    "description": "Hard limit to stop the algorithm after that many iterations.",
                },
                "randomJoins": {
                    "type": "integer",
                    "description": "The number of random attempts per node to connect new node neighbors based on random selection, for each iteration.",
                },
                "initialSampler": {
                    "type": "string",
                    "enum": ["uniform", "randomWalk"],
                    "description": 'The method used to sample the first k random neighbors for each node. "uniform" and "randomWalk", both case-insensitive, are valid inputs.',
                },
                "similarityCutoff": {
                    "type": "number",
                    "description": "Filter out from the list of K-nearest neighbors nodes with similarity below this threshold.",
                },
                "perturbationRate": {
                    "type": "number",
                    "description": "The probability of replacing the least similar known neighbor with an encountered neighbor of equal similarity.",
                },
                "seedTargetNodes": {
                    "type": "boolean",
                    "description": "Enable seeding of target nodes. If seeded, every node picks some of the target nodes initially. This guarantees that for every node we can avoid empty result (when the algorithm did not find for it any similar neighbors from the target set). Can only be used if targetNodeFilter is set.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run k-nearest neighbors on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "relTypes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The relationships types used to project and run k-nearest neighbors on. Relationship types of different type will be ignored. Do not specify to run for all relationship types",
                },
            },
            "required": ["nodeProperties"],
        },
    ),
]
