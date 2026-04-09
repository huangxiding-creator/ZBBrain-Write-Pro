@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置项目根目录
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: 设置Playwright浏览器路径
set "PLAYWRIGHT_BROWSERS_PATH=%PROJECT_DIR%portable\browsers"

:: 检查Python环境
if exist "portable\python\python.exe" (
    set "PYTHON_CMD=portable\python\python.exe"
) else (
    set "PYTHON_CMD=python"
)

:: 运行GUI程序
start "" %PYTHON_CMD% ZBBrainArticle_GUI.py
