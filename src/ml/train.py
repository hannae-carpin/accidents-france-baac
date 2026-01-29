from __future__ import annotations

from pathlib import Path
import json

import numpy as np
from joblib import dump
from sklearn.metrics import average_precision_score, roc_auc_score

from src.ml.make_dataset import make_xy, make_train_val_split
from src.ml.pipeline import make_preprocessor, make_models, compute_sample_weight


MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports/ml")


def train_and_select_best():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = make_xy()
    X_train, X_val, y_train, y_val = make_train_val_split(X, y, test_size=0.2)

    prep = make_preprocessor(X_train)
    models = make_models(prep)

    results = {}
    best_name = None
    best_pr_auc = -1.0

    for name, pipe in models.items():
        if name == "hgb":
            sw = compute_sample_weight(y_train.to_numpy())
            pipe.fit(X_train, y_train, clf__sample_weight=sw)
        else:
            pipe.fit(X_train, y_train)

        proba = pipe.predict_proba(X_val)[:, 1]
        pr_auc = float(average_precision_score(y_val, proba))
        roc_auc = float(roc_auc_score(y_val, proba))

        results[name] = {
            "pr_auc": pr_auc,
            "roc_auc": roc_auc,
            "val_prevalence": float(y_val.mean()),
            "n_train": int(len(y_train)),
            "n_val": int(len(y_val)),
        }

        dump(pipe, MODELS_DIR / f"{name}.joblib")

        if pr_auc > best_pr_auc:
            best_pr_auc = pr_auc
            best_name = name

    # Sauvegarde résumé
    results["best_model"] = best_name
    (REPORTS_DIR / "metrics.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("OK")
    print(f"- modèles: {MODELS_DIR.resolve()}")
    print(f"- métriques: {(REPORTS_DIR / 'metrics.json').resolve()}")
    print(f"- best_model: {best_name} (PR-AUC={best_pr_auc:.4f})")


if __name__ == "__main__":
    train_and_select_best()
