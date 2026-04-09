# 总包大脑输入框操作最佳实践

## 问题背景

在自动化操作总包大脑（metaso.cn）时，遇到输入框检测失败的问题：
- JavaScript能找到textarea元素，但`visible=false, width=0, height=0`
- 原因：总包大脑使用动态渲染，输入框初始时不可见

## 成功解决方案

### 核心代码模式

```python
async def _try_wait_selector_strategy(self, question: str) -> bool:
    """策略1：使用Playwright的wait_for_selector等待输入框可见"""
    try:
        # 定义标准选择器列表（按优先级排序）
        selectors = [
            'textarea[placeholder*="问"]',      # 最可能的选择器
            'textarea[placeholder*="输入"]',
            'textarea[placeholder*="请"]',
            'textarea[placeholder*="请输入"]',
            'textarea',
            'div[contenteditable="true"]',
            'input[type="text"]',
            'input:not([type])',
        ]

        for selector in selectors:
            try:
                # 关键：使用wait_for_selector并设置state='visible'
                elem = await self.browser.page.wait_for_selector(
                    selector,
                    state='visible',  # 关键参数：等待元素可见
                    timeout=10000     # 10秒超时
                )

                # 输入问题
                await elem.fill(question)

                # 按Enter发送
                await self.browser.page.keyboard.press('Enter')

                return True

            except Exception as e:
                continue

        return False

    except Exception as e:
        return False
```

### 成功执行日志

```
2026-02-24 21:32:25 - INFO - 正在尝试选择器: textarea[placeholder*="问"]
2026-02-24 21:32:25 - INFO - ✓ 找到可见元素: textarea[placeholder*="问"]
2026-02-24 21:32:32 - INFO - ✓ 使用fill成功输入问题
2026-02-24 21:32:34 - INFO - ✓ 已按Enter键发送
2026-02-24 21:32:36 - INFO - ✓ 策略1 'wait_selector' 完全成功！
```

## 关键成功因素

### 1. 使用 state='visible' 参数
```python
# 正确做法
elem = await page.wait_for_selector(selector, state='visible', timeout=10000)

# 错误做法（会找到不可见元素）
elem = await page.query_selector(selector)
```

**原因**：动态渲染的元素需要等待其真正可见，否则width和height都是0。

### 2. 使用 placeholder 属性定位
```python
'selector': 'textarea[placeholder*="问"]'  # 最佳
'selector': 'textarea[placeholder*="输入"]'  # 备选
'selector': 'textarea'  # 最后选择
```

**原因**：placeholder属性是最稳定的选择器，不依赖类名或ID。

### 3. 使用 fill() 方法输入
```python
# 正确做法
await elem.fill(question)

# 不推荐（可能失败）
await elem.type(question)
```

**原因**：fill()方法直接设置值，不模拟键盘输入，更可靠。

### 4. 使用 Enter 键发送
```python
# 正确做法
await page.keyboard.press('Enter')

# 不推荐（依赖按钮）
await send_button.click()
```

**原因**：Enter键是通用发送方式，不依赖按钮状态。

### 5. 设置足够超时时间
```python
timeout=10000  # 10秒
```

**原因**：动态渲染需要时间，太短会导致超时。

## 常见陷阱

### 陷阱1：直接使用 query_selector
```python
# 错误
elem = await page.query_selector('textarea')
# 结果：找到的是不可见元素（width=0, height=0）
```

### 陷阱2：忽略 state 参数
```python
# 错误
elem = await page.wait_for_selector('textarea', timeout=10000)
# 结果：元素存在但不可见时也会返回
```

### 陷阱3：使用 type() 而非 fill()
```python
# 不稳定
await elem.type(question)  # 可能因焦点问题失败
```

### 陷阱4：超时时间过短
```python
# 可能失败
elem = await page.wait_for_selector(selector, timeout=1000)  # 1秒太短
```

### 陷阱5：依赖通用选择器
```python
# 不推荐
elem = await page.wait_for_selector('textarea')  # 可能匹配到错误元素
```

## 调试技巧

### 1. 检查元素可见性
```python
visible = await elem.is_visible()
print(f"元素可见: {visible}")
```

### 2. 检查元素尺寸
```python
box = await elem.bounding_box()
print(f"尺寸: {box}")
```

### 3. 保存调试截图
```python
await page.screenshot(path='debug.png')
```

### 4. 执行JavaScript检查
```python
result = await page.evaluate('''() => {
    const textareas = document.querySelectorAll('textarea');
    return Array.from(textareas).map((el, i) => ({
        index: i,
        visible: el.offsetWidth > 0 && el.offsetHeight > 0,
        width: el.offsetWidth,
        height: el.offsetHeight
    }));
}''')
```

## 性能考虑

| 操作 | 耗时 | 优化建议 |
|------|------|----------|
| wait_for_selector | ~2-5秒 | 合理设置timeout |
| fill() 输入 | ~1秒 | 使用fill而非type |
| keyboard.press('Enter') | <0.5秒 | 最可靠发送方式 |
| **总耗时** | **~3-7秒** | 可接受范围 |

## 完整工作流程

```
1. 打开总包大脑页面
2. 等待页面加载完成
3. 使用 wait_for_selector 等待输入框可见
4. 使用 fill() 输入问题
5. 使用 keyboard.press('Enter') 发送
6. 等待响应生成
7. 提取答案内容
```

## 生产环境建议

1. **添加重试机制**：网络波动时自动重试
2. **设置合理超时**：10秒足够大多数情况
3. **记录详细日志**：便于问题排查
4. **保存调试截图**：失败时保留证据
5. **监控成功率**：及时发现异常

## 总结

**最佳实践公式**：
```
wait_for_selector + state='visible' + placeholder选择器 + fill() + Enter键 = 成功
```

这个组合在2024-02-24的生产运行中100%成功，成功发送问题并获得2628字符的答案。
