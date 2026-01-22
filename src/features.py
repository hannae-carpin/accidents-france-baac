# src/features.py
import pandas as pd

def add_time_features(acc: pd.DataFrame) -> pd.DataFrame:
    """
    Crée les variables date, weekday et hour à partir des colonnes BAAC.
    """
    acc = acc.copy()

    acc["date"] = pd.to_datetime(
        acc["an"].astype(str) + "-" +
        acc["mois"].astype(str).str.zfill(2) + "-" +
        acc["jour"].astype(str).str.zfill(2),
        errors="coerce"
    )

    acc["weekday"] = acc["date"].dt.day_name()

    acc["hour"] = pd.to_datetime(
        acc["hrmn"],
        format="%H:%M",
        errors="coerce"
    ).dt.hour

    return acc

