import logging
import uuid
from contextlib import suppress
from typing import Any

from .algorithm_handler import AlgorithmHandler, clean_params, snake_case_keys
from .node_translator import translate_ids_to_identifiers

logger = logging.getLogger("mcp_server_neo4j_gds")

PIPELINE_CONFIG_KEYS = [
    "graphName",
    "nodePropertySteps",
    "featureProperties",
    "linkFeatures",
    "splitConfig",
    "modelCandidates",
    "autoTuningConfig",
]


def add_node_property_steps(pipeline, steps):
    for step in steps or []:
        pipeline.add_node_property(
            step["procedure"], **snake_case_keys(step.get("config") or {})
        )


def add_model_candidates(pipeline, candidates, default_method, methods):
    if not candidates:
        candidates = [{"method": default_method}]
    for candidate in candidates:
        method = candidate.get("method")
        if method not in methods:
            raise ValueError(
                f"Unsupported model candidate method '{method}'. "
                f"Supported methods: {sorted(methods)}"
            )
        getattr(pipeline, methods[method])(
            **snake_case_keys(candidate.get("config") or {})
        )


def configure_pipeline(pipeline, kwargs, default_method, methods):
    add_node_property_steps(pipeline, kwargs.get("nodePropertySteps"))
    if kwargs.get("splitConfig"):
        pipeline.configure_split(**snake_case_keys(kwargs["splitConfig"]))
    add_model_candidates(
        pipeline, kwargs.get("modelCandidates"), default_method, methods
    )
    if kwargs.get("autoTuningConfig"):
        pipeline.configure_auto_tuning(**snake_case_keys(kwargs["autoTuningConfig"]))


def train_pipeline(gds, pipeline, kwargs, default_metrics):
    G = gds.graph.get(kwargs.get("graphName"))
    train_params = clean_params(kwargs, PIPELINE_CONFIG_KEYS)
    train_params.setdefault("metrics", default_metrics)
    logger.info(f"Pipeline train parameters: {train_params}")
    model, result = pipeline.train(G, **train_params)
    return {"modelName": model.name(), "trainResult": result.model_dump()}


def get_model(model_name, getter):
    return getter(model_name)


class NodeClassificationTrainHandler(AlgorithmHandler):
    def train_node_classification_model(self, **kwargs):
        pipeline, _ = self.gds.pipeline.node_classification.create(
            f"nc_pipeline_{uuid.uuid4().hex[:8]}"
        )
        try:
            pipeline.select_features(kwargs.get("featureProperties"))
            configure_pipeline(
                pipeline,
                kwargs,
                "logisticRegression",
                {
                    "logisticRegression": "add_logistic_regression",
                    "randomForest": "add_random_forest",
                    "mlp": "add_mlp",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["ACCURACY"])
        finally:
            with suppress(Exception):
                pipeline.drop(fail_if_missing=False)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.train_node_classification_model(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            targetProperty=arguments.get("targetProperty"),
            featureProperties=arguments.get("featureProperties"),
            nodePropertySteps=arguments.get("nodePropertySteps"),
            splitConfig=arguments.get("splitConfig"),
            modelCandidates=arguments.get("modelCandidates"),
            autoTuningConfig=arguments.get("autoTuningConfig"),
            metrics=arguments.get("metrics"),
            targetNodeLabels=arguments.get("targetNodeLabels"),
            randomSeed=arguments.get("randomSeed"),
        )


class NodeClassificationPredictHandler(AlgorithmHandler):
    def predict_node_classification(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        model = get_model(
            kwargs.get("modelName"),
            self.gds.pipeline.node_classification.get_model,
        )
        gds_params = clean_params(
            kwargs, ["graphName", "modelName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Node classification predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("nodeIdentifierProperty"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.predict_node_classification(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            predictedProbabilityProperty=arguments.get("predictedProbabilityProperty"),
            includePredictedProbabilities=arguments.get(
                "includePredictedProbabilities"
            ),
            targetNodeLabels=arguments.get("targetNodeLabels"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class LinkPredictionTrainHandler(AlgorithmHandler):
    def train_link_prediction_model(self, **kwargs):
        pipeline, _ = self.gds.pipeline.link_prediction.create(
            f"lp_pipeline_{uuid.uuid4().hex[:8]}"
        )
        try:
            for feature in kwargs.get("linkFeatures") or []:
                pipeline.add_feature(
                    feature["featureType"],
                    node_properties=feature["nodeProperties"],
                )
            configure_pipeline(
                pipeline,
                kwargs,
                "logisticRegression",
                {
                    "logisticRegression": "add_logistic_regression",
                    "randomForest": "add_random_forest",
                    "mlp": "add_mlp",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["AUCPR"])
        finally:
            with suppress(Exception):
                pipeline.drop(fail_if_missing=False)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.train_link_prediction_model(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            targetRelationshipType=arguments.get("targetRelationshipType"),
            sourceNodeLabel=arguments.get("sourceNodeLabel"),
            targetNodeLabel=arguments.get("targetNodeLabel"),
            linkFeatures=arguments.get("linkFeatures"),
            nodePropertySteps=arguments.get("nodePropertySteps"),
            splitConfig=arguments.get("splitConfig"),
            modelCandidates=arguments.get("modelCandidates"),
            autoTuningConfig=arguments.get("autoTuningConfig"),
            metrics=arguments.get("metrics"),
            negativeClassWeight=arguments.get("negativeClassWeight"),
            randomSeed=arguments.get("randomSeed"),
        )


class LinkPredictionPredictHandler(AlgorithmHandler):
    def predict_link_prediction(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        model = get_model(
            kwargs.get("modelName"),
            self.gds.pipeline.link_prediction.get_model,
        )
        gds_params = clean_params(
            kwargs, ["graphName", "modelName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Link prediction predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            translate_ids_to_identifiers(
                self.gds, node_identifier_property, result, "node1", "node1Name"
            )
            translate_ids_to_identifiers(
                self.gds, node_identifier_property, result, "node2", "node2Name"
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.predict_link_prediction(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
            mutateProperty=arguments.get("mutateProperty"),
            topN=arguments.get("topN"),
            threshold=arguments.get("threshold"),
            sampleRate=arguments.get("sampleRate"),
            topK=arguments.get("topK"),
            deltaThreshold=arguments.get("deltaThreshold"),
            maxIterations=arguments.get("maxIterations"),
            randomJoins=arguments.get("randomJoins"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class NodeRegressionTrainHandler(AlgorithmHandler):
    def train_node_regression_model(self, **kwargs):
        pipeline, _ = self.gds.pipeline.node_regression.create(
            f"nr_pipeline_{uuid.uuid4().hex[:8]}"
        )
        try:
            pipeline.select_features(kwargs.get("featureProperties"))
            configure_pipeline(
                pipeline,
                kwargs,
                "linearRegression",
                {
                    "linearRegression": "add_linear_regression",
                    "randomForest": "add_random_forest",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["MEAN_SQUARED_ERROR"])
        finally:
            with suppress(Exception):
                pipeline.drop(fail_if_missing=False)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.train_node_regression_model(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            targetProperty=arguments.get("targetProperty"),
            featureProperties=arguments.get("featureProperties"),
            nodePropertySteps=arguments.get("nodePropertySteps"),
            splitConfig=arguments.get("splitConfig"),
            modelCandidates=arguments.get("modelCandidates"),
            autoTuningConfig=arguments.get("autoTuningConfig"),
            metrics=arguments.get("metrics"),
            targetNodeLabels=arguments.get("targetNodeLabels"),
            randomSeed=arguments.get("randomSeed"),
        )


class NodeRegressionPredictHandler(AlgorithmHandler):
    def predict_node_regression(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        model = get_model(
            kwargs.get("modelName"),
            self.gds.pipeline.node_regression.get_model,
        )
        gds_params = clean_params(
            kwargs, ["graphName", "modelName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Node regression predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("nodeIdentifierProperty"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.predict_node_regression(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            targetNodeLabels=arguments.get("targetNodeLabels"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class ListModelsHandler(AlgorithmHandler):
    def list_models(self, **kwargs):
        model_details = self.gds.model.list()
        if not model_details:
            return {"models": [], "count": 0}
        models = [model.model_dump(by_alias=True) for model in model_details]
        return {"models": models, "count": len(models)}

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.list_models()


class DropModelHandler(AlgorithmHandler):
    def drop_model(self, model_name: str):
        self.gds.model.drop(model_name, fail_if_missing=False)
        return {"modelName": model_name, "dropped": True}

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.drop_model(model_name=arguments.get("modelName"))
