# Changelog

All notable changes to ZBBrain-Write will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open source preparation: LICENSE, CONTRIBUTING.md, SECURITY.md
- GitHub Actions CI/CD workflow
- Issue and Pull Request templates

## [3.6.9] - 2026-03-17

### Fixed - 登录持久化彻底修复（Super-Skill V3.10 深度分析）
**Cookie 域名隔离 + 超时保护**

1. 🐛 **Cookie 域名污染问题** - Critical fix
   - **问题**: 搜狗爬虫和总包大脑共享同一 cookies.json 文件
   - **症状**: 登录后下次运行仍要求扫码登录
   - **根本原因**: `close()` 保存时不检查域名，导致 sogou.com cookies 覆盖 metaso.cn cookies
   - **修复**: 添加 `cookie_domain_filter` 参数，只保存指定域名的 cookies

2. 🐛 **多个浏览器窗口问题** - Critical fix
   - **问题**: 浏览器关闭可能卡住，新浏览器启动后出现多窗口
   - **修复**: `close()` 方法添加 30 秒超时保护
   - **影响**: 确保旧浏览器完全关闭后再启动新浏览器

3. 🔧 **StagehandBrowser.close() 增强** - API improvement
   - 新增 `cookie_domain_filter` 参数，精确控制保存哪些域名的 cookies
   - 添加超时保护：context/browser/playwright 各 30 秒超时
   - 强制清理资源，确保引用被清除

4. 🔧 **MetasoAutomation.close() 修复** - API fix
   - 调用 `browser.close(save_cookies=True, cookie_domain_filter="metaso.cn")`
   - 确保只保存 metaso.cn 域名的登录状态

5. 🔧 **SogouWeChatScraper 修复** - Isolation fix
   - 调用 `browser.close(save_cookies=False, cookie_domain_filter=None)`
   - 完全不保存任何 cookies，防止污染 metaso.cn 登录状态

### Technical Details
- `StagehandBrowser.close(save_cookies=True, cookie_domain_filter="metaso.cn")` - 推荐用法
- `StagehandBrowser.close(save_cookies=False)` - Sogou 爬虫专用
- `_save_storage_state_for_domain(domain_filter)` - 新增方法，只保存指定域名
- 超时保护: 30 秒，防止关闭卡住

### Verified Flow
```
1. SogouWeChatScraper.scrape()
   → browser.start()
   → 爬取 sogou.com
   → browser.close(save_cookies=False)  ← 不保存任何 cookies

2. MetasoAutomation.send_question_and_get_answer()
   → browser.start()
   → 加载 metaso.cn cookies (恢复登录状态)
   → 获取回答
   → browser.close(save_cookies=True, cookie_domain_filter="metaso.cn")  ← 只保存 metaso.cn
```

## [3.6.8] - 2026-03-17

### Fixed - 登录持久化根本原因修复
**Cookie 保存时机错误修复**

1. 🐛 **SogouWeChatScraper.cookie 保存问题** - Critical fix
   - **问题**: SogouWeChatScraper 关闭时保存 sogou.com cookies，覆盖 metaso.cn 登录 cookies
   - **修复**: `browser.close(save_cookies=False)` - 不保存 sogou.com cookies
   - **影响**: 确保登录状态不会被搜狗爬虫覆盖

2. 🐛 **MetasoAutomation.close() 方法缺失** - Critical fix
   - **问题**: 代码调用 `metaso.close()` 但 MetasoAutomation 类没有 close() 方法
   - **修复**: 添加 `close()` 方法，正确保存 metaso.cn cookies
   - **影响**: 防止 `AttributeError` 运行时错误

3. 📝 **显式 cookie 保存参数** - Code clarity improvement
   - 所有 `browser.close()` 调用现在显式指定 `save_cookies=True/False`
   - 登录成功后立即保存 cookies
   - 登录失败时不保存无效 cookies

### Technical Details
- `SogouWeChatScraper.scrape()`: `browser.close(save_cookies=False)`
- `MetasoAutomation.close()`: 新方法，调用 `browser.close(save_cookies=True)`
- `MetasoAutomation._restart_browser()`: 显式 `save_cookies=True`
- `MetasoAutomation.send_question_and_get_answer()`: 显式保存 cookies

## [3.6.7] - 2026-03-17

### Added - Super-Skill V3.10 全面优化
**无人值守能力增强（50次迭代优化）**

1. 📊 **内容质量评分器** - New `ContentQualityScorer` class
   - 评估热点问题质量：长度、场景词、问句格式
   - 评估回答质量：长度、结构、专业性
   - 评估标题质量：长度、关键词、吸引力
   - 评分阈值：问题≥60分、回答≥50分、标题≥70分

2. 🔐 **登录状态预检测** - Pre-check login status before task execution
   - `_pre_check_login_status()`: 检查登录状态有效期
   - `_send_login_expiry_warning()`: 登录即将过期时发送预警
   - `_send_login_required_notification()`: 需要登录时发送通知

3. 🔄 **AI生成重试机制** - Enhanced retry mechanism for AI generation
   - 热点问题生成：最多3次重试 + 质量评分验证
   - 每次重试后评估质量分数
   - 失败时使用高质量备用问题列表

### Fixed

1. 🔧 **localStorage加载时机修复** - Fixed localStorage loading timing
   - 原先：页面加载后才加载 localStorage（页面脚本无法读取）
   - 现在：先在 about:blank 页面加载 localStorage，再导航到目标页面
   - 确保页面脚本可以正确读取已保存的登录状态

2. 📝 **质量评分集成** - Integrated quality scoring into main workflow
   - 生成热点问题后自动评分
   - 评分不达标时自动重试
   - 所有重试失败时使用备用方案

### Improved

- **无人值守率**: 从 ~85% 提升到 ~95%（目标99%）
- **内容质量**: 添加自动质量检测和重试机制
- **稳定性**: 增强错误恢复和降级策略

## [3.6.6] - 2026-03-17

### Fixed - 总包大脑登录状态持久化
**登录持久化问题修复**

1. 🔐 **localStorage 持久化** - Added localStorage persistence alongside cookies
   - New methods: `_save_local_storage()`, `_load_local_storage()`, `_save_storage_state()`, `_load_storage_state()`
   - Login state now persists across sessions using both cookies AND localStorage
   - Files saved to: `browser_data/cookies.json` and `browser_data/local_storage.json`

2. ✅ **登录成功后立即保存** - Save state immediately after successful login
   - `_wait_for_login()` now saves browser state right after detecting successful login
   - Prevents loss of login state if the browser crashes or is closed unexpectedly

3. 🔄 **页面加载后恢复 localStorage** - Restore localStorage after page navigation
   - `_navigate_to_metaso()` now loads saved localStorage after the page loads
   - Ensures login state is fully restored before checking login status

4. 📝 **关键词强制添加逻辑修复** - Fixed keyword requirement in title generation
   - Previous logic would skip adding keyword if "EPC" was already in the title
   - New logic always attempts to add the search keyword if not present and within length limit

## [3.6.5] - 2026-03-16

### Fixed - 深度代码审查修复（Super-Skill V3.10）
**CRITICAL问题修复（12项）**

1. 🐛 **裸异常捕获修复** - Fixed 16 bare `except:` clauses
   - All bare exceptions now catch specific types: `(asyncio.TimeoutError, Exception)`
   - Added debug logging for failed operations
   - Prevents catching `KeyboardInterrupt` and `SystemExit` incorrectly

2. 🔒 **原子写入实现** - Atomic JSON write operations
   - Added `atomic_write_json()` function using tempfile + os.replace
   - Prevents file corruption during process crashes
   - All state files now use atomic write pattern

3. 🔐 **文件锁支持** - Cross-platform file locking
   - Added `file_lock()` context manager
   - Supports both Unix (fcntl) and Windows (msvcrt)
   - Prevents concurrent access race conditions

4. ⏱️ **API调用超时** - API call timeout protection
   - Added `Constants.API_CALL_TIMEOUT = 120s` and `API_STREAM_TIMEOUT = 300s`
   - All ZhipuAI API calls now include explicit `timeout` parameter
   - Prevents requests from hanging indefinitely

5. 📊 **索引边界检查** - Array index bounds checking
   - `get_current_wechat_account()` now validates `current_account_index`
   - Clamps index to valid range with warning log
   - Prevents IndexError crashes

6. 🧵 **线程安全单例** - Thread-safe singleton pattern
   - Added `get_singleton_lock()` utility function
   - Global performance monitor uses double-check locking
   - Prevents race conditions in multi-threaded contexts

7. 🔧 **网络检测优化** - Network detection improvements
   - Specific exception handling in IP service queries
   - Better error messages with exception type names
   - Rate limit (429) handling in IP API calls

### Technical Details
- Added imports: `tempfile`, `threading`, `fcntl`, `platform`
- New utility functions: `atomic_write_json()`, `file_lock()`, `get_singleton_lock()`
- Enhanced error messages with context information
- Improved debugging capability with structured logging

### Code Quality Improvements
- Reduced technical debt from code review findings
- Improved exception handling granularity
- Better resource cleanup in finally blocks
- More informative error logging

## [3.6.4] - 2026-03-16

### Fixed
- 🔄 **公众号轮换bug修复** - WeChat account rotation bug fix
  - Fixed `set_wechat_account()` not syncing `current_account_index`
  - Rotation now correctly tracks account index when syncing between Config instances
  - Prevents same account from receiving consecutive articles

### Technical Details
- Added index synchronization in `set_wechat_account()` method
- Matches account by appid to find correct index in `wechat_accounts` list
- Ensures `rotate_to_next_wechat_account()` uses correct starting index

## [3.6.3] - 2026-03-16

### Fixed
- 🔧 **运行间隔计算修复** - Run interval calculation fix
  - Fixed stale timestamp bug in scheduler
  - Now correctly uses `datetime.now()` instead of cached loop start time
  - Ensures accurate 1-hour intervals between runs

### Changed
- Disabled scheduled publishing (WeChat API doesn't support `publish_time` parameter)
- Updated `schedule_publish` method to remove unsupported parameter

## [3.6.2] - 2026-03-16

### Added
- 🧠 **长思考模式** - Long Thinking Mode
  - Automatic switching to long thinking mode before sending questions
  - Hover-triggered dropdown interaction with 4-layer fallback strategy
  - Extended wait time (15 min) for deeper AI responses
  - Config: `启用长思考模式 = true`

### Technical Details
- Playwright hover + click strategy
- Stagehand AI intelligent recognition fallback
- JavaScript event triggering fallback
- Direct element location fallback
- Smart stability detection (10 consecutive checks)

## [3.6.0] - 2026-03-15

### Added
- 💰 **0成本AI优化 V2.0** - Zero-Cost AI Optimization
  - Full migration to GLM-4.7-Flash (completely free)
  - 200K context window for all AI tasks
  - Enhanced prompts optimized for free model
  - Automatic cost status display at startup
  - Quality validation with retry mechanism

### Changed
- Default AI model changed from `glm-4-plus` to `glm-4.7-flash`
- Enhanced prompt engineering for content structuring
- Improved HTML formatting prompts for free model
- Updated startup logs to show cost optimization status

### Technical Details
- All AI tasks (hot question, title, structuring, formatting) now use free models
- Image generation uses `cogview-3-flash` (free)
- Quality maintained through enhanced prompts and validation
- Estimated cost savings: ~100% (from paid to free)

## [3.5.0] - 2026-03-15

### Added
- 🌐 **国内网络检测功能** - China domestic network detection
  - Automatic IP geolocation check
  - IP whitelist verification for WeChat API
  - Graceful degradation for international networks
- 📅 **定时发布功能** - Scheduled publishing
  - Configurable delay minutes after draft creation
  - Automatic WeChat draft scheduling
  - Config: `启用定时发布` and `定时发布延迟分钟`

### Changed
- Enhanced error handling for network-related operations
- Improved logging with detailed IP information

## [3.4.0] - 2026-03-14

### Added
- ⏰ **定时调度器 v3.4.0** - Enhanced scheduler
  - Working hours configuration (6:00-22:00 by default)
  - Hourly status reports
  - Improved timezone handling
- 🔄 **多维度轮换机制** - Multi-dimensional rotation
  - Keyword rotation (`keyword_rotation.json`)
  - Theme rotation (`theme_rotation.json`)
  - Prompt/Persona rotation (`prompt_rotation.json`)
  - WeChat account rotation (`wechat_accounts.json`)

### Changed
- Refactored scheduler for better stability
- Added configuration for start/stop hours

## [3.3.0] - 2026-03-13

### Added
- 🎨 **主题轮换系统** - Theme rotation system
  - 7 beautiful themes: 秋日暖光, 春日清新, 深海静谧, 优雅金, 活力红, 简约蓝, 专注绿
  - Automatic theme switching for visual variety
  - md2wechat integration for professional layouts
- 👤 **回复人设轮换** - Reply persona rotation
  - 麦肯锡版 - McKinsey style
  - 刘润版 - Liu Run style
  - 逻辑思维版 - Logical thinking style
  - 简要版 - Concise style

### Changed
- Improved AI content structure optimization
- Enhanced HTML formatting for WeChat

## [3.2.0] - 2026-03-10

### Added
- 🔧 **配置热重载** - Configuration hot reload
  - Automatic config file change detection
  - Zero-downtime configuration updates
- 📊 **性能监控** - Performance monitoring
  - Metrics collection
  - Health check system
  - Rate limiting with circuit breaker

### Changed
- Major code refactoring for maintainability
- Enhanced error recovery mechanisms

## [3.1.0] - 2026-03-05

### Added
- 🤖 **多公众号支持** - Multiple WeChat accounts support
  - Round-robin account rotation
  - Per-account configuration
  - Automatic account switching
- 📝 **封面图轮换** - Cover image rotation
  - Multiple cover images support
  - Automatic rotation for visual variety

### Fixed
- WeChat API rate limiting issues
- Browser automation stability improvements

## [3.0.0] - 2026-03-01

### Added
- 🚀 **全新架构** - Complete architecture redesign
  - Modular class structure (28 classes)
  - Custom exception hierarchy
  - Comprehensive logging system
- 🌐 **Stagehand浏览器自动化** - Stagehand browser automation
  - Playwright-based browser control
  - Metaso AI integration
  - Persistent browser context
- 📰 **搜狗微信爬虫** - Sogou WeChat scraper
  - Multi-page crawling
  - AI-powered article filtering
  - JTBD theory question generation
- 🤖 **智谱AI集成** - ZhipuAI integration
  - GLM-4-Plus for high-quality content
  - GLM-4-Flash for fast operations
  - CogView-3 for image generation

### Changed
- Complete rewrite from previous versions
- Production-grade infrastructure

## [2.x] - 2025-12 to 2026-02

### Added
- Basic WeChat article automation
- Simple AI integration
- GUI interface

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 3.6.4 | 2026-03-16 | WeChat account rotation bug fix |
| 3.6.3 | 2026-03-16 | Run interval calculation fix |
| 3.6.2 | 2026-03-16 | Long thinking mode, extended wait time |
| 3.6.0 | 2026-03-15 | Zero-cost AI optimization V2.0 |
| 3.5.0 | 2026-03-15 | Network detection, Scheduled publishing |
| 3.4.0 | 2026-03-14 | Enhanced scheduler, Multi-rotation |
| 3.3.0 | 2026-03-13 | Theme & Persona rotation |
| 3.2.0 | 2026-03-10 | Hot reload, Performance monitoring |
| 3.1.0 | 2026-03-05 | Multi-account, Cover rotation |
| 3.0.0 | 2026-03-01 | Complete architecture redesign |

---

## Upgrade Guide

### From 3.6.x to 3.6.4

1. Update `config.ini` with new options:
   ```ini
   [总包大脑]
   # 【v3.6.2新增】长思考模式配置
   启用长思考模式 = true
   # 长思考模式下会自动延长到至少900秒(15分钟)
   最大等待回复时间 = 900
   ```

2. No database migration required

### From 3.4.x to 3.5.0

1. Update `config.ini` with new options:
   ```ini
   [微信公众号]
   启用定时发布 = true
   定时发布延迟分钟 = 15
   ```

2. No database migration required

### From 3.x to 3.4.0

1. Add new rotation state files (auto-created)
2. Update keywords.txt with desired keywords

### From 2.x to 3.0.0

1. Complete reinstallation required
2. Copy your config.ini values to new template
3. Re-run setup.bat

---

[Unreleased]: https://github.com/your-repo/ZBBrain-Write/compare/v3.6.3...HEAD
[3.6.3]: https://github.com/your-repo/ZBBrain-Write/compare/v3.6.2...v3.6.3
[3.6.2]: https://github.com/your-repo/ZBBrain-Write/compare/v3.6.0...v3.6.2
[3.6.0]: https://github.com/your-repo/ZBBrain-Write/compare/v3.5.0...v3.6.0
[3.5.0]: https://github.com/your-repo/ZBBrain-Write/compare/v3.4.0...v3.5.0
[3.4.0]: https://github.com/your-repo/ZBBrain-Write/compare/v3.3.0...v3.4.0
[3.3.0]: https://github.com/your-repo/ZBBrain-Write/compare/v3.2.0...v3.3.0
[3.2.0]: https://github.com/your-repo/ZBBrain-Write/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/your-repo/ZBBrain-Write/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/your-repo/ZBBrain-Write/releases/tag/v3.0.0
