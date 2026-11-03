import logging
import uuid
from contextlib import suppress
from typing import Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import translate_ids_to_identifiers

logger = logging.getLogger("mcp_server_neo4j_gds")

PIPELINE_CONFIG_KEYS = [
    "graph_name",
    "node_property_steps",
    "feature_properties",
    "link_features",
    "split_config",
    "model_candidates",
    "auto_tuning_config",
]


def add_node_property_steps(pipeline, steps):
    for step in steps or []:
        pipeline.add_node_property(step["procedure"], **(step.get("config") or {}))


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
    add_node_property_steps(pipeline, kwargs.get("node_property_steps"))
    if kwargs.get("split_config"):
        pipeline.configure_split(**kwargs["split_config"])
    add_model_candidates(
        pipeline, kwargs.get("model_candidates"), default_method, methods
    )
    if kwargs.get("auto_tuning_config"):
        pipeline.configure_auto_tuning(**kwargs["auto_tuning_config"])


def train_pipeline(gds, pipeline, kwargs, default_metrics):
    G = gds.graph.get(kwargs.get("graph_name"))
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
            pipeline.select_features(kwargs.get("feature_properties"))
            configure_pipeline(
                pipeline,
                kwargs,
                "logistic_regression",
                {
                    "logistic_regression": "add_logistic_regression",
                    "random_forest": "add_random_forest",
                    "mlp": "add_mlp",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["ACCURACY"])
        finally:
            with suppress(Exception):
                pipeline.drop(fail_if_missing=False)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.train_node_classification_model(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            target_property=arguments.get("target_property"),
            feature_properties=arguments.get("feature_properties"),
            node_property_steps=arguments.get("node_property_steps"),
            split_config=arguments.get("split_config"),
            model_candidates=arguments.get("model_candidates"),
            auto_tuning_config=arguments.get("auto_tuning_config"),
            metrics=arguments.get("metrics"),
            target_node_labels=arguments.get("target_node_labels"),
            random_seed=arguments.get("random_seed"),
        )


class NodeClassificationPredictHandler(AlgorithmHandler):
    def predict_node_classification(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        model = get_model(
            kwargs.get("model_name"),
            self.gds.pipeline.node_classification.get_model,
        )
        gds_params = clean_params(
            kwargs, ["graph_name", "model_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Node classification predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("node_identifier_property"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.predict_node_classification(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            predicted_probability_property=arguments.get(
                "predicted_probability_property"
            ),
            include_predicted_probabilities=arguments.get(
                "include_predicted_probabilities"
            ),
            target_node_labels=arguments.get("target_node_labels"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class LinkPredictionTrainHandler(AlgorithmHandler):
    def train_link_prediction_model(self, **kwargs):
        pipeline, _ = self.gds.pipeline.link_prediction.create(
            f"lp_pipeline_{uuid.uuid4().hex[:8]}"
        )
        try:
            for feature in kwargs.get("link_features") or []:
                pipeline.add_feature(
                    feature["feature_type"],
                    node_properties=feature["node_properties"],
                )
            configure_pipeline(
                pipeline,
                kwargs,
                "logistic_regression",
                {
                    "logistic_regression": "add_logistic_regression",
                    "random_forest": "add_random_forest",
                    "mlp": "add_mlp",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["AUCPR"])
        finally:
            with suppress(Exception):
                pipeline.drop(fail_if_missing=False)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.train_link_prediction_model(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            target_relationship_type=arguments.get("target_relationship_type"),
            source_node_label=arguments.get("source_node_label"),
            target_node_label=arguments.get("target_node_label"),
            link_features=arguments.get("link_features"),
            node_property_steps=arguments.get("node_property_steps"),
            split_config=arguments.get("split_config"),
            model_candidates=arguments.get("model_candidates"),
            auto_tuning_config=arguments.get("auto_tuning_config"),
            metrics=arguments.get("metrics"),
            negative_class_weight=arguments.get("negative_class_weight"),
            random_seed=arguments.get("random_seed"),
        )


class LinkPredictionPredictHandler(AlgorithmHandler):
    def predict_link_prediction(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        model = get_model(
            kwargs.get("model_name"),
            self.gds.pipeline.link_prediction.get_model,
        )
        gds_params = clean_params(
            kwargs, ["graph_name", "model_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Link prediction predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            node_identifier_property = kwargs.get("node_identifier_property")
            translate_ids_to_identifiers(
                self.gds, node_identifier_property, result, "node1", "node1Name"
            )
            translate_ids_to_identifiers(
                self.gds, node_identifier_property, result, "node2", "node2Name"
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.predict_link_prediction(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            mode=arguments.get("mode"),
            mutate_relationship_type=arguments.get("mutate_relationship_type"),
            mutate_property=arguments.get("mutate_property"),
            top_n=arguments.get("top_n"),
            threshold=arguments.get("threshold"),
            sample_rate=arguments.get("sample_rate"),
            top_k=arguments.get("top_k"),
            delta_threshold=arguments.get("delta_threshold"),
            max_iterations=arguments.get("max_iterations"),
            random_joins=arguments.get("random_joins"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class NodeRegressionTrainHandler(AlgorithmHandler):
    def train_node_regression_model(self, **kwargs):
        pipeline, _ = self.gds.pipeline.node_regression.create(
            f"nr_pipeline_{uuid.uuid4().hex[:8]}"
        )
        try:
            pipeline.select_features(kwargs.get("feature_properties"))
            configure_pipeline(
                pipeline,
                kwargs,
                "linear_regression",
                {
                    "linear_regression": "add_linear_regression",
                    "random_forest": "add_random_forest",
                },
            )
            return train_pipeline(self.gds, pipeline, kwargs, ["MEAN_SQUARED_ERROR"])
        finally:
            with suppress(Exception):
                pipeline.drop(fail_if_missing=False)

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.train_node_regression_model(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            target_property=arguments.get("target_property"),
            feature_properties=arguments.get("feature_properties"),
            node_property_steps=arguments.get("node_property_steps"),
            split_config=arguments.get("split_config"),
            model_candidates=arguments.get("model_candidates"),
            auto_tuning_config=arguments.get("auto_tuning_config"),
            metrics=arguments.get("metrics"),
            target_node_labels=arguments.get("target_node_labels"),
            random_seed=arguments.get("random_seed"),
        )


class NodeRegressionPredictHandler(AlgorithmHandler):
    def predict_node_regression(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        model = get_model(
            kwargs.get("model_name"),
            self.gds.pipeline.node_regression.get_model,
        )
        gds_params = clean_params(
            kwargs, ["graph_name", "model_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Node regression predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("node_identifier_property"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.predict_node_regression(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            target_node_labels=arguments.get("target_node_labels"),
            node_identifier_property=arguments.get("node_identifier_property"),
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
        return self.drop_model(model_name=arguments.get("model_name"))
