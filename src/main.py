"""
Pipeline principal - Capabilidade Produtiva - Label Code
Uso:  python -m src.main  (coloque apontamentos em dados/entrada/)
      EXECUTAR.bat         (clique duplo ou drag-and-drop)
"""
import sys
import shutil
from pathlib import Path

# Garante UTF-8 no console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from .config import ENTRADA_DIR, PROCESSADO_DIR, HISTORICO_PATH
from .loader import listar_arquivos_entrada, ler_apontamentos, ler_config_maq
from .storage import ler_historico, deduplicar, gravar_historico
from .transformer import categorizar, agregar, agregar_mensal
from .dashboard import construir_data, gerar_html


def processar(arquivos_extras: list | None = None):
    print("=" * 54)
    print("  CAPABILIDADE PRODUTIVA - LABEL CODE")
    print("=" * 54)

    # [1] Config
    print("\n[1/7] Carregando configuracoes...")
    mapa_vel = ler_config_maq()
    if mapa_vel:
        print(f"  OK  {len(mapa_vel)} maquinas com velocidade de referencia")
    else:
        print("  AVISO: Sem velocidades - capabilidade nao sera calculada")

    # [2] Historico
    print("\n[2/7] Lendo historico...")
    historico = ler_historico()
    print(f"  OK  {len(historico)} registros no historico")

    # Garante que historico tem ano/mes (retroativo)
    if not historico.empty:
        if "ano" not in historico.columns:
            import pandas as pd
            historico["Data de Início"] = pd.to_datetime(historico["Data de Início"], errors="coerce")
            historico["data_ref"] = historico["Data de Início"].dt.normalize()
            historico["ano"] = historico["data_ref"].dt.year
            historico["mes"] = historico["data_ref"].dt.month
            historico.to_parquet(HISTORICO_PATH, index=False)
            print("  (adicionadas colunas ano/mes ao historico e salvo)")

    # [3] Arquivos novos
    print("\n[3/7] Lendo arquivos de entrada...")
    arquivos = arquivos_extras or listar_arquivos_entrada()
    if not arquivos:
        print("  AVISO: Nenhum arquivo em dados/entrada/ - apenas regera o dashboard.")
    df_bruto = ler_apontamentos(arquivos) if arquivos else None

    # [4] Deduplica
    novos_count = 0
    if df_bruto is not None and not df_bruto.empty:
        print("\n[4/7] Deduplicando...")
        df_novos = deduplicar(df_bruto, historico)
        novos_count = len(df_novos)
        print(f"  OK  {novos_count} registros novos (de {len(df_bruto)} lidos)")

        if novos_count == 0:
            print("  Tudo ja esta no historico.")
        else:
            # [5] Classifica e calcula
            print("\n[5/7] Classificando operacoes e calculando...")
            df_cat    = categorizar(df_novos)
            df_diario = agregar(df_cat, mapa_vel)
            df_mensal = agregar_mensal(df_diario)

            # [6] Grava historico
            print("\n[6/7] Gravando historico...")
            gravar_historico(df_novos, historico)

            PROCESSADO_DIR.mkdir(parents=True, exist_ok=True)
            for f in arquivos:
                f = Path(f)
                dest = PROCESSADO_DIR / f.name
                shutil.move(str(f), str(dest))
            print(f"  OK  {len(arquivos)} arquivo(s) movido(s) para processado/")
    else:
        print("\n[4/7] Sem arquivos novos - pulando etapas 4-6.")
        print("\n[5/7] -\n[6/7] -")

    # [7] Dashboard
    print("\n[7/7] Gerando dashboard...")
    historico_final = ler_historico()
    if not historico_final.empty:
        df_cat_all    = categorizar(historico_final)
        df_diario_all = agregar(df_cat_all, mapa_vel)
        df_mensal_all = agregar_mensal(df_diario_all)
        data = construir_data(df_mensal_all)
    else:
        from .dashboard import _data_vazio
        data = _data_vazio()

    gerar_html(data)

    print("\n" + "=" * 54)
    print(f"  CONCLUIDO  ({novos_count} registros adicionados)")
    print("=" * 54)


if __name__ == "__main__":
    extras = [Path(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else None
    processar(extras)
