@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo ZBBrain-Write Python嵌入式环境下载工具
echo ============================================================
echo.

set "PROJECT_DIR=%~dp0"
set "PYTHON_VERSION=3.11.9"
set "PYTHON_EMBED_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "PYTHON_DIR=%PROJECT_DIR%portable\python"

:: 检查是否已存在
if exist "%PYTHON_DIR%\python.exe" (
    echo 嵌入式Python已存在于:
    echo   %PYTHON_DIR%
    echo.
    set /p "CONFIRM=是否重新下载？(y/N): "
    if /i not "!CONFIRM!"=="y" (
        echo 操作已取消
        pause
        exit /b 0
    )
    echo 删除旧版本...
    rmdir /s /q "%PYTHON_DIR%"
)

:: 创建目录
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"

:: 下载Python嵌入式版本
echo.
echo [1/4] 下载Python %PYTHON_VERSION% 嵌入式版本...
echo      URL: %PYTHON_EMBED_URL%

powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile '%PYTHON_DIR%\python-embed.zip' -UseBasicParsing }"

if not exist "%PYTHON_DIR%\python-embed.zip" (
    echo     × 下载失败
    pause
    exit /b 1
)
echo     √ 下载完成

:: 解压
echo.
echo [2/4] 解压Python文件...
powershell -Command "Expand-Archive -Path '%PYTHON_DIR%\python-embed.zip' -DestinationPath '%PYTHON_DIR%' -Force"
del "%PYTHON_DIR%\python-embed.zip"
echo     √ 解压完成

:: 修改._pth文件以启用site-packages
echo.
echo [3/4] 配置Python环境...
cd /d "%PYTHON_DIR%"
for %%f in (*._pth) do (
    echo import site>> "%%f"
    echo     √ 已配置 %%f
)

:: 下载pip
echo.
echo [4/4] 安装pip包管理器...
powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%PYTHON_DIR%\get-pip.py' -UseBasicParsing }"
"%PYTHON_DIR%\python.exe" "%PYTHON_DIR%\get-pip.py" --no-warn-script-location -q
del "%PYTHON_DIR%\get-pip.py"
echo     √ pip安装完成

:: 验证安装
echo.
echo ============================================================
echo                  安装完成！
echo ============================================================
echo.
echo Python嵌入式版本已安装到:
echo   %PYTHON_DIR%
echo.
"%PYTHON_DIR%\python.exe" --version
"%PYTHON_DIR%\python.exe" -m pip --version
echo.
echo 下一步：运行 setup_portable.bat 完成依赖安装
echo.
pause
