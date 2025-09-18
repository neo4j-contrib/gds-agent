import logging
import os
import platform
import sys
import signal
from dotenv import load_dotenv

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


def main():
    """Main entry point for the package."""
    load_dotenv("../../../.env")
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

    args = parser.parse_args()

    asyncio.run(
        server.main(
            db_url=args.db_url,
            username=args.username,
            password=args.password,
            database=args.database,
        )
    )


__all__ = ["main", "server"]
