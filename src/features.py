# src/features.py
import pandas as pd

def add_time_features(acc: pd.DataFrame) -> pd.DataFrame:
    """
    Crée les variables date, weekday, hour et time à partir des colonnes BAAC.
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

    acc["time"] = pd.to_datetime(
    acc["hrmn"],
    format="%H:%M",
    errors="coerce"
)
    
    return acc

def merge_usagers_accidents(usag, acc):
    """
    Fusionne les usagers avec les informations temporelles des accidents.
    """
    return usag.merge(
        acc[["Num_Acc", "hour"]],
        on="Num_Acc",
        how="left"
    )

def accidents_par_departement(acc):
    """
    Calcule le nombre d'accidents par département.
    """
    acc_dep = (
        acc["dep"]
        .value_counts()
        .reset_index()
    )
    acc_dep.columns = ["dep", "nb_accidents"]
    acc_dep["dep"] = acc_dep["dep"].astype(str).str.zfill(2)
    return acc_dep

def merge_accidents_geo(geo_dep, acc_dep):
    """
    Fusionne les données géographiques avec les accidents par département.
    """
    geo_dep = geo_dep.copy()
    geo_dep["code"] = geo_dep["code"].astype(str)

    geo_dep_acc = geo_dep.merge(
        acc_dep,
        left_on="code",
        right_on="dep",
        how="left"
    )

    geo_dep_acc["nb_accidents"] = geo_dep_acc["nb_accidents"].fillna(0)
    return geo_dep_acc

