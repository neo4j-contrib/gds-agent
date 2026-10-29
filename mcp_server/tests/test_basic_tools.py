import json

import pytest


@pytest.mark.asyncio
async def test_list_tools(mcp_client):
    """Test that all expected tools are listed."""

    # Get list of available tools
    tools = await mcp_client.list_tools()
    tool_names = [tool["name"] for tool in tools]

    # Expected tools (based on server.py imports)
    expected_tools = [
        # Basic tools
        "get_node_properties_keys",
        "get_relationship_properties_keys",
        "get_node_labels",
        "get_relationship_types",
        "read_neo4j_cypher",
        "write_neo4j_cypher",
        "get_neo4j_schema",
        # Graph projection tools
        "project_graph_cypher",
        "drop_graph",
        "list_graphs",
        "get_graph_info",
        "stream_node_properties",
        "stream_relationship_properties",
        "stream_relationships",
        # Centrality algorithms
        "article_rank",
        "articulation_points",
        "betweenness_centrality",
        "bridges",
        "CELF",
        "closeness_centrality",
        "degree_centrality",
        "eigenvector_centrality",
        "pagerank",
        "harmonic_centrality",
        "HITS",
        # Community algorithms
        "conductance",
        "HDBSCAN",
        "k_core_decomposition",
        "k_1_coloring",
        "k_means_clustering",
        "label_propagation",
        "leiden",
        "local_clustering_coefficient",
        "louvain",
        "modularity_metric",
        "modularity_optimization",
        "strongly_connected_components",
        "triangle_count",
        "weakly_connected_components",
        "approximate_maximum_k_cut",
        "speaker_listener_label_propagation",
        # Path algorithms
        "find_shortest_path",
        "delta_stepping_shortest_path",
        "dijkstra_single_source_shortest_path",
        "a_star_shortest_path",
        "yens_shortest_paths",
        "minimum_weight_spanning_tree",
        "minimum_directed_steiner_tree",
        "prize_collecting_steiner_tree",
        "all_pairs_shortest_paths",
        "random_walk",
        "breadth_first_search",
        "depth_first_search",
        "bellman_ford_single_source_shortest_path",
        "longest_path",
        "max_flow",
        # similarity
        "node_similarity",
        "k_nearest_neighbors",
        # Node embedding algorithms
        "fast_rp",
        "node2vec",
        "hashgnn",
        "graph_sage_train",
        "graph_sage_predict",
        # ML pipelines and model catalog
        "train_node_classification_model",
        "predict_node_classification",
        "train_link_prediction_model",
        "predict_link_prediction",
        "train_node_regression_model",
        "predict_node_regression",
        "list_models",
        "drop_model",
    ]

    # Check that we have the expected tools
    assert len(tool_names) == len(expected_tools)
    for expected_tool in expected_tools:
        assert expected_tool in tool_names, (
            f"Expected tool '{expected_tool}' not found in tool list"
        )


@pytest.mark.asyncio
async def test_get_node_properties_keys(mcp_client):
    result = await mcp_client.call_tool("get_node_properties_keys")

    assert len(result) == 1
    result_text = result[0]["text"]
    properties_keys = json.loads(result_text)

    assert properties_keys == [
        "zone",
        "rail",
        "latitude",
        "name",
        "total_lines",
        "id",
        "display_name",
        "longitude",
    ]


@pytest.mark.asyncio
async def test_get_relationship_properties_keys(mcp_client):
    result = await mcp_client.call_tool("get_relationship_properties_keys")

    assert len(result) == 1
    result_text = result[0]["text"]
    properties_keys = json.loads(result_text)

    assert properties_keys == ["distance", "line", "time"]


@pytest.mark.asyncio
async def test_get_node_labels(mcp_client):
    result = await mcp_client.call_tool("get_node_labels")

    assert len(result) == 1
    result_text = result[0]["text"]
    properties_keys = json.loads(result_text)

    assert properties_keys == ["UndergroundStation"]


@pytest.mark.asyncio
async def test_get_relationship_types(mcp_client):
    result = await mcp_client.call_tool("get_relationship_types")

    assert len(result) == 1
    result_text = result[0]["text"]
    properties_keys = json.loads(result_text)

    assert properties_keys == ["LINK"]


@pytest.mark.asyncio
async def test_read_neo4j_cypher(mcp_client):
    result = await mcp_client.call_tool(
        "read_neo4j_cypher",
        {
            "query": "MATCH (n:UndergroundStation {name: $name}) RETURN n.name AS name",
            "params": {"name": "Baker Street"},
        },
    )

    assert len(result) == 1
    assert json.loads(result[0]["text"]) == [{"name": "Baker Street"}]


@pytest.mark.asyncio
async def test_read_neo4j_cypher_rejects_writes(mcp_client):
    result = await mcp_client.call_tool(
        "read_neo4j_cypher",
        {
            "query": "CREATE (n:ReadCypherGuard) RETURN n",
        },
    )

    assert len(result) == 1
    check = await mcp_client.call_tool(
        "read_neo4j_cypher",
        {"query": "MATCH (n:ReadCypherGuard) RETURN count(n) AS count"},
    )
    assert json.loads(check[0]["text"]) == [{"count": 0}]


@pytest.mark.asyncio
async def test_write_neo4j_cypher(mcp_client):
    created = await mcp_client.call_tool(
        "write_neo4j_cypher",
        {
            "query": "CREATE (n:WriteCypherGuard {name: $name}) RETURN n.name AS name",
            "params": {"name": "temp"},
        },
    )
    try:
        assert json.loads(created[0]["text"])["nodes_created"] == 1
    finally:
        await mcp_client.call_tool(
            "write_neo4j_cypher",
            {"query": "MATCH (n:WriteCypherGuard {name: 'temp'}) DELETE n"},
        )


@pytest.mark.asyncio
async def test_write_neo4j_cypher_rejects_reads(mcp_client):
    result = await mcp_client.call_tool(
        "write_neo4j_cypher",
        {"query": "MATCH (n:UndergroundStation) RETURN n.name AS name LIMIT 1"},
    )

    assert len(result) == 1
    assert "Only write queries are allowed for write-query" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_neo4j_schema(mcp_client):
    result = await mcp_client.call_tool("get_neo4j_schema")

    assert len(result) == 1
    schema = json.loads(result[0]["text"])
    station = schema["UndergroundStation"]
    assert station["type"] == "node"
    assert "name" in station["properties"]
    assert "UndergroundStation" in station["relationships"]["LINK"]["labels"]
