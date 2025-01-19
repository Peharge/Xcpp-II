@echo off
REM Das Skript startet die Python-Programme test2.py und model3.py, wobei model3.py 10 Sekunden später gestartet wird

REM Pfad zum Python-Interpreter
set PYTHON_PATH=C:\Users\%USERNAME%\PycharmProjects\Xcpp\.venv\Scripts\python.exe

REM Pfad zu deinen Python-Skripten
set SCRIPT_PATH1=C:\Users\%USERNAME%\PycharmProjects\Xcpp\main\test2.py
set SCRIPT_PATH2=C:\Users\%USERNAME%\PycharmProjects\Xcpp\main\model4.py

REM Skript 1 starten
start "" /B "%PYTHON_PATH%" "%SCRIPT_PATH1%"

REM 10 Sekunden warten
timeout /T 10 /NOBREAK

REM Skript 2 starten
start "" /B "%PYTHON_PATH%" "%SCRIPT_PATH2%"

REM Konsole offen halten
echo Both scripts are running... Press any key to exit.
pause
