from graphdatascience import GraphDataScience


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
            # Handle list of node names
            query = f"""
                    UNWIND $names AS name
                    MATCH (s)
                    WHERE toLower(s.{node_identifier_property}) = toLower(name)
                    RETURN id(s) as node_id
                    """
            df = gds.run_cypher(
                query,
                params={
                    "names": input_nodes,
                },
            )
            input_node_ids = df["node_id"].tolist()
            call_params[input_nodes_variable_name] = input_node_ids
        else:
            # Handle single  node name
            query = f"""
                    MATCH (s)
                    WHERE toLower(s.{node_identifier_property}) = toLower($name)
                    RETURN id(s) as node_id
                    """
            df = gds.run_cypher(
                query,
                params={
                    "name": input_nodes,
                },
            )
            if not df.empty:
                call_params[input_nodes_variable_name] = int(df["node_id"].iloc[0])
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
        node_name_values = [
            gds.util.asNode(node_id).get(node_identifier_property)
            for node_id in results[id_name]
        ]
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
    query = f"""
            UNWIND $names AS name
            MATCH (s)
            WHERE toLower(s.{node_identifier_property}) = toLower(name)
            RETURN id(s) as node_id
            """
    df = gds.run_cypher(
        query,
        params={
            "names": node_names,
        },
    )
    return filter_results(df, results, id_name)


def filter_identifiers_pro(
    gds: GraphDataScience,
    node_identifier_property,
    node_names,
    node_labels,
    results,
    id_name="nodeId",
):
    if node_labels is None:
        return filter_identifiers(
            gds, node_identifier_property, node_names, results, id_name
        )

    query = f"""
            UNWIND $labels AS label
            MATCH (s)
            WHERE label IN labels(s) AND s.{node_identifier_property} IS NOT NULL
            WITH DISTINCT s.{node_identifier_property} as node_id
            RETURN COLLECT(node_id) AS node_names 
            """
    df = gds.run_cypher(
        query,
        params={
            "labels": node_labels,
        },
    )
    return filter_identifiers(
        gds, node_identifier_property, df["node_names"].iloc[0], results, id_name
    )


def filter_results(df, results, id_name="nodeId"):
    node_ids = df["node_id"].tolist()
    filtered_results = results[results[id_name].isin(node_ids)]
    return filtered_results
