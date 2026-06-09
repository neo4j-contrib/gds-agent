import pandas as pd

from mcp_server_neo4j_gds.graph_projection_handlers import (
    GraphInfoHandler,
    StreamNodePropertiesHandler,
    StreamRelationshipPropertiesHandler,
    StreamRelationshipsHandler,
)


class FakeGraph:
    def name(self):
        return "g"

    def database(self):
        return "neo4j"

    def exists(self):
        return True

    def node_count(self):
        return 3

    def relationship_count(self):
        return 2

    def node_labels(self):
        return ["Person"]

    def relationship_types(self):
        return ["KNOWS"]

    def node_properties(self):
        return pd.Series({"Person": ["score"]})

    def relationship_properties(self):
        return pd.Series({"KNOWS": ["weight"]})

    def degree_distribution(self):
        return pd.Series({"min": 1, "max": 2})

    def density(self):
        return 0.5

    def size_in_bytes(self):
        return 1024

    def memory_usage(self):
        return "1 KiB"

    def configuration(self):
        return pd.Series({"relationshipProjection": "KNOWS"})

    def creation_time(self):
        return "created"

    def modification_time(self):
        return "modified"


class FakeRunner:
    def __init__(self, graph):
        self.graph = graph
        self.calls = []

    def get(self, graph_name):
        self.calls.append(("get", graph_name))
        return self.graph


class FakeStreamRunner:
    def __init__(self, calls, name):
        self.calls = calls
        self.name = name

    def stream(self, graph, **kwargs):
        self.calls.append((self.name, graph, kwargs))
        return pd.DataFrame({"ok": [True]})


class FakeGds:
    def __init__(self):
        self.calls = []
        graph = FakeGraph()
        self.graph = FakeRunner(graph)
        self.graph.nodeProperties = FakeStreamRunner(self.calls, "nodeProperties")
        self.graph.relationshipProperties = FakeStreamRunner(
            self.calls, "relationshipProperties"
        )
        self.graph.relationships = FakeStreamRunner(self.calls, "relationships")


def test_graph_info_handler_returns_graph_metadata():
    result = GraphInfoHandler(FakeGds()).execute({"graphName": "g"})

    assert result["graphName"] == "g"
    assert result["nodeLabels"] == ["Person"]
    assert result["nodeProperties"] == {"Person": ["score"]}
    assert result["relationshipProperties"] == {"KNOWS": ["weight"]}


def test_stream_node_properties_handler_maps_arguments():
    gds = FakeGds()

    result = StreamNodePropertiesHandler(gds).execute(
        {
            "graphName": "g",
            "nodeProperties": ["score"],
            "nodeLabels": "Person",
            "dbNodeProperties": ["name"],
        }
    )

    assert result["ok"].tolist() == [True]
    _, _, kwargs = gds.calls[0]
    assert kwargs == {
        "node_properties": ["score"],
        "node_labels": ["Person"],
        "db_node_properties": ["name"],
        "separate_property_columns": True,
    }


def test_stream_relationship_properties_handler_maps_arguments():
    gds = FakeGds()

    StreamRelationshipPropertiesHandler(gds).execute(
        {
            "graphName": "g",
            "relationshipProperties": "weight",
            "relationshipTypes": "KNOWS",
        }
    )

    _, _, kwargs = gds.calls[0]
    assert kwargs == {
        "relationship_properties": ["weight"],
        "relationship_types": ["KNOWS"],
        "separate_property_columns": True,
    }


def test_stream_relationships_handler_maps_arguments():
    gds = FakeGds()

    StreamRelationshipsHandler(gds).execute(
        {"graphName": "g", "relationshipTypes": "KNOWS"}
    )

    _, _, kwargs = gds.calls[0]
    assert kwargs == {"relationship_types": ["KNOWS"]}
