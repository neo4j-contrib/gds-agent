import logging
from typing import Dict, Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .gds import projected_graph_from_params
from .node_translator import (
    translate_ids_to_identifiers,
    translate_identifiers_to_ids,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class NodeSimilarityHandler(AlgorithmHandler):
    def node_similarity(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs,
                [
                    "nodeLabels",
                    "relTypes",
                    "nodeIdentifierProperty",
                    "sourceNodeFilter",
                    "targetNodeFilter",
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
            node_similarity_result = self.gds.nodeSimilarity.filtered.stream(
                G, **gds_params
            )

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds,
            node_identifier_property,
            node_similarity_result,
            "node1",
            "node1Name",
        )
        translate_ids_to_identifiers(
            self.gds,
            node_identifier_property,
            node_similarity_result,
            "node2",
            "node2Name",
        )
        return node_similarity_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.node_similarity(
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodeFilter=arguments.get("sourceNodeFilter"),
            targetNodeFilter=arguments.get("targetNodeFilter"),
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
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class KNearestNeighborsHandler(AlgorithmHandler):
    def k_nearest_neighbors(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs,
                [
                    "nodeLabels",
                    "relTypes",
                    "nodeIdentifierProperty",
                    "sourceNodeFilter",
                    "targetNodeFilter",
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
            k_nearest_neighbors_result = self.gds.knn.filtered.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds,
            node_identifier_property,
            k_nearest_neighbors_result,
            "node1",
            "node1Name",
        )
        translate_ids_to_identifiers(
            self.gds,
            node_identifier_property,
            k_nearest_neighbors_result,
            "node2",
            "node2Name",
        )

        return k_nearest_neighbors_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.k_nearest_neighbors(
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodeFilter=arguments.get("sourceNodeFilter"),
            targetNodeFilter=arguments.get("targetNodeFilter"),
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
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )
