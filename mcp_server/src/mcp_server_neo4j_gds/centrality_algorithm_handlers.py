import logging
from typing import Any, Dict

from .algorithm_handler import AlgorithmHandler
from .gds import projected_graph
from .node_translator import (
    filter_identifiers,
    translate_ids_to_identifiers,
    translate_identifiers_to_ids,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


class ArticleRankHandler(AlgorithmHandler):
    def article_rank(self, **kwargs):
        with projected_graph(self.gds) as G:
            # If any optional parameter is not None, use that parameter
            args = locals()
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None
                and k not in ["nodes", "nodeIdentifierProperty", "sourceNodes"]
            }
            node_names = kwargs.get("nodes", None)
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            source_nodes = kwargs.get("sourceNodes", None)

            # Handle sourceNodes - convert names to IDs if nodeIdentifierProperty is provided
            translate_identifiers_to_ids(
                self.gds, source_nodes, "sourceNodes", node_identifier_property, params
            )

            logger.info(f"ArticleRank parameters: {params}")
            article_ranks = self.gds.articleRank.stream(G, **params)

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
        )


class ArticulationPointsHandler(AlgorithmHandler):
    def articulation_points(self, **kwargs):
        with projected_graph(self.gds, undirected=True) as G:
            articulation_points = self.gds.articulationPoints.stream(G)

        # Add node names to the results if nodeIdentifierProperty is provided
        node_identifier_property = kwargs.get("nodeIdentifierProperty")
        translate_ids_to_identifiers(
            self.gds, node_identifier_property, articulation_points
        )
        return articulation_points

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.articulation_points(
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty")
        )


class BetweennessCentralityHandler(AlgorithmHandler):
    def betweenness_centrality(self, **kwargs):
        with projected_graph(self.gds) as G:
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None and k not in ["nodes", "nodeIdentifierProperty"]
            }
            logger.info(f"Betweenness centrality parameters: {params}")
            centrality = self.gds.betweenness.stream(G, **params)

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
        )


class BridgesHandler(AlgorithmHandler):
    def bridges(self, **kwargs):
        with projected_graph(self.gds, undirected=True) as G:
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
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty")
        )


class CELFHandler(AlgorithmHandler):
    def celf(self, **kwargs):
        with projected_graph(self.gds) as G:
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None and k not in ["nodeIdentifierProperty"]
            }
            logger.info(f"CELF parameters: {params}")
            result = self.gds.influenceMaximization.celf.stream(G, **params)

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
        )


class ClosenessCentralityHandler(AlgorithmHandler):
    def closeness_centrality(self, **kwargs):
        with projected_graph(self.gds) as G:
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None and k not in ["nodes", "nodeIdentifierProperty"]
            }
            logger.info(f"Closeness centrality parameters: {params}")
            centrality = self.gds.closeness.stream(G, **params)

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
        )


class DegreeCentralityHandler(AlgorithmHandler):
    def degree_centrality(self, **kwargs):
        # with projected_graph(self.gds) as G:
        #     params = {
        #         k: v
        #         for k, v in kwargs.items()
        #         if v is not None and k not in ["nodes", "nodeIdentifierProperty"]
        #     }
        #     logger.info(f"Degree centrality parameters: {params}")
        #     centrality = self.gds.degree.stream(G, **params)

        # # Add node names to the results if nodeIdentifierProperty is provided
        # node_identifier_property = kwargs.get("nodeIdentifierProperty")
        # translate_ids_to_identifiers(self.gds, node_identifier_property, centrality)

        # # Filter results by node names if provided
        # node_names = kwargs.get("nodes", None)
        # centrality = filter_identifiers(
        #     self.gds, node_identifier_property, node_names, centrality
        # )
        orientation = kwargs.get("orientation")
        if orientation is None:
            relationships_dict = """
            {
                'RELATIONSHIPS': {
                    'sourceTable': 'NODES',
                    'targetTable': 'NODES',
                }
            }
            """
        else:
            relationships_dict = f"""
            {{
                'RELATIONSHIPS': {{
                    'sourceTable': 'NODES',
                    'targetTable': 'NODES',
                    'orientation': '{orientation}'
                }}
            }}
            """

        relationshipWeightProperty = kwargs.get("relationshipWeightProperty")
        if relationshipWeightProperty is None:
            compute_dict = """
            { }
            """
        else:
            compute_dict = f"""
            {{
                'relationshipWeightProperty': '{relationshipWeightProperty}'
            }}
            """

        res = self.gds.sql(
                f"""
                CALL Neo4j_Graph_Analytics.graph.degree('CPU_X64_XS', {{
                    'defaultTablePrefix': 'EXAMPLE_DB.PUBLIC',
                    'project': {{
                        'nodeTables': [ 'NODES' ],
                        'relationshipTables': {relationships_dict}
                    }},
                    'compute': {compute_dict},
                    'write': [{{
                        'nodeLabel': 'NODES',
                        'outputTable': 'NODES_DEGREE_CENTRALITY'
                    }}]
                }});
                """
        ).collect()

        logger.info(f"Degree centrality execution: {res}")
        output_table = self.gds.table("EXAMPLE_DB.PUBLIC.NODES_DEGREE_CENTRALITY")
        return output_table.to_pandas()

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.degree_centrality(
            orientation=arguments.get("orientation"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class EigenvectorCentralityHandler(AlgorithmHandler):
    def eigenvector_centrality(self, **kwargs):
        with projected_graph(self.gds) as G:
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None
                and k not in ["nodes", "nodeIdentifierProperty", "sourceNodes"]
            }
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            source_nodes = kwargs.get("sourceNodes", None)

            # Handle sourceNodes - convert names to IDs if nodeIdentifierProperty is provided
            translate_identifiers_to_ids(
                self.gds, source_nodes, "sourceNodes", node_identifier_property, params
            )

            logger.info(f"Eigenvector centrality parameters: {params}")
            centrality = self.gds.eigenvector.stream(G, **params)

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
        )


class PageRankHandler(AlgorithmHandler):
    def pagerank(self, **kwargs):
        with projected_graph(self.gds) as G:
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None
                and k not in ["nodes", "nodeIdentifierProperty", "sourceNodes"]
            }
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            source_nodes = kwargs.get("sourceNodes", None)

            # Handle sourceNodes - convert names to IDs if nodeIdentifierProperty is provided
            translate_identifiers_to_ids(
                self.gds, source_nodes, "sourceNodes", node_identifier_property, params
            )
            logger.info(f"Pagerank parameters: {params}")
            pageranks = self.gds.pageRank.stream(G, **params)

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
        )


class HarmonicCentralityHandler(AlgorithmHandler):
    def harmonic_centrality(self, **kwargs):
        with projected_graph(self.gds) as G:
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
        )


class HITSHandler(AlgorithmHandler):
    def hits(self, **kwargs):
        with projected_graph(self.gds) as G:
            params = {
                k: v
                for k, v in kwargs.items()
                if v is not None and k not in ["nodes", "nodeIdentifierProperty"]
            }
            logger.info(f"HITS parameters: {params}")
            result = self.gds.hits.stream(G, **params)

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
        )
