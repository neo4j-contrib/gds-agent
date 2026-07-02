"""
Live integration test for GDS Aura Graph Analytics session mode.

Skipped automatically unless all of these env vars are set:
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    AURA_API_CLIENT_ID, AURA_API_CLIENT_SECRET
Optional: NEO4J_DATABASE, AURA_API_PROJECT_ID.

For local runs, put creds in a .env file at the repo root (already
gitignored) and source it (or use direnv), then:
    cd mcp_server
    uv run pytest tests/test_aura_integration.py -v -s

What this verifies end-to-end against a real AuraDB:
    - SessionManager detects SESSION mode
    - Session creation via the Aura sessions API
    - Session listing
    - Remote graph projection via the Python client
    - Remote graph projection via ProjectGraphCypherHandler (MCP tool path)
    - Algorithm execution (PageRank.stream)
    - Session deletion (teardown)

The AuraDB instance must contain at least one node with one relationship.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from mcp_server_neo4j_gds.graph_projection_handlers import ProjectGraphCypherHandler
from mcp_server_neo4j_gds.server import create_base_gds
from mcp_server_neo4j_gds.session_manager import GdsMode, SessionManager

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REQUIRED_ENV = [
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
    "AURA_API_CLIENT_ID",
    "AURA_API_CLIENT_SECRET",
]

pytestmark = pytest.mark.skipif(
    not all(os.getenv(v) for v in REQUIRED_ENV),
    reason=f"Aura credentials not set; required: {', '.join(REQUIRED_ENV)}",
)


@pytest.fixture
def base_gds():
    gds = create_base_gds(
        os.environ["NEO4J_URI"],
        os.environ["NEO4J_USERNAME"],
        os.environ["NEO4J_PASSWORD"],
        database=os.getenv("NEO4J_DATABASE"),
    )
    yield gds
    gds.close()


@pytest.fixture
def session_manager():
    sm = SessionManager()
    yield sm
    for name, _ in sm.active_sessions():
        try:
            sm.delete_session(name)
        except Exception:
            pass
    sm.close()


def test_aura_session_full_cycle(base_gds, session_manager):
    assert session_manager.detect_mode(base_gds) == GdsMode.SESSION

    session_name = "mcp_integration_test_session"
    session_gds = session_manager.create_or_get_session(
        os.environ["NEO4J_URI"],
        (os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        os.getenv("NEO4J_DATABASE"),
        session_name=session_name,
    )
    assert session_manager.get_session(session_name) is session_gds

    listing = session_manager.list_sessions()
    assert any(s["name"] == session_name for s in listing["sessions"])

    cypher = """
        MATCH (n)-[r]->(m)
        WITH n, r, m
        LIMIT 1000
        RETURN gds.graph.project.remote(
            n, m,
            {
                sourceNodeLabels: labels(n),
                targetNodeLabels: labels(m),
                relationshipType: type(r)
            }
        )
    """

    G, _ = session_gds.graph.project("integration_direct_graph", cypher)
    try:
        assert G.node_count() > 0
        result = session_gds.pageRank.stream(G)
        assert len(result) > 0
    finally:
        session_gds.graph.drop("integration_direct_graph")

    handler = ProjectGraphCypherHandler(session_gds)
    handler_result = handler.project_graph_cypher("integration_test_graph", cypher)
    try:
        assert handler_result["nodeCount"] > 0
    finally:
        session_gds.graph.drop("integration_test_graph")
