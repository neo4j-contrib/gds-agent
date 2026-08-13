from graphdatascience import GraphDataScience

from .result_limits import limit_dataframe_rows


def _replace_dataframe_contents(target, source):
    if source is target:
        return

    target.drop(target.index, inplace=True)
    for column in list(target.columns):
        if column not in source.columns:
            target.drop(columns=[column], inplace=True)
    for column in source.columns:
        target[column] = source[column]
    target.attrs.update(source.attrs)


def _to_number(value):
    """Return int/float if value is numeric; otherwise None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        s = value.strip()
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return None
    return None


def _lookup_node_ids(gds, values, property_name):
    """Resolve identifier values to Neo4j ids.

    Numerics use exact ``=`` (toLower fails on number properties).
    Strings use case-insensitive CONTAINS.
    """
    if not isinstance(values, list):
        values = [values]

    numeric_values = []
    string_values = []
    for value in values:
        numeric = _to_number(value)
        if numeric is not None:
            numeric_values.append(numeric)
        else:
            string_values.append(value)

    node_ids = []
    if numeric_values:
        query = f"""
                UNWIND $names AS name
                MATCH (s)
                WHERE s.{property_name} = name
                RETURN id(s) as node_id
                """
        df = gds.run_cypher(query, params={"names": numeric_values})
        node_ids.extend(df["node_id"].tolist())
    if string_values:
        query = f"""
                UNWIND $names AS name
                MATCH (s)
                WHERE toLower(s.{property_name}) CONTAINS toLower(name)
                RETURN id(s) as node_id
                """
        df = gds.run_cypher(query, params={"names": string_values})
        node_ids.extend(df["node_id"].tolist())
    return node_ids


def translate_identifiers_to_ids(
    gds: GraphDataScience,
    input_nodes,
    input_nodes_variable_name,
    node_identifier_property,
    call_params,
):
    # Handle input nodes - convert names to IDs if nodeIdentifierProperty is provided
    if input_nodes is not None and node_identifier_property is not None:
        if isinstance(input_nodes, list):
            call_params[input_nodes_variable_name] = _lookup_node_ids(
                gds, input_nodes, node_identifier_property
            )
        else:
            node_ids = _lookup_node_ids(gds, input_nodes, node_identifier_property)
            if node_ids:
                call_params[input_nodes_variable_name] = int(node_ids[0])
    elif input_nodes is not None:
        # If input_nodes provided but no nodeIdentifierProperty, pass through as-is
        call_params[input_nodes_variable_name] = input_nodes


def translate_ids_to_identifiers(
    gds: GraphDataScience,
    node_identifier_property,
    results,
    id_name="nodeId",
    node_identifier_output_name="nodeName",
):
    if node_identifier_property is not None:
        limited_results = limit_dataframe_rows(results)
        _replace_dataframe_contents(results, limited_results)

        nodes = gds.util.asNodes(results[id_name].tolist())
        node_name_values = [node.get(node_identifier_property) for node in nodes]
        results[node_identifier_output_name] = node_name_values


def filter_identifiers(
    gds: GraphDataScience,
    node_identifier_property,
    node_names,
    results,
    id_name="nodeId",
):
    if node_names is None:
        return results
    if node_identifier_property is None:
        raise ValueError(
            "If 'nodes' is provided, 'nodeIdentifierProperty' must also be specified."
        )
    node_ids = _lookup_node_ids(gds, node_names, node_identifier_property)
    filtered_results = results[results[id_name].isin(node_ids)]
    return filtered_results
