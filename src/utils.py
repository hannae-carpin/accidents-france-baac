# src/utils.py
from pathlib import Path
import matplotlib.pyplot as plt

# Racine du projet = dossier parent de /src
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"

def save_fig(filename: str, dpi: int = 150):
    """
    Sauvegarde la figure matplotlib courante dans outputs/figures (chemin absolu robuste).
    """
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    return path  # 👈 on renvoie le chemin du fichier
