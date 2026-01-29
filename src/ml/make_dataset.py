from __future__ import annotations

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FEATURES = [
    # time
    "jour", "mois", "weekday", "hour", "hrmn",
    # environment / conditions
    "lum", "atm", "surf", "plan", "infra", "situ",
    # road / circulation
    "agg", "int", "catr", "circ", "nbv", "vosp", "prof",
    "lartpc", "larrout", "vma",
    # geo (safe)
    "dep",
]

DROP_IF_PRESENT = [
    "Num_Acc", "date", "time", "an", "com", "adr", "voie", "v1", "v2", "lat", "long", "pr", "pr1", "col"
]

def load_processed(processed_dir: Path = PROCESSED_DIR) -> tuple[pd.DataFrame, pd.DataFrame]:
    acc_path = processed_dir / "accidents-2024.parquet"
    usag_path = processed_dir / "usagers-2024.parquet"

    if not acc_path.exists():
        raise FileNotFoundError(f"Fichier manquant: {acc_path}")
    if not usag_path.exists():
        raise FileNotFoundError(f"Fichier manquant: {usag_path}")

    acc = pd.read_parquet(acc_path)
    usag = pd.read_parquet(usag_path)
    return acc, usag


def build_target_from_usagers(usag: pd.DataFrame) -> pd.DataFrame:
    """
    y: is_fatal = 1 si au moins un usager est 'Tué' sur l'accident.
    """
    required = {"Num_Acc", "grav_label"}
    missing = required - set(usag.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans usagers: {sorted(missing)}")

    y = (
        usag.assign(_fatal=(usag["grav_label"] == "Tué").astype("int8"))
            .groupby("Num_Acc", as_index=False)["_fatal"]
            .max()
            .rename(columns={"_fatal": "is_fatal"})
    )
    return y


def make_xy(processed_dir: Path = PROCESSED_DIR) -> tuple[pd.DataFrame, pd.Series]:
    """
    Retourne X (features accident-level) et y (is_fatal) alignés par Num_Acc.
    """
    acc, usag = load_processed(processed_dir)
    y_acc = build_target_from_usagers(usag)

    # Merge y sur acc
    df = acc.merge(y_acc, on="Num_Acc", how="left")
    df["is_fatal"] = df["is_fatal"].fillna(0).astype("int8")

    # Vérifie features existantes
    missing_feats = [c for c in FEATURES if c not in df.columns]
    if missing_feats:
        raise ValueError(f"Features attendues manquantes dans accidents: {missing_feats}")

    X = df[FEATURES].copy()
    y = df["is_fatal"].copy()

    return X, y


def make_train_val_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
):
    """
    Split stratifié (car classe rare). Comme tu n'as que 2024 dans tes parquets.
    Quand tu ajouteras plusieurs années: on passera en split temporel.
    """
    from sklearn.model_selection import train_test_split

    return train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
