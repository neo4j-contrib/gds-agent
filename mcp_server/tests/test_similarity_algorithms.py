import re

import pytest


@pytest.mark.asyncio
async def test_node_similarity(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "node_similarity",
        {
            "node_identifier_property": "name",
            "top_n": 35,
            "graph_name": projected_test_graph,
        },
    )

    assert len(result) == 1

    result_text = result[0]["text"]

    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 35
    assert "Aldgate" in data_lines[34]


@pytest.mark.asyncio
async def test_filtered_node_similarity(mcp_client, projected_test_graph):
    # test source-filter only
    result = await mcp_client.call_tool(
        "node_similarity",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "source_node_filter": ["Acton Town"],
            "graph_name": projected_test_graph,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 3
    assert "Acton Town" in data_lines[0]

    # test target-filter alone

    result = await mcp_client.call_tool(
        "node_similarity",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "target_node_filter": "Stamford Brook",
            "graph_name": projected_test_graph,
        },
    )
    assert len(result) == 1
    result_text = result[0]["text"]
    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 4
    assert "Stamford Brook" in data_lines[0]

    # test combination of filters
    result = await mcp_client.call_tool(
        "node_similarity",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "source_node_filter": ["Acton Town"],
            "target_node_filter": ["Stamford Brook"],
            "graph_name": projected_test_graph,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 1
    assert "Acton Town" in data_lines[0]
    assert "Stamford Brook" in data_lines[0]


@pytest.mark.asyncio
async def test_node_similarity_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "node_similarity",
        {
            "graph_name": projected_test_graph,
            "mode": "mutate",
            "mutate_property": "similarity",
            "mutate_relationship_type": "SIMILAR_TO",
            "top_k": 3,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "relationships_written" in result_text

    match = re.search(r"relationships_written=(\d+)", result_text)
    assert match is not None
    relationships_written = int(match.group(1))
    assert relationships_written > 0


@pytest.mark.asyncio
async def test_k_nearest_neighbors(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "k_nearest_neighbors",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "node_properties": {"rail": "DEFAULT"},
            "graph_name": projected_undirected_graph,
        },
    )

    assert len(result) == 1

    result_text = result[0]["text"]

    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 302 * 3


@pytest.mark.asyncio
async def test_filtered_knn(mcp_client, projected_undirected_graph):
    # test source-filter only
    result = await mcp_client.call_tool(
        "k_nearest_neighbors",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "source_node_filter": ["Acton Town"],
            "node_properties": {"rail": "DEFAULT"},
            "graph_name": projected_undirected_graph,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 3
    assert "Acton Town" in data_lines[0]

    # test target-filter alone

    result = await mcp_client.call_tool(
        "k_nearest_neighbors",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "target_node_filter": "Stamford Brook",
            "node_properties": {"rail": "DEFAULT"},
            "graph_name": projected_undirected_graph,
        },
    )
    assert len(result) == 1
    result_text = result[0]["text"]
    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0
    assert "Stamford Brook" in data_lines[0]

    # test combination of filters
    result = await mcp_client.call_tool(
        "k_nearest_neighbors",
        {
            "node_identifier_property": "name",
            "top_k": 3,
            "source_node_filter": ["Acton Town"],
            "target_node_filter": ["Stamford Brook"],
            "seed_target_nodes": True,  # k-nn filtering is a bit special, it might not necessarily find answer if this is not specified (at least for this small example graph)
            "node_properties": {"rail": "DEFAULT"},
            "graph_name": projected_undirected_graph,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    # Verify structure of a result entry
    assert "node1" in result_text
    assert "node2" in result_text
    assert "node1Name" in result_text
    assert "node2Name" in result_text
    assert "similarity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 1
    assert "Acton Town" in data_lines[0]
    assert "Stamford Brook" in data_lines[0]


@pytest.mark.asyncio
async def test_knn_mutate(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "k_nearest_neighbors",
        {
            "graph_name": projected_undirected_graph,
            "mode": "mutate",
            "mutate_property": "knnScore",
            "mutate_relationship_type": "KNN_SIMILAR",
            "top_k": 3,
            "node_properties": {"rail": "DEFAULT"},
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "relationships_written" in result_text

    match = re.search(r"relationships_written=(\d+)", result_text)
    assert match is not None
    relationships_written = int(match.group(1))
    assert relationships_written == 302 * 3
