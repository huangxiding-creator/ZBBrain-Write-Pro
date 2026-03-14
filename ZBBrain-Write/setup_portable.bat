@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo ZBBrain-Write 便携式部署工具
echo EPC总承包微信公众号自动化文章生成工具
echo ============================================================
echo.

:: 设置项目根目录
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: 步骤1: 检查Python嵌入式版本
echo [步骤 1/5] 检查Python环境...
if exist "portable\python\python.exe" (
    echo     √ 找到嵌入式Python
    set "PYTHON_CMD=portable\python\python.exe"
) else (
    echo     ! 未找到嵌入式Python，使用系统Python
    where python >nul 2>&1
    if errorlevel 1 (
        echo     × 错误：未找到Python，请先安装Python 3.9+
        echo     下载地址：https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

:: 步骤2: 安装Python依赖
echo.
echo [步骤 2/5] 安装Python依赖包...
%PYTHON_CMD% -m pip install --upgrade pip -q
%PYTHON_CMD% -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo     × 依赖安装失败，尝试使用国内镜像...
    %PYTHON_CMD% -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ -q
)
echo     √ 依赖安装完成

:: 步骤3: 安装Playwright浏览器
echo.
echo [步骤 3/5] 安装Playwright浏览器...
if exist "portable\browsers\chromium" (
    echo     √ 找到本地浏览器缓存
    set "PLAYWRIGHT_BROWSERS_PATH=%PROJECT_DIR%portable\browsers"
) else (
    echo     正在下载Chromium浏览器（约400MB）...
    set "PLAYWRIGHT_BROWSERS_PATH=%PROJECT_DIR%portable\browsers"
    %PYTHON_CMD% -m playwright install chromium
    if errorlevel 1 (
        echo     × 浏览器安装失败
        pause
        exit /b 1
    )
)
echo     √ 浏览器准备完成

:: 步骤4: 验证配置文件
echo.
echo [步骤 4/5] 验证配置文件...
if not exist "config.ini" (
    if exist "config.ini.example" (
        echo     复制配置模板...
        copy "config.ini.example" "config.ini" >nul
        echo     ! 请编辑 config.ini 填入您的API密钥
    ) else (
        echo     × 错误：未找到config.ini
        pause
        exit /b 1
    )
)
echo     √ 配置文件就绪

:: 步骤5: 创建必要的目录
echo.
echo [步骤 5/5] 创建必要的目录...
if not exist "temp" mkdir temp
if not exist "browser_data" mkdir browser_data
if not exist "image" mkdir image
if not exist "logs" mkdir logs
echo     √ 目录创建完成

echo.
echo ============================================================
echo                  部署完成！
echo ============================================================
echo.
echo 运行方式：
echo   1. 双击 run.bat 运行命令行版本
echo   2. 双击 run_gui.bat 运行图形界面版本
echo.
echo 首次运行前，请确保：
echo   1. 编辑 config.ini 填入智谱AI API密钥
echo   2. 添加微信公众号 AppID 和 AppSecret
echo   3. 如需广告图，放入 image/top-image.jpg 和 bottom-image.jpg
echo.
pause
