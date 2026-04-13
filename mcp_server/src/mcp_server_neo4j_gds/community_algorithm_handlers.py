import logging
from typing import Dict, Any
from .node_translator import (
    filter_identifiers,
    translate_ids_to_identifiers,
)

from .algorithm_handler import AlgorithmHandler, clean_params

logger = logging.getLogger("mcp_server_neo4j_gds")


class ConductanceHandler(AlgorithmHandler):
    def conductance(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName"])
        logger.info(f"Conductance parameters: {gds_params}")
        conductance = self.gds.conductance.stream(G, **gds_params)
        return conductance

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.conductance(
            graphName=arguments.get("graphName"),
            communityProperty=arguments.get("communityProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class HDBSCANHandler(AlgorithmHandler):
    def hdbscan(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"HDBSCAN parameters: {gds_params}")
        hdbscan_result = self.gds.hdbscan.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, hdbscan_result)

        return hdbscan_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.hdbscan(
            graphName=arguments.get("graphName"),
            nodeProperty=arguments.get("nodeProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            minClusterSize=arguments.get("minClusterSize"),
            samples=arguments.get("samples"),
            leafSize=arguments.get("leafSize"),
        )


class KCoreDecompositionHandler(AlgorithmHandler):
    def k_core_decomposition(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        logger.info("Running K-Core Decomposition")
        k_core_decomposition_result = self.gds.kcore.stream(G)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, k_core_decomposition_result
        )
        return k_core_decomposition_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_core_decomposition(
            graphName=arguments.get("graphName"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class K1ColoringHandler(AlgorithmHandler):
    def k_1_coloring(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"K-1 Coloring parameters: {gds_params}")
        k1_coloring_result = self.gds.k1coloring.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, k1_coloring_result
        )

        return k1_coloring_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_1_coloring(
            graphName=arguments.get("graphName"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            maxIterations=arguments.get("maxIterations"),
            minCommunitySize=arguments.get("minCommunitySize"),
        )


class KMeansClusteringHandler(AlgorithmHandler):
    def k_means_clustering(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"K-Means Clustering parameters: {gds_params}")
        kmeans_clustering_result = self.gds.kmeans.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, kmeans_clustering_result
        )

        return kmeans_clustering_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_means_clustering(
            graphName=arguments.get("graphName"),
            nodeProperty=arguments.get("nodeProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            k=arguments.get("k"),
            maxIterations=arguments.get("maxIterations"),
            deltaThreshold=arguments.get("deltaThreshold"),
            numberOfRestarts=arguments.get("numberOfRestarts"),
            initialSampler=arguments.get("initialSampler"),
            seedCentroids=arguments.get("seedCentroids"),
            computeSilhouette=arguments.get("computeSilhouette"),
        )


class LabelPropagationHandler(AlgorithmHandler):
    def label_propagation(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Label Propagation parameters: {gds_params}")
        label_propagation_result = self.gds.labelPropagation.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, label_propagation_result
        )

        return label_propagation_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.label_propagation(
            graphName=arguments.get("graphName"),
            maxIterations=arguments.get("maxIterations"),
            nodeWeightProperty=arguments.get("nodeWeightProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            seedProperty=arguments.get("seedProperty"),
            consecutiveIds=arguments.get("consecutiveIds"),
            minCommunitySize=arguments.get("minCommunitySize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class LeidenHandler(AlgorithmHandler):
    def leiden(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Leiden parameters: {gds_params}")
        leiden_result = self.gds.leiden.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, leiden_result)

        return leiden_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.leiden(
            graphName=arguments.get("graphName"),
            maxLevels=arguments.get("maxLevels"),
            gamma=arguments.get("gamma"),
            theta=arguments.get("theta"),
            tolerance=arguments.get("tolerance"),
            includeIntermediateCommunities=arguments.get(
                "includeIntermediateCommunities"
            ),
            seedProperty=arguments.get("seedProperty"),
            minCommunitySize=arguments.get("minCommunitySize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class LocalClusteringCoefficientHandler(AlgorithmHandler):
    def local_clustering_coefficient(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty", "nodes"])
        logger.info(f"Local Clustering Coefficient parameters: {gds_params}")
        local_clustering_coefficient_result = (
            self.gds.localClusteringCoefficient.stream(G, **gds_params)
        )

        # Get filtering parameters
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        # Add node names to the results if nodeIdentifierProperty is provided
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, local_clustering_coefficient_result
        )

        # Filter results if nodes parameter provided
        local_clustering_coefficient_result = filter_identifiers(
            self.gds,
            node_identifier_property,
            node_names,
            local_clustering_coefficient_result,
        )

        return local_clustering_coefficient_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.local_clustering_coefficient(
            graphName=arguments.get("graphName"),
            triangleCountProperty=arguments.get("triangleCountProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodes=arguments.get("nodes"),
        )


class LouvainHandler(AlgorithmHandler):
    def louvain(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Louvain parameters: {gds_params}")
        louvain_result = self.gds.louvain.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, louvain_result)

        return louvain_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.louvain(
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            seedProperty=arguments.get("seedProperty"),
            maxLevels=arguments.get("maxLevels"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
            includeIntermediateCommunities=arguments.get(
                "includeIntermediateCommunities"
            ),
            consecutiveIds=arguments.get("consecutiveIds"),
            minCommunitySize=arguments.get("minCommunitySize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class ModularityMetricHandler(AlgorithmHandler):
    def modularity_metric(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Modularity Metric parameters: {gds_params}")
        modularity_metric_result = self.gds.modularity.stream(G, **gds_params)

        return modularity_metric_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.modularity_metric(
            graphName=arguments.get("graphName"),
            communityProperty=arguments.get("communityProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class ModularityOptimizationHandler(AlgorithmHandler):
    def modularity_optimization(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Modularity Optimization parameters: {gds_params}")
        modularity_optimization_result = self.gds.modularityOptimization.stream(
            G, **gds_params
        )

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, modularity_optimization_result
        )

        return modularity_optimization_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.modularity_optimization(
            graphName=arguments.get("graphName"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
            seedProperty=arguments.get("seedProperty"),
            consecutiveIds=arguments.get("consecutiveIds"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            minCommunitySize=arguments.get("minCommunitySize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class StronglyConnectedComponentsHandler(AlgorithmHandler):
    def strongly_connected_components(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Strongly Connected Components parameters: {gds_params}")
        strongly_connected_components_result = self.gds.scc.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, strongly_connected_components_result
        )

        return strongly_connected_components_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.strongly_connected_components(
            graphName=arguments.get("graphName"),
            consecutiveIds=arguments.get("consecutiveIds"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class TriangleCountHandler(AlgorithmHandler):
    def triangle_count(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodes", "nodeIdentifierProperty"])
        logger.info(f"Triangle Count parameters: {gds_params}")
        triangle_count_result = self.gds.triangleCount.stream(G, **gds_params)

        # Get filtering parameters
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        # Add node names to the results if nodeIdentifierProperty is provided
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, triangle_count_result
        )

        # Filter results if nodes parameter provided
        triangle_count_result = filter_identifiers(
            self.gds, node_identifier_property, node_names, triangle_count_result
        )

        return triangle_count_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.triangle_count(
            graphName=arguments.get("graphName"),
            maxDegree=arguments.get("maxDegree"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodes=arguments.get("nodes"),
        )


class WeaklyConnectedComponentsHandler(AlgorithmHandler):
    def weakly_connected_components(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Weakly Connected Components parameters: {gds_params}")
        weakly_connected_components_result = self.gds.wcc.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, weakly_connected_components_result
        )

        return weakly_connected_components_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.weakly_connected_components(
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            seedProperty=arguments.get("seedProperty"),
            threshold=arguments.get("threshold"),
            consecutiveIds=arguments.get("consecutiveIds"),
            minComponentSize=arguments.get("minComponentSize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class ApproximateMaximumKCutHandler(AlgorithmHandler):
    def approximate_maximum_k_cut(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Approximate Maximum K Cut parameters: {gds_params}")
        approximate_maximum_k_cut_result = self.gds.maxkcut.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, approximate_maximum_k_cut_result
        )

        return approximate_maximum_k_cut_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.approximate_maximum_k_cut(
            graphName=arguments.get("graphName"),
            k=arguments.get("k"),
            iterations=arguments.get("iterations"),
            vnsMaxNeighborhoodOrder=arguments.get("vnsMaxNeighborhoodOrder"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            minCommunitySize=arguments.get("minCommunitySize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class SpeakerListenerLabelPropagationHandler(AlgorithmHandler):
    def speaker_listener_label_propagation(self, **kwargs):
        G = self.get_graph(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Speaker Listener Label Propagation parameters: {gds_params}")
        speaker_listener_label_propagation_result = self.gds.sllpa.stream(
            G, **gds_params
        )

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds,
            node_identifier_property,
            speaker_listener_label_propagation_result,
        )

        return speaker_listener_label_propagation_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.speaker_listener_label_propagation(
            graphName=arguments.get("graphName"),
            maxIterations=arguments.get("maxIterations"),
            minAssociationStrength=arguments.get("minAssociationStrength"),
            partitioning=arguments.get("partitioning"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )
