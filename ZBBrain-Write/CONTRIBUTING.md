# Contributing to ZBBrain-Write

[中文](#中文贡献指南) | [English](#english-contributing-guide)

---

## 中文贡献指南

感谢您有兴趣为 ZBBrain-Write 做出贡献！本文档将帮助您了解如何参与项目开发。

### 🚀 快速开始

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目到您的账号
   ```

2. **克隆仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ZBBrain-Write.git
   cd ZBBrain-Write
   ```

3. **创建配置文件**
   ```bash
   cp config.ini.example config.ini
   # 编辑 config.ini 填入您的配置
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### 📝 代码规范

- **代码风格**: 遵循 PEP 8 规范
- **命名约定**:
  - 类名使用 PascalCase (如 `WeChatManager`)
  - 函数/方法名使用 snake_case (如 `create_draft`)
  - 常量使用 UPPER_SNAKE_CASE (如 `MAX_RETRY_COUNT`)
- **文档字符串**: 所有公共方法必须有中文文档字符串
- **类型提示**: 建议使用 Python 类型提示

### 🔒 安全准则

**⚠️ 重要: 绝对不要提交以下内容:**
- 真实的 API 密钥或 Token
- 微信公众号的 AppID/AppSecret
- 数据库密码
- 任何 `config.ini` 文件（非 `.example`）
- `wechat_accounts.json` 文件

```bash
# 提交前检查
git diff --staged | grep -E "(api[_-]?key|secret|password|token)" && echo "⚠️ 可能包含敏感信息!"
```

### 🐛 提交 Bug

1. 在 [Issues](https://github.com/your-repo/ZBBrain-Write/issues) 页面搜索是否已有相关问题
2. 如果没有，创建新 Issue，包含:
   - 清晰的标题描述问题
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息（Python版本、操作系统）
   - 相关日志（移除敏感信息）

### ✨ 提交新功能

1. 先创建 Issue 讨论功能设计
2. 等待维护者确认方向
3. 创建 Pull Request

### 📦 Pull Request 流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **编写代码**
   - 保持提交原子化，每个 commit 只做一件事
   - 编写清晰的 commit message

3. **测试**
   ```bash
   # 运行测试（如果有）
   python -m pytest tests/

   # 手动测试您修改的功能
   python ZBBrainArticle.py --once
   ```

4. **提交 PR**
   - 标题清晰描述变更内容
   - 在描述中关联相关 Issue
   - 等待代码审查

### 📚 项目结构

```
ZBBrain-Write/
├── ZBBrainArticle.py      # 主程序（核心业务逻辑）
├── ZBBrainArticle_GUI.py  # Tkinter GUI
├── zbbrain_gui.py         # PyQt5 GUI
├── config.ini.example     # 配置模板
├── requirements.txt       # Python依赖
├── keywords.txt           # 关键词列表
├── Prompt/                # 提示词模板
├── image/                 # 图片资源
└── temp/                  # 临时文件
```

---

## English Contributing Guide

Thank you for your interest in contributing to ZBBrain-Write! This document will help you understand how to participate in the project.

### 🚀 Quick Start

1. **Fork the Project**
   ```bash
   # Fork the project to your account on GitHub
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ZBBrain-Write.git
   cd ZBBrain-Write
   ```

3. **Create Config File**
   ```bash
   cp config.ini.example config.ini
   # Edit config.ini with your settings
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

### 📝 Code Standards

- **Code Style**: Follow PEP 8 guidelines
- **Naming Conventions**:
  - Class names: PascalCase (e.g., `WeChatManager`)
  - Functions/methods: snake_case (e.g., `create_draft`)
  - Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- **Docstrings**: All public methods must have docstrings
- **Type Hints**: Python type hints recommended

### 🔒 Security Guidelines

**⚠️ IMPORTANT: Never commit the following:**
- Real API keys or Tokens
- WeChat Official Account AppID/AppSecret
- Database passwords
- Any `config.ini` file (non-`.example`)
- `wechat_accounts.json` file

### 🐛 Reporting Bugs

1. Search [Issues](https://github.com/your-repo/ZBBrain-Write/issues) for existing reports
2. If not found, create a new Issue with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment info (Python version, OS)
   - Relevant logs (remove sensitive info)

### ✨ Feature Requests

1. Create an Issue to discuss the design first
2. Wait for maintainer confirmation
3. Create a Pull Request

### 📦 Pull Request Process

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Write Code**
   - Keep commits atomic
   - Write clear commit messages

3. **Test**
   ```bash
   # Run tests (if available)
   python -m pytest tests/

   # Manual test your changes
   python ZBBrainArticle.py --once
   ```

4. **Submit PR**
   - Clear title describing changes
   - Reference related Issues
   - Wait for code review

### 📜 License

By contributing to ZBBrain-Write, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Thank You!

Every contribution matters, whether it's:
- Reporting a bug
- Suggesting a feature
- Improving documentation
- Submitting a pull request

We appreciate your time and effort!
