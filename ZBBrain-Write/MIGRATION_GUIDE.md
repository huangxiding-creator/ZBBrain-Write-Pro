# ZBBrain-Write 项目迁移指南

本指南帮助您将 ZBBrain-Write 项目从当前电脑迁移到另一台笔记本电脑。

## 迁移步骤概览

1. 准备迁移包
2. 在新电脑上安装依赖环境
3. 复制项目文件
4. 安装 Claude Code Skill
5. 配置并测试运行

---

## 第一步：准备迁移包

在当前电脑上，将以下文件打包：

### 1.1 项目核心文件
创建一个文件夹 `ZBBrain-Write/`，包含以下文件：

```
ZBBrain-Write/
├── ZBBrainArticle.py          # 核心业务逻辑
├── ZBBrainArticle_GUI.py      # GUI界面
├── config.ini                  # 配置文件（包含API密钥）
├── zbbrain_article.log         # 日志文件（可选）
├── image/                      # 广告图目录
│   ├── top-image.jpg
│   └── bottom-image.jpg
├── temp/                       # 临时文件目录（可选）
├── fix_existing_markdown_files.py
├── test_ad_image_fix.py
├── test_md2wechat_simulation.py
└── BEST_PRACTICES_METASO_INPUT.md  # 总包大脑操作最佳实践
```

### 1.2 Skill 文件
创建一个文件夹 `ZBBrain-Write-Skill/`，包含以下文件：

```
ZBBrain-Write-Skill/
├── SKILL.md
├── scripts/
│   ├── update_config.py
│   ├── validate_skill.py
│   └── test_skill_standalone.py
├── references/
│   └── REFERENCES.md
└── assets/
    └── README.md
```

### 1.3 打包
将上述两个文件夹压缩为：
- `ZBBrain-Write-Project.zip`（包含项目文件）
- `ZBBrain-Write-Skill.zip`（包含Skill文件）

---

## 第二步：在新电脑上安装依赖环境

### 2.1 安装 Python
下载并安装 Python 3.10 或更高版本：
- 访问：https://www.python.org/downloads/
- 下载 Windows installer
- 安装时勾选 "Add Python to PATH"

### 2.2 安装依赖库
打开命令行，执行：

```bash
# 安装核心依赖
pip install playwright configparser requests zhipuai

# 安装 md2wechat（微信格式转换工具）
pip install md2wechat

# 安装 Playwright 浏览器
playwright install chromium
```

### 2.3 安装 Claude Code
如果新电脑还没有安装 Claude Code：
- 访问：https://claude.ai/download
- 下载并安装 Claude Code

---

## 第三步：复制项目文件

### 3.1 创建项目目录
在新电脑上创建项目目录（推荐位置）：
- Windows: `D:\ZBBrain-Write\`
- 或: `C:\Users\<你的用户名>\ZBBrain-Write\`

### 3.2 解压项目文件
将 `ZBBrain-Write-Project.zip` 解压到上述目录。

### 3.3 验证文件结构
确保以下文件存在：
```
D:\ZBBrain-Write\
├── ZBBrainArticle.py          ✓
├── ZBBrainArticle_GUI.py      ✓
├── config.ini                  ✓
├── image/
│   ├── top-image.jpg          ✓
│   └── bottom-image.jpg       ✓
└── temp/
```

---

## 第四步：安装 Claude Code Skill

### 4.1 定位 Skill 目录
Claude Code Skill 目录位置：
- Windows: `C:\Users\<你的用户名>\.claude\skills\`

### 4.2 创建 Skill 目录
```bash
# 创建 Skill 目录
mkdir "C:\Users\<你的用户名>\.claude\skills\ZBBrain-Write"
```

### 4.3 解压 Skill 文件
将 `ZBBrain-Write-Skill.zip` 解压到上述目录。

### 4.4 验证 Skill 结构
确保以下结构：
```
C:\Users\<你的用户名>\.claude\skills\ZBBrain-Write\
├── SKILL.md                   ✓
├── scripts/
│   ├── update_config.py       ✓
│   ├── validate_skill.py      ✓
│   └── test_skill_standalone.py ✓
├── references/
│   └── REFERENCES.md          ✓
└── assets/
    └── README.md              ✓
```

### 4.5 重启 Claude Code
关闭并重新打开 Claude Code，Skill 会自动加载。

---

## 第五步：配置并测试运行

### 5.1 检查配置文件
打开 `D:\ZBBrain-Write\config.ini`，确认以下配置：

```ini
[智谱AI]
api key = 你的智谱API密钥

[微信公众号]
appid = 你的公众号AppID
appsecret = 你的公众号Secret

[工程豹公众号]
appid = wxab4386f9c12d3636
secret = ff9f895ed854f5df15ff88ec8b69f818

[总包说公众号]
appid = wx580e54435d78a2b7
secret = a3a294fbe9805b4cf65927d1282ab076
```

### 5.2 修改项目路径（如果需要）
如果新电脑上项目路径不是 `D:\ZBBrain-Write\`，需要修改：

1. 在 `config.ini` 中修改路径配置：
```ini
[其他]
日志文件路径 = ./zbbrain_article.log
临时文件目录 = ./temp
```

2. 确保 Skill 中的脚本也使用正确路径：
- 编辑 `C:\Users\<你的用户名>\.claude\skills\ZBBrain-Write\scripts\test_skill_standalone.py`
- 修改 `project_path` 为你的实际路径

### 5.3 测试运行
```bash
cd D:\ZBBrain-Write

# 测试命令行模式
python ZBBrainArticle.py --keyword "EPC总承包" --pages 1

# 或测试 GUI 模式
python ZBBrainArticle_GUI.py
```

### 5.4 验证 Skill 加载
打开 Claude Code，输入：
```
我可以看到哪些技能？
```

确认列表中包含 **ZBBrain-Write** Skill。

---

## 常见问题

### Q1: ImportError: No module named 'playwright'
**A**: 未安装 Playwright，执行：
```bash
pip install playwright
playwright install chromium
```

### Q2: 微信公众号 IP 白名单错误
**A**: 新电脑的 IP 地址可能不同，需要：
1. 运行项目获取当前外网 IP
2. 登录微信公众平台添加新 IP 到白名单

### Q3: 智谱 AI API 调用失败
**A**: 检查 config.ini 中的 API key 是否正确，或网络是否可以访问智谱 AI。

### Q4: Skill 没有出现在 Claude Code 中
**A**: 确保：
1. Skill 目录路径正确
2. SKILL.md 文件存在且格式正确
3. 已重启 Claude Code

### Q5: GUI 界面显示乱码
**A**: 确保系统已安装中文字体（微软雅黑），或使用命令行模式。

---

## 迁移检查清单

使用此清单确保迁移成功：

- [ ] Python 3.10+ 已安装
- [ ] 所有依赖库已安装（playwright, configparser, requests, zhipuai, md2wechat）
- [ ] Playwright 浏览器已安装（chromium）
- [ ] Claude Code 已安装
- [ ] 项目文件已复制到新电脑
- [ ] config.ini 配置正确（API 密钥、公众号配置）
- [ ] 广告图文件存在（image/top-image.jpg, image/bottom-image.jpg）
- [ ] Skill 文件已复制到正确的目录
- [ ] Skill 已在 Claude Code 中加载
- [ ] 命令行模式测试成功
- [ ] GUI 模式测试成功
- [ ] 微信公众号 IP 白名单已配置
- [ ] 完整项目运行测试成功
- [ ] 已阅读 BEST_PRACTICES_METASO_INPUT.md 了解最佳实践

---

## 技术支持

如遇到迁移问题，请检查：

1. **日志文件**: `D:\ZBBrain-Write\zbbrain_article.log`
2. **错误信息**: 记录完整的错误堆栈
3. **环境信息**: Python 版本、操作系统版本

---

## 经验教训与最佳实践

### 总包大脑输入框操作经验（2024-02-24验证成功）

**问题背景**：
自动化操作总包大脑时，JavaScript能找到textarea元素，但`visible=false, width=0, height=0`。

**根本原因**：
总包大脑使用动态渲染，输入框需要等待才能真正可见。

**成功解决方案**：
```python
# 1. 使用 wait_for_selector 并设置 state='visible'
elem = await page.wait_for_selector(
    'textarea[placeholder*="问"]',
    state='visible',  # 关键参数
    timeout=10000
)

# 2. 使用 fill() 方法输入
await elem.fill(question)

# 3. 使用 Enter 键发送
await page.keyboard.press('Enter')
```

**关键成功因素**：
- `state='visible'` - 等待元素真正可见
- `placeholder*="问"` - 使用稳定的选择器
- `fill()` 方法 - 直接设置值，不模拟键盘
- `Enter` 键 - 通用发送方式
- 10秒超时 - 给予动态渲染足够时间

**生产验证**：
- 2024-02-24 生产运行 100% 成功
- 成功获取2628字符的答案
- 完整文章发布成功

详细文档请参阅：[BEST_PRACTICES_METASO_INPUT.md](BEST_PRACTICES_METASO_INPUT.md)

### IP 白名单配置经验

**问题**：
微信公众平台 IP 白名单生效需要等待几分钟。

**解决方案**：
1. 提前添加 IP 到白名单
2. 等待5-10分钟让白名单生效
3. 测试环境可临时跳过检查（生产环境需恢复）

**验证方法**：
运行项目时会显示当前外网IP，确保该IP在微信公众平台白名单中。

---

迁移完成后，您就可以在新电脑上正常使用 ZBBrain-Write Skill 了！
