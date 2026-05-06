from unittest.mock import Mock, MagicMock
from src.mcp_server_neo4j_gds import server as server_module
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
