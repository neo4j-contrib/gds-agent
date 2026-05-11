import pytest
from mcp.server import Server
from starlette.testclient import TestClient

from mcp_server_neo4j_gds import server as server_module


def test_normalize_transport_accepts_http_aliases():
    assert server_module.normalize_transport("stdio") == "stdio"
    assert server_module.normalize_transport("http") == "streamable-http"
    assert server_module.normalize_transport("streamable-http") == "streamable-http"


def test_normalize_transport_rejects_unsupported_transport():
    with pytest.raises(ValueError, match="Unsupported transport"):
        server_module.normalize_transport("sse")


def test_streamable_http_app_mounts_normalized_path():
    app = server_module.create_streamable_http_app(
        Server("test", version="1"), "api/mcp"
    )

    assert [route.path for route in app.routes] == ["/api/mcp"]


def test_streamable_http_app_handles_initialize_request():
    app = server_module.create_streamable_http_app(Server("test", version="1"), "/mcp")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1"},
        },
    }

    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            json=request,
            headers={
                "content-type": "application/json",
                "accept": "application/json, text/event-stream",
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    assert response.headers["mcp-session-id"]
    assert '"serverInfo":{"name":"test","version":"1"}' in response.text


@pytest.mark.asyncio
async def test_main_dispatches_http_transport_and_closes_resources(monkeypatch):
    fake_server = Server("test", version="1")
    calls = {}

    class Closable:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_session_manager = Closable()
    fake_base_gds = Closable()

    def fake_create_mcp_server(db_url, username, password, database):
        calls["create"] = (db_url, username, password, database)
        return fake_server, fake_session_manager, fake_base_gds

    async def fake_run_streamable_http_server(server, host, port, path):
        calls["http"] = (server, host, port, path)

    async def fake_run_stdio_server(server):
        calls["stdio"] = server

    monkeypatch.setattr(server_module, "create_mcp_server", fake_create_mcp_server)
    monkeypatch.setattr(
        server_module, "run_streamable_http_server", fake_run_streamable_http_server
    )
    monkeypatch.setattr(server_module, "run_stdio_server", fake_run_stdio_server)

    await server_module.main(
        "bolt://example",
        "neo4j",
        "password",
        transport="http",
        host="0.0.0.0",
        port=9000,
        path="mcp",
    )

    assert calls["create"] == ("bolt://example", "neo4j", "password", None)
    assert calls["http"] == (fake_server, "0.0.0.0", 9000, "mcp")
    assert "stdio" not in calls
    assert fake_session_manager.closed
    assert fake_base_gds.closed


@pytest.mark.asyncio
async def test_main_defaults_to_stdio_transport(monkeypatch):
    fake_server = Server("test", version="1")
    calls = {}

    class Closable:
        def close(self):
            calls["closed"] = calls.get("closed", 0) + 1

    def fake_create_mcp_server(db_url, username, password, database):
        return fake_server, Closable(), Closable()

    async def fake_run_streamable_http_server(server, host, port, path):
        calls["http"] = (server, host, port, path)

    async def fake_run_stdio_server(server):
        calls["stdio"] = server

    monkeypatch.setattr(server_module, "create_mcp_server", fake_create_mcp_server)
    monkeypatch.setattr(
        server_module, "run_streamable_http_server", fake_run_streamable_http_server
    )
    monkeypatch.setattr(server_module, "run_stdio_server", fake_run_stdio_server)

    await server_module.main("bolt://example", "neo4j", "password")

    assert calls["stdio"] is fake_server
    assert "http" not in calls
    assert calls["closed"] == 2
