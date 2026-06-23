@echo off
title Label Code - Capabilidade Produtiva
cd /d "%~dp0"
cls

echo ======================================================
echo   CAPABILIDADE PRODUTIVA - LABEL CODE
echo ======================================================
echo.

:: Instala dependencias se necessario
pip show pandas >nul 2>&1 || (
    echo Instalando dependencias...
    pip install -r requirements.txt
    echo.
)

if "%~1"=="" (
    :: Sem arquivos arrastados - processa pasta entrada/
    echo Processando arquivos em dados\entrada\ ...
    python -m src.main
) else (
    :: Arquivos arrastados sobre o bat
    echo Processando arquivos arrastados...
    python -m src.main %*
)

echo.
echo ======================================================
echo   PROCESSO FINALIZADO
echo ======================================================
echo.
echo Abrindo dashboard...
start "" "%~dp0dashboard\index.html"
pause
