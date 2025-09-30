import logging
from typing import Any, Dict

from .algorithm_handler import AlgorithmHandler, clean_params
from .gds import projected_graph_from_params

from .node_translator import (
    filter_identifiers,
    filter_identifiers_pro,
    translate_ids_to_identifiers,
    translate_identifiers_to_ids,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class ArticleRankHandler(AlgorithmHandler):
    def article_rank(self, **kwargs):
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodes", None)

        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs,
                [
                    "nodes",
                    "nodeIdentifierProperty",
                    "sourceNodes",
                    "nodeLabels",
                    "relTypes",
                ],
            )
            # Handle sourceNodes - convert names to IDs if nodeIdentifierProperty is provided
            translate_identifiers_to_ids(
                self.gds,
                source_nodes,
                "sourceNodes",
                node_identifier_property,
                gds_params,
            )

            logger.info(f"ArticleRank parameters: {gds_params}")
            article_ranks = self.gds.articleRank.stream(G, **gds_params)

        translate_ids_to_identifiers(self.gds, node_identifier_property, article_ranks)

        logger.info(f"Filtering ArticleRank results for nodes: {node_names}")
        article_ranks = filter_identifiers(
            self.gds, node_identifier_property, node_names, article_ranks
        )

        return article_ranks

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.article_rank(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            scaler=arguments.get("scaler"),
            dampingFactor=arguments.get("dampingFactor"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class ArticulationPointsHandler(AlgorithmHandler):
    def articulation_points(self, **kwargs):
        with projected_graph_from_params(self.gds, undirected=True, kwargs=kwargs) as G:
            articulation_points = self.gds.articulationPoints.stream(G)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, articulation_points
        )
        return articulation_points

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.articulation_points(
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class BetweennessCentralityHandler(AlgorithmHandler):
    def betweenness_centrality(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs, ["nodes", "nodeIdentifierProperty", "nodeLabels", "relTypes"]
            )
            logger.info(f"Betweenness centrality parameters: {gds_params}")
            centrality = self.gds.betweenness.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, centrality)

        # Filter results by node names if provided
        node_names = kwargs.get("nodes", None)
        centrality = filter_identifiers(
            self.gds, node_identifier_property, node_names, centrality
        )

        return centrality

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.betweenness_centrality(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            samplingSize=arguments.get("samplingSize"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class BridgesHandler(AlgorithmHandler):
    def bridges(self, **kwargs):
        with projected_graph_from_params(self.gds, undirected=True, kwargs=kwargs) as G:
            bridges_result = self.gds.bridges.stream(G)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, bridges_result, "from", "fromName"
        )
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, bridges_result, "to", "toName"
        )

        return bridges_result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.bridges(
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class CELFHandler(AlgorithmHandler):
    def celf(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs, ["nodeIdentifierProperty", "nodeLabels", "relTypes"]
            )
            logger.info(f"CELF parameters: {gds_params}")
            result = self.gds.influenceMaximization.celf.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.celf(
            seedSetSize=arguments.get("seedSetSize"),
            monteCarloSimulations=arguments.get("monteCarloSimulations"),
            propagationProbability=arguments.get("propagationProbability"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class ClosenessCentralityHandler(AlgorithmHandler):
    def closeness_centrality(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs, ["nodes", "nodeIdentifierProperty", "nodeLabels", "relTypes"]
            )
            logger.info(f"Closeness centrality parameters: {gds_params}")
            centrality = self.gds.closeness.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, centrality)

        # Filter results by node names if provided
        node_names = kwargs.get("nodes", None)
        centrality = filter_identifiers(
            self.gds, node_identifier_property, node_names, centrality
        )

        return centrality

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.closeness_centrality(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            useWassermanFaust=arguments.get("useWassermanFaust"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class DegreeCentralityHandler(AlgorithmHandler):
    def degree_centrality(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs,
                [
                    "nodes",
                    "nodeIdentifierProperty",
                    "nodeLabels",
                    "relTypes",
                    "nodeResultFilter",
                ],
            )
            logger.info(f"Degree centrality parameters: {gds_params}")
            centrality = self.gds.degree.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, centrality)

        # Filter results by node names/labels if provided
        node_names = kwargs.get("nodes", None)
        node_result_filter = kwargs.get("nodeResultFilter", None)
        centrality = filter_identifiers_pro(
            self.gds,
            node_identifier_property,
            node_names,
            node_result_filter,
            centrality,
        )

        return centrality

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.degree_centrality(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            orientation=arguments.get("orientation"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
            nodeResultFilter=arguments.get("nodeResultFilter"),
        )


class EigenvectorCentralityHandler(AlgorithmHandler):
    def eigenvector_centrality(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs,
                [
                    "nodes",
                    "nodeIdentifierProperty",
                    "sourceNodes",
                    "nodeLabels",
                    "relTypes",
                ],
            )
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            source_nodes = kwargs.get("sourceNodes", None)

            # Handle sourceNodes - convert names to IDs if nodeIdentifierProperty is provided
            translate_identifiers_to_ids(
                self.gds,
                source_nodes,
                "sourceNodes",
                node_identifier_property,
                gds_params,
            )

            logger.info(f"Eigenvector centrality parameters: {gds_params}")
            centrality = self.gds.eigenvector.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, centrality)

        # Filter results by node names if provided
        node_names = kwargs.get("nodes", None)
        centrality = filter_identifiers(
            self.gds, node_identifier_property, node_names, centrality
        )

        return centrality

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.eigenvector_centrality(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            scaler=arguments.get("scaler"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class PageRankHandler(AlgorithmHandler):
    def pagerank(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs,
                [
                    "nodes",
                    "nodeIdentifierProperty",
                    "sourceNodes",
                    "nodeLabels",
                    "relTypes",
                ],
            )
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            source_nodes = kwargs.get("sourceNodes", None)

            # Handle sourceNodes - convert names to IDs if nodeIdentifierProperty is provided
            translate_identifiers_to_ids(
                self.gds,
                source_nodes,
                "sourceNodes",
                node_identifier_property,
                gds_params,
            )
            logger.info(f"Pagerank parameters: {gds_params}")
            pageranks = self.gds.pageRank.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, pageranks)

        # Filter results by node names if provided
        node_names = kwargs.get("nodes", None)
        pageranks = filter_identifiers(
            self.gds, node_identifier_property, node_names, pageranks
        )

        return pageranks

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.pagerank(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            dampingFactor=arguments.get("dampingFactor"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class HarmonicCentralityHandler(AlgorithmHandler):
    def harmonic_centrality(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            centrality = self.gds.closeness.harmonic.stream(G)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, centrality)

        # Filter results by node names if provided
        node_names = kwargs.get("nodes", None)
        centrality = filter_identifiers(
            self.gds, node_identifier_property, node_names, centrality
        )
        return centrality

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.harmonic_centrality(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )


class HITSHandler(AlgorithmHandler):
    def hits(self, **kwargs):
        with projected_graph_from_params(self.gds, kwargs=kwargs) as G:
            gds_params = clean_params(
                kwargs, ["nodes", "nodeIdentifierProperty", "nodeLabels", "relTypes"]
            )
            logger.info(f"HITS parameters: {gds_params}")
            result = self.gds.hits.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        # Filter results by node names if provided
        node_names = kwargs.get("nodes", None)
        result = filter_identifiers(
            self.gds, node_identifier_property, node_names, result
        )
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.hits(
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            hitsIterations=arguments.get("hitsIterations"),
            authProperty=arguments.get("authProperty"),
            hubProperty=arguments.get("hubProperty"),
            partitioning=arguments.get("partitioning"),
            nodeLabels=arguments.get("nodeLabels"),
            relTypes=arguments.get("relTypes"),
        )
