import logging
from typing import Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import (
    filter_identifiers,
    translate_ids_to_identifiers,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class ConductanceHandler(AlgorithmHandler):
    def conductance(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(kwargs, ["graph_name"])
        logger.info(f"Conductance parameters: {gds_params}")
        result = self.gds.conductance.stream(G, **gds_params)
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.conductance(
            graph_name=arguments.get("graph_name"),
            community_property=arguments.get("community_property"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
        )


class HDBSCANHandler(AlgorithmHandler):
    def hdbscan(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"HDBSCAN parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.hdbscan.mutate(G, **gds_params)
        else:
            result = self.gds.hdbscan.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.hdbscan(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_property=arguments.get("node_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            min_cluster_size=arguments.get("min_cluster_size"),
            samples=arguments.get("samples"),
            leaf_size=arguments.get("leaf_size"),
        )


class KCoreDecompositionHandler(AlgorithmHandler):
    def k_core_decomposition(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"K-Core Decomposition parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.kcore.mutate(G, **gds_params)
        else:
            result = self.gds.kcore.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.k_core_decomposition(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class K1ColoringHandler(AlgorithmHandler):
    def k_1_coloring(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"K-1 Coloring parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.k1_coloring.mutate(G, **gds_params)
        else:
            result = self.gds.k1_coloring.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.k_1_coloring(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            max_iterations=arguments.get("max_iterations"),
            min_community_size=arguments.get("min_community_size"),
        )


class KMeansClusteringHandler(AlgorithmHandler):
    def k_means_clustering(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"K-Means Clustering parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.kmeans.mutate(G, **gds_params)
        else:
            result = self.gds.kmeans.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.k_means_clustering(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_property=arguments.get("node_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            k=arguments.get("k"),
            max_iterations=arguments.get("max_iterations"),
            delta_threshold=arguments.get("delta_threshold"),
            number_of_restarts=arguments.get("number_of_restarts"),
            initial_sampler=arguments.get("initial_sampler"),
            seed_centroids=arguments.get("seed_centroids"),
            compute_silhouette=arguments.get("compute_silhouette"),
        )


class LabelPropagationHandler(AlgorithmHandler):
    def label_propagation(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Label Propagation parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.label_propagation.mutate(G, **gds_params)
        else:
            result = self.gds.label_propagation.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.label_propagation(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            max_iterations=arguments.get("max_iterations"),
            node_weight_property=arguments.get("node_weight_property"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            seed_property=arguments.get("seed_property"),
            consecutive_ids=arguments.get("consecutive_ids"),
            min_community_size=arguments.get("min_community_size"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class LeidenHandler(AlgorithmHandler):
    def leiden(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Leiden parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.leiden.mutate(G, **gds_params)
        else:
            result = self.gds.leiden.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.leiden(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            max_levels=arguments.get("max_levels"),
            gamma=arguments.get("gamma"),
            theta=arguments.get("theta"),
            tolerance=arguments.get("tolerance"),
            include_intermediate_communities=arguments.get(
                "include_intermediate_communities"
            ),
            seed_property=arguments.get("seed_property"),
            min_community_size=arguments.get("min_community_size"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class LocalClusteringCoefficientHandler(AlgorithmHandler):
    def local_clustering_coefficient(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property", "nodes"]
        )
        logger.info(f"Local Clustering Coefficient parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.local_clustering_coefficient.mutate(G, **gds_params)
        else:
            result = self.gds.local_clustering_coefficient.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds,
                node_identifier_property,
                node_names,
                result,
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.local_clustering_coefficient(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            triangle_count_property=arguments.get("triangle_count_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
            nodes=arguments.get("nodes"),
        )


class LouvainHandler(AlgorithmHandler):
    def louvain(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Louvain parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.louvain.mutate(G, **gds_params)
        else:
            result = self.gds.louvain.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.louvain(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            seed_property=arguments.get("seed_property"),
            max_levels=arguments.get("max_levels"),
            max_iterations=arguments.get("max_iterations"),
            tolerance=arguments.get("tolerance"),
            include_intermediate_communities=arguments.get(
                "include_intermediate_communities"
            ),
            consecutive_ids=arguments.get("consecutive_ids"),
            min_community_size=arguments.get("min_community_size"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class ModularityMetricHandler(AlgorithmHandler):
    def modularity_metric(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(kwargs, ["graph_name", "node_identifier_property"])
        logger.info(f"Modularity Metric parameters: {gds_params}")
        result = self.gds.modularity.stream(G, **gds_params)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.modularity_metric(
            graph_name=arguments.get("graph_name"),
            community_property=arguments.get("community_property"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
        )


class ModularityOptimizationHandler(AlgorithmHandler):
    def modularity_optimization(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Modularity Optimization parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.modularity_optimization.mutate(G, **gds_params)
        else:
            result = self.gds.modularity_optimization.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.modularity_optimization(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            max_iterations=arguments.get("max_iterations"),
            tolerance=arguments.get("tolerance"),
            seed_property=arguments.get("seed_property"),
            consecutive_ids=arguments.get("consecutive_ids"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            min_community_size=arguments.get("min_community_size"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class StronglyConnectedComponentsHandler(AlgorithmHandler):
    def strongly_connected_components(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Strongly Connected Components parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.scc.mutate(G, **gds_params)
        else:
            result = self.gds.scc.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.strongly_connected_components(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            consecutive_ids=arguments.get("consecutive_ids"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class TriangleCountHandler(AlgorithmHandler):
    def triangle_count(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "nodes", "node_identifier_property"]
        )
        logger.info(f"Triangle Count parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.triangle_count.mutate(G, **gds_params)
        else:
            result = self.gds.triangle_count.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.triangle_count(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            max_degree=arguments.get("max_degree"),
            node_identifier_property=arguments.get("node_identifier_property"),
            nodes=arguments.get("nodes"),
        )


class WeaklyConnectedComponentsHandler(AlgorithmHandler):
    def weakly_connected_components(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Weakly Connected Components parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.wcc.mutate(G, **gds_params)
        else:
            result = self.gds.wcc.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.weakly_connected_components(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            seed_property=arguments.get("seed_property"),
            threshold=arguments.get("threshold"),
            consecutive_ids=arguments.get("consecutive_ids"),
            min_component_size=arguments.get("min_component_size"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class ApproximateMaximumKCutHandler(AlgorithmHandler):
    def approximate_maximum_k_cut(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Approximate Maximum K Cut parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.max_k_cut.mutate(G, **gds_params)
        else:
            result = self.gds.max_k_cut.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.approximate_maximum_k_cut(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            k=arguments.get("k"),
            iterations=arguments.get("iterations"),
            vns_max_neighborhood_order=arguments.get("vns_max_neighborhood_order"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            min_community_size=arguments.get("min_community_size"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class SpeakerListenerLabelPropagationHandler(AlgorithmHandler):
    def speaker_listener_label_propagation(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")
        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"Speaker Listener Label Propagation parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.sllpa.mutate(G, **gds_params)
        else:
            result = self.gds.sllpa.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds,
                node_identifier_property,
                result,
            )

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.speaker_listener_label_propagation(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            max_iterations=arguments.get("max_iterations"),
            min_association_strength=arguments.get("min_association_strength"),
            partitioning=arguments.get("partitioning"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )
