# Security Policy

[中文](#安全策略) | [English](#security-policy)

---

## 安全策略

### 🔐 支持版本

我们为以下版本提供安全更新：

| 版本 | 支持状态 |
| ------- | ------------------ |
| 3.5.x   | ✅ 活跃支持 |
| 3.4.x   | ✅ 安全更新 |
| < 3.4   | ❌ 不再支持 |

### 🚨 报告安全漏洞

如果您发现安全漏洞，**请勿**通过公开 Issue 报告。

请通过以下方式私下报告：

1. **GitHub Security Advisories**（推荐）
   - 访问项目的 [Security](https://github.com/your-repo/ZBBrain-Write/security/advisories) 页面
   - 点击 "Report a vulnerability"

2. **邮件联系**
   - 发送邮件至项目维护者
   - 邮件标题: `[SECURITY] ZBBrain-Write 漏洞报告`

### 📋 报告内容

请包含以下信息：

- 漏洞描述
- 复现步骤
- 影响范围
- 可能的修复方案（如有）
- 您的联系方式

### ⏱️ 响应时间

- **确认收到**: 24小时内
- **初步评估**: 3个工作日内
- **修复时间表**: 根据严重程度
  - 严重: 7天内
  - 高危: 14天内
  - 中危: 30天内
  - 低危: 下个版本

### 🛡️ 安全最佳实践

#### 配置文件安全

**⚠️ 绝对不要提交包含真实凭证的配置文件！**

```bash
# 确保 config.ini 被忽略
git status | grep config.ini
# 应该显示: (未被跟踪或已忽略)

# 如果不小心提交了，立即：
# 1. 轮换所有暴露的密钥
# 2. 从 git 历史中移除敏感信息
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config.ini" \
  --prune-empty --tag-name-filter cat -- --all
```

#### API 密钥管理

```ini
# ❌ 不要硬编码
api_key = sk-xxxxx

# ✅ 使用环境变量
api_key = ${ZHIPU_API_KEY}
```

#### 微信公众号安全

1. **定期轮换 AppSecret**
   - 每90天更换一次
   - 发现泄露时立即更换

2. **IP 白名单**
   - 只添加必要的服务器IP
   - 定期审核白名单

3. **权限最小化**
   - 只授予必要的接口权限
   - 使用子账号隔离权限

### 🔧 安全配置检查清单

- [ ] `config.ini` 未被 git 跟踪
- [ ] `wechat_accounts.json` 未被 git 跟踪
- [ ] 所有 API 密钥通过环境变量或配置文件注入
- [ ] 生产环境禁用调试模式 (`调试模式 = false`)
- [ ] 日志中不包含敏感信息
- [ ] 定期更新依赖包 (`pip install --upgrade -r requirements.txt`)
- [ ] 使用 HTTPS 协议访问所有 API

---

## Security Policy

### 🔐 Supported Versions

We provide security updates for the following versions:

| Version | Supported |
| ------- | ------------------ |
| 3.5.x   | ✅ Active |
| 3.4.x   | ✅ Security fixes |
| < 3.4   | ❅ End of life |

### 🚨 Reporting a Vulnerability

If you discover a security vulnerability, **please do NOT** report it through public Issues.

Please report privately via:

1. **GitHub Security Advisories** (Recommended)
   - Visit the project's [Security](https://github.com/your-repo/ZBBrain-Write/security/advisories) page
   - Click "Report a vulnerability"

2. **Email**
   - Send to project maintainers
   - Subject: `[SECURITY] ZBBrain-Write Vulnerability Report`

### 📋 What to Include

- Description of the vulnerability
- Steps to reproduce
- Impact assessment
- Possible fix (if available)
- Your contact information

### ⏱️ Response Timeline

- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 3 business days
- **Fix Timeline**: Based on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next release

### 🛡️ Security Best Practices

#### Configuration File Security

**⚠️ NEVER commit configuration files with real credentials!**

```bash
# Verify config.ini is ignored
git status | grep config.ini
# Should show: (untracked or ignored)

# If accidentally committed, immediately:
# 1. Rotate all exposed secrets
# 2. Remove sensitive info from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config.ini" \
  --prune-empty --tag-name-filter cat -- --all
```

#### API Key Management

```ini
# ❌ Don't hardcode
api_key = sk-xxxxx

# ✅ Use environment variables
api_key = ${ZHIPU_API_KEY}
```

#### WeChat Official Account Security

1. **Rotate AppSecret Regularly**
   - Every 90 days
   - Immediately upon leak detection

2. **IP Whitelist**
   - Only add necessary server IPs
   - Regularly audit the whitelist

3. **Least Privilege**
   - Grant only necessary API permissions
   - Use sub-accounts for isolation

### 🔧 Security Configuration Checklist

- [ ] `config.ini` is not tracked by git
- [ ] `wechat_accounts.json` is not tracked by git
- [ ] All API keys injected via environment or config
- [ ] Debug mode disabled in production (`调试模式 = false`)
- [ ] Logs contain no sensitive information
- [ ] Dependencies updated regularly
- [ ] HTTPS used for all API calls

---

## Acknowledgments

We thank all security researchers who responsibly disclose vulnerabilities to help keep ZBBrain-Write secure.

### Hall of Fame

<!-- Security researchers will be listed here with their permission -->
- *Awaiting first contributor*

---

**Last Updated**: 2026-03-15
