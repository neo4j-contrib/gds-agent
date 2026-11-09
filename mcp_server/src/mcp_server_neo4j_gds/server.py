# server.py
import asyncio
import contextlib
import json
import logging
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import mcp.server.stdio
import pandas as pd
from anyio import BrokenResourceError
from graphdatascience import GraphDataScience
from graphdatascience.query_runner.query_mode import QueryMode
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from neo4j import READ_ACCESS, WRITE_ACCESS, GraphDatabase, Query

from .centrality_algorithm_specs import centrality_tool_definitions
from .community_algorithm_specs import community_tool_definitions
from .embedding_algorithm_specs import embedding_tool_definitions
from .graph_projection_handlers import (
    DropGraphHandler,
    GraphInfoHandler,
    ListGraphsHandler,
    ProjectGraphCypherHandler,
    StreamNodePropertiesHandler,
    StreamRelationshipPropertiesHandler,
    StreamRelationshipsHandler,
)
from .graph_projection_specs import graph_projection_tool_definitions
from .ml_pipeline_handlers import DropModelHandler, ListModelsHandler
from .ml_pipeline_specs import ml_pipeline_tool_definitions
from .path_algorithm_specs import path_tool_definitions
from .registry import AlgorithmRegistry
from .result_limits import (
    dataframe_limit_reminder,
    dataframe_limit_warning,
    limit_dataframe_rows,
    limit_text,
    max_cell_chars,
)
from .session_manager import GdsMode, SessionManager, ensure_mcp_session_name
from .similarity_algorithm_specs import similarity_tool_definitions

logger = logging.getLogger("mcp_server_neo4j_gds")
SERVER_NAME = "neo4j_gds"
SERVER_INSTRUCTIONS = (
    "Inspect the Neo4j schema before assuming labels, relationship types, or properties. "
    "GDS algorithms require an in-memory graph created with project_graph_cypher; in Aura "
    "session mode, create a session first. Use stream mode for returned rows and mutate mode "
    "to store results in the projected graph for later steps. node_identifier_property maps "
    "database property values to readable node identifiers. Drop unused graphs, models, and sessions."
)
try:
    SERVER_VERSION = version("gds-agent")
except PackageNotFoundError:
    SERVER_VERSION = "0.0.0"
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_PATH = "/mcp"
DEFAULT_READ_TIMEOUT = 120
STDIO_TRANSPORT = "stdio"
HTTP_TRANSPORT = "streamable-http"
TRANSPORT_ALIASES = {
    STDIO_TRANSPORT: STDIO_TRANSPORT,
    "http": HTTP_TRANSPORT,
    HTTP_TRANSPORT: HTTP_TRANSPORT,
}


class Neo4jDriverConnection:
    def __init__(
        self, db_url: str, username: str, password: str, database: str | None = None
    ):
        self._driver = GraphDatabase.driver(db_url, auth=(username, password))
        self._database = database

    def run_cypher(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        database: str | None = None,
        mode: QueryMode | None = None,
    ) -> pd.DataFrame:
        access_mode = READ_ACCESS if mode == QueryMode.READ else WRITE_ACCESS
        with self._driver.session(
            database=database or self._database, default_access_mode=access_mode
        ) as session:
            result = session.run(query, params or {})
            keys = result.keys()
            return pd.DataFrame([record.data() for record in result], columns=keys)

    def close(self):
        self._driver.close()


def read_cypher(
    connection,
    query: str,
    params: dict[str, Any] | None = None,
    timeout: float = DEFAULT_READ_TIMEOUT,
) -> list[dict[str, Any]]:
    params = params or {}
    if isinstance(connection, Neo4jDriverConnection):
        driver, database = connection._driver, connection._database
    else:
        runner = connection._query_runner
        driver, database = runner._driver, runner._database

    with driver.session(database=database, default_access_mode=READ_ACCESS) as session:
        result = session.run(Query(query, timeout=float(timeout)), params)
        return [record.data() for record in result]


def write_cypher(connection, query: str, params: dict[str, Any] | None = None) -> dict:
    params = params or {}
    if isinstance(connection, Neo4jDriverConnection):
        driver, database = connection._driver, connection._database
    else:
        runner = connection._query_runner
        driver, database = runner._driver, runner._database

    with driver.session(database=database, default_access_mode=WRITE_ACCESS) as session:
        explained = session.run(f"EXPLAIN {query}", params)
        if "w" not in (explained.consume().query_type or ""):
            raise ValueError("Only write queries are allowed for write-query")
        counters = session.run(query, params).consume().counters

    return {
        name: getattr(counters, name)
        for name in (
            "nodes_created",
            "nodes_deleted",
            "relationships_created",
            "relationships_deleted",
            "properties_set",
            "labels_added",
            "labels_removed",
            "indexes_added",
            "indexes_removed",
            "constraints_added",
            "constraints_removed",
            "system_updates",
            "contains_updates",
        )
    }


def is_aura_graph_analytics_versionless_error(error: Exception) -> bool:
    return "Aura Graph Analytics is versionless" in str(error)


def create_base_gds(
    db_url: str, username: str, password: str, database: str | None = None
):
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
            text = f"{warning}\n\n{text}\n\n{dataframe_limit_reminder(result)}"
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
    db_url: str,
    username: str,
    password: str,
    database: str | None = None,
    allow_writes: bool = False,
    read_timeout: float = DEFAULT_READ_TIMEOUT,
) -> tuple[Server, SessionManager, GraphDataScience | Neo4jDriverConnection]:
    logger.info(f"Starting MCP Server for {db_url} with username {username}")
    if database:
        logger.info(f"Connecting to database: {database}")

    # Create GraphDataScience object with optional database parameter
    base_gds = create_base_gds(db_url, username, password, database)
    logger.info("Successfully connected to Neo4j database")

    session_manager = SessionManager()
    mode = session_manager.detect_mode(base_gds)
    logger.info(f"Detected GDS mode: {mode}")

    def get_gds_for_graph(graph_name: str | None = None) -> GraphDataScience:
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

    async def handle_list_tools(
        _ctx: Any, _params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
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
                                "session_name": {
                                    "type": "string",
                                    "description": "Name of the session to delete",
                                }
                            },
                            "required": ["session_name"],
                        },
                    ),
                    types.Tool(
                        name="create_session",
                        description="""Create a named GDS session, or reconnect to an existing one.

Sessions are never created implicitly: create one with this tool before projecting graphs with project_graph_cypher (its session_name parameter picks the target session). All other tools locate a graph's session automatically from graph_name.
Most workflows need a single session holding all projected graphs; create additional sessions only to isolate graphs on separate compute, e.g. to run independent analyses in parallel.
To resize an existing session (e.g. after an OOM), delete it with delete_session and create it again with a larger memory_gb; this drops all graphs projected into it.
Session names are prefixed with 'mcp_' if not already; the returned session_name is the actual name.""",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "session_name": {
                                    "type": "string",
                                    "description": "Name for the session. 'mcp_' is prepended if missing.",
                                },
                                "memory_gb": {
                                    "type": "integer",
                                    "description": "Optional memory size in GB (defaults to SESSION_MEMORY_GB or 8)",
                                },
                            },
                            "required": ["session_name"],
                        },
                    ),
                ]

            cypher_tools = [
                types.Tool(
                    name="read_neo4j_cypher",
                    description="""Execute a read Cypher query on the neo4j database.""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The Cypher query to execute.",
                            },
                            "params": {
                                "type": "object",
                                "description": "The parameters to pass to the Cypher query.",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="get_neo4j_schema",
                    description="""Returns nodes, their properties (with types), and relationship types using native Neo4j schema introspection.""",
                    inputSchema={
                        "type": "object",
                    },
                ),
            ]
            if allow_writes:
                cypher_tools = cypher_tools + [
                    types.Tool(
                        name="write_neo4j_cypher",
                        description="""Execute a write Cypher query on the neo4j database.""",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The Cypher query to execute.",
                                },
                                "params": {
                                    "type": "object",
                                    "description": "The parameters to pass to the Cypher query.",
                                },
                            },
                            "required": ["query"],
                        },
                    )
                ]

            tools = (
                cypher_tools
                + session_tools
                + graph_projection_tool_definitions
                + centrality_tool_definitions
                + community_tool_definitions
                + path_tool_definitions
                + similarity_tool_definitions
                + embedding_tool_definitions
                + ml_pipeline_tool_definitions
            )
            logger.info(f"Returning {len(tools)} tools")
            return types.ListToolsResult(tools=tools)
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
                    session_name = arguments.get("session_name") if arguments else None
                    result = session_manager.delete_session(session_name)
                    return [
                        types.TextContent(type="text", text=serialize_result(result))
                    ]

                # create_session
                arguments = arguments or {}
                session_name = ensure_mcp_session_name(arguments.get("session_name"))
                session_manager.create_or_get_session(
                    db_url,
                    (username, password),
                    database,
                    session_name=session_name,
                    memory_gb=arguments.get("memory_gb"),
                )
                result = {"session_name": session_name, "status": "ready"}
                return [types.TextContent(type="text", text=serialize_result(result))]

            arguments = arguments or {}

            if name == "read_neo4j_cypher":
                result = read_cypher(
                    base_gds,
                    arguments.get("query"),
                    arguments.get("params"),
                    timeout=read_timeout,
                )
                return [
                    types.TextContent(
                        type="text",
                        text=serialize_result(result),
                    )
                ]

            if name == "write_neo4j_cypher":
                if not allow_writes:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: write_neo4j_cypher is not available in read-only mode",
                        )
                    ]
                result = write_cypher(
                    base_gds,
                    arguments.get("query"),
                    arguments.get("params"),
                )
                return [types.TextContent(type="text", text=serialize_result(result))]

            if name == "get_neo4j_schema":
                schema = {}
                node_props = base_gds.run_cypher(
                    "CALL db.schema.nodeTypeProperties() YIELD nodeLabels, propertyName, propertyTypes, mandatory",
                    mode=QueryMode.READ,
                )
                for _, row in node_props.iterrows():
                    for label in row["nodeLabels"]:
                        entry = schema.setdefault(
                            label, {"type": "node", "properties": {}}
                        )
                        if row["propertyName"]:
                            entry["properties"][row["propertyName"]] = {
                                "type": row["propertyTypes"],
                                "mandatory": row["mandatory"],
                            }
                rel_props = base_gds.run_cypher(
                    "CALL db.schema.relTypeProperties() YIELD relType, propertyName, propertyTypes, mandatory",
                    mode=QueryMode.READ,
                )
                for _, row in rel_props.iterrows():
                    rel_type = row["relType"].lstrip(":").strip("`")
                    entry = schema.setdefault(
                        rel_type,
                        {"type": "relationship", "properties": {}, "connections": []},
                    )
                    if row["propertyName"]:
                        entry["properties"][row["propertyName"]] = {
                            "type": row["propertyTypes"],
                            "mandatory": row["mandatory"],
                        }
                indexes = base_gds.run_cypher(
                    "SHOW INDEXES YIELD labelsOrTypes, properties RETURN labelsOrTypes, properties",
                    mode=QueryMode.READ,
                )
                indexed_props = set()
                for _, row in indexes.iterrows():
                    for label in row["labelsOrTypes"] or []:
                        for prop in row["properties"] or []:
                            indexed_props.add((label, prop))
                triplets = base_gds.run_cypher(
                    "MATCH (a)-[r]->(b) RETURN DISTINCT type(r) AS rel_type, labels(a)[0] AS from_label, labels(b)[0] AS to_label",
                    mode=QueryMode.READ,
                )
                for _, row in triplets.iterrows():
                    if row["rel_type"] in schema:
                        schema[row["rel_type"]]["connections"].append(
                            {"from": row["from_label"], "to": row["to_label"]}
                        )
                for key, entry in schema.items():
                    if entry["type"] == "node":
                        for prop_name, prop_info in entry["properties"].items():
                            prop_info["indexed"] = (key, prop_name) in indexed_props
                        result = base_gds.run_cypher(
                            f"MATCH (n:`{key}`) RETURN count(n) AS count",
                            mode=QueryMode.READ,
                        )
                        entry["count"] = int(result["count"].iloc[0])
                    elif entry["type"] == "relationship":
                        result = base_gds.run_cypher(
                            f"MATCH ()-[r:{key}]->() RETURN count(r) AS count",
                            mode=QueryMode.READ,
                        )
                        entry["count"] = int(result["count"].iloc[0])
                return [types.TextContent(type="text", text=serialize_result(schema))]

            graph_name = arguments.get("graph_name")

            if name == "project_graph_cypher":
                requested_session = arguments.get("session_name")
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
                    session_manager.record_graph(result["graph_name"], target_session)
                return [types.TextContent(type="text", text=serialize_result(result))]

            active_gds = get_gds_for_graph(graph_name)

            if name == "drop_graph":
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
                            graph["session_name"] = s_name
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
                        model["session_name"] = s_name
                    models.extend(listing["models"])
                result = {"models": models, "count": len(models)}
                return [types.TextContent(type="text", text=serialize_result(result))]

            elif name == "drop_model" and mode == GdsMode.SESSION:
                for s_name, s_gds in session_manager.active_sessions():
                    try:
                        result = DropModelHandler(s_gds).execute(arguments)
                    except Exception as e:
                        logger.debug("drop_model failed in session '%s': %s", s_name, e)
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
            return [types.TextContent(type="text", text=f"Error: {e!s}")]

    async def handle_call_tool(
        _ctx: Any, params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        # Run blocking GDS calls off the event loop so tool calls can execute in parallel
        content = await asyncio.to_thread(execute_tool, params.name, params.arguments)
        return types.CallToolResult(content=content)

    server = Server(
        SERVER_NAME,
        version=SERVER_VERSION,
        instructions=SERVER_INSTRUCTIONS,
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )
    return server, session_manager, base_gds


def initialization_options(server: Server) -> InitializationOptions:
    return server.create_initialization_options(
        notification_options=NotificationOptions(),
        experimental_capabilities={},
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


def create_streamable_http_app(
    server: Server,
    path: str = DEFAULT_HTTP_PATH,
    host: str = DEFAULT_HTTP_HOST,
    stateless: bool = False,
    json_response: bool = False,
):
    return server.streamable_http_app(
        streamable_http_path=normalize_http_path(path),
        json_response=json_response,
        stateless_http=stateless,
        host=host,
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

    app = create_streamable_http_app(server, path, host=host)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    uvicorn_server = uvicorn.Server(config)
    await uvicorn_server.serve()


async def main(
    db_url: str,
    username: str,
    password: str,
    database: str | None = None,
    transport: str = STDIO_TRANSPORT,
    host: str = DEFAULT_HTTP_HOST,
    port: int = DEFAULT_HTTP_PORT,
    path: str = DEFAULT_HTTP_PATH,
    allow_writes: bool = False,
    read_timeout: float = DEFAULT_READ_TIMEOUT,
):
    transport_mode = normalize_transport(transport)
    server, session_manager, base_gds = create_mcp_server(
        db_url,
        username,
        password,
        database,
        allow_writes=allow_writes,
        read_timeout=read_timeout,
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
    import argparse
    import asyncio
    import os

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
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Do not expose write_neo4j_cypher. This is the default; set NEO4J_READ_ONLY=false to expose it.",
    )
    parser.add_argument(
        "--read-timeout",
        type=float,
        default=float(os.environ.get("NEO4J_READ_TIMEOUT") or DEFAULT_READ_TIMEOUT),
        help="Timeout in seconds for read_neo4j_cypher queries (default: 120).",
    )
    args = parser.parse_args()
    allow_writes = (
        not args.read_only
        and os.environ.get("NEO4J_READ_ONLY", "true").strip().lower() == "false"
    )

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
            allow_writes=allow_writes,
            read_timeout=args.read_timeout,
        )
    )
