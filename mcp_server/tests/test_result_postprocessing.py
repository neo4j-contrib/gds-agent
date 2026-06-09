import pandas as pd

from mcp_server_neo4j_gds.centrality_algorithm_handlers import DegreeCentralityHandler
from mcp_server_neo4j_gds.node_translator import translate_ids_to_identifiers
from mcp_server_neo4j_gds.result_limits import SOURCE_ROW_COUNT_ATTR


class FakeUtil:
    def __init__(self):
        self.calls = []

    def asNode(self, node_id):
        self.calls.append(node_id)
        return {"name": f"node-{node_id}"}


def test_translate_ids_to_identifiers_limits_before_lookup(monkeypatch):
    monkeypatch.setenv("GDS_AGENT_MAX_RESULT_ROWS", "2")

    class FakeGds:
        util = FakeUtil()

    result = pd.DataFrame({"nodeId": [1, 2, 3]})

    translate_ids_to_identifiers(FakeGds, "name", result)

    assert FakeGds.util.calls == [1, 2]
    assert result["nodeName"].tolist() == ["node-1", "node-2"]
    assert result.attrs[SOURCE_ROW_COUNT_ATTR] == 3


def test_degree_centrality_filters_before_lookup():
    class FakeGraphRunner:
        def get(self, graph_name):
            return graph_name

    class FakeDegreeRunner:
        def stream(self, graph, **kwargs):
            return pd.DataFrame({"nodeId": [1, 2, 3], "score": [0.1, 0.2, 0.3]})

    class FakeGds:
        graph = FakeGraphRunner()
        degree = FakeDegreeRunner()
        util = FakeUtil()

        def run_cypher(self, query, params):
            assert params == {"names": ["target"]}
            return pd.DataFrame({"node_id": [3]})

    result = DegreeCentralityHandler(FakeGds()).execute(
        {
            "graphName": "g",
            "nodeIdentifierProperty": "name",
            "nodes": ["target"],
        }
    )

    assert FakeGds.util.calls == [3]
    assert result["nodeId"].tolist() == [3]
    assert result["nodeName"].tolist() == ["node-3"]
