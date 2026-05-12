@echo off
setlocal
cd /d "%~dp0"
set "LOG_FILE=data\boot.log"
set "FLAG_FILE=data\installed.flag"

echo [INICIANDO]> "%LOG_FILE%"

:: 1. Verificação ultra-rápida de Python
echo Verificando motor... > "%LOG_FILE%"
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO_PYTHON > "%LOG_FILE%"
    exit /b
)

:: 2. Só instala bibliotecas se for a primeira vez ou se a pasta data estiver limpa
if not exist "%FLAG_FILE%" (
    echo Preparando ambiente pela primeira vez... > "%LOG_FILE%"
    python -m pip install -r backend\requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ERRO_LIBS > "%LOG_FILE%"
        exit /b
    )
    echo OK > "%FLAG_FILE%"
)

echo Ligando o Motor... > "%LOG_FILE%"
echo [OK] Pronto! >> "%LOG_FILE%"

:: Iniciar o backend
python backend\main.py 2> data\error.log
