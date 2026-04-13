from typing import Dict, Any
from .algorithm_handler import AlgorithmHandler


class ProjectGraphCypherHandler(AlgorithmHandler):
    """Handler for projecting graphs using custom Cypher queries."""

    def project_graph_cypher(self, graph_name: str, cypher_query: str, **kwargs):
        """
        Project a graph using a custom Cypher query.

        Args:
            graph_name: Unique name for the projected graph
            cypher_query: Full Cypher projection query

        Returns:
            Graph metadata (node count, rel count, memory usage, properties)
        """
        if not graph_name:
            raise ValueError("graphName parameter is required")

        if not cypher_query:
            raise ValueError("cypherQuery parameter is required")

        try:
            # Call GDS cypher projection
            G, result = self.gds.graph.cypher.project(
                cypher_query, graph_name=graph_name
            )

            # Extract graph information
            graph_info = {
                "graphName": graph_name,
                "nodeCount": G.node_count(),
                "relationshipCount": G.relationship_count(),
                "memoryUsage": result.get("memoryUsage", "unknown"),
                "projectMillis": result.get("projectMillis", 0),
            }

            return graph_info

        except Exception as e:
            # Check if graph already exists
            error_msg = str(e).lower()
            if "already exists" in error_msg or "graph with name" in error_msg:
                raise ValueError(
                    f"Graph '{graph_name}' already exists. Use drop_graph to remove it first."
                )
            raise

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.project_graph_cypher(
            graph_name=arguments.get("graphName"),
            cypher_query=arguments.get("cypherQuery"),
        )


class DropGraphHandler(AlgorithmHandler):
    """Handler for dropping projected graphs."""

    def drop_graph(self, graph_name: str, **kwargs):
        """Drop a projected graph from memory."""
        if not graph_name:
            raise ValueError("graphName parameter is required")

        try:
            result = self.gds.graph.drop(graph_name)
            return {
                "graphName": graph_name,
                "dropped": True,
                "database": result.get("database", "unknown"),
            }
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg:
                return {
                    "graphName": graph_name,
                    "dropped": False,
                    "error": f"Graph '{graph_name}' does not exist",
                }
            raise

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.drop_graph(graph_name=arguments.get("graphName"))


class ListGraphsHandler(AlgorithmHandler):
    """Handler for listing all projected graphs."""

    def list_graphs(self, **kwargs):
        """List all projected graphs in the database."""
        graphs_df = self.gds.graph.list()

        if graphs_df.empty:
            return {"graphs": [], "count": 0}

        graphs = []
        for _, row in graphs_df.iterrows():
            graph_info = {
                "graphName": row["graphName"],
                "nodeCount": int(row["nodeCount"]),
                "relationshipCount": int(row["relationshipCount"]),
                "schema": row.get("schema", {}),
                "creationTime": row.get("creationTime", "unknown"),
                "memoryUsage": row.get("memoryUsage", "unknown"),
            }
            graphs.append(graph_info)

        return {"graphs": graphs, "count": len(graphs)}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.list_graphs()
