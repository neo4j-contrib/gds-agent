import pytest

from mcp_server_neo4j_gds import env_value
from mcp_server_neo4j_gds import server as server_module
from mcp_server_neo4j_gds.session_manager import SessionManager


def test_server_version_comes_from_package_metadata():
    assert server_module.SERVER_VERSION not in ("", "0.0.0")


def test_server_instructions_are_advertised():
    server = server_module.Server(
        server_module.SERVER_NAME,
        version=server_module.SERVER_VERSION,
        instructions=server_module.SERVER_INSTRUCTIONS,
    )

    options = server_module.initialization_options(server)

    assert options.instructions == server_module.SERVER_INSTRUCTIONS
    assert "project_graph_cypher" in options.instructions


def test_env_value_treats_empty_string_as_unset(monkeypatch):
    monkeypatch.setenv("GDS_AGENT_TEST_VAR", "")

    assert env_value("GDS_AGENT_TEST_VAR", default="fallback") == "fallback"


def test_empty_aura_credentials_rejected(monkeypatch):
    monkeypatch.setenv("AURA_API_CLIENT_ID", "")
    monkeypatch.setenv("AURA_API_CLIENT_SECRET", "")

    with pytest.raises(ValueError, match="Missing Aura API credentials"):
        SessionManager()._ensure_sessions_client()
