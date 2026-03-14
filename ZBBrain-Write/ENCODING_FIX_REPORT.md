# 微信草稿API编码问题修复报告

**修复时间**: 2026-02-25
**修复文件**: [ZBBrainArticle.py:5950-5956](e:\CPOPC\ZBBrain-Write\ZBBrain-Write\ZBBrainArticle.py#L5950)
**问题ID**: errcode=45003 title size out of limit

---

## 🎯 问题根因

### 错误代码（修复前）
```python
# 第5950行
response = requests.post(url, json=data, timeout=30)
```

### 问题分析

1. **缺少charset声明**
   - `requests.post(json=data)` 自动设置 `Content-Type: application/json`
   - **但没有添加 `charset=utf-8` 声明**

2. **中文被转为Unicode转义**
   - `json.dumps()` 默认使用 `ensure_ascii=True`
   - 中文被转换为 `\u5b9e\u64cd` 格式
   - 示例：`"title": "\u5b9e\u64cd\uff1a4\u6b65"`

3. **微信API解析错误**
   - 接收到没有charset的请求
   - 看到Unicode转义序列
   - **无法正确确定编码来计算字节长度**
   - 导致：`errcode=45003 title size out of limit`

---

## ✅ 修复方案

### 修复代码（修复后）
```python
# 第5950-5956行
# 使用正确的编码方式：显式UTF-8编码 + charset声明（GitHub最佳实践）
# 修复微信API 45003错误：中文被正确解析，不会被误判为长度超限
headers = {'Content-Type': 'application/json; charset=utf-8'}
json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
self.logger.debug(f"请求Content-Type: {headers['Content-Type']}")
self.logger.debug(f"JSON数据字节长度: {len(json_data)}")
response = requests.post(url, data=json_data, headers=headers, timeout=30)
```

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| Content-Type | `application/json` | `application/json; charset=utf-8` |
| charset声明 | ❌ 缺失 | ✅ 显式声明 |
| 中文编码 | `\u5b9e\u64cd` (转义) | `实操` (原始UTF-8) |
| JSON字节长度 | 322字节 | 193字节 |
| 微信API解析 | ⚠️ 可能出错 | ✅ 正确解析 |

---

## 🔍 详细技术分析

### 为什么会导致45003错误？

#### 修复前的请求流程
```
1. requests.post(url, json=data)
   ↓
2. 自动设置: Content-Type: application/json
   ↓
3. 自动序列化: json.dumps(data, ensure_ascii=True)
   ↓
4. 中文转为: {"title": "\u5b9e\u64cd"}
   ↓
5. 微信API收到请求
   ↓
6. 检查Content-Type: 只有application/json，没有charset
   ↓
7. 看到Unicode转义: \u5b9e\u64cd
   ↓
8. ❌ 无法确定编码方式计算长度
   ↓
9. 错误: errcode=45003
```

#### 修复后的请求流程
```
1. 设置headers: {'Content-Type': 'application/json; charset=utf-8'}
   ↓
2. 显式编码: json.dumps(data, ensure_ascii=False).encode('utf-8')
   ↓
3. 中文保持: {"title": "实操"}
   ↓
4. 微信API收到请求
   ↓
5. 检查Content-Type: application/json; charset=utf-8
   ↓
6. 明确知道使用UTF-8编码
   ↓
7. 正确解析中文: 实操
   ↓
8. ✅ 正确计算字节长度
   ↓
9. 成功创建草稿
```

---

## 🧪 验证结果

### 语法验证
```bash
✓ ZBBrainArticle模块导入成功
✓ JSON编码正常
✓ requests模块可用
✓ 代码语法正确
```

### 编码对比测试
```python
# 测试数据
title = 'EPC实操：4步平台创构高效管控'
digest = '在使用EPC总承包模式的项目投标阶段'

# 修复前
JSON字节长度: 322字节
中文编码: Unicode转义

# 修复后
JSON字节长度: 193字节 (减少40%)
中文编码: 原始UTF-8字节
```

---

## 📚 参考资源

### GitHub最佳实践
参考了以下GitHub项目的实现方式：
1. **wechatpy/wechatpy** - Python微信SDK
2. **GitHub社区讨论** - requests.post编码问题

### 关键技术点
1. **Content-Type with charset**
   ```python
   headers = {'Content-Type': 'application/json; charset=utf-8'}
   ```

2. **json.dumps ensure_ascii**
   ```python
   json.dumps(data, ensure_ascii=False)  # 保持中文原样
   ```

3. **显式UTF-8编码**
   ```python
   .encode('utf-8')  # 显式编码为UTF-8字节流
   ```

---

## 🚀 预期效果

### 修复前
```
✗ errcode=45003
✗ errmsg=title size out of limit
✗ 创建草稿失败
```

### 修复后
```
✓ Content-Type: application/json; charset=utf-8
✓ 中文被正确解析
✓ 字节长度正确计算
✓ 创建草稿成功
```

---

## 📝 改进点

### 新增的调试日志
```python
self.logger.debug(f"请求Content-Type: {headers['Content-Type']}")
self.logger.debug(f"JSON数据字节长度: {len(json_data)}")
```

**作用**：
- 便于排查编码问题
- 记录实际发送的字节长度
- 符合生产级日志要求

### 代码注释
```python
# 使用正确的编码方式：显式UTF-8编码 + charset声明（GitHub最佳实践）
# 修复微信API 45003错误：中文被正确解析，不会被误判为长度超限
```

**作用**：
- 说明修复原因
- 记录参考来源（GitHub最佳实践）
- 便于后续维护

---

## ✅ 修复验证清单

- [x] 代码语法正确
- [x] 模块导入成功
- [x] JSON编码测试通过
- [x] Content-Type头正确设置
- [x] 中文字符保持原样
- [x] 调试日志已添加
- [x] 代码注释完整

---

## 🎉 结论

**问题**: 微信草稿API返回 `errcode=45003 title size out of limit`

**根因**: `requests.post(json=data)` 缺少charset声明，中文被转义导致微信API无法正确解析

**修复**: 显式设置 `Content-Type: application/json; charset=utf-8` + `ensure_ascii=False`

**状态**: ✅ 已修复，待生产环境验证

---

**修复完成时间**: 2026-02-25
**下一步**: 重新运行项目，验证草稿创建功能
