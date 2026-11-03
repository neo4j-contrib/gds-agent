import logging
from typing import Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import translate_ids_to_identifiers

logger = logging.getLogger("mcp_server_neo4j_gds")


class FastRPHandler(AlgorithmHandler):
    def fast_rp(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"FastRP parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.fast_rp.mutate(G, **gds_params)
        else:
            result = self.gds.fast_rp.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("node_identifier_property"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.fast_rp(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            embedding_dimension=arguments.get("embedding_dimension"),
            iteration_weights=arguments.get("iteration_weights"),
            normalization_strength=arguments.get("normalization_strength"),
            node_self_influence=arguments.get("node_self_influence"),
            property_ratio=arguments.get("property_ratio"),
            feature_properties=arguments.get("feature_properties"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            random_seed=arguments.get("random_seed"),
        )


class Node2VecHandler(AlgorithmHandler):
    def node2vec(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Node2Vec parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.node2vec.mutate(G, **gds_params)
        else:
            result = self.gds.node2vec.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("node_identifier_property"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.node2vec(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            embedding_dimension=arguments.get("embedding_dimension"),
            walk_length=arguments.get("walk_length"),
            walks_per_node=arguments.get("walks_per_node"),
            in_out_factor=arguments.get("in_out_factor"),
            return_factor=arguments.get("return_factor"),
            window_size=arguments.get("window_size"),
            negative_sampling_rate=arguments.get("negative_sampling_rate"),
            positive_sampling_factor=arguments.get("positive_sampling_factor"),
            embedding_initializer=arguments.get("embedding_initializer"),
            iterations=arguments.get("iterations"),
            initial_learning_rate=arguments.get("initial_learning_rate"),
            min_learning_rate=arguments.get("min_learning_rate"),
            walk_buffer_size=arguments.get("walk_buffer_size"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            random_seed=arguments.get("random_seed"),
        )


class HashGNNHandler(AlgorithmHandler):
    def hash_gnn(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"HashGNN parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.hash_gnn.mutate(G, **gds_params)
        else:
            result = self.gds.hash_gnn.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("node_identifier_property"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.hash_gnn(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            iterations=arguments.get("iterations"),
            embedding_density=arguments.get("embedding_density"),
            feature_properties=arguments.get("feature_properties"),
            generate_features=arguments.get("generate_features"),
            binarize_features=arguments.get("binarize_features"),
            heterogeneous=arguments.get("heterogeneous"),
            neighbor_influence=arguments.get("neighbor_influence"),
            output_dimension=arguments.get("output_dimension"),
            random_seed=arguments.get("random_seed"),
        )


class GraphSageTrainHandler(AlgorithmHandler):
    def graph_sage_train(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(kwargs, ["graph_name"])
        logger.info(f"GraphSAGE train parameters: {gds_params}")
        model, result = self.gds.graph_sage.train(G, **gds_params)
        return {"modelName": model.name(), "trainResult": result.model_dump()}

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.graph_sage_train(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            feature_properties=arguments.get("feature_properties"),
            embedding_dimension=arguments.get("embedding_dimension"),
            aggregator=arguments.get("aggregator"),
            activation_function=arguments.get("activation_function"),
            sample_sizes=arguments.get("sample_sizes"),
            epochs=arguments.get("epochs"),
            max_iterations=arguments.get("max_iterations"),
            search_depth=arguments.get("search_depth"),
            batch_size=arguments.get("batch_size"),
            learning_rate=arguments.get("learning_rate"),
            tolerance=arguments.get("tolerance"),
            negative_sample_weight=arguments.get("negative_sample_weight"),
            penaltyL2=arguments.get("penalty_l2"),
            projected_feature_dimension=arguments.get("projected_feature_dimension"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            random_seed=arguments.get("random_seed"),
        )


class GraphSagePredictHandler(AlgorithmHandler):
    def graph_sage_predict(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        model_name = kwargs.get("model_name")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        model = self.gds.graph_sage.get(model_name)
        gds_params = clean_params(
            kwargs, ["graph_name", "model_name", "mode", "node_identifier_property"]
        )
        logger.info(f"GraphSAGE predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("node_identifier_property"), result
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.graph_sage_predict(
            graph_name=arguments.get("graph_name"),
            model_name=arguments.get("model_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            batch_size=arguments.get("batch_size"),
        )
