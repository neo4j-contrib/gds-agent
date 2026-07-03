from mcp import types

DESTRUCTIVE_TOOLS = {"drop_graph", "drop_model", "delete_session"}
CATALOG_WRITE_TOOLS = {
    "project_graph_cypher",
    "create_session",
    "graph_sage_train",
    "train_node_classification_model",
    "train_link_prediction_model",
    "train_node_regression_model",
}
MUTATE_PARAMS = {"mode", "mutateProperty", "mutateRelationshipType"}


def annotations_for(tool: types.Tool) -> types.ToolAnnotations:
    # No tool ever writes to the Neo4j database; hints describe the in-memory
    # graph/session/model catalogs.
    if tool.name in DESTRUCTIVE_TOOLS:
        return types.ToolAnnotations(readOnlyHint=False, destructiveHint=True)
    params = set(tool.inputSchema.get("properties", {}))
    if tool.name in CATALOG_WRITE_TOOLS or params & MUTATE_PARAMS:
        return types.ToolAnnotations(readOnlyHint=False, destructiveHint=False)
    return types.ToolAnnotations(readOnlyHint=True)


def apply_tool_annotations(tools: list[types.Tool]) -> list[types.Tool]:
    for tool in tools:
        if tool.annotations is None:
            tool.annotations = annotations_for(tool)
    return tools
