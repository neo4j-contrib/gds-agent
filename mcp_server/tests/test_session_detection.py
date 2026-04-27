import pytest
from unittest.mock import Mock, MagicMock
from src.mcp_server_neo4j_gds.session_manager import SessionManager, GdsMode
from src.mcp_server_neo4j_gds.gds import is_session_mode


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


def test_is_session_mode_returns_false_for_plugin():
    mock_gds = Mock()
    mock_gds.run_cypher.side_effect = Exception("There is no procedure with the name")

    result = is_session_mode(mock_gds)

    assert result is False


def test_is_session_mode_returns_true_for_session():
    mock_gds = Mock()
    mock_gds.run_cypher.return_value = MagicMock()

    result = is_session_mode(mock_gds)

    assert result is True


def test_mode_cached_after_first_detection():
    mock_gds = Mock()
    mock_gds.run_cypher.return_value = MagicMock()

    session_manager = SessionManager()
    mode1 = session_manager.detect_mode(mock_gds)
    mode2 = session_manager.detect_mode(mock_gds)

    assert mode1 == mode2 == GdsMode.SESSION
    assert mock_gds.run_cypher.call_count == 1
