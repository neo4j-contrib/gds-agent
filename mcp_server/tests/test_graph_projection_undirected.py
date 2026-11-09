from unittest.mock import MagicMock, Mock

import pytest
from graphdatascience.session.aura_graph_data_science import AuraGraphDataScience

from src.mcp_server_neo4j_gds.graph_projection_handlers import (
    ProjectGraphCypherHandler,
)
from src.mcp_server_neo4j_gds.graph_projection_specs import (
    get_graph_projection_tool_definitions,
)
from src.mcp_server_neo4j_gds.session_manager import GdsMode

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
    gds.graph.project.cypher.return_value = (_mock_graph(), {})

    ProjectGraphCypherHandler(gds).execute(
        {
            "graph_name": "g",
            "cypher_query": CYPHER,
            "undirected_relationship_types": ["LINK"],
        }
    )

    _, kwargs = gds.graph.project.cypher.call_args
    assert kwargs["undirected_relationship_types"] == ["LINK"]


def test_session_mode_without_undirected_passes_none():
    gds = Mock(spec=AuraGraphDataScience)
    gds.graph.project.cypher.return_value = (_mock_graph(), {})

    ProjectGraphCypherHandler(gds).execute({"graph_name": "g", "cypher_query": CYPHER})

    _, kwargs = gds.graph.project.cypher.call_args
    assert kwargs["undirected_relationship_types"] is None


def test_plugin_mode_rejects_undirected_relationship_types():
    gds = MagicMock()  # not an AuraGraphDataScience -> plugin mode

    with pytest.raises(ValueError, match="plugin"):
        ProjectGraphCypherHandler(gds).execute(
            {
                "graph_name": "g",
                "cypher_query": CYPHER,
                "undirected_relationship_types": ["LINK"],
            }
        )
    gds.graph.project.cypher.assert_not_called()


def test_project_graph_cypher_spec_differs_by_mode():
    plugin_tool = get_graph_projection_tool_definitions(GdsMode.PLUGIN)[0]
    session_tool = get_graph_projection_tool_definitions(GdsMode.SESSION)[0]

    assert plugin_tool.name == "project_graph_cypher"
    assert set(plugin_tool.input_schema["properties"]) == {
        "graph_name",
        "cypher_query",
    }
    assert plugin_tool.input_schema["required"] == ["graph_name", "cypher_query"]
    assert "gds.graph.project(" in plugin_tool.description
    assert "gds.graph.project.remote" not in plugin_tool.description

    assert session_tool.name == "project_graph_cypher"
    assert set(session_tool.input_schema["properties"]) == {
        "graph_name",
        "cypher_query",
        "session_name",
        "undirected_relationship_types",
    }
    assert session_tool.input_schema["required"] == [
        "graph_name",
        "cypher_query",
        "session_name",
    ]
    assert "gds.graph.project.remote(" in session_tool.description
    assert "gds.graph.project(" not in session_tool.description
