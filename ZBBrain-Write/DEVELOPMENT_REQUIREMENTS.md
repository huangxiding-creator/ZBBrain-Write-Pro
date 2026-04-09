# ZBBrain-Write 完整开发需求文档

> **文档目的**: 本文档包含项目从初始开发到当前状态的全部需求细节，确保AI一次性即可完成到当前成果的开发工作。

---

## 一、项目概述

### 1.1 项目名称
**ZBBrain-Write** - EPC总承包微信公众号自动化文章生成工具

### 1.2 项目定位
这是一个生产级的自动化工具，用于：
- 从搜狗微信搜索爬取EPC总承包相关资讯
- 使用智谱AI分析生成热点问题
- 通过总包大脑（秘塔AI）获取专业回答
- 自动创建微信公众号草稿文章
- 支持定时调度自动运行

### 1.3 技术栈
- **语言**: Python 3.9+
- **浏览器自动化**: Playwright（异步API）
- **AI服务**: 智谱AI (GLM-4-Plus)
- **微信公众号API**: wechatpy
- **Markdown转换**: md2wechat工具 + 智谱AI专业排版
- **时区处理**: pytz (Asia/Shanghai)

---

## 二、核心功能模块

### 2.1 资讯爬取模块（搜狗微信搜索）

#### 功能要求
1. **搜索配置**
   - 默认搜索关键词: `EPC总承包`
   - 支持自定义关键词覆盖
   - 默认翻页页数: 5页
   - 最大翻页限制: 10页

2. **数据提取**
   - 从搜狗微信搜索资讯页面爬取文章
   - 提取文章标题、摘要、来源、发布时间
   - 支持多页翻页爬取

3. **配置项**
   ```ini
   [搜狗微信搜索]
   搜狗微信搜索网址 = https://www.sogou.com/sogou?...
   默认搜索关键词 = EPC总承包
   默认翻页页数 = 5
   最大翻页页数 = 10
   ```

### 2.2 热点问题生成模块（智谱AI）

#### 功能要求
1. **问题生成策略**
   - 使用智谱AI GLM-4-Plus模型
   - 基于JTBD（Jobs-To-Be-Done）理论分析
   - 从爬取的资讯中提取热点问题
   - 问题最小字符数: 30

2. **问题生成Prompt模板**
   ```
   你是EPC总承包领域的资深专家，擅长基于JTBD理论发现用户真正的需求和痛点。

   以下是最近搜索到的EPC总承包相关资讯：
   {资讯内容}

   请分析这些资讯，从中提炼出一个最有价值的热点问题。

   要求：
   1. 问题必须与EPC总承包密切相关
   2. 问题应该具有普遍性和实用性
   3. 问题表述清晰，便于总包大脑回答
   4. 只输出问题本身，不要其他解释
   ```

3. **配置项**
   ```ini
   [智谱AI]
   api key = your-api-key
   api 地址 = https://open.bigmodel.cn/api/paas/v4/chat/completions
   模型名称 = glm-4-plus
   问题最小字符数 = 30
   回复最小字符数 = 500
   ```

### 2.3 总包大脑交互模块

#### 功能要求
1. **浏览器自动化**
   - 使用Playwright异步API
   - 保持浏览器用户数据目录（登录状态持久化）
   - 自动检测登录状态，如需登录则等待用户扫码

2. **问答交互流程**
   - 访问总包大脑网址
   - 检测输入框并填充问题
   - 等待AI回复（监控回复稳定性）
   - 回复稳定检测: 连续6次检查内容不变则认为完成
   - 最大等待时间: 600秒
   - 检查间隔: 5秒

3. **回答内容保护（重要！）**
   - **绝对禁止修改总包大脑回答内容**
   - 不允许精炼、压缩、概括、扩展
   - 只允许添加Markdown标题结构(##, ###)
   - 保持原文100%完整

4. **配置项**
   ```ini
   [总包大脑]
   总包大脑网址 = https://metaso.cn/s/rOw6BLS
   用户数据目录 = ./browser_data
   最大等待回复时间 = 600
   回复检查间隔 = 5
   ```

### 2.4 文章格式转换模块

#### 功能要求
1. **主题风格（整合md2wechat-skill设计）**

   **秋日暖光主题（默认）**:
   ```python
   theme_config = {
       'colors': {
           'primary': '#d97758',      # 秋日暖橙
           'secondary': '#c06b4d',    # 橙红
           'background': '#faf9f5',   # 暖白
           'card_bg': '#fef4e7',      # 淡橙
           'text': '#4a413d',         # 深褐灰
           'border': '#d97758',
       },
       'style': '温暖治愈、橙色调、文艺美学',
       'features': ['卡片式布局', '米白方格纹理', '圆角18px', '柔和阴影', '▶ 符号装饰'],
       'border_radius': '18px',
   }
   ```

   **其他可用主题**:
   - 春日清新 (spring-fresh): 绿色调，清新自然
   - 深海静谧 (ocean-calm): 蓝色调，专业稳重
   - 优雅金 (elegant-gold): 金色调，高端大气
   - 活力红 (bold-red): 红色调，活力热情
   - 简约蓝 (minimal-blue): 蓝色调，简约现代
   - 专注绿 (focus-green): 绿色调，专注沉稳

2. **主题轮换（重要！）**
   - **每次运行自动更换主题**，避免观众视觉疲劳
   - 7种主题循环轮换：秋日暖光 → 春日清新 → 深海静谧 → 优雅金 → 活力红 → 简约蓝 → 专注绿
   - 状态保存在 `theme_rotation.json` 文件中
   - 配置项：
     ```ini
     [文章主题]
     启用主题轮换 = true
     主题轮换状态文件 = ./theme_rotation.json
     ```

3. **HTML转换规则**
   - 所有CSS必须是内联样式
   - 不使用外部样式表或`<style>`标签
   - 只使用微信安全标签: section, p, span, strong, em, br, h1-h6, ul, ol, li, blockquote, pre, code, img
   - 图片使用占位符格式: `<!-- IMG:数字 -->`

3. **排版Prompt模板**
   ```
   你是专业的微信公众号排版设计师，精通'{theme_name}'主题设计。

   排版原则：
   - 专业：遵循排版规范，细节考究
   - 精致：每个元素都经过精心设计
   - 易读：舒适的字号、行高和间距
   - 美观：配色协调，视觉平衡

   【重要规则】
   1. 所有CSS必须是内联样式（style属性）
   2. 不使用外部样式表或<style>标签
   3. 只使用安全的HTML标签
   4. 图片使用占位符格式：<!-- IMG:数字 -->
   5. 只输出HTML，不要额外说明
   ```

### 2.5 广告图模块

#### 功能要求
1. **顶部广告图**
   - 位于文章标题**之前**
   - 文件路径: `./image/top-image.jpg`
   - 支持本地文件、HTTP(S) URL、base64格式

2. **底部广告图**
   - 位于文章正文**之后**
   - 文件路径: `./image/bottom-image.jpg`
   - 支持本地文件、HTTP(S) URL、base64格式

3. **Markdown输出格式**
   ```markdown
   {顶部广告图}

   # {文章标题}

   {正文内容}

   {底部广告图}

   ---

   *本文由总包大脑AI生成，仅供参考*
   ```

4. **配置项**
   ```ini
   [广告图设置]
   显示顶部广告图 = true
   顶部广告图路径 = ./image/top-image.jpg
   显示底部广告图 = true
   底部广告图路径 = ./image/bottom-image.jpg
   ```

### 2.6 微信公众号草稿模块

#### 功能要求
1. **草稿创建**
   - 使用微信公众号API创建草稿
   - 上传封面图片到素材库（900x500px JPG）
   - 设置文章作者、标题、内容

2. **原创声明**
   - 支持标记为原创内容
   - 支持开启评论功能

3. **多公众号支持**
   - 总包之声公众号（默认）
   - 工程豹公众号
   - 总包说公众号

4. **配置项**
   ```ini
   [微信公众号]
   appid = YOUR_WECHAT_APPID_HERE
   appsecret = YOUR_WECHAT_APPSECRET_HERE
   封面图片路径 = ./cover.jpg
   默认作者 = 总包大脑
   声明原创 = 1
   开启评论 = 1

   [工程豹公众号]
   appid = YOUR_GONGCHENGBAO_APPID_HERE
   secret = YOUR_GONGCHENGBAO_SECRET_HERE

   [总包说公众号]
   appid = YOUR_ZONGBAOSHUO_APPID_HERE
   secret = YOUR_ZONGBAOSHUO_SECRET_HERE
   ```

### 2.7 通知模块

#### 功能要求
1. **企业微信通知**
   - 使用Webhook发送消息
   - 支持Markdown格式
   - 发送成功/失败通知

2. **邮件通知（可选）**
   - SMTP协议发送邮件
   - QQ邮箱支持（需要授权码）

3. **配置项**
   ```ini
   [企业微信通知]
   Webhook地址 = https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx

   [邮件通知]
   接收邮箱 = your-email@qq.com
   SMTP服务器 = smtp.qq.com
   SMTP端口 = 587
   发件邮箱 = your-email@qq.com
   授权码 = your-authorization-code
   ```

---

## 三、定时调度模块

### 3.1 功能要求
1. **调度策略**
   - 启动时立即运行1次
   - 每隔指定小时数运行1次（默认2小时）
   - 使用北京时间（Asia/Shanghai）

2. **工作时间控制**
   - 超过停止时间（默认22:00）停止运行
   - 达到开始时间（默认6:00）才开始运行
   - 非工作时间进入等待状态

3. **命令行参数**
   | 参数 | 说明 | 默认值 |
   |------|------|--------|
   | `-s, --schedule` | 强制启用定时调度模式 | - |
   | `--once` | 仅运行一次（禁用定时） | - |
   | `-c, --config` | 配置文件路径 | config.ini |
   | `-k, --keyword` | 自定义搜索关键词 | - |
   | `-p, --pages` | 爬取页数 | - |
   | `-m, --mode` | 运行模式(auto/user) | auto |
   | `-q, --question` | 用户命题（user模式） | - |
   | `-d, --debug` | 调试模式 | false |
   | `-e, --send-email` | 发送邮件通知 | false |

4. **运行模式优先级**
   ```
   --once > --schedule > 配置文件设置
   ```

5. **配置项**
   ```ini
   [任务调度]
   启用定时任务 = true
   运行频率小时 = 2
   停止运行小时 = 22
   开始运行小时 = 6
   ```

### 3.2 代码实现示例
```python
def main():
    # 确定是否启用定时模式
    # 优先级: --once > --schedule > 配置文件
    if args.once:
        use_schedule = False
    elif args.schedule:
        use_schedule = True
    else:
        use_schedule = config.getboolean('任务调度', '启用定时任务', fallback=True)

    if use_schedule:
        run_scheduler(config, logger, ...)
    else:
        task = ZBBrainArticleTask(config_path)
        success = task.run(...)
```

---

## 四、代码架构要求

### 4.1 类结构
```
Constants              # 常量定义类
├── 浏览器相关常量
├── 网络请求相关常量
├── 内容相关常量
└── 时间相关常量

Config                 # 配置管理类
├── 配置文件读取
├── 参数验证
└── 默认值处理

Logger                 # 日志管理类
├── 控制台输出
├── 文件记录
└── 调试模式支持

ZBBrainArticleTask     # 主任务类
├── run()                     # 主运行方法
├── scrape_sogou()            # 搜狗爬取
├── generate_hot_question()   # 生成热点问题
├── send_to_zbbrain()         # 发送到总包大脑
├── _structure_content_with_headings()  # 仅添加标题
├── _convert_answer_to_structured_markdown()  # 转换Markdown
├── _get_theme_prompt()       # 获取主题Prompt
├── convert_md_to_wechat_html()  # 转换微信HTML
├── create_wechat_draft()     # 创建微信草稿
└── send_notification()       # 发送通知

run_scheduler()        # 定时调度器函数
```

### 4.2 异常处理
```python
class ZBBrainException(Exception): pass
class ConfigurationError(ZBBrainException): pass
class BrowserError(ZBBrainException): pass
class ScrapingError(ZBBrainException): pass
class AIError(ZBBrainException): pass
class WeChatAPIError(ZBBrainException): pass
```

### 4.3 资源管理
- 使用上下文管理器确保资源正确释放
- 浏览器实例正确关闭
- 临时文件自动清理

---

## 五、关键实现细节

### 5.1 内容保护实现（_structure_content_with_headings方法）
```python
def _structure_content_with_headings(self, content: str) -> str:
    """仅添加层次化标题结构，绝对不修改原文内容"""
    prompt = f"""你是一位专业的公众号文章排版编辑。你的唯一任务是为已有内容添加Markdown标题结构。

**绝对禁止事项：**
1. 禁止删减任何原文内容
2. 禁止精炼、压缩、概括原文
3. 禁止扩展、补充、增加内容
4. 禁止修改任何句子、词汇、标点
5. 禁止调整段落顺序
6. 禁止改变原文的语气和风格

**你只能做以下操作：**
1. 在适当位置插入二级标题(##)和三级标题(###)
2. 标题必须放在对应段落之前
3. 标题应简洁概括下方内容的主题

**需要添加标题的内容：**
{content}
"""
    # 调用智谱AI...
```

### 5.2 主题轮换实现（Config类方法）

```python
def _get_next_theme(self) -> str:
    """获取下一个主题（主题轮换）

    轮换策略：
    1. 读取上次使用的主题索引
    2. 选择下一个主题（循环）
    3. 保存当前选择供下次使用

    Returns:
        下一个主题的中文名称
    """
    # 可用主题列表（7种核心主题）
    available_themes = [
        '秋日暖光',    # 温暖治愈，橙色调
        '春日清新',    # 清新自然，绿色调
        '深海静谧',    # 深沉冷静，蓝色调
        '优雅金',      # 高端大气，金色调
        '活力红',      # 活力热情，红色调
        '简约蓝',      # 简约现代，蓝色调
        '专注绿',      # 专注沉稳，绿色调
    ]

    # 读取状态文件
    rotation_state = self._load_theme_rotation_state()
    last_index = rotation_state.get('last_index', -1)

    # 计算下一个主题索引（循环）
    next_index = (last_index + 1) % len(available_themes)
    next_theme = available_themes[next_index]

    # 保存状态
    self._save_theme_rotation_state({
        'last_index': next_index,
        'last_theme': next_theme,
        'last_update': datetime.now().isoformat()
    })

    return next_theme
```

### 5.3 主题Prompt生成（_get_theme_prompt方法）
```python
def _get_theme_prompt(self, theme_name: str, theme_desc: str) -> str:
    """根据主题名称生成对应的AI提示词"""
    theme_configs = {
        '秋日暖光': {
            'colors': {
                'primary': '#d97758',
                'secondary': '#c06b4d',
                'background': '#faf9f5',
                'card_bg': '#fef4e7',
                'text': '#4a413d',
                'border': '#d97758',
            },
            'style': '温暖治愈、橙色调、文艺美学',
            'features': ['卡片式布局', '米白方格纹理', '圆角18px', '柔和阴影'],
            'border_radius': '18px',
        },
        # ... 其他主题配置
    }
    # 生成详细的CSS样式Prompt...
```

### 5.3 广告图Markdown构建
```python
# 构建顶部广告图Markdown（在标题之前）
top_ad_md = ""
if enable_top_ad and top_ad_image:
    if top_ad_image.startswith('http'):
        top_ad_md = f"""
<div style="text-align: center; margin: 20px 0;">
<img src="{top_ad_image}" alt="顶部广告" style="width: 100%; max-width: 900px; height: auto;"/>
</div>

----
"""
    else:
        top_ad_md = f"![顶部广告]({top_ad_image})\n\n----\n"

# 构建Markdown：顶部广告图 → 标题 → 正文 → 底部广告图 → 签名
markdown = f"""{top_ad_md}# {question}

{structured_content}

{bottom_ad_md}---

*本文由总包大脑AI生成，仅供参考*
"""
```

---

---

## 六、成本优化策略（v3.4.0新增）

### 6.1 双模型配置

为了实现**0成本运行**，项目采用双模型策略：

| 模型 | 用途 | 成本 |
|------|------|------|
| **glm-4-flash** | 简单任务（生成问题、标题、图片提示词） | **免费** |
| **glm-4-plus** | 关键任务（内容结构化、HTML排版） | 收费 |

### 6.2 任务分类

**使用低成本模型（glm-4-flash）的场景**：
1. `generate_hot_question()` - 生成热点问题
2. `generate_catchy_title()` - 生成爆款标题
3. `generate_cover_image_prompt()` - 生成封面图片提示词

**必须使用高质量模型（glm-4-plus）的场景**：
1. `_structure_content_with_headings()` - 内容结构化（必须保证原文100%不变）
2. `convert_md_to_wechat_html_with_ai()` - HTML排版转换（最终输出质量）

### 6.3 配置示例

```ini
[智谱AI]
# 模型配置（降低成本策略）
# - 低成本模型（glm-4-flash）：免费，用于简单任务
# - 高质量模型（glm-4-plus）：收费，用于关键任务
低成本模型名称 = glm-4-flash
高质量模型名称 = glm-4-plus
```

### 6.4 代码实现

```python
# Config类中添加模型配置
self.zhipu_model_fast = self.config.get('智谱AI', '低成本模型名称', fallback='glm-4-flash')
self.zhipu_model_pro = self.config.get('智谱AI', '高质量模型名称', fallback='glm-4-plus')

# 简单任务使用低成本模型
response = self.client.chat.completions.create(
    model=self.config.zhipu_model_fast,  # glm-4-flash（免费）
    ...
)

# 关键任务使用高质量模型
response = self.client.chat.completions.create(
    model=self.config.zhipu_model_pro,  # glm-4-plus（收费）
    ...
)
```

### 6.5 成本对比

| 任务类型 | 原方案 | 优化后 | 节省 |
|---------|--------|--------|------|
| 生成问题 | glm-4-plus | glm-4-flash | 100% |
| 生成标题 | glm-4-plus | glm-4-flash | 100% |
| 图片提示词 | glm-4-plus | glm-4-flash | 100% |
| 内容结构化 | glm-4-plus | glm-4-plus | 0% |
| HTML排版 | glm-4-plus | glm-4-plus | 0% |
| **总体** | - | - | **~60%** |

---

## 七、文件结构

```
ZBBrain-Write/
├── ZBBrainArticle.py       # 主脚本（~8000行）
├── config.ini              # 配置文件（含敏感信息，不提交）
├── config.ini.example      # 配置模板
├── requirements.txt        # Python依赖
├── setup.bat               # Windows安装脚本
├── md2wechat.exe           # Markdown转微信工具
├── README.md               # 项目说明
├── DEVELOPMENT_REQUIREMENTS.md  # 本文档
├── image/
│   ├── top-image.jpg       # 顶部广告图
│   └── bottom-image.jpg    # 底部广告图
├── cover.jpg               # 文章封面图（900x500px）
├── browser_data/           # 浏览器用户数据（登录状态）
├── temp/                   # 临时文件目录
└── zbbrain_article.log     # 运行日志
```

---

## 七、依赖包清单（requirements.txt）

```txt
# Web Automation
playwright>=1.40.0
stagehand-py>=0.1.0

# HTTP Requests
requests>=2.31.0
httpx>=0.25.0

# AI SDK
zhipuai>=2.0.0

# Configuration
configparser>=6.0.0
python-dotenv>=1.0.0

# Logging
colorlog>=6.8.0

# Email
secure-smtplib>=0.1.1

# Data Processing
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Image Processing
Pillow>=10.0.0

# Date & Time
python-dateutil>=2.8.2
pytz>=2023.3

# Markdown Processing
markdown>=3.5.0

# Utilities
tqdm>=4.66.0

# WeChat integration
wechatpy>=1.8.18

# Browser automation support
patchright>=0.1.0
```

---

## 八、完整配置文件模板

```ini
# ============================================================
# ZBBrain-Write 配置文件
# EPC总承包微信公众号自动化文章生成工具
# ============================================================

[搜狗微信搜索]
搜狗微信搜索网址 = https://www.sogou.com/sogou?...
默认搜索关键词 = EPC总承包
默认翻页页数 = 5
最大翻页页数 = 10

[总包大脑]
总包大脑网址 = https://metaso.cn/s/rOw6BLS
用户数据目录 = ./browser_data
最大等待回复时间 = 600
回复检查间隔 = 5

[智谱AI]
api key = your-zhipu-api-key
api 地址 = https://open.bigmodel.cn/api/paas/v4/chat/completions
模型名称 = glm-4-plus
问题最小字符数 = 30
回复最小字符数 = 500

[微信公众号]
appid = your-wechat-appid
appsecret = your-wechat-secret
封面图片路径 = ./cover.jpg
默认作者 = 总包大脑
声明原创 = 1
开启评论 = 1

[工程豹公众号]
appid = your-appid
secret = your-secret

[总包说公众号]
appid = your-appid
secret = your-secret

[文章主题]
默认主题 = 秋日暖光
秋日暖光描述 = 温暖治愈，橙色调，文艺美学，适合情感故事、生活随笔
春日清新描述 = 清新自然，绿色调，生机盎然，适合旅行日记、自然主题
深海静谧描述 = 深沉冷静，蓝色调，专业稳重，适合技术文章、商务报告

[广告图设置]
显示顶部广告图 = true
顶部广告图路径 = ./image/top-image.jpg
显示底部广告图 = true
底部广告图路径 = ./image/bottom-image.jpg

[任务调度]
启用定时任务 = true
运行频率小时 = 2
停止运行小时 = 22
开始运行小时 = 6

[企业微信通知]
Webhook地址 = your-wechat-webhook-url

[邮件通知]
接收邮箱 = your-email@qq.com
SMTP服务器 = smtp.qq.com
SMTP端口 = 587
发件邮箱 = your-email@qq.com
授权码 = your-qq-authorization-code

[其他]
日志文件路径 = ./zbbrain_article.log
临时文件目录 = ./temp
调试模式 = false
最多重试次数 = 5
```

---

## 九、工作流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    ZBBrain-Write 工作流程                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 启动                                                      │
│    ├─ 加载 config.ini 配置                                   │
│    ├─ 初始化日志系统                                         │
│    └─ 判断运行模式（定时/单次）                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 爬取搜狗微信搜索                                          │
│    ├─ 访问搜狗微信搜索页面                                   │
│    ├─ 搜索关键词（默认: EPC总承包）                          │
│    ├─ 翻页爬取资讯（默认5页）                                │
│    └─ 提取文章标题、摘要、来源                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 智谱AI生成热点问题                                        │
│    ├─ 基于JTBD理论分析                                       │
│    ├─ 从资讯中提炼热点问题                                   │
│    └─ 验证问题长度（≥30字符）                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 总包大脑交互                                              │
│    ├─ 检查登录状态                                          │
│    │   └─ 如需登录，等待用户扫码                             │
│    ├─ 发送问题到总包大脑                                     │
│    ├─ 等待AI回复（最长600秒）                                │
│    ├─ 回复稳定性检测（连续6次不变）                          │
│    └─ 验证回答长度（≥500字符）                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 内容处理（重要：不修改原文）                              │
│    ├─ 仅添加Markdown标题结构(##, ###)                        │
│    ├─ 绝对禁止精炼、压缩、扩展原文                           │
│    └─ 保持原文100%完整                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Markdown构建                                              │
│    ├─ 顶部广告图（标题之前）                                 │
│    ├─ # 文章标题                                            │
│    ├─ 正文内容（带##/###标题）                               │
│    ├─ 底部广告图                                            │
│    └─ 签名：*本文由总包大脑AI生成，仅供参考*                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. 转换为微信HTML                                            │
│    ├─ 应用秋日暖光主题配色                                   │
│    │   ├─ primary: #d97758                                  │
│    │   ├─ background: #faf9f5                               │
│    │   ├─ card_bg: #fef4e7                                  │
│    │   └─ 圆角: 18px                                        │
│    ├─ 智谱AI专业排版                                        │
│    └─ 生成内联样式HTML                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. 微信公众号草稿                                            │
│    ├─ 上传封面图片到素材库                                   │
│    ├─ 创建草稿                                              │
│    │   ├─ 标题                                              │
│    │   ├─ 作者：总包大脑                                    │
│    │   ├─ 内容（HTML）                                      │
│    │   ├─ 封面图                                            │
│    │   ├─ 声明原创                                          │
│    │   └─ 开启评论                                          │
│    └─ 返回草稿ID                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. 发送通知                                                  │
│    ├─ 企业微信（Webhook）                                    │
│    │   └─ 发送成功/失败消息                                  │
│    └─ 邮件（可选）                                          │
│        └─ 发送详细报告                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. 定时调度（如启用）                                       │
│     ├─ 等待下次运行时间                                     │
│     ├─ 检查工作时间（6:00-22:00）                           │
│     └─ 循环执行                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十、关键约束与注意事项

### 10.1 内容保护（最高优先级）
- **总包大脑回答内容必须100%保留**
- 只允许添加`##`和`###`标题
- 严禁任何形式的内容修改

### 10.2 配置文件Section名称（必须一致）
- `[搜狗微信搜索]`
- `[总包大脑]`
- `[智谱AI]`
- `[微信公众号]`
- `[工程豹公众号]`
- `[总包说公众号]`
- `[文章主题]`
- `[广告图设置]`
- `[任务调度]`
- `[企业微信通知]`
- `[邮件通知]`
- `[其他]`

### 10.3 广告图位置
- 顶部广告图：**在标题之前**
- 底部广告图：**在正文之后、签名之前**

### 10.4 时区处理
- 所有时间计算使用北京时间（Asia/Shanghai）
- 使用pytz库处理时区

### 10.5 默认运行模式
- 配置文件 `启用定时任务 = true`
- 默认启动即为定时调度模式
- 使用 `--once` 参数才单次运行

---

## 十一、版本历史

| 版本 | 主要更新 |
|------|----------|
| v3.3.0 | **主题轮换**：每次运行自动更换7种主题，避免观众视觉疲劳 |
| v3.4.0 | **成本优化**：采用双模型策略，简单任务使用免费模型（glm-4-flash），实现0成本运行 |
| v3.2.0 | 定时调度模式默认启用，Beijing时区支持 |
| v2.5.0 | 监控增强、健康检查、异步任务队列、配置热重载 |
| v2.4.0 | SQLite持久化、指数退避重试、优雅关闭 |
| v2.3.0 | 安全增强、资源管理、上下文管理器 |
| v2.2.0 | 性能监控、缓存机制、类型提示 |
| v2.1.0 | 代码重构、异常类层次、常量管理 |
| v2.0.0 | Playwright异步API、完整文章生成流程 |

---

## 十二、验收标准

当AI收到本文档后，应能够一次性完成以下功能：

1. ✅ 从搜狗微信搜索爬取EPC总承包资讯
2. ✅ 使用智谱AI生成热点问题
3. ✅ 发送问题到总包大脑并获取回答
4. ✅ 保持原文内容100%不变（仅添加标题）
5. ✅ **每次运行自动轮换主题（7种主题循环）**
6. ✅ 在标题前插入顶部广告图
7. ✅ 在正文后插入底部广告图
8. ✅ 创建微信公众号草稿（原创声明+评论）
9. ✅ 发送企业微信和邮件通知
10. ✅ 定时调度模式默认启用
11. ✅ 支持北京时间工作时间控制
12. ✅ 主题轮换状态持久化到theme_rotation.json
13. ✅ **双模型策略：简单任务用glm-4-flash（免费），关键任务用glm-4-plus**
14. ✅ **实现约60%成本节省，力争0成本运行**

---

**文档版本**: 1.2
**最后更新**: 2026-02-26
**适用于**: ZBBrain-Write v3.4.0
**适用于**: ZBBrain-Write v3.3.0
