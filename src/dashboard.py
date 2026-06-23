"""
Gera dashboard/index.html e docs/index.html a partir do histórico processado.
"""
import json
import shutil
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

from .config import TEMPLATE_PATH, DASHBOARD_OUT, DOCS_OUT, CONFIG_MAQ, DIAS_UTEIS
from .loader import ler_config_maq, ler_dias_uteis

MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]


def _fmt_mes(ano: int, mes: int) -> str:
    return f"{MESES_PT[mes-1]} {str(ano)[-2:]}"


def _round2(v) -> float:
    return round(float(v), 2)


def _delta(cur, prev):
    """Diferença absoluta. Retorna 0 se não há período anterior."""
    if prev is None or prev == 0:
        return 0
    return _round2(cur - prev)


def _delta_pct(cur, prev):
    if prev is None or prev == 0:
        return 0
    return _round2((cur - prev) / prev * 100)


def construir_data(df_hist: pd.DataFrame) -> dict:
    """Constrói o objeto DATA completo para o template HTML."""
    if df_hist.empty:
        return _data_vazio()

    # ── garante colunas numéricas ──────────────────────────────────────────
    num_cols = [
        "Total_Apontado", "Horas_Disp", "Extra", "Metros Lineares",
        "01. PRODUTIVO", "02. MANUT. PREVENTIVA", "03. MANUT. CORRETIVA",
        "04. SETUP", "05. OUTROS IMPRODUTIVOS",
        "Cap_Disponivel_m", "Pct_Capabilidade",
        "Pct_Prod", "Pct_Setup", "Pct_Prev", "Pct_Corr",
        "Pct_Cap", "Pct_Manut", "Pct_Prev_Disp", "Pct_Corr_Disp",
    ]
    for c in num_cols:
        if c in df_hist.columns:
            df_hist[c] = pd.to_numeric(df_hist[c], errors="coerce").fillna(0)

    # ── últimos 6 meses com dados ──────────────────────────────────────────
    meses_disponiveis = (
        df_hist[["ano", "mes"]]
        .drop_duplicates()
        .sort_values(["ano", "mes"])
        .tail(6)
    )

    series_labels = []
    s_pct_cap   = []; s_hrs_prod  = []; s_hrs_disp  = []; s_hrs_apont = []
    s_hrs_prev  = []; s_hrs_corr  = []; s_hrs_setup = []; s_hrs_extra = []
    s_pct_prev  = []; s_pct_corr  = []; s_pct_manut = []

    for _, row in meses_disponiveis.iterrows():
        ano, mes = int(row["ano"]), int(row["mes"])
        m = df_hist[(df_hist["ano"] == ano) & (df_hist["mes"] == mes)]
        series_labels.append(_fmt_mes(ano, mes))

        ta   = m["Total_Apontado"].sum()
        prod = m["01. PRODUTIVO"].sum() if "01. PRODUTIVO" in m else 0
        prev = m["02. MANUT. PREVENTIVA"].sum() if "02. MANUT. PREVENTIVA" in m else 0
        corr = m["03. MANUT. CORRETIVA"].sum() if "03. MANUT. CORRETIVA" in m else 0
        setup= m["04. SETUP"].sum() if "04. SETUP" in m else 0
        disp = m["Horas_Disp"].sum() if "Horas_Disp" in m else 0
        ext  = m["Extra"].sum() if "Extra" in m else 0
        cap_t= m["Cap_Disponivel_m"].sum() if "Cap_Disponivel_m" in m else 0
        metros = m["Metros Lineares"].sum() if "Metros Lineares" in m else 0

        s_hrs_prod.append(_round2(prod))
        s_hrs_prev.append(_round2(prev))
        s_hrs_corr.append(_round2(corr))
        s_hrs_setup.append(_round2(setup))
        s_hrs_disp.append(_round2(disp))
        s_hrs_apont.append(_round2(ta))
        s_hrs_extra.append(_round2(ext))
        s_pct_cap.append(_round2(metros / cap_t * 100) if cap_t > 0 else 0)
        s_pct_prev.append(_round2(prev / disp * 100) if disp > 0 else 0)
        s_pct_corr.append(_round2(corr / disp * 100) if disp > 0 else 0)
        s_pct_manut.append(_round2((prev + corr) / disp * 100) if disp > 0 else 0)

    # ── KPIs totais do período completo ────────────────────────────────────
    total = df_hist
    ta_tot  = total["Total_Apontado"].sum()
    prod_tot= total["01. PRODUTIVO"].sum() if "01. PRODUTIVO" in total else 0
    prev_tot= total["02. MANUT. PREVENTIVA"].sum() if "02. MANUT. PREVENTIVA" in total else 0
    corr_tot= total["03. MANUT. CORRETIVA"].sum() if "03. MANUT. CORRETIVA" in total else 0
    setup_tot=total["04. SETUP"].sum() if "04. SETUP" in total else 0
    disp_tot= total["Horas_Disp"].sum() if "Horas_Disp" in total else 0
    ext_tot = total["Extra"].sum() if "Extra" in total else 0
    cap_t_tot= total["Cap_Disponivel_m"].sum() if "Cap_Disponivel_m" in total else 0
    metros_tot= total["Metros Lineares"].sum() if "Metros Lineares" in total else 0
    imp_tot = ta_tot - prod_tot

    # ── deltas vs. mês anterior (últimos 2 meses disponíveis) ──────────────
    def _mes_kpis(m_df):
        ta   = m_df["Total_Apontado"].sum()
        prod = m_df["01. PRODUTIVO"].sum() if "01. PRODUTIVO" in m_df else 0
        prev = m_df["02. MANUT. PREVENTIVA"].sum() if "02. MANUT. PREVENTIVA" in m_df else 0
        corr = m_df["03. MANUT. CORRETIVA"].sum() if "03. MANUT. CORRETIVA" in m_df else 0
        setup= m_df["04. SETUP"].sum() if "04. SETUP" in m_df else 0
        disp = m_df["Horas_Disp"].sum() if "Horas_Disp" in m_df else 0
        ext  = m_df["Extra"].sum() if "Extra" in m_df else 0
        cap_t= m_df["Cap_Disponivel_m"].sum() if "Cap_Disponivel_m" in m_df else 0
        metros= m_df["Metros Lineares"].sum() if "Metros Lineares" in m_df else 0
        return dict(prod=prod,prev=prev,corr=corr,setup=setup,disp=disp,ext=ext,
                    cap_t=cap_t,metros=metros,ta=ta,
                    pct_prod=prod/ta*100 if ta>0 else 0,
                    pct_cap=metros/cap_t*100 if cap_t>0 else 0,
                    pct_setup=setup/ta*100 if ta>0 else 0)

    ultimos = meses_disponiveis.tail(2)
    k_cur = _mes_kpis(df_hist[(df_hist["ano"]==int(ultimos.iloc[-1]["ano"])) & (df_hist["mes"]==int(ultimos.iloc[-1]["mes"]))]) if len(ultimos) >= 1 else None
    k_ant = _mes_kpis(df_hist[(df_hist["ano"]==int(ultimos.iloc[-2]["ano"])) & (df_hist["mes"]==int(ultimos.iloc[-2]["mes"]))]) if len(ultimos) >= 2 else None

    # ── por máquina ────────────────────────────────────────────────────────
    por_maq = []
    for maq, g in df_hist.groupby("Máquina"):
        ta   = g["Total_Apontado"].sum()
        cap_t= g["Cap_Disponivel_m"].sum() if "Cap_Disponivel_m" in g else 0
        metros= g["Metros Lineares"].sum() if "Metros Lineares" in g else 0
        vel  = g["Vel_Ref"].iloc[0] if "Vel_Ref" in g else 0
        pct  = round(metros / cap_t * 100) if cap_t > 0 else 0
        por_maq.append(dict(nm=str(maq), vel=int(vel), h=_round2(ta),
                            cap_tot=int(cap_t), cap_real=int(metros), pct_cap=pct))
    por_maq.sort(key=lambda x: x["pct_cap"], reverse=True)

    # ── dias úteis ─────────────────────────────────────────────────────────
    df_du = ler_dias_uteis()
    dias_uteis_list = []
    if not df_du.empty:
        for _, r in df_du.iterrows():
            dias_uteis_list.append(dict(
                m=str(r.get("Mês", r.get("Mes", ""))),
                d=int(r.get("Dias_Uteis", r.get("Dias Úteis", 0))),
                obs=str(r.get("Observação", r.get("Observacao", "—"))),
            ))

    # ── config máquinas ────────────────────────────────────────────────────
    mapa_vel = ler_config_maq()
    config_maq_list = [{"maquina": k.title(), "vel_ref": int(v)} for k, v in mapa_vel.items()]

    # ── período texto ──────────────────────────────────────────────────────
    anos_meses = df_hist[["ano","mes"]].drop_duplicates().sort_values(["ano","mes"])
    if len(anos_meses) >= 2:
        r0 = anos_meses.iloc[0]; r1 = anos_meses.iloc[-1]
        periodo = f"{_fmt_mes(int(r0['ano']),int(r0['mes']))} – {_fmt_mes(int(r1['ano']),int(r1['mes']))}"
    elif len(anos_meses) == 1:
        r0 = anos_meses.iloc[0]
        periodo = _fmt_mes(int(r0["ano"]), int(r0["mes"]))
    else:
        periodo = "—"

    dias_uteis_periodo = int(df_hist["Horas_Disp"].sum() / 8.8) if "Horas_Disp" in df_hist else 0

    data = dict(
        periodo=periodo,
        dias_uteis_periodo=dias_uteis_periodo,
        atualizado_em=datetime.now().strftime("%d/%m/%Y %H:%M"),
        kpis=dict(
            pct_produtivo=_round2(prod_tot/ta_tot*100) if ta_tot>0 else 0,
            d_pct_produtivo=_delta(k_cur["pct_prod"], k_ant["pct_prod"]) if k_ant else 0,
            pct_cap=_round2(metros_tot/cap_t_tot*100) if cap_t_tot>0 else 0,
            d_pct_cap=_delta(k_cur["pct_cap"], k_ant["pct_cap"]) if k_ant else 0,
            hrs_prod=_round2(prod_tot),
            d_hrs_prod=_delta(k_cur["prod"], k_ant["prod"]) if k_ant else 0,
            hrs_improd=_round2(imp_tot),
            d_hrs_improd=_delta(ta_tot-prod_tot, (k_ant["ta"]-k_ant["prod"])) if k_ant else 0,
            cap_total_m=int(cap_t_tot),
            cap_util_m=int(metros_tot),
            d_cap_util_pct=_delta_pct(k_cur["metros"], k_ant["metros"]) if k_ant else 0,
            pct_setup=_round2(setup_tot/ta_tot*100) if ta_tot>0 else 0,
            d_pct_setup=_delta(k_cur["pct_setup"], k_ant["pct_setup"]) if k_ant else 0,
            hrs_extra=_round2(ext_tot),
            d_hrs_extra=_delta(k_cur["ext"], k_ant["ext"]) if k_ant else 0,
            hrs_prev=_round2(prev_tot),
            d_hrs_prev=_delta(k_cur["prev"], k_ant["prev"]) if k_ant else 0,
            hrs_corr=_round2(corr_tot),
            d_hrs_corr=_delta(k_cur["corr"], k_ant["corr"]) if k_ant else 0,
            hrs_setup=_round2(setup_tot),
            d_hrs_setup=_delta(k_cur["setup"], k_ant["setup"]) if k_ant else 0,
            pct_manut=_round2((prev_tot+corr_tot)/disp_tot*100) if disp_tot>0 else 0,
            metros_prod=int(metros_tot),
            d_metros_pct=_delta_pct(k_cur["metros"], k_ant["metros"]) if k_ant else 0,
        ),
        series=dict(
            labels=series_labels,
            pct_cap=s_pct_cap,
            hrs_prod=s_hrs_prod,
            hrs_disp=s_hrs_disp,
            hrs_apont=s_hrs_apont,
            hrs_prev=s_hrs_prev,
            hrs_corr=s_hrs_corr,
            hrs_setup=s_hrs_setup,
            hrs_extra=s_hrs_extra,
            pct_prev=s_pct_prev,
            pct_corr=s_pct_corr,
            pct_manut=s_pct_manut,
        ),
        por_maquina=por_maq,
        dias_uteis=dias_uteis_list,
        config_maq=config_maq_list,
        mensal=_mensal_records(df_hist),
    )
    return data


def _mensal_records(df: pd.DataFrame) -> list:
    """Um registro por (maquina × mes) com valores brutos — usado para filtros client-side."""
    cols = {
        "01. PRODUTIVO": "prod", "02. MANUT. PREVENTIVA": "prev",
        "03. MANUT. CORRETIVA": "corr", "04. SETUP": "setup",
        "05. OUTROS IMPRODUTIVOS": "outros",
        "Horas_Disp": "disp", "Total_Apontado": "apont",
        "Extra": "extra", "Metros Lineares": "metros",
        "Cap_Disponivel_m": "cap_tot",
    }
    records = []
    for _, row in df.iterrows():
        rec = {"ano": int(row["ano"]), "mes": int(row["mes"]), "maq": str(row["Máquina"])}
        for src, dst in cols.items():
            rec[dst] = _round2(row[src]) if src in row.index else 0
        records.append(rec)
    return records


def _data_vazio() -> dict:
    return dict(periodo="—", dias_uteis_periodo=0, atualizado_em="—",
                kpis={k:0 for k in ["pct_produtivo","d_pct_produtivo","pct_cap","d_pct_cap",
                      "hrs_prod","d_hrs_prod","hrs_improd","d_hrs_improd","cap_total_m","cap_util_m",
                      "d_cap_util_pct","pct_setup","d_pct_setup","hrs_extra","d_hrs_extra",
                      "hrs_prev","d_hrs_prev","hrs_corr","d_hrs_corr","hrs_setup","d_hrs_setup",
                      "pct_manut","metros_prod","d_metros_pct"]},
                series=dict(labels=[],pct_cap=[],hrs_prod=[],hrs_disp=[],hrs_apont=[],
                            hrs_prev=[],hrs_corr=[],hrs_setup=[],hrs_extra=[],
                            pct_prev=[],pct_corr=[],pct_manut=[]),
                por_maquina=[], dias_uteis=[], config_maq=[])


def gerar_html(data: dict) -> None:
    if not TEMPLATE_PATH.exists():
        print(f"  AVISO: Template não encontrado: {TEMPLATE_PATH}")
        return

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data_json = json.dumps(data, ensure_ascii=False)
    html = template.replace("__DATA_PLACEHOLDER__", data_json)

    DASHBOARD_OUT.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_OUT.write_text(html, encoding="utf-8")
    print(f"  OK Dashboard gerado: {DASHBOARD_OUT}")

    DOCS_OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DASHBOARD_OUT, DOCS_OUT)
    print(f"  OK Copiado para docs/: {DOCS_OUT}")
