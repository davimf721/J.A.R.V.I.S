@echo off
REM Script para iniciar Ollama no Windows
REM Execute este script em uma janela PowerShell ou CMD separada

echo.
echo ========================================
echo Parando Ollama (se estiver rodando)
echo ========================================
echo.

REM Procurar e matar processo ollama.exe
taskkill /IM ollama.exe /F /T 2>nul

if %ERRORLEVEL% EQU 0 (
    echo [INFO] Ollama parado com sucesso!
    timeout /t 2 >nul
) else (
    echo [INFO] Nenhum processo Ollama encontrado em execução
)

REM Aguardar um pouco para liberar a porta
timeout /t 3 >nul

echo.
echo ========================================
echo Iniciando Ollama Local
echo ========================================
echo.

REM Verificar se ollama está instalado
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Ollama não está instalado ou não está no PATH
    echo.
    echo Para instalar Ollama, visite: https://ollama.ai
    echo.
    pause
    exit /b 1
)

echo [INFO] Ollama encontrado!
echo [INFO] Iniciando servidor...
echo.

REM Iniciar Ollama
ollama serve

pause
