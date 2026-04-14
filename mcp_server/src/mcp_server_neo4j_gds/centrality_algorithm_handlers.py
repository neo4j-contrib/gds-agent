import logging
from typing import Any, Dict

from .algorithm_handler import AlgorithmHandler, clean_params

from .node_translator import (
    filter_identifiers,
    translate_ids_to_identifiers,
    translate_identifiers_to_ids,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class ArticleRankHandler(AlgorithmHandler):
    def article_rank(self, **kwargs):
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodes", None)

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "nodes",
                "nodeIdentifierProperty",
                "sourceNodes",
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            scaler=arguments.get("scaler"),
            dampingFactor=arguments.get("dampingFactor"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
        )


class ArticulationPointsHandler(AlgorithmHandler):
    def articulation_points(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        articulation_points = self.gds.articulationPoints.stream(G)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, articulation_points
        )
        return articulation_points

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.articulation_points(
            graphName=arguments.get("graphName"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class BetweennessCentralityHandler(AlgorithmHandler):
    def betweenness_centrality(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "nodes", "nodeIdentifierProperty"]
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            samplingSize=arguments.get("samplingSize"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class BridgesHandler(AlgorithmHandler):
    def bridges(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
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
            graphName=arguments.get("graphName"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class CELFHandler(AlgorithmHandler):
    def celf(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty"])
        logger.info(f"CELF parameters: {gds_params}")
        result = self.gds.influenceMaximization.celf.stream(G, **gds_params)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.celf(
            graphName=arguments.get("graphName"),
            seedSetSize=arguments.get("seedSetSize"),
            monteCarloSimulations=arguments.get("monteCarloSimulations"),
            propagationProbability=arguments.get("propagationProbability"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class ClosenessCentralityHandler(AlgorithmHandler):
    def closeness_centrality(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "nodes", "nodeIdentifierProperty"]
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            useWassermanFaust=arguments.get("useWassermanFaust"),
        )


class DegreeCentralityHandler(AlgorithmHandler):
    def degree_centrality(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "nodes", "nodeIdentifierProperty"]
        )
        logger.info(f"Degree centrality parameters: {gds_params}")
        centrality = self.gds.degree.stream(G, **gds_params)

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
        return self.degree_centrality(
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            orientation=arguments.get("orientation"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class EigenvectorCentralityHandler(AlgorithmHandler):
    def eigenvector_centrality(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "nodes",
                "nodeIdentifierProperty",
                "sourceNodes",
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            scaler=arguments.get("scaler"),
        )


class PageRankHandler(AlgorithmHandler):
    def pagerank(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "nodes",
                "nodeIdentifierProperty",
                "sourceNodes",
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            dampingFactor=arguments.get("dampingFactor"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
        )


class HarmonicCentralityHandler(AlgorithmHandler):
    def harmonic_centrality(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class HITSHandler(AlgorithmHandler):
    def hits(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "nodes", "nodeIdentifierProperty"]
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
            graphName=arguments.get("graphName"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            hitsIterations=arguments.get("hitsIterations"),
            authProperty=arguments.get("authProperty"),
            hubProperty=arguments.get("hubProperty"),
            partitioning=arguments.get("partitioning"),
        )
