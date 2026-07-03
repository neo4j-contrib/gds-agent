import pytest
from mcp.server import Server

from mcp_server_neo4j_gds import env_value
from mcp_server_neo4j_gds import server as server_module
from mcp_server_neo4j_gds.graph_projection_specs import (
    graph_projection_tool_definitions,
)
from mcp_server_neo4j_gds.centrality_algorithm_specs import (
    centrality_tool_definitions,
)
from mcp_server_neo4j_gds.ml_pipeline_specs import ml_pipeline_tool_definitions
from mcp_server_neo4j_gds.instructions import SERVER_INSTRUCTIONS
from mcp_server_neo4j_gds.session_manager import SessionManager
from mcp_server_neo4j_gds.tool_annotations import apply_tool_annotations


def annotated(definitions):
    return {tool.name: tool for tool in apply_tool_annotations(list(definitions))}


def test_initialization_options_carry_instructions():
    server = Server("test", version="1", instructions=SERVER_INSTRUCTIONS)
    options = server_module.initialization_options(server)

    assert options.instructions == SERVER_INSTRUCTIONS
    assert server.create_initialization_options().instructions == SERVER_INSTRUCTIONS


def test_server_version_comes_from_package_metadata():
    assert server_module.SERVER_VERSION not in ("", "0.0.0")


def test_drop_tools_annotated_destructive():
    tools = annotated(graph_projection_tool_definitions + ml_pipeline_tool_definitions)

    for name in ("drop_graph", "drop_model"):
        assert tools[name].annotations.destructiveHint is True
        assert tools[name].annotations.readOnlyHint is False


def test_accessor_tools_annotated_read_only():
    tools = annotated(graph_projection_tool_definitions + ml_pipeline_tool_definitions)

    for name in (
        "list_graphs",
        "get_graph_info",
        "stream_node_properties",
        "list_models",
    ):
        assert tools[name].annotations.readOnlyHint is True


def test_writing_tools_annotated_non_destructive():
    tools = annotated(graph_projection_tool_definitions + centrality_tool_definitions)

    for name in ("project_graph_cypher", "pagerank"):
        assert tools[name].annotations.readOnlyHint is False
        assert tools[name].annotations.destructiveHint is False


def test_apply_tool_annotations_preserves_existing():
    from mcp import types

    tool = types.Tool(
        name="custom",
        inputSchema={"type": "object"},
        annotations=types.ToolAnnotations(readOnlyHint=False),
    )
    existing = tool.annotations
    apply_tool_annotations([tool])

    assert tool.annotations is existing


def test_env_value_treats_empty_string_as_unset(monkeypatch):
    monkeypatch.setenv("GDS_AGENT_TEST_VAR", "")

    assert env_value("GDS_AGENT_TEST_VAR", default="fallback") == "fallback"


def test_empty_aura_credentials_rejected(monkeypatch):
    monkeypatch.setenv("AURA_API_CLIENT_ID", "")
    monkeypatch.setenv("AURA_API_CLIENT_SECRET", "")

    with pytest.raises(ValueError, match="Missing Aura API credentials"):
        SessionManager()._ensure_sessions_client()
