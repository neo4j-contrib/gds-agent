from graphdatascience import GraphDataScience
import uuid
from contextlib import contextmanager
import logging
import os
import platform


def get_log_file_path():
    """Get the appropriate log file path based on the environment."""
    current_dir = os.getcwd()

    # Check if we're in development (project directory has pyproject.toml or src/)
    if os.path.exists(os.path.join(current_dir, "pyproject.toml")) or os.path.exists(
        os.path.join(current_dir, "src")
    ):
        return "mcp-server-neo4j-gds.log"

    # Production: use platform-specific Claude logs directory
    system = platform.system()
    home = os.path.expanduser("~")

    if system == "Darwin":  # macOS
        claude_logs_dir = os.path.join(home, "Library", "Logs", "Claude")
    elif system == "Windows":
        claude_logs_dir = os.path.join(
            os.environ.get("APPDATA", home), "Claude", "Logs"
        )
    else:  # Linux and other Unix-like systems
        claude_logs_dir = os.path.join(home, ".local", "share", "Claude", "logs")

    # Use Claude logs directory if it exists, otherwise fall back to current directory
    if os.path.exists(claude_logs_dir):
        return os.path.join(claude_logs_dir, "mcp-server-neo4j-gds.log")
    else:
        return "mcp-server-neo4j-gds.log"


log_file = get_log_file_path()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger("mcp_server_neo4j_gds")


@contextmanager
def projected_graph(gds, node_labels=None, undirected=False):
    """
    Project a graph from the database.

    Args:
        gds: GraphDataScience instance
        node_labels: specifies node labels to project. If empty, all nodes are projected. Default is []
        undirected: If True, project as undirected graph. Default is False (directed).
    """
    if node_labels is None:
        node_labels = []
    graph_name = f"temp_graph_{uuid.uuid4().hex[:8]}"

    try:
        # Get relationship properties (non-string)
        rel_properties = get_relationship_properties_keys(gds)
        valid_rel_properties = validate_rel_properties(gds, rel_properties, node_labels)
        rel_prop_map = ", ".join(f"{prop}: r.{prop}" for prop in valid_rel_properties)

        # Get node properties and validate to see which are compatible with GDS
        node_properties = get_node_properties_keys(gds)
        valid_node_projection_properties = validate_node_properties(
            gds, node_properties
        )
        node_prop_map_source = create_source_projection_properties(
            valid_node_projection_properties
        )
        node_prop_map_target = create_target_projection_properties(
            valid_node_projection_properties
        )

        logger.info(f"Node property map source: '{node_prop_map_source}'")
        logger.info(f"Node property map target: '{node_prop_map_target}'")

        # Configure graph projection based on undirected parameter
        # Create data configuration (node/relationship structure)
        data_config_parts = [
            "sourceNodeLabels: labels(n)",
            "targetNodeLabels: labels(m)",
            "relationshipType: type(r)",
        ]

        # create projection query for node/rel entities
        match_proj_query = create_projection_query(node_labels)

        if node_prop_map_source or node_prop_map_target:
            data_config_parts.extend(
                [
                    f"sourceNodeProperties: {{{node_prop_map_source}}}",
                    f"targetNodeProperties: {{{node_prop_map_target}}}",
                ]
            )

        if rel_prop_map:
            data_config_parts.append(f"relationshipProperties: {{{rel_prop_map}}}")

        data_config = ", ".join(data_config_parts)

        # Create additional configuration
        additional_config_parts = []
        if undirected:
            additional_config_parts.append("undirectedRelationshipTypes: ['*']")

        additional_config = (
            ", ".join(additional_config_parts) if additional_config_parts else ""
        )

        # Use separate data and additional configuration parameters
        if additional_config:
            project_query = f"""
                       {match_proj_query}
                       WITH n, r, m
                       RETURN gds.graph.project(
                           $graph_name,
                           n,
                           m,
                           {{{data_config}}},
                           {{{additional_config}}}
                       )
                       """
            logger.info(f"Project query: '{project_query}'")
            G, _ = gds.graph.cypher.project(
                project_query,
                graph_name=graph_name,
            )
        else:
            projection_query = f"""
                       {match_proj_query}
                       WITH n, r, m
                       RETURN gds.graph.project(
                           $graph_name,
                           n,
                           m,
                           {{{data_config}}}
                       )
                       """
            logger.info(f"Projection query: '{projection_query}'")
            G, _ = gds.graph.cypher.project(
                projection_query,
                graph_name=graph_name,
            )
        yield G
    finally:
        gds.graph.drop(graph_name)


def get_node_labels(gds: GraphDataScience):
    query = """
                MATCH (n)
                RETURN DISTINCT labels(n) as labels
                """
    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["labels"].iloc[0]


def count_nodes(gds: GraphDataScience):
    with projected_graph(gds) as G:
        return G.node_count()


def get_node_properties_keys(gds: GraphDataScience):
    query = """
        MATCH (n)
        RETURN DISTINCT keys(properties(n)) AS properties_keys
        """
    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["properties_keys"].iloc[0]


def get_relationship_properties_keys(gds: GraphDataScience):
    query = """
        MATCH (n)-[r]->(m)
        RETURN DISTINCT keys(properties(r)) AS properties_keys
        """
    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["properties_keys"].iloc[0]


def create_projection_query(node_labels):
    if len(node_labels) > 0:
        match_proj_query = f"""
               MATCH (n)
               WHERE ANY(l IN labels(n) WHERE l IN {node_labels})
               OPTIONAL
               MATCH (n)-[r]->(m)
               WHERE ANY(l IN labels(n) WHERE l IN {node_labels})
                 AND ANY(l IN labels(m) WHERE l IN {node_labels})

               """
    else:
        match_proj_query = """MATCH (n) OPTIONAL MATCH (n)-[r]->(m)"""
    return match_proj_query


def validate_rel_properties(gds: GraphDataScience, rel_properties, node_labels=None):
    if len(node_labels) > 0:
        match_rel_query = f"""
            MATCH (n)-[r]->(m)
            WHERE ANY(l IN labels(n) WHERE l IN {node_labels})
              AND ANY(l IN labels(m) WHERE l IN {node_labels})

            """
    else:
        match_rel_query = """MATCH (n)-[r]->(m)"""
    valid_rel_properties = {}
    for i in range(len(rel_properties)):
        pi = gds.run_cypher(
            f"{match_rel_query} RETURN distinct r.{rel_properties[i]} IS :: STRING AS ISSTRING"
        )
        if pi.shape[0] == 1 and bool(pi["ISSTRING"][0]) is False:
            valid_rel_properties[rel_properties[i]] = f"r.{rel_properties[i]}"
    return valid_rel_properties


def validate_node_properties(gds: GraphDataScience, node_properties, node_labels=None):
    if node_labels is None:
        node_labels = []

    projectable_properties = {}

    for i in range(len(node_properties)):
        # Check property types and whether all values are whole numbers
        if len(node_labels) > 0:
            match_node_query = f"MATCH (n) WHERE ANY(l IN labels(n) WHERE l IN {node_labels}) AND n.{node_properties[i]} IS NOT NULL"
        else:
            match_node_query = f"MATCH (n) WHERE n.{node_properties[i]} IS NOT NULL"

        type_check = gds.run_cypher(
            f"""
            {match_node_query}
            WITH n.{node_properties[i]} AS prop
            RETURN 
                prop IS :: LIST<FLOAT NOT NULL> AS IS_LIST_FLOAT,
                prop IS :: LIST<INTEGER NOT NULL> AS IS_LIST_INTEGER,
                prop IS :: INTEGER AS IS_INTEGER,
                prop IS :: FLOAT AS IS_FLOAT,
                CASE 
                    WHEN prop IS :: FLOAT THEN null
                    WHEN prop IS :: INTEGER THEN null
                    WHEN prop IS :: LIST<FLOAT NOT NULL> THEN null
                    WHEN prop IS :: LIST<INTEGER NOT NULL> THEN null
                    ELSE 1
                END AS INVALID_PROP_TYPE
            LIMIT 10 
            """
        )
        if not type_check.empty:
            has_invalids = len(type_check["INVALID_PROP_TYPE"].dropna()) > 0

            if not has_invalids:  # all properties are ok
                has_ints = any(type_check["IS_INTEGER"])
                has_floats = any(type_check["IS_FLOAT"])
                has_lists_float = any(type_check["IS_LIST_FLOAT"])
                has_lists_int = any(type_check["IS_LIST_INTEGER"])
                has_lists = has_lists_float or has_lists_int
                has_nums = has_ints or has_floats
                if has_nums and not has_lists:
                    if has_floats:
                        projectable_properties[node_properties[i]] = "FLOAT"
                    else:
                        projectable_properties[node_properties[i]] = "INTEGER"
                if has_lists and not has_nums:
                    if has_lists_float:
                        projectable_properties[node_properties[i]] = "FLOAT_LIST"
                    else:
                        projectable_properties[node_properties[i]] = "INTEGER_LIST"

    return projectable_properties


def create_source_projection_properties(projectable_properties):
    return create_projection_properties(projectable_properties, "n")


def create_target_projection_properties(projectable_properties):
    return create_projection_properties(projectable_properties, "m")


def create_projection_properties(projectable_properties, variable):
    valid_node_properties = {}
    for prop in projectable_properties:
        property_type = projectable_properties[prop]
        if property_type == "FLOAT_LIST":
            valid_node_properties[prop] = f"toFloatList({variable}. {prop})"
        elif property_type == "FLOAT":
            valid_node_properties[prop] = f"toFloat({variable}. {prop})"
        elif property_type == "INTEGER_LIST" or property_type == "INTEGER":
            valid_node_properties[prop] = f"{variable}. {prop}"
        else:
            raise "should never end up here"

    node_prop_map = ", ".join(
        f"{prop}: {expr}" for prop, expr in valid_node_properties.items()
    )
    return node_prop_map
