# ZBBrain-Write

EPC总承包微信公众号自动化文章生成工具

## 功能特性

- 🔍 **智能爬取**: 从搜狗微信搜索爬取EPC总承包相关资讯
- 🤖 **AI分析**: 使用智谱AI分析并生成热点问题
- 💬 **总包大脑**: 自动向总包大脑获取专业回答
- 📝 **微信草稿**: 自动创建微信公众号草稿
- 📅 **定时调度**: 支持定时自动运行
- 🎨 **多主题**: 支持7种文章主题轮换

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置

复制配置文件模板并填入真实凭证：

```bash
cp ZBBrain-Write/config.ini.example ZBBrain-Write/config.ini
```

编辑 `config.ini`，填入以下凭证：
- 智谱AI API Key
- 微信公众号 AppID 和 AppSecret
- 企业微信 Webhook 地址（可选）
- 邮箱配置（可选）

### 3. 运行

```bash
# 定时运行模式（默认）
python ZBBrain-Write/ZBBrainArticle.py

# 仅运行一次
python ZBBrain-Write/ZBBrainArticle.py --once

# 指定关键词
python ZBBrain-Write/ZBBrainArticle.py -k "EPC总承包" -p 5
```

## 项目结构

```
ZBBrain-Write/
├── ZBBrainArticle.py      # 主程序
├── ZBBrainArticle_GUI.py  # GUI版本
├── config.ini             # 配置文件（需自行创建）
├── config.ini.example     # 配置模板
├── keywords.txt           # 关键词列表
├── cover.jpg              # 封面图片
└── temp/                  # 临时文件目录
```

## 配置说明

详见 `config.ini.example` 文件

## 许可证

MIT License
