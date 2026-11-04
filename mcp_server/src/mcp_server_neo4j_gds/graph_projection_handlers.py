from typing import Any

from .algorithm_handler import AlgorithmHandler
from .gds import is_session_gds


def _as_dict(value):
    return value.to_dict() if hasattr(value, "to_dict") else value


def _as_list(value, default=None):
    if value is None:
        return default
    return value if isinstance(value, list) else [value]


class ProjectGraphCypherHandler(AlgorithmHandler):
    def project_graph_cypher(
        self,
        graph_name: str,
        cypher_query: str,
        undirected_relationship_types=None,
        **kwargs,
    ):
        if is_session_gds(self.gds):
            # In session (remote) mode undirectedRelationshipTypes is a top-level
            # projection parameter, not a key inside the gds.graph.project.remote
            # data config map, which rejects it.
            G, result = self.gds.graph.project.cypher(
                graph_name,
                cypher_query,
                undirected_relationship_types=undirected_relationship_types,
            )
        else:
            if undirected_relationship_types:
                raise ValueError(
                    "In plugin (on-prem) mode, undirected relationships are declared "
                    "inside the Cypher query, in the optional configuration map "
                    "(5th argument of gds.graph.project, after the data config map), "
                    "e.g. { undirectedRelationshipTypes: ['LINK'] }. The "
                    "undirectedRelationshipTypes tool parameter only applies to Aura "
                    "session mode."
                )
            G, result = self.gds.graph.project.cypher(
                cypher_query, graph_name=graph_name
            )
        return {
            "graphName": graph_name,
            "nodeCount": G.node_count(),
            "relationshipCount": G.relationship_count(),
            "memoryUsage": getattr(result, "memory_usage", "unknown"),
            "projectMillis": getattr(result, "project_millis", 0),
        }

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.project_graph_cypher(
            graph_name=arguments.get("graph_name"),
            cypher_query=arguments.get("cypher_query"),
            undirected_relationship_types=arguments.get(
                "undirected_relationship_types"
            ),
        )


class DropGraphHandler(AlgorithmHandler):
    def drop_graph(self, graph_name: str, **kwargs):
        dropped = self.gds.graph.drop(graph_name, fail_if_missing=True)
        info = dropped[0] if dropped else None
        return {
            "graphName": graph_name,
            "dropped": True,
            "database": getattr(info, "database", "unknown"),
        }

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.drop_graph(graph_name=arguments.get("graph_name"))


class ListGraphsHandler(AlgorithmHandler):
    def list_graphs(self, **kwargs):
        graph_infos = self.gds.graph.list()
        if not graph_infos:
            return {"graphs": [], "count": 0}

        graphs = []
        for info in graph_infos:
            graphs.append(
                {
                    "graphName": info.graph_name,
                    "nodeCount": int(info.node_count),
                    "relationshipCount": int(info.relationship_count),
                    "schema": getattr(info, "graph_schema", {}),
                    "creationTime": getattr(info, "creation_time", "unknown"),
                    "memoryUsage": getattr(info, "memory_usage", "unknown"),
                }
            )

        return {"graphs": graphs, "count": len(graphs)}

    def execute(self, arguments: dict[str, Any]) -> Any:
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

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.graph_info(graph_name=arguments.get("graph_name"))


class StreamNodePropertiesHandler(AlgorithmHandler):
    def stream_node_properties(
        self,
        graph_name: str,
        node_properties,
        node_labels=None,
        db_node_properties=None,
    ):
        G = self.gds.graph.get(graph_name)
        return self.gds.graph.node_properties.stream(
            G,
            node_properties=node_properties,
            node_labels=_as_list(node_labels, ["*"]),
            db_node_properties=_as_list(db_node_properties, []),
        )

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.stream_node_properties(
            graph_name=arguments.get("graph_name"),
            node_properties=arguments.get("node_properties"),
            node_labels=arguments.get("node_labels"),
            db_node_properties=arguments.get("db_node_properties"),
        )


class StreamRelationshipPropertiesHandler(AlgorithmHandler):
    def stream_relationship_properties(
        self,
        graph_name: str,
        relationship_properties,
        relationship_types=None,
    ):
        G = self.gds.graph.get(graph_name)
        return self.gds.graph.relationship_properties.stream(
            G,
            relationship_properties=_as_list(relationship_properties, []),
            relationship_types=_as_list(relationship_types, ["*"]),
        )

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.stream_relationship_properties(
            graph_name=arguments.get("graph_name"),
            relationship_properties=arguments.get("relationship_properties"),
            relationship_types=arguments.get("relationship_types"),
        )


class StreamRelationshipsHandler(AlgorithmHandler):
    def stream_relationships(self, graph_name: str, relationship_types=None):
        G = self.gds.graph.get(graph_name)
        return self.gds.graph.relationships.stream(
            G,
            relationship_types=_as_list(relationship_types, ["*"]),
        )

    def execute(self, arguments: dict[str, Any]) -> Any:
        return self.stream_relationships(
            graph_name=arguments.get("graph_name"),
            relationship_types=arguments.get("relationship_types"),
        )
