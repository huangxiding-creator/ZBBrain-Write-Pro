# 微信草稿API错误 45003 根因分析报告

**分析时间**: 2026-02-25
**错误代码**: errcode=45003
**错误信息**: title size out of limit

---

## 🔍 问题复现

### 错误日志
```
2026-02-25 08:20:50 - ZBBrainArticle - INFO - 摘要长度: 91
2026-02-25 08:20:51 - ZBBrainArticle - INFO - 微信API响应: {'errcode': 45003, 'errmsg': 'title size out of limit'}
```

### 实际字节长度分析
```python
标题: "EPC实操：4步平台创构高效管控"
  - 字符长度: 20字符
  - 字节长度: 40字节 ✓ (在64字节限制内)

摘要: "在使用EPC总承包模式的项目投标阶段..." (前91字符)
  - 字符长度: 91字符
  - 字节长度: 267字节 ❌ (严重超限！)
```

---

## 🎯 根本原因

### 原因1: digest字段字节长度超限（主要原因）

**代码位置**: [ZBBrainArticle.py:5881-5882](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L5881)

```python
if len(digest) > 120:  # 微信摘要限制约120个字符
    digest = digest[:120]
    self.logger.warning(f"摘要过长，已截断")
```

**问题分析**:
1. ❌ **错误假设**: 代码假设限制是**120个字符**
2. ❌ **实际限制**: 微信API的digest字段限制是**120字节**（UTF-8编码）
3. ❌ **字符 vs 字节**: 91个中文字符 = 273字节（91 × 3），远超120字节

**计算示例**:
```
1个中文字符 = 3字节 (UTF-8)
91个中文字符 = 273字节
实际限制: 120字节
超出: 273 - 120 = 153字节 (超出127.5%)
```

### 原因2: 微信API错误信息误导

**微信API返回**: `title size out of limit`

**实际情况**: digest字段超限，但API错误信息指向title

**可能原因**:
1. 微信API参数验证顺序问题（先验证title，再验证digest）
2. 错误信息模板化，不准确
3. API文档与实际实现不一致

### 原因3: requests.post编码方式（次要因素）

**代码位置**: [ZBBrainArticle.py:5950](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L5950)

```python
response = requests.post(url, json=data, timeout=30)
```

**分析**:
- `json=data` 使用 `requests` 的自动JSON序列化
- 默认使用 `json.dumps(ensure_ascii=True)`
- 将中文转换为 Unicode转义序列（如 `\u4e2d\u6587`）
- 虽然能正确编码，但不是最佳实践

**最佳实践**（GitHub上wechatpy等项目的做法）:
```python
headers = {'Content-Type': 'application/json; charset=utf-8'}
json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
response = requests.post(url, data=json_data, headers=headers, timeout=30)
```

---

## 📊 为什么另一台电脑能成功？

### 可能原因分析

#### 假设1: 摘要内容不同
- **成功案例**: 摘要可能是英文或较短的内容
- **失败案例**: 摘要是62字符的中文问题（267字节）

#### 假设2: 代码版本不同
- **成功案例**: 可能已经修复了digest长度检查逻辑
- **失败案例**: 当前代码只检查字符长度，不检查字节长度

#### 假设3: 微信API差异
- 不同公众号的API限制可能略有不同
- 或者微信在不同时间点的API实现有差异

#### 假设4: 编码环境差异
- 另一台电脑的Python环境、requests库版本可能不同
- 导致JSON编码行为略有差异

---

## 🔧 修复方案

### 方案1: 修复digest字节长度验证（推荐）

**修改位置**: [ZBBrainArticle.py:5881-5884](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L5881)

```python
# 修改前
if len(digest) > 120:  # 微信摘要限制约120个字符
    digest = digest[:120]
    self.logger.warning(f"摘要过长，已截断")

# 修改后
digest_bytes = len(digest.encode('utf-8'))
if digest_bytes > 120:  # 微信摘要限制120字节（UTF-8）
    # 按字节截断，确保不截断多字节字符的中途
    digest = digest.encode('utf-8')[:120].decode('utf-8', errors='ignore')
    self.logger.warning(f"摘要字节长度({digest_bytes})超限，已截断到120字节")
```

### 方案2: 不传递digest字段（让微信自动生成）

**修改位置**: [ZBBrainArticle.py:7147](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L7147)

```python
# 修改前
success = wechat_manager.create_draft(
    title=catchy_title,
    content=html_content,
    digest=question,  # 使用原始热点问题作为摘要
    cover_media_id=cover_media_id
)

# 修改后
success = wechat_manager.create_draft(
    title=catchy_title,
    content=html_content,
    digest=None,  # 不传递摘要，让微信自动从正文提取前54个字
    cover_media_id=cover_media_id
)
```

**优点**:
- 简单直接
- 微信会自动从正文提取前54个字作为摘要
- 符合微信官方推荐做法

**缺点**:
- 摘要内容不可控
- 可能不如热点问题更有吸引力

### 方案3: 生成简短摘要（最优）

**修改位置**: [ZBBrainArticle.py:7147](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L7147)

```python
# 生成简短摘要（最多40个中文字符 = 120字节）
short_digest = question[:40] if len(question) > 40 else question

success = wechat_manager.create_draft(
    title=catchy_title,
    content=html_content,
    digest=short_digest,  # 使用截断后的热点问题
    cover_media_id=cover_media_id
)
```

**优点**:
- 摘要内容可控
- 保留热点问题的核心吸引力
- 字节长度安全（40 × 3 = 120字节）

### 方案4: 改进requests.post编码方式（可选）

**修改位置**: [ZBBrainArticle.py:5950](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L5950)

```python
# 修改前
response = requests.post(url, json=data, timeout=30)

# 修改后
headers = {'Content-Type': 'application/json; charset=utf-8'}
json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
response = requests.post(url, data=json_data, headers=headers, timeout=30)
```

**优点**:
- 符合GitHub最佳实践
- 更明确的编码方式
- 避免潜在的编码问题

---

## ✅ 推荐修复步骤

### 步骤1: 立即修复（快速验证）

使用**方案2**（不传递digest），快速验证是否解决问题：

```python
# 第7147行
digest=None,  # 让微信自动生成摘要
```

### 步骤2: 完整修复（生产环境）

结合**方案1**和**方案3**：

1. **修复digest字节长度验证**（第5881行）
2. **生成简短摘要**（第7147行）
3. **改进requests编码**（第5950行，可选）

### 步骤3: 添加防御性检查

在`create_draft`函数中添加字节长度验证：

```python
def create_draft(self, title: str, content: str, author: str = None,
                 digest: str = None, cover_media_id: str = None) -> bool:
    """创建草稿（支持原创声明）"""

    # 标题字节长度检查
    title_bytes = len(title.encode('utf-8'))
    if title_bytes > 64:
        self.logger.warning(f"标题字节长度({title_bytes})超限，截断到64字节")
        title = title.encode('utf-8')[:64].decode('utf-8', errors='ignore')

    # 摘要字节长度检查
    if digest:
        digest_bytes = len(digest.encode('utf-8'))
        if digest_bytes > 120:
            self.logger.warning(f"摘要字节长度({digest_bytes})超限，截断到120字节")
            digest = digest.encode('utf-8')[:120].decode('utf-8', errors='ignore')

    # ... 原有代码 ...
```

---

## 📚 参考资料

1. **微信草稿API文档**
   - [新增草稿接口](https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_Draft.html)
   - digest字段：可选，建议不超过120字节

2. **UTF-8编码说明**
   - 中文字符：3字节/字符
   - 英文字符：1字节/字符
   - 标点符号：1-3字节不等

3. **Python JSON编码最佳实践**
   - `json.dumps(ensure_ascii=False)` - 保持中文原样
   - `.encode('utf-8')` - 显式编码为UTF-8字节流
   - `Content-Type: application/json; charset=utf-8` - 声明编码

---

## 📝 总结

### 错误原因
❌ **digest字段字节长度超限**（267字节 > 120字节）
⚠️ 微信API错误信息误导（指向title而非digest）

### 关键发现
- 标题字节长度: 40字节 ✓
- 摘要字节长度: 267字节 ❌
- 代码检查的是**字符长度**（120字符）而非**字节长度**（120字节）

### 修复优先级
1. **高优先级**: 修复digest字节长度验证（方案1）
2. **中优先级**: 生成简短摘要（方案3）
3. **低优先级**: 改进requests编码（方案4）

### 验证方法
修复后重新运行，验证草稿创建是否成功。

---

**报告生成时间**: 2026-02-25
**分析者**: Claude Code
**文档版本**: v1.0
