import pandas as pd
from pathlib import Path

_CSV_PATH = Path("data/owkin_take_home_data.csv")
_df = pd.read_csv(_CSV_PATH)


def get_targets(cancer_name: str) -> list[str]:
    """Return a list of genes for a given cancer type."""
    return _df[_df["cancer_indication"] == cancer_name]["gene"].tolist()


def get_expressions(cancer_name: str, genes: list[str]) -> dict[str, float]:
    """Return median expression values for the given genes within a specific cancer type."""
    mask = (_df["cancer_indication"] == cancer_name) & (_df["gene"].isin(genes))
    subset = _df[mask]
    return dict(zip(subset["gene"], subset["median_value"]))


def get_available_cancers() -> list[str]:
    """Return all unique cancer types in the dataset."""
    return sorted(_df["cancer_indication"].unique().tolist())
