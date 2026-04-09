@echo off
chcp 65001 >nul
echo ============================================
echo   总包大脑文章自动生成器 - GUI模式
echo ============================================
echo.
echo 正在启动图形界面...
echo.

python ZBBrainArticle_GUI.py

if errorlevel 1 (
    echo.
    echo 启动失败！请检查Python是否已安装。
    echo.
    pause
)
