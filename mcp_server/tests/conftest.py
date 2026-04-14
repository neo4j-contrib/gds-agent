import os
import subprocess
import time
import pytest
import pytest_asyncio
import asyncio
import json
import sys
import atexit
from neo4j import GraphDatabase
from pathlib import Path

NEO4J_IMAGE = "neo4j:2025.05.0"
NEO4J_BOLT_PORT = 7687
NEO4J_HTTP_PORT = 7474
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "testpassword"


# Global cleanup function
def cleanup_containers():
    """Clean up any lingering Neo4j containers."""
    try:
        print("Cleaning up Neo4j containers...", flush=True)
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "ancestor=neo4j:2025.05.0", "-q"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            container_ids = result.stdout.strip().split("\n")
            subprocess.run(["docker", "rm", "-f"] + container_ids, check=False)
    except Exception as e:
        print(f"Error during cleanup: {e}", flush=True)


# Register cleanup function
atexit.register(cleanup_containers)


def is_neo4j_responsive(url):
    """Check if Neo4j is responsive."""
    try:
        driver = GraphDatabase.driver(url, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            gds_check = session.run("RETURN gds.version()")
            print(gds_check.single()["gds.version()"])
        driver.close()
        return True
    except Exception as e:
        print(f"Neo4j not responsive: {e}", flush=True)
        return False


@pytest.fixture(scope="session")
def neo4j_container(docker_ip, docker_services):
    """Start a Neo4j container for testing."""
    # Get the dynamically allocated port for the neo4j service
    port = docker_services.port_for("neo4j", NEO4J_BOLT_PORT)
    url = f"bolt://{docker_ip}:{port}"

    print(f"Waiting for Neo4j to be responsive at {url}", flush=True)

    # Wait a bit before first connection attempt
    time.sleep(10)

    # Wait for Neo4j to be responsive with longer timeout and less frequent checks
    docker_services.wait_until_responsive(
        timeout=180.0,  # 3 minutes timeout
        pause=10.0,  # Check every 10 seconds (much less frequent)
        check=lambda: is_neo4j_responsive(url),
    )

    print(f"Neo4j is now responsive at {url}", flush=True)

    try:
        yield url
    finally:
        # Ensure cleanup happens even if tests are interrupted
        print("Cleaning up Neo4j container...", flush=True)


@pytest.fixture(scope="session")
def import_test_data(neo4j_container):
    """Import test data into Neo4j."""
    # Set environment variables for the import script
    os.environ["NEO4J_URI"] = neo4j_container
    os.environ["NEO4J_USERNAME"] = NEO4J_USER
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # Check if data already exists
        res = session.run(
            "MATCH (n) WHERE 'UndergroundStation' IN labels(n) RETURN count(n) as count"
        )
        existing_count = res.single()["count"]
        print(f"Existing UndergroundStation count: {existing_count}", flush=True)

        if existing_count > 0:
            print("Data already exists, skipping import", flush=True)
            driver.close()
            return

        # Clean up any existing data and constraints
        print("Cleaning up existing data...", flush=True)
        session.run("MATCH (n) DETACH DELETE n")

        # Drop all existing constraints
        try:
            constraints = session.run("SHOW CONSTRAINTS").data()
            for constraint in constraints:
                constraint_name = constraint.get("name", "")
                if constraint_name:
                    session.run(f"DROP CONSTRAINT {constraint_name} IF EXISTS")
                    print(f"Dropped constraint: {constraint_name}", flush=True)
        except Exception as e:
            print(f"Error dropping constraints: {e}", flush=True)

        res = session.run("MATCH (n) RETURN count(n)")
        print(f"Node count after cleanup: {res.single()['count(n)']}", flush=True)
    driver.close()

    # Import the data using the existing import script
    # Add project root to path (go up from tests/ to mcp_server/ to project root)
    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))

    # Change to project root directory so the relative path works
    original_cwd = os.getcwd()
    os.chdir(project_root)

    print(f"Importing test data from {project_root}/dataset/london.json", flush=True)
    from import_data import import_tube_data

    import_tube_data(neo4j_container, NEO4J_USER, NEO4J_PASSWORD, "dataset/london.json")
    print("Test data imported successfully", flush=True)

    # Verify the data was actually imported
    driver = GraphDatabase.driver(neo4j_container, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        count = session.run(
            "MATCH (n) WHERE 'UndergroundStation' IN labels(n) RETURN count(n) as count"
        ).single()["count"]
        print(f"Verified: {count} UndergroundStation nodes in database", flush=True)
    driver.close()

    # Change back to original directory
    os.chdir(original_cwd)


@pytest_asyncio.fixture
async def mcp_server_process(import_test_data):
    """Start the MCP server as a subprocess and communicate via stdio."""
    # Start the server process
    proc = await asyncio.create_subprocess_exec(
        "python",
        "-m",
        "mcp_server_neo4j_gds.server",
        os.environ["NEO4J_URI"],
        os.environ["NEO4J_USERNAME"],
        os.environ["NEO4J_PASSWORD"],
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=1024 * 1024 * 10,  # 10MB buffer limit
    )

    # Wait a moment for the server to initialize
    await asyncio.sleep(5)

    # Check if the process is still alive
    if proc.returncode is not None:
        stderr_output = await proc.stderr.read()
        print(
            f"Server process died with return code {proc.returncode}: {stderr_output.decode()}"
        )
        raise RuntimeError(f"Server process failed to start: {stderr_output.decode()}")

    yield proc

    # Cleanup
    proc.terminate()
    await proc.wait()


class MCPClient:
    """Simple MCP client for testing via stdio."""

    def __init__(self, process):
        self.process = process
        self.request_id = 0

    async def send_request(self, method, params=None):
        """Send a JSON-RPC request to the MCP server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }

        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()

        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from MCP server")

        # Decode with error handling for large responses
        try:
            response_text = response_line.decode().strip()
            response = json.loads(response_text)
        except UnicodeDecodeError as e:
            raise RuntimeError(f"Failed to decode response: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response: {e}")

        return response

    async def list_tools(self):
        """List available tools."""
        response = await self.send_request("tools/list")
        return response.get("result", {}).get("tools", [])

    async def call_tool(self, name, arguments=None):
        """Call a tool by name with arguments."""
        response = await self.send_request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )
        return response.get("result", {}).get("content", [])


@pytest_asyncio.fixture
async def mcp_client(mcp_server_process):
    """Create an MCP client for testing."""
    client = MCPClient(mcp_server_process)

    # Initialize the connection
    await client.send_request(
        "initialize",
        {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    )

    # Send initialized notification (no ID for notifications)
    notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    notification_str = json.dumps(notification) + "\n"
    client.process.stdin.write(notification_str.encode())
    await client.process.stdin.drain()

    yield client


@pytest_asyncio.fixture
async def projected_test_graph(mcp_client):
    import uuid

    graph_name = f"test_graph_{uuid.uuid4().hex[:8]}"

    cypher_query = """
        MATCH (n:UndergroundStation)-[r:LINK]->(m:UndergroundStation)
        RETURN gds.graph.project(
            $graph_name,
            n,
            m,
            {
                sourceNodeLabels: labels(n),
                targetNodeLabels: labels(m),
                relationshipType: type(r),
                sourceNodeProperties: {
                    total_lines: toInteger(n.total_lines),
                    zone: toFloat(n.zone),
                    rail: toInteger(n.rail),
                    latitude: toFloat(n.latitude),
                    longitude: toFloat(n.longitude)
                },
                targetNodeProperties: {
                    total_lines: toInteger(m.total_lines),
                    zone: toFloat(m.zone),
                    rail: toInteger(m.rail),
                    latitude: toFloat(m.latitude),
                    longitude: toFloat(m.longitude)
                },
                relationshipProperties: {time: toFloat(r.time), distance: toFloat(r.distance)}
            }
        )
    """

    await mcp_client.call_tool(
        "project_graph_cypher",
        {"graphName": graph_name, "cypherQuery": cypher_query},
    )

    yield graph_name

    try:
        await mcp_client.call_tool("drop_graph", {"graphName": graph_name})
    except Exception:
        pass


@pytest_asyncio.fixture
async def projected_undirected_graph(mcp_client):
    import uuid

    graph_name = f"test_undirected_{uuid.uuid4().hex[:8]}"

    cypher_query = """
        MATCH (n:UndergroundStation)-[r:LINK]->(m:UndergroundStation)
        RETURN gds.graph.project(
            $graph_name,
            n,
            m,
            {
                sourceNodeLabels: labels(n),
                targetNodeLabels: labels(m),
                relationshipType: type(r),
                sourceNodeProperties: {
                    total_lines: toInteger(n.total_lines),
                    zone: toFloat(n.zone),
                    rail: toInteger(n.rail),
                    latitude: toFloat(n.latitude),
                    longitude: toFloat(n.longitude)
                },
                targetNodeProperties: {
                    total_lines: toInteger(m.total_lines),
                    zone: toFloat(m.zone),
                    rail: toInteger(m.rail),
                    latitude: toFloat(m.latitude),
                    longitude: toFloat(m.longitude)
                },
                relationshipProperties: {time: toFloat(r.time), distance: toFloat(r.distance)}
            },
            {
                undirectedRelationshipTypes: ['LINK']
            }
        )
    """

    await mcp_client.call_tool(
        "project_graph_cypher",
        {"graphName": graph_name, "cypherQuery": cypher_query},
    )

    yield graph_name

    try:
        await mcp_client.call_tool("drop_graph", {"graphName": graph_name})
    except Exception:
        pass
