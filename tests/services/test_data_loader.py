from app.services.data_loader import get_targets, get_expressions, get_available_cancers


def test_get_targets_lung():
    targets = get_targets("lung")
    assert sorted(targets) == ["ALK", "KRAS", "RET", "ROS1", "STK11"]


def test_get_targets_breast():
    targets = get_targets("breast")
    assert sorted(targets) == [
        "AKT1", "BRCA1", "BRCA2", "CDH1", "ESR1",
        "GATA3", "HER2", "MAP3K1", "PIK3CA", "TP53",
    ]


def test_get_targets_unknown_cancer():
    targets = get_targets("nonexistent")
    assert targets == []


def test_get_expressions_lung_kras():
    result = get_expressions("lung", ["KRAS"])
    assert result == {"KRAS": 0.359}


def test_get_expressions_breast_multiple_genes():
    result = get_expressions("breast", ["BRCA1", "BRCA2"])
    assert result == {"BRCA1": 0.094, "BRCA2": 0.032}


def test_get_expressions_gene_across_cancers():
    """TP53 has different values in breast (0.233) vs colorectal (0.643)."""
    breast_result = get_expressions("breast", ["TP53"])
    colorectal_result = get_expressions("colorectal", ["TP53"])
    assert breast_result == {"TP53": 0.233}
    assert colorectal_result == {"TP53": 0.643}


def test_get_expressions_unknown_gene():
    result = get_expressions("lung", ["FAKEGENE"])
    assert result == {}


def test_get_expressions_unknown_cancer():
    result = get_expressions("nonexistent", ["KRAS"])
    assert result == {}


def test_get_available_cancers():
    cancers = get_available_cancers()
    assert set(cancers) == {
        "breast", "colorectal", "gastric", "glioblastoma",
        "lung", "melanoma", "ovarian", "pancreatic", "prostate", "renal",
    }
