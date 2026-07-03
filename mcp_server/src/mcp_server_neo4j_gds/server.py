# server.py
import asyncio
import contextlib
import logging
from importlib.metadata import PackageNotFoundError, version
from anyio import BrokenResourceError
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
import mcp.types as types
from typing import Any
import mcp.server.stdio
import pandas as pd
import json
from graphdatascience import GraphDataScience
from neo4j import GraphDatabase

from .similarity_algorithm_specs import similarity_tool_definitions
from .centrality_algorithm_specs import centrality_tool_definitions
from .community_algorithm_specs import community_tool_definitions
from .path_algorithm_specs import path_tool_definitions
from .graph_projection_specs import graph_projection_tool_definitions
from .embedding_algorithm_specs import embedding_tool_definitions
from .ml_pipeline_specs import ml_pipeline_tool_definitions
from .registry import AlgorithmRegistry
from .gds import (
    count_nodes,
    get_node_properties_keys,
    get_relationship_properties_keys,
    get_node_labels,
    get_relationship_types,
)
from .graph_projection_handlers import (
    ProjectGraphCypherHandler,
    DropGraphHandler,
    ListGraphsHandler,
    GraphInfoHandler,
    StreamNodePropertiesHandler,
    StreamRelationshipPropertiesHandler,
    StreamRelationshipsHandler,
)
from .ml_pipeline_handlers import ListModelsHandler, DropModelHandler
from .instructions import SERVER_INSTRUCTIONS
from .session_manager import SessionManager, GdsMode, ensure_mcp_session_name
from .tool_annotations import apply_tool_annotations
from .result_limits import (
    dataframe_limit_warning,
    limit_dataframe_rows,
    limit_text,
    max_cell_chars,
)

logger = logging.getLogger("mcp_server_neo4j_gds")
SERVER_NAME = "neo4j_gds"
try:
    SERVER_VERSION = version("gds-agent")
except PackageNotFoundError:
    SERVER_VERSION = "0.0.0"
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_PATH = "/mcp"
STDIO_TRANSPORT = "stdio"
HTTP_TRANSPORT = "streamable-http"
TRANSPORT_ALIASES = {
    STDIO_TRANSPORT: STDIO_TRANSPORT,
    "http": HTTP_TRANSPORT,
    HTTP_TRANSPORT: HTTP_TRANSPORT,
}


class Neo4jDriverConnection:
    def __init__(self, db_url: str, username: str, password: str, database: str = None):
        self._driver = GraphDatabase.driver(db_url, auth=(username, password))
        self._database = database

    def run_cypher(
        self, query: str, params: dict[str, Any] = None, database: str = None
    ) -> pd.DataFrame:
        with self._driver.session(database=database or self._database) as session:
            result = session.run(query, params or {})
            keys = result.keys()
            return pd.DataFrame([record.data() for record in result], columns=keys)

    def close(self):
        self._driver.close()


def is_aura_graph_analytics_versionless_error(error: Exception) -> bool:
    return "Aura Graph Analytics is versionless" in str(error)


def create_base_gds(db_url: str, username: str, password: str, database: str = None):
    try:
        if database:
            return GraphDataScience(
                db_url, auth=(username, password), aura_ds=False, database=database
            )
        return GraphDataScience(db_url, auth=(username, password), aura_ds=False)
    except Exception as e:
        if is_aura_graph_analytics_versionless_error(e):
            logger.info(
                "Using Neo4j driver connection for Aura Graph Analytics session detection"
            )
            return Neo4jDriverConnection(db_url, username, password, database)
        logger.error(f"Failed to connect to Neo4j database: {e}")
        raise


def serialize_result(result: Any) -> str:
    """Serialize results to string without truncation, handling DataFrames specially"""
    if isinstance(result, pd.DataFrame):
        result = limit_dataframe_rows(result)
        warning = dataframe_limit_warning(result)
        with pd.option_context(
            "display.max_rows",
            None,
            "display.max_columns",
            None,
            "display.width",
            None,
            "display.max_colwidth",
            max_cell_chars(),
        ):
            text = result.to_string(index=True)
        if warning:
            text = f"{warning}\n\n{text}"
        return limit_text(text)
    elif isinstance(result, (list, dict)):
        # Use JSON for better formatting of complex data structures
        return limit_text(json.dumps(result, indent=2, default=str))
    else:
        # For other types, use string conversion
        return limit_text(str(result))


def normalize_transport(transport: str) -> str:
    normalized_transport = (transport or STDIO_TRANSPORT).strip().lower()
    if normalized_transport not in TRANSPORT_ALIASES:
        supported = ", ".join(sorted(TRANSPORT_ALIASES))
        raise ValueError(
            f"Unsupported transport '{transport}'. Supported transports: {supported}"
        )
    return TRANSPORT_ALIASES[normalized_transport]


def normalize_http_path(path: str) -> str:
    if not path:
        return DEFAULT_HTTP_PATH
    if path.startswith("/"):
        return path
    return f"/{path}"


def create_mcp_server(
    db_url: str, username: str, password: str, database: str = None
) -> tuple[Server, SessionManager, GraphDataScience | Neo4jDriverConnection]:
    logger.info(f"Starting MCP Server for {db_url} with username {username}")
    if database:
        logger.info(f"Connecting to database: {database}")

    server = Server(
        SERVER_NAME, version=SERVER_VERSION, instructions=SERVER_INSTRUCTIONS
    )

    # Create GraphDataScience object with optional database parameter
    base_gds = create_base_gds(db_url, username, password, database)
    logger.info("Successfully connected to Neo4j database")

    session_manager = SessionManager()
    mode = session_manager.detect_mode(base_gds)
    logger.info(f"Detected GDS mode: {mode}")

    def get_gds_for_graph(graph_name: str = None) -> GraphDataScience:
        # Tools without a graphName only query the database and run on the base connection
        if mode != GdsMode.SESSION or not graph_name:
            return base_gds
        session_name = session_manager.session_for_graph(graph_name)
        if session_name is None:
            raise ValueError(
                f"Graph '{graph_name}' was not found in any active session. "
                "Create a session with create_session and project the graph with project_graph_cypher."
            )
        session_gds = session_manager.get_session(session_name)
        if session_gds is None:
            raise ValueError(
                f"Session '{session_name}' is no longer available. Recreate it with create_session."
            )
        return session_gds

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
                                    "description": "Name of the session to delete",
                                }
                            },
                            "required": ["sessionName"],
                        },
                    ),
                    types.Tool(
                        name="create_session",
                        description="""Create a named GDS session, or reconnect to an existing one.

Sessions are never created implicitly: create one with this tool before projecting graphs with project_graph_cypher (its sessionName parameter picks the target session). All other tools locate a graph's session automatically from graphName.
Most workflows need a single session holding all projected graphs; create additional sessions only to isolate graphs on separate compute, e.g. to run independent analyses in parallel.
To resize an existing session (e.g. after an OOM), delete it with delete_session and create it again with a larger memoryGB; this drops all graphs projected into it.
Session names are prefixed with 'mcp_' if not already; the returned sessionName is the actual name.""",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sessionName": {
                                    "type": "string",
                                    "description": "Name for the session. 'mcp_' is prepended if missing.",
                                },
                                "memoryGB": {
                                    "type": "integer",
                                    "description": "Optional memory size in GB (defaults to SESSION_MEMORY_GB or 8)",
                                },
                            },
                            "required": ["sessionName"],
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
                + embedding_tool_definitions
                + ml_pipeline_tool_definitions
            )
            apply_tool_annotations(tools)
            logger.info(f"Returning {len(tools)} tools")
            return tools
        except Exception as e:
            logger.error(f"Error in handle_list_tools: {e}")
            raise

    def execute_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        try:
            session_tool_names = {
                "list_sessions",
                "delete_session",
                "create_session",
            }
            if name in session_tool_names:
                if mode != GdsMode.SESSION:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Error: Session tool '{name}' is not available in plugin mode",
                        )
                    ]

                if name == "list_sessions":
                    result = session_manager.list_sessions()
                    return [
                        types.TextContent(type="text", text=serialize_result(result))
                    ]

                if name == "delete_session":
                    session_name = arguments.get("sessionName") if arguments else None
                    result = session_manager.delete_session(session_name)
                    return [
                        types.TextContent(type="text", text=serialize_result(result))
                    ]

                # create_session
                arguments = arguments or {}
                session_name = ensure_mcp_session_name(arguments.get("sessionName"))
                session_manager.create_or_get_session(
                    db_url,
                    (username, password),
                    database,
                    session_name=session_name,
                    memory_gb=arguments.get("memoryGB"),
                )
                result = {"sessionName": session_name, "status": "ready"}
                return [types.TextContent(type="text", text=serialize_result(result))]

            arguments = arguments or {}
            graph_name = arguments.get("graphName")

            if name == "project_graph_cypher":
                requested_session = arguments.get("sessionName")
                if mode == GdsMode.SESSION:
                    if not requested_session:
                        return [
                            types.TextContent(
                                type="text",
                                text="Error: sessionName is required in Aura session mode. "
                                "Create a session with create_session first.",
                            )
                        ]
                    target_session = ensure_mcp_session_name(requested_session)
                    project_gds = session_manager.get_session(target_session)
                    if project_gds is None:
                        return [
                            types.TextContent(
                                type="text",
                                text=f"Error: Session '{target_session}' not found. "
                                "Create it with create_session.",
                            )
                        ]
                    session_manager.assert_graph_unmapped(graph_name, target_session)
                else:
                    if requested_session:
                        return [
                            types.TextContent(
                                type="text",
                                text="Error: sessionName is only available in Aura session mode",
                            )
                        ]
                    project_gds = base_gds
                handler = ProjectGraphCypherHandler(project_gds)
                result = handler.execute(arguments)
                if mode == GdsMode.SESSION:
                    session_manager.record_graph(result["graphName"], target_session)
                return [types.TextContent(type="text", text=serialize_result(result))]

            active_gds = get_gds_for_graph(graph_name)

            if name == "count_nodes":
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

            elif name == "drop_graph":
                handler = DropGraphHandler(active_gds)
                result = handler.execute(arguments)
                if mode == GdsMode.SESSION:
                    session_manager.forget_graph(graph_name)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "list_graphs":
                if mode == GdsMode.SESSION:
                    graphs = []
                    for s_name, s_gds in session_manager.active_sessions():
                        listing = ListGraphsHandler(s_gds).execute({})
                        for graph in listing["graphs"]:
                            graph["sessionName"] = s_name
                        graphs.extend(listing["graphs"])
                    result = {"graphs": graphs, "count": len(graphs)}
                else:
                    result = ListGraphsHandler(active_gds).execute(arguments)
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "get_graph_info":
                handler = GraphInfoHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "stream_node_properties":
                handler = StreamNodePropertiesHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "stream_relationship_properties":
                handler = StreamRelationshipPropertiesHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "stream_relationships":
                handler = StreamRelationshipsHandler(active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

            # Model catalog tools carry no graphName; in session mode they span all sessions
            elif name == "list_models" and mode == GdsMode.SESSION:
                models = []
                for s_name, s_gds in session_manager.active_sessions():
                    listing = ListModelsHandler(s_gds).execute({})
                    for model in listing["models"]:
                        model["sessionName"] = s_name
                    models.extend(listing["models"])
                result = {"models": models, "count": len(models)}
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "drop_model" and mode == GdsMode.SESSION:
                for _, s_gds in session_manager.active_sessions():
                    try:
                        result = DropModelHandler(s_gds).execute(arguments)
                    except Exception:
                        continue
                    return [
                        types.TextContent(type="text", text=serialize_result(result))
                    ]
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: Model '{arguments.get('modelName')}' not found in any active session",
                    )
                ]

            else:
                handler = AlgorithmRegistry.get_handler(name, active_gds)
                result = handler.execute(arguments or {})
                return [types.TextContent(type="text", text=serialize_result(result))]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        # Run blocking GDS calls off the event loop so tool calls can execute in parallel
        return await asyncio.to_thread(execute_tool, name, arguments)

    return server, session_manager, base_gds


def initialization_options(server: Server) -> InitializationOptions:
    return InitializationOptions(
        server_name=SERVER_NAME,
        server_version=SERVER_VERSION,
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
        instructions=SERVER_INSTRUCTIONS,
    )


def is_stdio_disconnect_error(error: BaseException) -> bool:
    if isinstance(
        error, (BrokenResourceError, BrokenPipeError, ConnectionResetError, OSError)
    ):
        return True
    if isinstance(error, BaseExceptionGroup):
        return any(
            is_stdio_disconnect_error(sub_error) for sub_error in error.exceptions
        )
    return False


class StreamableHTTPASGIApp:
    def __init__(self, session_manager: StreamableHTTPSessionManager):
        self.session_manager = session_manager

    async def __call__(self, scope, receive, send):
        await self.session_manager.handle_request(scope, receive, send)


def create_streamable_http_app(
    server: Server,
    path: str = DEFAULT_HTTP_PATH,
    stateless: bool = False,
    json_response: bool = False,
):
    from starlette.applications import Starlette
    from starlette.routing import Route

    http_session_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=json_response,
        stateless=stateless,
    )
    http_app = StreamableHTTPASGIApp(http_session_manager)

    @contextlib.asynccontextmanager
    async def lifespan(app):
        async with http_session_manager.run():
            yield

    return Starlette(
        routes=[Route(normalize_http_path(path), endpoint=http_app)],
        lifespan=lifespan,
    )


async def run_stdio_server(server: Server):
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            initialization_options(server),
            raise_exceptions=False,
        )


async def run_streamable_http_server(
    server: Server,
    host: str = DEFAULT_HTTP_HOST,
    port: int = DEFAULT_HTTP_PORT,
    path: str = DEFAULT_HTTP_PATH,
):
    import uvicorn

    app = create_streamable_http_app(server, path)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()


async def main(
    db_url: str,
    username: str,
    password: str,
    database: str = None,
    transport: str = STDIO_TRANSPORT,
    host: str = DEFAULT_HTTP_HOST,
    port: int = DEFAULT_HTTP_PORT,
    path: str = DEFAULT_HTTP_PATH,
):
    transport_mode = normalize_transport(transport)
    server, session_manager, base_gds = create_mcp_server(
        db_url, username, password, database
    )
    try:
        if transport_mode == HTTP_TRANSPORT:
            await run_streamable_http_server(server, host, port, path)
        else:
            await run_stdio_server(server)
    except Exception as e:
        stdio_disconnect = (
            transport_mode == STDIO_TRANSPORT and is_stdio_disconnect_error(e)
        )
        if stdio_disconnect:
            logger.info("Server shutdown (client disconnected)")
        else:
            logger.info(f"Server shutdown with error: {e}")
            raise
    finally:
        with contextlib.suppress(Exception):
            session_manager.close()
            base_gds.close()


if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Neo4j GDS MCP Server")
    parser.add_argument("db_url", help="URL to Neo4j database")
    parser.add_argument("username", help="Username for Neo4j database")
    parser.add_argument("password", help="Password for Neo4j database")
    parser.add_argument("database", nargs="?", help="Database name to connect to")
    parser.add_argument(
        "--transport",
        choices=sorted(TRANSPORT_ALIASES),
        default=STDIO_TRANSPORT,
        help="MCP transport to use",
    )
    parser.add_argument("--host", default=DEFAULT_HTTP_HOST, help="HTTP host")
    parser.add_argument("--port", type=int, default=DEFAULT_HTTP_PORT, help="HTTP port")
    parser.add_argument("--path", default=DEFAULT_HTTP_PATH, help="HTTP MCP path")
    args = parser.parse_args()

    asyncio.run(
        main(
            args.db_url,
            args.username,
            args.password,
            args.database,
            transport=args.transport,
            host=args.host,
            port=args.port,
            path=args.path,
        )
    )
