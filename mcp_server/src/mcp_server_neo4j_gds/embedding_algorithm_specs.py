from mcp import types

from .common_specs import (
    GRAPH_NAME_DESCRIPTION,
    MODE_DESCRIPTION,
    MUTATE_NODE_PROPERTY_DESCRIPTION,
    NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
    RANDOM_SEED_DESCRIPTION,
    RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
)

embedding_tool_definitions = [
    types.Tool(
        name="fast_rp",
        description="""Fast Random Projection (FastRP) is a node embedding algorithm that computes a vector representation for every node in the graph.
        Embeddings capture graph topology, and can optionally incorporate node properties via propertyRatio and featureProperties.
        To make embeddings comparable across nodes connected by undirected semantics, project the graph as undirected.
        """,
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "embedding_dimension": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Dimension of the computed node embeddings (>= 1).",
                },
                "iteration_weights": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Weight for each hop iteration (list length = number of iterations; default: [0.0, 1.0, 1.0]).",
                },
                "normalization_strength": {
                    "type": "number",
                    "description": "Degree scaling exponent for initial random vectors (default: 0).",
                },
                "node_self_influence": {
                    "type": "number",
                    "description": "Contribution weight of a node's own initial random vector (default: 0).",
                },
                "property_ratio": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Fraction of embedding_dimension derived from feature_properties in [0, 1] (default: 0).",
                },
                "feature_properties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Numeric or numeric-array node properties used as features (requires property_ratio > 0).",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "random_seed": RANDOM_SEED_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "embedding_dimension"],
        },
    ),
    types.Tool(
        name="node2vec",
        description="Compute node embeddings by training a skip-gram neural network on second-order random walks (controlled by returnFactor and inOutFactor).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "embedding_dimension": {
                    "type": "integer",
                    "description": "Dimension of the computed node embeddings (default: 128).",
                },
                "walk_length": {
                    "type": "integer",
                    "description": "Number of steps per random walk (default: 80).",
                },
                "walks_per_node": {
                    "type": "integer",
                    "description": "Number of random walks per node (default: 10).",
                },
                "in_out_factor": {
                    "type": "number",
                    "description": "Second-order walk parameter q; higher values stay local (default: 1.0).",
                },
                "return_factor": {
                    "type": "number",
                    "description": "Second-order walk parameter p; values < 1.0 return to the previous node more often (default: 1.0).",
                },
                "window_size": {
                    "type": "integer",
                    "description": "Skip-gram context window size (default: 10).",
                },
                "negative_sampling_rate": {
                    "type": "integer",
                    "description": "Negative samples per positive sample (default: 5).",
                },
                "positive_sampling_factor": {
                    "type": "number",
                    "description": "Down-sampling factor for frequent nodes (default: 0.001).",
                },
                "embedding_initializer": {
                    "type": "string",
                    "enum": ["NORMALIZED", "UNIFORM"],
                    "description": "Embedding initialization method (default: NORMALIZED).",
                },
                "iterations": {
                    "type": "integer",
                    "description": "Number of training iterations (default: 1).",
                },
                "initial_learning_rate": {
                    "type": "number",
                    "description": "Initial training learning rate (default: 0.01).",
                },
                "min_learning_rate": {
                    "type": "number",
                    "description": "Minimum learning rate floor during decay (default: 0.0001).",
                },
                "walk_buffer_size": {
                    "type": "integer",
                    "description": "Number of random walks buffered before training (default: 1000).",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "random_seed": RANDOM_SEED_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name"],
        },
    ),
    types.Tool(
        name="hashgnn",
        description="""HashGNN is a node embedding algorithm which resembles Graph Neural Networks but does not include a model or require training.
        It uses hashing functions (min-hash) instead of trained neural network weights, making it orders of magnitude faster than GNNs.
        Node input features must be binary; provide binary featureProperties, or use binarizeFeatures to binarize numeric properties, or generateFeatures to generate random binary features from topology alone.
        It supports heterogeneous graphs (set heterogeneous to true) where embeddings distinguish different relationship types.
        Output embeddings are binary by default; set outputDimension to densify them into float vectors.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "iterations": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of message-passing iterations / hops (>= 1).",
                },
                "embedding_density": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of min-hash features sampled per node per iteration (>= 1).",
                },
                "feature_properties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Node properties used as input features (must be binary unless binarize_features is set). Provide either feature_properties or generate_features.",
                },
                "generate_features": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "integer", "minimum": 1},
                        "density_level": {"type": "integer", "minimum": 1},
                    },
                    "required": ["dimension", "density_level"],
                    "description": "Generate random binary features from topology alone ({dimension, density_level}); mutually exclusive with feature_properties and binarize_features.",
                },
                "binarize_features": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "integer", "minimum": 1},
                        "threshold": {"type": "number"},
                    },
                    "required": ["dimension"],
                    "description": "Binarize numeric feature_properties via hyperplane rounding ({dimension, threshold}).",
                },
                "heterogeneous": {
                    "type": "boolean",
                    "description": "Whether to distinguish different relationship types (default: false).",
                },
                "neighbor_influence": {
                    "type": "number",
                    "description": "Relative weight of neighbor features vs. self features (default: 1.0).",
                },
                "output_dimension": {
                    "type": "integer",
                    "description": "Project binary embeddings into dense float vectors of this dimension.",
                },
                "random_seed": RANDOM_SEED_DESCRIPTION,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "iterations", "embedding_density"],
        },
    ),
    types.Tool(
        name="graph_sage_train",
        description="""Trains a GraphSAGE model and stores it in the GDS model catalog under modelName.
        GraphSAGE is an inductive graph neural network that learns a function to generate node embeddings by sampling and aggregating features from a node's local neighborhood.
        The graph should be projected with undirected relationships for best results.
        All featureProperties must exist in the projected graph as numeric properties (use get_graph_info to check).
        After training, use graph_sage_predict to generate embeddings, list_models to inspect models, and drop_model to free memory.""",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": {
                    "type": "string",
                    "description": "Unique name for the trained model in the model catalog.",
                },
                "feature_properties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Numeric or numeric-array node properties in the projected graph to use as input features.",
                },
                "embedding_dimension": {
                    "type": "integer",
                    "description": "Dimension of embeddings and hidden layers (default: 64).",
                },
                "aggregator": {
                    "type": "string",
                    "enum": ["mean", "pool"],
                    "description": "Neighbor aggregation method (default: 'mean').",
                },
                "activation_function": {
                    "type": "string",
                    "enum": ["sigmoid", "relu"],
                    "description": "Layer activation function (default: 'sigmoid').",
                },
                "sample_sizes": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Neighbors sampled per layer; list length defines layer count (default: [25, 10]).",
                },
                "epochs": {
                    "type": "integer",
                    "description": "Number of training epochs (default: 1).",
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum weight update iterations per batch (default: 10).",
                },
                "search_depth": {
                    "type": "integer",
                    "description": "Random walk depth for positive example sampling (default: 5).",
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Training examples per batch (default: 100).",
                },
                "learning_rate": {
                    "type": "number",
                    "description": "Weight update step size (default: 0.1).",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Loss difference threshold for early convergence (default: 1e-4).",
                },
                "negative_sample_weight": {
                    "type": "integer",
                    "description": "Weight of negative samples in the loss function (default: 20).",
                },
                "penalty_l2": {
                    "type": "number",
                    "description": "L2 regularization weight (default: 0).",
                },
                "projected_feature_dimension": {
                    "type": "integer",
                    "description": "Shared feature projection dimension to enable multi-label mode on heterogeneous graphs.",
                },
                "relationship_weight_property": RELATIONSHIP_WEIGHT_PROPERTY_DESCRIPTION,
                "random_seed": RANDOM_SEED_DESCRIPTION,
            },
            "required": ["graph_name", "model_name", "feature_properties"],
        },
    ),
    types.Tool(
        name="graph_sage_predict",
        description="Generate node embeddings using a trained GraphSAGE model; the graph must contain the feature properties expected by the model.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": {
                    "type": "string",
                    "description": "Name of the trained GraphSAGE model in the model catalog.",
                },
                "batch_size": {
                    "type": "integer",
                    "description": "Nodes per inference batch (default: 100).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "model_name"],
        },
    ),
]
