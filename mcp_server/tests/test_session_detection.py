from unittest.mock import Mock, MagicMock
import pytest
from src.mcp_server_neo4j_gds import server as server_module
from src.mcp_server_neo4j_gds import session_manager as session_manager_module
from src.mcp_server_neo4j_gds.session_manager import (
    SessionManager,
    GdsMode,
    ensure_mcp_session_name,
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


def test_create_or_get_session_reuses_available_cached_session():
    class FakeSessionInfo:
        name = "mcp_analytics"
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
    session_manager._sessions["mcp_analytics"] = cached_gds

    result = session_manager.create_or_get_session(
        "bolt://example", ("neo4j", "pw"), session_name="analytics"
    )

    assert result is cached_gds
    assert not cached_gds.closed


def test_create_or_get_session_recreates_missing_cached_session():
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
    session_manager._sessions["mcp_analytics"] = cached_gds

    result = session_manager.create_or_get_session(
        "bolt://example", ("neo4j", "pw"), session_name="analytics"
    )

    assert cached_gds.closed
    assert result is new_gds
    assert fake_sessions.created == 1
    assert session_manager._sessions["mcp_analytics"] is new_gds


def test_ensure_mcp_session_name_enforces_prefix():
    assert ensure_mcp_session_name("analytics") == "mcp_analytics"
    assert ensure_mcp_session_name("mcp_analytics") == "mcp_analytics"
    with pytest.raises(ValueError):
        ensure_mcp_session_name("")
    with pytest.raises(ValueError):
        ensure_mcp_session_name(None)


def test_sessions_are_cached_independently():
    class FakeSessionInfo:
        def __init__(self, name):
            self.name = name
            self.status = "Ready"

    class FakeGds:
        def close(self):
            pass

    class FakeGdsSessions:
        def __init__(self):
            self.created = []

        def list(self):
            return [FakeSessionInfo(name) for name in self.created]

        def get_or_create(self, *args, **kwargs):
            self.created.append(kwargs["session_name"])
            return FakeGds()

    fake_sessions = FakeGdsSessions()
    manager = SessionManager()
    manager._sessions_client = fake_sessions

    first = manager.create_or_get_session(
        "bolt://example", ("neo4j", "pw"), session_name="analytics"
    )
    second = manager.create_or_get_session(
        "bolt://example", ("neo4j", "pw"), session_name="reporting"
    )

    assert fake_sessions.created == ["mcp_analytics", "mcp_reporting"]
    assert first is not second
    assert dict(manager.active_sessions()) == {
        "mcp_analytics": first,
        "mcp_reporting": second,
    }

    reused = manager.create_or_get_session(
        "bolt://example", ("neo4j", "pw"), session_name="mcp_analytics"
    )

    assert reused is first
    assert fake_sessions.created == ["mcp_analytics", "mcp_reporting"]


def test_get_session_returns_cached_session_or_none():
    class FakeSessionInfo:
        name = "mcp_analytics"
        status = "Ready"

    class FakeGdsSessions:
        def list(self):
            return [FakeSessionInfo()]

    manager = SessionManager()
    manager._sessions_client = FakeGdsSessions()
    cached = Mock()
    manager._sessions["mcp_analytics"] = cached

    assert manager.get_session("analytics") is cached
    assert manager.get_session("missing") is None


def test_graph_routing_tracks_sessions_and_conflicts():
    manager = SessionManager()
    manager._sessions["mcp_first"] = Mock()
    manager._sessions["mcp_analytics"] = Mock()

    manager.record_graph("g1", "mcp_first")
    manager.record_graph("g2", "mcp_analytics")

    assert manager.session_for_graph("g1") == "mcp_first"
    assert manager.session_for_graph("g2") == "mcp_analytics"

    with pytest.raises(ValueError, match="already exists in session"):
        manager.assert_graph_unmapped("g2", "mcp_first")
    manager.assert_graph_unmapped("g2", "mcp_analytics")

    manager.forget_graph("g2")
    manager.assert_graph_unmapped("g2", "mcp_first")


def test_session_for_graph_scans_sessions_for_unmapped_graphs():
    manager = SessionManager()
    session_gds = Mock()
    session_gds.graph.exists.return_value = {"exists": True}
    manager._sessions["mcp_analytics"] = session_gds

    assert manager.session_for_graph("unmapped") == "mcp_analytics"
    assert manager.graph_sessions["unmapped"] == "mcp_analytics"


def test_session_for_graph_returns_none_when_graph_not_found():
    manager = SessionManager()
    session_gds = Mock()
    session_gds.graph.exists.return_value = {"exists": False}
    manager._sessions["mcp_analytics"] = session_gds

    assert manager.session_for_graph("missing") is None


def test_delete_session_purges_session_and_graph_routing():
    class FakeGdsSessions:
        def __init__(self):
            self.deleted = None

        def list(self):
            return []

        def delete(self, session_name):
            self.deleted = session_name
            return True

    manager = SessionManager()
    manager._sessions_client = FakeGdsSessions()
    session_gds = Mock()
    manager._sessions["mcp_analytics"] = session_gds
    manager.record_graph("g", "mcp_analytics")

    result = manager.delete_session("analytics")

    assert result == {"session_name": "mcp_analytics", "deleted": True}
    assert manager._sessions_client.deleted == "mcp_analytics"
    assert "mcp_analytics" not in manager._sessions
    assert manager.graph_sessions == {}
    session_gds.close.assert_called_once()


def test_recreate_session_supports_named_sessions():
    class FakeGds:
        def close(self):
            pass

    class FakeGdsSessions:
        def __init__(self):
            self.deleted = []
            self.created = []

        def list(self):
            return []

        def delete(self, session_name):
            self.deleted.append(session_name)
            return True

        def get_or_create(self, *args, **kwargs):
            self.created.append(kwargs["session_name"])
            return FakeGds()

    fake_sessions = FakeGdsSessions()
    manager = SessionManager()
    manager._sessions_client = fake_sessions
    manager._db_url = "bolt://example"
    manager._auth = ("neo4j", "pw")
    manager._database = None

    manager.recreate_session(session_name="analytics")

    assert fake_sessions.deleted == ["mcp_analytics"]
    assert fake_sessions.created == ["mcp_analytics"]


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
