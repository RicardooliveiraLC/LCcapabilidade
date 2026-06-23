from .config import OP_PRODUTIVAS


def classificar_operacao(op: str) -> str:
    op_up = str(op).upper()

    # Verificar keywords de manutenção ANTES das de revisão
    # (evita "REVISÃO MÁQUINA FLEXO" cair em PRODUTIVO)
    if "PREVENTIVA" in op_up:
        return "02. MANUT. PREVENTIVA"
    if "CORRETIVA" in op_up:
        return "03. MANUT. CORRETIVA"
    if "REVISÃO MÁQUINA" in op_up or "REVISAO MAQUINA" in op_up:
        return "02. MANUT. PREVENTIVA"

    # Produtivo: operações configuradas + revisão manual de produto
    if any(p.upper() in op_up for p in OP_PRODUTIVAS):
        return "01. PRODUTIVO"
    if "REVISAO MANUAL" in op_up or "REVISÃO MANUAL" in op_up:
        return "01. PRODUTIVO"

    # Setup
    if "SETUP" in op_up or "AJUSTE DE COR" in op_up or "TROCA DE FACA" in op_up:
        return "04. SETUP"

    return "05. OUTROS IMPRODUTIVOS"
