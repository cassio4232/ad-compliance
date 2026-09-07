@echo off
title AdCompliance Inspector - YouTube Ads ^& Demand Gen
cd /d "%~dp0"

echo ================================================================
echo    ADCOMPLIANCE INSPECTOR - DEMAND GEN & YOUTUBE ADS
echo ================================================================
echo.
echo [*] Iniciando o servidor do aplicativo...
echo [*] Voce pode acessar no seu computador em: http://localhost:8501
echo [*] Para acessar pelo celular no mesmo Wi-Fi, abra o navegador e acesse:
for /f "tokens=4" %%a in ('route print ^| find " 0.0.0.0 "') do (
    echo     ==^> http://%%a:8501
    goto :done_ip
)
:done_ip
echo.
echo ================================================================
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause
