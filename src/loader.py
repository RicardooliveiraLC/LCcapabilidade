import pandas as pd
from pathlib import Path
from .config import CONFIG_MAQ, DIAS_UTEIS, ENTRADA_DIR


def listar_arquivos_entrada() -> list:
    return list(ENTRADA_DIR.glob("*.xlsx")) + list(ENTRADA_DIR.glob("*.csv"))


def ler_apontamentos(arquivos: list) -> pd.DataFrame:
    frames = []
    for f in arquivos:
        f = Path(f)
        try:
            df = pd.read_csv(f) if f.suffix.lower() == ".csv" else pd.read_excel(f)
            print(f"  OK {f.name}  ({len(df)} linhas)")
            frames.append(df)
        except Exception as e:
            print(f"  AVISO: Erro ao ler {f.name}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def ler_config_maq() -> dict:
    if not CONFIG_MAQ.exists():
        print("  AVISO: config_maq.xlsx não encontrado — capabilidade não será calculada.")
        return {}
    try:
        df = pd.read_excel(CONFIG_MAQ)
        df.columns = [str(c).strip() for c in df.columns]
        df["Maquina"] = df["Maquina"].astype(str).str.strip().str.upper()
        return dict(zip(df["Maquina"], df.iloc[:, 1].astype(float)))
    except Exception as e:
        print(f"  AVISO: Erro ao ler config_maq.xlsx: {e}")
        return {}


def ler_dias_uteis() -> pd.DataFrame:
    if not DIAS_UTEIS.exists():
        print("  AVISO: dias_uteis.xlsx não encontrado — usando cálculo padrão.")
        return pd.DataFrame()
    try:
        df = pd.read_excel(DIAS_UTEIS)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        print(f"  AVISO: Erro ao ler dias_uteis.xlsx: {e}")
        return pd.DataFrame()
