# src/io.py
from pathlib import Path
import pandas as pd
from typing import Optional

def load_baac_csv(
    path: Path,
    usecols: Optional[list[str]] = None
) -> pd.DataFrame:
    """
    Charge un fichier BAAC au format CSV (séparateur ;, encodage latin-1).
    
    Parameters
    ----------
    path : Path
        Chemin vers le fichier CSV
    usecols : list[str], optional
        Colonnes à charger (si None, toutes les colonnes sont chargées)
    """
    return pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        usecols=usecols,
        low_memory=False
    )
