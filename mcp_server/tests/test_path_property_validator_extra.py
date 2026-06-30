"""Extra coverage for ``_validate_property_name`` and the path-handler fix.

Adds a few edge-case checks on top of ``test_path_property_injection.py``:

* the validator helper rejects empty strings, non-strings, dotted names,
  Cypher-syntax payloads, and identifiers wrapped in backticks;
* the validator accepts a representative set of legitimate identifier-shaped
  property names without modification;
* a handful of additional handlers accept legitimate property names and
  reject a different injection payload from the original PoC.

These tests use the same in-memory fake GDS object pattern as the existing
regression suite and run without Docker/Neo4j.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcp_server_neo4j_gds.path_algorithm_handlers import (
    _IDENTIFIER_RE,
    _validate_property_name,
    AStarShortestPathHandler,
    BreadthFirstSearchHandler,
    DijkstraShortestPathHandler,
)


class _RecordingGds:
    def __init__(self):
        self.queries: list[str] = []
        self.graph = type("_G", (), {"get": staticmethod(lambda name: name)})()

    def run_cypher(self, query, params=None):
        self.queries.append(query)
        return pd.DataFrame()


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "1name",  # starts with a digit
        "na me",  # contains a space
        "name)",  # parenthesis (the original PoC opener)
        "name) //",  # comment trailer
        "name; DROP",  # semicolon
        "na.me",  # dotted access
        "`name`",  # backticked identifier
        "name\n RETURN 1",  # newline + Cypher
        "naïve",  # non-ASCII letter (regex is ASCII-only)
        None,
        123,
        ["name"],
        {"name": "name"},
    ],
)
def test_validator_rejects_invalid_property_names(bad):
    with pytest.raises(ValueError):
        _validate_property_name(bad)


@pytest.mark.parametrize(
    "good",
    ["name", "Name", "title", "_private", "node_name", "Name123", "n", "_", "A1B2"],
)
def test_validator_accepts_identifier_shaped_names(good):
    assert _validate_property_name(good) == good
    assert _IDENTIFIER_RE.match(good) is not None


def test_dijkstra_with_legitimate_property_name_runs_lookup_query():
    gds = _RecordingGds()
    DijkstraShortestPathHandler(gds).execute(
        {
            "start_node": "A",
            "end_node": "B",
            "nodeIdentifierProperty": "title",
            "graphName": "g",
        }
    )
    assert gds.queries, "Expected a lookup query for legitimate input."
    assert "start.title" in gds.queries[0]
    assert "end.title" in gds.queries[0]


def test_astar_rejects_alternate_injection_payload():
    gds = _RecordingGds()
    payload = "name`) RETURN labels(start) AS leak //"
    with pytest.raises(ValueError):
        AStarShortestPathHandler(gds).execute(
            {
                "sourceNode": "A",
                "targetNode": "B",
                "nodeIdentifierProperty": payload,
                "graphName": "g",
            }
        )
    # Nothing should have been sent to run_cypher.
    assert gds.queries == []


def test_bfs_rejects_unicode_lookalike_payload():
    gds = _RecordingGds()
    # Cyrillic 'е' (U+0435) instead of ASCII 'e' — visually similar but not
    # in [A-Za-z]. Must be rejected by the ASCII-only identifier regex.
    payload = "nam\u0435"
    with pytest.raises(ValueError):
        BreadthFirstSearchHandler(gds).execute(
            {
                "sourceNode": "A",
                "nodeIdentifierProperty": payload,
                "graphName": "g",
            }
        )
    assert gds.queries == []
