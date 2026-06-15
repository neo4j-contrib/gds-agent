from unittest.mock import Mock, MagicMock

import pytest
from graphdatascience.session.aura_graph_data_science import AuraGraphDataScience

from src.mcp_server_neo4j_gds.graph_projection_handlers import (
    ProjectGraphCypherHandler,
)

CYPHER = (
    "MATCH (n)-[r:LINK]->(m) RETURN gds.graph.project.remote(n, m, "
    "{relationshipType: 'LINK'})"
)


def _mock_graph():
    G = Mock()
    G.node_count.return_value = 10
    G.relationship_count.return_value = 20
    return G


def test_session_mode_forwards_undirected_relationship_types():
    gds = Mock(spec=AuraGraphDataScience)
    gds.graph.project.return_value = (_mock_graph(), {})

    ProjectGraphCypherHandler(gds).execute(
        {
            "graphName": "g",
            "cypherQuery": CYPHER,
            "undirectedRelationshipTypes": ["LINK"],
        }
    )

    _, kwargs = gds.graph.project.call_args
    assert kwargs["undirected_relationship_types"] == ["LINK"]


def test_session_mode_without_undirected_passes_none():
    gds = Mock(spec=AuraGraphDataScience)
    gds.graph.project.return_value = (_mock_graph(), {})

    ProjectGraphCypherHandler(gds).execute({"graphName": "g", "cypherQuery": CYPHER})

    _, kwargs = gds.graph.project.call_args
    assert kwargs["undirected_relationship_types"] is None


def test_plugin_mode_rejects_undirected_relationship_types():
    gds = MagicMock()  # not an AuraGraphDataScience -> plugin mode

    with pytest.raises(ValueError, match="plugin"):
        ProjectGraphCypherHandler(gds).execute(
            {
                "graphName": "g",
                "cypherQuery": CYPHER,
                "undirectedRelationshipTypes": ["LINK"],
            }
        )
    gds.graph.cypher.project.assert_not_called()
