@echo off
echo ========================================
echo Cleaning up files before Git commit
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Checking for sensitive files...
echo.

REM Check for .env file
if exist .env (
    echo [WARNING] Found .env file with potential secrets!
    echo [ACTION] This file is in .gitignore, will not be committed
    echo.
) else (
    echo [OK] No .env file found
    echo.
)

echo Step 2: Removing old/deprecated directories from staging...
echo.

REM These directories should NOT be committed
for %%D in (ai_news analyzer evaluation evolution executor monitor optimizer patches) do (
    if exist "%%D\" (
        echo [INFO] Directory '%%D\' exists but is excluded by .gitignore
    )
)

echo Step 3: Checking for large internal documents...
echo.

if exist ARCHITECTURE_LIMITATIONS.md (
    echo [WARNING] ARCHITECTURE_LIMITATIONS.md (72.9KB) - Internal document
    echo [ACTION] Excluded by .gitignore
)

if exist ARCHITECTURE_LIMITATION_MODIFY.md (
    echo [WARNING] ARCHITECTURE_LIMITATION_MODIFY.md (429.4KB) - Large internal document
    echo [ACTION] Excluded by .gitignore
)

echo.
echo Step 4: Verifying .gitignore rules...
echo.

REM Test .gitignore
echo Testing .gitignore patterns...
git check-ignore ARCHITECTURE_LIMITATIONS.md >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ARCHITECTURE_LIMITATIONS.md is ignored
) else (
    echo [ERROR] ARCHITECTURE_LIMITATIONS.md is NOT ignored!
)

git check-ignore ARCHITECTURE_LIMITATION_MODIFY.md >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ARCHITECTURE_LIMITATION_MODIFY.md is ignored
) else (
    echo [ERROR] ARCHITECTURE_LIMITATION_MODIFY.md is NOT ignored!
)

git check-ignore ai_news/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ai_news/ is ignored
) else (
    echo [ERROR] ai_news/ is NOT ignored!
)

echo.
echo Step 5: Checking for API keys in code...
echo.

REM Search for common API key patterns
findstr /S /I /C:"api_key = \"sk-" *.py >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Found potential API keys in Python files!
    echo [ACTION] Review and remove before committing
    findstr /S /I /C:"api_key = \"sk-" *.py
) else (
    echo [OK] No obvious API keys found in current directory
)

echo.
echo ========================================
echo Cleanup check complete!
echo ========================================
echo.
echo Next steps:
echo 1. Review the warnings above
echo 2. Remove any sensitive files manually if needed
echo 3. Run: git add .
echo 4. Run: git status (verify only intended files are staged)
echo 5. Run: git commit -m "Your message"
echo.
pause
