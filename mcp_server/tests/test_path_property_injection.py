"""Unit tests for the ``nodeIdentifierProperty`` validation added to
``mcp_server_neo4j_gds.path_algorithm_handlers``.

The regression is CWE-943 (Cypher injection): the property-accessor name
was interpolated raw into f-string queries. All affected handlers now
share a single ``_validate_property_name`` guard, so these unit tests
focus on the guard itself and on the wiring — they don't call every one
of the 13 handlers, because per-handler end-to-end behaviour against a
real Neo4j+GDS is covered by ``test_path_algorithms.py``.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcp_server_neo4j_gds.path_algorithm_handlers import (
    _IDENTIFIER_RE,
    _validate_property_name,
    DijkstraShortestPathHandler,
)


class _RecordingGds:
    """Captures every Cypher query sent to ``run_cypher``."""

    def __init__(self):
        self.queries: list[str] = []
        self.graph = type("_G", (), {"get": staticmethod(lambda name: name)})()

    def run_cypher(self, query, params=None):
        self.queries.append(query)
        return pd.DataFrame()


# Payloads that must be rejected. The regex allows unquoted-identifier
# shape only, so anything with punctuation, whitespace, non-ASCII
# letters, or non-string types must raise ValueError.
INVALID_PROPERTY_NAMES = [
    "",
    "1name",  # starts with a digit
    "na me",  # whitespace
    "name)",  # parenthesis
    "name) //",  # comment trailer
    # Reviewer note: `name) RETURN 1 AS pwned //` on its own is not valid
    # Cypher (the WHERE has no boolean predicate) — but a payload with a
    # trivial predicate would parse. Both must be rejected up front.
    "name) IS NOT NULL WITH 1 AS pwned RETURN pwned //",
    "name) = start.name //",
    "na.me",  # dotted access
    "\u0060name\u0060",  # quoted identifier (Cypher accent-quoted, U+0060)
    "name\n RETURN 1",  # newline + Cypher
    "naïve",  # non-ASCII letter (regex is ASCII-only)
    "nam\u0435",  # visually-similar Cyrillic 'е'
    None,
    123,
    ["name"],
    {"name": "name"},
]

VALID_PROPERTY_NAMES = [
    "name",
    "Name",
    "title",
    "_private",
    "node_name",
    "Name123",
    "n",
    "_",
    "A1B2",
]


@pytest.mark.parametrize("bad", INVALID_PROPERTY_NAMES)
def test_validator_rejects_invalid_property_names(bad):
    with pytest.raises(ValueError):
        _validate_property_name(bad)


@pytest.mark.parametrize("good", VALID_PROPERTY_NAMES)
def test_validator_accepts_identifier_shaped_names(good):
    assert _validate_property_name(good) == good
    assert _IDENTIFIER_RE.match(good) is not None


# One handler-level smoke test is enough to confirm the guard is wired
# into the execute() path. The rejection contract is the same for every
# handler because they all delegate to _validate_property_name, and the
# happy path is covered end-to-end (against a live Neo4j+GDS) by
# tests/test_path_algorithms.py.
def test_dijkstra_rejects_injection_before_running_cypher():
    gds = _RecordingGds()
    with pytest.raises(ValueError):
        DijkstraShortestPathHandler(gds).execute(
            {
                "start_node": "A",
                "end_node": "B",
                # This payload is syntactically valid Cypher when
                # concatenated into the pre-patch WHERE clause (unlike
                # the earlier `name) RETURN 1 AS pwned //`, which the
                # query engine rejected with a type error). It must be
                # rejected by the Python-level validator, well before
                # anything reaches run_cypher.
                "nodeIdentifierProperty": (
                    "name) IS NOT NULL WITH 1 AS pwned RETURN pwned //"
                ),
                "graphName": "g",
            }
        )
    assert gds.queries == [], (
        "run_cypher must not be called when the property name is invalid."
    )


def test_dijkstra_accepts_legitimate_property_name():
    gds = _RecordingGds()
    result = DijkstraShortestPathHandler(gds).execute(
        {
            "start_node": "A",
            "end_node": "B",
            "nodeIdentifierProperty": "title",
            "graphName": "g",
        }
    )
    # Empty DataFrame -> handler returns "not found".
    assert result == {
        "found": False,
        "message": "One or both node names not found",
    }
    assert gds.queries, "Expected the handler to run a lookup query."
    assert "start.title" in gds.queries[0]
    assert "end.title" in gds.queries[0]
