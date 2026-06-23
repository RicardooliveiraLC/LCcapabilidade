import pandas as pd
from .config import HISTORICO_PATH, CHAVE_DEDUP


def ler_historico() -> pd.DataFrame:
    if not HISTORICO_PATH.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(HISTORICO_PATH)
    except Exception as e:
        print(f"  AVISO: Erro ao ler histórico: {e}")
        return pd.DataFrame()


def deduplicar(novos: pd.DataFrame, historico: pd.DataFrame) -> pd.DataFrame:
    chave = [c for c in CHAVE_DEDUP if c in novos.columns]
    if historico.empty:
        return novos.drop_duplicates(subset=chave)
    chave_comum = [c for c in chave if c in historico.columns]
    if not chave_comum:
        return novos.drop_duplicates(subset=chave)
    merged = novos.merge(historico[chave_comum], on=chave_comum, how="left", indicator=True)
    return merged[merged["_merge"] == "left_only"].drop("_merge", axis=1).reset_index(drop=True)


def gravar_historico(novos: pd.DataFrame, historico: pd.DataFrame) -> None:
    combinado = pd.concat([historico, novos], ignore_index=True) if not historico.empty else novos.copy()
    HISTORICO_PATH.parent.mkdir(parents=True, exist_ok=True)
    combinado.to_parquet(HISTORICO_PATH, index=False)
    print(f"  OK Histórico salvo: {len(combinado)} linhas totais")
