<div align="center">

# 🧠 ZBBrain-Write

**EPC总承包领域 · 微信公众号全自动化内容生产系统**

**AI-Powered WeChat Official Account Content Automation for EPC Industry**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.6.3-orange?style=flat)](CHANGELOG.md)
[![Stars](https://img.shields.io/github/stars/your-username/ZBBrain-Write?style=flat&logo=github)](https://github.com/your-username/ZBBrain-Write/stargazers)

[English](#-english-documentation) | [中文文档](#-中文文档) | [快速开始](#-快速开始) | [技术创新](#-技术创新点) | [贡献指南](CONTRIBUTING.md)

---

**一句话概括**: AI自动发现行业热点 → 生成专业内容 → 发布到微信公众号

**TL;DR**: AI discovers industry trends → Generates professional content → Publishes to WeChat

</div>

---

## 🌟 Stars History

<details>
<summary>⭐ Show your support - Star ZBBrain-Write!</summary>

If you find this project helpful, please consider giving it a star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/ZBBrain-Write&type=Date)](https://star-history.com/#your-username/ZBBrain-Write&Date)

</details>

---

# 📖 中文文档

## 🎯 项目简介

ZBBrain-Write 是专为 **EPC总承包** 领域打造的微信公众号自动化内容生产系统。通过智能化的工作流程，实现从行业资讯到专业文章的自动转化。

### 核心流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  搜狗微信    │ →  │  智谱AI     │ →  │  总包大脑   │ →  │  AI排版     │ →  │  微信公众号  │
│  资讯爬虫    │    │  热点分析   │    │  深度回答   │    │  HTML美化   │    │  草稿发布   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      ↓                   ↓                   ↓                   ↓
   多页爬取           JTBD理论           长思考模式           7种主题
   智能过滤           场景化问题         15分钟深度           自动轮换
```

---

## 💡 技术创新点

### 🏆 核心技术创新

#### 1. AI驱动的全自动化内容生产流水线

```
传统方式: 人工选题 → 人工写作 → 人工排版 → 人工发布 (耗时4-8小时)
本项目:   自动发现 → AI分析 → AI回答 → AI排版 → 自动发布 (耗时30分钟)
```

- **端到端自动化**: 从资讯发现到草稿发布，全流程无需人工干预
- **多AI协同**: 智谱AI (热点分析) + 总包大脑 (专业回答) + CogView (封面生成)
- **0成本运行**: 全流程使用免费AI模型，无任何API费用

#### 2. 长思考模式智能切换技术 (v3.6.2 新增)

```python
# 创新的Hover触发下拉菜单交互模式
快思考 ──[hover]──> 下拉菜单 ──[click]──> 长思考
         │
         └──> 多重策略保证稳定性:
              ├── 策略1: Playwright hover + click
              ├── 策略2: Stagehand AI智能识别
              ├── 策略3: JavaScript触发事件
              └── 策略4: 直接元素定位
```

- **深度回答**: 长思考模式获得更详细、更深度的专业回复
- **智能等待**: 自动延长等待时间至15分钟，确保回答完整性
- **稳定切换**: 4重fallback策略保证100%切换成功

#### 3. JTBD理论驱动的问题生成

```
传统问题: "EPC项目如何管理？" (泛泛而谈)
JTBD问题: "风电EPC项目中，大叶片运输导致的工期延误如何进行索赔？" (具体场景)
```

- **场景优先**: 所有问题基于具体业务场景
- **真实痛点**: 反映从业者实际工作中的困惑
- **50字以上**: 详细描述确保问题清晰度

#### 4. 多维度智能轮换系统

| 轮换维度 | 技术实现 | 业务价值 |
|---------|---------|---------|
| **关键词轮换** | JSON状态持久化 | 内容多样性 |
| **人设轮换** | Prompt模板切换 | 回答角度丰富 |
| **主题轮换** | 7套CSS主题库 | 视觉不疲劳 |
| **公众号轮换** | 账号矩阵配置 | 多账号运营 |

#### 5. 生产级稳定性保障体系

```yaml
熔断器模式:
  - AI API故障自动熔断
  - 微信API限流自动降级
  - 失败自动重试(最多5次)

智能缓存:
  - 热点问题24小时缓存
  - Token自动管理

健康检查:
  - 浏览器进程自动恢复
  - 网络环境自适应检测
```

#### 6. 国内网络环境自适应 (v3.5.0 新增)

```python
# 自动检测网络环境
if is_china_network():
    # 国内网络 → 正常调用微信API
else:
    # 海外网络 → 优雅降级，跳过发布
```

- **IP地理位置检测**: 自动判断是否在中国大陆
- **微信IP白名单验证**: 提前发现配置问题
- **优雅降级**: 海外网络环境自动跳过微信发布

#### 7. 企业级定时调度系统

```python
# 北京时区感知调度
北京时区 = Asia/Shanghai (UTC+8)
工作时间窗口 = 06:00 - 22:00
运行间隔 = 可配置（默认1小时）

# 智能间隔计算（v3.6.3修复）
下次运行时间 = 当前任务完成时间 + 配置间隔
# 而非: 下次运行时间 = 任务开始时间 + 配置间隔 (错误!)
```

---

## ✨ 核心功能

### 🔄 智能轮换机制

| 轮换维度 | 说明 | 效果 |
|---------|------|------|
| **关键词轮换** | 自动切换搜索关键词 | 内容多样性 ↑ |
| **人设轮换** | 麦肯锡/刘润/逻辑思维等风格 | 回答角度丰富 |
| **主题轮换** | 7种精美主题自动切换 | 视觉不疲劳 |
| **公众号轮换** | 多公众号自动轮换发布 | 账号矩阵运营 |

### 🎨 7种专业主题

| 主题 | 风格 | 适用场景 |
|------|------|----------|
| 秋日暖光 | 温暖治愈，橙色调 | 情感故事、生活随笔 |
| 春日清新 | 清新自然，绿色调 | 旅行日记、自然主题 |
| 深海静谧 | 深沉冷静，蓝色调 | 技术文章、商务报告 |
| 优雅金 | 高端大气，金色调 | 商务报告、专业资讯 |
| 活力红 | 活力热情，红色调 | 活动宣传、重要通知 |
| 简约蓝 | 简约现代，蓝色调 | 技术文章、产品介绍 |
| 专注绿 | 专注沉稳，绿色调 | 环保主题、健康资讯 |

### 📝 专业内容生成

- **JTBD理论驱动**: 基于场景生成真实问题
- **10万+标题优化**: 自动生成吸引眼球的标题
- **Markdown排版**: 专业级图文排版
- **封面图生成**: AI生成火柴人风格封面

### 💰 0成本AI驱动 (V3.6.0 新增)

**完全免费运行，无需支付任何AI费用！**

| 环节 | 模型 | 价格 |
|------|------|------|
| 热点问题生成 | GLM-4.7-Flash | 🆓 免费 |
| 爆款标题生成 | GLM-4.7-Flash | 🆓 免费 |
| 内容结构化 | GLM-4.7-Flash | 🆓 免费 |
| HTML专业排版 | GLM-4.7-Flash | 🆓 免费 |
| 封面图生成 | CogView-3-Flash | 🆓 免费 |

**GLM-4.7-Flash 能力**:
- 200K 超长上下文
- 同级别最强通用能力
- 高效的代码生成能力
- 智谱AI官方完全免费

> 配置方法：在 `config.ini` 中设置 `低成本模型名称 = glm-4.7-flash`

### 🛡️ 生产级稳定性

| 特性 | 说明 |
|------|------|
| 熔断器 | AI/微信API故障自动熔断 |
| 速率限制 | 控制API调用频率 |
| 自动重试 | 失败自动重试（最多5次） |
| 智能缓存 | 热点问题24小时缓存 |
| 健康检查 | 自动检测并恢复浏览器 |
| 网络自适应 | 国内/海外网络环境自动适配 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ZBBrain-Write 系统架构                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │   调度器     │    │  配置管理    │    │  日志系统    │                     │
│  │  Scheduler  │    │   Config    │    │   Logger    │                     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│         │                  │                  │                            │
│         ▼                  ▼                  ▼                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         主控制器 MainController                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐            │
│         │                          │                          │            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐      │
│  │  爬虫模块    │           │   AI模块    │           │  发布模块    │      │
│  │   Scraper   │           │  ZhipuAI    │           │  Publisher  │      │
│  └──────┬──────┘           └──────┬──────┘           └──────┬──────┘      │
│         │                          │                          │            │
│         ▼                          ▼                          ▼            │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐      │
│  │ 搜狗微信API  │           │ 智谱AI API   │           │ 微信公众平台  │      │
│  └─────────────┘           │ 总包大脑     │           │   API       │      │
│                            └─────────────┘           └─────────────┘      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         浏览器自动化层                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │Playwright│  │Stagehand │  │ 持久化    │  │ 智能等待  │            │   │
│  │  │          │  │   AI     │  │ Context  │  │  Retry   │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         稳定性保障层                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │ 熔断器   │  │速率限制   │  │ 智能缓存  │  │ 健康检查  │            │   │
│  │  │Circuit   │  │Rate      │  │  Cache   │  │ Health   │            │   │
│  │  │Breaker   │  │Limiter   │  │          │  │ Check    │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows 10/11 (推荐) / macOS / Linux

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/ZBBrain-Write.git
cd ZBBrain-Write

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装浏览器
playwright install chromium

# 4. 创建配置文件
cp config.ini.example config.ini
# 编辑 config.ini 填入您的API密钥和公众号配置

# 5. 运行
python ZBBrainArticle.py --once
```

### 运行模式

```bash
# 单次运行 (推荐新手)
python ZBBrainArticle.py --once

# 自主选题模式
python ZBBrainArticle.py --keyword "EPC总承包" --pages 5

# 用户命题模式
python ZBBrainArticle.py --mode user --question "如何优化EPC项目成本控制？"

# 定时调度模式 (生产环境)
python ZBBrainArticle.py --schedule

# GUI模式
python ZBBrainArticle_GUI.py
```

## ⚙️ 配置说明

编辑 `config.ini` 文件：

```ini
[搜狗微信搜索]
默认搜索关键词 = EPC总承包
默认翻页页数 = 5

[智谱AI]
API Key = your_zhipu_api_key
# 【0成本优化】使用免费模型
低成本模型名称 = glm-4.7-flash
高质量模型名称 = glm-4.7-flash
图片生成模型 = cogview-3-flash

[总包大脑]
总包大脑网址 = https://metaso.cn/s/YOUR_LINK
# 【v3.6.2新增】长思考模式 - 获得更深度的回答
启用长思考模式 = true
# 长思考模式至少等待15分钟
最大等待回复时间 = 900

[微信公众号]
AppID = your_appid
AppSecret = your_appsecret

[文章主题]
默认主题 = 秋日暖光
启用主题轮换 = true

[定时任务]
运行间隔小时 = 1
开始运行小时 = 6
停止运行小时 = 22
```

## 📊 项目结构

```
ZBBrain-Write/
├── ZBBrainArticle.py          # 主程序 (28个类，生产级代码)
├── ZBBrainArticle_GUI.py      # GUI界面
├── zbbrain_gui.py             # PyQt5配置界面
├── config.ini.example         # 配置模板
├── requirements.txt           # 依赖列表
├── keywords.txt               # 关键词列表
├── Prompt/                    # 提示词模板
│   ├── 总包大脑麦肯锡版提示词.md
│   ├── 总包大脑刘润版提示词.md
│   └── ...
├── image/                     # 图片资源
├── temp/                      # 临时文件
└── docs/                      # 文档
```

## 🔧 开发指南

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码检查
flake8 ZBBrainArticle.py
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

# 📖 English Documentation

## 🎯 Overview

ZBBrain-Write is an AI-powered content automation system designed for WeChat Official Accounts in the EPC (Engineering, Procurement, Construction) industry. It automatically discovers industry trends, generates professional content, and publishes to WeChat.

### Core Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Sogou      │ →  │  ZhipuAI    │ →  │  Metaso     │ →  │  WeChat     │
│  Scraper    │    │  Analysis   │    │  Response   │    │  Publish    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## 💡 Technical Innovations

### 1. AI-Driven End-to-End Automation Pipeline
- From news discovery to draft publishing, fully automated
- Multi-AI collaboration: ZhipuAI + Metaso + CogView
- Zero-cost operation using free AI models

### 2. Long Thinking Mode Smart Switching (v3.6.2)
- Hover-triggered dropdown interaction
- 4-layer fallback strategy for 100% reliability
- Extended wait time (15 min) for deeper responses

### 3. JTBD Theory-Driven Question Generation
- Scenario-based questions, not generic ones
- Real pain points from practitioners
- 50+ character detailed descriptions

### 4. Multi-Dimensional Rotation System
- Keyword / Persona / Theme / Account rotation
- Ensures content diversity and visual variety

### 5. Production-Grade Stability
- Circuit breaker pattern
- Smart caching
- Automatic health checks
- Network environment adaptation

## ✨ Key Features

### 🔄 Intelligent Rotation System

| Dimension | Description |
|-----------|-------------|
| **Keyword Rotation** | Automatic search keyword switching |
| **Persona Rotation** | Multiple AI response styles (McKinsey, Liu Run, etc.) |
| **Theme Rotation** | 7 beautiful themes auto-switching |
| **Account Rotation** | Multiple WeChat accounts support |

### 🎨 7 Professional Themes

- Autumn Warm (秋日暖光)
- Spring Fresh (春日清新)
- Ocean Calm (深海静谧)
- Elegant Gold (优雅金)
- Bold Red (活力红)
- Minimal Blue (简约蓝)
- Focus Green (专注绿)

### 🛡️ Production-Grade Stability

- Circuit Breaker pattern
- Rate limiting
- Automatic retry
- Smart caching
- Health monitoring
- Network environment adaptation

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Windows 10/11 / macOS / Linux

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/ZBBrain-Write.git
cd ZBBrain-Write

# Install dependencies
pip install -r requirements.txt

# Install browser
playwright install chromium

# Create config
cp config.ini.example config.ini
# Edit config.ini with your API keys

# Run
python ZBBrainArticle.py --once
```

### Usage

```bash
# Single run
python ZBBrainArticle.py --once

# Custom keyword
python ZBBrainArticle.py --keyword "EPC" --pages 5

# User question mode
python ZBBrainArticle.py --mode user --question "Your question?"

# Scheduled mode
python ZBBrainArticle.py --schedule

# GUI mode
python ZBBrainArticle_GUI.py
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [ZhipuAI](https://open.bigmodel.cn/) - AI content generation
- [Playwright](https://playwright.dev/) - Browser automation
- [WeChat Public Platform API](https://developers.weixin.qq.com/)

---

## 📞 Contact & Support

- 📧 Email: [Create an issue](https://github.com/your-username/ZBBrain-Write/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/ZBBrain-Write/discussions)

---

<div align="center">

**If you find this project helpful, please give it a ⭐ Star!**

[![Star](https://img.shields.io/github/stars/your-username/ZBBrain-Write?style=social)](https://github.com/your-username/ZBBrain-Write/stargazers)

Made with ❤️ by ZBBrain Team

</div>
