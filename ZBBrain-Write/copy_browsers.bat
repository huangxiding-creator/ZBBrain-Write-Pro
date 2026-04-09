@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo ZBBrain-Write Playwright浏览器复制工具
echo ============================================================
echo.

set "PROJECT_DIR=%~dp0"
set "BROWSERS_DIR=%PROJECT_DIR%portable\browsers"
set "SOURCE_DIR=%LOCALAPPDATA%\ms-playwright"

:: 检查源目录
if not exist "%SOURCE_DIR%" (
    echo 错误：未找到系统Playwright浏览器目录
    echo 预期位置：%SOURCE_DIR%
    echo.
    echo 请先运行以下命令安装浏览器：
    echo   python -m playwright install chromium
    pause
    exit /b 1
)

:: 显示可用浏览器
echo 找到以下浏览器：
echo.
for /d %%d in ("%SOURCE_DIR%\chromium-*") do (
    echo   [1] %%~nxd
)
for /d %%d in ("%SOURCE_DIR%\firefox-*") do (
    echo   [2] %%~nxd
)
for /d %%d in ("%SOURCE_DIR%\webkit-*") do (
    echo   [3] %%~nxd
)
echo.

set /p "CONFIRM=是否复制Chromium浏览器到项目目录？(Y/n): "
if /i "!CONFIRM!"=="n" (
    echo 操作已取消
    pause
    exit /b 0
)

:: 创建目标目录
if not exist "%BROWSERS_DIR%" mkdir "%BROWSERS_DIR%"

:: 复制最新版本的Chromium
echo.
echo 正在复制浏览器文件（约400MB），请耐心等待...

:: 找到最新的chromium版本
set "LATEST_CHROMIUM="
for /f "delims=" %%d in ('dir /b /ad "%SOURCE_DIR%\chromium-???? 2>nul"') do (
    set "LATEST_CHROMIUM=%%d"
)

if "%LATEST_CHROMIUM%"=="" (
    echo 错误：未找到Chromium浏览器
    pause
    exit /b 1
)

echo 复制 %LATEST_CHROMIUM%...
xcopy "%SOURCE_DIR%\%LATEST_CHROMIUM%" "%BROWSERS_DIR%\%LATEST_CHROMIUM%\" /E /I /Q /Y

:: 复制对应的headless shell
set "HEADLESS_VER=%LATEST_CHROMIUM:chromium-=chromium_headless_shell-%"
if exist "%SOURCE_DIR%\%HEADLESS_VER%" (
    echo 复制 %HEADLESS_VER%...
    xcopy "%SOURCE_DIR%\%HEADLESS_VER%" "%BROWSERS_DIR%\%HEADLESS_VER%\" /E /I /Q /Y
)

:: 复制.links目录
if exist "%SOURCE_DIR%\.links" (
    echo 复制 .links...
    xcopy "%SOURCE_DIR%\.links" "%BROWSERS_DIR%\.links\" /E /I /Q /Y
)

echo.
echo ============================================================
echo                  复制完成！
echo ============================================================
echo.
echo 浏览器已复制到：
echo   %BROWSERS_DIR%
echo.
dir /b "%BROWSERS_DIR%"
echo.
pause
