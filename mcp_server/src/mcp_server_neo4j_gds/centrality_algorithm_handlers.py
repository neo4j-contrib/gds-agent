import logging
from typing import Any

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import (
    filter_identifiers,
    translate_identifiers_to_ids,
    translate_ids_to_identifiers,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class ArticleRankHandler(AlgorithmHandler):
    def article_rank(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")
        source_nodes = kwargs.get("source_nodes", None)

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs,
            [
                "graph_name",
                "mode",
                "nodes",
                "node_identifier_property",
                "source_nodes",
            ],
        )
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "source_nodes",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"ArticleRank parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.article_rank.mutate(G, **gds_params)
        else:
            result = self.gds.article_rank.stream(G, **gds_params)
            logger.info(f"Filtering ArticleRank results for nodes: {node_names}")
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.article_rank(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            source_nodes=arguments.get("source_nodes"),
            scaler=arguments.get("scaler"),
            damping_factor=arguments.get("damping_factor"),
            max_iterations=arguments.get("max_iterations"),
            tolerance=arguments.get("tolerance"),
        )


class ArticulationPointsHandler(AlgorithmHandler):
    def articulation_points(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )

        if mode == "mutate":
            result = self.gds.articulation_points.mutate(G, **gds_params)
        else:
            result = self.gds.articulation_points.stream(G)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.articulation_points(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class BetweennessCentralityHandler(AlgorithmHandler):
    def betweenness_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "nodes", "node_identifier_property"]
        )
        logger.info(f"Betweenness centrality parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.betweenness.mutate(G, **gds_params)
        else:
            result = self.gds.betweenness.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.betweenness_centrality(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            sampling_size=arguments.get("sampling_size"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
        )


class BridgesHandler(AlgorithmHandler):
    def bridges(self, **kwargs):
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))

        result = self.gds.bridges.stream(G)
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, result, "from", "fromName"
        )
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, result, "to", "toName"
        )

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.bridges(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class CELFHandler(AlgorithmHandler):
    def celf(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "node_identifier_property"]
        )
        logger.info(f"CELF parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.influence_maximization_celf.mutate(G, **gds_params)
        else:
            result = self.gds.influence_maximization_celf.stream(G, **gds_params)
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.celf(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            seed_set_size=arguments.get("seed_set_size"),
            monte_carlo_simulations=arguments.get("monte_carlo_simulations"),
            propagation_probability=arguments.get("propagation_probability"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class ClosenessCentralityHandler(AlgorithmHandler):
    def closeness_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "nodes", "node_identifier_property"]
        )
        logger.info(f"Closeness centrality parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.closeness.mutate(G, **gds_params)
        else:
            result = self.gds.closeness.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.closeness_centrality(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            use_wasserman_faust=arguments.get("use_wasserman_faust"),
        )


class DegreeCentralityHandler(AlgorithmHandler):
    def degree_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "nodes", "node_identifier_property"]
        )
        logger.info(f"Degree centrality parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.degree.mutate(G, **gds_params)
        else:
            result = self.gds.degree.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.degree_centrality(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            orientation=arguments.get("orientation"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
        )


class EigenvectorCentralityHandler(AlgorithmHandler):
    def eigenvector_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")
        source_nodes = kwargs.get("source_nodes", None)

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs,
            [
                "graph_name",
                "mode",
                "nodes",
                "node_identifier_property",
                "source_nodes",
            ],
        )
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "source_nodes",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"Eigenvector centrality parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.eigenvector.mutate(G, **gds_params)
        else:
            result = self.gds.eigenvector.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.eigenvector_centrality(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            max_iterations=arguments.get("max_iterations"),
            tolerance=arguments.get("tolerance"),
            relationship_weight_property=arguments.get("relationship_weight_property"),
            source_nodes=arguments.get("source_nodes"),
            scaler=arguments.get("scaler"),
        )


class PageRankHandler(AlgorithmHandler):
    def pagerank(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")
        source_nodes = kwargs.get("source_nodes", None)

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs,
            [
                "graph_name",
                "mode",
                "nodes",
                "node_identifier_property",
                "source_nodes",
            ],
        )
        translate_identifiers_to_ids(
            self.gds,
            source_nodes,
            "source_nodes",
            node_identifier_property,
            gds_params,
        )

        logger.info(f"Pagerank parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.page_rank.mutate(G, **gds_params)
        else:
            result = self.gds.page_rank.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.pagerank(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            source_nodes=arguments.get("source_nodes"),
            damping_factor=arguments.get("damping_factor"),
            max_iterations=arguments.get("max_iterations"),
            tolerance=arguments.get("tolerance"),
        )


class HarmonicCentralityHandler(AlgorithmHandler):
    def harmonic_centrality(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "nodes", "node_identifier_property"]
        )

        if mode == "mutate":
            result = self.gds.harmonic.mutate(G, **gds_params)
        else:
            result = self.gds.harmonic.stream(G)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.harmonic_centrality(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
        )


class HITSHandler(AlgorithmHandler):
    def hits(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        node_names = kwargs.get("nodes", None)
        node_identifier_property = kwargs.get("node_identifier_property")

        G = self.gds.graph.get(kwargs.get("graph_name"))
        gds_params = clean_params(
            kwargs, ["graph_name", "mode", "nodes", "node_identifier_property"]
        )
        gds_params["auth_property"] = "auth"
        gds_params["hub_property"] = "hub"
        logger.info(f"HITS parameters: {gds_params}")

        if mode == "mutate":
            result = self.gds.hits.mutate(G, **gds_params)
        else:
            result = self.gds.hits.stream(G, **gds_params)
            result = filter_identifiers(
                self.gds, node_identifier_property, node_names, result
            )
            translate_ids_to_identifiers(self.gds, node_identifier_property, result)

        return result

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.hits(
            graph_name=arguments.get("graph_name"),
            mode=arguments.get("mode"),
            mutate_property=arguments.get("mutate_property"),
            nodes=arguments.get("nodes"),
            node_identifier_property=arguments.get("node_identifier_property"),
            hits_iterations=arguments.get("hits_iterations"),
            partitioning=arguments.get("partitioning"),
        )
