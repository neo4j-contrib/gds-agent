from unittest.mock import Mock, MagicMock
import pytest
from src.mcp_server_neo4j_gds import server as server_module
from src.mcp_server_neo4j_gds import session_manager as session_manager_module
from src.mcp_server_neo4j_gds.session_manager import (
    SessionManager,
    GdsMode,
    default_session_name,
)


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


def test_default_session_name_depends_on_database_identity():
    name1 = default_session_name("neo4j+s://db1.databases.neo4j.io", "neo4j")
    name2 = default_session_name("neo4j+s://db2.databases.neo4j.io", "neo4j")
    name3 = default_session_name("neo4j+s://db1.databases.neo4j.io", "analytics")

    assert name1.startswith("mcp_gds_session_")
    assert name1 != name2
    assert name1 != name3


def test_create_or_get_session_uses_database_specific_default_name():
    class FakeGds:
        pass

    class FakeGdsSessions:
        def __init__(self):
            self.created_session_name = None

        def list(self):
            return []

        def get_or_create(self, *args, **kwargs):
            self.created_session_name = kwargs["session_name"]
            return FakeGds()

    fake_sessions = FakeGdsSessions()
    session_manager = SessionManager()
    session_manager._sessions_client = fake_sessions

    session_manager.create_or_get_session(
        "neo4j+s://db1.databases.neo4j.io", ("neo4j", "pw"), "neo4j"
    )

    assert fake_sessions.created_session_name == default_session_name(
        "neo4j+s://db1.databases.neo4j.io", "neo4j"
    )


def test_create_or_get_session_reuses_available_cached_session():
    session_name = default_session_name("bolt://example")

    class FakeSessionInfo:
        name = session_name
        status = "Ready"

    class FakeGds:
        closed = False

        def close(self):
            self.closed = True

    class FakeGdsSessions:
        def list(self):
            return [FakeSessionInfo()]

        def get_or_create(self, *args, **kwargs):
            raise AssertionError("cached session should be reused")

    cached_gds = FakeGds()
    session_manager = SessionManager()
    session_manager._sessions_client = FakeGdsSessions()
    session_manager.session_gds = cached_gds
    session_manager.session_name = session_name

    result = session_manager.create_or_get_session("bolt://example", ("neo4j", "pw"))

    assert result is cached_gds
    assert not cached_gds.closed


def test_create_or_get_session_recreates_missing_cached_session():
    session_name = default_session_name("bolt://example")

    class FakeGds:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    class FakeGdsSessions:
        def __init__(self, new_gds):
            self.new_gds = new_gds
            self.created = 0

        def list(self):
            return []

        def get_or_create(self, *args, **kwargs):
            self.created += 1
            return self.new_gds

    cached_gds = FakeGds()
    new_gds = FakeGds()
    fake_sessions = FakeGdsSessions(new_gds)
    session_manager = SessionManager()
    session_manager._sessions_client = fake_sessions
    session_manager.session_gds = cached_gds
    session_manager.session_name = session_name

    result = session_manager.create_or_get_session("bolt://example", ("neo4j", "pw"))

    assert cached_gds.closed
    assert result is new_gds
    assert fake_sessions.created == 1
    assert session_manager.session_gds is new_gds
    assert session_manager.session_name == session_name


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
