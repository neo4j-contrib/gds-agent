import logging
from typing import Dict, Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import (
    translate_ids_to_identifiers,
    translate_identifiers_to_ids,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class NodeSimilarityHandler(AlgorithmHandler):
    def node_similarity(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "nodeIdentifierProperty",
                "sourceNodeFilter",
                "targetNodeFilter",
                "mode",
            ],
        )
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodeFilter", None)
        target_nodes = kwargs.get("targetNodeFilter", None)
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "sourceNodeFilter",
            node_identifier_property,
            gds_params,
        )
        translate_identifiers_to_ids(
            self.gds,
            target_nodes,
            "targetNodeFilter",
            node_identifier_property,
            gds_params,
        )
        logger.info(f"Node Similarity parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.nodeSimilarity.filtered.mutate(G, **gds_params)
        else:
            result = self.gds.nodeSimilarity.filtered.stream(G, **gds_params)

            node_identifier_property = kwargs.get("nodeIdentifierProperty")
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

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.node_similarity(
            graphName=arguments.get("graphName"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodeFilter=arguments.get("sourceNodeFilter"),
            targetNodeFilter=arguments.get("targetNodeFilter"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
            similarityCutoff=arguments.get("similarityCutoff"),
            degreeCutoff=arguments.get("degreeCutoff"),
            upperDegreeCutoff=arguments.get("upperDegreeCutoff"),
            topK=arguments.get("topK"),
            bottomK=arguments.get("bottomK"),
            topN=arguments.get("topN"),
            bottomN=arguments.get("bottomN"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            similarityMetric=arguments.get("similarityMetric"),
            useComponents=arguments.get("useComponents"),
        )


class KNearestNeighborsHandler(AlgorithmHandler):
    def k_nearest_neighbors(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "nodeIdentifierProperty",
                "sourceNodeFilter",
                "targetNodeFilter",
                "mode",
            ],
        )
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodeFilter", None)
        target_nodes = kwargs.get("targetNodeFilter", None)
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "sourceNodeFilter",
            node_identifier_property,
            gds_params,
        )
        translate_identifiers_to_ids(
            self.gds,
            target_nodes,
            "targetNodeFilter",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"K-Nearest Neighbors parameters: {kwargs}")
        if mode == "mutate":
            result = self.gds.knn.filtered.mutate(G, **gds_params)
        else:
            result = self.gds.knn.filtered.stream(G, **gds_params)

            node_identifier_property = kwargs.get("nodeIdentifierProperty")
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

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_nearest_neighbors(
            graphName=arguments.get("graphName"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodeFilter=arguments.get("sourceNodeFilter"),
            targetNodeFilter=arguments.get("targetNodeFilter"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
            nodeProperties=arguments.get("nodeProperties"),
            topK=arguments.get("topK"),
            sampleRate=arguments.get("sampleRate"),
            deltaThreshold=arguments.get("deltaThreshold"),
            maxIterations=arguments.get("maxIterations"),
            randomJoins=arguments.get("randomJoins"),
            initialSampler=arguments.get("initialSampler"),
            similarityCutoff=arguments.get("similarityCutoff"),
            perturbationRate=arguments.get("perturbationRate"),
            seedTargetNodes=arguments.get("seedTargetNodes"),
        )
