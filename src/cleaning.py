# src/cleaning.py
import pandas as pd

GRAVITY_MAP = {
    1: "Indemne",
    2: "Tué",
    3: "Blessé hospitalisé",
    4: "Blessé léger"
}

def add_gravity_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute un libellé de gravité à partir du code 'grav'.
    """
    return df.assign(
        grav_label=df["grav"].map(GRAVITY_MAP)
    )
