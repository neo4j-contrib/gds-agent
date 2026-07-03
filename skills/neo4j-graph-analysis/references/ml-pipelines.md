# Embeddings and ML pipelines

## Node embeddings

Embeddings turn topology (and optionally properties) into vectors for
similarity search, clustering, or ML features. Run them in `mutate` mode with a
`mutateProperty` so downstream tools on the same projection can use the result.

| Tool | Choose when | Key inputs |
|---|---|---|
| `fast_rp` | Default: fast, scalable, topology-based | `embeddingDimension` required; `propertyRatio`/`featureProperties` to mix in properties |
| `node2vec` | Control over structural-vs-community flavour | `inOutFactor`, `returnFactor` (random-walk based) |
| `hashgnn` | GNN-like without training; heterogeneous graphs | binary features: `featureProperties` or `binarizeFeatures` or `generateFeatures`; `heterogeneous: true` |
| `graph_sage_train` + `graph_sage_predict` | Inductive: reuse a trained model on unseen nodes/graphs with the same schema | numeric `featureProperties` must exist in the projection; prefer undirected; model stored under `modelName` |

Typical chains:
- Similar nodes: `fast_rp` (mutate `embedding`) → `k_nearest_neighbors`
  (`nodeProperties: ["embedding"]`).
- Property clustering: embedding (mutate) → `k_means_clustering` or `HDBSCAN`
  (`nodeProperty: "embedding"`).

For deterministic runs pass `randomSeed`.

## Supervised pipelines

Three train/predict pairs, all storing models in the GDS model catalog:

| Task | Train | Predict | Target |
|---|---|---|---|
| Categorical node property | `train_node_classification_model` | `predict_node_classification` | integer `targetProperty` |
| Missing/future relationships | `train_link_prediction_model` | `predict_link_prediction` | `targetRelationshipType` (must be UNDIRECTED in the projection) |
| Numeric node property | `train_node_regression_model` | `predict_node_regression` | numeric `targetProperty` |

Workflow:

1. **Project** the graph including the target property/relationships and any
   database-side features. Link prediction requires the target relationship
   type projected UNDIRECTED (see projections.md).
2. **Features.** `featureProperties` (or `linkFeatures` inputs) must exist in
   the projection — either projected from the database or computed by
   `nodePropertySteps` (e.g. a fastRP/degree step inside the pipeline) or by a
   prior mutate-mode algorithm.
3. **Train** with `modelName`. Optional: `modelCandidates` (logistic
   regression / random forest / MLP with hyperparameters), `splitConfig`,
   `autoTuningConfig`, `metrics`, `randomSeed`. Training evaluates candidates
   and keeps the winner; the temporary pipeline is cleaned up automatically.
4. **Predict** with the same `modelName`, on the training graph or another
   projection with the same schema/features. Stream mode returns predictions
   (`includePredictedProbabilities` for classification); mutate mode writes
   them to the in-memory graph. `predict_link_prediction` needs `topN`
   (exhaustive) or `sampleRate < 1` (approximate).

## Model catalog

- `list_models` — models with type, config, metrics (spans sessions in session
  mode).
- `drop_model` — free memory; database and projections are unaffected.
- Model names must be unique; drop before retraining under the same name.
