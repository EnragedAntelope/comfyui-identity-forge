@echo off
REM ============================================================
REM  Identity Forge Cosplay Gallery — Build & Deploy
REM
REM  Drop new JPEGs into your source folder, then run this.
REM  It optimizes images, regenerates the manifest, and deploys
REM  to gh-pages (GitHub Pages).  Existing images are skipped.
REM
REM  Usage:   gallery_update.bat
REM           gallery_update.bat C:\my\new\images
REM
REM  Default source folder if none given:
REM           D:\tempforgithubrepo\identityforge
REM ============================================================

setlocal enabledelayedexpansion

REM --- Paths ---
set "REPO=C:\github_projects\comfyui-identity-forge"
set "BUILD_SCRIPT=%REPO%\gallery\cosplay\build_gallery_images.py"
set "MANIFEST_SCRIPT=%REPO%\gallery\cosplay\build_manifest.py"
set "DEPLOY_SCRIPT=%REPO%\gallery\cosplay\deploy.py"

REM --- Source folder (first argument, or default) ---
if "%~1"=="" (
    set "SOURCE=D:\tempforgithubrepo\identityforge"
) else (
    set "SOURCE=%~1"
)

echo.
echo ============================================================
echo   Identity Forge Gallery — Build ^& Deploy
echo ============================================================
echo   Source:  %SOURCE%
echo   Repo:    %REPO%
echo ============================================================
echo.

REM --- Check source folder exists ---
if not exist "%SOURCE%\" (
    echo ERROR: Source folder not found: %SOURCE%
    pause
    exit /b 1
)

REM --- Step 1: Optimize images (incremental - skip existing) ---
echo [1/3] Optimizing new images...
python "%BUILD_SCRIPT%" --source "%SOURCE%" --skip-existing
if errorlevel 1 (
    echo ERROR: Image optimization failed.
    pause
    exit /b 1
)

REM --- Step 2: Regenerate manifest ---
echo.
echo [2/3] Regenerating manifest...
python "%MANIFEST_SCRIPT%"
if errorlevel 1 (
    echo ERROR: Manifest generation failed.
    pause
    exit /b 1
)

REM --- Step 3: Deploy to gh-pages ---
echo.
echo [3/3] Deploying to gh-pages...
python "%DEPLOY_SCRIPT%"
if errorlevel 1 (
    echo ERROR: Deployment failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Done! Gallery updated:
echo   https://enragedantelope.github.io/comfyui-identity-forge/gallery/cosplay/
echo ============================================================
echo.
pause
