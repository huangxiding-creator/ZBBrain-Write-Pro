@echo off
REM ZBBrainArticle 部署脚本 (Windows)

if "%1"=="" (
    echo 使用方法: deploy.bat ^<version^> [environment]
    echo 示例: deploy.bat 2.5.0 production
    exit /b 1
)

set VERSION=%1
set ENVIRONMENT=%2

if "%ENVIRONMENT%"=="" set ENVIRONMENT=staging

echo 正在部署版本 %VERSION% 到 %ENVIRONMENT% 环境...
python deploy.py --version %VERSION% --environment %ENVIRONMENT%

if errorlevel 1 (
    echo 部署失败！
    exit /b 1
) else (
    echo 部署成功！
    exit /b 0
)
