from mcp import types

from .common_specs import (
    GRAPH_NAME_DESCRIPTION,
    MODE_DESCRIPTION,
    MUTATE_NODE_PROPERTY_DESCRIPTION,
    MUTATE_REL_TYPE_DESCRIPTION,
    NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
    RANDOM_SEED_DESCRIPTION,
)

_node_property_steps_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "procedure": {"type": "string"},
            "config": {
                "type": "object",
                "properties": {"mutate_property": {"type": "string"}},
                "required": ["mutate_property"],
            },
        },
        "required": ["procedure", "config"],
    },
    "description": "Optional GDS algorithm steps executed before training to compute extra node properties: [{procedure, config}] where config includes mutate_property (e.g. {procedure: 'fastRP', config: {mutate_property: 'embedding', embedding_dimension: 64}}).",
}


def _model_candidates_description(default_method):
    return (
        "Model candidates [{method, config}] to evaluate; selects the best by the first metric. "
        f"Supports hyperparameter tuning via {{range: [min, max]}} in config. If omitted, adds {{method: '{default_method}'}}."
    )


_auto_tuning_schema = {
    "type": "object",
    "properties": {"max_trials": {"type": "integer"}},
    "description": "Auto-tuning config, e.g. {max_trials: 10} (used when candidate configs contain ranges).",
}

_TRAIN_MODEL_NAME_SCHEMA = {
    "type": "string",
    "description": "Unique name for the trained model in the model catalog.",
}

_FEATURE_PROPERTIES_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
    "description": "Node properties used as features (must exist in the projection or be produced by node_property_steps).",
}

_TARGET_NODE_LABELS_SCHEMA = {
    "type": "array",
    "items": {"type": "string"},
    "description": "Optional node labels to restrict to.",
}

ml_pipeline_tool_definitions = [
    types.Tool(
        name="train_node_classification_model",
        description="Train a supervised node classification model to predict an integer target_property and store it in the model catalog (use predict_node_classification for inference).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": _TRAIN_MODEL_NAME_SCHEMA,
                "target_property": {
                    "type": "string",
                    "description": "Integer node property holding the class label to predict.",
                },
                "feature_properties": _FEATURE_PROPERTIES_SCHEMA,
                "node_property_steps": _node_property_steps_schema,
                "split_config": {
                    "type": "object",
                    "properties": {
                        "test_fraction": {"type": "number"},
                        "validation_folds": {"type": "integer"},
                    },
                    "description": "Train/test split config, e.g. {test_fraction: 0.3, validation_folds: 3}.",
                },
                "model_candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": [
                                    "logistic_regression",
                                    "random_forest",
                                    "mlp",
                                ],
                            },
                            "config": {"type": "object"},
                        },
                        "required": ["method"],
                    },
                    "description": _model_candidates_description("logistic_regression"),
                },
                "auto_tuning_config": _auto_tuning_schema,
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Evaluation metrics, e.g. ACCURACY, F1_WEIGHTED, F1_MACRO, OUT_OF_BAG_ERROR (default: [ACCURACY]).",
                },
                "target_node_labels": _TARGET_NODE_LABELS_SCHEMA,
                "random_seed": RANDOM_SEED_DESCRIPTION,
            },
            "required": [
                "graph_name",
                "model_name",
                "target_property",
                "feature_properties",
            ],
        },
    ),
    types.Tool(
        name="predict_node_classification",
        description="Predict node class labels using a trained model; the graph must contain the feature properties expected by the model.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": {
                    "type": "string",
                    "description": "Name of the trained node classification model in the model catalog.",
                },
                "include_predicted_probabilities": {
                    "type": "boolean",
                    "description": "In stream mode, also return per-class probabilities (default: false).",
                },
                "target_node_labels": _TARGET_NODE_LABELS_SCHEMA,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
                "predicted_probability_property": {
                    "type": "string",
                    "description": "In mutate mode, optional node property to store per-class probabilities.",
                },
            },
            "required": ["graph_name", "model_name"],
        },
    ),
    types.Tool(
        name="train_link_prediction_model",
        description="Train a supervised link prediction model for target_relationship_type and store it in the model catalog (use predict_link_prediction for inference). Requires target_relationship_type to be UNDIRECTED in the projection.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": _TRAIN_MODEL_NAME_SCHEMA,
                "target_relationship_type": {
                    "type": "string",
                    "description": "Relationship type to predict (must be projected as UNDIRECTED).",
                },
                "source_node_label": {
                    "type": "string",
                    "description": "Optional source node label filter.",
                },
                "target_node_label": {
                    "type": "string",
                    "description": "Optional target node label filter.",
                },
                "link_features": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "feature_type": {
                                "type": "string",
                                "enum": ["hadamard", "cosine", "l2", "same_category"],
                            },
                            "node_properties": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["feature_type", "node_properties"],
                    },
                    "description": "Pairwise link feature combiner steps, e.g. [{feature_type: 'hadamard', node_properties: ['embedding']}].",
                },
                "node_property_steps": _node_property_steps_schema,
                "split_config": {
                    "type": "object",
                    "properties": {
                        "train_fraction": {"type": "number"},
                        "test_fraction": {"type": "number"},
                        "validation_folds": {"type": "integer"},
                        "negative_sampling_ratio": {"type": "number"},
                    },
                    "description": "Relationship split config, e.g. {train_fraction: 0.25, test_fraction: 0.25, validation_folds: 3}.",
                },
                "model_candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": [
                                    "logistic_regression",
                                    "random_forest",
                                    "mlp",
                                ],
                            },
                            "config": {"type": "object"},
                        },
                        "required": ["method"],
                    },
                    "description": _model_candidates_description("logistic_regression"),
                },
                "auto_tuning_config": _auto_tuning_schema,
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Evaluation metrics, e.g. AUCPR, OUT_OF_BAG_ERROR (default: [AUCPR]).",
                },
                "negative_class_weight": {
                    "type": "number",
                    "description": "Relative weight of negative examples in the loss function.",
                },
                "random_seed": RANDOM_SEED_DESCRIPTION,
            },
            "required": [
                "graph_name",
                "model_name",
                "target_relationship_type",
                "link_features",
            ],
        },
    ),
    types.Tool(
        name="predict_link_prediction",
        description="Predict new relationships on an undirected projected graph using a trained link prediction model (exhaustive search requires top_n; set sample_rate < 1 for approximate kNN search).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": {
                    "type": "string",
                    "description": "Name of the trained link prediction model in the model catalog.",
                },
                "top_n": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of top predictions to return (required when sample_rate is omitted or 1).",
                },
                "threshold": {
                    "type": "number",
                    "description": "Minimum predicted probability in exhaustive search (default: 0).",
                },
                "sample_rate": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "maximum": 1,
                    "description": "In (0, 1]. Set < 1 to use approximate kNN search instead of exhaustive search (default: 1).",
                },
                "top_k": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Predicted relationships per node when sample_rate < 1 (default: 10).",
                },
                "delta_threshold": {
                    "type": "number",
                    "description": "Early stopping threshold when sample_rate < 1 (default: 0.001).",
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum iterations when sample_rate < 1 (default: 100).",
                },
                "random_joins": {
                    "type": "integer",
                    "description": "Random node comparisons per iteration when sample_rate < 1 (default: 10).",
                },
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_relationship_type": MUTATE_REL_TYPE_DESCRIPTION,
                "mutate_property": {
                    "type": "string",
                    "description": "Relationship property to store predicted probabilities in mutate mode (default: 'probability').",
                },
            },
            "required": ["graph_name", "model_name"],
        },
    ),
    types.Tool(
        name="train_node_regression_model",
        description="Train a supervised node regression model to predict a continuous numeric target_property and store it in the model catalog (use predict_node_regression for inference).",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": _TRAIN_MODEL_NAME_SCHEMA,
                "target_property": {
                    "type": "string",
                    "description": "Continuous numeric node property to predict.",
                },
                "feature_properties": _FEATURE_PROPERTIES_SCHEMA,
                "node_property_steps": _node_property_steps_schema,
                "split_config": {
                    "type": "object",
                    "properties": {
                        "test_fraction": {"type": "number"},
                        "validation_folds": {"type": "integer"},
                    },
                    "description": "Train/test split config, e.g. {test_fraction: 0.3, validation_folds: 3}.",
                },
                "model_candidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["linear_regression", "random_forest"],
                            },
                            "config": {"type": "object"},
                        },
                        "required": ["method"],
                    },
                    "description": _model_candidates_description("linear_regression"),
                },
                "auto_tuning_config": _auto_tuning_schema,
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Evaluation metrics, e.g. MEAN_SQUARED_ERROR, ROOT_MEAN_SQUARED_ERROR, MEAN_ABSOLUTE_ERROR (default: [MEAN_SQUARED_ERROR]).",
                },
                "target_node_labels": _TARGET_NODE_LABELS_SCHEMA,
                "random_seed": RANDOM_SEED_DESCRIPTION,
            },
            "required": [
                "graph_name",
                "model_name",
                "target_property",
                "feature_properties",
            ],
        },
    ),
    types.Tool(
        name="predict_node_regression",
        description="Predict continuous node values using a trained model; the graph must contain the feature properties expected by the model.",
        inputSchema={
            "type": "object",
            "properties": {
                "graph_name": GRAPH_NAME_DESCRIPTION,
                "model_name": {
                    "type": "string",
                    "description": "Name of the trained node regression model in the model catalog.",
                },
                "target_node_labels": _TARGET_NODE_LABELS_SCHEMA,
                "node_identifier_property": NODE_IDENTIFIER_PROPERTY_DESCRIPTION,
                "mode": MODE_DESCRIPTION,
                "mutate_property": MUTATE_NODE_PROPERTY_DESCRIPTION,
            },
            "required": ["graph_name", "model_name"],
        },
    ),
    types.Tool(
        name="list_models",
        description="List all trained ML models in the GDS model catalog (GraphSAGE, node classification, link prediction, node regression) with their configuration and metrics.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    types.Tool(
        name="drop_model",
        description="Remove a trained ML model from the GDS model catalog to free memory.",
        inputSchema={
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Name of the model to drop.",
                }
            },
            "required": ["model_name"],
        },
    ),
]
