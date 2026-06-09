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
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName"])
        logger.info(f"Conductance parameters: {gds_params}")
        result = self.gds.conductance.stream(G, **gds_params)
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.conductance(
            graphName=arguments.get("graphName"),
            communityProperty=arguments.get("communityProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class HDBSCANHandler(AlgorithmHandler):
    def hdbscan(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"HDBSCAN parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.hdbscan.mutate(G, **gds_params)
        else:
            result = self.gds.hdbscan.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.hdbscan(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeProperty=arguments.get("nodeProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            minClusterSize=arguments.get("minClusterSize"),
            samples=arguments.get("samples"),
            leafSize=arguments.get("leafSize"),
        )


class KCoreDecompositionHandler(AlgorithmHandler):
    def k_core_decomposition(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"K-Core Decomposition parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.kcore.mutate(G, **gds_params)
        else:
            result = self.gds.kcore.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_core_decomposition(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class K1ColoringHandler(AlgorithmHandler):
    def k_1_coloring(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"K-1 Coloring parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.k1coloring.mutate(G, **gds_params)
        else:
            result = self.gds.k1coloring.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_1_coloring(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            maxIterations=arguments.get("maxIterations"),
            minCommunitySize=arguments.get("minCommunitySize"),
        )


class KMeansClusteringHandler(AlgorithmHandler):
    def k_means_clustering(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"K-Means Clustering parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.kmeans.mutate(G, **gds_params)
        else:
            result = self.gds.kmeans.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_means_clustering(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Label Propagation parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.labelPropagation.mutate(G, **gds_params)
        else:
            result = self.gds.labelPropagation.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.label_propagation(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Leiden parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.leiden.mutate(G, **gds_params)
        else:
            result = self.gds.leiden.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.leiden(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty", "nodes"]
        )
        logger.info(f"Local Clustering Coefficient parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.localClusteringCoefficient.mutate(G, **gds_params)
        else:
            result = self.gds.localClusteringCoefficient.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds,
                node_identifier_property,
                node_names,
                result,
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.local_clustering_coefficient(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            triangleCountProperty=arguments.get("triangleCountProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodes=arguments.get("nodes"),
        )


class LouvainHandler(AlgorithmHandler):
    def louvain(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Louvain parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.louvain.mutate(G, **gds_params)
        else:
            result = self.gds.louvain.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.louvain(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"Modularity Metric parameters: {gds_params}")
        result = self.gds.modularity.stream(G, **gds_params)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.modularity_metric(
            graphName=arguments.get("graphName"),
            communityProperty=arguments.get("communityProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class ModularityOptimizationHandler(AlgorithmHandler):
    def modularity_optimization(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Modularity Optimization parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.modularityOptimization.mutate(G, **gds_params)
        else:
            result = self.gds.modularityOptimization.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.modularity_optimization(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Strongly Connected Components parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.scc.mutate(G, **gds_params)
        else:
            result = self.gds.scc.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.strongly_connected_components(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            consecutiveIds=arguments.get("consecutiveIds"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class TriangleCountHandler(AlgorithmHandler):
    def triangle_count(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodes", "nodeIdentifierProperty"]
        )
        logger.info(f"Triangle Count parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.triangleCount.mutate(G, **gds_params)
        else:
            result = self.gds.triangleCount.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.triangle_count(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            maxDegree=arguments.get("maxDegree"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodes=arguments.get("nodes"),
        )


class WeaklyConnectedComponentsHandler(AlgorithmHandler):
    def weakly_connected_components(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Weakly Connected Components parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.wcc.mutate(G, **gds_params)
        else:
            result = self.gds.wcc.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.weakly_connected_components(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            seedProperty=arguments.get("seedProperty"),
            threshold=arguments.get("threshold"),
            consecutiveIds=arguments.get("consecutiveIds"),
            minComponentSize=arguments.get("minComponentSize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class ApproximateMaximumKCutHandler(AlgorithmHandler):
    def approximate_maximum_k_cut(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Approximate Maximum K Cut parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.maxkcut.mutate(G, **gds_params)
        else:
            result = self.gds.maxkcut.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.approximate_maximum_k_cut(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            k=arguments.get("k"),
            iterations=arguments.get("iterations"),
            vnsMaxNeighborhoodOrder=arguments.get("vnsMaxNeighborhoodOrder"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            minCommunitySize=arguments.get("minCommunitySize"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class SpeakerListenerLabelPropagationHandler(AlgorithmHandler):
    def speaker_listener_label_propagation(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
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

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.speaker_listener_label_propagation(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            maxIterations=arguments.get("maxIterations"),
            minAssociationStrength=arguments.get("minAssociationStrength"),
            partitioning=arguments.get("partitioning"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )
