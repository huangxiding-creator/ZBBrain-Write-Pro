@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================
:: ZBBrain-Write 定时运行模式启动脚本
:: ============================================

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

:: 显示启动信息
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   ZBBrain-Write v3.4.0 - 定时运行模式                      ║
echo ║   EPC总承包微信公众号自动化文章生成工具                    ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║   模式: 定时调度器（启动时立即运行1次，之后按配置周期运行）║
echo ║   工作时间: 6:00 - 22:00 (北京时间)                        ║
echo ║   运行间隔: 每2小时                                        ║
echo ║   定时汇报: 每小时自动发送运行状态                         ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║   按 Ctrl+C 可安全停止运行                                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: 运行主程序（定时调度模式）
:: 不使用 --once 参数，启用内置定时调度器
%PYTHON_CMD% ZBBrainArticle.py %*

:: 如果程序异常退出，暂停以查看错误信息
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出，请检查日志文件
    pause
)
