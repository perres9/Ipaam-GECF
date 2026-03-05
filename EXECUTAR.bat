@echo off
title IPAAM - Mapa de Licencas Ambientais
color 0A
cd /d "%~dp0"
cls
echo.
echo   ======================================================
echo   =                                                    =
echo   =                      IPAAM                         =
echo   =                                                    =
echo   =     Instituto de Protecao Ambiental do Amazonas   =
echo   =                                                    =
echo   =     Mapa Historico de Licencas Ambientais         =
echo   =                                                    =
echo   =     Estagiario - Anizio Filho                     =
echo   =                                                    =
echo   ======================================================
echo.
echo   Iniciando processamento...
echo.
call .venv\Scripts\activate.bat
python main.py
echo.
echo   Abrindo mapa no navegador...
start "" "output\mapa_ipaam_premium.html"
echo.
echo   ======================================================
echo   =         Processo concluido com sucesso!           =
echo   ======================================================
echo.
echo   Pressione qualquer tecla para fechar...
pause >nul
