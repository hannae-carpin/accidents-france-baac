# src/features.py
import pandas as pd

def add_time_features(acc):
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
        acc[["Num_Acc", "hour", "weekday", "dep"]],
        on="Num_Acc",
        how="left"
    )

def normaliser_dep_metropole(dep):
    """
    Normalise les codes départementaux pour la France métropolitaine.
    """
    dep = dep.astype("string").str.strip().str.upper()

    mask = (
        dep.isin(["2A", "2B"])
        | dep.str.fullmatch(r"\d{1,2}", na=False)
    )

    dep = dep.where(mask).str.zfill(2)
    return dep

def accidents_par_departement(acc):
    """
    Agrège les accidents par département (France métropolitaine uniquement).
    """
    acc_dep = (
        acc["dep"]
        .value_counts()
        .reset_index()
    )
    acc_dep.columns = ["dep", "nb_accidents"]

    acc_dep["dep"] = normaliser_dep_metropole(acc_dep["dep"])
    acc_dep = acc_dep.dropna(subset=["dep"])

    return acc_dep


def merge_accidents_geo(geo_dep, acc_dep):
    """
    Fusionne les données géographiques avec les indicateurs d'accidents.
    """
    geo_dep = geo_dep.copy()
    acc_dep = acc_dep.copy()

    geo_dep["dep"] = normaliser_dep_metropole(geo_dep["dep"])
    geo_dep = geo_dep.dropna(subset=["dep"])

    acc_dep["dep"] = normaliser_dep_metropole(acc_dep["dep"])
    acc_dep = acc_dep.dropna(subset=["dep"])

    geo_dep_acc = geo_dep.merge(acc_dep, on="dep", how="left")
    if "nb_accidents" in geo_dep_acc.columns:
        geo_dep_acc["nb_accidents"] = geo_dep_acc["nb_accidents"].fillna(0)

    return geo_dep_acc

def add_taux_100k(acc_dep, pop):
    """
    Calcule le taux d'accidents pour 100 000 habitants par département.
    """
    acc_dep = acc_dep.copy()
    pop = pop.copy()

    acc_dep["dep"] = normaliser_dep_metropole(acc_dep["dep"])
    pop["dep"] = normaliser_dep_metropole(pop["dep"])

    acc_dep = acc_dep.dropna(subset=["dep"])
    pop = pop.dropna(subset=["dep"])

    pop["population"] = pd.to_numeric(pop["population"], errors="coerce")

    acc_dep_pop = acc_dep.merge(pop[["dep", "population"]], on="dep", how="left")
    acc_dep_pop["taux_100k"] = (acc_dep_pop["nb_accidents"] / acc_dep_pop["population"]) * 100_000
    acc_dep_pop.loc[acc_dep_pop["population"].isna() | (acc_dep_pop["population"] <= 0), "taux_100k"] = pd.NA

    return acc_dep_pop
