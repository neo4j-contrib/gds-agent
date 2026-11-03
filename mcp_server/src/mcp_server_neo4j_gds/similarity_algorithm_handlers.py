import logging
from typing import Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import (
    translate_identifiers_to_ids,
    translate_ids_to_identifiers,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class NodeSimilarityHandler(AlgorithmHandler):
    def node_similarity(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs,
            [
                "graph_name",
                "node_identifier_property",
                "source_node_filter",
                "target_node_filter",
                "mode",
            ],
        )
        node_identifier_property = kwargs.get("node_identifier_property")
        source_nodes = kwargs.get("source_node_filter", None)
        target_nodes = kwargs.get("target_node_filter", None)
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "source_node_filter",
            node_identifier_property,
            gds_params,
        )
        translate_identifiers_to_ids(
            self.gds,
            target_nodes,
            "target_node_filter",
            node_identifier_property,
            gds_params,
        )
        logger.info(f"Node Similarity parameters: {gds_params}")
        use_filtered = (
            "source_node_filter" in gds_params or "target_node_filter" in gds_params
        )
        if use_filtered:
            # .filtered requires both args; default missing one to None so ConfigConverter skips it
            gds_params.setdefault("source_node_filter", None)
            gds_params.setdefault("target_node_filter", None)
        if mode == "mutate":
            if use_filtered:
                result = self.gds.node_similarity.filtered.mutate(G, **gds_params)
            else:
                result = self.gds.node_similarity.mutate(G, **gds_params)
        else:
            if use_filtered:
                result = self.gds.node_similarity.filtered.stream(G, **gds_params)
            else:
                result = self.gds.node_similarity.stream(G, **gds_params)

            node_identifier_property = kwargs.get("node_identifier_property")
            translate_ids_to_identifiers(
                self.gds,
                node_identifier_property,
                result,
                "node1",
                "node1Name",
            )
            translate_ids_to_identifiers(
                self.gds,
                node_identifier_property,
                result,
                "node2",
                "node2Name",
            )
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.node_similarity(
            graph_name=arguments.get("graph_name"),
            node_identifier_property=arguments.get("node_identifier_property"),
            source_node_filter=arguments.get("source_node_filter"),
            target_node_filter=arguments.get("target_node_filter"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            mutate_relationship_type=arguments.get("mutate_relationship_type"),
            similarity_cutoff=arguments.get("similarity_cutoff"),
            degree_cutoff=arguments.get("degree_cutoff"),
            upper_degree_cutoff=arguments.get("upper_degree_cutoff"),
            top_k=arguments.get("top_k"),
            bottom_k=arguments.get("bottom_k"),
            top_n=arguments.get("top_n"),
            bottom_n=arguments.get("bottom_n"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            similarity_metric=arguments.get("similarity_metric"),
            use_components=arguments.get("use_components"),
        )


class KNearestNeighborsHandler(AlgorithmHandler):
    def k_nearest_neighbors(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs,
            [
                "graph_name",
                "node_identifier_property",
                "source_node_filter",
                "target_node_filter",
                "mode",
            ],
        )
        node_identifier_property = kwargs.get("node_identifier_property")
        source_nodes = kwargs.get("source_node_filter", None)
        target_nodes = kwargs.get("target_node_filter", None)
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "source_node_filter",
            node_identifier_property,
            gds_params,
        )
        translate_identifiers_to_ids(
            self.gds,
            target_nodes,
            "target_node_filter",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"K-Nearest Neighbors parameters: {kwargs}")
        use_filtered = (
            "source_node_filter" in gds_params or "target_node_filter" in gds_params
        )
        if use_filtered:
            # .filtered requires both args; default missing one to None so ConfigConverter skips it
            gds_params.setdefault("source_node_filter", None)
            gds_params.setdefault("target_node_filter", None)
        if mode == "mutate":
            if use_filtered:
                result = self.gds.knn.filtered.mutate(G, **gds_params)
            else:
                result = self.gds.knn.mutate(G, **gds_params)
        else:
            if use_filtered:
                result = self.gds.knn.filtered.stream(G, **gds_params)
            else:
                result = self.gds.knn.stream(G, **gds_params)

            node_identifier_property = kwargs.get("node_identifier_property")
            translate_ids_to_identifiers(
                self.gds,
                node_identifier_property,
                result,
                "node1",
                "node1Name",
            )
            translate_ids_to_identifiers(
                self.gds,
                node_identifier_property,
                result,
                "node2",
                "node2Name",
            )

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.k_nearest_neighbors(
            graph_name=arguments.get("graph_name"),
            node_identifier_property=arguments.get("node_identifier_property"),
            source_node_filter=arguments.get("source_node_filter"),
            target_node_filter=arguments.get("target_node_filter"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            mutate_relationship_type=arguments.get("mutate_relationship_type"),
            node_properties=arguments.get("node_properties"),
            top_k=arguments.get("top_k"),
            sample_rate=arguments.get("sample_rate"),
            delta_threshold=arguments.get("delta_threshold"),
            max_iterations=arguments.get("max_iterations"),
            random_joins=arguments.get("random_joins"),
            initial_sampler=arguments.get("initial_sampler"),
            similarity_cutoff=arguments.get("similarity_cutoff"),
            perturbation_rate=arguments.get("perturbation_rate"),
            seed_target_nodes=arguments.get("seed_target_nodes"),
        )
