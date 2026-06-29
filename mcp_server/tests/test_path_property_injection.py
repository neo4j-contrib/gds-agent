"""Regression tests for CWE-943 Cypher injection via nodeIdentifierProperty.

The path-algorithm handlers interpolate ``nodeIdentifierProperty`` into
Cypher queries via Python f-strings. Without validation a malicious MCP
caller could break out of the property accessor (``start.<name>``) and
execute arbitrary Cypher.

These tests use a small in-memory fake GDS object so they run without a
live Neo4j; they cover both the rejection path (malicious input raises
``ValueError`` before any query is built) and a sanity check that
legitimate identifier-shaped property names continue to work.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcp_server_neo4j_gds.path_algorithm_handlers import (
    AStarShortestPathHandler,
    BellmanFordSingleSourceShortestPathHandler,
    BreadthFirstSearchHandler,
    DeltaSteppingShortestPathHandler,
    DepthFirstSearchHandler,
    DijkstraShortestPathHandler,
    DijkstraSingleSourceShortestPathHandler,
    LongestPathHandler,
    MaxFlowHandler,
    MinimumDirectedSteinerTreeHandler,
    MinimumWeightSpanningTreeHandler,
    RandomWalkHandler,
    YensShortestPathsHandler,
)


class _RecordingGds:
    """Captures every Cypher query sent to ``run_cypher``."""

    def __init__(self):
        self.queries: list[str] = []
        self.graph = type("_G", (), {"get": staticmethod(lambda name: name)})()

    def run_cypher(self, query, params=None):
        self.queries.append(query)
        return pd.DataFrame()


# Common injection payload: terminates the property accessor and tries to
# inject extra Cypher. Any handler that builds a Cypher query containing
# this fragment would be exploitable.
MALICIOUS = "name) RETURN 1 AS pwned //"


def _assert_no_injection(gds: _RecordingGds) -> None:
    for query in gds.queries:
        assert "RETURN 1 AS pwned" not in query, (
            "Injected Cypher reached run_cypher; the property name is "
            "concatenated into the query without validation. Captured: " + query
        )


@pytest.mark.parametrize(
    "handler_cls, arguments",
    [
        (
            DijkstraShortestPathHandler,
            {
                "start_node": "A",
                "end_node": "B",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            DeltaSteppingShortestPathHandler,
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            DijkstraSingleSourceShortestPathHandler,
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            AStarShortestPathHandler,
            {
                "sourceNode": "A",
                "targetNode": "B",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            YensShortestPathsHandler,
            {
                "sourceNode": "A",
                "targetNode": "B",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            MinimumWeightSpanningTreeHandler,
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            MinimumDirectedSteinerTreeHandler,
            {
                "sourceNode": "A",
                "targetNodes": ["B"],
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            BreadthFirstSearchHandler,
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            DepthFirstSearchHandler,
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            BellmanFordSingleSourceShortestPathHandler,
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
        (
            MaxFlowHandler,
            {
                "sourceNodes": ["A"],
                "targetNodes": ["B"],
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            },
        ),
    ],
)
def test_handlers_reject_malicious_node_identifier_property(handler_cls, arguments):
    gds = _RecordingGds()
    with pytest.raises(ValueError):
        handler_cls(gds).execute(arguments)
    _assert_no_injection(gds)


def test_random_walk_rejects_malicious_node_identifier_property():
    gds = _RecordingGds()
    with pytest.raises(ValueError):
        RandomWalkHandler(gds).execute(
            {
                "sourceNodes": ["A"],
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            }
        )
    _assert_no_injection(gds)


def test_longest_path_rejects_malicious_node_identifier_property():
    gds = _RecordingGds()
    with pytest.raises(ValueError):
        LongestPathHandler(gds).execute(
            {
                "targetNodes": ["A"],
                "nodeIdentifierProperty": MALICIOUS,
                "graphName": "g",
            }
        )
    _assert_no_injection(gds)


def test_legitimate_property_name_is_accepted():
    """Sanity check: identifier-shaped names continue to work."""

    gds = _RecordingGds()
    result = DijkstraShortestPathHandler(gds).execute(
        {
            "start_node": "A",
            "end_node": "B",
            "nodeIdentifierProperty": "name",
            "graphName": "g",
        }
    )
    assert result == {
        "found": False,
        "message": "One or both node names not found",
    }
    assert gds.queries, "Expected the handler to run a lookup query."
    assert "start.name" in gds.queries[0]
