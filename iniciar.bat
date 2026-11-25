@echo off
REM =============================================================================
REM iniciar.bat — prepara e sobe o ambiente no Windows (cmd / PowerShell da FATEC)
REM sem precisar alterar ExecutionPolicy do PowerShell.
REM
REM   iniciar.bat                     tudo: venv -> deps -> runserver do SGS (porta 6100)
REM   iniciar.bat tudo [porta]        tudo, em outra porta
REM   iniciar.bat preparar            cria .venv e instala dependencias (sem subir servidor)
REM   iniciar.bat ativar              prepara (se precisar) e ATIVA o .venv neste terminal cmd
REM   iniciar.bat provap3 [porta]     prepara e sobe o sistema provaP3 (.env, migrations, admin, runserver)
REM   iniciar.bat sistema <nome> [p]  prepara e sobe qualquer sistema em sistemas_gerados\<nome>
REM   iniciar.bat testar [filtro]     roda pytest do SGS (ou de um sistema)
REM   iniciar.bat rodar [porta]       sobe o SGS na porta indicada (padrao: 6100)
REM   iniciar.bat ajuda               mostra esta ajuda
REM =============================================================================

set "DJANGO_SETTINGS_MODULE="
set "RAIZ=%~dp0"
if "%RAIZ:~-1%"=="\" set "RAIZ=%RAIZ:~0,-1%"
set "SGS_DIR=%RAIZ%\Gerador_Sistemas"
set "VENV=%SGS_DIR%\.venv"
set "VENV_PY=%VENV%\Scripts\python.exe"
set "REQ_FILE=%SGS_DIR%\requirements.txt"

set "CMD=%~1"
if "%CMD%"=="" set "CMD=tudo"

if /I "%CMD%"=="ajuda" goto :ajuda
if /I "%CMD%"=="-h" goto :ajuda
if /I "%CMD%"=="--help" goto :ajuda

if /I "%CMD%"=="ativar" goto :cmd_ativar

setlocal enabledelayedexpansion
set "DJANGO_SETTINGS_MODULE="

if /I "%CMD%"=="tudo" (
  call :garantir_ambiente || exit /b 1
  call :rodar_sgs "%~2" || exit /b 1
  exit /b 0
)
if /I "%CMD%"=="preparar" (
  call :garantir_ambiente || exit /b 1
  echo.
  echo Ambiente pronto! Para ativar no cmd atual:
  echo   iniciar.bat ativar
  echo Para subir o SGS:
  echo   iniciar.bat
  echo Para subir a Prova P3:
  echo   iniciar.bat provap3
  exit /b 0
)
if /I "%CMD%"=="venv" (
  call :criar_venv || exit /b 1
  exit /b 0
)
if /I "%CMD%"=="deps" (
  call :garantir_ambiente || exit /b 1
  exit /b 0
)
if /I "%CMD%"=="provap3" (
  call :garantir_ambiente || exit /b 1
  call :rodar_sistema "provaP3" "%~2" || exit /b 1
  exit /b 0
)
if /I "%CMD%"=="sistema" (
  if "%~2"=="" (
    echo Uso: iniciar.bat sistema ^<nome_da_pasta^> [porta]
    exit /b 2
  )
  call :garantir_ambiente || exit /b 1
  call :rodar_sistema "%~2" "%~3" || exit /b 1
  exit /b 0
)
if /I "%CMD%"=="testar" (
  call :garantir_ambiente || exit /b 1
  if "%~2"=="" (
    pushd "%SGS_DIR%"
    "%VENV_PY%" -m pytest -q -p no:cacheprovider
    set "RC=!errorlevel!"
    popd
    exit /b !RC!
  ) else (
    pushd "%SGS_DIR%\sistemas_gerados\%~2"
    "%VENV_PY%" -m pytest -q -p no:cacheprovider
    set "RC=!errorlevel!"
    popd
    exit /b !RC!
  )
)
if /I "%CMD%"=="rodar" (
  call :garantir_ambiente || exit /b 1
  call :rodar_sgs "%~2" || exit /b 1
  exit /b 0
)

echo Comando desconhecido: %CMD%  (veja: iniciar.bat ajuda)
exit /b 2

:cmd_ativar
call :garantir_ambiente_sem_local || exit /b 1
if exist "%VENV%\Scripts\activate.bat" (
  call "%VENV%\Scripts\activate.bat"
  echo Ambiente ativado: %VENV%
  exit /b 0
)
echo ERRO: nao encontrei %VENV%\Scripts\activate.bat
exit /b 1

:garantir_ambiente_sem_local
if not exist "%VENV_PY%" (
  call :criar_venv_base || exit /b 1
)
"%VENV_PY%" -m pip install -q --disable-pip-version-check --no-index -r "%REQ_FILE%" >nul 2>&1
if errorlevel 1 (
  echo.
  echo ==^> instalando dependencias de %REQ_FILE%
  "%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
  "%VENV_PY%" -m pip install -r "%REQ_FILE%" || exit /b 1
)
exit /b 0

:criar_venv_base
set "PY_BASE="
py -3 -c "import sys; sys.exit(sys.version_info < (3, 12))" >nul 2>&1
if not errorlevel 1 set "PY_BASE=py -3"
if "%PY_BASE%"=="" (
  python -c "import sys; sys.exit(sys.version_info < (3, 12))" >nul 2>&1
  if not errorlevel 1 set "PY_BASE=python"
)
if "%PY_BASE%"=="" (
  echo ERRO: este projeto precisa do Python 3.12 ou mais novo ^(Django 6^).
  exit /b 1
)
echo.
echo ==^> criando ambiente virtual em %VENV% ^(com %PY_BASE%^)
%PY_BASE% -m venv "%VENV%" || (
  rmdir /s /q "%VENV%" 2>nul
  echo ERRO: falhou ao criar o ambiente virtual em %VENV%.
  exit /b 1
)
exit /b 0

:garantir_ambiente
call :criar_venv || exit /b 1
call :instalar_deps || exit /b 1
exit /b 0

:criar_venv
if exist "%VENV_PY%" (
  echo ambiente ok: %VENV_PY%
  exit /b 0
)
call :criar_venv_base || exit /b 1
exit /b 0

:instalar_deps
"%VENV_PY%" -m pip install -q --disable-pip-version-check --no-index -r "%REQ_FILE%" >nul 2>&1
if not errorlevel 1 (
  echo dependencias ok ^(todas as do requirements.txt ja estao instaladas^)
  exit /b 0
)
echo.
echo ==^> instalando dependencias de %REQ_FILE%
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
"%VENV_PY%" -m pip install -r "%REQ_FILE%" || exit /b 1
exit /b 0

:rodar_sgs
set "PORTA=%~1"
if "%PORTA%"=="" set "PORTA=6100"
"%VENV_PY%" -c "import socket, sys; s=socket.socket(); rc=s.connect_ex(('127.0.0.1', int(sys.argv[1]))); s.close(); sys.exit(0 if rc != 0 else 1)" "%PORTA%"
if errorlevel 1 (
  echo ERRO: a porta %PORTA% ja esta em uso. Tente outra porta: iniciar.bat rodar 6150
  exit /b 1
)
echo.
echo ==^> subindo o SGS em http://127.0.0.1:%PORTA%/  (Ctrl+C para parar)
pushd "%RAIZ%"
set "DJANGO_SETTINGS_MODULE="
"%VENV_PY%" manage.py runserver 127.0.0.1:%PORTA%
set "RC=%errorlevel%"
popd
exit /b %RC%

:rodar_sistema
set "SYS_NOME=%~1"
set "SYS_PORTA=%~2"
set "SYS_DIR=%SGS_DIR%\sistemas_gerados\%SYS_NOME%"
set "SYS_WEB=%SYS_DIR%\web"
if not exist "%SYS_WEB%\manage.py" (
  echo ERRO: sistema Django nao encontrado em %SYS_DIR%
  exit /b 1
)
if exist "%SYS_DIR%\requirements.txt" (
  "%VENV_PY%" -m pip install -q --disable-pip-version-check --no-index -r "%SYS_DIR%\requirements.txt" >nul 2>&1
  if errorlevel 1 (
    echo.
    echo ==^> instalando dependencias de %SYS_NOME%\requirements.txt
    "%VENV_PY%" -m pip install -r "%SYS_DIR%\requirements.txt" || exit /b 1
  )
)
if exist "%SYS_WEB%\.env.example" (
  if not exist "%SYS_WEB%\.env" (
    echo.
    echo ==^> criando %SYS_NOME%\web\.env a partir de .env.example
    "%VENV_PY%" -c "import pathlib, re, secrets, sys; src=pathlib.Path(sys.argv[1]); dst=pathlib.Path(sys.argv[2]); t=src.read_text(encoding='utf-8'); dst.write_text(re.sub(r'^SECRET_KEY=.*$', 'SECRET_KEY=' + secrets.token_urlsafe(40), t, flags=re.M), encoding='utf-8', newline='\n')" "%SYS_WEB%\.env.example" "%SYS_WEB%\.env" || exit /b 1
  ) else (
    echo %SYS_NOME%\web\.env ok ^(ja existe — nao sobrescrevo^)
  )
)
echo.
echo ==^> migrations de %SYS_NOME%
pushd "%SYS_WEB%"
set "DJANGO_SETTINGS_MODULE="
"%VENV_PY%" manage.py makemigrations || (popd & exit /b 1)
"%VENV_PY%" manage.py migrate || (popd & exit /b 1)
"%VENV_PY%" manage.py garantir_admin 2>nul
if "%SYS_PORTA%"=="" (
  for /f "tokens=2 delims==" %%P in ('findstr /B "PORTA=" "%SYS_WEB%\.env" 2^>nul') do set "SYS_PORTA=%%P"
)
if "%SYS_PORTA%"=="" set "SYS_PORTA=8000"
echo.
echo ==^> subindo %SYS_NOME% em http://127.0.0.1:%SYS_PORTA%/  (Ctrl+C para parar)
"%VENV_PY%" manage.py runserver 127.0.0.1:%SYS_PORTA%
set "RC=%errorlevel%"
popd
exit /b %RC%

:ajuda
echo Uso:
echo   iniciar.bat                     prepara .venv/deps e sobe o SGS (porta 6100)
echo   iniciar.bat tudo [porta]        prepara .venv/deps e sobe o SGS na porta indicada
echo   iniciar.bat preparar            cria .venv e instala dependencias (sem subir servidor)
echo   iniciar.bat ativar              prepara (se precisar) e ativa o .venv neste terminal cmd
echo   iniciar.bat provap3 [porta]     prepara e sobe o sistema provaP3 (.env, migrations, admin, runserver)
echo   iniciar.bat sistema ^<nome^> [p]  prepara e sobe qualquer sistema em sistemas_gerados\^<nome^>
echo   iniciar.bat testar [nome]       roda pytest do SGS (ou de um sistema especifico)
echo   iniciar.bat rodar [porta]       sobe o SGS na porta indicada (padrao: 6100)
exit /b 0
