# 广告图插入修复验证报告

## 修复日期
2026-02-25 16:27

## 问题描述
从实际运行情况看，广告图没有成功插入到文章顶部和底部。

## 根本原因分析（使用Super-Skill分析）

### 1. AI转换时的占位符问题
- **问题**：智谱AI转换时将所有图片转换为占位符 `<!-- IMG:index -->`
- **影响**：占位符没有被替换回实际的图片HTML标签
- **位置**：`_convert_with_zhipu_ai` 方法（6891行）

### 2. 占位符格式不匹配
- **问题**：提示词中定义为 `<!-- IMG:index -->`，但代码中查找 `<!-- IMG:0 -->`、`<!-- IMG:1 -->`
- **影响**：替换逻辑无法找到匹配的占位符
- **位置**：提示词定义（6946行）vs 替换逻辑（6991行）

### 3. 缺少图片处理辅助方法
- **问题**：`MarkdownToWeChat` 类没有 `_image_to_base64` 方法
- **影响**：无法将本地图片转换为base64嵌入HTML
- **位置**：`_process_image_for_html` 调用缺失依赖

## 修复方案

### 修复1：添加图片提取逻辑
**文件**：`ZBBrainArticle.py`
**位置**：6891行，`_convert_with_zhipu_ai` 方法

```python
# 提取所有图片引用（在AI转换前保存）
import re
image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
images = re.findall(image_pattern, md_content)
self.logger.info(f"从Markdown中提取到 {len(images)} 个图片引用")

# 构建图片路径列表（按出现顺序）
image_paths = [img_path for alt_text, img_path in images]
```

### 修复2：添加图片占位符替换逻辑
**文件**：`ZBBrainArticle.py`
**位置**：6985-7001行

```python
# 替换图片占位符为实际的图片HTML标签
if image_paths:
    self.logger.info("开始替换图片占位符...")
    md_dir = os.path.dirname(md_file)

    for idx, img_path in enumerate(image_paths):
        placeholder = f"<!-- IMG:{idx} -->"
        if placeholder in html_content:
            # 处理图片路径
            img_html = self._process_image_for_html(img_path, md_dir)
            if img_html:
                html_content = html_content.replace(placeholder, img_html)
                self.logger.info(f"✓ 已替换图片占位符 {idx}: {img_path}")
```

### 修复3：添加图片处理辅助方法
**文件**：`ZBBrainArticle.py`
**位置**：7015-7066行

```python
def _process_image_for_html(self, img_path: str, md_dir: str) -> str:
    """处理图片并转换为HTML img标签"""
    try:
        from pathlib import Path
        img_path_obj = Path(img_path)

        # 如果是相对路径，基于markdown文件目录解析
        if not img_path_obj.is_absolute():
            full_path = Path(md_dir) / img_path
        else:
            full_path = img_path_obj

        # 检查文件是否存在
        if not full_path.exists():
            self.logger.warning(f"图片文件不存在: {full_path}")
            return ""

        # 转换为base64嵌入（确保在微信中能显示）
        base64_data = self._image_to_base64(str(full_path))
        if base64_data:
            # 返回带样式的HTML img标签
            return f'<div style="text-align: center; margin: 20px 0;"><img src="{base64_data}" alt="广告图" style="width: 100%; max-width: 900px; height: auto;"/></div>'
        else:
            return ""

    except Exception as e:
        self.logger.error(f"处理图片失败 ({img_path}): {str(e)}")
        return ""
```

### 修复4：添加base64转换方法
**文件**：`ZBBrainArticle.py`
**位置**：7068-7095行

```python
def _image_to_base64(self, image_path: str) -> str:
    """将图片转换为base64编码（用于嵌入HTML）"""
    try:
        import base64

        # 检查文件大小，限制在2MB以内（微信公众号限制）
        file_size = os.path.getsize(image_path)
        if file_size > 2 * 1024 * 1024:  # 2MB
            self.logger.warning(f"图片文件过大({file_size/1024/1024:.2f}MB)，无法转换为base64")
            return ""

        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')

        # 根据文件扩展名确定MIME类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'

        # 返回data URI格式
        self.logger.info(f"图片已转换为base64格式，大小: {len(base64_data)}字符")
        return f"data:{mime_type};base64,{base64_data}"

    except Exception as e:
        self.logger.error(f"图片转base64失败: {str(e)}")
        return ""
```

### 修复5：修改AI提示词
**文件**：`ZBBrainArticle.py`
**位置**：6946行

**修改前**：
```
4. 图片使用占位符：<!-- IMG:index -->
```

**修改后**：
```
4. 图片使用占位符格式：<!-- IMG:数字 -->，从0开始编号，例如第一张图片用<!-- IMG:0 -->，第二张用<!-- IMG:1 -->
```

## 验证结果

### 运行日志
```
2026-02-25 16:25:55 - INFO - 从Markdown中提取到 2 个图片引用
2026-02-25 16:27:16 - INFO - 开始替换图片占位符...
2026-02-25 16:27:16 - INFO - 图片已转换为base64格式，大小: 1111520字符
2026-02-25 16:27:16 - INFO - ✓ 已替换图片占位符 0: top-ad.jpg
2026-02-25 16:27:16 - INFO - 图片已转换为base64格式，大小: 347328字符
2026-02-25 16:27:16 - INFO - ✓ 已替换图片占位符 1: bottom-ad.jpg
```

### HTML文件验证
**文件**：`temp/article_1772007912.html`
**大小**：1,471,514 字节（1.4MB）

**顶部广告图**：
```html
<div style="text-align: center; margin: 20px 0;">
<img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..." alt="广告图" style="width: 100%; max-width: 900px; height: auto;"/>
</div>
```

**底部广告图**：
```html
<div style="text-align: center; margin: 20px 0;">
<img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..." alt="广告图" style="width: 100%; max-width: 900px; height: auto;"/>
</div>
```

**验证统计**：
- ✅ 图片引用提取：成功提取 2 个图片引用
- ✅ 顶部广告图：成功转换为 base64（1,111,520 字符）
- ✅ 底部广告图：成功转换为 base64（347,328 字符）
- ✅ HTML中图片数量：2 个 base64 编码的图片
- ✅ 微信草稿创建：成功（ad_count: 2）

## 对比分析

### 修复前
| 项目 | 状态 |
|------|------|
| 图片提取 | ❌ 未实现 |
| 占位符生成 | ✅ AI生成 `<!-- IMG:index -->` |
| 占位符替换 | ❌ 未实现 |
| base64转换 | ❌ 方法不存在 |
| HTML嵌入 | ❌ 占位符残留 |

### 修复后
| 项目 | 状态 |
|------|------|
| 图片提取 | ✅ 正则表达式提取 |
| 占位符生成 | ✅ AI生成 `<!-- IMG:0 -->`、`<!-- IMG:1 -->` |
| 占位符替换 | ✅ 完整替换逻辑 |
| base64转换 | ✅ 2MB以内支持 |
| HTML嵌入 | ✅ 完整img标签+样式 |

## 技术要点

### 1. 正则表达式图片提取
```python
image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
images = re.findall(image_pattern, md_content)
```
- 匹配Markdown图片语法 `![alt](path)`
- 提取alt文本和路径
- 保持出现顺序

### 2. Base64编码优势
- **兼容性**：微信公众号完美支持
- **自包含**：不依赖外部URL
- **无过期**：永久有效
- **无上传**：无需使用素材库API

### 3. 文件大小限制
- **限制**：2MB以内
- **原因**：微信公众号限制
- **处理**：超过限制时记录警告并跳过

### 4. 路径解析策略
- **相对路径**：基于Markdown文件目录解析
- **绝对路径**：直接使用
- **跨平台**：使用 `pathlib.Path` 处理

## 迭代次数
**实际迭代**：1次
**最大迭代**：20次
**效率**：通过Super-Skill的frontend-patterns分析，一次定位根本原因

## 结论
✅ **广告图插入功能已完全修复并验证成功**

所有修改已完成并通过测试：
1. ✅ 图片提取逻辑正常
2. ✅ 占位符格式统一
3. ✅ base64转换功能正常
4. ✅ HTML嵌入成功
5. ✅ 微信草稿创建成功（ad_count: 2）

广告图现在能够成功插入到微信公众号文章的顶部和底部，使用base64编码确保在微信中正常显示。
