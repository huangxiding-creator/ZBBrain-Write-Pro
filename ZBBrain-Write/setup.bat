@echo off
REM ZBBrainArticle Setup Script for Windows
REM 总包大脑文章自动生成脚本 - Windows安装脚本

echo ====================================
echo ZBBrainArticle 安装脚本
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.9或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] 检测到Python版本:
python --version
echo.

REM 检查pip是否可用
pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] pip不可用
    pause
    exit /b 1
)

echo [2/6] 升级pip到最新版本...
python -m pip install --upgrade pip
echo.

echo [3/6] 安装Python依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖包安装失败
    pause
    exit /b 1
)
echo.

echo [4/6] 安装Playwright浏览器...
python -m playwright install
python -m playwright install chromium
echo.

echo [5/6] 创建必要的目录...
if not exist "browser_data" mkdir browser_data
if not exist "temp" mkdir temp
echo.

echo [6/6] 检查md2wechat工具...
md2wechat --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到md2wechat工具
    echo 请手动安装md2wechat:
    echo 1. 访问 https://github.com/geekjourneyx/md2wechat-skill/releases
    echo 2. 下载 md2wechat-windows-amd64.exe
    echo 3. 重命名为 md2wechat.exe
    echo 4. 复制到 C:\Windows\System32\ 或当前目录
    echo.
) else (
    echo [OK] md2wechat工具已安装
)
echo.

echo ====================================
echo 安装完成！
echo ====================================
echo.
echo 下一步:
echo 1. 复制 config.ini.example 为 config.ini
echo 2. 编辑 config.ini 填入您的配置信息
echo 3. 准备一张封面图片 (900x500px JPG) 命名为 cover.jpg
echo 4. 运行: python ZBBrainArticle.py
echo.
echo 更多信息请查看 README.md
echo.

pause
