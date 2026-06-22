import logging
from typing import Any, Dict

from graphdatascience.model.graphsage_model import GraphSageModel

from .algorithm_handler import AlgorithmHandler, clean_params
from .node_translator import translate_ids_to_identifiers

logger = logging.getLogger("mcp_server_neo4j_gds")


class FastRPHandler(AlgorithmHandler):
    def fast_rp(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"FastRP parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.fastRP.mutate(G, **gds_params)
        else:
            result = self.gds.fastRP.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("nodeIdentifierProperty"), result
            )
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.fast_rp(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            embeddingDimension=arguments.get("embeddingDimension"),
            iterationWeights=arguments.get("iterationWeights"),
            normalizationStrength=arguments.get("normalizationStrength"),
            nodeSelfInfluence=arguments.get("nodeSelfInfluence"),
            propertyRatio=arguments.get("propertyRatio"),
            featureProperties=arguments.get("featureProperties"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            randomSeed=arguments.get("randomSeed"),
        )


class Node2VecHandler(AlgorithmHandler):
    def node2vec(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"Node2Vec parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.node2vec.mutate(G, **gds_params)
        else:
            result = self.gds.node2vec.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("nodeIdentifierProperty"), result
            )
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.node2vec(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            embeddingDimension=arguments.get("embeddingDimension"),
            walkLength=arguments.get("walkLength"),
            walksPerNode=arguments.get("walksPerNode"),
            inOutFactor=arguments.get("inOutFactor"),
            returnFactor=arguments.get("returnFactor"),
            windowSize=arguments.get("windowSize"),
            negativeSamplingRate=arguments.get("negativeSamplingRate"),
            positiveSamplingFactor=arguments.get("positiveSamplingFactor"),
            embeddingInitializer=arguments.get("embeddingInitializer"),
            iterations=arguments.get("iterations"),
            initialLearningRate=arguments.get("initialLearningRate"),
            minLearningRate=arguments.get("minLearningRate"),
            walkBufferSize=arguments.get("walkBufferSize"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            randomSeed=arguments.get("randomSeed"),
        )


class HashGNNHandler(AlgorithmHandler):
    def hashgnn(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(
            kwargs, ["graphName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"HashGNN parameters: {gds_params}")
        if mode == "mutate":
            result = self.gds.hashgnn.mutate(G, **gds_params)
        else:
            result = self.gds.hashgnn.stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("nodeIdentifierProperty"), result
            )
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.hashgnn(
            graphName=arguments.get("graphName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            iterations=arguments.get("iterations"),
            embeddingDensity=arguments.get("embeddingDensity"),
            featureProperties=arguments.get("featureProperties"),
            generateFeatures=arguments.get("generateFeatures"),
            binarizeFeatures=arguments.get("binarizeFeatures"),
            heterogeneous=arguments.get("heterogeneous"),
            neighborInfluence=arguments.get("neighborInfluence"),
            outputDimension=arguments.get("outputDimension"),
            randomSeed=arguments.get("randomSeed"),
        )


class GraphSageTrainHandler(AlgorithmHandler):
    def graph_sage_train(self, **kwargs):
        G = self.gds.graph.get(kwargs.get("graphName"))
        gds_params = clean_params(kwargs, ["graphName"])
        logger.info(f"GraphSAGE train parameters: {gds_params}")
        model, result = self.gds.beta.graphSage.train(G, **gds_params)
        return {"modelName": model.name(), "trainResult": result.to_dict()}

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.graph_sage_train(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            featureProperties=arguments.get("featureProperties"),
            embeddingDimension=arguments.get("embeddingDimension"),
            aggregator=arguments.get("aggregator"),
            activationFunction=arguments.get("activationFunction"),
            sampleSizes=arguments.get("sampleSizes"),
            epochs=arguments.get("epochs"),
            maxIterations=arguments.get("maxIterations"),
            searchDepth=arguments.get("searchDepth"),
            batchSize=arguments.get("batchSize"),
            learningRate=arguments.get("learningRate"),
            tolerance=arguments.get("tolerance"),
            negativeSampleWeight=arguments.get("negativeSampleWeight"),
            penaltyL2=arguments.get("penaltyL2"),
            projectedFeatureDimension=arguments.get("projectedFeatureDimension"),
            relationshipWeightProperty=arguments.get("relationshipWeightProperty"),
            randomSeed=arguments.get("randomSeed"),
        )


class GraphSagePredictHandler(AlgorithmHandler):
    def graph_sage_predict(self, **kwargs):
        mode = kwargs.get("mode", "stream")
        model_name = kwargs.get("modelName")
        G = self.gds.graph.get(kwargs.get("graphName"))
        model = self.gds.model.get(model_name)
        if not isinstance(model, GraphSageModel):
            raise ValueError(
                f"Model '{model_name}' is not a GraphSAGE model (type: {model.type()}). "
                "Use graph_sage_train to train one."
            )
        gds_params = clean_params(
            kwargs, ["graphName", "modelName", "mode", "nodeIdentifierProperty"]
        )
        logger.info(f"GraphSAGE predict parameters: {gds_params}")
        if mode == "mutate":
            result = model.predict_mutate(G, **gds_params)
        else:
            result = model.predict_stream(G, **gds_params)
            translate_ids_to_identifiers(
                self.gds, kwargs.get("nodeIdentifierProperty"), result
            )
        return result

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return self.graph_sage_predict(
            graphName=arguments.get("graphName"),
            modelName=arguments.get("modelName"),
            mode=arguments.get("mode"),
            mutateProperty=arguments.get("mutateProperty"),
            nodeIdentifierProperty=arguments.get("nodeIdentifierProperty"),
            batchSize=arguments.get("batchSize"),
        )
