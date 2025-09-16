# server.py
import contextlib
import logging
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from typing import Any
import mcp.server.stdio
import pandas as pd
import json
from graphdatascience import GraphDataScience

from .similarity_algorithm_specs import similarity_tool_definitions
from .centrality_algorithm_specs import centrality_tool_definitions
from .community_algorithm_specs import community_tool_definitions
from .path_algorithm_specs import path_tool_definitions
from .registry import AlgorithmRegistry
from .gds import (
    count_nodes,
    get_node_properties_keys,
    get_relationship_properties_keys,
    get_node_labels,
    get_relationship_types,
)

logger = logging.getLogger("mcp_server_neo4j_gds")


def serialize_result(result: Any) -> str:
    """Serialize results to string without truncation, handling DataFrames specially"""
    if isinstance(result, pd.DataFrame):
        # Configure pandas to show all rows and columns
        with pd.option_context(
            "display.max_rows",
            None,
            "display.max_columns",
            None,
            "display.width",
            None,
            "display.max_colwidth",
            None,
        ):
            return result.to_string(index=True)
    elif isinstance(result, (list, dict)):
        # Use JSON for better formatting of complex data structures
        return json.dumps(result, indent=2, default=str)
    else:
        # For other types, use string conversion
        return str(result)


async def main(db_url: str, username: str, password: str, database: str = None):
    logger.info(f"Starting MCP Server for {db_url} with username {username}")
    if database:
        logger.info(f"Connecting to database: {database}")

    server = Server("gds-agent")

    # Create GraphDataScience object with optional database parameter
    try:
        if database:
            gds = GraphDataScience(
                db_url, auth=(username, password), aura_ds=False, database=database
            )
        else:
            gds = GraphDataScience(db_url, auth=(username, password), aura_ds=False)
        logger.info("Successfully connected to Neo4j database")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j database: {e}")
        raise

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        try:
            tools = (
                [
                    types.Tool(
                        name="count_nodes",
                        description="""Count the number of nodes in the graph""",
                        inputSchema={
                            "type": "object",
                        },
                    ),
                    types.Tool(
                        name="get_node_properties_keys",
                        description="""Get all node properties keys in the database""",
                        inputSchema={
                            "type": "object",
                        },
                    ),
                    types.Tool(
                        name="get_relationship_properties_keys",
                        description="""Get all relationship properties keys in the database""",
                        inputSchema={
                            "type": "object",
                        },
                    ),
                    types.Tool(
                        name="get_node_labels",
                        description="""Get all node labels in the database""",
                        inputSchema={
                            "type": "object",
                        },
                    ),
                    types.Tool(
                        name="get_relationship_types",
                        description="""Get relationship types in the database.""",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "nodeLabels": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Ignore relationships whose source and target node is not in the specified node labels. To use this parameter, use get_node_labels first.",
                                },
                            },
                            "required": [],
                        },
                    ),
                ]
                + centrality_tool_definitions
                + community_tool_definitions
                + path_tool_definitions
                + similarity_tool_definitions
            )
            logger.info(f"Returning {len(tools)} tools")
            return tools
        except Exception as e:
            logger.error(f"Error in handle_list_tools: {e}")
            raise

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "count_nodes":
                result = count_nodes(gds)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "get_node_properties_keys":
                result = get_node_properties_keys(gds)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "get_relationship_properties_keys":
                result = get_relationship_properties_keys(gds)
                return [types.TextContent(type="text", text=serialize_result(result))]
            elif name == "get_node_labels":
                result = get_node_labels(gds)
                return [types.TextContent(type="text", text=serialize_result(result))]
            elif name == "get_relationship_types":
                if "nodeLabels" in arguments:
                    result = get_relationship_types(gds, arguments["nodeLabels"])
                else:
                    result = get_relationship_types(gds)
                return [types.TextContent(type="text", text=serialize_result(result))]

            else:
                handler = AlgorithmRegistry.get_handler(name, gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="neo4j_gds",
                    server_version="0.4.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
                raise_exceptions=False,
            )
    except Exception as e:
        # Log shutdown info - connection errors are expected, others may need attention
        if isinstance(e, (BrokenPipeError, ConnectionResetError, OSError)):
            logger.info("Server shutdown (client disconnected)")
        else:
            logger.info(f"Server shutdown with error: {e}")
    finally:
        with contextlib.suppress(Exception):
            gds.close()


if __name__ == "__main__":
    import sys
    import asyncio

    if len(sys.argv) < 4:
        print(
            "Usage: python -m mcp_server_neo4j_gds.server <db_url> <username> <password> [database]"
        )
        sys.exit(1)

    db_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    database = sys.argv[4] if len(sys.argv) > 4 else None

    asyncio.run(main(db_url, username, password, database))
