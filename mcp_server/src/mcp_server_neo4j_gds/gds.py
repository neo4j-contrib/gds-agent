from graphdatascience.session.aura_graph_data_science import AuraGraphDataScience


def is_session_gds(gds) -> bool:
    return isinstance(gds, AuraGraphDataScience)
