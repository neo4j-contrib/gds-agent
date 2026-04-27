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
from .graph_projection_specs import graph_projection_tool_definitions
from .registry import AlgorithmRegistry
from .gds import (
    count_nodes,
    get_node_properties_keys,
    get_relationship_properties_keys,
    get_node_labels,
    get_relationship_types,
    is_session_mode,
)
from .graph_projection_handlers import (
    ProjectGraphCypherHandler,
    DropGraphHandler,
    ListGraphsHandler,
)
from .session_manager import SessionManager, GdsMode

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
            base_gds = GraphDataScience(
                db_url, auth=(username, password), aura_ds=False, database=database
            )
        else:
            base_gds = GraphDataScience(
                db_url, auth=(username, password), aura_ds=False
            )
        logger.info("Successfully connected to Neo4j database")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j database: {e}")
        raise

    session_manager = SessionManager()
    mode = session_manager.detect_mode(base_gds)
    logger.info(f"Detected GDS mode: {mode}")

    def get_gds() -> GraphDataScience:
        if mode == GdsMode.SESSION:
            if session_manager.session_gds is None:
                logger.info("Creating session on first use")
                return session_manager.create_or_get_session(
                    db_url, (username, password), database
                )
            return session_manager.session_gds
        return base_gds

    gds = base_gds

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        try:
            session_tools = []
            if mode == GdsMode.SESSION:
                session_tools = [
                    types.Tool(
                        name="list_sessions",
                        description="""List all GDS sessions""",
                        inputSchema={
                            "type": "object",
                        },
                    ),
                    types.Tool(
                        name="delete_session",
                        description="""Delete a GDS session""",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sessionName": {
                                    "type": "string",
                                    "description": "Name of the session to delete (optional, defaults to current session)",
                                }
                            },
                        },
                    ),
                    types.Tool(
                        name="recreate_session",
                        description="""Recreate the current session with a new memory size (useful for OOM errors)""",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "memoryGB": {
                                    "type": "integer",
                                    "description": "Memory size in GB for the new session",
                                }
                            },
                        },
                    ),
                ]

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
                        },
                    ),
                ]
                + session_tools
                + graph_projection_tool_definitions
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
            active_gds = get_gds()

            if name == "list_sessions":
                result = session_manager.list_sessions()
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "delete_session":
                session_name = arguments.get("sessionName") if arguments else None
                result = session_manager.delete_session(session_name)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "recreate_session":
                memory_gb = arguments.get("memoryGB") if arguments else None
                result = session_manager.recreate_session(memory_gb)
                return [
                    types.TextContent(
                        type="text", text="Session recreated successfully"
                    )
                ]

            elif name == "count_nodes":
                result = count_nodes(active_gds)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "get_node_properties_keys":
                result = get_node_properties_keys(active_gds)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "get_relationship_properties_keys":
                result = get_relationship_properties_keys(active_gds)
                return [types.TextContent(type="text", text=serialize_result(result))]
            elif name == "get_node_labels":
                result = get_node_labels(active_gds)
                return [types.TextContent(type="text", text=serialize_result(result))]
            elif name == "get_relationship_types":
                result = get_relationship_types(active_gds)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "project_graph_cypher":
                handler = ProjectGraphCypherHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "drop_graph":
                handler = DropGraphHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "list_graphs":
                handler = ListGraphsHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            else:
                handler = AlgorithmRegistry.get_handler(name, active_gds)
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
                    server_version="0.5.1",
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
            session_manager.close()
            base_gds.close()


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
