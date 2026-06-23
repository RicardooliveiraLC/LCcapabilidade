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

echo.
echo Sincronizando com GitHub...
git add docs\index.html index.html
if errorlevel 1 (
    echo. [AVISO] Git nao disponivel ou repo nao inicializado.
    echo.
) else (
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
    git commit -m "dashboard atualizado - %mydate% %mytime%"
    if errorlevel 1 (
        echo. [OK] Nada novo para commitar.
    ) else (
        git push
        if errorlevel 1 (
            echo. [AVISO] Erro ao fazer push. Verifique sua conexao com GitHub.
        ) else (
            echo. [OK] Dashboard sincronizado com GitHub Pages ^!
        )
    )
)
pause
