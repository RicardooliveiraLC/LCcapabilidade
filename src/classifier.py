import re
from .config import OP_PRODUTIVAS_COD, OP_PRODUTIVAS_NOMES

_COD_RE = re.compile(r"^\s*(\d{3})")


def classificar_operacao(op: str) -> str:
    """
    Classifica operação em 5 categorias com base em:
    1) Código numérico de 3 dígitos (ex: '049 - PRODUÇÃO ...')
    2) Fallback por nome quando não houver código
    """
    s  = str(op)
    su = s.upper()

    # Extrai código de 3 dígitos no início (se houver)
    m   = _COD_RE.match(s)
    cod = m.group(1) if m else None

    # 1. PRODUTIVO - lista explícita de códigos
    if cod is not None and cod in OP_PRODUTIVAS_COD:
        return "01. PRODUTIVO"
    if any(nome.upper() in su for nome in OP_PRODUTIVAS_NOMES):
        return "01. PRODUTIVO"

    # 2. MANUTENÇÃO PREVENTIVA
    if "PREVENTIVA" in su:
        return "02. MANUT. PREVENTIVA"

    # 3. MANUTENÇÃO CORRETIVA
    if "CORRETIVA" in su:
        return "03. MANUT. CORRETIVA"

    # 4. SETUP
    if "SETUP" in su or "AJUSTE DE COR" in su or "TROCA DE FACA" in su:
        return "04. SETUP"

    return "05. OUTROS IMPRODUTIVOS"
