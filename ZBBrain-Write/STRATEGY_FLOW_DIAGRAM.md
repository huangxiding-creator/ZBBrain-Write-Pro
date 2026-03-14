# 总包大脑输入框检测策略流程图

## 主流程

```
开始: _send_question_fallback(question)
│
├─ 准备工作
│  ├─ 创建 debug_dir
│  └─ 初始化策略计数器
│
├─▼ 策略1: wait_for_selector
│  ├─ 等待页面稳定
│  ├─ 尝试标准选择器列表
│  │  ├─ textarea[placeholder*="问"]
│  │  ├─ textarea[placeholder*="输入"]
│  │  ├─ div[contenteditable="true"]:visible
│  │  ├─ textarea:not([style*="display: none"])
│  │  └─ ... (共12个选择器)
│  ├─ 对每个选择器:
│  │  ├─ wait_for_selector(state='visible', timeout=10s)
│  │  ├─ 如果找到 → _input_and_send()
│  │  └─ 如果成功 → ✓ 返回 True
│  └─ 如果全部失败 → 继续策略2
│
├─▼ 策略2: Playwright Locator
│  ├─ 强制滚动到底部
│  ├─ 尝试 Locator 策略列表
│  │  ├─ get_by_text("问").locator('..')
│  │  ├─ get_by_placeholder("问")
│  │  ├─ get_by_role("textbox")
│  │  ├─ locator('textarea').filter(is_visible=True)
│  │  └─ ... (共8个策略)
│  ├─ 对每个策略:
│  │  ├─ 等待 locator.count() > 0
│  │  ├─ 检查 is_visible()
│  │  ├─ 如果找到 → _input_and_send()
│  │  └─ 如果成功 → ✓ 返回 True
│  └─ 如果全部失败 → 继续策略3
│
├─▼ 策略3: IntersectionObserver
│  ├─ 强制滚动到底部
│  ├─ 注入 JavaScript: IntersectionObserver
│  │  ├─ 监听所有输入元素
│  │  ├─ 检测元素进入视口
│  │  ├─ 验证元素真正可见
│  │  └─ 超时: 15秒
│  ├─ 如果找到元素:
│  │  ├─ 解析元素信息
│  │  ├─ 获取元素引用
│  │  ├─ _input_and_send()
│  │  └─ 如果成功 → ✓ 返回 True
│  └─ 如果失败 → 继续策略4
│
├─▼ 策略4: JavaScript 智能搜索
│  ├─ 保存截图 (strategy4_before.png)
│  ├─ 循环 3 次:
│  │  ├─ 强制滚动到底部 (多种方式)
│  │  ├─ 等待 2 秒
│  │  ├─ JavaScript 智能查找:
│  │  │  ├─ 遍历所有输入元素
│  │  │  ├─ 计算可见性得分
│  │  │  ├─ 评分公式: score = positionScore + widthScore
│  │  │  │  └─ positionScore = rect.top + scrollY
│  │  │  │  └─ widthScore = rect.width * 2
│  │  │  └─ 返回最高分元素
│  │  ├─ 如果找到:
│  │  │  ├─ 记录元素信息
│  │  │  ├─ 获取元素引用
│  │  │  ├─ _input_and_send()
│  │  │  └─ 如果成功 → ✓ 返回 True
│  │  └─ 如果失败 → 继续下一次循环
│  └─ 如果 3 次都失败 → 继续策略5
│
├─▼ 策略5: 最后 Fallback
│  ├─ 强制滚动到底部
│  ├─ 获取所有输入元素信息:
│  │  ├─ 所有 textarea
│  │  ├─ 所有 contenteditable
│  │  └─ 所有 text input
│  ├─ 按宽度排序 (降序)
│  ├─ 尝试前 10 个元素:
│  │  ├─ 滚动到元素
│  │  ├─ 尝试点击
│  │  ├─ _input_and_send()
│  │  └─ 如果成功 → ✓ 返回 True
│  └─ 如果全部失败 → 返回 False
│
└─▼ 所有策略失败
   ├─ 记录错误日志
   └─ 抛出异常: "无法找到或操作输入框"
```

## _input_and_send 子流程

```
_input_and_send(element, question, debug_dir, strategy_name)
│
├─ 滚动到元素
│  ├─ scroll_into_view_if_needed(timeout=5s)
│  └─ 等待 0.5s
│
├─ 点击元素
│  ├─ click(timeout=5s)
│  └─ 等待 0.5s
│
├─ 清空现有内容
│  ├─ Control+A (全选)
│  ├─ Backspace (删除)
│  └─ 等待 0.2s
│
├─ 尝试输入方式 (按顺序)
│  │
│  ├─ 方式1: fill()
│  │  ├─ element.fill(question, timeout=5s)
│  │  ├─ 验证输入成功
│  │  └─ 如果成功 → input_success = True
│  │
│  ├─ 方式2: type() (如果方式1失败)
│  │  ├─ element.type(question, delay=20, timeout=5s)
│  │  └─ 如果成功 → input_success = True
│  │
│  └─ 方式3: JavaScript (如果方式2失败)
│     ├─ 根据tagName选择设置方式
│     │  ├─ TEXTAREA/INPUT → el.value = question
│     │  └─ DIV → el.textContent = question
│     ├─ 触发事件: input, change
│     └─ 如果成功 → input_success = True
│
├─ 验证输入
│  ├─ 如果 input_success = True
│  │  ├─ 保存截图 (after_input_{strategy_name}.png)
│  │  ├─ 等待 1s
│  │  └─ 继续
│  └─ 如果 input_success = False
│     └─ 返回 False
│
├─ 尝试发送
│  └─ _try_send_button()
│     │
│     ├─ 方式1: 选择器查找
│     │  ├─ button:has-text("发送")
│     │  ├─ button:has-text("提交")
│     │  ├─ button:has-text("Send")
│     │  └─ 如果找到 → 点击 → 返回 True
│     │
│     ├─ 方式2: JavaScript 查找
│     │  ├─ 遍历所有按钮
│     │  ├─ 检查文本/aria-label/class
│     │  └─ 如果找到 → 点击 → 返回 True
│     │
│     └─ 方式3: Enter 键
│        └─ keyboard.press('Enter') → 返回 True
│
└─ 返回结果
   ├─ True: 输入和发送都成功
   └─ False: 任一步骤失败
```

## _scroll_to_bottom_forcefully 子流程

```
_scroll_to_bottom_forcefully()
│
├─ 方式1: window.scrollTo(body.scrollHeight)
├─ 方式2: window.scrollTo(element.scrollHeight)
├─ 方式3: body.scrollTop = scrollHeight
├─ 方式4: element.scrollTop = scrollHeight
└─ 方式5: scrollTo with behavior: "instant"
│
└─ 每次间隔 0.2s
```

## 数据流

```
用户输入 (question)
│
├─▼ _send_question_fallback
│  │
│  ├─▼ 策略1
│  │  └─ 元素引用 → _input_and_send → 结果
│  │
│  ├─▼ 策略2 (如果策略1失败)
│  │  └─ 元素引用 → _input_and_send → 结果
│  │
│  ├─▼ 策略3 (如果策略2失败)
│  │  └─ 元素引用 → _input_and_send → 结果
│  │
│  ├─▼ 策略4 (如果策略3失败)
│  │  └─ 元素引用 → _input_and_send → 结果
│  │
│  └─▼ 策略5 (如果策略4失败)
│     └─ 元素引用 → _input_and_send → 结果
│
└─▼ 最终结果
   ├─ True: 成功发送问题
   └─ False: 所有策略失败
```

## 时间复杂度

| 策略 | 最佳情况 | 最坏情况 |
|------|----------|----------|
| 策略1 | 1-2秒 | 10秒 (12个选择器 × 超时) |
| 策略2 | 1-2秒 | 5秒 (8个locator) |
| 策略3 | 1-5秒 | 15秒 (等待观察) |
| 策略4 | 2-3秒 | 9秒 (3次 × (2s等待+1s处理)) |
| 策略5 | 2-3秒 | 10秒 (10个元素 × 1s) |
| **总计** | **1-2秒** | **~49秒** |

## 空间复杂度

- 日志文件: 每次执行约 5-10KB
- 截图文件: 每次执行约 500KB - 2MB (取决于页面大小)
- 临时变量: 最小 (O(1))

## 成功率预估

| 场景 | 策略1 | 策略2 | 策略3 | 策略4 | 策略5 | 总计 |
|------|-------|-------|-------|-------|-------|------|
| 标准渲染 | 95% | - | - | - | - | 95% |
| 延迟加载 | - | 80% | - | - | - | 80% |
| 动态显示 | - | - | 85% | - | - | 85% |
| 滚动触发 | - | - | - | 90% | - | 90% |
| 复杂情况 | - | - | - | - | 70% | 70% |
| **总体** | **-** | **-** | **-** | **-** | **-** | **~95%** |

---

修复日期: 2026-02-24
版本: 1.0
状态: 已完成
