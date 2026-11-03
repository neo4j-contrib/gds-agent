import re

import pytest


@pytest.mark.asyncio
async def test_node_classification_train_and_predict(mcp_client, projected_test_graph):
    model_name = "test_nc_model"
    try:
        result = await mcp_client.call_tool(
            "train_node_classification_model",
            {
                "graph_name": projected_test_graph,
                "model_name": model_name,
                "target_property": "rail",
                "feature_properties": ["zone", "total_lines"],
                "split_config": {"test_fraction": 0.3, "validation_folds": 2},
                "random_seed": 42,
            },
        )

        assert len(result) == 1
        result_text = result[0]["text"]
        assert model_name in result_text
        assert "trainResult" in result_text
        assert "ACCURACY" in result_text

        stream_result = await mcp_client.call_tool(
            "predict_node_classification",
            {
                "graph_name": projected_test_graph,
                "model_name": model_name,
                "node_identifier_property": "name",
            },
        )
        stream_text = stream_result[0]["text"]
        assert "predictedClass" in stream_text
        assert "nodeName" in stream_text
        lines = stream_text.strip().split("\n")
        data_lines = [line for line in lines[1:] if line.strip()]
        assert len(data_lines) == 302

        mutate_result = await mcp_client.call_tool(
            "predict_node_classification",
            {
                "graph_name": projected_test_graph,
                "model_name": model_name,
                "mode": "mutate",
                "mutate_property": "predicted_rail",
            },
        )
        mutate_text = mutate_result[0]["text"]
        assert "node_properties_written" in mutate_text
        match = re.search(r"node_properties_written=(\d+)", mutate_text)
        assert match is not None
        assert int(match.group(1)) == 302
    finally:
        await mcp_client.call_tool("drop_model", {"model_name": model_name})


@pytest.mark.asyncio
async def test_node_classification_predict_wrong_model_type(
    mcp_client, projected_test_graph
):
    result = await mcp_client.call_tool(
        "predict_node_classification",
        {
            "graph_name": projected_test_graph,
            "model_name": "nonexistent_model",
        },
    )
    assert "Error" in result[0]["text"]


@pytest.mark.asyncio
async def test_link_prediction_train_and_predict(
    mcp_client, projected_undirected_graph
):
    model_name = "test_lp_model"
    try:
        result = await mcp_client.call_tool(
            "train_link_prediction_model",
            {
                "graph_name": projected_undirected_graph,
                "model_name": model_name,
                "target_relationship_type": "LINK",
                "link_features": [
                    {
                        "feature_type": "hadamard",
                        "node_properties": ["latitude", "longitude"],
                    }
                ],
                "split_config": {
                    "train_fraction": 0.4,
                    "test_fraction": 0.3,
                    "validation_folds": 2,
                },
                "random_seed": 42,
            },
        )

        assert len(result) == 1
        result_text = result[0]["text"]
        assert model_name in result_text
        assert "trainResult" in result_text
        assert "AUCPR" in result_text

        stream_result = await mcp_client.call_tool(
            "predict_link_prediction",
            {
                "graph_name": projected_undirected_graph,
                "model_name": model_name,
                "top_n": 5,
                "node_identifier_property": "name",
            },
        )
        stream_text = stream_result[0]["text"]
        assert "probability" in stream_text
        assert "node1Name" in stream_text
        assert "node2Name" in stream_text
        lines = stream_text.strip().split("\n")
        data_lines = [line for line in lines[1:] if line.strip()]
        assert len(data_lines) == 5

        mutate_result = await mcp_client.call_tool(
            "predict_link_prediction",
            {
                "graph_name": projected_undirected_graph,
                "model_name": model_name,
                "mode": "mutate",
                "top_n": 5,
                "mutate_relationship_type": "PREDICTED_LINK",
            },
        )
        mutate_text = mutate_result[0]["text"]
        assert "relationships_written" in mutate_text
        match = re.search(r"relationships_written=(\d+)", mutate_text)
        assert match is not None
        assert int(match.group(1)) > 0
    finally:
        await mcp_client.call_tool("drop_model", {"model_name": model_name})


@pytest.mark.asyncio
async def test_node_regression_train_and_predict(mcp_client, projected_test_graph):
    model_name = "test_nr_model"
    try:
        result = await mcp_client.call_tool(
            "train_node_regression_model",
            {
                "graph_name": projected_test_graph,
                "model_name": model_name,
                "target_property": "zone",
                "feature_properties": ["latitude", "longitude", "total_lines"],
                "split_config": {"test_fraction": 0.3, "validation_folds": 2},
                "model_candidates": [{"method": "linear_regression"}],
                "random_seed": 42,
            },
        )

        assert len(result) == 1
        result_text = result[0]["text"]
        assert model_name in result_text
        assert "trainResult" in result_text
        assert "MEAN_SQUARED_ERROR" in result_text

        stream_result = await mcp_client.call_tool(
            "predict_node_regression",
            {
                "graph_name": projected_test_graph,
                "model_name": model_name,
                "node_identifier_property": "name",
            },
        )
        stream_text = stream_result[0]["text"]
        assert "predictedValue" in stream_text
        assert "nodeName" in stream_text
        lines = stream_text.strip().split("\n")
        data_lines = [line for line in lines[1:] if line.strip()]
        assert len(data_lines) == 302
    finally:
        await mcp_client.call_tool("drop_model", {"model_name": model_name})


@pytest.mark.asyncio
async def test_list_models_empty(mcp_client):
    result = await mcp_client.call_tool("list_models", {})
    assert len(result) == 1
    result_text = result[0]["text"]
    assert "models" in result_text
    assert "count" in result_text
