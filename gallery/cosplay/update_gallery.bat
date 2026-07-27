@echo off
REM ==========================================================================
REM  Identity Forge - publish the COSPLAY sample gallery
REM
REM  Drag a folder of images onto this file, or run it and type the path.
REM  Images must be named after the entry: "Batman.jpeg", "Chun-Li.png", ...
REM
REM  Entries you do NOT supply an image for are left completely alone.
REM  Nothing is ever deleted by this script.
REM
REM  ONE OF THREE NEAR-IDENTICAL COPIES (cosplay / archetypes / creatures).
REM  Fix a bug here and apply it to the other two - see gallery\README.md.
REM ==========================================================================
setlocal
set "GALLERY=cosplay"
set "HERE=%~dp0"
set "REPO=%HERE%..\.."

title Identity Forge - update %GALLERY% gallery

echo.
echo ==========================================================
echo   Identity Forge - %GALLERY% gallery
echo ==========================================================
echo.

REM --- source folder: dragged onto the .bat, or typed at the prompt ---------
set "SOURCE=%~1"
if not defined SOURCE goto :ask
goto :havesource

:ask
echo Drop the folder of images here, or paste its path.
echo Leave it blank and press Enter to cancel.
echo.
set /p "SOURCE=Source folder: "
if not defined SOURCE goto :cancelled

:havesource
REM Strip surrounding quotes that drag-and-drop adds.
set "SOURCE=%SOURCE:"=%"
if not exist "%SOURCE%\" goto :nosource

REM --- mode ----------------------------------------------------------------
echo.
echo Which entries should be written?
echo.
echo   [1] Add only what is missing        - default, safest
echo   [2] Add missing AND replace existing
echo   [3] Preview only, change nothing    - dry run
echo.
set "CHOICE="
set /p "CHOICE=Choose 1, 2 or 3 [1]: "
if not defined CHOICE set "CHOICE=1"

set "FLAGS="
if "%CHOICE%"=="1" set "FLAGS="
if "%CHOICE%"=="2" set "FLAGS=--overwrite"
if "%CHOICE%"=="3" set "FLAGS=--dry-run"
if "%CHOICE%"=="1" goto :run
if "%CHOICE%"=="2" goto :run
if "%CHOICE%"=="3" goto :run
goto :badchoice

:run
echo.
echo ----------------------------------------------------------
python "%HERE%publish.py" --source "%SOURCE%" %FLAGS%
if errorlevel 1 goto :failed
echo ----------------------------------------------------------
echo.
echo Finished.
echo.
pause
endlocal
exit /b 0

:nosource
echo.
echo ERROR: that folder does not exist:
echo   %SOURCE%
echo.
pause
endlocal
exit /b 1

:badchoice
echo.
echo ERROR: "%CHOICE%" is not one of 1, 2 or 3.
echo.
pause
endlocal
exit /b 1

:failed
echo ----------------------------------------------------------
echo.
echo FAILED. The gallery was NOT updated. Read the messages above.
echo.
echo Common causes:
echo   - Pillow is not installed        fix: pip install Pillow
echo   - not signed in to git/GitHub    fix: check your credentials
echo   - the gh-pages branch moved      fix: git fetch origin
echo.
pause
endlocal
exit /b 1

:cancelled
echo.
echo Cancelled - nothing was changed.
echo.
pause
endlocal
exit /b 0
