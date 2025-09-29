from graphdatascience import GraphDataScience
import uuid
from contextlib import contextmanager
import logging


logger = logging.getLogger("mcp_server_neo4j_gds")


@contextmanager
def projected_graph_from_params(gds, node_labels=None, undirected=False, **kwargs):
    """
    Project a graph from the database, delegating to projected_graph.

    Supports both:
    - Positional node_labels as the 2nd argument.
    - nodeLabels/relTypes passed either directly as kwargs or nested under a 'kwargs' dict.

    Returns the projected GDS graph. The caller is responsible for dropping it
    (e.g., gds.graph.drop(G)).
    """
    # Unwrap if the caller passed a nested 'kwargs' dict
    params = (
        kwargs.get("kwargs")
        if "kwargs" in kwargs and isinstance(kwargs.get("kwargs"), dict)
        else kwargs
    )

    # Prefer explicit node_labels positional arg, fall back to params["nodeLabels"]
    nodeLabels = params.get("nodeLabels", node_labels)
    relTypes = params.get("relTypes")

    with projected_graph(
        gds, node_labels=nodeLabels, relationship_types=relTypes, undirected=undirected
    ) as G:
        yield G


@contextmanager
def projected_graph(gds, node_labels=None, relationship_types=None, undirected=False):
    """
    Project a graph from the database.

    Args:
        gds: GraphDataScience instance
        node_labels: specifies node labels to project. If empty, all nodes are projected. Default is []
        relationship_types: specifies relationship types to project. If empty, all relationships are projected. Default is [].
        undirected: If True, project as undirected graph. Default is False (directed).
    """
    if relationship_types is None:
        relationship_types = []
    if node_labels is None:
        node_labels = []

    graph_name = f"temp_graph_{uuid.uuid4().hex[:8]}"

    try:
        # Get relationship properties (non-string)
        rel_properties = get_relationship_properties_keys(gds, relationship_types)
        valid_rel_properties = validate_rel_properties(
            gds, rel_properties, node_labels, relationship_types
        )
        rel_prop_map = ", ".join(f"{prop}: r.{prop}" for prop in valid_rel_properties)

        # Get node properties and validate to see which are compatible with GDS
        node_properties = get_node_properties_keys(gds, node_labels)
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
        match_proj_query = create_projection_query(node_labels, relationship_types)

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
                WITH DISTINCT labels(n) AS labels
                UNWIND labels AS label
                WITH DISTINCT label
                RETURN COLLECT(label) AS labels
            """
    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["labels"].iloc[0]


def count_nodes(gds: GraphDataScience):
    with projected_graph(gds) as G:
        return G.node_count()


def get_node_properties_keys(gds: GraphDataScience, node_labels=None):
    if node_labels is None:
        node_labels = []
    nodelabels_query = create_node_cypher_match_query(node_labels)
    property_extractor = """
                            WITH keys(properties(n)) AS prop_keys_list
                            UNWIND prop_keys_list AS prop_keys
                            WITH DISTINCT prop_keys
                            RETURN COLLECT(prop_keys) AS properties_keys
                        """

    query = nodelabels_query + property_extractor
    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["properties_keys"].iloc[0]


def get_relationship_properties_keys(gds: GraphDataScience, relationshipTypes=None):
    if relationshipTypes is None:
        relationshipTypes = []
    rel_query = create_relationship_cypher_match_query([], relationshipTypes)
    property_extractor = """
                            WITH keys(properties(r)) AS prop_keys_list
                            UNWIND prop_keys_list AS prop_keys
                            WITH DISTINCT prop_keys
                            RETURN COLLECT(prop_keys) AS properties_keys
                        """
    query = rel_query + property_extractor

    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["properties_keys"].iloc[0]


def get_relationship_types(gds: GraphDataScience):
    node_labels = []
    type_extractor = """
                     WITH type(r) AS type
                     WITH DISTINCT type
                     RETURN COLLECT(type) AS relationship_types
                     """
    query = create_relationship_cypher_match_query(node_labels, []) + type_extractor

    df = gds.run_cypher(query)
    if df.empty:
        return []
    return df["relationship_types"].iloc[0]


def create_projection_query(node_labels, rel_types):
    node_query = create_node_cypher_match_query(node_labels)
    rel_query = create_relationship_cypher_match_query(node_labels, rel_types)
    match_proj_query = f"{node_query} OPTIONAL {rel_query}"
    return match_proj_query


def create_node_cypher_match_query(node_labels):
    if len(node_labels) > 0:
        match_query = f"MATCH (n) WHERE ANY(l IN labels(n) WHERE l IN {node_labels})"
    else:
        match_query = "MATCH (n)"
    return match_query


def create_relationship_cypher_match_query(node_labels, relationship_types):
    label_constraint = f"ANY(l IN labels(n) WHERE l IN {node_labels}) AND ANY(l IN labels(m) WHERE l IN {node_labels})"
    type_constraint = f"type(r) IN {relationship_types}"
    match_query = "MATCH (n)-[r]->(m)"
    if len(node_labels) > 0 and len(relationship_types) > 0:
        return match_query + f" WHERE {label_constraint} AND {type_constraint}"
    elif len(relationship_types) > 0:
        return match_query + f" WHERE {type_constraint}"
    elif len(node_labels) > 0:
        return match_query + f" WHERE {label_constraint}"
    else:
        return match_query


def validate_rel_properties(
    gds: GraphDataScience, rel_properties, node_labels=None, rel_types=None
):
    if rel_types is None:
        rel_types = []
    if node_labels is None:
        node_labels = []
    match_rel_query = create_relationship_cypher_match_query(node_labels, rel_types)
    valid_rel_properties = {}
    for i in range(len(rel_properties)):
        pi = gds.run_cypher(
            f"""
            {match_rel_query} 
            WITH r.{rel_properties[i]}  AS prop
            WHERE prop IS NOT NULL
            WITH 
            CASE 
                WHEN prop IS :: FLOAT THEN 1
                WHEN prop IS :: INTEGER THEN 1
            ELSE 2
            END AS INVALID_PROP_TYPE
            RETURN distinct(INVALID_PROP_TYPE)
            """
        )
        if pi.shape[0] == 1 and int(pi["INVALID_PROP_TYPE"][0]) == 1:
            valid_rel_properties[rel_properties[i]] = f"toFloat(r.{rel_properties[i]}"
    return valid_rel_properties


def validate_node_properties(gds: GraphDataScience, node_properties, node_labels=None):
    if node_labels is None:
        node_labels = []
    projectable_properties = {}

    for i in range(len(node_properties)):
        # Check property types and whether all values are whole numbers
        match_node_query = create_node_cypher_match_query(node_labels)

        type_check = gds.run_cypher(
            f"""
            {match_node_query}
            WITH n.{node_properties[i]} AS prop
            WHERE prop IS NOT NULL
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
    return create_node_projection_properties(projectable_properties, "n")


def create_target_projection_properties(projectable_properties):
    return create_node_projection_properties(projectable_properties, "m")


def create_node_projection_properties(projectable_properties, variable):
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
