"""
Migra DADOS_HISTORICOS do xlsx legado para historico.parquet.
Uso: python scripts/migrar_historico.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.config import HISTORICO_PATH

XLSX_LEGADO = ROOT / "obsoleto" / "Capabilidade_produtiva_recuperacao.xlsx"


def migrar():
    if not XLSX_LEGADO.exists():
        print(f"❌ Arquivo não encontrado: {XLSX_LEGADO}")
        return

    print(f"Lendo {XLSX_LEGADO.name} ...")
    try:
        df = pd.read_excel(XLSX_LEGADO, sheet_name="DADOS_HISTORICOS")
        print(f"  ✓ {len(df)} linhas na aba DADOS_HISTORICOS")
    except Exception as e:
        print(f"  ⚠ Aba DADOS_HISTORICOS não encontrada: {e}")
        print("  Tentando ler a primeira aba...")
        try:
            df = pd.read_excel(XLSX_LEGADO)
            print(f"  ✓ {len(df)} linhas lidas")
        except Exception as e2:
            print(f"❌ Falha ao ler o arquivo: {e2}")
            return

    if df.empty:
        print("❌ Nenhum dado encontrado.")
        return

    HISTORICO_PATH.parent.mkdir(parents=True, exist_ok=True)

    if HISTORICO_PATH.exists():
        print(f"\nHistórico existente encontrado ({HISTORICO_PATH}).")
        resp = input("Substituir? (s/N): ").strip().lower()
        if resp != "s":
            print("Migração cancelada.")
            return

    df.to_parquet(HISTORICO_PATH, index=False)
    print(f"\n✅ Migração concluída: {len(df)} registros → {HISTORICO_PATH}")


if __name__ == "__main__":
    migrar()
