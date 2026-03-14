# ZBBrain-Write 环境配置指南

## 项目概述

**ZBBrain-Write** 是一个EPC总承包微信公众号自动化文章生成生产级工具。

- **项目路径**: `e:\CPOPC\ZBBrain-Write\ZBBrain-Write`
- **Python版本**: 3.11.9
- **当前状态**: ✅ 生产级运行环境已就绪

---

## 环境检查结果

### ✅ 系统环境

| 项目 | 状态 | 版本/路径 |
|------|------|-----------|
| Python | ✅ | 3.11.9 (MSC v.1938 64 bit) |
| Python路径 | ✅ | C:\Users\91216\AppData\Local\Programs\Python\Python311\python.exe |
| 操作系统 | ✅ | Windows 10 |

### ✅ Python依赖包

| 包名 | 状态 | 版本 |
|------|------|------|
| playwright | ✅ | 1.58.0 |
| stagehand-py | ✅ | 0.3.10 |
| zhipuai | ✅ | 2.1.5.20250725 |
| requests | ✅ | 2.31.0 |
| beautifulsoup4 | ✅ | 4.14.3 |
| lxml | ✅ | 6.0.0 |
| configparser | ✅ | 6.0.1 |
| colorlog | ✅ | 6.10.1 |
| httpx | ✅ | 0.28.1 |
| openai | ✅ | 2.16.0 |
| python-dotenv | ✅ | 1.2.1 |
| tqdm | ✅ | 4.67.1 |
| pytz | ✅ | 2025.2 |
| python-dateutil | ✅ | 2.9.0.post0 |
| wechatpy | ✅ | 1.8.18 |
| md2wechat | ✅ | 1.0.0 |

### ✅ 外部工具

| 工具 | 状态 | 路径/版本 |
|------|------|-----------|
| Playwright Chromium | ✅ | C:\Users\91216\AppData\Local\ms-playwright\chromium-1208\chrome-win64\chrome.exe |
| md2wechat.exe | ✅ | E:\CPOPC\ZBBrain-Write\ZBBrain-Write\md2wechat.exe |

### ✅ 项目结构

```
ZBBrain-Write/
├── ZBBrainArticle.py          ✅ 核心业务逻辑 (~6500行)
├── ZBBrainArticle_GUI.py      ✅ GUI界面 (~1400行)
├── config.ini                  ✅ 配置文件 (12个配置区块)
├── requirements.txt            ✅ Python依赖列表
├── md2wechat.exe              ✅ Markdown转微信工具
├── browser_data/               ✅ 浏览器数据目录
├── temp/                       ✅ 临时文件目录
├── image/                      ✅ 图片资源目录
│   ├── top-image.jpg           ✅ 顶部广告图
│   └── bottom-image.jpg        ✅ 底部广告图
└── *.log                       日志文件
```

### ✅ 配置文件区块

config.ini 包含以下12个配置区块：

1. **[搜狗微信搜索]** - 搜狗微信搜索配置
   - 搜狗微信搜索网址
   - 默认搜索关键词 = EPC总承包
   - 默认翻页页数 = 5
   - 最大翻页页数 = 10

2. **[总包大脑]** - 总包大脑AI配置
   - 总包大脑网址 = https://metaso.cn/s/rOw6BLS
   - 用户数据目录 = ./browser_data
   - 最大等待回复时间 = 600秒
   - 回复检查间隔 = 5秒

3. **[智谱AI]** - 智谱AI配置
   - API Key = 810287c9375844c1a15fc546721cd69c.xnkuiMfecV06kE8q
   - API地址 = https://open.bigmodel.cn/api/paas/v4/chat/completions
   - 模型名称 = glm-4-plus
   - 问题最小字符数 = 30
   - 回复最小字符数 = 500

4. **[微信公众号]** - 微信公众号配置
   - appid = wx937e6194af9dabd8
   - appsecret = d5ba9b16e9bd109b0cd906244edb74e0
   - 封面图片路径 = ./cover.jpg
   - 默认作者 = 总包大脑

5. **[工程豹公众号]** - 工程豹公众号配置
   - appid = wxab4386f9c3636
   - secret = ff9f895ed854f5df15ff88ec8b69f818

6. **[总包说公众号]** - 总包说公众号配置
   - appid = wx580e54435d78a2b7
   - secret = a3a294fbe9805b4cf65927d1282ab076

7. **[文章主题]** - 文章主题配置
   - 默认主题 = 秋日暖光

8. **[广告图设置]** - 广告图显示控制
   - 显示顶部广告图 = true
   - 显示底部广告图 = true

9. **[企业微信]** - 企业微信通知配置
   - webhook地址 = https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f543f393-4e15-42f9-90eb-d4b8510e3ba6

10. **[邮件通知]** - 邮件通知配置
    - 接收邮箱 = 51817@qq.com
    - smtp服务器 = smtp.qq.com
    - smtp端口 = 587
    - 发件邮箱 = 51817@qq.com
    - 授权码 = eouxzjgxwuhcbggi

11. **[任务调度]** - 任务调度配置
    - 运行频率小时 = 4
    - 停止运行小时 = 22
    - 开始运行小时 = 6

12. **[其他]** - 其他配置
    - 日志文件路径 = ./zbbrain_article.log
    - 临时文件目录 = ./temp
    - 调试模式 = false
    - 最多重试次数 = 5

---

## 核心功能特性

### 1. 智能文章生成

**自主选题模式**（默认）：
- ✅ 自动爬取搜狗微信搜索资讯
- ✅ 使用智谱AI分析生成热点问题（应用JTBD理论）
- ✅ 发送到总包大脑获取专业回答
- ✅ 生成封面图片和10万+标题
- ✅ 发布到微信公众号

**用户命题模式**：
- ✅ 用户直接提供问题
- ✅ 跳过资讯爬取和AI分析步骤
- ✅ 直接获取回答并生成文章

### 2. 生产级特性

**可靠性保障**：
- ✅ 自动重试机制（最多5次）
- ✅ 熔断器保护（Circuit Breaker）
- ✅ 速率限制（Rate Limiter）
- ✅ 错误恢复策略
- ✅ 优雅关闭（Graceful Shutdown）

**监控体系**：
- ✅ 详细日志记录
- ✅ 性能指标收集
- ✅ 请求/响应跟踪
- ✅ 健康检查系统

**可维护性**：
- ✅ 配置热重载
- ✅ 版本控制和回滚
- ✅ 完整的文档

### 3. 自定义配置

**搜索配置**：
- 搜索关键词：可自定义（默认：EPC总承包）
- 翻页数：可自定义（默认：5页，推荐范围：2-10页）

**文章主题**：
- 秋日暖光（默认）
- 简约清新
- 商务专业
- 科技感
- 其他md2wechat支持的主题

**广告图控制**：
- 顶部广告图：可显示/隐藏
- 底部广告图：可显示/隐藏
- 文件位置：`./image/top-image.jpg` 和 `./image/bottom-image.jpg`

**多公众号发布**：
- 工程豹 (wxab4386f9c12d3636)
- 总包之声 (默认发布)
- 总包说 (wx580e54435d78a2b7)

---

## 运行方式

### 方式1：GUI模式（推荐）

```bash
cd e:\CPOPC\ZBBrain-Write\ZBBrain-Write
python ZBBrainArticle_GUI.py
```

**优势**：
- 直观的图形界面
- 实时日志显示
- 可视化配置管理
- 进度条显示

### 方式2：命令行模式

```bash
cd e:\CPOPC\ZBBrain-Write\ZBBrain-Write

# 自主选题模式（默认）
python ZBBrainArticle.py -k "EPC总承包" -p 5

# 用户命题模式
python ZBBrainArticle.py -m user -q "如何优化EPC项目成本控制？"

# 使用自定义配置文件
python ZBBrainArticle.py -c custom_config.ini

# 启用调试模式
python ZBBrainArticle.py -d
```

**命令行参数**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `-c, --config` | 指定配置文件路径 | `-c custom.ini` |
| `-k, --keyword` | 自定义搜索关键词 | `-k "EPC总承包"` |
| `-p, --pages` | 自定义爬取页数 | `-p 5` |
| `-m, --mode` | 运行模式（auto/user） | `-m user` |
| `-q, --question` | 用户问题（用户命题模式） | `-q "问题内容"` |
| `-s, --schedule` | 启用定时调度模式 | `-s` |
| `-d, --debug` | 启用调试模式 | `-d` |

### 方式3：定时调度模式

```bash
cd e:\CPOPC\ZBBrain-Write\ZBBrain-Write

# 启动定时调度（每4小时执行一次，6:00-22:00运行）
python ZBBrainArticle.py -s
```

---

## 工作流程

```
1. 配置加载与验证
   ↓
2. IP白名单检查
   ↓
3. 爬取资讯（自主选题模式）
   ├─ 从搜狗微信搜索获取EPC相关文章
   └─ 使用AI分析文章内容
   ↓
4. AI生成问题
   ├─ 使用智谱AI分析资讯
   ├─ 应用JTBD理论生成热点问题
   └─ 确保问题符合要求（≥30字符）
   ↓
5. 获取回答
   ├─ 发送问题到总包大脑
   ├─ 等待回答生成（最长10分钟）
   └─ 验证回答长度（需≥500字符）
   ↓
6. 生成封面
   └─ 使用智谱AI生成美式动画风格封面图
   ↓
7. 生成标题
   └─ 基于热点问题生成10万+自媒体标题
   ↓
8. 格式转换
   └─ 使用md2wechat转换为微信公众号格式
   ↓
9. 创建草稿
   └─ 自动创建草稿到微信公众平台
   ↓
10. 发送通知
    ├─ 发送企业微信通知
    └─ 发送邮件通知
```

---

## 技术架构

### 核心技术栈

- **Python 3.11.9** - 主要编程语言
- **Playwright 1.58.0** - 浏览器自动化
- **Stagehand-py 0.3.10** - AI驱动的浏览器自动化
- **智谱AI (GLM-4)** - AI内容生成
- **md2wechat 1.0.0** - Markdown到微信格式转换
- **tkinter/customtkinter** - GUI界面

### 架构特性

- **异步架构** - 使用 asyncio 实现高并发
- **重试机制** - 指数退避重试策略
- **熔断器** - 防止级联故障
- **速率限制** - 防止超过API限制
- **健康检查** - 系统状态监控
- **配置热重载** - 无需重启更新配置
- **优雅关闭** - 正确处理信号和清理资源

---

## 常见问题

### Q1: IP白名单错误

如果出现 `invalid ip` 错误：

1. 查看日志中显示的当前外网IP地址
2. 登录微信公众平台：https://mp.weixin.qq.com
3. 进入「设置与开发」→「基本配置」
4. 将当前IP添加到IP白名单
5. 重新运行项目

### Q2: 依赖安装失败

```bash
# 如果pip安装失败，尝试升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: Playwright浏览器安装失败

```bash
# 手动安装浏览器
python -m playwright install --with-deps chromium

# 如果下载慢，使用镜像
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
python -m playwright install chromium
```

### Q4: 广告图不显示

1. 检查 `./image/` 目录
2. 确保存在 `top-image.jpg` 和 `bottom-image.jpg`
3. 检查 config.ini 中的广告图设置
4. 确保md2wechat能找到图片文件

### Q5: 标题生成失败

- 系统会自动使用备用标题模板
- 备用模板位于代码中的 title_templates 列表
- 可根据需要调整备用标题

### Q6: 如何查看日志？

```bash
# 实时查看日志（Windows PowerShell）
Get-Content zbbrain_article.log -Wait

# 查看最近50行
Get-Content zbbrain_article.log -Tail 50
```

---

## 性能指标

### 预期性能

- 爬取速度: ~10篇文章/分钟
- AI响应时间: 5-30秒
- 总包大脑响应: 30秒-10分钟
- 总体完成时间: 5-15分钟

### 资源使用

- 内存: ~500MB (浏览器 + AI)
- CPU: 中等（浏览器渲染时）
- 磁盘: ~100MB (日志 + 临时文件)

---

## 版本信息

- **当前版本**: v2.5.0 (Optimized Edition - Iteration 5)
- **最后更新**: 2026-02-25
- **Python要求**: 3.9+
- **支持平台**: Windows/Mac/Linux

---

## 开源资源

本项目使用了以下开源资源：

- [Playwright](https://playwright.dev/) - 浏览器自动化框架
- [Stagehand](https://github.com/browserbase/stagehand) - AI浏览器自动化框架
- [md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill) - Markdown转微信格式工具
- [ZhipuAI](https://open.bigmodel.cn/) - 智谱AI SDK

---

## 安全注意事项

⚠️ **重要提示**：

1. **不要将配置文件提交到版本控制系统** - config.ini 包含敏感信息（API密钥、密码等）
2. **定期更换API密钥** - 建议每3-6个月更换一次
3. **使用环境变量** - 生产环境建议使用环境变量存储敏感信息
4. **IP白名单** - 确保微信公众平台IP白名单配置正确
5. **日志安全** - 定期清理日志文件，避免泄露敏感信息

---

## 许可证

MIT License

---

## 联系方式

如有问题或建议，请提交Issue或Pull Request。

---

**环境状态**: ✅ **READY** (生产级运行环境已就绪)

**最后检查时间**: 2026-02-25
