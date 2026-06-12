import pytest
import re


@pytest.mark.asyncio
async def test_fast_rp_stream(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "fast_rp",
        {
            "graphName": projected_test_graph,
            "embeddingDimension": 32,
            "randomSeed": 42,
            "nodeIdentifierProperty": "name",
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
            "graphName": projected_test_graph,
            "embeddingDimension": 32,
            "randomSeed": 42,
            "mode": "mutate",
            "mutateProperty": "fastrp_embedding",
        },
    )

    assert len(result) == 1
    result_text = result[0]["text"]
    assert "nodePropertiesWritten" in result_text
    match = re.search(r"nodePropertiesWritten\s+(\d+)", result_text)
    assert match is not None
    assert int(match.group(1)) == 302

    stream_result = await mcp_client.call_tool(
        "stream_node_properties",
        {
            "graphName": projected_test_graph,
            "nodeProperties": "fastrp_embedding",
        },
    )
    assert "fastrp_embedding" in stream_result[0]["text"]


@pytest.mark.asyncio
async def test_node2vec_stream(mcp_client, projected_test_graph):
    result = await mcp_client.call_tool(
        "node2vec",
        {
            "graphName": projected_test_graph,
            "embeddingDimension": 16,
            "walkLength": 10,
            "walksPerNode": 2,
            "iterations": 1,
            "randomSeed": 42,
            "nodeIdentifierProperty": "name",
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
            "graphName": projected_test_graph,
            "iterations": 2,
            "embeddingDensity": 4,
            "generateFeatures": {"dimension": 16, "densityLevel": 2},
            "randomSeed": 42,
            "nodeIdentifierProperty": "name",
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
                "graphName": projected_undirected_graph,
                "modelName": model_name,
                "featureProperties": ["zone", "latitude", "longitude"],
                "embeddingDimension": 16,
                "sampleSizes": [5, 3],
                "epochs": 1,
                "maxIterations": 2,
                "batchSize": 100,
                "randomSeed": 42,
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
                "graphName": projected_undirected_graph,
                "modelName": model_name,
                "nodeIdentifierProperty": "name",
            },
        )
        stream_text = stream_result[0]["text"]
        assert "embedding" in stream_text
        assert "nodeName" in stream_text

        mutate_result = await mcp_client.call_tool(
            "graph_sage_predict",
            {
                "graphName": projected_undirected_graph,
                "modelName": model_name,
                "mode": "mutate",
                "mutateProperty": "sage_embedding",
            },
        )
        mutate_text = mutate_result[0]["text"]
        assert "nodePropertiesWritten" in mutate_text
        match = re.search(r"nodePropertiesWritten\s+(\d+)", mutate_text)
        assert match is not None
        assert int(match.group(1)) == 302
    finally:
        drop_result = await mcp_client.call_tool(
            "drop_model", {"modelName": model_name}
        )
        assert "dropped" in drop_result[0]["text"]
