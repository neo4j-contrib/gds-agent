from typing import Dict, Any
from .algorithm_handler import AlgorithmHandler


class ProjectGraphCypherHandler(AlgorithmHandler):
    def project_graph_cypher(self, graph_name: str, cypher_query: str, **kwargs):
        G, result = self.gds.graph.cypher.project(cypher_query, graph_name=graph_name)
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
            graphs.append({
                "graphName": row["graphName"],
                "nodeCount": int(row["nodeCount"]),
                "relationshipCount": int(row["relationshipCount"]),
                "schema": row.get("schema", {}),
                "creationTime": row.get("creationTime", "unknown"),
                "memoryUsage": row.get("memoryUsage", "unknown"),
            })

        return {"graphs": graphs, "count": len(graphs)}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.list_graphs()
