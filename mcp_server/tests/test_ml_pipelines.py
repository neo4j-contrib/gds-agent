import pytest
import re


@pytest.mark.asyncio
async def test_node_classification_train_and_predict(mcp_client, projected_test_graph):
    model_name = "test_nc_model"
    try:
        result = await mcp_client.call_tool(
            "train_node_classification_model",
            {
                "graphName": projected_test_graph,
                "modelName": model_name,
                "targetProperty": "rail",
                "featureProperties": ["zone", "total_lines"],
                "splitConfig": {"testFraction": 0.3, "validationFolds": 2},
                "randomSeed": 42,
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
                "graphName": projected_test_graph,
                "modelName": model_name,
                "nodeIdentifierProperty": "name",
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
                "graphName": projected_test_graph,
                "modelName": model_name,
                "mode": "mutate",
                "mutateProperty": "predicted_rail",
            },
        )
        mutate_text = mutate_result[0]["text"]
        assert "nodePropertiesWritten" in mutate_text
        match = re.search(r"nodePropertiesWritten\s+(\d+)", mutate_text)
        assert match is not None
        assert int(match.group(1)) == 302
    finally:
        await mcp_client.call_tool("drop_model", {"modelName": model_name})


@pytest.mark.asyncio
async def test_node_classification_predict_wrong_model_type(
    mcp_client, projected_test_graph
):
    result = await mcp_client.call_tool(
        "predict_node_classification",
        {
            "graphName": projected_test_graph,
            "modelName": "nonexistent_model",
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
                "graphName": projected_undirected_graph,
                "modelName": model_name,
                "targetRelationshipType": "LINK",
                "linkFeatures": [
                    {
                        "featureType": "hadamard",
                        "nodeProperties": ["latitude", "longitude"],
                    }
                ],
                "splitConfig": {
                    "trainFraction": 0.4,
                    "testFraction": 0.3,
                    "validationFolds": 2,
                },
                "randomSeed": 42,
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
                "graphName": projected_undirected_graph,
                "modelName": model_name,
                "topN": 5,
                "nodeIdentifierProperty": "name",
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
                "graphName": projected_undirected_graph,
                "modelName": model_name,
                "mode": "mutate",
                "topN": 5,
                "mutateRelationshipType": "PREDICTED_LINK",
            },
        )
        mutate_text = mutate_result[0]["text"]
        assert "relationshipsWritten" in mutate_text
        match = re.search(r"relationshipsWritten\s+(\d+)", mutate_text)
        assert match is not None
        assert int(match.group(1)) > 0
    finally:
        await mcp_client.call_tool("drop_model", {"modelName": model_name})


@pytest.mark.asyncio
async def test_node_regression_train_and_predict(mcp_client, projected_test_graph):
    model_name = "test_nr_model"
    try:
        result = await mcp_client.call_tool(
            "train_node_regression_model",
            {
                "graphName": projected_test_graph,
                "modelName": model_name,
                "targetProperty": "zone",
                "featureProperties": ["latitude", "longitude", "total_lines"],
                "splitConfig": {"testFraction": 0.3, "validationFolds": 2},
                "modelCandidates": [{"method": "linearRegression"}],
                "randomSeed": 42,
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
                "graphName": projected_test_graph,
                "modelName": model_name,
                "nodeIdentifierProperty": "name",
            },
        )
        stream_text = stream_result[0]["text"]
        assert "predictedValue" in stream_text
        assert "nodeName" in stream_text
        lines = stream_text.strip().split("\n")
        data_lines = [line for line in lines[1:] if line.strip()]
        assert len(data_lines) == 302
    finally:
        await mcp_client.call_tool("drop_model", {"modelName": model_name})


@pytest.mark.asyncio
async def test_list_models_empty(mcp_client):
    result = await mcp_client.call_tool("list_models", {})
    assert len(result) == 1
    result_text = result[0]["text"]
    assert "models" in result_text
    assert "count" in result_text
