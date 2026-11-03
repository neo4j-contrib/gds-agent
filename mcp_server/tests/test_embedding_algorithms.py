import re

import pytest


@pytest.mark.asyncio
async def test_fast_rp_stream(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "fast_rp",
        {
            "graph_name": projected_test_graph,
            "embedding_dimension": 32,
            "random_seed": 42,
            "node_identifier_property": "name",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "nodeId" in result_text
    assert "embedding" in result_text
    assert "nodeName" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 302


@pytest.mark.asyncio
async def test_fast_rp_mutate(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "fast_rp",
        {
            "graph_name": projected_test_graph,
            "embedding_dimension": 32,
            "random_seed": 42,
            "mode": "mutate",
            "mutate_property": "fastrp_embedding",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "node_properties_written" in result_text
    match = re.search(r"node_properties_written=(\d+)", result_text)
    assert match is not None
    assert int(match.group(1)) == 302

    stream_result = await mcp_client.call_tool(
        "stream_node_properties",
        {
            "graph_name": projected_test_graph,
            "node_properties": "fastrp_embedding",
        },
    )
    assert "fastrp_embedding" in stream_result[0]["text"]


@pytest.mark.asyncio
async def test_node2vec_stream(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "node2vec",
        {
            "graph_name": projected_test_graph,
            "embedding_dimension": 16,
            "walk_length": 10,
            "walks_per_node": 2,
            "iterations": 1,
            "random_seed": 42,
            "node_identifier_property": "name",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "embedding" in result_text
    assert "nodeName" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 302


@pytest.mark.asyncio
async def test_hashgnn_stream(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "hashgnn",
        {
            "graph_name": projected_test_graph,
            "iterations": 2,
            "embedding_density": 4,
            "generate_features": {"dimension": 16, "density_level": 2},
            "random_seed": 42,
            "node_identifier_property": "name",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "embedding" in result_text
    assert "nodeName" in result_text
    lines = result_text.strip().split("\n")
    data_lines = [line for line in lines[1:] if line.strip()]
    assert len(data_lines) == 302


@pytest.mark.asyncio
async def test_graph_sage_train_and_predict(mcp_client, projected_undirected_graph):
    model_name = "test_graphsage_model"
    try:
        result = await mcp_client.call_tool(
            "graph_sage_train",
            {
                "graph_name": projected_undirected_graph,
                "model_name": model_name,
                "feature_properties": ["zone", "latitude", "longitude"],
                "embedding_dimension": 16,
                "sample_sizes": [5, 3],
                "epochs": 1,
                "max_iterations": 2,
                "batch_size": 100,
                "random_seed": 42,
            },
        )

        assert len(result) == 1
        result_text = result[0]["text"]
        assert model_name in result_text
        assert "trainResult" in result_text

        list_result = await mcp_client.call_tool("list_models", {})
        assert model_name in list_result[0]["text"]

        stream_result = await mcp_client.call_tool(
            "graph_sage_predict",
            {
                "graph_name": projected_undirected_graph,
                "model_name": model_name,
                "node_identifier_property": "name",
            },
        )
        stream_text = stream_result[0]["text"]
        assert "embedding" in stream_text
        assert "nodeName" in stream_text

        mutate_result = await mcp_client.call_tool(
            "graph_sage_predict",
            {
                "graph_name": projected_undirected_graph,
                "model_name": model_name,
                "mode": "mutate",
                "mutate_property": "sage_embedding",
            },
        )
        mutate_text = mutate_result[0]["text"]
        assert "node_properties_written" in mutate_text
        match = re.search(r"node_properties_written=(\d+)", mutate_text)
        assert match is not None
        assert int(match.group(1)) == 302
    finally:
        drop_result = await mcp_client.call_tool(
            "drop_model", {"model_name": model_name}
        )
        assert "dropped" in drop_result[0]["text"]
