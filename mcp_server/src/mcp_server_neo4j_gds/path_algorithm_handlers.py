import logging
import re
from typing import Dict, Any


from .algorithm_handler import AlgorithmHandler, clean_params

logger = logging.getLogger("mcp_server_neo4j_gds")

# Cypher identifiers that can be used without backtick quoting must match
# this shape. We use it to reject node_identifier_property values that
# would otherwise be interpolated as raw Cypher fragments into the
# `n.<property>` accessor and could break out of the surrounding query.
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_property_name(name):
    """Validate a Cypher property name supplied by the MCP client.

    The ``nodeIdentifierProperty`` tool argument is interpolated directly
    into Cypher queries (``n.<name>``). Without validation a crafted
    value can break out of the property accessor and execute arbitrary
    Cypher. Restricting it to unquoted-identifier shape preserves the
    documented contract ("e.g. 'name', 'Name', 'title'") while making
    injection impossible.
    """
    if not isinstance(name, str) or not _IDENTIFIER_RE.match(name):
        raise ValueError(
            "Invalid nodeIdentifierProperty: must match "
            "[A-Za-z_][A-Za-z0-9_]* (e.g. 'name', 'Name', 'title')."
        )
    return name


def _as_node_pairs(gds, node_id_pairs):
    node_ids = [node_id for pair in node_id_pairs for node_id in pair]
    if not node_ids:
        return []
    nodes = iter(gds.util.asNodes(node_ids))
    return list(zip(nodes, nodes))


class DijkstraShortestPathHandler(AlgorithmHandler):
    def find_shortest_path(
        self, start_node: str, end_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        query = f"""
        MATCH (start)
        WHERE toLower(start.{node_identifier_property}) CONTAINS toLower($start_name)
        MATCH (end)
        WHERE toLower(end.{node_identifier_property}) CONTAINS toLower($end_name)
        RETURN id(start) as start_id, id(end) as end_id
        """

        df = self.gds.run_cypher(
            query, params={"start_name": start_node, "end_name": end_node}
        )

        if df.empty:
            return {"found": False, "message": "One or both node names not found"}

        start_node_id = int(df["start_id"].iloc[0])
        end_node_id = int(df["end_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"Dijkstra single-source shortest path parameters: {params}")

        if mode == "mutate":
            result = self.gds.shortestPath.dijkstra.mutate(
                G, sourceNode=start_node_id, targetNode=end_node_id, **params
            )
        else:
            path_data = self.gds.shortestPath.dijkstra.stream(
                G, sourceNode=start_node_id, targetNode=end_node_id, **params
            )

            if path_data.empty:
                return {
                    "found": False,
                    "message": "No path found between the specified nodes",
                }

            # Convert to native Python types as needed - handle both list and Series objects
            node_ids = path_data["nodeIds"].iloc[0]
            costs = path_data["costs"].iloc[0]

            # Convert only if not already a list
            if hasattr(node_ids, "tolist"):
                node_ids = node_ids.tolist()
            if hasattr(costs, "tolist"):
                costs = costs.tolist()

            # Get node names using GDS utility function
            node_names = self.gds.util.asNodes(node_ids)

            return {
                "totalCost": float(path_data["totalCost"].iloc[0]),
                "nodeIds": node_ids,
                "nodeNames": node_names,
                "path": path_data["path"].iloc[0],
                "costs": costs,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.find_shortest_path(
            arguments.get("start_node"),
            arguments.get("end_node"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationship_property"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class DeltaSteppingShortestPathHandler(AlgorithmHandler):
    def delta_stepping_shortest_path(
        self, source_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        df = self.gds.run_cypher(query, params={"source_name": source_node})

        if df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(df["source_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"Delta-Stepping shortest path parameters: {params}")

        if mode == "mutate":
            result = self.gds.allShortestPaths.delta.mutate(
                G, sourceNode=source_node_id, **params
            )
        else:
            path_data = self.gds.allShortestPaths.delta.stream(
                G, sourceNode=source_node_id, **params
            )

            if path_data.empty:
                return {
                    "found": False,
                    "message": "No paths found from the source node",
                }

            # Convert to native Python types as needed
            result_data = []
            for _, row in path_data.iterrows():
                target_node_id = int(row["targetNode"])
                total_cost = float(row["totalCost"])

                # Get the path details
                node_ids = row["nodeIds"]
                costs = row["costs"]
                path = row["path"]

                # Convert to native Python types if needed
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()
                if hasattr(costs, "tolist"):
                    costs = costs.tolist()

                # Get node names using GDS utility function
                target_node_name = self.gds.util.asNode(target_node_id)
                node_names = self.gds.util.asNodes(node_ids)

                result_data.append(
                    {
                        "targetNode": target_node_id,
                        "targetNodeName": target_node_name,
                        "totalCost": total_cost,
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "costs": costs,
                        "path": path,
                    }
                )

            return {
                "found": True,
                "sourceNodeId": source_node_id,
                "sourceNodeName": self.gds.util.asNode(source_node_id),
                "results": result_data,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.delta_stepping_shortest_path(
            arguments.get("sourceNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            delta=arguments.get("delta"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class DijkstraSingleSourceShortestPathHandler(AlgorithmHandler):
    def dijkstra_single_source_shortest_path(
        self, source_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        df = self.gds.run_cypher(query, params={"source_name": source_node})

        if df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(df["source_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"Dijkstra single-source shortest path parameters: {params}")

        if mode == "mutate":
            result = self.gds.allShortestPaths.dijkstra.mutate(
                G, sourceNode=source_node_id, **params
            )
        else:
            path_data = self.gds.allShortestPaths.dijkstra.stream(
                G, sourceNode=source_node_id, **params
            )

            if path_data.empty:
                return {
                    "found": False,
                    "message": "No paths found from the source node",
                }

            # Convert to native Python types as needed
            result_data = []
            for _, row in path_data.iterrows():
                target_node_id = int(row["targetNode"])
                total_cost = float(row["totalCost"])

                # Get the path details
                node_ids = row["nodeIds"]
                costs = row["costs"]
                path = row["path"]

                # Convert to native Python types if needed
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()
                if hasattr(costs, "tolist"):
                    costs = costs.tolist()

                # Get node names using GDS utility function
                target_node_name = self.gds.util.asNode(target_node_id)
                node_names = self.gds.util.asNodes(node_ids)

                result_data.append(
                    {
                        "targetNode": target_node_id,
                        "targetNodeName": target_node_name,
                        "totalCost": total_cost,
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "costs": costs,
                        "path": path,
                    }
                )

            return {
                "found": True,
                "sourceNodeId": source_node_id,
                "sourceNodeName": self.gds.util.asNode(source_node_id),
                "results": result_data,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.dijkstra_single_source_shortest_path(
            arguments.get("sourceNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class AStarShortestPathHandler(AlgorithmHandler):
    def a_star_shortest_path(
        self,
        source_node: str,
        target_node: str,
        node_identifier_property: str,
        **kwargs,
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        MATCH (target)
        WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
        RETURN id(source) as source_id, id(target) as target_id
        """

        df = self.gds.run_cypher(
            query, params={"source_name": source_node, "target_name": target_node}
        )

        if df.empty:
            return {"found": False, "message": "One or both node names not found"}

        source_node_id = int(df["source_id"].iloc[0])
        target_node_id = int(df["target_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"A* shortest path parameters: {params}")

        if mode == "mutate":
            result = self.gds.shortestPath.astar.mutate(
                G, sourceNode=source_node_id, targetNode=target_node_id, **params
            )
        else:
            path_data = self.gds.shortestPath.astar.stream(
                G, sourceNode=source_node_id, targetNode=target_node_id, **params
            )

            if path_data.empty:
                return {
                    "found": False,
                    "message": "No path found between the specified nodes",
                }

            # Convert to native Python types as needed - handle both list and Series objects
            node_ids = path_data["nodeIds"].iloc[0]
            costs = path_data["costs"].iloc[0]

            # Convert only if not already a list
            if hasattr(node_ids, "tolist"):
                node_ids = node_ids.tolist()
            if hasattr(costs, "tolist"):
                costs = costs.tolist()

            # Get node names using GDS utility function
            node_names = self.gds.util.asNodes(node_ids)

            return {
                "totalCost": float(path_data["totalCost"].iloc[0]),
                "nodeIds": node_ids,
                "nodeNames": node_names,
                "path": path_data["path"].iloc[0],
                "costs": costs,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.a_star_shortest_path(
            arguments.get("sourceNode"),
            arguments.get("targetNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            latitudeProperty=arguments.get("latitudeProperty"),
            longitudeProperty=arguments.get("longitudeProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class YensShortestPathsHandler(AlgorithmHandler):
    def yens_shortest_paths(
        self,
        source_node: str,
        target_node: str,
        node_identifier_property: str,
        **kwargs,
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        MATCH (target)
        WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
        RETURN id(source) as source_id, id(target) as target_id
        """

        df = self.gds.run_cypher(
            query, params={"source_name": source_node, "target_name": target_node}
        )

        if df.empty:
            return {"found": False, "message": "One or both node names not found"}

        source_node_id = int(df["source_id"].iloc[0])
        target_node_id = int(df["target_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"Yen's shortest paths parameters: {params}")

        if mode == "mutate":
            result = self.gds.shortestPath.yens.mutate(
                G, sourceNode=source_node_id, targetNode=target_node_id, **params
            )
        else:
            path_data = self.gds.shortestPath.yens.stream(
                G, sourceNode=source_node_id, targetNode=target_node_id, **params
            )

            if path_data.empty:
                return {
                    "found": False,
                    "message": "No paths found between the specified nodes",
                }

            # Convert to native Python types as needed
            result_data = []
            for _, row in path_data.iterrows():
                # Convert to native Python types as needed - handle both list and Series objects
                node_ids = row["nodeIds"]
                costs = row["costs"]

                # Convert only if not already a list
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()
                if hasattr(costs, "tolist"):
                    costs = costs.tolist()

                # Get node names using GDS utility function
                node_names = self.gds.util.asNodes(node_ids)

                result_data.append(
                    {
                        "index": int(row["index"]),
                        "totalCost": float(row["totalCost"]),
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "path": row["path"],
                        "costs": costs,
                    }
                )

            return {
                "found": True,
                "sourceNodeId": source_node_id,
                "sourceNodeName": self.gds.util.asNode(source_node_id),
                "targetNodeId": target_node_id,
                "targetNodeName": self.gds.util.asNode(target_node_id),
                "results": result_data,
                "totalResults": len(result_data),
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.yens_shortest_paths(
            arguments.get("sourceNode"),
            arguments.get("targetNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            k=arguments.get("k"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class MinimumWeightSpanningTreeHandler(AlgorithmHandler):
    def minimum_weight_spanning_tree(
        self, source_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        df = self.gds.run_cypher(query, params={"source_name": source_node})

        if df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(df["source_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"Minimum Weight Spanning Tree parameters: {params}")

        if mode == "mutate":
            result = self.gds.spanningTree.mutate(
                G, sourceNode=source_node_id, **params
            )
        else:
            mst_data = self.gds.spanningTree.stream(
                G, sourceNode=source_node_id, **params
            )

            if mst_data.empty:
                return {
                    "found": False,
                    "message": "No spanning tree found from the source node",
                }

            # Convert to native Python types as needed
            edge_rows = []
            total_weight = 0.0

            for _, row in mst_data.iterrows():
                node_id = int(row["nodeId"])
                parent_id = int(row["parentId"])
                weight = float(row["weight"])

                # Skip the root node (where nodeId == parentId)
                if node_id == parent_id:
                    continue

                total_weight += weight

                edge_rows.append((node_id, parent_id, weight))

            node_pairs = _as_node_pairs(
                self.gds, [(node_id, parent_id) for node_id, parent_id, _ in edge_rows]
            )

            edges = []
            for (node_id, parent_id, weight), (node_name, parent_name) in zip(
                edge_rows, node_pairs
            ):
                edges.append(
                    {
                        "nodeId": node_id,
                        "parentId": parent_id,
                        "nodeName": node_name,
                        "parentName": parent_name,
                        "weight": weight,
                    }
                )

            return {
                "found": True,
                "totalWeight": total_weight,
                "edges": edges,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.minimum_weight_spanning_tree(
            arguments.get("sourceNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            objective=arguments.get("objective"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class MinimumDirectedSteinerTreeHandler(AlgorithmHandler):
    def minimum_directed_steiner_tree(
        self,
        source_node: str,
        target_nodes: list,
        node_identifier_property: str,
        **kwargs,
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        # Find source node ID
        source_query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        source_df = self.gds.run_cypher(
            source_query, params={"source_name": source_node}
        )

        if source_df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(source_df["source_id"].iloc[0])

        # Find target node IDs - ensure ALL target nodes are found
        target_node_ids = []
        target_node_names = []
        unmatched_targets = []

        for target_name in target_nodes:
            target_query = f"""
            MATCH (target)
            WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
            RETURN id(target) as target_id, target.{node_identifier_property} as target_name
            """

            target_df = self.gds.run_cypher(
                target_query, params={"target_name": target_name}
            )

            if not target_df.empty:
                target_node_ids.append(int(target_df["target_id"].iloc[0]))
                target_node_names.append(target_df["target_name"].iloc[0])
            else:
                unmatched_targets.append(target_name)

        # Check if all target nodes were found
        if unmatched_targets:
            return {
                "found": False,
                "message": f"The following target nodes were not found: {', '.join(unmatched_targets)}",
            }

        if not target_node_ids:
            return {"found": False, "message": "No target nodes found"}

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName"])
        logger.info(f"Minimum Directed Steiner Tree parameters: {params}")

        # Run the steiner tree algorithm
        steiner_data = self.gds.steinerTree.stream(
            G, sourceNode=source_node_id, targetNodes=target_node_ids, **params
        )

        if steiner_data.empty:
            return {
                "found": False,
                "message": "No steiner tree found connecting the source to all target nodes",
            }

        # Convert to native Python types as needed
        edge_rows = []
        total_weight = 0.0

        for _, row in steiner_data.iterrows():
            node_id = int(row["nodeId"])
            parent_id = int(row["parentId"])
            weight = float(row["weight"])

            # Skip the root node (where nodeId == parentId)
            if node_id == parent_id:
                continue

            total_weight += weight

            edge_rows.append((node_id, parent_id, weight))

        node_pairs = _as_node_pairs(
            self.gds, [(node_id, parent_id) for node_id, parent_id, _ in edge_rows]
        )

        edges = []
        for (node_id, parent_id, weight), (node_name, parent_name) in zip(
            edge_rows, node_pairs
        ):
            edges.append(
                {
                    "nodeId": node_id,
                    "parentId": parent_id,
                    "nodeName": node_name,
                    "parentName": parent_name,
                    "weight": weight,
                }
            )

        return {
            "found": True,
            "totalWeight": total_weight,
            "edges": edges,
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.minimum_directed_steiner_tree(
            arguments.get("sourceNode"),
            arguments.get("targetNodes"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            delta=arguments.get("delta"),
            applyRerouting=arguments.get("applyRerouting"),
        )


class PrizeCollectingSteinerTreeHandler(AlgorithmHandler):
    def prize_collecting_steiner_tree(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName"])
        logger.info(f"Prize-Collecting Steiner Tree parameters: {params}")

        # Run the prize-collecting steiner tree algorithm
        steiner_data = self.gds.prizeSteinerTree.stream(G, **params)

        if steiner_data.empty:
            return {
                "found": False,
                "message": "No prize-collecting steiner tree found",
            }

        # Convert to native Python types as needed
        edge_rows = []
        total_weight = 0.0

        for _, row in steiner_data.iterrows():
            node_id = int(row["nodeId"])
            parent_id = int(row["parentId"])
            weight = float(row["weight"])

            # Skip the root node (where nodeId == parentId)
            if node_id == parent_id:
                continue

            total_weight += weight

            edge_rows.append((node_id, parent_id, weight))

        node_pairs = _as_node_pairs(
            self.gds, [(node_id, parent_id) for node_id, parent_id, _ in edge_rows]
        )

        edges = []
        for (node_id, parent_id, weight), (node_name, parent_name) in zip(
            edge_rows, node_pairs
        ):
            edges.append(
                {
                    "nodeId": node_id,
                    "parentId": parent_id,
                    "nodeName": node_name,
                    "parentName": parent_name,
                    "weight": weight,
                }
            )

        return {
            "found": True,
            "totalWeight": total_weight,
            "edges": edges,
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.prize_collecting_steiner_tree(
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            prizeProperty=arguments.get("prizeProperty"),
        )


class AllPairsShortestPathsHandler(AlgorithmHandler):
    def all_pairs_shortest_paths(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName"])
        logger.info(f"All Pairs Shortest Paths parameters: {params}")

        # Run the all pairs shortest paths algorithm
        apsp_data = self.gds.allShortestPaths.stream(G, **params)

        if apsp_data.empty:
            return {"found": False, "message": "No shortest paths found"}

        # Get node names using GDS utility function (batch operation)
        apsp_data["sourceNodeName"] = self.gds.util.asNodes(
            apsp_data["sourceNodeId"].tolist()
        )
        apsp_data["targetNodeName"] = self.gds.util.asNodes(
            apsp_data["targetNodeId"].tolist()
        )

        # Convert to list of dictionaries
        paths = apsp_data[
            [
                "sourceNodeId",
                "targetNodeId",
                "sourceNodeName",
                "targetNodeName",
                "distance",
            ]
        ].to_dict("records")

        return {
            "found": True,
            "paths": paths,
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.all_pairs_shortest_paths(
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class RandomWalkHandler(AlgorithmHandler):
    def random_walk(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        # Process source nodes if provided
        source_node_ids = []
        if "sourceNodes" in kwargs and kwargs["sourceNodes"]:
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            if not node_identifier_property:
                return {
                    "found": False,
                    "message": "nodeIdentifierProperty is required when sourceNodes are provided",
                }
            node_identifier_property = _validate_property_name(node_identifier_property)

            for source_name in kwargs["sourceNodes"]:
                source_query = f"""
                MATCH (source)
                WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
                RETURN id(source) as source_id
                """

                source_df = self.gds.run_cypher(
                    source_query, params={"source_name": source_name}
                )

                if not source_df.empty:
                    source_node_ids.append(int(source_df["source_id"].iloc[0]))

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty", "mode"])
        logger.info(f"Random Walk parameters: {params}")

        # Add source nodes if found
        if source_node_ids:
            params["sourceNodes"] = source_node_ids

        logger.info(f"Random Walk parameters: {params}")

        if mode == "mutate":
            result = self.gds.randomWalk.mutate(G, **params)
        else:
            # Run the random walk algorithm
            walk_data = self.gds.randomWalk.stream(G, **params)

            if walk_data.empty:
                return {"found": False, "message": "No random walks generated"}

            # Convert to native Python types as needed
            walks = []

            for _, row in walk_data.iterrows():
                node_ids = row["nodeIds"]
                # Convert node_ids to list if it's not already
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()

                # Get node names using GDS utility function
                node_names = self.gds.util.asNodes(node_ids)

                walks.append(
                    {
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "walkLength": len(node_ids),
                    }
                )

            return {
                "found": True,
                "walks": walks,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.random_walk(
            graphName=arguments.get("graphName"),
            sourceNodes=arguments.get("sourceNodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            walkLength=arguments.get("walkLength"),
            walksPerNode=arguments.get("walksPerNode"),
            inOutFactor=arguments.get("inOutFactor"),
            returnFactor=arguments.get("returnFactor"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            walkBufferSize=arguments.get("walkBufferSize"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
        )


class BreadthFirstSearchHandler(AlgorithmHandler):
    def breadth_first_search(
        self, source_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        # Find source node ID
        source_query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        source_df = self.gds.run_cypher(
            source_query, params={"source_name": source_node}
        )

        if source_df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(source_df["source_id"].iloc[0])

        # Process target nodes if provided
        target_node_ids = []
        if "targetNodes" in kwargs and kwargs["targetNodes"]:
            for target_name in kwargs["targetNodes"]:
                target_query = f"""
                MATCH (target)
                WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
                RETURN id(target) as target_id
                """

                target_df = self.gds.run_cypher(
                    target_query, params={"target_name": target_name}
                )

                if not target_df.empty:
                    target_node_ids.append(int(target_df["target_id"].iloc[0]))

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty", "mode"])

        # Add target nodes if found
        if target_node_ids:
            params["targetNodes"] = target_node_ids

        logger.info(f"Breadth First Search parameters: {params}")

        if mode == "mutate":
            result = self.gds.bfs.mutate(G, sourceNode=source_node_id, **params)
        else:
            # Run the breadth first search algorithm
            bfs_data = self.gds.bfs.stream(G, sourceNode=source_node_id, **params)

            if bfs_data.empty:
                return {
                    "found": False,
                    "message": "No nodes visited in breadth first search",
                }

            # Convert to native Python types as needed
            traversals = []

            for _, row in bfs_data.iterrows():
                source_node = int(row["sourceNode"])
                node_ids = row["nodeIds"]

                # Convert node_ids to list if it's not already
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()

                # Get node names using GDS utility function
                node_names = self.gds.util.asNodes(node_ids)

                traversals.append(
                    {
                        "sourceNode": source_node,
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "visitedNodes": len(node_ids),
                    }
                )

            return {
                "found": True,
                "traversals": traversals,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.breadth_first_search(
            arguments.get("sourceNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            targetNodes=arguments.get("targetNodes"),
            maxDepth=arguments.get("maxDepth"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class DepthFirstSearchHandler(AlgorithmHandler):
    def depth_first_search(
        self, source_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        # Find source node ID
        source_query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        source_df = self.gds.run_cypher(
            source_query, params={"source_name": source_node}
        )

        if source_df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(source_df["source_id"].iloc[0])

        # Process target nodes if provided
        target_node_ids = []
        if "targetNodes" in kwargs and kwargs["targetNodes"]:
            for target_name in kwargs["targetNodes"]:
                target_query = f"""
                MATCH (target)
                WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
                RETURN id(target) as target_id
                """

                target_df = self.gds.run_cypher(
                    target_query, params={"target_name": target_name}
                )

                if not target_df.empty:
                    target_node_ids.append(int(target_df["target_id"].iloc[0]))

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty", "mode"])
        # Add target nodes if found
        if target_node_ids:
            params["targetNodes"] = target_node_ids

        logger.info(f"Depth First Search parameters: {params}")

        if mode == "mutate":
            result = self.gds.dfs.mutate(G, sourceNode=source_node_id, **params)
        else:
            # Run the depth first search algorithm
            dfs_data = self.gds.dfs.stream(G, sourceNode=source_node_id, **params)

            if dfs_data.empty:
                return {
                    "found": False,
                    "message": "No nodes visited in depth first search",
                }

            # Convert to native Python types as needed
            traversals = []

            for _, row in dfs_data.iterrows():
                source_node = int(row["sourceNode"])
                node_ids = row["nodeIds"]

                # Convert node_ids to list if it's not already
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()

                # Get node names using GDS utility function
                node_names = self.gds.util.asNodes(node_ids)

                traversals.append(
                    {
                        "sourceNode": source_node,
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "visitedNodes": len(node_ids),
                    }
                )

            return {
                "found": True,
                "traversals": traversals,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.depth_first_search(
            arguments.get("sourceNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            targetNodes=arguments.get("targetNodes"),
            maxDepth=arguments.get("maxDepth"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class BellmanFordSingleSourceShortestPathHandler(AlgorithmHandler):
    def bellman_ford_single_source_shortest_path(
        self, source_node: str, node_identifier_property: str, **kwargs
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        # Find source node ID
        source_query = f"""
        MATCH (source)
        WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
        RETURN id(source) as source_id
        """

        source_df = self.gds.run_cypher(
            source_query, params={"source_name": source_node}
        )

        if source_df.empty:
            return {"found": False, "message": "Source node name not found"}

        source_node_id = int(source_df["source_id"].iloc[0])

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "nodeIdentifierProperty", "mode"])
        logger.info(f"Bellman-Ford Single-Source Shortest Path parameters: {params}")

        if mode == "mutate":
            result = self.gds.bellmanFord.mutate(G, sourceNode=source_node_id, **params)
        else:
            # Run the Bellman-Ford algorithm
            bellman_ford_data = self.gds.bellmanFord.stream(
                G, sourceNode=source_node_id, **params
            )

            if bellman_ford_data.empty:
                return {
                    "found": False,
                    "message": "No paths found from the source node",
                }

            # Convert to native Python types as needed
            paths = []

            for _, row in bellman_ford_data.iterrows():
                index = int(row["index"])
                source_node = int(row["sourceNode"])
                target_node = int(row["targetNode"])
                total_cost = float(row["totalCost"])
                node_ids = row["nodeIds"]
                costs = row["costs"]
                is_negative_cycle = bool(row["isNegativeCycle"])

                # Convert arrays to lists if needed
                if hasattr(node_ids, "tolist"):
                    node_ids = node_ids.tolist()
                if hasattr(costs, "tolist"):
                    costs = costs.tolist()

                # Get node names using GDS utility function
                node_names = self.gds.util.asNodes(node_ids)

                paths.append(
                    {
                        "index": index,
                        "sourceNode": source_node,
                        "targetNode": target_node,
                        "totalCost": total_cost,
                        "nodeIds": node_ids,
                        "nodeNames": node_names,
                        "costs": costs,
                        "isNegativeCycle": is_negative_cycle,
                    }
                )

            return {
                "found": True,
                "paths": paths,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.bellman_ford_single_source_shortest_path(
            arguments.get("sourceNode"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            mode=arguments.get("mode"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )


class LongestPathHandler(AlgorithmHandler):
    def longest_path(self, **kwargs):
        # Process target nodes if provided
        target_node_ids = []
        if "targetNodes" in kwargs and kwargs["targetNodes"]:
            node_identifier_property = kwargs.get("nodeIdentifierProperty")
            if not node_identifier_property:
                return {
                    "found": False,
                    "message": "nodeIdentifierProperty is required when targetNodes are provided",
                }
            node_identifier_property = _validate_property_name(node_identifier_property)

            for target_name in kwargs["targetNodes"]:
                target_query = f"""
                MATCH (target)
                WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
                RETURN id(target) as target_id
                """
                target_df = self.gds.run_cypher(
                    target_query, params={"target_name": target_name}
                )
                if not target_df.empty:
                    target_node_ids.append(int(target_df["target_id"].iloc[0]))
        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(
            kwargs,
            ["graphName", "nodeIdentifierProperty", "targetNodes"],
        )
        logger.info(f"Longest Path parameters: {params}")

        # Run the longest path algorithm
        longest_path_data = self.gds.dag.longestPath.stream(G, **params)

        if longest_path_data.empty:
            return {
                "found": False,
                "message": "No longest paths found. The graph may contain cycles or be empty.",
            }

        # Convert to native Python types as needed
        paths = []

        for _, row in longest_path_data.iterrows():
            index = int(row["index"])
            source_node = int(row["sourceNode"])
            target_node = int(row["targetNode"])
            total_cost = float(row["totalCost"])
            node_ids = row["nodeIds"]
            costs = row["costs"]

            # Filter by target nodes if specified
            if target_node_ids and target_node not in target_node_ids:
                continue

            # Convert arrays to lists if needed
            if hasattr(node_ids, "tolist"):
                node_ids = node_ids.tolist()
            if hasattr(costs, "tolist"):
                costs = costs.tolist()

            # Get node names using GDS utility function
            node_names = self.gds.util.asNodes(node_ids)

            paths.append(
                {
                    "index": index,
                    "sourceNode": source_node,
                    "targetNode": target_node,
                    "totalCost": total_cost,
                    "nodeIds": node_ids,
                    "nodeNames": node_names,
                    "costs": costs,
                }
            )

        return {
            "found": True,
            "paths": paths,
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.longest_path(
            graphName=arguments.get("graphName"),
            targetNodes=arguments.get("targetNodes"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
        )


class MaxFlowHandler(AlgorithmHandler):
    def max_flow(
        self,
        source_nodes: list,
        target_nodes: list,
        node_identifier_property: str,
        **kwargs,
    ):
        node_identifier_property = _validate_property_name(node_identifier_property)
        mode = kwargs.get("mode", "stream")
        source_node_ids = []
        source_node_names = []
        unmatched_sources = []

        for source_name in source_nodes:
            source_query = f"""
            MATCH (source)
            WHERE toLower(source.{node_identifier_property}) CONTAINS toLower($source_name)
            RETURN id(source) as source_id, source.{node_identifier_property} as source_name
            """

            source_df = self.gds.run_cypher(
                source_query, params={"source_name": source_name}
            )

            if not source_df.empty:
                source_node_ids.append(int(source_df["source_id"].iloc[0]))
                source_node_names.append(source_df["source_name"].iloc[0])
            else:
                unmatched_sources.append(source_name)

        # Check if all source nodes were found
        if unmatched_sources:
            return {
                "found": False,
                "message": f"The following source nodes were not found: {', '.join(unmatched_sources)}",
            }

        if not source_node_ids:
            return {"found": False, "message": "No source nodes found"}

        # Find target node IDs
        target_node_ids = []
        target_node_names = []
        unmatched_targets = []

        for target_name in target_nodes:
            target_query = f"""
            MATCH (target)
            WHERE toLower(target.{node_identifier_property}) CONTAINS toLower($target_name)
            RETURN id(target) as target_id, target.{node_identifier_property} as target_name
            """

            target_df = self.gds.run_cypher(
                target_query, params={"target_name": target_name}
            )

            if not target_df.empty:
                target_node_ids.append(int(target_df["target_id"].iloc[0]))
                target_node_names.append(target_df["target_name"].iloc[0])
            else:
                unmatched_targets.append(target_name)

        # Check if all target nodes were found
        if unmatched_targets:
            return {
                "found": False,
                "message": f"The following target nodes were not found: {', '.join(unmatched_targets)}",
            }

        if not target_node_ids:
            return {"found": False, "message": "No target nodes found"}

        G = self.gds.graph.get(kwargs.get("graphName"))
        params = clean_params(kwargs, ["graphName", "mode"])
        logger.info(f"Max Flow parameters: {params}")

        if mode == "mutate":
            result = self.gds.maxFlow.mutate(
                G, sourceNodes=source_node_ids, targetNodes=target_node_ids, **params
            )
        else:
            max_flow_data = self.gds.maxFlow.stream(
                G, sourceNodes=source_node_ids, targetNodes=target_node_ids, **params
            )

            # Get node names using GDS utility function (batch operation)
            max_flow_data["sourceNodeName"] = self.gds.util.asNodes(
                max_flow_data["source"].tolist()
            )
            max_flow_data["targetNodeName"] = self.gds.util.asNodes(
                max_flow_data["target"].tolist()
            )

            # Convert to list of dictionaries
            flows = max_flow_data[
                [
                    "source",
                    "target",
                    "sourceNodeName",
                    "targetNodeName",
                    "flow",
                ]
            ].to_dict("records")

            return {
                "found": True,
                "flows": flows,
            }

        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.max_flow(
            arguments.get("sourceNodes"),
            arguments.get("targetNodes"),
            arguments.get("nodeIdentifierProperty"),
            graphName=arguments.get("graphName"),
            capacityProperty=arguments.get("capacityProperty"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            mutateRelationshipType=arguments.get("mutateRelationshipType"),
        )
