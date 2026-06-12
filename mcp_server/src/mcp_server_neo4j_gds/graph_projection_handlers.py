from typing import Dict, Any
from .algorithm_handler import AlgorithmHandler
from .gds import is_session_gds


def _as_dict(value):
    return value.to_dict() if hasattr(value, "to_dict") else value


def _as_list(value, default=None):
    if value is None:
        return default
    return value if isinstance(value, list) else [value]


class ProjectGraphCypherHandler(AlgorithmHandler):
    def project_graph_cypher(self, graph_name: str, cypher_query: str, **kwargs):
        if is_session_gds(self.gds):
            G, result = self.gds.graph.project(graph_name, cypher_query)
        else:
            G, result = self.gds.graph.cypher.project(
                cypher_query, graph_name=graph_name
            )
        return {
            "graphName": graph_name,
            "nodeCount": G.node_count(),
            "relationshipCount": G.relationship_count(),
            "memoryUsage": result.get("memoryUsage", "unknown"),
            "projectMillis": result.get("projectMillis", 0),
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.project_graph_cypher(
            graph_name=arguments.get("graphName"),
            cypher_query=arguments.get("cypherQuery"),
        )


class DropGraphHandler(AlgorithmHandler):
    def drop_graph(self, graph_name: str, **kwargs):
        result = self.gds.graph.drop(graph_name)
        return {
            "graphName": graph_name,
            "dropped": True,
            "database": result.get("database", "unknown"),
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.drop_graph(graph_name=arguments.get("graphName"))


class ListGraphsHandler(AlgorithmHandler):
    def list_graphs(self, **kwargs):
        graphs_df = self.gds.graph.list()
        if graphs_df.empty:
            return {"graphs": [], "count": 0}

        graphs = []
        for _, row in graphs_df.iterrows():
            graphs.append(
                {
                    "graphName": row["graphName"],
                    "nodeCount": int(row["nodeCount"]),
                    "relationshipCount": int(row["relationshipCount"]),
                    "schema": row.get("schema", {}),
                    "creationTime": row.get("creationTime", "unknown"),
                    "memoryUsage": row.get("memoryUsage", "unknown"),
                }
            )

        return {"graphs": graphs, "count": len(graphs)}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.list_graphs()


class GraphInfoHandler(AlgorithmHandler):
    def graph_info(self, graph_name: str):
        G = self.gds.graph.get(graph_name)
        exists = G.exists()
        if not exists:
            return {"graphName": graph_name, "exists": False}

        return {
            "graphName": G.name(),
            "database": G.database(),
            "exists": exists,
            "nodeCount": G.node_count(),
            "relationshipCount": G.relationship_count(),
            "nodeLabels": G.node_labels(),
            "relationshipTypes": G.relationship_types(),
            "nodeProperties": _as_dict(G.node_properties()),
            "relationshipProperties": _as_dict(G.relationship_properties()),
            "degreeDistribution": _as_dict(G.degree_distribution()),
            "density": G.density(),
            "sizeInBytes": G.size_in_bytes(),
            "memoryUsage": G.memory_usage(),
            "configuration": _as_dict(G.configuration()),
            "creationTime": G.creation_time(),
            "modificationTime": G.modification_time(),
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.graph_info(graph_name=arguments.get("graphName"))


class StreamNodePropertiesHandler(AlgorithmHandler):
    def stream_node_properties(
        self,
        graph_name: str,
        node_properties,
        node_labels=None,
        db_node_properties=None,
    ):
        G = self.gds.graph.get(graph_name)
        return self.gds.graph.nodeProperties.stream(
            G,
            node_properties=node_properties,
            node_labels=_as_list(node_labels, ["*"]),
            db_node_properties=_as_list(db_node_properties, []),
            separate_property_columns=True,
        )

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.stream_node_properties(
            graph_name=arguments.get("graphName"),
            node_properties=arguments.get("nodeProperties"),
            node_labels=arguments.get("nodeLabels"),
            db_node_properties=arguments.get("dbNodeProperties"),
        )


class StreamRelationshipPropertiesHandler(AlgorithmHandler):
    def stream_relationship_properties(
        self,
        graph_name: str,
        relationship_properties,
        relationship_types=None,
    ):
        G = self.gds.graph.get(graph_name)
        return self.gds.graph.relationshipProperties.stream(
            G,
            relationship_properties=_as_list(relationship_properties, []),
            relationship_types=_as_list(relationship_types, ["*"]),
            separate_property_columns=True,
        )

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.stream_relationship_properties(
            graph_name=arguments.get("graphName"),
            relationship_properties=arguments.get("relationshipProperties"),
            relationship_types=arguments.get("relationshipTypes"),
        )


class StreamRelationshipsHandler(AlgorithmHandler):
    def stream_relationships(self, graph_name: str, relationship_types=None):
        G = self.gds.graph.get(graph_name)
        return self.gds.graph.relationships.stream(
            G,
            relationship_types=_as_list(relationship_types, ["*"]),
        )

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.stream_relationships(
            graph_name=arguments.get("graphName"),
            relationship_types=arguments.get("relationshipTypes"),
        )
