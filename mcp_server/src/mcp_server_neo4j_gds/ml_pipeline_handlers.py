import logging
import uuid
from contextlib import suppress
from typing import Any, Dict

from graphdatascience.model.link_prediction_model import LPModel
from graphdatascience.model.node_classification_model import NCModel
from graphdatascience.model.node_regression_model import NRModel

from .algorithm_handler import AlgorithmHandler, clean_params
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
        pipeline.addNodeProperty(step["procedure"], **(step.get("config") or {}))


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
        getattr(pipeline, methods[method])(**(candidate.get("config") or {}))


def configure_pipeline(pipeline, kwargs, default_method, methods):
    add_node_property_steps(pipeline, kwargs.get("nodePropertySteps"))
    if kwargs.get("splitConfig"):
        pipeline.configureSplit(**kwargs["splitConfig"])
    add_model_candidates(
        pipeline, kwargs.get("modelCandidates"), default_method, methods
    )
    if kwargs.get("autoTuningConfig"):
        pipeline.configureAutoTuning(**kwargs["autoTuningConfig"])


def train_pipeline(gds, pipeline, kwargs, default_metrics):
    G = gds.graph.get(kwargs.get("graphName"))
    train_params = clean_params(kwargs, PIPELINE_CONFIG_KEYS)
    train_params.setdefault("metrics", default_metrics)
    logger.info(f"Pipeline train parameters: {train_params}")
    model, result = pipeline.train(G, **train_params)
    return {"modelName": model.name(), "trainResult": result.to_dict()}


def get_model(gds, model_name, expected_type, train_tool):
    model = gds.model.get(model_name)
    if not isinstance(model, expected_type):
        raise ValueError(
            f"Model '{model_name}' is not a {expected_type.__name__} model "
            f"(type: {model.type()}). Use {train_tool} to train one."
        )
    return model


class NodeClassificationTrainHandler(AlgorithmHandler):
    def train_node_classification_model(self, **kwargs):
        pipeline = self.gds.nc_pipe(f"nc_pipeline_{uuid.uuid4().hex[:8]}")
        try:
            pipeline.selectFeatures(kwargs.get("featureProperties"))
            configure_pipeline(
                pipeline,
                kwargs,
                "logisticRegression",
                {
                    "logisticRegression": "addLogisticRegression",
                    "randomForest": "addRandomForest",
                    "mlp": "addMLP",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["ACCURACY"])
        finally:
            with suppress(Exception):
                pipeline.drop(failIfMissing=False)

    def execute(self, arguments: Dict[str, Any]) -> Any:
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
            self.gds,
            kwargs.get("modelName"),
            NCModel,
            "train_node_classification_model",
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

    def execute(self, arguments: Dict[str, Any]) -> Any:
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
        pipeline = self.gds.lp_pipe(f"lp_pipeline_{uuid.uuid4().hex[:8]}")
        try:
            for feature in kwargs.get("linkFeatures") or []:
                pipeline.addFeature(
                    feature["featureType"], nodeProperties=feature["nodeProperties"]
                )
            configure_pipeline(
                pipeline,
                kwargs,
                "logisticRegression",
                {
                    "logisticRegression": "addLogisticRegression",
                    "randomForest": "addRandomForest",
                    "mlp": "addMLP",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["AUCPR"])
        finally:
            with suppress(Exception):
                pipeline.drop(failIfMissing=False)

    def execute(self, arguments: Dict[str, Any]) -> Any:
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
            self.gds, kwargs.get("modelName"), LPModel, "train_link_prediction_model"
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

    def execute(self, arguments: Dict[str, Any]) -> Any:
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
        pipeline = self.gds.nr_pipe(f"nr_pipeline_{uuid.uuid4().hex[:8]}")
        try:
            pipeline.selectFeatures(kwargs.get("featureProperties"))
            configure_pipeline(
                pipeline,
                kwargs,
                "linearRegression",
                {
                    "linearRegression": "addLinearRegression",
                    "randomForest": "addRandomForest",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["MEAN_SQUARED_ERROR"])
        finally:
            with suppress(Exception):
                pipeline.drop(failIfMissing=False)

    def execute(self, arguments: Dict[str, Any]) -> Any:
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
            self.gds, kwargs.get("modelName"), NRModel, "train_node_regression_model"
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

    def execute(self, arguments: Dict[str, Any]) -> Any:
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
        models_df = self.gds.model.list()
        if models_df.empty:
            return {"models": [], "count": 0}
        models = models_df.to_dict(orient="records")
        return {"models": models, "count": len(models)}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.list_models()


class DropModelHandler(AlgorithmHandler):
    def drop_model(self, model_name: str):
        model = self.gds.model.get(model_name)
        model.drop(failIfMissing=False)
        return {"modelName": model_name, "dropped": True}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.drop_model(model_name=arguments.get("modelName"))
