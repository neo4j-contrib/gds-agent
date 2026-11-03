import re
from abc import ABC, abstractmethod
from typing import Any

from graphdatascience import GraphDataScience


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def snake_case_keys(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    return {snake_case(key): snake_case_keys(item) for key, item in value.items()}


def clean_params(arguments: dict[str, Any], forbidden):
    return {
        snake_case(key): value
        for key, value in arguments.items()
        if value is not None and key not in forbidden
    }


class AlgorithmHandler(ABC):
    def __init__(self, gds: GraphDataScience):
        self.gds = gds

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> Any:
        pass
