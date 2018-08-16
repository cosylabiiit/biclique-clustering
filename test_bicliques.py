from .bicliques import MaximalBicliques
from .test_cases import meat_edges


def test_bicliques():
    maxbi = MaximalBicliques()
    maxbi.calculate_bicliques(edge_list=meat_edges)
    assert maxbi.num_unique_nodes == (157, 41)
    assert maxbi.num_edges == 1868
    assert maxbi.num_bicliques == 710
