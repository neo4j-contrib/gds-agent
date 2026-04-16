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
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodes", None)

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "mode",
                "nodes",
                "nodeIdentifierProperty",
                "sourceNodes",
            ],
        )
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "sourceNodes",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"ArticleRank parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.articleRank.mutate(G, **gds_params)
        else:
            result = self.gds.articleRank.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            logger.info(f"Filtering ArticleRank results for nodes: {node_names}")
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.article_rank(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )

        if mode == "mutate":
            result = self.gds.articulationPoints.mutate(G, **gds_params)
        else:
            result = self.gds.articulationPoints.stream(G)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.articulation_points(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class BetweennessCentralityHandler(AlgorithmHandler):
    def betweenness_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodes", "nodeIdentifierProperty"]
        )
        logger.info(f"Betweenness centrality parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.betweenness.mutate(G, **gds_params)
        else:
            result = self.gds.betweenness.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.betweenness_centrality(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            samplingSize=arguments.get("samplingSize"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class BridgesHandler(AlgorithmHandler):
    def bridges(self, **kwargs):
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))

        result = self.gds.bridges.stream(G)
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, result, "from", "fromName"
        )
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, result, "to", "toName"
        )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.bridges(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class CELFHandler(AlgorithmHandler):
    def celf(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"CELF parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.influenceMaximization.celf.mutate(G, **gds_params)
        else:
            result = self.gds.influenceMaximization.celf.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.celf(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            seedSetSize=arguments.get("seedSetSize"),
            monteCarloSimulations=arguments.get("monteCarloSimulations"),
            propagationProbability=arguments.get("propagationProbability"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class ClosenessCentralityHandler(AlgorithmHandler):
    def closeness_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodes", "nodeIdentifierProperty"]
        )
        logger.info(f"Closeness centrality parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.closeness.mutate(G, **gds_params)
        else:
            result = self.gds.closeness.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.closeness_centrality(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            useWassermanFaust=arguments.get("useWassermanFaust"),
        )


class DegreeCentralityHandler(AlgorithmHandler):
    def degree_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodes", "nodeIdentifierProperty"]
        )
        logger.info(f"Degree centrality parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.degree.mutate(G, **gds_params)
        else:
            result = self.gds.degree.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.degree_centrality(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            orientation=arguments.get("orientation"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class EigenvectorCentralityHandler(AlgorithmHandler):
    def eigenvector_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodes", None)

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "mode",
                "nodes",
                "nodeIdentifierProperty",
                "sourceNodes",
            ],
        )
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "sourceNodes",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"Eigenvector centrality parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.eigenvector.mutate(G, **gds_params)
        else:
            result = self.gds.eigenvector.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.eigenvector_centrality(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
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
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        source_nodes = kwargs.get("sourceNodes", None)

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs,
            [
                "graphName",
                "mode",
                "nodes",
                "nodeIdentifierProperty",
                "sourceNodes",
            ],
        )
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "sourceNodes",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"Pagerank parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.pageRank.mutate(G, **gds_params)
        else:
            result = self.gds.pageRank.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.pagerank(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            sourceNodes=arguments.get("sourceNodes"),
            dampingFactor=arguments.get("dampingFactor"),
            maxIterations=arguments.get("maxIterations"),
            tolerance=arguments.get("tolerance"),
        )


class HarmonicCentralityHandler(AlgorithmHandler):
    def harmonic_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodes", "nodeIdentifierProperty"]
        )

        if mode == "mutate":
            result = self.gds.closeness.harmonic.mutate(G, **gds_params)
        else:
            result = self.gds.closeness.harmonic.stream(G)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.harmonic_centrality(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
        )


class HITSHandler(AlgorithmHandler):
    def hits(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("nodeIdentifierProperty")

        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodes", "nodeIdentifierProperty"]
        )
        gds_params["authProperty"] = "auth"
        gds_params["hubProperty"] = "hub"
        logger.info(f"HITS parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.hits.mutate(G, **gds_params)
        else:
            result = self.gds.hits.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.hits(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodes=arguments.get("nodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            hitsIterations=arguments.get("hitsIterations"),
            partitioning=arguments.get("partitioning"),
        )
