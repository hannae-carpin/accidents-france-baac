from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt

from joblib import load
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    confusion_matrix,
    ConfusionMatrixDisplay,
    brier_score_loss,
)
from sklearn.calibration import calibration_curve

from src.ml.make_dataset import make_xy, make_train_val_split


MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports/ml")


def evaluate(model_name: str = "hgb", top_percent: float = 0.05):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = make_xy()
    X_train, X_test, y_train, y_test = make_train_val_split(X, y, test_size=0.2)

    model_path = MODELS_DIR / f"{model_name}.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Modèle introuvable: {model_path} (lance train.py avant)")

    model = load(model_path)
    proba = model.predict_proba(X_test)[:, 1]

    # PR Curve
    prec, rec, _ = precision_recall_curve(y_test, proba)
    ap = float(average_precision_score(y_test, proba))

    plt.figure(figsize=(7, 5))
    plt.plot(rec, prec)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Precision-Recall ({model_name}) — AP={ap:.3f}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / f"pr_curve_{model_name}.png", dpi=160)
    plt.close()

    # Calibration
    frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=10, strategy="quantile")
    brier = float(brier_score_loss(y_test, proba))

    plt.figure(figsize=(7, 5))
    plt.plot(mean_pred, frac_pos, marker="o")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("Probabilité prédite (bins)")
    plt.ylabel("Fréquence observée")
    plt.title(f"Calibration ({model_name}) — Brier={brier:.3f}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / f"calibration_{model_name}.png", dpi=160)
    plt.close()

    # Seuil pragmatique: top X% des scores (priorisation)
    q = 1.0 - float(top_percent)
    threshold = float(np.quantile(proba, q))
    y_pred = (proba >= threshold).astype(int)

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(values_format="d")
    plt.title(f"Confusion ({model_name}) — seuil top {int(top_percent*100)}%")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / f"confusion_{model_name}.png", dpi=160)
    plt.close()

    summary = {
        "model": model_name,
        "ap_pr_auc": ap,
        "brier": brier,
        "test_prevalence": float(np.mean(y_test)),
        "threshold_top_percent": top_percent,
        "threshold_value": threshold,
        "confusion_matrix": cm.tolist(),
    }
    (REPORTS_DIR / f"eval_{model_name}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("OK")
    print(f"- figures: {REPORTS_DIR.resolve()}")
    print(f"- résumé: {(REPORTS_DIR / f'eval_{model_name}.json').resolve()}")


if __name__ == "__main__":
    evaluate(model_name="hgb", top_percent=0.05)
