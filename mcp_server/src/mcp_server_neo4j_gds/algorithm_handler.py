from abc import ABC, abstractmethod
from typing import Dict, Any
from graphdatascience import GraphDataScience


def clean_params(arguments: Dict[str, Any], forbidden):
    if len(forbidden) == 0:
        return arguments
    params = {
        k: v for k, v in arguments.items() if v is not None and k not in forbidden
    }
    return params


class AlgorithmHandler(ABC):
    def __init__(self, gds: GraphDataScience):
        self.gds = gds

    def get_graph(self, graph_name: str):
        """
        Get a projected graph by name with validation.

        Args:
            graph_name: Name of the projected graph

        Returns:
            Graph object

        Raises:
            ValueError: If graph_name is not provided or graph not found
        """
        if not graph_name:
            raise ValueError("graphName parameter is required")

        try:
            return self.gds.graph.get(graph_name)
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg:
                raise ValueError(
                    f"Graph '{graph_name}' not found. Use project_graph_cypher to create it first."
                )
            raise

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Any:
        pass
