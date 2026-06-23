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

OP_PRODUTIVAS = [
    'PRODUÇÃO FLEXOGRÁFICO',
    'PRODUÇÃO OFFSET',
    'APLICANDO TRATAMENTO EM MP',
    'PRODUÇÃO PEÇA',
    'REFILE MP AVULSO',
    'IMPRESSÃO INTERNA',
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
