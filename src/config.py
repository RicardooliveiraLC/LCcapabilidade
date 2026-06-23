from pathlib import Path

ROOT           = Path(__file__).parent.parent
CONFIG_MAQ     = ROOT / "config" / "config_maq.xlsx"
DIAS_UTEIS     = ROOT / "config" / "dias_uteis.xlsx"
ENTRADA_DIR    = ROOT / "dados" / "entrada"
PROCESSADO_DIR = ROOT / "dados" / "processado"
HISTORICO_PATH = ROOT / "dados" / "historico.parquet"
TEMPLATE_PATH  = ROOT / "templates" / "dashboard.html.j2"
DASHBOARD_OUT  = ROOT / "dashboard" / "index.html"
DOCS_OUT       = ROOT / "docs" / "index.html"
ROOT_OUT       = ROOT / "index.html"

# Códigos de operações PRODUTIVAS (definidos pelo usuário)
# 049 - PRODUÇÃO FLEXOGRÁFICO
# 050 - PRODUÇÃO OFFSET
# 055 - APLICANDO TRATAMENTO EM MP
# 056 - PRODUÇÃO OFFSET
# 078 - REVISÃO MÁQUINA FLEXO
# 083 - REVISÃO MÁQUINA FLEXO
# 085 - REVISÃO MÁQUINA FLEXO PC
# 011 - REVISÃO MANUAL
OP_PRODUTIVAS_COD = {"049", "050", "055", "056", "078", "083", "085", "011"}

# Fallback por nome (caso a operação venha sem código)
OP_PRODUTIVAS_NOMES = [
    "PRODUÇÃO FLEXOGRÁFICO",
    "PRODUCAO FLEXOGRAFICO",
    "PRODUÇÃO OFFSET",
    "PRODUCAO OFFSET",
    "APLICANDO TRATAMENTO EM MP",
    "REVISÃO MÁQUINA FLEXO",
    "REVISAO MAQUINA FLEXO",
    "REVISÃO MANUAL",
    "REVISAO MANUAL",
]

CATEGORIAS = [
    "01. PRODUTIVO",
    "02. MANUT. PREVENTIVA",
    "03. MANUT. CORRETIVA",
    "04. SETUP",
    "05. OUTROS IMPRODUTIVOS",
]

CHAVE_DEDUP = [
    'Número da Ordem',
    'Máquina',
    'Data de Início',
    'Hora de Início',
    'Operação',
]
