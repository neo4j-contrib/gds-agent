from unittest.mock import Mock, MagicMock
import pytest
from src.mcp_server_neo4j_gds import server as server_module
from src.mcp_server_neo4j_gds import session_manager as session_manager_module
from src.mcp_server_neo4j_gds.session_manager import SessionManager, GdsMode


def test_detect_plugin_mode():
    mock_gds = Mock()
    mock_gds.run_cypher.side_effect = Exception("There is no procedure with the name")

    session_manager = SessionManager()
    mode = session_manager.detect_mode(mock_gds)

    assert mode == GdsMode.PLUGIN
    assert session_manager.mode == GdsMode.PLUGIN


def test_detect_session_mode():
    mock_gds = Mock()
    mock_gds.run_cypher.return_value = MagicMock()

    session_manager = SessionManager()
    mode = session_manager.detect_mode(mock_gds)

    assert mode == GdsMode.SESSION
    assert session_manager.mode == GdsMode.SESSION


def test_mode_cached_after_first_detection():
    mock_gds = Mock()
    mock_gds.run_cypher.return_value = MagicMock()

    session_manager = SessionManager()
    mode1 = session_manager.detect_mode(mock_gds)
    mode2 = session_manager.detect_mode(mock_gds)

    assert mode1 == mode2 == GdsMode.SESSION
    assert mock_gds.run_cypher.call_count == 1


def test_sessions_client_requires_aura_client_credentials(monkeypatch):
    monkeypatch.delenv("AURA_API_CLIENT_ID", raising=False)
    monkeypatch.delenv("AURA_API_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("AURA_API_PROJECT_ID", raising=False)

    session_manager = SessionManager()

    with pytest.raises(
        ValueError, match="AURA_API_CLIENT_ID and AURA_API_CLIENT_SECRET"
    ):
        session_manager._ensure_sessions_client()


def test_sessions_client_accepts_missing_project_id(monkeypatch):
    captured = {}

    class FakeAuraAPICredentials:
        def __init__(self, client_id, client_secret, project_id=None):
            captured["credentials"] = (client_id, client_secret, project_id)

    class FakeGdsSessions:
        def __init__(self, api_credentials):
            captured["api_credentials"] = api_credentials

    monkeypatch.setenv("AURA_API_CLIENT_ID", "client-id")
    monkeypatch.setenv("AURA_API_CLIENT_SECRET", "client-secret")
    monkeypatch.delenv("AURA_API_PROJECT_ID", raising=False)
    monkeypatch.setattr(
        session_manager_module, "AuraAPICredentials", FakeAuraAPICredentials
    )
    monkeypatch.setattr(session_manager_module, "GdsSessions", FakeGdsSessions)

    session_manager = SessionManager()
    session_manager._ensure_sessions_client()

    assert captured["credentials"] == ("client-id", "client-secret", None)


def test_create_base_gds_uses_driver_connection_for_versionless_aura(monkeypatch):
    class FakeGraphDataScience:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Aura Graph Analytics is versionless.")

    class FakeNeo4jDriverConnection:
        def __init__(self, db_url, username, password, database):
            self.args = (db_url, username, password, database)

    monkeypatch.setattr(server_module, "GraphDataScience", FakeGraphDataScience)
    monkeypatch.setattr(
        server_module, "Neo4jDriverConnection", FakeNeo4jDriverConnection
    )

    connection = server_module.create_base_gds("neo4j+s://example", "neo4j", "pw")

    assert isinstance(connection, FakeNeo4jDriverConnection)
    assert connection.args == ("neo4j+s://example", "neo4j", "pw", None)
