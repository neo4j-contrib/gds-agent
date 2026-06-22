from mcp import types

embedding_tool_definitions = [
    types.Tool(
        name="fast_rp",
        description="Fast Random Projection (FastRP) is a node embedding algorithm that computes a vector representation for every node in the graph. "
        "It uses sparse random projections and iterative averaging over node neighborhoods, making it very fast and scalable. "
        "Embeddings capture graph topology, and can optionally incorporate node properties via propertyRatio and featureProperties. "
        "The resulting embeddings can be used for downstream tasks such as k_nearest_neighbors similarity, clustering, or as features for ML pipeline training. "
        "For downstream use within the same projected graph, prefer mode 'mutate' to store embeddings as a node property; "
        "stream mode returns one embedding vector per node and can produce large outputs. "
        "To make embeddings comparable across nodes connected by undirected semantics, project the graph as undirected.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Use project_graph_cypher to create a graph first.",
                },
                "embeddingDimension": {
                    "type": "integer",
                    "description": "The dimension of the computed node embeddings. Minimum value is 1. Typical values are 128-1024.",
                },
                "iterationWeights": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Contains a weight for each iteration. The weight controls how much the intermediate embedding from that iteration contributes to the final embedding. The number of iterations equals the length of this list. Default is [0.0, 1.0, 1.0].",
                },
                "normalizationStrength": {
                    "type": "number",
                    "description": "The initial random vector for each node is scaled by its degree to the power of normalizationStrength. Negative values downplay the importance of high-degree neighbors. Default is 0.",
                },
                "nodeSelfInfluence": {
                    "type": "number",
                    "description": "Controls how much a node's initial random vector contributes to its final embedding. Default is 0.",
                },
                "propertyRatio": {
                    "type": "number",
                    "description": "The fraction of the embedding dimension dedicated to node property features. Must be between 0 and 1. Requires featureProperties when greater than 0. Default is 0 (topology only).",
                },
                "featureProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Names of node properties (numbers or arrays of numbers) to use as input features. Requires propertyRatio greater than 0.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "A random seed to produce reproducible embeddings across runs.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns embeddings as a table, 'mutate' writes embeddings to the in-memory graph as a node property. Default is 'stream'.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write embeddings to.",
                },
            },
            "required": ["graphName", "embeddingDimension"],
        },
    ),
    types.Tool(
        name="node2vec",
        description="Node2Vec is a node embedding algorithm that computes a vector representation of a node based on second-order random walks in the graph. "
        "The random walks are controlled by returnFactor and inOutFactor to interpolate between breadth-first (structural roles) and depth-first (community) characteristics. "
        "A skip-gram neural network is trained on the walks to produce the embeddings. "
        "Embeddings can be used for downstream tasks such as k_nearest_neighbors similarity, clustering, or as features for ML pipeline training. "
        "For downstream use within the same projected graph, prefer mode 'mutate' to store embeddings as a node property.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Use project_graph_cypher to create a graph first.",
                },
                "embeddingDimension": {
                    "type": "integer",
                    "description": "Size of the computed node embeddings. Default is 128.",
                },
                "walkLength": {
                    "type": "integer",
                    "description": "The number of steps in a single random walk. Default is 80.",
                },
                "walksPerNode": {
                    "type": "integer",
                    "description": "The number of random walks generated for each node. Default is 10.",
                },
                "inOutFactor": {
                    "type": "number",
                    "description": "Tendency of the random walk to stay close to the start node or fan out in the graph. Higher value means stay local. Default is 1.0.",
                },
                "returnFactor": {
                    "type": "number",
                    "description": "Tendency of the random walk to return to the last visited node. A value below 1.0 means a higher tendency. Default is 1.0.",
                },
                "windowSize": {
                    "type": "integer",
                    "description": "Size of the context window when training the neural network. Default is 10.",
                },
                "negativeSamplingRate": {
                    "type": "integer",
                    "description": "Number of negative samples to produce for each positive sample. Default is 5.",
                },
                "positiveSamplingFactor": {
                    "type": "number",
                    "description": "Factor for influencing the distribution for positive samples. A higher value increases the probability that frequent nodes are down-sampled. Default is 0.001.",
                },
                "embeddingInitializer": {
                    "type": "string",
                    "enum": ["NORMALIZED", "UNIFORM"],
                    "description": "Method to initialize embeddings. Default is NORMALIZED.",
                },
                "iterations": {
                    "type": "integer",
                    "description": "Number of training iterations. Default is 1.",
                },
                "initialLearningRate": {
                    "type": "number",
                    "description": "Learning rate used initially for training the neural network. The learning rate decreases after each training iteration. Default is 0.01.",
                },
                "minLearningRate": {
                    "type": "number",
                    "description": "Lower bound for learning rate as it is decreased during training. Default is 0.0001.",
                },
                "walkBufferSize": {
                    "type": "integer",
                    "description": "The number of random walks to complete before starting training. Default is 1000.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights to influence walk probabilities. If unspecified, the algorithm runs unweighted.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "Seed value used to generate the random walks. Note that full determinism additionally requires single-threaded computation on the server.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns embeddings as a table, 'mutate' writes embeddings to the in-memory graph as a node property. Default is 'stream'.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write embeddings to.",
                },
            },
            "required": ["graphName"],
        },
    ),
    types.Tool(
        name="hashgnn",
        description="HashGNN is a node embedding algorithm which resembles Graph Neural Networks but does not include a model or require training. "
        "It uses hashing functions (min-hash) instead of trained neural network weights, making it orders of magnitude faster than GNNs. "
        "Node input features must be binary; provide binary featureProperties, or use binarizeFeatures to binarize numeric properties, or generateFeatures to generate random binary features from topology alone. "
        "It supports heterogeneous graphs (set heterogeneous to true) where embeddings distinguish different relationship types. "
        "Output embeddings are binary by default; set outputDimension to densify them into float vectors. "
        "For downstream use within the same projected graph, prefer mode 'mutate' to store embeddings as a node property.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to run the algorithm on. Use project_graph_cypher to create a graph first.",
                },
                "iterations": {
                    "type": "integer",
                    "description": "The number of iterations to run HashGNN. Similar to layers in a GNN: a node's embedding is influenced by neighbors at most this many hops away. Must be at least 1.",
                },
                "embeddingDensity": {
                    "type": "integer",
                    "description": "The number of features to sample per node in each iteration. Called K in the original paper. A larger value yields higher quality but slower computation. Must be at least 1.",
                },
                "featureProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Names of node properties to use as input features. Must be binary (0/1) values or arrays of binary values, unless binarizeFeatures is also given.",
                },
                "generateFeatures": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "integer"},
                        "densityLevel": {"type": "integer"},
                    },
                    "description": "Generate random binary node features from topology alone (use when no suitable node properties exist). 'dimension' is the feature vector length and 'densityLevel' is the number of set bits per node. Mutually exclusive with featureProperties.",
                },
                "binarizeFeatures": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "integer"},
                        "threshold": {"type": "number"},
                    },
                    "description": "Binarize non-binary featureProperties using hyperplane rounding. 'dimension' is the binarized feature vector length and 'threshold' (default 0) controls bit assignment.",
                },
                "heterogeneous": {
                    "type": "boolean",
                    "description": "Whether different relationship types should be treated differently. Default is false.",
                },
                "neighborInfluence": {
                    "type": "number",
                    "description": "Controls how often neighbors' features are sampled in each iteration relative to sampling the node's own features. Default is 1.0.",
                },
                "outputDimension": {
                    "type": "integer",
                    "description": "If set, embeddings are projected into dense float vectors of this dimension instead of binary vectors.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "A random seed to produce deterministic results.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns embeddings as a table, 'mutate' writes embeddings to the in-memory graph as a node property. Default is 'stream'.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write embeddings to.",
                },
            },
            "required": ["graphName", "iterations", "embeddingDensity"],
        },
    ),
    types.Tool(
        name="graph_sage_train",
        description="Trains a GraphSAGE model and stores it in the GDS model catalog under modelName. "
        "GraphSAGE is an inductive graph neural network that learns a function to generate node embeddings by sampling and aggregating features from a node's local neighborhood. "
        "Unlike FastRP or Node2Vec, a trained GraphSAGE model can be reused to compute embeddings for unseen nodes or other graphs with the same schema (use graph_sage_predict). "
        "The graph should be projected with undirected relationships for best results. "
        "All featureProperties must exist in the projected graph as numeric properties (use get_graph_info to check). "
        "After training, use graph_sage_predict to generate embeddings, list_models to inspect models, and drop_model to free memory.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to train on. Use project_graph_cypher to create a graph first.",
                },
                "modelName": {
                    "type": "string",
                    "description": "Unique name for the trained model in the model catalog.",
                },
                "featureProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Node properties in the projected graph to use as input features. Must be numbers or arrays of numbers.",
                },
                "embeddingDimension": {
                    "type": "integer",
                    "description": "Size of the node embeddings and the hidden layers. Default is 64.",
                },
                "aggregator": {
                    "type": "string",
                    "enum": ["mean", "pool"],
                    "description": "Aggregator used to combine neighbor embeddings. Default is 'mean'.",
                },
                "activationFunction": {
                    "type": "string",
                    "enum": ["sigmoid", "relu"],
                    "description": "Activation function in the neural network layers. Default is 'sigmoid'.",
                },
                "sampleSizes": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Number of neighbors sampled per layer; the list length is the number of layers. Default is [25, 10].",
                },
                "epochs": {
                    "type": "integer",
                    "description": "Number of times to traverse the graph during training. Default is 1.",
                },
                "maxIterations": {
                    "type": "integer",
                    "description": "Maximum number of weight update iterations per batch. Default is 10.",
                },
                "searchDepth": {
                    "type": "integer",
                    "description": "Maximum depth of the random walks used to sample positive examples. Default is 5.",
                },
                "batchSize": {
                    "type": "integer",
                    "description": "Number of training examples per batch. Default is 100.",
                },
                "learningRate": {
                    "type": "number",
                    "description": "Step size for weight updates. Default is 0.1.",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Loss difference threshold for early convergence. Default is 1e-4.",
                },
                "negativeSampleWeight": {
                    "type": "integer",
                    "description": "Weight of negative samples in the loss function. Default is 20.",
                },
                "penaltyL2": {
                    "type": "number",
                    "description": "Influence of the L2 regularization term in the loss. Default is 0.",
                },
                "projectedFeatureDimension": {
                    "type": "integer",
                    "description": "Enables multi-label mode for heterogeneous graphs by projecting per-label features into a shared feature space of this dimension.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "A random seed for reproducible training.",
                },
            },
            "required": ["graphName", "modelName", "featureProperties"],
        },
    ),
    types.Tool(
        name="graph_sage_predict",
        description="Generates node embeddings using a previously trained GraphSAGE model from the model catalog (see graph_sage_train). "
        "The graph must contain the feature properties the model was trained on. "
        "Use mode 'mutate' to store embeddings as a node property for downstream tools such as k_nearest_neighbors or ML pipeline training; "
        "stream mode returns one embedding vector per node.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to compute embeddings for.",
                },
                "modelName": {
                    "type": "string",
                    "description": "Name of the trained GraphSAGE model in the model catalog.",
                },
                "batchSize": {
                    "type": "integer",
                    "description": "Number of nodes per inference batch. Default is 100.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns embeddings as a table, 'mutate' writes embeddings to the in-memory graph as a node property. Default is 'stream'.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write embeddings to.",
                },
            },
            "required": ["graphName", "modelName"],
        },
    ),
]
