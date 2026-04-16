import pytest
import re


@pytest.mark.asyncio
async def test_conductance(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "conductance",
        {
            "communityProperty": "total_lines",
            "graphName": projected_undirected_graph,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "community" in result_text
    assert "conductance" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_hdbscan(mcp_client):
    # TODO: Implement test for HDBSCAN. The LN-Underground graph does not have an array node property to use for clustering.
    pass


@pytest.mark.asyncio
async def test_k_core_decomposition(mcp_client, projected_undirected_graph):
    result_with_names = await mcp_client.call_tool(
        "k_core_decomposition",
        {
            "nodeIdentifierProperty": "name",
            "graphName": projected_undirected_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "coreValue" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_k_1_coloring(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "k_1_coloring",
        {
            "nodeIdentifierProperty": "name",
            "maxIterations": 5,
            "graphName": projected_test_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "color" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_k_core_decomposition_mutate(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "k_core_decomposition",
        {
            "graphName": projected_undirected_graph,
            "mode": "mutate",
            "mutateProperty": "kcore",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written > 0


@pytest.mark.asyncio
async def test_k_1_coloring_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "k_1_coloring",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "color",
            "maxIterations": 5,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodeCount" in result_text
    assert "colorCount" in result_text

    match = re.search(r"nodeCount\s+(\d+)", result_text)
    assert match is not None
    nodes_counted = int(match.group(1))
    assert nodes_counted == 302


@pytest.mark.asyncio
async def test_k_means_clustering(mcp_client):
    # TODO: Implement test for K-Means Clustering. The LN-Underground graph does not have an array node property to use for clustering.
    pass


@pytest.mark.asyncio
async def test_label_propagation(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "label_propagation",
        {
            "nodeIdentifierProperty": "name",
            "maxIterations": 10,
            "graphName": projected_test_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "communityId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_leiden(mcp_client, projected_undirected_graph):
    result_with_names = await mcp_client.call_tool(
        "leiden",
        {
            "nodeIdentifierProperty": "name",
            "maxLevels": 10,
            "graphName": projected_undirected_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "communityId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_local_clustering_coefficient(mcp_client, projected_undirected_graph):
    result_filtered = await mcp_client.call_tool(
        "local_clustering_coefficient",
        {
            "nodeIdentifierProperty": "name",
            "nodes": ["Bank"],
            "graphName": projected_undirected_graph,
        },
    )
    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "localClusteringCoefficient" in result_filtered_text
    assert "nodeName" in result_filtered_text
    filtered_lines = result_filtered_text.strip().split("\n")
    filtered_data_lines = [line for line in filtered_lines[1:] if line.strip()]
    assert any("Bank" in line for line in filtered_data_lines)


@pytest.mark.asyncio
async def test_label_propagation_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "label_propagation",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "community",
            "maxIterations": 10,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written == 302


@pytest.mark.asyncio
async def test_leiden_mutate(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "leiden",
        {
            "graphName": projected_undirected_graph,
            "mode": "mutate",
            "mutateProperty": "leidenCommunity",
            "maxLevels": 10,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written > 0


@pytest.mark.asyncio
async def test_local_clustering_coefficient_mutate(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "local_clustering_coefficient",
        {
            "graphName": projected_undirected_graph,
            "mode": "mutate",
            "mutateProperty": "lcc",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written > 0


@pytest.mark.asyncio
async def test_louvain(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "louvain",
        {
            "nodeIdentifierProperty": "name",
            "maxLevels": 10,
            "graphName": projected_test_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "communityId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_louvain_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "louvain",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "louvainCommunity",
            "maxLevels": 10,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written == 302


@pytest.mark.asyncio
async def test_modularity_metric(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "modularity_metric",
        {
            "communityProperty": "total_lines",
            "graphName": projected_undirected_graph,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "communityId" in result_text
    assert "modularity" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0

    for line in data_lines:
        parts = line.split()
        if "communityId" in parts:
            continue
        assert len(parts) >= 3, (
            f"Expected at least 3 columns, got {len(parts)}: {parts}"
        )
        modularity_value = float(parts[2])
        assert isinstance(modularity_value, float), (
            f"Modularity value {modularity_value} is not numeric"
        )


@pytest.mark.asyncio
async def test_modularity_optimization(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "modularity_optimization",
        {
            "nodeIdentifierProperty": "name",
            "maxIterations": 10,
            "graphName": projected_test_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "communityId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_modularity_optimization_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "modularity_optimization",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "modularityCommunity",
            "maxIterations": 10,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodes" in result_text
    assert "communityCount" in result_text

    match = re.search(r"nodes\s+(\d+)", result_text)
    assert match is not None
    nodes_counted = int(match.group(1))
    assert nodes_counted == 302


@pytest.mark.asyncio
async def test_strongly_connected_components(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "strongly_connected_components",
        {"nodeIdentifierProperty": "name", "graphName": projected_test_graph},
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "componentId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_triangle_count(mcp_client, projected_undirected_graph):
    result_filtered = await mcp_client.call_tool(
        "triangle_count",
        {
            "nodeIdentifierProperty": "name",
            "nodes": ["Bank"],
            "graphName": projected_undirected_graph,
        },
    )
    assert len(result_filtered) == 1
    result_filtered_text = result_filtered[0]["text"]
    assert "nodeId" in result_filtered_text
    assert "triangleCount" in result_filtered_text
    assert "nodeName" in result_filtered_text
    filtered_lines = result_filtered_text.strip().split("\n")
    filtered_data_lines = [line for line in filtered_lines[1:] if line.strip()]
    assert any("Bank" in line for line in filtered_data_lines)


@pytest.mark.asyncio
async def test_strongly_connected_components_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "strongly_connected_components",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "sccComponent",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written == 302


@pytest.mark.asyncio
async def test_triangle_count_mutate(mcp_client, projected_undirected_graph):
    result = await mcp_client.call_tool(
        "triangle_count",
        {
            "graphName": projected_undirected_graph,
            "mode": "mutate",
            "mutateProperty": "triangles",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written > 0


@pytest.mark.asyncio
async def test_weakly_connected_components(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "weakly_connected_components",
        {"nodeIdentifierProperty": "name", "graphName": projected_test_graph},
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "componentId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_approximate_maximum_k_cut(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "approximate_maximum_k_cut",
        {"nodeIdentifierProperty": "name", "k": 2, "graphName": projected_test_graph},
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "communityId" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_weakly_connected_components_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "weakly_connected_components",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "wccComponent",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written == 302


@pytest.mark.asyncio
async def test_approximate_maximum_k_cut_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "approximate_maximum_k_cut",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "cutCommunity",
            "k": 2,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written == 302


@pytest.mark.asyncio
async def test_speaker_listener_label_propagation(mcp_client, projected_test_graph):
    result_with_names = await mcp_client.call_tool(
        "speaker_listener_label_propagation",
        {
            "nodeIdentifierProperty": "name",
            "maxIterations": 10,
            "minAssociationStrength": 0.1,
            "graphName": projected_test_graph,
        },
    )

    assert len(result_with_names) == 1
    result_with_names_text = result_with_names[0]["text"]
    assert "nodeId" in result_with_names_text
    assert "values" in result_with_names_text
    assert "nodeName" in result_with_names_text
    lines = result_with_names_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) > 0


@pytest.mark.asyncio
async def test_speaker_listener_label_propagation_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "speaker_listener_label_propagation",
        {
            "graphName": projected_test_graph,
            "mode": "mutate",
            "mutateProperty": "sllpCommunity",
            "maxIterations": 10,
            "minAssociationStrength": 0.1,
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]

    assert "nodePropertiesWritten" in result_text

    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    nodes_written = int(match.group(1))
    assert nodes_written == 302
