# ZBBrain-Write 便携式独立运行包

## 概述

本便携式包允许您将整个项目文件夹拷贝给他人，他们无需额外配置即可直接运行。

## 目录结构

```
ZBBrain-Write/
├── ZBBrainArticle.py          # 主程序
├── ZBBrainArticle_GUI.py      # GUI界面程序
├── config.ini                 # 配置文件（需要填写API密钥）
├── config.ini.example         # 配置文件模板
├── requirements.txt           # Python依赖列表
├── md2wechat.exe              # Markdown转微信格式工具
├── cover.jpg                  # 默认封面图片
│
├── portable/                  # 便携式环境目录
│   ├── python/                # 嵌入式Python（约60MB）
│   └── browsers/              # Playwright浏览器（约400MB）
│       └── chromium-xxxx/     # Chromium浏览器
│
├── image/                     # 广告图目录
│   ├── top-image.jpg          # 顶部广告图
│   └── bottom-image.jpg       # 底部广告图
│
├── temp/                      # 临时文件目录
├── browser_data/              # 浏览器用户数据
│
├── download_python.bat        # 下载嵌入式Python
├── copy_browsers.bat          # 复制Playwright浏览器
├── setup_portable.bat         # 一键安装依赖
├── run.bat                    # 运行命令行版本
└── run_gui.bat                # 运行GUI版本
```

## 快速开始（接收方操作指南）

### 方式一：完整便携包（推荐）

如果您收到了完整的便携式包（包含 `portable` 目录），操作非常简单：

1. **配置API密钥**
   - 编辑 `config.ini` 文件
   - 填入您的智谱AI API密钥（`api key`）
   - 填入微信公众号 AppID 和 AppSecret

2. **运行程序**
   - 双击 `run.bat` 运行命令行版本
   - 或双击 `run_gui.bat` 运行图形界面版本

### 方式二：精简包（需要联网安装）

如果您收到的是精简包（不包含 `portable` 目录），需要先安装环境：

1. **下载Python环境**（可选，如果系统已安装Python可跳过）
   ```
   双击 download_python.bat
   ```

2. **安装依赖和浏览器**
   ```
   双击 setup_portable.bat
   ```

3. **配置并运行**
   - 编辑 `config.ini` 填入API密钥
   - 双击 `run.bat` 或 `run_gui.bat` 运行

## 制作便携式包（发送方操作指南）

### 步骤1：下载Python嵌入式版本

```
双击 download_python.bat
```

这会下载Python 3.11.9嵌入式版本到 `portable/python/` 目录。

### 步骤2：复制Playwright浏览器

```
双击 copy_browsers.bat
```

这会将系统已安装的Chromium浏览器复制到 `portable/browsers/` 目录。

### 步骤3：安装Python依赖

```
双击 setup_portable.bat
```

这会安装所有必需的Python包到嵌入式Python环境中。

### 步骤4：打包项目

将以下文件和文件夹打包：

**必需文件：**
- `ZBBrainArticle.py`
- `ZBBrainArticle_GUI.py`
- `config.ini.example`（重命名为 `config.ini` 让接收方填写）
- `requirements.txt`
- `md2wechat.exe`
- `portable/` 整个目录

**可选文件：**
- `image/` 目录（包含广告图）
- `run.bat`、`run_gui.bat`
- `PORTABLE_DEPLOYMENT.md`（本文档）

## 系统要求

- **操作系统**: Windows 10/11 64位
- **磁盘空间**: 约800MB（完整便携包）
- **内存**: 建议8GB以上
- **网络**: 需要互联网连接（访问智谱AI API）

## 配置说明

### 必需配置项

编辑 `config.ini`：

```ini
[智谱AI]
api key = 您的智谱AI_API密钥

[微信公众号]
appid = 您的公众号AppID
appsecret = 您的公众号AppSecret
```

### 可选配置项

```ini
[文章主题]
默认主题 = 秋日暖光

[广告图设置]
显示顶部广告图 = true
显示底部广告图 = true

[任务调度]
运行频率小时 = 2
```

## 故障排除

### 问题1：找不到Python

**解决方案**：
- 运行 `download_python.bat` 下载嵌入式Python
- 或安装系统Python：https://www.python.org/downloads/

### 问题2：浏览器启动失败

**解决方案**：
- 确保 `portable/browsers/` 目录存在且包含Chromium
- 运行 `copy_browsers.bat` 重新复制浏览器

### 问题3：依赖包缺失

**解决方案**：
- 运行 `setup_portable.bat` 重新安装依赖
- 或手动安装：`python -m pip install -r requirements.txt`

### 问题4：IP白名单错误

**解决方案**：
1. 运行程序查看当前外网IP
2. 登录微信公众平台
3. 进入「设置与开发」→「基本配置」
4. 将显示的IP添加到白名单

## 文件大小参考

| 组件 | 大小 | 说明 |
|------|------|------|
| Python嵌入式 | 261MB | python-3.11.9-embed + 依赖包 |
| Chromium浏览器 | 656MB | playwright chromium v1208 |
| 项目代码 | ~1MB | Python源文件 |
| md2wechat.exe | 10MB | Markdown转微信工具 |
| **完整便携包总计** | **~1.1GB** | 压缩后约400MB |

### 已安装的Python依赖

```
playwright>=1.58.0
stagehand-py>=0.3.10
requests>=2.32.5
httpx>=0.28.1
zhipuai>=2.1.5
configparser>=7.2.0
secure-smtplib>=0.1.1
beautifulsoup4>=4.14.3
markdown>=3.10.2
wechatpy>=1.8.18
patchright>=1.58.0
```

## 版本信息

- ZBBrain-Write: v3.3.0
- Python: 3.11.9
- Playwright: 1.40.0+
- Chromium: 1208

---

如有问题，请联系原项目提供方。
