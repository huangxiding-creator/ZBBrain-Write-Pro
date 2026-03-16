# Changelog

All notable changes to ZBBrain-Write will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Open source preparation: LICENSE, CONTRIBUTING.md, SECURITY.md
- GitHub Actions CI/CD workflow
- Issue and Pull Request templates

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

### From 3.6.x to 3.6.3

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
