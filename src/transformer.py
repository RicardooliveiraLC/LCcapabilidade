import pandas as pd
import numpy as np
from .config import CATEGORIAS
from .classifier import classificar_operacao


def _vel_ref(nome: str, mapa: dict) -> float:
    nome = str(nome).strip().upper()
    for maq, vel in mapa.items():
        if maq in nome:
            return float(vel)
    return 0.0


def categorizar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Data de Início"] = pd.to_datetime(df["Data de Início"], errors="coerce")
    df = df.dropna(subset=["Data de Início"]).copy()
    df["data_ref"] = df["Data de Início"].dt.normalize()
    df["ano"]      = df["data_ref"].dt.year
    df["mes"]      = df["data_ref"].dt.month
    df["Categoria"] = df["Operação"].apply(classificar_operacao)
    return df


def agregar(df: pd.DataFrame, mapa_vel: dict) -> pd.DataFrame:
    # pivot minutos → horas por categoria
    pivot = df.pivot_table(
        index=["data_ref", "ano", "mes", "Máquina"],
        columns="Categoria",
        values="Total Minutos",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for col in CATEGORIAS:
        pivot[col] = pivot.get(col, 0) / 60

    # horas disponíveis (seg-qui=9h, sex=8h, sáb/dom=0)
    pivot["Horas_Disp"] = np.where(
        pivot["data_ref"].dt.weekday < 4, 9.0,
        np.where(pivot["data_ref"].dt.weekday == 4, 8.0, 0.0),
    )

    pivot["Total_Apontado"] = pivot[CATEGORIAS].sum(axis=1)
    pivot["Extra"] = (pivot["Total_Apontado"] - pivot["Horas_Disp"]).clip(lower=0)

    # metros lineares
    metros = (
        df.groupby(["data_ref", "Máquina"])["Metros Lineares"]
        .sum()
        .reset_index()
    )
    res = pd.merge(pivot, metros, on=["data_ref", "Máquina"], how="left").fillna(0)

    # capabilidade
    res["Vel_Ref"] = res["Máquina"].apply(lambda x: _vel_ref(x, mapa_vel))
    res["Cap_Disponivel_m"] = res["Total_Apontado"] * res["Vel_Ref"] * 60
    res["Pct_Capabilidade"] = np.where(
        res["Cap_Disponivel_m"] > 0,
        res["Metros Lineares"] / res["Cap_Disponivel_m"],
        0,
    )

    # percentuais
    ta = res["Total_Apontado"].replace(0, np.nan)
    res["Pct_Prod"]  = res["01. PRODUTIVO"] / ta
    res["Pct_Setup"] = res["04. SETUP"] / ta
    res["Pct_Prev"]  = res["02. MANUT. PREVENTIVA"] / ta
    res["Pct_Corr"]  = res["03. MANUT. CORRETIVA"] / ta
    res = res.fillna(0)

    return res


def agregar_mensal(df_diario: pd.DataFrame) -> pd.DataFrame:
    """Agrega o resultado diário em visão mensal, preservando nomes de colunas."""
    sum_cols = (
        ["Metros Lineares", "Total_Apontado", "Horas_Disp", "Extra", "Cap_Disponivel_m"]
        + CATEGORIAS
    )
    agg_map = {c: "sum" for c in sum_cols if c in df_diario.columns}
    if "Vel_Ref" in df_diario.columns:
        agg_map["Vel_Ref"] = "first"

    grp = df_diario.groupby(["ano", "mes", "Máquina"]).agg(agg_map).reset_index()

    ta   = grp["Total_Apontado"].replace(0, np.nan)
    disp = grp["Horas_Disp"].replace(0, np.nan)
    prod = grp.get("01. PRODUTIVO",  pd.Series(0, index=grp.index))
    prev = grp.get("02. MANUT. PREVENTIVA", pd.Series(0, index=grp.index))
    corr = grp.get("03. MANUT. CORRETIVA",  pd.Series(0, index=grp.index))
    setup= grp.get("04. SETUP",             pd.Series(0, index=grp.index))
    cap_t= grp.get("Cap_Disponivel_m",      pd.Series(0, index=grp.index))
    metros = grp.get("Metros Lineares",     pd.Series(0, index=grp.index))

    grp["Pct_Prod"]  = prod  / ta
    grp["Pct_Setup"] = setup / ta
    grp["Pct_Prev"]  = prev  / ta
    grp["Pct_Corr"]  = corr  / ta
    grp["Pct_Cap"]   = np.where(cap_t  > 0, metros / cap_t,        0)
    grp["Pct_Manut"] = np.where(disp   > 0, (prev + corr) / disp,  0)
    grp["Pct_Prev_Disp"] = np.where(disp > 0, prev / disp, 0)
    grp["Pct_Corr_Disp"] = np.where(disp > 0, corr / disp, 0)
    return grp.fillna(0)
