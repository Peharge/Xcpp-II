@echo off
setlocal

REM Setzt den Pfad zur Python-Installation in der virtuellen Umgebung
set "VENV_PATH=C:\Users\julia\PycharmProjects\Xcpp\.venv\Scripts"
if not exist "%VENV_PATH%\python.exe" (
    echo Python-Interpreter in der virtuellen Umgebung nicht gefunden. Bitte überprüfen Sie den Pfad.
    exit /b 1
)
set "PATH=%VENV_PATH%;%PATH%"

REM Wechselt in das Verzeichnis des Python-Projekts
cd /d "C:\Users\julia\PycharmProjects\Xcpp" || (
    echo Projektverzeichnis nicht gefunden. Bitte überprüfen Sie den Pfad.
    exit /b 1
)

REM Debug-Ausgabe des aktuellen Verzeichnisses
echo Aktuelles Verzeichnis: %CD%

REM Überprüft, ob die Datei existiert
if not exist "paswort1.py" (
    echo Datei "paswort1.py" nicht gefunden. Bitte überprüfen Sie den Dateipfad.
    exit /b 1
)

REM Führt das Python-Skript aus
python "paswort1.py"
if errorlevel 1 (
    echo Fehler beim Ausführen des Python-Skripts.
    exit /b 1
)

echo Python-Skript erfolgreich ausgeführt.
exit /b 0
