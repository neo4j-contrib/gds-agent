import pytest


@pytest.mark.asyncio
async def test_project_and_drop_graph(mcp_client):
    """Test creating and dropping a graph projection."""
    # Project a graph
    result = await mcp_client.call_tool(
        "project_graph_cypher",
        {
            "graphName": "test_projection",
            "cypherQuery": """
                MATCH (n:UndergroundStation)-[r:LINK]->(m:UndergroundStation)
                RETURN gds.graph.project(
                    $graph_name,
                    n,
                    m,
                    {
                        sourceNodeLabels: labels(n),
                        targetNodeLabels: labels(m),
                        relationshipType: type(r)
                    }
                )
            """,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    print(f"Projection result: {result_text}")
    assert "test_projection" in result_text or "graphName" in result_text

    # List graphs to verify it was created
    list_result = await mcp_client.call_tool("list_graphs", {})
    assert len(list_result) == 1
    list_text = list_result[0]["text"]
    print(f"List graphs result: {list_text}")
    assert "test_projection" in list_text

    # Drop the graph
    drop_result = await mcp_client.call_tool(
        "drop_graph", {"graphName": "test_projection"}
    )
    assert len(drop_result) == 1
    drop_text = drop_result[0]["text"]
    print(f"Drop result: {drop_text}")
    assert "test_projection" in drop_text


@pytest.mark.asyncio
async def test_projected_test_graph_fixture(mcp_client, projected_test_graph):
    """Test that the projected_test_graph fixture works."""
    # List graphs to verify the fixture created a graph
    list_result = await mcp_client.call_tool("list_graphs", {})
    assert len(list_result) == 1
    list_text = list_result[0]["text"]
    print(f"List graphs result: {list_text}")
    print(f"projected_test_graph name: {projected_test_graph}")
    assert projected_test_graph in list_text

    # Run a simple algorithm on it
    result = await mcp_client.call_tool(
        "pagerank",
        {
            "graphName": projected_test_graph,
            "nodeIdentifierProperty": "name",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    print(f"PageRank result (first 500 chars): {result_text[:500]}")
    assert "nodeId" in result_text or "nodeName" in result_text
