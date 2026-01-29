from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier


def infer_column_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]
    return num_cols, cat_cols


def make_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    num_cols, cat_cols = infer_column_types(X)

    num_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ])

    cat_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, num_cols),
            ("cat", cat_pipe, cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False
    )


def make_models(prep: ColumnTransformer):
    """
    2 modèles:
    - logreg: baseline interprétable + class_weight
    - hgb: modèle fort tabulaire (boosting)
    """
    logreg = Pipeline(steps=[
        ("prep", prep),
        ("clf", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
        ))
    ])

    hgb = Pipeline(steps=[
        ("prep", prep),
        ("clf", HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=400,
            max_depth=None,
        ))
    ])

    return {"logreg": logreg, "hgb": hgb}


def compute_sample_weight(y: np.ndarray) -> np.ndarray:
    """
    Poids inverses fréquence. Simple, robuste, très utile pour classe rare.
    """
    p = float(np.mean(y))
    p = max(min(p, 1 - 1e-6), 1e-6)
    w_pos = 0.5 / p
    w_neg = 0.5 / (1 - p)
    return np.where(y == 1, w_pos, w_neg).astype("float32")
