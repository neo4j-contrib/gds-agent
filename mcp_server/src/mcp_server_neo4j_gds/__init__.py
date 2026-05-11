import logging
import os
import sys
from dotenv import find_dotenv, load_dotenv

from . import server
import asyncio
import argparse


logger = logging.getLogger("mcp_server_neo4j_gds")
logger.handlers.clear()
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


def env_value(*names: str, default=None):
    for name in names:
        value = os.environ.get(name)
        if value is not None:
            return value
    return default


def main():
    """Main entry point for the package."""
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(env_path)
    parser = argparse.ArgumentParser(description="Neo4j GDS MCP Server")
    parser.add_argument(
        "--db-url", default=os.environ.get("NEO4J_URI"), help="URL to Neo4j database"
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("NEO4J_USERNAME", "neo4j"),
        help="Username for Neo4j database",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("NEO4J_PASSWORD"),
        help="Password for Neo4j database",
    )
    parser.add_argument(
        "--database",
        default=os.environ.get("NEO4J_DATABASE"),
        help="Database name to connect to (optional). By default, the server will connect to the 'neo4j' database.",
    )
    parser.add_argument(
        "--transport",
        choices=sorted(server.TRANSPORT_ALIASES),
        default=env_value(
            "GDS_AGENT_TRANSPORT",
            "NEO4J_TRANSPORT",
            "MCP_TRANSPORT",
            default=server.STDIO_TRANSPORT,
        ),
        help="MCP transport to use. Use 'stdio' for local MCP clients or 'http'/'streamable-http' for HTTP clients.",
    )
    parser.add_argument(
        "--host",
        default=env_value(
            "GDS_AGENT_HOST",
            "NEO4J_MCP_SERVER_HOST",
            "MCP_SERVER_HOST",
            default=server.DEFAULT_HTTP_HOST,
        ),
        help="HTTP host when using HTTP transport.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(
            env_value(
                "GDS_AGENT_PORT",
                "NEO4J_MCP_SERVER_PORT",
                "MCP_SERVER_PORT",
                default=server.DEFAULT_HTTP_PORT,
            )
        ),
        help="HTTP port when using HTTP transport.",
    )
    parser.add_argument(
        "--path",
        default=env_value(
            "GDS_AGENT_PATH",
            "NEO4J_MCP_SERVER_PATH",
            "MCP_SERVER_PATH",
            default=server.DEFAULT_HTTP_PATH,
        ),
        help="HTTP path when using HTTP transport.",
    )

    args = parser.parse_args()

    asyncio.run(
        server.main(
            db_url=args.db_url,
            username=args.username,
            password=args.password,
            database=args.database,
            transport=args.transport,
            host=args.host,
            port=args.port,
            path=args.path,
        )
    )


__all__ = ["main", "server"]
