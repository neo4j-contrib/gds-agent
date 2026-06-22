from mcp import types

_node_property_steps_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "procedure": {"type": "string"},
            "config": {"type": "object"},
        },
        "required": ["procedure"],
    },
    "description": "Optional GDS algorithm steps executed on the graph before training to produce extra node properties, in order. "
    "Each step is {procedure, config} where procedure is a GDS algorithm name (e.g. 'fastRP', 'degree', 'pageRank', 'beta.hashgnn') and config is its mutate-mode configuration "
    "(must include mutateProperty; e.g. {mutateProperty: 'embedding', embeddingDimension: 64}). "
    "Properties produced here can be used as features.",
}


def _model_candidates_description(default_method):
    return (
        "Model candidates to evaluate during training; the best one (by the first metric) is selected. "
        "Each entry is {method, config}. "
        "Hyperparameter ranges for auto-tuning can be given as {range: [min, max]} values inside config. "
        f"If omitted, a single default candidate is added ({default_method})."
    )


_auto_tuning_schema = {
    "type": "object",
    "properties": {"maxTrials": {"type": "integer"}},
    "description": "Auto-tuning configuration, e.g. {maxTrials: 10}. Only relevant when model candidate configs contain ranges.",
}

ml_pipeline_tool_definitions = [
    types.Tool(
        name="train_node_classification_model",
        description="Train a node classification model on a projected graph and store it in the GDS model catalog under modelName. "
        "Node classification predicts a categorical node property (the targetProperty) from feature properties using supervised machine learning. "
        "This tool builds a GDS node classification pipeline (node property steps, feature selection, train/test split, model candidates), trains it, "
        "evaluates it with the given metrics, and cleans up the temporary pipeline. "
        "The targetProperty must be an integer property in the projected graph, and all feature properties must exist in the projection "
        "(either projected from the database or produced by nodePropertySteps). "
        "Use predict_node_classification to apply the trained model.",
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
                "targetProperty": {
                    "type": "string",
                    "description": "Node property holding the class label to predict. Must be an integer property in the projected graph.",
                },
                "featureProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Node properties to use as model features. Each must exist in the projected graph or be produced by nodePropertySteps.",
                },
                "nodePropertySteps": _node_property_steps_schema,
                "splitConfig": {
                    "type": "object",
                    "properties": {
                        "testFraction": {"type": "number"},
                        "validationFolds": {"type": "integer"},
                    },
                    "description": "Train/test split configuration, e.g. {testFraction: 0.3, validationFolds: 3}.",
                },
                "modelCandidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": [
                                    "logisticRegression",
                                    "randomForest",
                                    "mlp",
                                ],
                            },
                            "config": {"type": "object"},
                        },
                        "required": ["method"],
                    },
                    "description": _model_candidates_description("logistic regression"),
                },
                "autoTuningConfig": _auto_tuning_schema,
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Evaluation metrics, e.g. ACCURACY, F1_WEIGHTED, F1_MACRO, OUT_OF_BAG_ERROR. Default is [ACCURACY].",
                },
                "targetNodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional node labels to restrict training to.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "A random seed for reproducible training.",
                },
            },
            "required": [
                "graphName",
                "modelName",
                "targetProperty",
                "featureProperties",
            ],
        },
    ),
    types.Tool(
        name="predict_node_classification",
        description="Predict class labels for nodes in a projected graph using a trained node classification model from the model catalog "
        "(see train_node_classification_model). "
        "The graph must contain the feature properties the model was trained on. "
        "Stream mode returns predicted classes (and optionally probabilities) per node; mutate mode writes predictions to the in-memory graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to predict on.",
                },
                "modelName": {
                    "type": "string",
                    "description": "Name of the trained node classification model in the model catalog.",
                },
                "includePredictedProbabilities": {
                    "type": "boolean",
                    "description": "In stream mode, also return the predicted probability per class. Default is false.",
                },
                "targetNodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional node labels to restrict prediction to.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns predictions as a table, 'mutate' writes predictions to the in-memory graph as a node property. Default is 'stream'.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write predicted classes to.",
                },
                "predictedProbabilityProperty": {
                    "type": "string",
                    "description": "In mutate mode, optionally also write per-class probabilities to this node property.",
                },
            },
            "required": ["graphName", "modelName"],
        },
    ),
    types.Tool(
        name="train_link_prediction_model",
        description="Train a link prediction model on a projected graph and store it in the GDS model catalog under modelName. "
        "Link prediction predicts missing or future relationships of the targetRelationshipType between node pairs, using link features "
        "computed by combining node properties (e.g. embeddings) of both nodes. "
        "This tool builds a GDS link prediction pipeline (node property steps, link features, relationship split, model candidates), trains it, "
        "and cleans up the temporary pipeline. "
        "IMPORTANT: the projected graph must contain UNDIRECTED relationships of the targetRelationshipType; project with undirectedRelationshipTypes. "
        "Use predict_link_prediction to apply the trained model.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to train on. Must contain undirected relationships of the targetRelationshipType.",
                },
                "modelName": {
                    "type": "string",
                    "description": "Unique name for the trained model in the model catalog.",
                },
                "targetRelationshipType": {
                    "type": "string",
                    "description": "The relationship type to learn to predict. Must be undirected in the projection.",
                },
                "sourceNodeLabel": {
                    "type": "string",
                    "description": "Optional node label of relationship source nodes to learn from.",
                },
                "targetNodeLabel": {
                    "type": "string",
                    "description": "Optional node label of relationship target nodes to learn from.",
                },
                "linkFeatures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "featureType": {
                                "type": "string",
                                "enum": ["hadamard", "cosine", "l2", "sameCategory"],
                            },
                            "nodeProperties": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["featureType", "nodeProperties"],
                    },
                    "description": "How to combine node properties of a node pair into link features, e.g. [{featureType: 'hadamard', nodeProperties: ['embedding']}]. "
                    "Node properties must exist in the projection or be produced by nodePropertySteps.",
                },
                "nodePropertySteps": _node_property_steps_schema,
                "splitConfig": {
                    "type": "object",
                    "properties": {
                        "trainFraction": {"type": "number"},
                        "testFraction": {"type": "number"},
                        "validationFolds": {"type": "integer"},
                        "negativeSamplingRatio": {"type": "number"},
                    },
                    "description": "Relationship split configuration, e.g. {trainFraction: 0.25, testFraction: 0.25, validationFolds: 3}.",
                },
                "modelCandidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": [
                                    "logisticRegression",
                                    "randomForest",
                                    "mlp",
                                ],
                            },
                            "config": {"type": "object"},
                        },
                        "required": ["method"],
                    },
                    "description": _model_candidates_description("logistic regression"),
                },
                "autoTuningConfig": _auto_tuning_schema,
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Evaluation metrics, e.g. AUCPR, OUT_OF_BAG_ERROR. Default is [AUCPR].",
                },
                "negativeClassWeight": {
                    "type": "number",
                    "description": "Weight of negative examples in the loss. Positive examples have weight 1.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "A random seed for reproducible training.",
                },
            },
            "required": [
                "graphName",
                "modelName",
                "targetRelationshipType",
                "linkFeatures",
            ],
        },
    ),
    types.Tool(
        name="predict_link_prediction",
        description="Predict new relationships in a projected graph using a trained link prediction model from the model catalog "
        "(see train_link_prediction_model). "
        "The graph must contain the node properties the model's link features were built from, and the relationships must be undirected. "
        "Stream mode returns predicted node pairs with probabilities; mutate mode writes the top predicted relationships to the in-memory graph. "
        "By default an exhaustive search over all node pairs is used and topN is required; set sampleRate below 1 for a faster approximate search.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to predict on.",
                },
                "modelName": {
                    "type": "string",
                    "description": "Name of the trained link prediction model in the model catalog.",
                },
                "topN": {
                    "type": "integer",
                    "description": "Limit on the number of predicted relationships to output, ordered by probability. Required when sampleRate is 1 (the default exhaustive search).",
                },
                "threshold": {
                    "type": "number",
                    "description": "Minimum predicted probability for a relationship to be output (exhaustive search only). Default is 0.",
                },
                "sampleRate": {
                    "type": "number",
                    "description": "Between 0 and 1. If below 1, an approximate K-nearest-neighbor-based search is used instead of scoring every node pair. Default is 1.",
                },
                "topK": {
                    "type": "integer",
                    "description": "For approximate search (sampleRate below 1): number of predicted relationships to output per node. Default is 10.",
                },
                "deltaThreshold": {
                    "type": "number",
                    "description": "For approximate search: early stopping threshold as a fraction of updated potential relationships. Default is 0.001.",
                },
                "maxIterations": {
                    "type": "integer",
                    "description": "For approximate search: maximum number of iterations. Default is 100.",
                },
                "randomJoins": {
                    "type": "integer",
                    "description": "For approximate search: number of random node comparisons per iteration. Default is 10.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns predicted node pairs as a table, 'mutate' writes predicted relationships to the in-memory graph. Default is 'stream'.",
                },
                "mutateRelationshipType": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The relationship type to use for the new predicted relationships.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "In mutate mode, the relationship property to store the predicted probability in. Default is 'probability'.",
                },
            },
            "required": ["graphName", "modelName"],
        },
    ),
    types.Tool(
        name="train_node_regression_model",
        description="Train a node regression model on a projected graph and store it in the GDS model catalog under modelName. "
        "Node regression predicts a continuous numeric node property (the targetProperty) from feature properties using supervised machine learning. "
        "This tool builds a GDS node regression pipeline (node property steps, feature selection, train/test split, model candidates), trains it, "
        "and cleans up the temporary pipeline. "
        "The targetProperty and all feature properties must exist in the projected graph "
        "(either projected from the database or produced by nodePropertySteps). "
        "Use predict_node_regression to apply the trained model.",
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
                "targetProperty": {
                    "type": "string",
                    "description": "Numeric node property to predict.",
                },
                "featureProperties": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Node properties to use as model features. Each must exist in the projected graph or be produced by nodePropertySteps.",
                },
                "nodePropertySteps": _node_property_steps_schema,
                "splitConfig": {
                    "type": "object",
                    "properties": {
                        "testFraction": {"type": "number"},
                        "validationFolds": {"type": "integer"},
                    },
                    "description": "Train/test split configuration, e.g. {testFraction: 0.3, validationFolds: 3}.",
                },
                "modelCandidates": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": ["linearRegression", "randomForest"],
                            },
                            "config": {"type": "object"},
                        },
                        "required": ["method"],
                    },
                    "description": _model_candidates_description("linear regression"),
                },
                "autoTuningConfig": _auto_tuning_schema,
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Evaluation metrics, e.g. MEAN_SQUARED_ERROR, ROOT_MEAN_SQUARED_ERROR, MEAN_ABSOLUTE_ERROR. Default is [MEAN_SQUARED_ERROR].",
                },
                "targetNodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional node labels to restrict training to.",
                },
                "randomSeed": {
                    "type": "integer",
                    "description": "A random seed for reproducible training.",
                },
            },
            "required": [
                "graphName",
                "modelName",
                "targetProperty",
                "featureProperties",
            ],
        },
    ),
    types.Tool(
        name="predict_node_regression",
        description="Predict numeric values for nodes in a projected graph using a trained node regression model from the model catalog "
        "(see train_node_regression_model). "
        "The graph must contain the feature properties the model was trained on. "
        "Stream mode returns the predicted value per node; mutate mode writes predictions to the in-memory graph.",
        inputSchema={
            "type": "object",
            "properties": {
                "graphName": {
                    "type": "string",
                    "description": "Name of the projected graph to predict on.",
                },
                "modelName": {
                    "type": "string",
                    "description": "Name of the trained node regression model in the model catalog.",
                },
                "targetNodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional node labels to restrict prediction to.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes in stream output (e.g., 'name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["stream", "mutate"],
                    "description": "Execution mode: 'stream' returns predictions as a table, 'mutate' writes predictions to the in-memory graph as a node property. Default is 'stream'.",
                },
                "mutateProperty": {
                    "type": "string",
                    "description": "Required when mode is 'mutate'. The name of the node property to write predicted values to.",
                },
            },
            "required": ["graphName", "modelName"],
        },
    ),
    types.Tool(
        name="list_models",
        description="List all machine learning models in the GDS model catalog (GraphSAGE, node classification, link prediction, node regression) "
        "with their type, training configuration, and metrics. "
        "Models are created by graph_sage_train, train_node_classification_model, train_link_prediction_model, and train_node_regression_model.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    types.Tool(
        name="drop_model",
        description="Remove a trained machine learning model from the GDS model catalog to free memory. "
        "This does not affect the underlying data in the Neo4j database or any projected graphs.",
        inputSchema={
            "type": "object",
            "properties": {
                "modelName": {
                    "type": "string",
                    "description": "Name of the model to drop. Use list_models to see available models.",
                }
            },
            "required": ["modelName"],
        },
    ),
]
