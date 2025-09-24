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

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Any:
        pass
