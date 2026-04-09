# 总包大脑输入框检测修复 - 快速参考

## 修复位置
文件：`d:\ZBBrain-Write\ZBBrainArticle.py`
方法：`_send_question_fallback` 及相关辅助方法（第4472行起）

## 快速理解

### 问题根源
原代码使用简单的 JavaScript 查找输入框，但总包大脑的输入框可能是：
- 动态渲染的（需要等待）
- 最初隐藏的（width=0, height=0）
- 需要滚动到特定位置才可见

### 解决方案
实现 **5层递进式检测策略**，从标准方法到fallback，确保成功率。

## 5层策略概览

```
_send_question_fallback()
│
├─ 策略1: wait_for_selector (标准选择器)
│  ├─ 等待元素出现并可见
│  ├─ 超时: 10秒
│  └─ 选择器: textarea, contenteditable, input等
│
├─ 策略2: Playwright Locator (高级定位)
│  ├─ get_by_text, get_by_placeholder, get_by_role
│  ├─ filter(is_visible=True)
│  └─ 利用Playwright智能定位
│
├─ 策略3: IntersectionObserver (监听DOM变化)
│  ├─ 注入JavaScript监听器
│  ├─ 自动检测元素何时可见
│  └─ 超时: 15秒
│
├─ 策略4: JavaScript智能搜索 (评分系统)
│  ├─ 多次强制滚动
│  ├─ 智能评分: 位置 + 宽度
│  └─ 尝试3次
│
└─ 策略5: 最后Fallback (暴力尝试)
   ├─ 获取所有输入元素
   ├─ 按宽度排序
   └─ 逐个尝试前10个
```

## 关键方法说明

### 主入口
```python
async def _send_question_fallback(self, question: str):
    """智能回退方法：使用多重策略检测并发送问题"""
```

### 辅助方法
```python
# 策略实现
async def _try_wait_selector_strategy(question, debug_dir)
async def _try_locator_strategy(question, debug_dir)
async def _try_intersection_observer_strategy(question, debug_dir)
async def _try_js_smart_search_strategy(question, debug_dir)
async def _try_last_resort_strategy(question, debug_dir)

# 通用辅助
async def _scroll_to_bottom_forcefully()
async def _input_and_send(element, question, debug_dir, strategy_name)
async def _try_send_button()
```

## 使用示例

### 基本使用（自动）
```python
# 在 ask_question 方法中自动调用
await self._send_question_fallback(question)
```

### 调试模式
查看详细日志和截图：
```python
# 日志会输出每个策略的执行情况
# 截图保存在 debug_dir 目录
- before_send.png          # 发送前完整页面
- after_input_{strategy}.png  # 各策略输入后的截图
```

## 配置参数

### 可调整的超时时间
```python
# 策略1: wait_for_selector
timeout=10000  # 10秒

# 策略3: IntersectionObserver
timeout=15000  # 15秒

# 策略4: 智能搜索尝试次数
for attempt in range(3)  # 3次

# 策略5: 尝试元素数量
for elem_info in inputs_info[:10]  # 前10个
```

### 选择器优先级
```python
standard_selectors = [
    'textarea[placeholder*="问"]',      # 最高优先级
    'textarea[placeholder*="输入"]',
    'textarea[placeholder*="问题"]',
    'div[contenteditable="true"]:visible',
    'textarea:not([style*="display: none"])',
    # ... 更多选择器
]
```

## 日志输出示例

```
============================================================
策略1：使用wait_for_selector等待标准选择器
============================================================
尝试选择器: textarea[placeholder*="问"]
✓ 找到可见元素: textarea[placeholder*="问"]
✓ 成功点击元素
✓ 使用fill成功输入
✓ 点击发送按钮成功: button:has-text("发送")
✓ 策略 'wait_selector' 完全成功
```

## 常见问题

### Q: 为什么需要5层策略？
A: 总包大脑的输入框可能在不同情况下以不同方式呈现，多层策略确保适应各种场景。

### Q: 性能影响？
A: 策略1通常就足够了（10秒内），后续策略只在前面失败时执行，整体影响可控。

### Q: 如何自定义？
A: 修改相应策略方法中的选择器列表、超时时间或尝试次数。

### Q: 调试信息在哪里？
A:
- 日志：通过 logger 输出，查看控制台或日志文件
- 截图：保存在 `config.temp_dir` 目录

## 测试建议

1. **功能测试**：在真实页面上测试能否成功输入和发送
2. **性能测试**：测量各策略执行时间
3. **容错测试**：模拟各种失败场景（隐藏元素、延迟加载等）
4. **日志验证**：检查日志输出是否详细准确

## 维护建议

1. **定期检查**：总包大脑页面结构变化时，更新选择器
2. **性能监控**：记录各策略成功率，优化优先级
3. **日志清理**：定期清理 debug_dir 中的截图
4. **版本记录**：重大修改时更新此文档

## 相关文件

- 主文件：`ZBBrainArticle.py`
- 详细文档：`FIX_SUMMARY.md`
- 本文档：`INPUT_FIX_QUICK_REFERENCE.md`

## 技术栈

- **Playwright**: 浏览器自动化
- **JavaScript**: DOM操作和IntersectionObserver
- **Python**: 异步编程和错误处理

---

修复日期：2026-02-24
状态：已完成并验证语法
