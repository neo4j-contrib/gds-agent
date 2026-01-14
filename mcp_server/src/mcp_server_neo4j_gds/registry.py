from typing import Dict, Type
from graphdatascience import GraphDataScience
from .algorithm_handler import AlgorithmHandler
from .centrality_algorithm_handlers import (
    PageRankHandler,
    ArticleRankHandler,
    DegreeCentralityHandler,
    ArticulationPointsHandler,
    BetweennessCentralityHandler,
    BridgesHandler,
    CELFHandler,
    ClosenessCentralityHandler,
    EigenvectorCentralityHandler,
    HarmonicCentralityHandler,
    HITSHandler,
)
from .community_algorithm_handlers import (
    ConductanceHandler,
    HDBSCANHandler,
    KCoreDecompositionHandler,
    K1ColoringHandler,
    KMeansClusteringHandler,
    LabelPropagationHandler,
    LeidenHandler,
    LocalClusteringCoefficientHandler,
    LouvainHandler,
    ModularityMetricHandler,
    ModularityOptimizationHandler,
    StronglyConnectedComponentsHandler,
    TriangleCountHandler,
    WeaklyConnectedComponentsHandler,
    ApproximateMaximumKCutHandler,
    SpeakerListenerLabelPropagationHandler,
)
from .similarity_algorithm_handlers import (
    NodeSimilarityHandler,
    KNearestNeighborsHandler,
)
from .path_algorithm_handlers import (
    DijkstraShortestPathHandler,
    DeltaSteppingShortestPathHandler,
    DijkstraSingleSourceShortestPathHandler,
    AStarShortestPathHandler,
    YensShortestPathsHandler,
    MinimumWeightSpanningTreeHandler,
    MinimumDirectedSteinerTreeHandler,
    PrizeCollectingSteinerTreeHandler,
    AllPairsShortestPathsHandler,
    RandomWalkHandler,
    BreadthFirstSearchHandler,
    DepthFirstSearchHandler,
    BellmanFordSingleSourceShortestPathHandler,
    LongestPathHandler,
    MaxFlowHandler,
)


class AlgorithmRegistry:
    _handlers: Dict[str, Type[AlgorithmHandler]] = {
        # Centrality algorithms
        "article_rank": ArticleRankHandler,
        "articulation_points": ArticulationPointsHandler,
        "betweenness_centrality": BetweennessCentralityHandler,
        "bridges": BridgesHandler,
        "CELF": CELFHandler,
        "closeness_centrality": ClosenessCentralityHandler,
        "degree_centrality": DegreeCentralityHandler,
        "eigenvector_centrality": EigenvectorCentralityHandler,
        "pagerank": PageRankHandler,
        "harmonic_centrality": HarmonicCentralityHandler,
        "HITS": HITSHandler,
        # Community detection algorithms
        "conductance": ConductanceHandler,
        "hdbscan": HDBSCANHandler,
        "k_core_decomposition": KCoreDecompositionHandler,
        "k_1_coloring": K1ColoringHandler,
        "k_means_clustering": KMeansClusteringHandler,
        "label_propagation": LabelPropagationHandler,
        "leiden": LeidenHandler,
        "local_clustering_coefficient": LocalClusteringCoefficientHandler,
        "louvain": LouvainHandler,
        "modularity_metric": ModularityMetricHandler,
        "modularity_optimization": ModularityOptimizationHandler,
        "strongly_connected_components": StronglyConnectedComponentsHandler,
        "triangle_count": TriangleCountHandler,
        "weakly_connected_components": WeaklyConnectedComponentsHandler,
        "approximate_maximum_k_cut": ApproximateMaximumKCutHandler,
        "speaker_listener_label_propagation": SpeakerListenerLabelPropagationHandler,
        # Similarity algorithms
        "node_similarity": NodeSimilarityHandler,
        "k_nearest_neighbors": KNearestNeighborsHandler,
        # Path finding algorithms
        "find_shortest_path": DijkstraShortestPathHandler,
        "delta_stepping_shortest_path": DeltaSteppingShortestPathHandler,
        "dijkstra_single_source_shortest_path": DijkstraSingleSourceShortestPathHandler,
        "a_star_shortest_path": AStarShortestPathHandler,
        "yens_shortest_paths": YensShortestPathsHandler,
        "minimum_weight_spanning_tree": MinimumWeightSpanningTreeHandler,
        "minimum_directed_steiner_tree": MinimumDirectedSteinerTreeHandler,
        "prize_collecting_steiner_tree": PrizeCollectingSteinerTreeHandler,
        "all_pairs_shortest_paths": AllPairsShortestPathsHandler,
        "random_walk": RandomWalkHandler,
        "breadth_first_search": BreadthFirstSearchHandler,
        "depth_first_search": DepthFirstSearchHandler,
        "bellman_ford_single_source_shortest_path": BellmanFordSingleSourceShortestPathHandler,
        "longest_path": LongestPathHandler,
        "max_flow": MaxFlowHandler,
    }

    @classmethod
    def get_handler(cls, name: str, gds: GraphDataScience) -> AlgorithmHandler:
        handler_class = cls._handlers.get(name)
        if handler_class is None:
            raise ValueError(f"Unknown tool: {name}.")
        return handler_class(gds)
