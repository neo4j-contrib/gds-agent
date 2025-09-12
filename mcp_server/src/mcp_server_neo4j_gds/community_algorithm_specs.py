from mcp import types

community_tool_definitions = [
    types.Tool(
        name="conductance",
        description="""Calculate the conductance metric for all communities""",
        inputSchema={
            "type": "object",
            "properties": {
                "communityProperty": {
                    "type": "string",
                    "description": "The node property that holds the community ID as an integer for each node. "
                    "Note that only non-negative community IDs are considered valid and will have their conductance computed.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "The relationship property that holds the weight of the relationships. "
                    "If not provided, all relationships are considered to have a weight of 1.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run conductance on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
            "required": ["communityProperty"],
        },
    ),
    types.Tool(
        name="HDBSCAN",
        description="Perform HDBSCAN clustering on the graph. HDBSCAN, which stands for Hierarchical Density-Based Spatial Clustering of Applications with Noise, "
        "is a clustering algorithm used to identify clusters of similar data points within a dataset. "
        "It builds upon the DBSCAN algorithm but adds a hierarchical structure, making it more robust to varying densities within the data. "
        "Unlike DBSCAN, HDBSCAN does not require tuning a specific density parameter; "
        "instead, it runs DBSCAN over a range of parameters, creating a hierarchy of clusters. "
        "This hierarchical approach allows HDBSCAN to find clusters of varying densities and to be more adaptable to real-world data.HDBSCAN is known for its ease of use, "
        "noise tolerance, and ability to handle data with varying densities, making it a versatile tool for clustering tasks, "
        "especially when dealing with complex, high-dimensional datasets.",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeProperty": {
                    "type": "string",
                    "description": "A node property corresponding to an array of floats used by HDBSCAN to compute clusters",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "minClusterSize": {
                    "type": "integer",
                    "description": "The minimum number of nodes that a cluster should contain.",
                },
                "samples": {
                    "type": "integer",
                    "description": "The number of neighbours to be considered when computing the core distances of a node.",
                },
                "leafSize": {
                    "type": "integer",
                    "description": "The number of leaf nodes of the supporting tree data structure.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run HDBSCAN on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
            "required": ["nodeProperty"],
        },
    ),
    types.Tool(
        name="k_core_decomposition",
        description="The K-core decomposition constitutes a process of separates the nodes in a graph into groups based on the degree sequence and topology of the graph. "
        "The term i-core refers to a maximal subgraph of the original graph such that each node in this subgraph has degree at least i. "
        "The maximality ensures that it is not possible to find another subgraph with more nodes where this degree property holds. "
        "The nodes in the subgraph denoted by i-core also belong to the subgraph denoted by j-core for any j<i. The converse however is not true.  "
        "Each node u is associated with a core value which denotes the largest value i such that u belongs to the i-core. "
        "The largest core value is called the degeneracy of the graph.Standard algorithms for K-Core Decomposition iteratively remove the node of lowest degree until the graph becomes empty. "
        "When a node is removed from the graph, all of its relationships are removed, and the degree of its neighbors is reduced by one. "
        "With this approach, the different core groups are discovered one-by-one.",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run K Core decomposition on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="k_1_coloring",
        description="The K-1 Coloring algorithm assigns a color to every node in the graph, "
        "trying to optimize for two objectives: "
        "1. To make sure that every neighbor of a given node has a different color than the node itself. "
        "2. To use as few colors as possible. "
        "Note that the graph coloring problem is proven to be NP-complete, which makes it intractable on anything but trivial graph sizes. "
        "For that reason the implemented algorithm is a greedy algorithm. "
        "Thus it is neither guaranteed that the result is an optimal solution, using as few colors as theoretically possible, "
        "nor does it always produce a correct result where no two neighboring nodes have different colors. "
        "However the precision of the latter can be controlled by the number of iterations this algorithm runs.",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run K-1 Coloring on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "maxIterations": {
                    "type": "integer",
                    "description": "The maximum number of iterations to run the coloring algorithm.",
                },
                "minCommunitySize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
            },
            "required": [],
        },
    ),
    types.Tool(
        name="k_means_clustering",
        description="K-Means clustering is an unsupervised learning algorithm that is used to solve clustering problems. "
        "It follows a simple procedure of classifying a given data set into a number of clusters, defined by the parameter k. "
        "The Neo4j GDS Library conducts clustering based on node properties, with a float array node property being passed as input via the nodeProperty parameter. "
        "Nodes in the graph are then positioned as points in a d-dimensional space (where d is the length of the array property). "
        "The algorithm then begins by selecting k initial cluster centroids, which are d-dimensional arrays (see section below for more details). "
        "The centroids act as representatives for a cluster. "
        "Then, all nodes in the graph calculate their Euclidean distance from each of the cluster centroids and are assigned to the cluster of minimum distance from them. "
        "After these assignments, each cluster takes the mean of all nodes (as points) assigned to it to form its new representative centroid (as a d-dimensional array). "
        "The process repeats with the new centroids until results stabilize, i.e., only a few nodes change clusters per iteration or the number of maximum iterations is reached. "
        "Note that the K-Means implementation ignores relationships as it is only focused on node properties.",
        inputSchema={
            "type": "object",
            "properties": {
                "nodeProperty": {
                    "type": "string",
                    "description": "A node property corresponding to an array of floats used by K-Means to cluster nodes into communities.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "Property name to use for identifying nodes (e.g., 'name', 'Name', 'title'). Use get_node_properties_keys to find available properties.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run K-Means on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
                "k": {
                    "type": "integer",
                    "description": "The number of clusters to create.",
                },
                "maxIterations": {
                    "type": "integer",
                    "description": "The maximum number of iterations the algorithm will run.",
                },
                "deltaThreshold": {
                    "type": "number",
                    "description": "Value as a percentage to determine when to stop early. If fewer than 'deltaThreshold * |nodes|' nodes change their cluster , the algorithm stops. Value must be between 0 (exclusive) and 1 (inclusive).",
                },
                "numberOfRestarts": {
                    "type": "integer",
                    "description": "Number of times to execute K-Means with different initial centers. The communities returned are those minimizing the average node-center distances.",
                },
                "initialSampler": {
                    "type": "string",
                    "enum": ["uniform", "kmeans++"],
                    "description": "The method used to sample the first k centroids. 'uniform' and 'kmeans++', both case-insensitive, are valid inputs.",
                },
                "seedCentroids": {
                    "type": "array",
                    "items": {"type": "array", "items": {"type": "number"}},
                    "description": "Parameter to explicitly give the initial centroids. It cannot be enabled together with a non-default value of the numberOfRestarts parameter.",
                },
                "computeSilhouette": {
                    "type": "boolean",
                    "description": "If set to true, the silhouette scores are computed once the clustering has been determined. Silhouette is a metric on how well the nodes have been clustered.",
                },
            },
            "required": ["nodeProperty"],
        },
    ),
    types.Tool(
        name="label_propagation",
        description="The Label Propagation algorithm (LPA) is a fast algorithm for finding communities in a graph. "
        "It detects these communities using network structure alone as its guide, and doesn't require a pre-defined objective function or prior information about the communities. "
        "LPA works by propagating labels throughout the network and forming communities based on this process of label propagation.",
        inputSchema={
            "type": "object",
            "properties": {
                "maxIterations": {
                    "type": "integer",
                    "description": "The maximum number of iterations to run.",
                },
                "nodeWeightProperty": {
                    "type": "string",
                    "description": "The name of a node property that contains node weights.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "seedProperty": {
                    "type": "string",
                    "description": "The name of a node property that defines an initial numeric label.",
                },
                "consecutiveIds": {
                    "type": "boolean",
                    "description": "Flag to decide whether component identifiers are mapped into a consecutive id space (requires additional memory).",
                },
                "minCommunitySize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Label Propagation on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="leiden",
        description="The Leiden algorithm is an algorithm for detecting communities in large networks. "
        "The algorithm separates nodes into disjoint communities so as to maximize a modularity score for each community. "
        "Modularity quantifies the quality of an assignment of nodes to communities, that is how densely connected nodes in a community are, compared to how connected they would be in a random network. "
        "The Leiden algorithm is a hierarchical clustering algorithm, that recursively merges communities into single nodes by greedily optimizing the modularity and the process repeats in the condensed graph. "
        "It modifies the Louvain algorithm to address some of its shortcomings, namely the case where some of the communities found by Louvain are not well-connected. "
        "This is achieved by periodically randomly breaking down communities into smaller well-connected ones.",
        inputSchema={
            "type": "object",
            "properties": {
                "maxLevels": {
                    "type": "integer",
                    "description": "The maximum number of levels in which the graph is clustered and then condensed.",
                },
                "gamma": {
                    "type": "number",
                    "description": "Resolution parameter used when computing the modularity. Internally the value is divided by the number of relationships for an unweighted graph, or the sum of weights of all relationships otherwise.",
                },
                "theta": {
                    "type": "number",
                    "description": "Controls the randomness while breaking a community into smaller ones.",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Minimum change in modularity between iterations. If the modularity changes less than the tolerance value, the result is considered stable and the algorithm returns.",
                },
                "includeIntermediateCommunities": {
                    "type": "boolean",
                    "description": "Indicates whether to write intermediate communities. If set to false, only the final community is persisted.",
                },
                "seedProperty": {
                    "type": "string",
                    "description": "Used to set the initial community for a node. The property value needs to be a non-negative number.",
                },
                "minCommunitySize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Leiden on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="local_clustering_coefficient",
        description="The Local Clustering Coefficient algorithm computes the local clustering coefficient for each node in the graph. "
        "The local clustering coefficient Cn of a node n describes the likelihood that the neighbours of n are also connected. "
        "To compute Cn we use the number of triangles a node is a part of Tn, and the degree of the node dn. "
        "The formula to compute the local clustering coefficient is as follows: Cn = 2 * Tn / (dn * (dn - 1))"
        "As we can see the triangle count is required to compute the local clustering coefficient. "
        "To do this the Triangle Count algorithm is utilised. "
        "Additionally, the algorithm can compute the average clustering coefficient for the whole graph. "
        "This is the normalised sum over all the local clustering coefficients.",
        inputSchema={
            "type": "object",
            "properties": {
                "triangleCountProperty": {
                    "type": "string",
                    "description": "Node property that contains pre-computed triangle count.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of node names to filter results. Only nodes whose names (based on nodeIdentifierProperty) contain any of these values will be included in the results. Requires nodeIdentifierProperty to be specified.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Local Clustering Coefficient on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="louvain",
        description="The Louvain method is an algorithm to detect communities in large networks. "
        "It maximizes a modularity score for each community, where the modularity quantifies the quality of an assignment of nodes to communities. "
        "This means evaluating how much more densely connected the nodes within a community are, compared to how connected they would be in a random network. "
        "The Louvain algorithm is a hierarchical clustering algorithm, that recursively merges communities into a single node and executes the modularity clustering on the condensed graphs.",
        inputSchema={
            "type": "object",
            "properties": {
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "seedProperty": {
                    "type": "string",
                    "description": "Used to set the initial community for a node. The property value needs to be a non-negative number.",
                },
                "maxLevels": {
                    "type": "integer",
                    "description": "The maximum number of levels in which the graph is clustered and then condensed.",
                },
                "maxIterations": {
                    "type": "integer",
                    "description": "The maximum number of iterations that the modularity optimization will run for each level.",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Minimum change in modularity between iterations. If the modularity changes less than the tolerance value, the result is considered stable and the algorithm returns.",
                },
                "includeIntermediateCommunities": {
                    "type": "boolean",
                    "description": "Indicates whether to write intermediate communities. If set to false, only the final community is persisted.",
                },
                "consecutiveIds": {
                    "type": "boolean",
                    "description": "Flag to decide whether component identifiers are mapped into a consecutive id space (requires additional memory). Cannot be used in combination with the includeIntermediateCommunities flag.",
                },
                "minCommunitySize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Louvain on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="modularity_metric",
        description="Modularity is a metric that allows you to evaluate the quality of a community detection. "
        "Relationships of nodes in a community C connect to nodes either within C or outside C. "
        "Graphs with high modularity have dense connections between the nodes within communities but sparse connections between nodes in different communities.",
        inputSchema={
            "type": "object",
            "properties": {
                "communityProperty": {
                    "type": "string",
                    "description": "The node property that holds the community ID as an integer for each node. Note that only non-negative community IDs are considered valid and will have their modularity score computed.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Modularity on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
            "required": ["communityProperty"],
        },
    ),
    types.Tool(
        name="modularity_optimization",
        description="The Modularity Optimization algorithm tries to detect communities in the graph based on their modularity. "
        "Modularity is a measure of the structure of a graph, measuring the density of connections within a module or community. "
        "Graphs with a high modularity score will have many connections within a community but only few pointing outwards to other communities. "
        "The algorithm will explore for every node if its modularity score might increase if it changes its community to one of its neighboring nodes.",
        inputSchema={
            "type": "object",
            "properties": {
                "maxIterations": {
                    "type": "integer",
                    "description": "The maximum number of iterations to run.",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Minimum change in modularity between iterations. If the modularity changes less than the tolerance value, the result is considered stable and the algorithm returns.",
                },
                "seedProperty": {
                    "type": "string",
                    "description": "Used to define initial set of labels.",
                },
                "consecutiveIds": {
                    "type": "boolean",
                    "description": "Flag to decide whether component identifiers are mapped into a consecutive id space (requires additional memory).",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "minCommunitySize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run modularity optimization on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="strongly_connected_components",
        description="The Strongly Connected Components (SCC) algorithm finds maximal sets of connected nodes in a directed graph. "
        "A set is considered a strongly connected component if there is a directed path between each pair of nodes within the set. "
        "It is often used early in a graph analysis process to help us get an idea of how our graph is structured.",
        inputSchema={
            "type": "object",
            "properties": {
                "consecutiveIds": {
                    "type": "boolean",
                    "description": "Flag to decide whether component identifiers are mapped into a consecutive id space (requires additional memory).",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run SCC on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="triangle_count",
        description="The Triangle Count algorithm counts the number of triangles for each node in the graph. "
        "A triangle is a set of three nodes where each node has a relationship to the other two. "
        "In graph theory terminology, this is sometimes referred to as a 3-clique. "
        "The Triangle Count algorithm in the GDS library only finds triangles in undirected graphs. "
        "Triangle counting has gained popularity in social network analysis, where it is used to detect communities and measure the cohesiveness of those communities. "
        "It can also be used to determine the stability of a graph, and is often used as part of the computation of network indices, such as clustering coefficients. "
        "The Triangle Count algorithm is also used to compute the Local Clustering Coefficient.",
        inputSchema={
            "type": "object",
            "properties": {
                "maxDegree": {
                    "type": "integer",
                    "description": "If a node has a degree higher than this it will not be considered by the algorithm. The triangle count for these nodes will be -1.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of node names to filter results. Only nodes whose names (based on nodeIdentifierProperty) contain any of these values will be included in the results. Requires nodeIdentifierProperty to be specified.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Triangle Count on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="weakly_connected_components",
        description="The Weakly Connected Components (WCC) algorithm finds sets of connected nodes in directed and undirected graphs. "
        "Two nodes are connected, if there exists a path between them. The set of all nodes that are connected with each other form a component. "
        "In contrast to Strongly Connected Components (SCC), the direction of relationships on the path between two nodes is not considered. "
        "For example, in a directed graph (a)→(b), a and b will be in the same component, even if there is no directed relationship (b)→(a). "
        "WCC is often used early in an analysis to understand the structure of a graph. "
        "Using WCC to understand the graph structure enables running other algorithms independently on an identified cluster.",
        inputSchema={
            "type": "object",
            "properties": {
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "Name of the relationship property to use as weights. If unspecified, the algorithm runs unweighted.",
                },
                "seedProperty": {
                    "type": "string",
                    "description": "Used to set the initial component for a node. The property value needs to be a number.",
                },
                "threshold": {
                    "type": "number",
                    "description": "The value of the weight above which the relationship is considered in the computation.",
                },
                "consecutiveIds": {
                    "type": "boolean",
                    "description": "Flag to decide whether component identifiers are mapped into a consecutive id space (requires additional memory).",
                },
                "minComponentSize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run WCC on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="approximate_maximum_k_cut",
        description="A k-cut of a graph is an assignment of its nodes into k disjoint communities. "
        "So for example a 2-cut of a graph with nodes a,b,c,d could be the communities {a,b,c} and {d}. "
        "A Maximum k-cut is a k-cut such that the total weight of relationships between nodes from different communities in the k-cut is maximized. "
        "That is, a k-cut that maximizes the sum of weights of relationships whose source and target nodes are assigned to different communities in the k-cut. "
        "Suppose in the simple a,b,c,d node set example above we only had one relationship b → c, and it was of weight 1.0. "
        "The 2-cut we outlined above would then not be a maximum 2-cut (with a cut cost of 0.0), whereas for example the 2-cut with communities {a,b} and {c,d} would be one (with a cut cost of 1.0). "
        "n practice, finding the best cut is not feasible for larger graphs and only an approximation can be computed in reasonable time. "
        "The approximate heuristic algorithm implemented in GDS is a parallelized GRASP style algorithm optionally enhanced (via config) with variable neighborhood search (VNS)",
        inputSchema={
            "type": "object",
            "properties": {
                "k": {
                    "type": "integer",
                    "description": "The number of disjoint communities the nodes will be divided into.",
                },
                "iterations": {
                    "type": "integer",
                    "description": "The number of iterations the algorithm will run before returning the best solution among all the iterations.",
                },
                "vnsMaxNeighborhoodOrder": {
                    "type": "integer",
                    "description": "The maximum number of nodes VNS will swap when perturbing solutions.",
                },
                "relationshipWeightProperty": {
                    "type": "string",
                    "description": "If set, the values stored at the given property are used as relationship weights during the computation. If not set, the graph is considered unweighted.",
                },
                "minCommunitySize": {
                    "type": "integer",
                    "description": "Only nodes inside communities larger or equal the given value are returned.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run Max-K-Cut  on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
    types.Tool(
        name="speaker_listener_label_propagation",
        description="The Speaker-Listener Label Propagation Algorithm (SLLPA) is a variation of the Label Propagation algorithm that is able to detect multiple communities per node. "
        "The GDS implementation is based on the SLPA: Uncovering Overlapping Communities in Social Networks via A Speaker-listener Interaction Dynamic Process publication by Xie et al. "
        "The algorithm is randomized in nature and will not produce deterministic results. "
        "To accommodate this, we recommend using a higher number of iterations.",
        inputSchema={
            "type": "object",
            "properties": {
                "maxIterations": {
                    "type": "integer",
                    "description": "Maximum number of iterations to run.",
                },
                "minAssociationStrength": {
                    "type": "number",
                    "description": "Minimum influence required for a community to retain a node.",
                },
                "partitioning": {
                    "type": "string",
                    "enum": ["AUTO", "RANGE", "DEGREE"],
                    "description": "The partitioning scheme used to divide the work between threads. Available options are AUTO, RANGE, DEGREE.",
                },
                "nodeIdentifierProperty": {
                    "type": "string",
                    "description": "The name of a node property to use as node identifier in the result. If provided, the result will include a 'nodeName' column with values from this property.",
                },
                "nodeLabels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The node labels used to project and run SLLPA on. Nodes with different node labels will be ignored. Do not specify to run for all nodes",
                },
            },
        },
    ),
]
