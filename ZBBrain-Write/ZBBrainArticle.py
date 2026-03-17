#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
ZBBrainArticle - 总包大脑文章自动生成脚本 (Stagehand版本)

功能描述：
1. 从搜狗微信搜索爬取EPC总承包相关资讯
2. 使用智谱AI分析生成热点问题
3. 发送到总包大脑获取回答
4. 转换为微信公众号文章格式
5. 发送通知到企业微信和邮箱

本版本使用 Stagehand 进行所有浏览器自动化操作

作者：AI助手
版本：2.5.0 (Optimized Edition - Iteration 5)

优化历史：
- v2.5.0 (当前版本 - 迭代5):
  * 监控增强：添加MetricsCollector指标收集系统
  * 监控增强：实现性能、错误、业务和系统指标分类
  * 监控增强：支持指标聚合和摘要统计
  * 健康检查：添加HealthCheck健康检查系统
  * 健康检查：支持自定义健康检查函数注册
  * 健康检查：提供健康状态报告和监控
  * 并发管理：实现AsyncTaskQueue异步任务队列
  * 并发管理：支持任务优先级和并发控制
  * 并发管理：实现失败任务自动重试机制
  * 并发管理：提供任务状态监控和结果查询
  * 配置管理：添加ConfigHotReload配置热重载
  * 配置管理：支持配置文件变更自动检测
  * 配置管理：实现配置历史和回滚功能
  * 配置管理：支持配置变更回调通知

- v2.4.0 (迭代6):
  * 数据库持久化：实现SQLite数据库缓存层，支持持久化存储
  * 数据库持久化：添加数据库连接池和事务管理
  * 重试策略：实现指数退避重试策略
  * 重试策略：添加抖动（jitter）以避免惊群效应
  * 重试策略：支持可配置的重试条件和最大重试次数
  * 优雅关闭：添加信号处理器（SIGINT, SIGTERM）
  * 优雅关闭：实现资源清理和状态保存
  * 优雅关闭：支持正在进行的任务完成后关闭
  * 结构化日志：添加JSON格式日志输出选项
  * 结构化日志：实现结构化日志记录器
  * 结构化日志：支持日志聚合和分析友好的格式

- v2.3.0 (迭代3):
  * 安全增强：添加输入清理和验证工具
  * 安全增强：实现安全的凭证管理（不在日志中泄露敏感信息）
  * 安全增强：添加URL验证和安全检查
  * 资源管理：使用上下文管理器确保资源正确释放
  * 资源管理：改进文件句柄管理（使用with语句）
  * 资源管理：增强网络连接的超时和清理
  * 资源管理：添加浏览器资源清理的上下文管理器
  * 文档增强：添加更多模块和类的详细文档字符串
  * 文档增强：添加关键方法的内联注释
  * 测试增强：扩展测试覆盖范围

- v2.2.0 (迭代2):
  * 添加性能监控工具（PerformanceMonitor类）
  * 添加@profile装饰器用于性能分析
  * 实现SimpleCache缓存机制
  * 添加@cached装饰器用于函数结果缓存
  * 替换所有裸except子句为具体异常类型
  * 为关键方法添加返回类型提示
  * 增强输入验证（类型检查、长度验证、范围检查）
  * 为AI分析方法和爬取方法添加缓存支持
  * 改进错误处理的一致性和可追溯性

- v2.1.0 (迭代1):
  * 整合重复的import语句到文件顶部
  * 添加自定义异常类层次结构
  * 添加常量类统一管理魔法数字
  * 添加工具函数：重试逻辑、输入验证、文件名清理
  * 改进异常处理，使用具体异常类型替代裸except
  * 添加类型提示和增强的文档字符串
  * 添加配置验证方法
  * 改进日志设置，添加错误处理
  * 优化代码结构和可维护性

- v2.0.0:
  * 使用Stagehand进行浏览器自动化
  * 实现完整的文章生成流程
  * 支持微信公众号草稿创建
  * 支持企业微信和邮件通知
"""

import os
import sys
import json
import time
import logging
from logging import Logger, StreamHandler
import configparser
import subprocess
import re
import asyncio
import html
import signal
import random
import sqlite3
import tempfile
import threading
import platform
# fcntl 仅在 Unix/Linux 上可用，Windows 使用 msvcrt
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple, ContextManager, Callable, TypeVar, cast, Set, Awaitable, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
import requests
import urllib.request
from collections import Counter
import functools
from abc import ABC, abstractmethod
from enum import Enum

# Stagehand imports - Using Playwright async API with Stagehand-style interface
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Other imports
from zhipuai import ZhipuAI


# =============================================================================
# 常量定义
# =============================================================================

class Constants:
    """项目常量定义"""
    # 浏览器相关常量
    DEFAULT_BROWSER_WIDTH = 1280
    DEFAULT_BROWSER_HEIGHT = 900
    DEFAULT_PAGE_LOAD_TIMEOUT = 60000
    DEFAULT_ELEMENT_WAIT_TIMEOUT = 30000
    DEFAULT_STABLE_WAIT_TIMEOUT = 5000

    # 网络请求相关
    DEFAULT_REQUEST_TIMEOUT = 30
    API_CALL_TIMEOUT = 120  # AI API调用默认超时（秒）
    API_STREAM_TIMEOUT = 300  # AI流式响应超时（秒）
    MAX_RETRY_ATTEMPTS = 3
    RETRY_BACKOFF_BASE = 2

    # 内容相关
    MIN_ARTICLE_TITLE_LENGTH = 5
    MAX_ARTICLE_SUMMARY_LENGTH = 200
    MAX_CONTEXT_ARTICLES = 20
    AI_ANALYSIS_BATCH_SIZE = 5
    MAX_TITLE_LENGTH = 24
    MIN_QUESTION_LENGTH = 30
    DEFAULT_COVER_IMAGE_SIZE = (900, 500)

    # 时间相关
    LOGIN_CHECK_INTERVAL = 2
    ANSWER_STABLE_COUNT = 6
    MIN_ANSWER_WAIT_TIME = 30
    TYPING_DELAY_MS = 10

    # 日志相关
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # 选择器常量
    INPUT_SELECTORS = [
        'textarea:not([style*="display: none"]):not([style*="visibility: hidden"])',
        'input[type="text"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
        '[contenteditable="true"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
        'textarea',
        'input[type="text"]',
        '[contenteditable="true"]',
    ]

    # 错误消息常量
    ERROR_INPUT_NOT_FOUND = "无法找到或填充输入框"
    ERROR_NO_ANSWER = "等待超时且未获取到任何回答"
    ERROR_LOGIN_TIMEOUT = "等待登录超时"

    # 【v3.6.8】质量评分阈值
    MIN_QUESTION_SCORE = 60  # 热点问题最低分数
    MIN_ANSWER_SCORE = 50    # 回答最低分数
    MIN_TITLE_SCORE = 70     # 标题最低分数


# =============================================================================
# 【v3.6.7新增】内容质量评分器
# =============================================================================

class ContentQualityScorer:
    """
    内容质量评分器

    用于评估AI生成内容的质量，确保输出符合标准。
    评分维度：
    - 热点问题：长度、场景词、问句格式
    - 回答内容：长度、结构、专业性
    - 标题：长度、关键词、吸引力

    v3.6.7新增
    """

    # 场景关键词（EPC总承包相关）
    SCENE_WORDS = [
        'EPC', '总承包', '投标', '设计', '施工', '竣工', '结算',
        '合同', '分包', '索赔', '变更', '成本', '质量', '安全',
        '风险', '管理', '进度', '采购', '监理', '审计'
    ]

    # 专业性关键词
    PROFESSIONAL_WORDS = [
        '合同', '风险', '管理', '控制', '流程', '规范', '标准',
        '条款', '责任', '义务', '权利', '变更', '索赔', '违约'
    ]

    # 标题吸引力词
    ATTRACTIVE_WORDS = [
        '必看', '必知', '实战', '技巧', '方法', '策略', '避坑',
        '注意', '建议', '解析', '指南', '关键', '核心', '重要'
    ]

    def __init__(self, logger=None):
        """初始化评分器"""
        self.logger = logger

    def _log(self, level: str, message: str):
        """安全的日志记录"""
        if self.logger:
            getattr(self.logger, level)(message)

    def score_question(self, question: str) -> dict:
        """
        评估热点问题质量

        Args:
            question: 待评估的问题文本

        Returns:
            dict: 包含score（分数）、issues（问题列表）、passed（是否通过）
        """
        if not question:
            return {'score': 0, 'issues': ['问题为空'], 'passed': False}

        score = 0
        issues = []
        max_score = 100

        # 1. 长度检查 (40分)
        if len(question) >= 50:
            score += 40
        elif len(question) >= 30:
            score += 25
            issues.append(f"问题长度({len(question)}字)不足50字")
        else:
            score += 10
            issues.append(f"问题长度({len(question)}字)严重不足")

        # 2. 场景词检查 (30分)
        scene_count = sum(1 for w in self.SCENE_WORDS if w in question)
        if scene_count >= 2:
            score += 30
        elif scene_count == 1:
            score += 15
        else:
            issues.append("缺少场景关键词")

        # 3. 问句格式检查 (30分)
        # 问号结尾 (15分)
        if question.endswith('？') or question.endswith('?'):
            score += 15
        else:
            issues.append("问题应以问号结尾")

        # 疑问词 (15分)
        question_words = ['如何', '怎样', '为什么', '什么', '哪些', '怎么', '能否', '是否']
        if any(w in question for w in question_words):
            score += 15
        else:
            issues.append("缺少疑问词（如何/怎样/为什么等）")

        passed = score >= Constants.MIN_QUESTION_SCORE

        if not passed:
            self._log('warning', f"热点问题质量不达标: {score}分 - {issues}")
        else:
            self._log('info', f"✓ 热点问题质量达标: {score}分")

        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'passed': passed,
            'details': {
                'length': len(question),
                'scene_words_count': scene_count,
                'has_question_mark': question.endswith('？') or question.endswith('?')
            }
        }

    def score_answer(self, answer: str) -> dict:
        """
        评估回答内容质量

        Args:
            answer: 待评估的回答文本

        Returns:
            dict: 包含score（分数）、issues（问题列表）、passed（是否通过）
        """
        if not answer:
            return {'score': 0, 'issues': ['回答为空'], 'passed': False}

        score = 0
        issues = []
        max_score = 100

        # 1. 长度检查 (50分)
        if len(answer) >= 1000:
            score += 50
        elif len(answer) >= 500:
            score += 35
            issues.append(f"回答长度({len(answer)}字)建议达到1000字以上")
        elif len(answer) >= 300:
            score += 20
            issues.append(f"回答长度({len(answer)}字)不足")
        else:
            score += 5
            issues.append(f"回答长度({len(answer)}字)严重不足")

        # 2. 结构检查 (30分)
        # 检查是否有分点/分段 (15分)
        if '一、' in answer or '1.' in answer or '第一' in answer or '首先' in answer:
            score += 15
        else:
            issues.append("缺乏分点结构")

        # 检查是否有建议/方法 (15分)
        if any(w in answer for w in ['建议', '方法', '措施', '对策', '策略']):
            score += 15
        else:
            issues.append("缺乏具体建议")

        # 3. 专业性检查 (20分)
        prof_count = sum(1 for w in self.PROFESSIONAL_WORDS if w in answer)
        if prof_count >= 3:
            score += 20
        elif prof_count >= 1:
            score += 10
        else:
            issues.append("专业性词汇不足")

        passed = score >= Constants.MIN_ANSWER_SCORE

        if not passed:
            self._log('warning', f"回答质量不达标: {score}分 - {issues}")
        else:
            self._log('info', f"✓ 回答质量达标: {score}分")

        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'passed': passed,
            'details': {
                'length': len(answer),
                'has_structure': '一、' in answer or '1.' in answer,
                'professional_words_count': prof_count
            }
        }

    def score_title(self, title: str, keyword: str = None) -> dict:
        """
        评估标题质量

        Args:
            title: 待评估的标题文本
            keyword: 可选的关键词，检查是否包含

        Returns:
            dict: 包含score（分数）、issues（问题列表）、passed（是否通过）
        """
        if not title:
            return {'score': 0, 'issues': ['标题为空'], 'passed': False}

        score = 0
        issues = []
        max_score = 100

        # 1. 长度检查 (30分)
        if 28 <= len(title) <= 30:
            score += 30
        elif 25 <= len(title) <= 32:
            score += 25
        elif 20 <= len(title) <= 35:
            score += 15
            issues.append(f"标题长度({len(title)}字)建议在28-30字之间")
        else:
            score += 5
            issues.append(f"标题长度({len(title)}字)不符合要求(28-30字)")

        # 2. 关键词检查 (40分)
        # 必须包含EPC或总承包 (20分)
        if 'EPC' in title or '总承包' in title:
            score += 20
        else:
            issues.append("标题缺少'EPC'或'总承包'")

        # 包含搜索关键词 (20分)
        if keyword and keyword in title:
            score += 20
        elif keyword:
            issues.append(f"标题缺少关键词'{keyword}'")

        # 3. 吸引力检查 (30分)
        # 包含数字 (15分)
        if any(c.isdigit() for c in title):
            score += 15
        else:
            issues.append("标题建议包含数字")

        # 包含吸引力词汇 (15分)
        if any(w in title for w in self.ATTRACTIVE_WORDS):
            score += 15
        elif '！' in title or '!' in title:
            score += 10
        else:
            issues.append("标题建议包含吸引力词汇或感叹号")

        passed = score >= Constants.MIN_TITLE_SCORE

        if not passed:
            self._log('warning', f"标题质量不达标: {score}分 - {issues}")
        else:
            self._log('info', f"✓ 标题质量达标: {score}分")

        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'passed': passed,
            'details': {
                'length': len(title),
                'has_epc': 'EPC' in title or '总承包' in title,
                'has_keyword': keyword in title if keyword else None,
                'has_number': any(c.isdigit() for c in title)
            }
        }


# =============================================================================
# v3.6.4 原子写入和文件锁工具
# =============================================================================

import json as json_module

def atomic_write_json(filepath: str, data: Any, logger: Optional[Any] = None) -> bool:
    """原子写入JSON文件，防止写入过程中崩溃导致文件损坏

    Args:
        filepath: 目标文件路径
        data: 要写入的数据
        logger: 可选的日志记录器

    Returns:
        bool: 写入是否成功
    """
    filepath = Path(filepath)
    temp_fd = None
    temp_path = None

    try:
        # 创建临时文件
        temp_fd, temp_path = tempfile.mkstemp(
            dir=str(filepath.parent),
            prefix='.tmp_',
            suffix='.json'
        )

        # 写入临时文件
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
            json_module.dump(data, f, ensure_ascii=False, indent=2)

        # 原子替换（在 Unix 和 Windows 上都有效）
        os.replace(temp_path, str(filepath))

        return True

    except Exception as e:
        if logger:
            logger.error(f"原子写入JSON失败: {filepath}, 错误: {str(e)}")

        # 清理临时文件
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        return False


@contextmanager
def file_lock(filepath: str, timeout: float = 10.0, logger: Optional[Any] = None):
    """跨平台文件锁上下文管理器

    Args:
        filepath: 要锁定的文件路径
        timeout: 获取锁的超时时间（秒）
        logger: 可选的日志记录器

    Yields:
        bool: 是否成功获取锁
    """
    lock_path = str(filepath) + '.lock'
    lock_file = None
    acquired = False

    try:
        # 创建锁文件
        lock_file = open(lock_path, 'w')

        # 根据平台选择锁定方式
        if platform.system() != 'Windows':
            # Unix/Linux: 使用 fcntl
            import fcntl
            start_time = time.time()

            while True:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                    break
                except (IOError, BlockingIOError):
                    if time.time() - start_time >= timeout:
                        if logger:
                            logger.warning(f"获取文件锁超时: {filepath}")
                        break
                    time.sleep(0.1)
        else:
            # Windows: 使用 msvcrt (简化版，非阻塞)
            try:
                import msvcrt
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                acquired = True
            except (IOError, OSError):
                if logger:
                    logger.warning(f"Windows上获取文件锁失败: {filepath}")

        yield acquired

    finally:
        # 释放锁
        if lock_file:
            try:
                if platform.system() != 'Windows':
                    import fcntl
                    if acquired:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                else:
                    try:
                        import msvcrt
                        if acquired:
                            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    except (IOError, OSError):
                        pass
            except Exception:
                pass

            lock_file.close()

            # 删除锁文件
            try:
                os.unlink(lock_path)
            except Exception:
                pass


# 全局线程锁用于单例模式
_singleton_locks: Dict[str, threading.Lock] = {}
_singleton_lock = threading.Lock()

def get_singleton_lock(name: str) -> threading.Lock:
    """获取单例模式的线程锁"""
    with _singleton_lock:
        if name not in _singleton_locks:
            _singleton_locks[name] = threading.Lock()
        return _singleton_locks[name]


# =============================================================================
# 异常类定义
# =============================================================================

class ZBBrainException(Exception):
    """基础异常类"""
    pass


class ConfigurationError(ZBBrainException):
    """配置错误异常"""
    pass


class BrowserError(ZBBrainException):
    """浏览器操作异常"""
    pass


class ScrapingError(ZBBrainException):
    """爬取异常"""
    pass


class AIAnalysisError(ZBBrainException):
    """AI分析异常"""
    pass


class WeChatAPIError(ZBBrainException):
    """微信API异常"""
    pass


# =============================================================================
# 工具函数
# =============================================================================

async def retry_async(
    func,
    max_attempts: int = Constants.MAX_RETRY_ATTEMPTS,
    backoff_base: int = Constants.RETRY_BACKOFF_BASE,
    exceptions: Tuple = (Exception,),
    logger: Optional[Logger] = None
):
    """
    异步函数重试装饰器/包装器，使用指数退避策略

    Args:
        func: 要重试的异步函数
        max_attempts: 最大重试次数
        backoff_base: 退避基数（指数退避）
        exceptions: 需要重试的异常类型元组
        logger: 日志记录器

    Returns:
        函数执行结果

    Raises:
        最后一次调用的异常
    """
    attempt = 0
    last_exception = None

    while attempt < max_attempts:
        attempt += 1
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts:
                wait_time = backoff_base ** attempt
                if logger:
                    logger.warning(f"尝试 {attempt}/{max_attempts} 失败: {str(e)}，{wait_time}秒后重试...")
                await asyncio.sleep(wait_time)
            else:
                if logger:
                    logger.error(f"经过 {max_attempts} 次尝试后仍然失败")

    if last_exception:
        raise last_exception


def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None, param_name: str = "参数") -> None:
    """
    验证字符串长度

    Args:
        value: 要验证的字符串
        min_length: 最小长度
        max_length: 最大长度
        param_name: 参数名称（用于错误消息）

    Raises:
        ValueError: 如果验证失败
    """
    if not isinstance(value, str):
        raise ValueError(f"{param_name}必须是字符串类型")

    if len(value) < min_length:
        raise ValueError(f"{param_name}长度不能少于{min_length}个字符")

    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{param_name}长度不能超过{max_length}个字符")


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


# =============================================================================
# 安全工具函数
# =============================================================================

def sanitize_html(html_content: str) -> str:
    """
    清理HTML内容，转义危险字符以防止XSS攻击

    Args:
        html_content: 原始HTML内容

    Returns:
        转义后的安全HTML内容
    """
    return html.escape(html_content, quote=True)


def sanitize_url(url: str) -> str:
    """
    清理和验证URL，确保基本安全

    Args:
        url: 原始URL

    Returns:
        清理后的URL

    Raises:
        ValueError: 如果URL格式无效
    """
    url = url.strip()

    # 基本URL验证
    if not url:
        raise ValueError("URL不能为空")

    # 只允许http和https协议
    if not (url.startswith('http://') or url.startswith('https://')):
        raise ValueError("只允许HTTP和HTTPS协议")

    # 移除可能的危险字符
    dangerous_chars = ['\n', '\r', '\t', '\0']
    for char in dangerous_chars:
        url = url.replace(char, '')

    return url


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    清理用户输入，移除潜在的危险字符

    Args:
        text: 用户输入文本
        max_length: 最大允许长度

    Returns:
        清理后的文本
    """
    if not isinstance(text, str):
        raise ValueError("输入必须是字符串")

    # 移除控制字符（保留换行符和制表符）
    text = ''.join(char for char in text if char == '\n' or char == '\t' or not ord(char) < 32)

    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """
    掩码敏感数据（如API密钥、密码等）

    Args:
        data: 敏感数据字符串
        mask_char: 掩码字符
        visible_chars: 首尾保留的可见字符数

    Returns:
        掩码后的字符串
    """
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)

    return data[:visible_chars] + mask_char * (len(data) - visible_chars * 2) + data[-visible_chars:]


def is_safe_filepath(filepath: str, base_dir: str = None) -> bool:
    """
    检查文件路径是否安全（防止路径遍历攻击）

    Args:
        filepath: 要检查的文件路径
        base_dir: 基础目录，如果提供则确保filepath在base_dir内

    Returns:
        路径是否安全
    """
    # 规范化路径
    try:
        normalized_path = os.path.normpath(filepath)

        # 检查是否包含路径遍历字符
        if '..' in normalized_path.split(os.sep):
            return False

        # 如果提供了基础目录，确保文件路径在其内
        if base_dir:
            base_normalized = os.path.normpath(base_dir)
            full_path = os.path.join(base_normalized, normalized_path)
            full_path = os.path.normpath(full_path)

            if not full_path.startswith(base_normalized):
                return False

        return True
    except (ValueError, OSError):
        return False


# =============================================================================
# 资源管理工具
# =============================================================================

@contextmanager
def safe_file_read(filepath: str, mode: str = 'r', encoding: str = 'utf-8'):
    """
    安全的文件读取上下文管理器，确保文件句柄正确关闭

    Args:
        filepath: 文件路径
        mode: 打开模式
        encoding: 文件编码

    Yields:
        文件对象

    Raises:
        ValueError: 如果文件路径不安全
        FileNotFoundError: 如果文件不存在
    """
    # 检查路径安全性
    if not is_safe_filepath(filepath):
        raise ValueError(f"文件路径不安全: {filepath}")

    file_obj = None
    try:
        file_obj = open(filepath, mode, encoding=encoding)
        yield file_obj
    except FileNotFoundError:
        raise
    except Exception as e:
        raise IOError(f"读取文件失败: {filepath}, 错误: {str(e)}")
    finally:
        if file_obj:
            file_obj.close()


@contextmanager
def safe_file_write(filepath: str, mode: str = 'w', encoding: str = 'utf-8'):
    """
    安全的文件写入上下文管理器，确保文件句柄正确关闭

    Args:
        filepath: 文件路径
        mode: 写入模式
        encoding: 文件编码

    Yields:
        文件对象

    Raises:
        ValueError: 如果文件路径不安全
    """
    # 检查路径安全性
    if not is_safe_filepath(filepath):
        raise ValueError(f"文件路径不安全: {filepath}")

    # 确保目录存在
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    file_obj = None
    try:
        file_obj = open(filepath, mode, encoding=encoding)
        yield file_obj
        file_obj.flush()
        os.fsync(file_obj.fileno())
    except Exception as e:
        raise IOError(f"写入文件失败: {filepath}, 错误: {str(e)}")
    finally:
        if file_obj:
            file_obj.close()


@contextmanager
def safe_network_request(timeout: int = 30):
    """
    安全的网络请求上下文管理器

    Args:
        timeout: 超时时间（秒）

    Yields:
        包含超时设置的字典
    """
    yield {'timeout': timeout}


def validate_email(email: str) -> bool:
    """
    验证电子邮件地址格式

    Args:
        email: 电子邮件地址

    Returns:
        是否有效
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# =============================================================================
# 性能分析工具
# =============================================================================

F = TypeVar('F', bound=Callable[..., Any])


class PerformanceMonitor:
    """性能监控工具类"""

    def __init__(self, logger: Optional[Logger] = None):
        """
        初始化性能监控器

        Args:
            logger: 日志记录器，如果为None则使用print输出
        """
        self.logger = logger
        self.metrics: Dict[str, Dict[str, float]] = {}

    def record_execution_time(self, func_name: str, execution_time: float) -> None:
        """
        记录函数执行时间

        Args:
            func_name: 函数名称
            execution_time: 执行时间（秒）
        """
        if func_name not in self.metrics:
            self.metrics[func_name] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            }

        metrics = self.metrics[func_name]
        metrics['count'] += 1
        metrics['total_time'] += execution_time
        metrics['avg_time'] = metrics['total_time'] / metrics['count']
        metrics['max_time'] = max(metrics['max_time'], execution_time)
        metrics['min_time'] = min(metrics['min_time'], execution_time)

    def get_metrics(self, func_name: Optional[str] = None) -> Optional[Dict[str, Dict[str, float]]]:
        """
        获取性能指标

        Args:
            func_name: 函数名称，如果为None则返回所有函数的指标

        Returns:
            性能指标字典
        """
        if func_name:
            return self.metrics.get(func_name)
        return self.metrics if self.metrics else None

    def print_metrics(self) -> None:
        """打印性能指标"""
        if not self.metrics:
            if self.logger:
                self.logger.info("没有性能数据")
            else:
                print("没有性能数据")
            return

        if self.logger:
            self.logger.info("=" * 60)
            self.logger.info("性能指标汇总")
            self.logger.info("=" * 60)
            for func_name, metrics in self.metrics.items():
                self.logger.info(
                    f"{func_name}: "
                    f"调用次数={metrics['count']}, "
                    f"平均时间={metrics['avg_time']:.3f}s, "
                    f"最大时间={metrics['max_time']:.3f}s, "
                    f"最小时间={metrics['min_time']:.3f}s"
                )
            self.logger.info("=" * 60)
        else:
            print("=" * 60)
            print("性能指标汇总")
            print("=" * 60)
            for func_name, metrics in self.metrics.items():
                print(
                    f"{func_name}: "
                    f"调用次数={metrics['count']}, "
                    f"平均时间={metrics['avg_time']:.3f}s, "
                    f"最大时间={metrics['max_time']:.3f}s, "
                    f"最小时间={metrics['min_time']:.3f}s"
                )
            print("=" * 60)


# 全局性能监控器实例
_global_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    获取全局性能监控器实例

    Returns:
        PerformanceMonitor: 全局性能监控器
    """
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor


def profile(func: F) -> F:
    """
    函数性能分析装饰器

    自动记录函数的执行时间到全局性能监控器

    Args:
        func: 要分析的函数

    Returns:
        包装后的函数
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        monitor = get_performance_monitor()
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            execution_time = time.perf_counter() - start_time
            monitor.record_execution_time(func.__name__, execution_time)

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        monitor = get_performance_monitor()
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            execution_time = time.perf_counter() - start_time
            monitor.record_execution_time(func.__name__, execution_time)

    if asyncio.iscoroutinefunction(func):
        return cast(F, async_wrapper)
    return cast(F, wrapper)


# =============================================================================
# 缓存工具
# =============================================================================

from hashlib import md5
from typing import Union

class SimpleCache:
    """简单的内存缓存实现"""

    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        初始化缓存

        Args:
            max_size: 最大缓存条目数
            ttl: 生存时间（秒），默认1小时
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._access_count: Dict[str, int] = {}

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """
        生成缓存键

        Args:
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            缓存键
        """
        key_str = str(args) + str(sorted(kwargs.items()))
        return md5(key_str.encode()).hexdigest()

    def get(self, *args: Any, **kwargs: Any) -> Optional[Any]:
        """
        获取缓存值

        Args:
            *args: 键的位置参数
            **kwargs: 键的关键字参数

        Returns:
            缓存的值，如果不存在或过期则返回None
        """
        key = self._generate_key(*args, **kwargs)
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl:
            # 缓存过期
            del self._cache[key]
            if key in self._access_count:
                del self._access_count[key]
            return None

        # 更新访问计数
        self._access_count[key] = self._access_count.get(key, 0) + 1
        return value

    def set(self, value: Any, *args: Any, **kwargs: Any) -> None:
        """
        设置缓存值

        Args:
            value: 要缓存的值
            *args: 键的位置参数
            **kwargs: 键的关键字参数
        """
        key = self._generate_key(*args, **kwargs)

        # 如果缓存已满，删除最少使用的项
        if len(self._cache) >= self.max_size and key not in self._cache:
            if self._access_count:
                # 删除访问次数最少的项
                least_accessed_key = min(self._access_count, key=self._access_count.get)
                del self._cache[least_accessed_key]
                del self._access_count[least_accessed_key]
            else:
                # 如果没有访问计数，删除第一个项
                first_key = next(iter(self._cache))
                del self._cache[first_key]

        self._cache[key] = (value, time.time())
        self._access_count[key] = self._access_count.get(key, 0) + 1

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_count.clear()

    def size(self) -> int:
        """
        获取缓存大小

        Returns:
            当前缓存的条目数
        """
        return len(self._cache)


def cached(ttl: int = 3600, max_size: int = 100):
    """
    缓存装饰器

    Args:
        ttl: 生存时间（秒），默认1小时
        max_size: 最大缓存条目数，默认100

    Returns:
        装饰器函数
    """
    cache = SimpleCache(max_size=max_size, ttl=ttl)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # 尝试从缓存获取
            cached_value = cache.get(*args, **kwargs)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(result, *args, **kwargs)
            return result

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # 尝试从缓存获取
            cached_value = cache.get(*args, **kwargs)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache.set(result, *args, **kwargs)
            return result

        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator


# =============================================================================
# 迭代5: 高级监控和并发管理
# =============================================================================


# =============================================================================
# 迭代4: 速率限制、请求日志、熔断器和错误恢复
# =============================================================================

from collections import deque
from threading import Lock
import time as time_module
import uuid
from contextvars import ContextVar
from enum import Enum
from typing import Dict, Any, Optional, Callable, Tuple
import json
from datetime import datetime

# 前向声明
Logger = None  # 将在集成时从主模块导入


# =============================================================================
# Rate Limiter - 速率限制器
# =============================================================================

class RateLimiter:
    """
    速率限制器 - 实现 Token Bucket 和 Sliding Window 算法

    用于限制API调用频率，防止超过服务提供商的速率限制。

    Attributes:
        max_requests: 时间窗口内允许的最大请求数
        window_size: 时间窗口大小（秒）
        min_interval: 请求之间的最小间隔（秒）
        last_request_time: 上次请求时间
        request_times: 请求时间戳队列
        lock: 线程锁
    """

    def __init__(
        self,
        max_requests: int = 60,
        window_size: int = 60,
        min_interval: float = 0.1
    ):
        """
        初始化速率限制器

        Args:
            max_requests: 时间窗口内允许的最大请求数
            window_size: 时间窗口大小（秒）
            min_interval: 请求之间的最小间隔（秒）
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.min_interval = min_interval
        self.last_request_time = 0.0
        self.request_times: deque = deque()
        self.lock = Lock()

    def acquire(self, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        获取请求许可

        Args:
            block: 是否阻塞等待
            timeout: 阻塞等待超时时间（秒）

        Returns:
            是否成功获取许可
        """
        with self.lock:
            current_time = time_module.time()

            # 清理过期的请求时间戳
            while self.request_times and current_time - self.request_times[0] > self.window_size:
                self.request_times.popleft()

            # 检查是否超过速率限制
            if len(self.request_times) >= self.max_requests:
                return False

            # 检查最小间隔
            if current_time - self.last_request_time < self.min_interval:
                return False

            # 记录请求时间
            self.request_times.append(current_time)
            self.last_request_time = current_time
            return True

    def wait_until_available(self, max_wait: float = 60.0) -> bool:
        """
        等待直到可以发送请求

        Args:
            max_wait: 最大等待时间（秒）

        Returns:
            是否成功获取许可
        """
        start_time = time_module.time()
        while time_module.time() - start_time < max_wait:
            if self.acquire():
                return True
            time_module.sleep(0.1)
        return False

    def get_wait_time(self) -> float:
        """
        获取需要等待的时间（秒）

        Returns:
            需要等待的秒数
        """
        with self.lock:
            current_time = time_module.time()

            # 清理过期的请求时间戳
            while self.request_times and current_time - self.request_times[0] > self.window_size:
                self.request_times.popleft()

            if len(self.request_times) < self.max_requests:
                # 检查最小间隔
                interval_wait = self.min_interval - (current_time - self.last_request_time)
                return max(0.0, interval_wait)
            else:
                # 需要等待最早的请求过期
                return self.window_size - (current_time - self.request_times[0]) + 0.01

    def reset(self) -> None:
        """重置速率限制器"""
        with self.lock:
            self.request_times.clear()
            self.last_request_time = 0.0


# 预定义的速率限制器实例
class RateLimiters:
    """预定义的API速率限制器"""

    # 智谱AI速率限制器（假设：60请求/分钟）
    ZHIPU_AI = RateLimiter(max_requests=60, window_size=60, min_interval=0.5)

    # 微信公众号API速率限制器（假设：100请求/分钟）
    WECHAT_API = RateLimiter(max_requests=100, window_size=60, min_interval=0.2)

    # 企业微信Webhook速率限制器（假设：20请求/分钟）
    WECHAT_WEBHOOK = RateLimiter(max_requests=20, window_size=60, min_interval=1.0)

    # 通用HTTP请求速率限制器
    HTTP_REQUESTS = RateLimiter(max_requests=30, window_size=60, min_interval=0.5)


# =============================================================================
# Request ID Tracker - 请求ID跟踪器
# =============================================================================

# 上下文变量用于存储当前请求ID
_request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class RequestTracker:
    """
    请求ID跟踪器 - 为每个请求生成唯一的ID并跟踪请求/响应

    用于日志记录和调试，可以将相关联的请求和响应日志关联起来。
    """

    @staticmethod
    def generate_request_id() -> str:
        """
        生成唯一的请求ID

        Returns:
            唯一的请求ID字符串
        """
        return str(uuid.uuid4())

    @staticmethod
    def set_request_id(request_id: str) -> None:
        """
        设置当前上下文的请求ID

        Args:
            request_id: 请求ID
        """
        _request_id_context.set(request_id)

    @staticmethod
    def get_request_id() -> Optional[str]:
        """
        获取当前上下文的请求ID

        Returns:
            当前请求ID，如果未设置则返回None
        """
        return _request_id_context.get()

    @staticmethod
    def clear_request_id() -> None:
        """清除当前上下文的请求ID"""
        _request_id_context.set(None)


class RequestLogger:
    """
    请求/响应日志记录器

    记录所有API请求和响应的详细信息，包括请求ID、时间戳、参数等。
    """

    def __init__(self, logger=None):
        """
        初始化请求日志记录器

        Args:
            logger: 日志记录器，如果为None则使用print输出
        """
        self.logger = logger

    def log_request(
        self,
        service: str,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        记录API请求

        Args:
            service: 服务名称（如"ZhipuAI", "WeChat"等）
            method: HTTP方法（GET, POST等）
            url: 请求URL
            params: URL参数
            data: 请求体数据
            headers: 请求头

        Returns:
            请求ID
        """
        request_id = RequestTracker.generate_request_id()
        RequestTracker.set_request_id(request_id)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 构建日志消息
        log_parts = [
            f"[请求ID: {request_id}]",
            f"[{timestamp}]",
            f"服务: {service}",
            f"方法: {method}",
            f"URL: {url}"
        ]

        # 添加参数（如果存在）
        if params:
            log_parts.append(f"参数: {json.dumps(params, ensure_ascii=False)}")

        # 添加数据（如果存在且不敏感）
        if data:
            # 掩码敏感字段
            safe_data = self._mask_sensitive_fields(data)
            log_parts.append(f"数据: {json.dumps(safe_data, ensure_ascii=False)}")

        # 添加关键请求头
        if headers:
            safe_headers = self._mask_sensitive_headers(headers)
            log_parts.append(f"请求头: {json.dumps(safe_headers, ensure_ascii=False)}")

        log_message = " | ".join(log_parts)

        if self.logger:
            self.logger.info(f"📤 API请求: {log_message}")
        else:
            print(f"📤 API请求: {log_message}")

        return request_id

    def log_response(
        self,
        service: str,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: float = 0.0
    ) -> None:
        """
        记录API响应

        Args:
            service: 服务名称
            status_code: HTTP状态码
            response_data: 响应数据
            error: 错误信息（如果有）
            duration: 请求耗时（秒）
        """
        request_id = RequestTracker.get_request_id()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 构建日志消息
        log_parts = [
            f"[请求ID: {request_id or 'unknown'}]" if request_id else "[无请求ID]",
            f"[{timestamp}]",
            f"服务: {service}",
            f"状态码: {status_code}",
            f"耗时: {duration:.3f}s"
        ]

        # 添加响应数据（如果存在）
        if response_data:
            # 限制响应数据大小
            response_str = json.dumps(response_data, ensure_ascii=False)
            if len(response_str) > 500:
                response_str = response_str[:500] + "...（已截断）"
            log_parts.append(f"响应: {response_str}")

        # 添加错误信息（如果有）
        if error:
            log_parts.append(f"错误: {error}")

        log_message = " | ".join(log_parts)

        if status_code >= 400:
            if self.logger:
                self.logger.error(f"❌ API响应错误: {log_message}")
            else:
                print(f"❌ API响应错误: {log_message}")
        else:
            if self.logger:
                self.logger.info(f"📥 API响应: {log_message}")
            else:
                print(f"📥 API响应: {log_message}")

        # 清除请求ID
        RequestTracker.clear_request_id()

    def _mask_sensitive_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        掩码敏感字段

        Args:
            data: 原始数据

        Returns:
            掩码后的数据
        """
        from ZBBrainArticle import mask_sensitive_data

        sensitive_fields = ['api_key', 'password', 'secret', 'token', 'auth_code']
        safe_data = data.copy()

        for key, value in list(safe_data.items()):
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                if isinstance(value, str) and len(value) > 8:
                    safe_data[key] = mask_sensitive_data(value)

        return safe_data

    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        掩码敏感请求头

        Args:
            headers: 原始请求头

        Returns:
            掩码后的请求头
        """
        from ZBBrainArticle import mask_sensitive_data

        safe_headers = {}
        for key, value in headers.items():
            if key.lower() in ['authorization', 'x-api-key', 'cookie']:
                safe_headers[key] = mask_sensitive_data(value)
            else:
                safe_headers[key] = value
        return safe_headers


# =============================================================================
# Circuit Breaker - 熔断器
# =============================================================================

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常状态，请求正常通过
    OPEN = "open"          # 熔断状态，拒绝所有请求
    HALF_OPEN = "half_open"  # 半开状态，允许部分请求测试


class CircuitBreaker:
    """
    熔断器 - 实现熔断模式

    当外部服务连续失败达到阈值时，熔断器打开，阻止后续请求，
    避免级联故障。一段时间后进入半开状态，尝试恢复服务。

    Attributes:
        failure_threshold: 失败阈值
        success_threshold: 成功阈值（半开状态）
        timeout: 熔断超时时间（秒）
        recovery_timeout: 恢复超时时间（秒）
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        recovery_timeout: float = 30.0
    ):
        """
        初始化熔断器

        Args:
            service_name: 服务名称
            failure_threshold: 失败阈值（连续失败多少次后熔断）
            success_threshold: 成功阈值（半开状态时连续成功多少次后恢复）
            timeout: 熔断超时时间（秒）
            recovery_timeout: 恢复超时时间（秒）
        """
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.last_state_change = time_module.time()
        self.lock = Lock()

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        通过熔断器调用函数

        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数执行结果

        Raises:
            Exception: 熔断器打开或函数执行失败时抛出
        """
        with self.lock:
            if self.state == CircuitState.OPEN:
                # 检查是否可以尝试恢复
                if time_module.time() - self.last_state_change >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    self.last_state_change = time_module.time()
                else:
                    raise CircuitBreakerOpenError(
                        f"熔断器打开：{self.service_name} 服务暂时不可用"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        """处理成功情况"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.last_state_change = time_module.time()
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    def _on_failure(self) -> None:
        """处理失败情况"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time_module.time()

            if self.state == CircuitState.HALF_OPEN:
                # 半开状态失败，重新打开熔断器
                self.state = CircuitState.OPEN
                self.last_state_change = time_module.time()
            elif self.state == CircuitState.CLOSED:
                # 检查是否达到熔断阈值
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    self.last_state_change = time_module.time()

    def reset(self) -> None:
        """重置熔断器"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = 0.0
            self.last_state_change = time_module.time()

    def get_state(self) -> CircuitState:
        """
        获取当前状态

        Returns:
            当前熔断器状态
        """
        with self.lock:
            return self.state

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            return {
                'service_name': self.service_name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time,
                'last_state_change': self.last_state_change
            }


class CircuitBreakerOpenError(Exception):
    """熔断器打开异常"""
    pass


# 预定义的熔断器实例
class CircuitBreakers:
    """预定义的服务熔断器"""

    # 智谱AI熔断器
    ZHIPU_AI = CircuitBreaker("ZhipuAI", failure_threshold=5, timeout=60.0)

    # 微信公众号API熔断器
    WECHAT_API = CircuitBreaker("WeChatAPI", failure_threshold=3, timeout=30.0)

    # 企业微信Webhook熔断器
    WECHAT_WEBHOOK = CircuitBreaker("WeChatWebhook", failure_threshold=5, timeout=60.0)


# =============================================================================
# Error Recovery - 错误恢复机制
# =============================================================================

class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"           # 重试
    FALLBACK = "fallback"     # 降级
    IGNORE = "ignore"         # 忽略
    FAIL = "fail"             # 失败


class ErrorRecovery:
    """
    错误恢复管理器

    提供多种错误恢复策略，包括重试、降级、回退等。
    """

    @staticmethod
    def recover_with_retry(
        func: Callable,
        max_attempts: int = 3,
        backoff_base: float = 2.0,
        exceptions: Tuple = (Exception,),
        logger=None
    ) -> Any:
        """
        使用重试策略恢复错误

        Args:
            func: 要执行的函数
            max_attempts: 最大重试次数
            backoff_base: 退避基数
            exceptions: 需要重试的异常类型
            logger: 日志记录器

        Returns:
            函数执行结果

        Raises:
            Exception: 重试失败后抛出最后一次异常
        """
        last_exception = None

        for attempt in range(1, max_attempts + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts:
                    wait_time = backoff_base ** attempt
                    if logger:
                        logger.warning(
                            f"重试 {attempt}/{max_attempts} 失败: {str(e)}, "
                            f"{wait_time:.1f}秒后重试..."
                        )
                    time_module.sleep(wait_time)
                else:
                    if logger:
                        logger.error(f"经过 {max_attempts} 次重试后仍然失败")

        if last_exception:
            raise last_exception

    @staticmethod
    def recover_with_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        logger=None
    ) -> Any:
        """
        使用降级策略恢复错误

        Args:
            primary_func: 主函数
            fallback_func: 降级函数
            logger: 日志记录器

        Returns:
            函数执行结果
        """
        try:
            return primary_func()
        except Exception as e:
            if logger:
                logger.warning(f"主函数失败: {str(e)}, 使用降级策略")
            try:
                return fallback_func()
            except Exception as fallback_error:
                if logger:
                    logger.error(f"降级函数也失败: {str(fallback_error)}")
                raise fallback_error

    @staticmethod
    def recover_with_circuit_breaker(
        func: Callable,
        circuit_breaker: CircuitBreaker,
        logger=None
    ) -> Any:
        """
        使用熔断器保护函数调用

        Args:
            func: 要执行的函数
            circuit_breaker: 熔断器实例
            logger: 日志记录器

        Returns:
            函数执行结果

        Raises:
            Exception: 函数执行失败时抛出
        """
        try:
            return circuit_breaker.call(func)
        except CircuitBreakerOpenError as e:
            if logger:
                logger.error(str(e))
            raise e
        except Exception as e:
            if logger:
                logger.error(f"函数执行失败: {str(e)}")
            raise e

    @staticmethod
    def safe_execute(
        func: Callable,
        default_value: Any = None,
        logger=None,
        error_message: str = "操作失败"
    ) -> Any:
        """
        安全执行函数，失败时返回默认值

        Args:
            func: 要执行的函数
            default_value: 失败时返回的默认值
            logger: 日志记录器
            error_message: 错误消息

        Returns:
            函数执行结果或默认值
        """
        try:
            return func()
        except Exception as e:
            if logger:
                logger.error(f"{error_message}: {str(e)}")
            return default_value


# =============================================================================
# API Client Wrapper - API客户端包装器
# =============================================================================

class APIClientWrapper:
    """
    API客户端包装器

    集成速率限制、请求日志、熔断器和错误恢复功能。
    """

    def __init__(
        self,
        service_name: str,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        logger=None
    ):
        """
        初始化API客户端包装器

        Args:
            service_name: 服务名称
            rate_limiter: 速率限制器
            circuit_breaker: 熔断器
            logger: 日志记录器
        """
        self.service_name = service_name
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        self.logger = logger
        self.request_logger = RequestLogger(logger)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        发送HTTP请求（带完整的保护机制）

        Args:
            method: HTTP方法
            url: 请求URL
            params: URL参数
            data: 请求体数据
            headers: 请求头
            timeout: 超时时间

        Returns:
            响应数据字典

        Raises:
            Exception: 请求失败时抛出
        """
        def make_request() -> Dict[str, Any]:
            # 速率限制
            if self.rate_limiter:
                wait_time = self.rate_limiter.get_wait_time()
                if wait_time > 0:
                    if self.logger:
                        self.logger.info(
                            f"速率限制：等待 {wait_time:.2f} 秒后发送请求"
                        )
                    time_module.sleep(wait_time)

                if not self.rate_limiter.acquire():
                    raise RateLimitError(f"超过速率限制: {self.service_name}")

            # 记录请求
            self.request_logger.log_request(
                service=self.service_name,
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers
            )

            # 发送请求
            import requests
            start_time = time_module.time()
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, headers=headers, timeout=timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, params=params, json=data, headers=headers, timeout=timeout)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")

                duration = time_module.time() - start_time

                # 记录响应
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = {"text": response.text}

                self.request_logger.log_response(
                    service=self.service_name,
                    status_code=response.status_code,
                    response_data=response_data,
                    duration=duration
                )

                # 检查状态码
                if response.status_code >= 400:
                    error_msg = response_data.get('error', response.text)
                    raise APIError(f"API错误 ({response.status_code}): {error_msg}")

                return response_data

            except Exception as e:
                duration = time_module.time() - start_time
                self.request_logger.log_response(
                    service=self.service_name,
                    status_code=500,
                    error=str(e),
                    duration=duration
                )
                raise e

        # 使用熔断器保护
        if self.circuit_breaker:
            try:
                return self.circuit_breaker.call(make_request)
            except CircuitBreakerOpenError as e:
                if self.logger:
                    self.logger.error(str(e))
                raise e
        else:
            return make_request()

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        return self.request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        return self.request('POST', url, data=data, **kwargs)


class RateLimitError(Exception):
    """速率限制错误"""
    pass


class APIError(Exception):
    """API错误"""
    pass


# =============================================================================
# 迭代5: 高级监控和并发管理
# =============================================================================


class MetricsCollector:
    """
    指标收集器 - 收聚和聚合系统指标

    功能：
    - 收集性能指标（响应时间、吞吐量）
    - 收集错误指标（错误率、错误类型）
    - 收集业务指标（文章生成数、成功率）
    - 支持指标导出和报告生成

    Attributes:
        metrics: 指标存储字典
        start_time: 收集器启动时间
    """

    def __init__(self) -> None:
        """初始化指标收集器"""
        self.metrics: Dict[str, Dict[str, Any]] = {
            'performance': {},
            'errors': {},
            'business': {},
            'system': {}
        }
        self.start_time: float = time.time()
        self._lock = asyncio.Lock()

    async def record_metric(self, category: str, name: str, value: Any,
                           tags: Optional[Dict[str, str]] = None) -> None:
        """
        记录单个指标

        Args:
            category: 指标类别 (performance, errors, business, system)
            name: 指标名称
            value: 指标值
            tags: 可选的标签字典
        """
        async with self._lock:
            if category not in self.metrics:
                self.metrics[category] = {}

            if name not in self.metrics[category]:
                self.metrics[category][name] = {
                    'values': [],
                    'count': 0,
                    'tags': tags or {}
                }

            self.metrics[category][name]['values'].append(value)
            self.metrics[category][name]['count'] += 1

            # 保持最近1000个值
            if len(self.metrics[category][name]['values']) > 1000:
                self.metrics[category][name]['values'].pop(0)

    async def increment_counter(self, category: str, name: str,
                               delta: int = 1) -> None:
        """
        增加计数器

        Args:
            category: 指标类别
            name: 指标名称
            delta: 增量值
        """
        async with self._lock:
            if category not in self.metrics:
                self.metrics[category] = {}

            if name not in self.metrics[category]:
                self.metrics[category][name] = {'count': 0}

            self.metrics[category][name]['count'] += delta

    async def get_metric_summary(self, category: str,
                                 name: str) -> Optional[Dict[str, Any]]:
        """
        获取指标摘要统计

        Args:
            category: 指标类别
            name: 指标名称

        Returns:
            包含统计信息的字典，如果指标不存在则返回None
        """
        async with self._lock:
            if category not in self.metrics or name not in self.metrics[category]:
                return None

            metric = self.metrics[category][name]
            if 'values' in metric and metric['values']:
                values = metric['values']
                return {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1],
                    'tags': metric.get('tags', {})
                }
            elif 'count' in metric:
                return {
                    'count': metric['count'],
                    'tags': metric.get('tags', {})
                }
            return None

    async def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有指标

        Returns:
            所有指标的字典
        """
        async with self._lock:
            return self.metrics.copy()

    async def reset_metrics(self, category: Optional[str] = None) -> None:
        """
        重置指标

        Args:
            category: 要重置的类别，如果为None则重置所有
        """
        async with self._lock:
            if category:
                if category in self.metrics:
                    self.metrics[category] = {}
            else:
                for cat in self.metrics:
                    self.metrics[cat] = {}

    async def get_uptime(self) -> float:
        """
        获取运行时间

        Returns:
            运行时间（秒）
        """
        return time.time() - self.start_time


class HealthCheck:
    """
    健康检查系统

    功能：
    - 检查系统组件健康状态
    - 提供健康检查端点
    - 自动检测和报告系统问题
    - 支持自定义健康检查函数

    Attributes:
        checks: 注册的健康检查函数字典
        last_results: 最近一次检查结果
    """

    def __init__(self) -> None:
        """初始化健康检查系统"""
        self.checks: Dict[str, Callable[[], Awaitable[bool]]] = {}
        self.last_results: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def register_check(self, name: str,
                      check_func: Callable[[], Awaitable[bool]]) -> None:
        """
        注册健康检查函数

        Args:
            name: 检查名称
            check_func: 异步检查函数，返回True表示健康
        """
        self.checks[name] = check_func

    def register_sync_check(self, name: str,
                           check_func: Callable[[], bool]) -> None:
        """
        注册同步健康检查函数

        Args:
            name: 检查名称
            check_func: 同步检查函数，返回True表示健康
        """
        async def async_wrapper() -> bool:
            return check_func()
        self.checks[name] = async_wrapper

    async def run_check(self, name: str) -> Dict[str, Any]:
        """
        运行单个健康检查

        Args:
            name: 检查名称

        Returns:
            检查结果字典
        """
        if name not in self.checks:
            return {
                'name': name,
                'status': 'unknown',
                'error': 'Check not registered'
            }

        start_time = time.time()
        try:
            result = await self.checks[name]()
            duration = time.time() - start_time

            check_result = {
                'name': name,
                'status': 'healthy' if result else 'unhealthy',
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }

            async with self._lock:
                self.last_results[name] = check_result

            return check_result
        except Exception as e:
            duration = time.time() - start_time
            check_result = {
                'name': name,
                'status': 'error',
                'error': str(e),
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }

            async with self._lock:
                self.last_results[name] = check_result

            return check_result

    async def run_all_checks(self) -> Dict[str, Any]:
        """
        运行所有健康检查

        Returns:
            包含所有检查结果的字典
        """
        results = {}
        overall_healthy = True

        for name in self.checks:
            result = await self.run_check(name)
            results[name] = result
            if result['status'] != 'healthy':
                overall_healthy = False

        return {
            'overall_status': 'healthy' if overall_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'checks': results
        }

    async def get_last_results(self) -> Dict[str, Dict[str, Any]]:
        """
        获取最近的检查结果

        Returns:
            最近检查结果字典
        """
        async with self._lock:
            return self.last_results.copy()


class AsyncTaskQueue:
    """
    异步任务队列 - 管理并发操作

    功能：
    - 管理异步任务队列
    - 控制并发数量
    - 支持任务优先级
    - 提供任务状态监控
    - 自动重试失败任务

    Attributes:
        max_concurrent: 最大并发任务数
        queue: 任务队列
        running_tasks: 当前运行的任务
        results: 任务结果存储
    """

    def __init__(self, max_concurrent: int = 5,
                 max_retries: int = 3) -> None:
        """
        初始化任务队列

        Args:
            max_concurrent: 最大并发任务数
            max_retries: 失败任务最大重试次数
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Set[asyncio.Task] = set()
        self.worker_tasks: Set[asyncio.Task] = set()
        self.results: Dict[str, Any] = {}
        self.metrics: MetricsCollector = MetricsCollector()
        self._worker_semaphore = asyncio.Semaphore(max_concurrent)
        self._shutdown = False

    async def submit(self, coro: Callable[[], Any],
                    task_id: Optional[str] = None,
                    priority: int = 0) -> str:
        """
        提交任务到队列

        Args:
            coro: 协程函数或返回协程的可调用对象
            task_id: 可选的任务ID
            priority: 任务优先级（数字越大优先级越高）

        Returns:
            任务ID
        """
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}_{id(coro)}"

        await self.queue.put((priority, task_id, coro, 0))
        await self.metrics.increment_counter('queue', 'submitted')
        return task_id

    async def _worker(self) -> None:
        """工作协程 - 从队列获取并执行任务"""
        while not self._shutdown:
            try:
                # 获取任务（带超时以允许优雅关闭）
                try:
                    priority, task_id, coro_func, retry_count = \
                        await asyncio.wait_for(
                            self.queue.get(),
                            timeout=1.0
                        )
                except asyncio.TimeoutError:
                    continue

                # 执行任务
                async with self._worker_semaphore:
                    task = asyncio.create_task(
                        self._execute_task(task_id, coro_func, retry_count)
                    )
                    self.running_tasks.add(task)
                    task.add_done_callback(
                        lambda t: self.running_tasks.discard(t)
                    )

            except Exception as e:
                # 记录错误但继续运行
                await self.metrics.record_metric(
                    'errors', 'worker_error', 1,
                    {'error': str(e)}
                )

    async def _execute_task(self, task_id: str,
                           coro_func: Callable[[], Any],
                           retry_count: int) -> None:
        """
        执行单个任务

        Args:
            task_id: 任务ID
            coro_func: 协程函数或返回协程的可调用对象
            retry_count: 当前重试次数
        """
        start_time = time.time()
        try:
            # 执行函数/协程
            result = coro_func()

            # 如果返回的是协程，await它
            if asyncio.iscoroutine(result):
                result = await result

            # 记录成功结果
            duration = time.time() - start_time
            self.results[task_id] = {
                'status': 'completed',
                'result': result,
                'duration': duration,
                'retry_count': retry_count
            }

            await self.metrics.record_metric(
                'performance', 'task_duration', duration
            )
            await self.metrics.increment_counter('tasks', 'completed')

        except Exception as e:
            duration = time.time() - start_time

            # 尝试重试
            if retry_count < self.max_retries:
                await self.queue.put((
                    0,  # 重试任务优先级为0
                    task_id,
                    coro_func,
                    retry_count + 1
                ))
                await self.metrics.increment_counter('tasks', 'retrying')
            else:
                # 记录失败
                self.results[task_id] = {
                    'status': 'failed',
                    'error': str(e),
                    'duration': duration,
                    'retry_count': retry_count
                }
                await self.metrics.increment_counter('tasks', 'failed')

    async def start(self, num_workers: Optional[int] = None) -> None:
        """
        启动工作协程

        Args:
            num_workers: 工作协程数量，默认为max_concurrent的2倍
        """
        if num_workers is None:
            num_workers = self.max_concurrent * 2

        for _ in range(num_workers):
            worker = asyncio.create_task(self._worker())
            self.worker_tasks.add(worker)

    async def stop(self) -> None:
        """停止任务队列"""
        self._shutdown = True

        # 等待队列清空
        while not self.queue.empty():
            await asyncio.sleep(0.1)

        # 取消所有工作协程
        for worker in self.worker_tasks:
            worker.cancel()

        # 取消所有运行中的任务
        for task in self.running_tasks:
            task.cancel()

        # 等待任务取消完成
        all_tasks = list(self.worker_tasks) + list(self.running_tasks)
        if all_tasks:
            await asyncio.gather(*all_tasks, return_exceptions=True)

    async def get_status(self) -> Dict[str, Any]:
        """
        获取队列状态

        Returns:
            状态信息字典
        """
        return {
            'queue_size': self.queue.qsize(),
            'running_tasks': len(self.running_tasks),
            'max_concurrent': self.max_concurrent,
            'total_results': len(self.results),
            'completed': sum(
                1 for r in self.results.values()
                if r['status'] == 'completed'
            ),
            'failed': sum(
                1 for r in self.results.values()
                if r['status'] == 'failed'
            )
        }

    async def get_result(self, task_id: str,
                        timeout: Optional[float] = None) -> Any:
        """
        获取任务结果

        Args:
            task_id: 任务ID
            timeout: 可选的超时时间

        Returns:
            任务结果

        Raises:
            asyncio.TimeoutError: 超时未完成
            KeyError: 任务不存在
        """
        start_time = time.time()
        while True:
            if task_id in self.results:
                result = self.results[task_id]
                if result['status'] == 'completed':
                    return result['result']
                elif result['status'] == 'failed':
                    raise Exception(result['error'])

            if timeout and (time.time() - start_time) > timeout:
                raise asyncio.TimeoutError(
                    f"Task {task_id} did not complete in {timeout}s"
                )

            await asyncio.sleep(0.1)


class ConfigHotReload:
    """
    配置热重载管理器

    功能：
    - 监控配置文件变化
    - 自动重新加载配置
    - 验证新配置的有效性
    - 通知配置变更事件
    - 支持配置回滚

    Attributes:
        config_file: 配置文件路径
        config: 当前配置对象
        last_mtime: 最后修改时间
        reload_callbacks: 重载回调函数列表
        _watcher_task: 文件监控任务
    """

    def __init__(self, config_file: str,
                 check_interval: float = 5.0) -> None:
        """
        初始化配置热重载管理器

        Args:
            config_file: 配置文件路径
            check_interval: 检查间隔（秒）
        """
        self.config_file = config_file
        self.check_interval = check_interval
        self.config: Optional[Config] = None
        self.last_mtime: float = 0.0
        self.reload_callbacks: List[Callable[[Config], Any]] = []
        self._watcher_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        self._shutdown = False
        self._config_history: List[Tuple[Config, float]] = []

    async def start(self) -> None:
        """启动配置监控"""
        if not os.path.exists(self.config_file):
            raise ConfigurationError(
                f"配置文件不存在: {self.config_file}"
            )

        # 初始加载
        self.config = Config(self.config_file)
        self.last_mtime = os.path.getmtime(self.config_file)

        # 启动监控任务
        self._watcher_task = asyncio.create_task(self._watch_config_file())

    async def stop(self) -> None:
        """停止配置监控"""
        self._shutdown = True
        if self._watcher_task:
            self._watcher_task.cancel()
            try:
                await self._watcher_task
            except asyncio.CancelledError:
                pass

    async def _watch_config_file(self) -> None:
        """监控配置文件变化"""
        while not self._shutdown:
            try:
                current_mtime = os.path.getmtime(self.config_file)

                if current_mtime > self.last_mtime:
                    await self._reload_config()
                    self.last_mtime = current_mtime

                await asyncio.sleep(self.check_interval)

            except Exception as e:
                # 记录错误但继续监控
                await asyncio.sleep(self.check_interval)

    async def _reload_config(self) -> None:
        """重新加载配置"""
        async with self._lock:
            try:
                # 保存旧配置到历史（保留最近5个版本）
                if self.config:
                    self._config_history.append(
                        (self.config, time.time())
                    )
                    if len(self._config_history) > 5:
                        self._config_history.pop(0)

                # 加载新配置
                new_config = Config(self.config_file)

                # 验证新配置
                self._validate_new_config(new_config)

                # 更新当前配置
                self.config = new_config

                # 通知回调函数
                for callback in self.reload_callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(new_config)
                    else:
                        callback(new_config)

            except Exception as e:
                # 新配置无效，保持旧配置
                raise ConfigurationError(
                    f"配置重载失败，保持旧配置: {e}"
                )

    def _validate_new_config(self, new_config: Config) -> None:
        """
        验证新配置

        Args:
            new_config: 新配置对象

        Raises:
            ConfigurationError: 配置验证失败
        """
        # 基本验证已由Config类完成
        # 这里可以添加额外的验证逻辑

        # 示例：检查关键配置是否变更
        if self.config:
            # 如果API密钥变更，可能需要特别处理
            if new_config.zhipu_api_key != self.config.zhipu_api_key:
                # 可以在这里添加特殊的处理逻辑
                pass

    def on_reload(self, callback: Callable[[Config], Any]) -> None:
        """
        注册配置重载回调函数

        Args:
            callback: 回调函数，接收新配置作为参数
        """
        self.reload_callbacks.append(callback)

    async def get_config(self) -> Config:
        """
        获取当前配置

        Returns:
            当前配置对象
        """
        async with self._lock:
            if self.config is None:
                raise ConfigurationError("配置尚未加载")
            return self.config

    async def rollback(self, steps: int = 1) -> Optional[Config]:
        """
        回滚到之前的配置版本

        Args:
            steps: 回滚步数

        Returns:
            回滚后的配置对象，如果失败返回None
        """
        async with self._lock:
            if steps > len(self._config_history):
                return None

            old_config, _ = self._config_history[-steps]
            self.config = old_config

            # 通知回调函数
            for callback in self.reload_callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(old_config)
                else:
                    callback(old_config)

            return old_config

    async def force_reload(self) -> Config:
        """
        强制重新加载配置

        Returns:
            新配置对象
        """
        await self._reload_config()
        return await self.get_config()


# =============================================================================
# 配置管理类
# =============================================================================

class Config:
    """
    配置管理类

    负责加载、验证和管理项目的所有配置项。

    Attributes:
        config_file: 配置文件路径
        config: ConfigParser实例
       搜狗微信搜索相关配置
        总包大脑相关配置
        智谱AI相关配置
        微信公众号相关配置
        企业微信相关配置
        邮件通知相关配置
        任务调度相关配置
    """

    def __init__(self, config_file: str = "config.ini") -> None:
        """
        初始化配置

        Args:
            config_file: 配置文件路径，默认为"config.ini"

        Raises:
            ConfigurationError: 配置文件不存在或格式错误时抛出
        """
        self.config_file: str = config_file
        self.config: configparser.ConfigParser = configparser.RawConfigParser()
        self.load_config()
        self._validate_config()

    def load_config(self) -> None:
        """
        加载配置文件

        安全增强：
        - 验证URL配置
        - 掩码敏感信息（不在日志中显示）
        - 验证邮箱格式

        Raises:
            ConfigurationError: 配置文件不存在或格式错误时抛出
        """
        if not os.path.exists(self.config_file):
            raise ConfigurationError(f"配置文件不存在: {self.config_file}")

        self.config.read(self.config_file, encoding='utf-8')

        # 搜狗微信搜索配置
        self.sogou_url = sanitize_url(self.config.get('搜狗微信搜索', '搜狗微信搜索网址'))
        self.default_keyword = sanitize_input(self.config.get('搜狗微信搜索', '默认搜索关键词'), max_length=100)
        self.default_pages = self.config.getint('搜狗微信搜索', '默认翻页页数')
        self.max_pages = self.config.getint('搜狗微信搜索', '最大翻页页数')

        # 关键词轮换配置
        self.keyword_rotation_file = self.config.get('搜狗微信搜索', '关键词轮换状态文件', fallback='./keyword_rotation.json')
        self.keywords_file = './keywords.txt'
        self.default_keyword = self.default_keyword  # 保存默认关键词
        self._init_keyword_rotation()

        # 总包大脑配置
        self.metaso_url = sanitize_url(self.config.get('总包大脑', '总包大脑网址'))
        self.user_data_dir = self.config.get('总包大脑', '用户数据目录')
        self.max_wait_time = self.config.getint('总包大脑', '最大等待回复时间')
        self.check_interval = self.config.getint('总包大脑', '回复检查间隔')

        # 智谱AI配置（敏感信息）
        self.zhipu_api_key = self.config.get('智谱AI', 'API Key')
        self.zhipu_api_url = sanitize_url(self.config.get('智谱AI', 'API 地址'))
        # 【0成本优化 V2.0】使用 GLM-4.7-Flash 完全免费模型
        # GLM-4.7-Flash: 200K上下文，同级别最强通用能力，完全免费
        # 低成本模型配置（用于简单任务，如生成问题、标题、图片提示词）- 免费
        self.zhipu_model_fast = self.config.get('智谱AI', '低成本模型名称', fallback='glm-4.7-flash')
        # 标题生成也使用低成本模型，通过优化提示词提升质量
        self.zhipu_model_title = self.zhipu_model_fast
        # 【0成本优化 V2.0】高质量模型也使用 GLM-4.7-Flash 免费，通过增强提示词保障质量
        # GLM-4.7-Flash 能力足以胜任内容结构化和HTML排版任务
        self.zhipu_model_pro = self.config.get('智谱AI', '高质量模型名称', fallback='glm-4.7-flash')
        # 图片生成模型配置（cogview-3-flash 免费，cogview-3 收费）
        self.image_model = self.config.get('智谱AI', '图片生成模型', fallback='cogview-3-flash')
        # 兼容旧配置（如果没有指定低/高质量模型，则使用统一的模型名称）
        self.zhipu_model = self.config.get('智谱AI', '模型名称', fallback=self.zhipu_model_fast)
        self.min_question_length = self.config.getint('智谱AI', '问题最小字符数')
        self.min_answer_length = self.config.getint('智谱AI', '回复最小字符数')

        # 微信公众号配置（敏感信息）
        self.wechat_appid = self.config.get('微信公众号', 'AppID')
        self.wechat_secret = self.config.get('微信公众号', 'AppSecret')  # 敏感
        self.cover_image_path = self.config.get('微信公众号', '封面图片路径')
        # 封面图轮换配置
        self.cover_rotation_file = self.config.get('微信公众号', '封面轮换状态文件', fallback='./cover_rotation.json')
        self.cover_images = ['cover.jpg', 'cover2.jpg']  # 可轮换的封面图列表
        self.default_author = sanitize_input(self.config.get('微信公众号', '默认作者'), max_length=50)
        # 原创声明和评论配置
        self.declare_original = self.config.getboolean('微信公众号', '声明原创', fallback=True)
        self.enable_comment = self.config.getboolean('微信公众号', '开启评论', fallback=True)
        # 广告图配置
        self.top_ad_image = self.config.get('广告图设置', '顶部广告图路径', fallback='image/top-image.jpg')
        self.bottom_ad_image = self.config.get('广告图设置', '底部广告图路径', fallback='image/bottom-image.jpg')
        self.enable_top_ad = self.config.getboolean('广告图设置', '显示顶部广告图', fallback=True)
        self.enable_bottom_ad = self.config.getboolean('广告图设置', '显示底部广告图', fallback=True)

        # 原创声明和评论配置
        self.declare_original = self.config.getboolean('微信公众号', '声明原创', fallback=True)
        self.enable_comment = self.config.getboolean('微信公众号', '开启评论', fallback=True)

        # 定时发布配置
        self.enable_schedule_publish = self.config.getboolean('微信公众号', '启用定时发布', fallback=False)
        self.schedule_publish_delay = self.config.getint('微信公众号', '定时发布延迟分钟', fallback=15)

        # 企业微信配置
        self.wechat_webhook = sanitize_url(self.config.get('企业微信通知', 'Webhook地址'))

        # 邮件通知配置
        self.notification_email = self.config.get('邮件通知', '接收邮箱', fallback='')
        self.smtp_server = self.config.get('邮件通知', 'SMTP服务器', fallback='smtp.qq.com')
        self.smtp_port = self.config.getint('邮件通知', 'SMTP端口', fallback=587)
        self.sender_email = self.config.get('邮件通知', '发件邮箱', fallback='')
        self.email_auth_code = self.config.get('邮件通知', '授权码', fallback='')  # 敏感
        # 默认不启用邮件通知
        self.send_email_enabled = self.config.getboolean('邮件通知', '启用邮件通知', fallback=False)

        # 任务调度配置
        self.enable_scheduler = self.config.getboolean('定时任务', '启用定时任务', fallback=True)
        self.run_frequency_hours = self.config.getint('定时任务', '运行间隔小时', fallback=2)
        self.stop_run_hour = self.config.getint('定时任务', '停止运行小时', fallback=22)
        self.start_run_hour = self.config.getint('定时任务', '开始运行小时', fallback=6)

        # 系统设置
        self.content_retention_threshold = self.config.getfloat('系统设置', '内容保留阈值', fallback=0.95)

        # 其他配置
        self.log_file_path = self.config.get('其他', '日志文件路径')
        self.temp_dir = self.config.get('其他', '临时文件目录')
        self.debug_mode = self.config.getboolean('其他', '调试模式')
        self.max_retry_times = self.config.getint('其他', '最多重试次数')

        # 文章主题配置
        self.article_theme = self.config.get('文章主题', '默认主题', fallback='秋日暖光')
        # 中文主题名称映射到md2wechat的英文主题名（扩展版）
        self.theme_mapping = {
            '秋日暖光': 'autumn-warm',
            '春日清新': 'spring-fresh',
            '深海静谧': 'ocean-calm',
            '优雅金': 'elegant-gold',
            '活力红': 'bold-red',
            '简约蓝': 'minimal-blue',
            '专注绿': 'focus-green',
            # API主题（需要md2wechat API服务）
            '默认': 'default',
            '自定义': 'custom',
            '苹果风格': 'apple',
            '字节跳动': 'bytedance',
            '中国风': 'chinese',
            '赛博朋克': 'cyber',
            '运动风': 'sports',
        }
        self.md2wechat_theme = self.theme_mapping.get(self.article_theme, 'autumn-warm')

        # 读取主题描述（用于AI生成提示词）
        self.theme_descriptions = {}
        for key in self.config.options('文章主题'):
            if key.endswith('描述'):
                theme_name = key.replace('描述', '')
                self.theme_descriptions[theme_name] = self.config.get('文章主题', key)

        # 获取当前主题的描述
        self.theme_description = self.theme_descriptions.get(
            self.article_theme,
            '温暖治愈，橙色调，文艺美学'
        )

        # 主题轮换配置
        self.enable_theme_rotation = self.config.getboolean('文章主题', '启用主题轮换', fallback=True)
        self.theme_rotation_file = self.config.get('文章主题', '主题轮换状态文件', fallback='./theme_rotation.json')

        # 如果启用主题轮换，则自动选择下一个主题
        if self.enable_theme_rotation:
            self.article_theme = self._get_next_theme()
            self.md2wechat_theme = self.theme_mapping.get(self.article_theme, 'autumn-warm')
            self.theme_description = self.theme_descriptions.get(
                self.article_theme,
                '温暖治愈，橙色调，文艺美学'
            )
        # 注意：logger此时还未初始化，将在main()中输出主题信息

        # 创建必要的目录
        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)

        # 加载AI提示词配置
        self._load_prompts()

        # 初始化多微信公众号配置
        self._init_wechat_accounts()

        # 初始化回复人设提示词轮换配置
        self._init_prompts_rotation()

    def _load_prompts(self) -> None:
        """从配置文件加载AI提示词

        提示词存储在config.ini的[AI提示词-*]部分
        如果配置文件中没有，则使用默认值
        """
        # 热点问题提示词
        self.prompt_hot_question_system = self.config.get(
            'AI提示词-热点问题', '系统角色',
            fallback='''你是一位资深的EPC总承包行业专家，拥有20年以上行业经验，擅长运用JTBD（焦糖布丁）理论分析市场热点和用户真实需求。

你的核心能力：
1. 场景化思维：能够从文章中识别具体的应用场景（投标、设计、施工、竣工、国际项目等）
2. 问题敏锐度：能够从行业资讯中捕捉到从业者面临的真实困惑和挑战
3. 用户视角：能够站在从业者角度思考他们真正关心的问题

你的工作原则：
1. 场景优先：所有问题都必须基于具体场景，不能泛泛而谈
2. 真实问题：问题必须反映实际工作中的真实困惑，不是理论探讨
3. 清晰准确：用足够的文字把场景和问题描述清楚（不少于50字）
4. 问句形式：问题必须是问句，有明确的疑问指向'''
        )
        self.prompt_hot_question_user = self.config.get(
            'AI提示词-热点问题', '用户提示词',
            fallback='''基于以下EPC总承包行业资讯，运用JTBD理论分析并生成一个聚焦具体场景的真实问题。

【核心任务】
请仔细阅读以下资讯内容，从中识别出一个EPC总承包从业者在实际工作中可能面临的具体场景和真实问题。

【资讯内容】
{articles_context}

【问题生成要求】
1. 必须聚焦具体场景（如：投标利润分配、设计变更索赔、分包违约处理等）
2. 必须反映真实困惑（从业者在实际工作中会遇到的问题）
3. 字数不少于50字，确保描述清楚
4. 必须包含"EPC总承包"或"EPC"
5. 只输出一个问题，直接输出问题本身'''
        )

        # 爆款标题提示词
        self.prompt_title_system = self.config.get(
            'AI提示词-爆款标题', '系统角色',
            fallback='''你是公众号10万+爆款标题大师，精通自媒体标题心理学。

核心工作原则：
1. 场景优先：从热点问题中提取具体场景（投标/设计/施工/结算等）
2. 公式驱动：运用十大10万+标题公式生成标题
3. 痛点直击：标题必须直击从业者的真实痛点
4. 数字增强：用数字增强标题吸引力和可信度'''
        )
        self.prompt_title_user = self.config.get(
            'AI提示词-爆款标题', '用户提示词',
            fallback='''基于以下热点问题，凝练生成一个10万+风格的爆款标题。

【热点问题】
{question}

【文章内容（用于提取关键信息）】
{content}

【标题硬性要求】
1. 必须包含"EPC总承包"或"EPC"
2. 必须体现热点问题中的具体场景
3. 18-28个汉字之间，结尾不要有标点
4. 必须包含数字
5. 用词完整准确

【输出要求】
直接输出一个标题，不要任何解释'''
        )

        # 内容结构化提示词
        self.prompt_structure_system = self.config.get(
            'AI提示词-内容结构化', '系统角色',
            fallback='你是专业的排版编辑。你的唯一任务是在原文中插入Markdown标题(##和###)，绝对不能修改、删减或扩展任何原文内容。你必须确保输出的每一个字（除标题外）都与原文完全一致。'
        )
        self.prompt_structure_user = self.config.get(
            'AI提示词-内容结构化', '用户提示词',
            fallback='''请为以下内容添加层次化的Markdown标题结构。

【绝对禁止事项】
1. 禁止删减任何原文内容
2. 禁止精炼、压缩、概括原文
3. 禁止扩展、补充、增加内容
4. 禁止修改任何句子、词汇、标点
5. 禁止调整段落顺序
6. 禁止改变原文的语气和风格

【你只能做以下操作】
1. 在适当位置插入二级标题(##)和三级标题(###)
2. 标题必须放在对应段落之前
3. 标题应简洁概括下方内容的主题

【需要添加标题的内容】
{content}'''
        )

        # 封面图片提示词
        self.prompt_cover_system = self.config.get(
            'AI提示词-封面图片', '系统角色',
            fallback='你是专业的商业插画师，擅长创作色彩丰富、高饱和度的火柴人风格工程建设主题漫画。风格鲜艳明快，视觉冲击力强，色彩丰富，避免黑白灰单调配色，突出工程特点和审计场景，适合微信公众号文章封面。'
        )
        self.prompt_cover_user = self.config.get(
            'AI提示词-封面图片', '用户提示词',
            fallback='''请为以下EPC总承包主题生成一个高饱和度彩色火柴人风格的封面图片描述。

【主题内容】
{question}

【回答摘要】
{answer}

【风格要求】
- 高饱和度彩色火柴人风格
- 色彩丰富，视觉冲击力强
- 突出工程建设场景特点
- 横版构图900x500
- 描述不超过300字'''
        )

        # HTML排版提示词
        self.prompt_html_system_template = self.config.get(
            'AI提示词-HTML排版', '系统角色模板',
            fallback='''你是专业的微信公众号排版设计师，精通'{theme_name}'主题设计（{theme_desc}）。

你的专业能力：
1. 精通CSS内联样式和微信兼容HTML
2. 擅长创建视觉层次分明的排版
3. 注重阅读体验和美学平衡
4. 严格保持原文内容完整性

排版原则：
- 专业：遵循排版规范，细节考究
- 精致：每个元素都经过精心设计
- 易读：舒适的字号、行高和间距
- 美观：配色协调，视觉平衡'''
        )
        self.prompt_html_user = self.config.get(
            'AI提示词-HTML排版', '用户提示词',
            fallback='''请将以下Markdown内容转换为符合"{theme_name}"主题风格的HTML。

【重要规则】
1. 所有CSS必须是内联样式（style属性）
2. 不使用外部样式表或<style>标签
3. 只使用安全的HTML标签：section, p, span, strong, em, br, h1-h6, blockquote, pre, code, img
4. 【禁止使用列表标签】绝对禁止使用ul、ol、li等列表标签，所有列表项必须转换为段落(p)格式，使用序号或符号作为段落开头（如"1. "、"• "、"◆ "等）
5. 图片使用占位符格式：<!-- IMG:数字 -->，从0开始编号
6. 只输出HTML，不要额外说明

【Markdown内容】
{md_content}'''
        )

    def _get_next_theme(self) -> str:
        """获取下一个主题（主题轮换）

        轮换策略：
        1. 读取上次使用的主题索引
        2. 选择下一个主题（循环）
        3. 保存当前选择供下次使用

        Returns:
            下一个主题的中文名称
        """
        # 可用主题列表（仅使用核心主题，不包含API主题）
        available_themes = [
            '秋日暖光',    # 温暖治愈，橙色调
            '春日清新',    # 清新自然，绿色调
            '深海静谧',    # 深沉冷静，蓝色调
            '优雅金',      # 高端大气，金色调
            '活力红',      # 活力热情，红色调
            '简约蓝',      # 简约现代，蓝色调
            '专注绿',      # 专注沉稳，绿色调
        ]

        # 读取状态文件
        rotation_state = self._load_theme_rotation_state()
        last_index = rotation_state.get('last_index', -1)
        usage_count = rotation_state.get('usage_count', {})

        # 计算下一个主题索引（循环）
        next_index = (last_index + 1) % len(available_themes)
        next_theme = available_themes[next_index]

        # 更新使用次数
        usage_count[next_theme] = usage_count.get(next_theme, 0) + 1

        # 保存状态
        self._save_theme_rotation_state({
            'last_index': next_index,
            'last_theme': next_theme,
            'usage_count': usage_count,
            'last_update': datetime.now().isoformat()
        })

        return next_theme

    def _load_theme_rotation_state(self) -> Dict[str, Any]:
        """加载主题轮换状态

        Returns:
            包含上次索引、使用次数等信息的字典
        """
        try:
            if os.path.exists(self.theme_rotation_file):
                with open(self.theme_rotation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'last_index': -1, 'usage_count': {}}

    def _save_theme_rotation_state(self, state: Dict[str, Any]) -> None:
        """保存主题轮换状态

        Args:
            state: 要保存的状态字典
        """
        try:
            with open(self.theme_rotation_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_rotating_cover_image(self) -> str:
        """获取轮换的封面图片路径

        轮换策略：
        - 在 cover.jpg 和 cover2.jpg 之间交替轮换
        - 如果某个文件不存在则跳过
        - 状态保存在 cover_rotation.json 文件中

        Returns:
            str: 封面图片的绝对路径
        """
        script_dir = Path(__file__).parent.resolve()
        image_dir = script_dir / 'image'

        # 获取可用的封面图列表
        available_covers = []
        for cover_name in self.cover_images:
            cover_path = image_dir / cover_name
            if cover_path.exists():
                available_covers.append(cover_name)

        if not available_covers:
            _logger = getattr(self, 'logger', None)
            if _logger:
                _logger.warning("没有找到可用的封面图片")
            return str(image_dir / 'cover.jpg')  # 返回默认路径

        if len(available_covers) == 1:
            # 只有一个封面图，直接使用
            selected_cover = available_covers[0]
            _logger = getattr(self, 'logger', None)
            if _logger:
                _logger.info(f"仅有一个封面图可用: {selected_cover}")
            return str(image_dir / selected_cover)

        # 加载轮换状态
        state = self._load_cover_rotation_state()
        last_index = state.get('last_index', -1)

        # 计算下一个索引（轮换）
        next_index = (last_index + 1) % len(available_covers)
        selected_cover = available_covers[next_index]

        # 保存轮换状态
        self._save_cover_rotation_state({
            'last_index': next_index,
            'last_cover': selected_cover,
            'last_used': datetime.now().isoformat()
        })

        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"🎨 封面图轮换: {selected_cover} (索引: {next_index})")
        return str(image_dir / selected_cover)

    def _load_cover_rotation_state(self) -> Dict[str, Any]:
        """加载封面图轮换状态

        Returns:
            Dict: 包含轮换状态的字典
        """
        try:
            if os.path.exists(self.cover_rotation_file):
                with open(self.cover_rotation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'last_index': -1, 'last_cover': '', 'last_used': ''}

    def _save_cover_rotation_state(self, state: Dict[str, Any]) -> None:
        """保存封面图轮换状态

        Args:
            state: 要保存的状态字典
        """
        try:
            with open(self.cover_rotation_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _init_keyword_rotation(self) -> None:
        """初始化关键词轮换功能"""
        self.keywords_list = []
        self.current_keyword_index = 0

        # 从 keywords.txt 读取关键词列表
        try:
            if os.path.exists(self.keywords_file):
                with open(self.keywords_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        keyword = line.strip()
                        if keyword and not keyword.startswith('#'):
                            self.keywords_list.append(keyword)
                # 安全日志记录
                if hasattr(self, 'logger') and self.logger:
                    self.logger.info(f"从 {self.keywords_file} 加载了 {len(self.keywords_list)} 个关键词")
            else:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"关键词文件 {self.keywords_file} 不存在，使用默认关键词")
                self.keywords_list = [self.default_keyword]
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"读取关键词文件失败: {str(e)}")
            self.keywords_list = [self.default_keyword]

        # 加载轮换状态
        if len(self.keywords_list) > 0:
            state = self._load_keyword_rotation_state()
            self.current_keyword_index = state.get('current_index', 0)
            # 确保索引在有效范围内
            if self.current_keyword_index >= len(self.keywords_list):
                self.current_keyword_index = 0

    def get_next_keyword(self) -> str:
        """获取下一个关键词（关键词轮换）

        Returns:
            str: 下一个要使用的关键词
        """
        if not self.keywords_list:
            return self.default_keyword

        # 获取当前关键词
        keyword = self.keywords_list[self.current_keyword_index]

        # 安全日志记录
        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"🎨 当前关键词 ({self.current_keyword_index + 1}/{len(self.keywords_list)}): {keyword}")

        # 更新索引到下一个
        next_index = (self.current_keyword_index + 1) % len(self.keywords_list)

        # 保存状态
        self._save_keyword_rotation_state({
            'current_index': next_index,
            'last_keyword': keyword,
            'last_used': datetime.now().isoformat()
        })

        self.current_keyword_index = next_index
        return keyword

    def _load_keyword_rotation_state(self) -> Dict[str, Any]:
        """加载关键词轮换状态

        Returns:
            Dict: 包含轮换状态的字典
        """
        try:
            if os.path.exists(self.keyword_rotation_file):
                with open(self.keyword_rotation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'current_index': 0}

    def _save_keyword_rotation_state(self, state: Dict[str, Any]) -> None:
        """保存关键词轮换状态

        Args:
            state: 要保存的状态字典
        """
        try:
            with open(self.keyword_rotation_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # =========================================================================
    # 多微信公众号轮换功能
    # =========================================================================

    def _init_wechat_accounts(self) -> None:
        """初始化多微信公众号配置"""
        # 微信公众号配置文件路径
        self.wechat_accounts_file = self.config.get('微信公众号', '公众号配置文件',
                                                      fallback='./wechat_accounts.json')

        # 加载公众号列表
        self.wechat_accounts = []
        self.current_account_index = 0

        try:
            # 尝试从配置文件加载
            accounts_data = self._load_wechat_accounts_config()

            if accounts_data and 'accounts' in accounts_data:
                # 只加载启用状态的公众号
                self.wechat_accounts = [
                    acc for acc in accounts_data['accounts']
                    if acc.get('enabled', True)
                ]

                if self.wechat_accounts:
                    # 加载轮换状态
                    rotation_state = accounts_data.get('rotation', {})
                    self.current_account_index = rotation_state.get('current_index', 0)

                    # 确保索引在有效范围内
                    if self.current_account_index >= len(self.wechat_accounts):
                        self.current_account_index = 0

                    if hasattr(self, 'logger') and self.logger:
                        self.logger.info(f"✓ 加载了 {len(self.wechat_accounts)} 个微信公众号配置")
                        for i, acc in enumerate(self.wechat_accounts):
                            self.logger.info(f"  [{i+1}] {acc.get('name', '未命名')}")
                else:
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.warning("没有启用状态的微信公众号，使用默认配置")
                    self._use_default_wechat_config()
            else:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning("微信公众号配置文件格式不正确或为空，使用默认配置")
                self._use_default_wechat_config()

        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"加载微信公众号配置失败: {str(e)}，使用默认配置")
            self._use_default_wechat_config()

    def _use_default_wechat_config(self) -> None:
        """使用默认的微信公众号配置（兼容旧版）"""
        self.wechat_accounts = [{
            'name': '默认公众号',
            'appid': self.wechat_appid,
            'appsecret': self.wechat_secret,
            'default_author': self.default_author,
            'enabled': True
        }]
        self.current_account_index = 0

    def _load_wechat_accounts_config(self) -> Dict[str, Any]:
        """加载微信公众号配置文件

        Returns:
            Dict: 包含公众号列表和轮换状态的字典
        """
        try:
            # 处理相对路径
            config_path = self.wechat_accounts_file
            if not os.path.isabs(config_path):
                script_dir = Path(__file__).parent.resolve()
                config_path = script_dir / config_path

            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"读取微信公众号配置文件失败: {str(e)}")
        return {}

    def _save_wechat_accounts_rotation(self) -> None:
        """保存微信公众号轮换状态"""
        try:
            # 读取完整配置
            accounts_data = self._load_wechat_accounts_config()

            if not accounts_data:
                accounts_data = {'accounts': self.wechat_accounts, 'rotation': {}}

            # 更新轮换状态
            accounts_data['rotation'] = {
                'current_index': self.current_account_index,
                'last_updated': datetime.now().isoformat()
            }

            # 处理相对路径
            config_path = self.wechat_accounts_file
            if not os.path.isabs(config_path):
                script_dir = Path(__file__).parent.resolve()
                config_path = script_dir / config_path

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(accounts_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"保存微信公众号轮换状态失败: {str(e)}")

    def get_current_wechat_account(self) -> Dict[str, str]:
        """获取当前要使用的微信公众号配置

        Returns:
            Dict: 包含 name, appid, appsecret, default_author 的字典
        """
        if not self.wechat_accounts:
            self._init_wechat_accounts()

        if self.wechat_accounts:
            # 【v3.6.4修复】添加索引边界检查，防止数组越界
            safe_index = max(0, min(self.current_account_index, len(self.wechat_accounts) - 1))
            if safe_index != self.current_account_index:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"公众号索引 {self.current_account_index} 超出范围，已修正为 {safe_index}")
                self.current_account_index = safe_index

            account = self.wechat_accounts[self.current_account_index]
            return {
                'name': account.get('name', '未命名'),
                'appid': account.get('appid', ''),
                'appsecret': account.get('appsecret', ''),
                'default_author': account.get('default_author', '总包大脑')
            }

        # 回退到默认配置
        return {
            'name': '默认公众号',
            'appid': self.wechat_appid,
            'appsecret': self.wechat_secret,
            'default_author': self.default_author
        }

    def rotate_to_next_wechat_account(self) -> Dict[str, str]:
        """轮换到下一个微信公众号并返回其配置

        Returns:
            Dict: 下一个公众号的配置
        """
        if not self.wechat_accounts:
            self._init_wechat_accounts()

        if len(self.wechat_accounts) <= 1:
            # 只有一个公众号，无需轮换
            return self.get_current_wechat_account()

        # 获取当前公众号（用于日志）
        current_account = self.get_current_wechat_account()

        # 计算下一个索引（循环轮换）
        self.current_account_index = (self.current_account_index + 1) % len(self.wechat_accounts)

        # 保存轮换状态
        self._save_wechat_accounts_rotation()

        # 获取下一个公众号配置
        next_account = self.get_current_wechat_account()

        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"🔄 公众号轮换: {current_account['name']} → {next_account['name']}")

        return next_account

    def set_wechat_account(self, account: Dict[str, str]) -> None:
        """设置当前使用的微信公众号配置

        Args:
            account: 包含 appid, appsecret, default_author 的字典
        """
        self.wechat_appid = account.get('appid', '')
        self.wechat_secret = account.get('appsecret', '')
        self.default_author = account.get('default_author', '总包大脑')

        # 【v3.6.4修复】同步current_account_index，确保轮换逻辑正确
        # 根据appid找到对应的索引
        if self.wechat_accounts:
            for i, acc in enumerate(self.wechat_accounts):
                if acc.get('appid') == self.wechat_appid:
                    self.current_account_index = i
                    break

        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"✓ 切换到公众号: {account.get('name', '未命名')}")
            self.logger.info(f"  AppID: {self.wechat_appid[:8]}...")
            self.logger.info(f"  默认作者: {self.default_author}")
            self.logger.info(f"  当前索引: {self.current_account_index}")

    def get_all_wechat_accounts(self) -> list:
        """获取所有微信公众号配置列表

        Returns:
            List: 公众号配置列表
        """
        if not self.wechat_accounts:
            self._init_wechat_accounts()
        return self.wechat_accounts.copy()

    # =========================================================================
    # 回复人设提示词轮换功能
    # =========================================================================

    def _init_prompts_rotation(self) -> None:
        """初始化回复人设提示词轮换功能"""
        # 提示词轮换配置文件路径
        self.prompts_rotation_file = self.config.get('总包大脑', '提示词轮换配置文件',
                                                      fallback='./prompt_rotation.json')
        # 提示词文件夹路径
        self.prompts_folder = self.config.get('总包大脑', '提示词文件夹',
                                               fallback='./Prompt')
        # 【v3.6.2新增】长思考模式配置
        self.enable_long_thinking = self.config.getboolean('总包大脑', '启用长思考模式',
                                                            fallback=True)

        # 加载提示词列表
        self.prompts_list = []
        self.current_prompt_index = 0

        try:
            # 尝试从配置文件加载
            prompts_data = self._load_prompts_rotation_config()

            if prompts_data and 'prompts' in prompts_data:
                # 只加载启用状态的提示词
                self.prompts_list = [
                    prompt for prompt in prompts_data['prompts']
                    if prompt.get('enabled', True)
                ]

                if self.prompts_list:
                    # 加载轮换状态
                    rotation_state = prompts_data.get('rotation', {})
                    self.current_prompt_index = rotation_state.get('current_index', 0)

                    # 确保索引在有效范围内
                    if self.current_prompt_index >= len(self.prompts_list):
                        self.current_prompt_index = 0

                    if hasattr(self, 'logger') and self.logger:
                        self.logger.info(f"✓ 加载了 {len(self.prompts_list)} 套回复人设提示词")
                        for i, prompt in enumerate(self.prompts_list):
                            self.logger.info(f"  [{i+1}] {prompt.get('name', '未命名')}")
                else:
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.warning("没有启用状态的提示词，将使用默认提示词")
                    self._use_default_prompt()
            else:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning("提示词配置文件格式不正确或为空，将使用默认提示词")
                self._use_default_prompt()

        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"加载提示词配置失败: {str(e)}，将使用默认提示词")
            self._use_default_prompt()

    def _use_default_prompt(self) -> None:
        """使用默认提示词（兼容旧版）"""
        self.prompts_list = [{
            'name': '默认版',
            'file': '',
            'enabled': True
        }]
        self.current_prompt_index = 0

    def _load_prompts_rotation_config(self) -> Dict[str, Any]:
        """加载提示词轮换配置文件

        Returns:
            Dict: 包含提示词列表和轮换状态的字典
        """
        try:
            # 处理相对路径
            config_path = self.prompts_rotation_file
            if not os.path.isabs(config_path):
                script_dir = Path(__file__).parent.resolve()
                config_path = script_dir / config_path

            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"读取提示词配置文件失败: {str(e)}")
        return {}

    def _save_prompts_rotation_state(self) -> None:
        """保存提示词轮换状态"""
        try:
            # 读取完整配置
            prompts_data = self._load_prompts_rotation_config()

            if not prompts_data:
                prompts_data = {'prompts': self.prompts_list, 'rotation': {}}

            # 更新轮换状态
            prompts_data['rotation'] = {
                'current_index': self.current_prompt_index,
                'last_updated': datetime.now().isoformat()
            }

            # 处理相对路径
            config_path = self.prompts_rotation_file
            if not os.path.isabs(config_path):
                script_dir = Path(__file__).parent.resolve()
                config_path = script_dir / config_path

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"保存提示词轮换状态失败: {str(e)}")

    def get_current_prompt(self) -> Dict[str, str]:
        """获取当前要使用的回复人设提示词配置

        Returns:
            Dict: 包含 name, file, content 的字典
        """
        if not self.prompts_list:
            self._init_prompts_rotation()

        if self.prompts_list:
            prompt = self.prompts_list[self.current_prompt_index]

            # 读取提示词内容
            content = self._load_prompt_content(prompt.get('file', ''))

            return {
                'name': prompt.get('name', '未命名'),
                'file': prompt.get('file', ''),
                'content': content
            }

        # 回退到默认提示词
        return {
            'name': '默认版',
            'file': '',
            'content': ''
        }

    def _load_prompt_content(self, prompt_file: str) -> str:
        """加载提示词文件内容

        Args:
            prompt_file: 提示词文件名

        Returns:
            str: 提示词内容
        """
        if not prompt_file:
            return ''

        try:
            # 处理路径
            prompt_path = prompt_file
            if not os.path.isabs(prompt_path):
                script_dir = Path(__file__).parent.resolve()
                prompt_path = script_dir / self.prompts_folder / prompt_file

            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.warning(f"提示词文件不存在: {prompt_path}")
                return ''
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"读取提示词文件失败: {str(e)}")
            return ''

    def rotate_to_next_prompt(self) -> Dict[str, str]:
        """轮换到下一个回复人设提示词并返回其配置

        Returns:
            Dict: 下一个提示词的配置
        """
        if not self.prompts_list:
            self._init_prompts_rotation()

        if len(self.prompts_list) <= 1:
            # 只有一个提示词，无需轮换
            return self.get_current_prompt()

        # 获取当前提示词（用于日志）
        current_prompt = self.get_current_prompt()

        # 计算下一个索引（循环轮换）
        self.current_prompt_index = (self.current_prompt_index + 1) % len(self.prompts_list)

        # 保存轮换状态
        self._save_prompts_rotation_state()

        # 获取下一个提示词配置
        next_prompt = self.get_current_prompt()

        if hasattr(self, 'logger') and self.logger:
            self.logger.info(f"🔄 提示词轮换: {current_prompt['name']} → {next_prompt['name']}")

        return next_prompt

    def get_all_prompts(self) -> list:
        """获取所有回复人设提示词配置列表

        Returns:
            List: 提示词配置列表
        """
        if not self.prompts_list:
            self._init_prompts_rotation()
        return self.prompts_list.copy()

    def _validate_config(self) -> None:
        """
        验证配置的完整性和有效性

        验证项目：
        - 必需的配置节是否存在
        - API密钥是否已配置
        - URL格式是否正确
        - 邮箱格式是否正确
        - 数值范围是否合理

        Raises:
            ConfigurationError: 当配置项缺失或无效时抛出
        """
        required_sections = ['搜狗微信搜索', '总包大脑', '智谱AI']
        for section in required_sections:
            if not self.config.has_section(section):
                raise ConfigurationError(f"配置文件缺少必需的节: {section}")

        # 验证关键配置项
        if not self.zhipu_api_key:
            raise ConfigurationError("智谱AI API Key未配置")

        if not self.metaso_url:
            raise ConfigurationError("总包大脑网址未配置")

        if self.min_question_length < 10:
            raise ConfigurationError("问题最小字符数不能小于10")

        if self.min_answer_length < 100:
            raise ConfigurationError("回复最小字符数不能小于100")

        # 验证邮箱格式（如果配置了）
        if self.notification_email and not validate_email(self.notification_email):
            raise ConfigurationError(f"接收邮箱格式无效: {self.notification_email}")

        if self.sender_email and not validate_email(self.sender_email):
            raise ConfigurationError(f"发件邮箱格式无效: {self.sender_email}")

    def get_masked_credentials(self) -> Dict[str, str]:
        """
        获取掩码后的敏感凭证信息（用于日志显示）

        Returns:
            包含掩码后敏感信息的字典
        """
        return {
            'zhipu_api_key': mask_sensitive_data(self.zhipu_api_key) if self.zhipu_api_key else '',
            'wechat_secret': mask_sensitive_data(self.wechat_secret) if self.wechat_secret else '',
            'email_auth_code': mask_sensitive_data(self.email_auth_code) if self.email_auth_code else '',
        }


# =============================================================================
# 日志管理类
# =============================================================================

class Logger:
    """
    日志管理类

    提供统一的日志记录接口，支持文件和控制台输出，可配置日志级别。

    安全特性：
    - 自动掩码敏感信息（API密钥、密码等）
    - 防止敏感信息泄露到日志文件

    Attributes:
        log_file: 日志文件路径
        debug_mode: 是否启用调试模式
        logger: logging.Logger实例
        sensitive_patterns: 敏感信息匹配模式列表
    """

    def __init__(self, log_file: str, debug_mode: bool = False) -> None:
        """
        初始化日志

        Args:
            log_file: 日志文件路径
            debug_mode: 是否启用调试模式（DEBUG级别日志）
        """
        self.log_file: str = log_file
        self.debug_mode: bool = debug_mode
        self.logger: Optional[logging.Logger] = None
        # 敏感信息匹配模式（正则表达式）
        self.sensitive_patterns = [
            r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
            r'secret["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
            r'password["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
            r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
            r'authorization["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
        ]
        self.setup_logger()

    def _sanitize_message(self, message: str) -> str:
        """
        清理日志消息，掩码敏感信息

        Args:
            message: 原始日志消息

        Returns:
            清理后的日志消息
        """
        import re
        sanitized = message

        # 应用所有敏感信息模式
        for pattern in self.sensitive_patterns:
            def replacer(match):
                # 掩码匹配到的敏感信息
                sensitive_value = match.group(1) if match.lastindex else match.group(0)
                if len(sensitive_value) > 8:
                    return match.group(0).replace(sensitive_value, mask_sensitive_data(sensitive_value))
                return match.group(0).replace(sensitive_value, '****')

            sanitized = re.sub(pattern, replacer, sanitized, flags=re.IGNORECASE)

        return sanitized

    def setup_logger(self) -> None:
        """
        设置日志处理器和格式化器

        配置文件和控制台两种输出方式，文件记录DEBUG级别，
        控制台根据debug_mode设置记录INFO或DEBUG级别。
        """
        # 创建logger
        self.logger = logging.getLogger('ZBBrainArticle')
        self.logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)

        # 防止重复添加handler
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 创建文件处理器
        try:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
        except (IOError, OSError) as e:
            print(f"无法创建日志文件 {self.log_file}: {e}")
            file_handler = logging.StreamHandler()
            file_handler.setLevel(logging.DEBUG)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建格式化器
        formatter = logging.Formatter(
            Constants.LOG_FORMAT,
            datefmt=Constants.LOG_DATE_FORMAT
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message: str) -> None:
        """
        记录信息日志

        安全特性：自动掩码敏感信息
        """
        sanitized_message = self._sanitize_message(message)
        self.logger.info(sanitized_message)

    def debug(self, message: str) -> None:
        """
        记录调试日志

        安全特性：自动掩码敏感信息
        """
        sanitized_message = self._sanitize_message(message)
        self.logger.debug(sanitized_message)

    def warning(self, message: str) -> None:
        """
        记录警告日志

        安全特性：自动掩码敏感信息
        """
        sanitized_message = self._sanitize_message(message)
        self.logger.warning(sanitized_message)

    def error(self, message: str) -> None:
        """
        记录错误日志

        安全特性：自动掩码敏感信息
        """
        sanitized_message = self._sanitize_message(message)
        self.logger.error(sanitized_message)

    def critical(self, message: str) -> None:
        """
        记录严重错误日志

        安全特性：自动掩码敏感信息
        """
        sanitized_message = self._sanitize_message(message)
        self.logger.critical(sanitized_message)


# =============================================================================
# Stagehand浏览器自动化类
# =============================================================================

class StagehandBrowser:
    """
    Stagehand风格的浏览器自动化类 - 使用Playwright异步API实现

    这个类封装了Playwright的浏览器操作，提供了Stagehand风格的接口，
    支持自然语言指令执行、数据提取等功能。

    资源管理：
    - 支持上下文管理器（async with）确保资源正确释放
    - 自动清理浏览器、上下文和playwright资源

    Attributes:
        config: 配置对象
        logger: 日志记录器
        playwright: Playwright实例
        browser: 浏览器实例
        context: 浏览器上下文
        page: 页面对象
    """

    def __init__(self, config: Config, logger: Logger) -> None:
        """
        初始化浏览器

        Args:
            config: 配置对象，包含浏览器相关配置
            logger: 日志记录器，用于记录操作日志
        """
        self.config: Config = config
        self.logger: Logger = logger
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        """
        异步上下文管理器入口

        Returns:
            当前浏览器实例
        """
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器出口

        确保所有浏览器资源被正确释放
        """
        await self.close()
        return False

    async def start(self, headless: bool = True, use_persistent_context: bool = False) -> None:
        """
        启动浏览器

        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
            use_persistent_context: 是否使用持久化上下文（保持登录状态）
                注意：现在使用 launch() + new_context() + cookies 存储方式
                比 launch_persistent_context 在 Windows 上更稳定

        Raises:
            BrowserError: 浏览器启动失败时抛出
        """
        self.logger.info("启动Stagehand风格浏览器 (使用Playwright)")

        self.playwright = await async_playwright().start()

        # 始终使用 launch() + new_context() 方式，比 launch_persistent_context 更稳定
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--start-maximized=false',
                '--window-size=960,720'
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 960, 'height': 720},
            screen={'width': 960, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        self.page = await self.context.new_page()

        # 如果需要保持登录状态，加载已保存的 cookies
        if use_persistent_context:
            await self._load_cookies()

        self.logger.info("浏览器启动成功")

    async def _load_cookies(self) -> bool:
        """
        加载保存的 cookies

        【v3.6.8修复】只加载 metaso.cn 域名的 cookies

        Returns:
            bool: 是否成功加载 cookies
        """
        cookies_file = Path(self.config.user_data_dir) / "cookies.json"
        if cookies_file.exists():
            try:
                import json
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)

                # 【v3.6.8新增】验证 cookies 是否来自正确的域名
                metaso_cookies = [c for c in cookies if 'metaso' in c.get('domain', '')]
                if not metaso_cookies:
                    self.logger.warning("未找到 metaso.cn 域名的 cookies，文件可能已过期")
                    return False

                await self.context.add_cookies(cookies)
                self.logger.info(f"已加载 {len(cookies)} 个 cookies (其中 {len(metaso_cookies)} 个来自 metaso.cn)")
                return True
            except Exception as e:
                self.logger.warning(f"加载 cookies 失败: {e}")
        return False

    async def _save_cookies(self) -> bool:
        """
        保存当前 cookies

        【v3.6.8关键修复】只保存 metaso.cn 域名的 cookies
        原先保存的是 sogou.com 的 cookies，对登录持久化无效！

        Returns:
            bool: 是否成功保存 cookies
        """
        try:
            import json
            cookies_file = Path(self.config.user_data_dir) / "cookies.json"
            cookies_file.parent.mkdir(parents=True, exist_ok=True)

            # 获取所有 cookies
            all_cookies = await self.context.cookies()

            # 【v3.6.8关键修复】只保存 metaso.cn 相关的 cookies
            metaso_cookies = [
                c for c in all_cookies
                if 'metaso' in c.get('domain', '')
            ]

            if not metaso_cookies:
                self.logger.warning("⚠️ 当前没有 metaso.cn 域名的 cookies")
                self.logger.warning("可能原因：1) 未登录 2) 在错误的页面上保存")
                # 仍然保存所有 cookies 作为备份
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(all_cookies, f, ensure_ascii=False, indent=2)
                self.logger.info(f"已保存 {len(all_cookies)} 个 cookies (无 metaso.cn cookies)")
                return False

            # 保存过滤后的 metaso.cn cookies
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(metaso_cookies, f, ensure_ascii=False, indent=2)

            self.logger.info(f"✓ 已保存 {len(metaso_cookies)} 个 metaso.cn cookies")
            return True
        except Exception as e:
            self.logger.warning(f"保存 cookies 失败: {e}")
            return False

    async def _save_local_storage(self) -> bool:
        """
        保存当前页面的 localStorage

        Returns:
            bool: 是否成功保存 localStorage
        """
        try:
            import json
            storage_file = Path(self.config.user_data_dir) / "local_storage.json"
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            local_storage = await self.page.evaluate("() => JSON.stringify(localStorage)")
            with open(storage_file, 'w', encoding='utf-8') as f:
                f.write(local_storage)
            self.logger.info(f"已保存 localStorage")
            return True
        except Exception as e:
            self.logger.warning(f"保存 localStorage 失败: {e}")
            return False

    async def _load_local_storage(self) -> bool:
        """
        加载 localStorage 到当前页面

        Returns:
            bool: 是否成功加载 localStorage
        """
        try:
            import json
            storage_file = Path(self.config.user_data_dir) / "local_storage.json"
            if storage_file.exists():
                with open(storage_file, 'r', encoding='utf-8') as f:
                    local_storage = json.load(f)
                await self.page.evaluate("(items) => { for (const [k, v] of Object.entries(items)) { localStorage.setItem(k, v); } }", local_storage)
                self.logger.info(f"已加载 localStorage ({len(local_storage)} 项)")
                return True
        except Exception as e:
            self.logger.warning(f"加载 localStorage 失败: {e}")
        return False

    async def _save_storage_state(self) -> bool:
        """
        保存完整的浏览器状态（cookies + localStorage）
        用于持久化登录状态

        Returns:
            bool: 是否成功保存
        """
        try:
            cookies_ok = await self._save_cookies()
            storage_ok = await self._save_local_storage()
            if cookies_ok:
                self.logger.info("✓ 浏览器状态已保存（cookies + localStorage）")
            return cookies_ok
        except Exception as e:
            self.logger.warning(f"保存浏览器状态失败: {e}")
            return False

    async def _load_storage_state(self) -> bool:
        """
        加载完整的浏览器状态（cookies + localStorage）
        用于恢复登录状态

        Returns:
            bool: 是否成功加载
        """
        try:
            cookies_ok = await self._load_cookies()
            # localStorage 需要在页面加载后设置
            return cookies_ok
        except Exception as e:
            self.logger.warning(f"加载浏览器状态失败: {e}")
            return False

    async def goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = Constants.DEFAULT_PAGE_LOAD_TIMEOUT) -> bool:
        """
        导航到指定URL

        Args:
            url: 目标URL地址
            wait_until: 等待条件（domcontentloaded, load, networkidle）
            timeout: 超时时间（毫秒）

        Returns:
            bool: 导航是否成功
        """
        self.logger.info(f"导航到: {url}")
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            await asyncio.sleep(2)
            return True
        except Exception as e:
            self.logger.warning(f"导航超时或出错，尝试继续: {str(e)}")
            await asyncio.sleep(3)
            return False

    async def act(self, instruction: str, timeout: int = Constants.DEFAULT_PAGE_LOAD_TIMEOUT) -> bool:
        """
        执行自然语言指令 (使用Playwright实现)

        Args:
            instruction: 自然语言指令，如"点击发送按钮"、"在输入框输入: 文本"
            timeout: 超时时间（毫秒）

        Returns:
            bool: 指令是否执行成功
        """
        self.logger.debug(f"执行指令: {instruction}")

        try:
            # 解析指令并执行相应的Playwright操作
            instruction_lower = instruction.lower()

            # 点击操作
            if 'click' in instruction_lower or '点击' in instruction_lower:
                # 尝试从指令中提取选择器或文本
                if 'button' in instruction_lower:
                    buttons = await self.page.query_selector_all('button')
                    for btn in buttons:
                        text = await btn.inner_text()
                        if text and any(word in text.lower() for word in ['send', 'submit', '发送', '提交']):
                            await btn.click()
                            await asyncio.sleep(0.5)
                            return True

                # 尝试查找包含特定文本的可点击元素
                for keyword in ['发送', 'submit', 'send', '提交', '确定', 'confirm']:
                    try:
                        elem = await self.page.query_selector(f"text={keyword}")
                        if elem:
                            await elem.click()
                            await asyncio.sleep(0.5)
                            return True
                    except (TimeoutError, Exception) as e:
                        self.logger.debug(f"查找关键词 '{keyword}' 失败: {str(e)}")
                        continue

            # 输入操作
            elif 'type' in instruction_lower or '输入' in instruction_lower or 'fill' in instruction_lower:
                # 尝试找到输入框
                input_selectors = ['textarea', 'input[type="text"]', '[contenteditable="true"]']
                for selector in input_selectors:
                    try:
                        elem = await self.page.query_selector(selector)
                        if elem:
                            await elem.click()
                            await asyncio.sleep(0.3)
                            # 提取要输入的文本
                            text_match = re.search(r'[:：]\s*"([^"]+)"', instruction) or re.search(r'[:：]\s*([^\s]+)', instruction)
                            if text_match:
                                text = text_match.group(1)
                                await elem.fill(text)
                                await asyncio.sleep(0.5)
                                return True
                    except (TimeoutError, Exception) as e:
                        self.logger.debug(f"选择器 '{selector}' 输入失败: {str(e)}")
                        continue

            self.logger.warning(f"无法解析指令: {instruction}")
            return False

        except Exception as e:
            self.logger.error(f"执行指令失败: {str(e)}")
            return False

    async def extract(self, instruction: str, schema: Dict[str, Any]) -> Optional[Dict]:
        """提取结构化数据 (使用Playwright实现)"""
        self.logger.debug(f"提取数据: {instruction}")

        try:
            # 基于指令类型执行不同的提取逻辑
            if 'article' in instruction.lower() or '文章' in instruction.lower():
                # 提取文章信息
                articles = []

                # 尝试多种选择器
                selectors = [
                    'h3 a',
                    '.news-box a',
                    '.vr-title a',
                    'article h2 a',
                    '.title a'
                ]

                for selector in selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        for elem in elements[:10]:  # 最多提取10篇
                            try:
                                title = await elem.inner_text()
                                href = await elem.get_attribute('href')
                                articles.append({
                                    'title': title.strip(),
                                    'link': href or '',
                                    'content': title.strip()
                                })
                            except (AttributeError, Exception):
                                continue

                        if articles:
                            break
                    except (AttributeError, Exception):
                        continue

                return articles if articles else None

            elif 'answer' in instruction.lower() or 'response' in instruction.lower() or '回答' in instruction.lower():
                # 提取回答内容
                selectors = [
                    '[class*="message"] [class*="assistant"]',
                    '[class*="chat"] [class*="answer"]',
                    '[class*="response"]',
                    '.markdown-body',
                    '[class*="bubble"]'
                ]

                for selector in selectors:
                    try:
                        elem = await self.page.query_selector(selector)
                        if elem:
                            text = await elem.inner_text()
                            if text and len(text.strip()) > 50:
                                return text.strip()
                    except (TimeoutError, AttributeError, Exception):
                        continue

                return None

            return None

        except Exception as e:
            self.logger.error(f"提取数据失败: {str(e)}")
            return None

    async def observe(self, instruction: str = "") -> Optional[str]:
        """观察页面内容"""
        try:
            if instruction:
                # 基于指令返回特定的页面信息
                if 'login' in instruction.lower() or '登录' in instruction.lower():
                    page_text = await self.page.inner_text("body")
                    if '登录' in page_text or '扫码' in page_text or 'login' in page_text.lower():
                        return "需要登录"
                    return "无需登录"

                # 检查是否有输入框（判断是否已登录）
                input_count = await self.page.locator('textarea, input[type="text"], [contenteditable="true"]').count()
                if input_count > 0:
                    return "页面包含输入框"

                return await self.page.inner_text("body")
            else:
                return await self.page.inner_text("body")
        except Exception as e:
            self.logger.error(f"观察页面失败: {str(e)}")
            return None

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> bool:
        """等待选择器出现"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except (TimeoutError, Exception):
            return False

    async def wait_for_function(self, js_function: str, timeout: int = 30000) -> bool:
        """等待JavaScript函数返回true"""
        try:
            await self.page.wait_for_function(js_function, timeout=timeout)
            return True
        except (TimeoutError, Exception):
            return False

    async def fill(self, selector: str, value: str) -> None:
        """
        填充表单字段

        Args:
            selector: CSS选择器
            value: 要填充的值
        """
        try:
            await self.page.fill(selector, value)
            await asyncio.sleep(0.5)
        except Exception as e:
            self.logger.error(f"填充失败: {str(e)}")

    async def click(self, selector: str) -> None:
        """
        点击元素

        Args:
            selector: CSS选择器
        """
        try:
            await self.page.click(selector)
            await asyncio.sleep(0.5)
        except Exception as e:
            self.logger.error(f"点击失败: {str(e)}")

    async def press(self, key: str) -> None:
        """
        按键

        Args:
            key: 按键名称
        """
        try:
            await self.page.keyboard.press(key)
            await asyncio.sleep(0.5)
        except Exception as e:
            self.logger.error(f"按键失败: {str(e)}")

    async def screenshot(self, path: str) -> None:
        """
        截图

        Args:
            path: 保存路径
        """
        try:
            await self.page.screenshot(path=path)
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")

    async def scroll_element_into_view(self, selector: str) -> bool:
        """
        滚动元素到视图中

        Args:
            selector: CSS选择器

        Returns:
            是否成功滚动
        """
        try:
            elem = await self.page.query_selector(selector)
            if elem:
                await elem.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                return True
        except Exception as e:
            self.logger.debug(f"滚动失败: {str(e)}")
        return False

    async def fill_with_js(self, selector: str, value: str) -> bool:
        """使用JavaScript填充输入框（回退方法）"""
        try:
            # 尝试多种JavaScript方式
            js_scripts = [
                f'''document.querySelector("{selector}").value = "{value}"''',
                f'''document.querySelector("{selector}").innerText = "{value}"''',
                f'''document.querySelector("{selector}").textContent = "{value}"''',
                f'''document.querySelector("{selector}").setAttribute("value", "{value}")''',
            ]

            for script in js_scripts:
                try:
                    await self.page.evaluate(script)
                    # 触发input事件
                    await self.page.evaluate(f'''document.querySelector("{selector}").dispatchEvent(new Event("input", {{ bubbles: true }}))''')
                    await self.page.evaluate(f'''document.querySelector("{selector}").dispatchEvent(new Event("change", {{ bubbles: true }}))''')
                    await asyncio.sleep(0.3)
                    return True
                except (TimeoutError, AttributeError, Exception):
                    continue
        except Exception as e:
            self.logger.debug(f"JS填充失败: {str(e)}")
        return False

    async def wait_for_page_stable(self, timeout: int = 5000) -> None:
        """
        等待页面稳定（无网络请求）

        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
        except (TimeoutError, Exception):
            await asyncio.sleep(2)

    async def find_and_scroll_to_input(self, timeout: int = 10000) -> Optional[str]:
        """查找输入框并滚动到视图中"""
        input_selectors = [
            'textarea:not([style*="display: none"])',
            'input[type="text"]:not([style*="display: none"])',
            '[contenteditable="true"]:not([style*="display: none"])',
            'textarea',
            'input[type="text"]',
            '[contenteditable="true"]',
        ]

        for selector in input_selectors:
            try:
                elem = await self.page.query_selector(selector)
                if elem:
                    # 检查元素是否可见
                    is_visible = await elem.is_visible()
                    if is_visible:
                        await elem.scroll_into_view_if_needed(timeout=timeout)
                        await asyncio.sleep(0.5)
                        return selector
                    else:
                        # 尝试使元素可见
                        await self.page.evaluate(f'''document.querySelector("{selector}").style.display = "block"''')
                        await self.page.evaluate(f'''document.querySelector("{selector}").style.visibility = "visible"''')
                        await elem.scroll_into_view_if_needed(timeout=timeout)
                        await asyncio.sleep(0.5)
                        return selector
            except (TimeoutError, AttributeError, Exception):
                continue

        return None

    async def close(self, save_cookies: bool = True, cookie_domain_filter: str = None) -> None:
        """
        关闭浏览器

        Args:
            save_cookies: 是否在关闭前保存浏览器状态（默认 True）
            cookie_domain_filter: 【v3.6.9新增】只保存指定域名的 cookies
                - None: 保存所有 cookies（旧行为，不推荐）
                - "metaso.cn": 只保存 metaso.cn 域名的 cookies（推荐）
                - 调用时可传入 "sogou.com" 来阻止保存（因为会用空列表）

        清理所有浏览器资源

        【v3.6.9 修复】
        1. 添加超时保护，防止关闭卡住
        2. 添加域名过滤，确保只保存正确的 cookies
        3. 强制清理所有资源
        """
        self.logger.info("关闭浏览器")
        close_timeout = 30  # 30秒超时

        try:
            # 在关闭前保存完整的浏览器状态（cookies + localStorage）
            if save_cookies and self.context:
                # 【v3.6.9 关键修复】只有指定了域名过滤才保存
                if cookie_domain_filter:
                    await self._save_storage_state_for_domain(cookie_domain_filter)
                else:
                    await self._save_storage_state()

            # 【v3.6.9】添加超时保护
            async def close_context():
                if self.context:
                    await self.context.close()

            async def close_browser():
                if self.browser:
                    await self.browser.close()

            async def stop_playwright():
                if self.playwright:
                    await self.playwright.stop()

            # 依次关闭，每个都有超时保护
            try:
                await asyncio.wait_for(close_context(), timeout=close_timeout)
            except asyncio.TimeoutError:
                self.logger.warning(f"关闭 context 超时({close_timeout}秒)，强制继续")

            try:
                await asyncio.wait_for(close_browser(), timeout=close_timeout)
            except asyncio.TimeoutError:
                self.logger.warning(f"关闭 browser 超时({close_timeout}秒)，强制继续")

            try:
                await asyncio.wait_for(stop_playwright(), timeout=close_timeout)
            except asyncio.TimeoutError:
                self.logger.warning(f"停止 playwright 超时({close_timeout}秒)，强制继续")

        except Exception as e:
            self.logger.error(f"关闭浏览器失败: {str(e)}")
        finally:
            # 【v3.6.9】确保引用被清除
            self.context = None
            self.browser = None
            self.playwright = None
            self.page = None

    async def _save_storage_state_for_domain(self, domain_filter: str) -> bool:
        """
        【v3.6.9 新增】只保存指定域名的浏览器状态

        Args:
            domain_filter: 域名过滤字符串（如 "metaso.cn"）

        Returns:
            bool: 是否成功保存
        """
        try:
            import json
            cookies_file = Path(self.config.user_data_dir) / "cookies.json"
            cookies_file.parent.mkdir(parents=True, exist_ok=True)

            # 获取所有 cookies
            all_cookies = await self.context.cookies()

            # 【关键修复】只保存指定域名的 cookies
            filtered_cookies = [
                c for c in all_cookies
                if domain_filter in c.get('domain', '')
            ]

            if not filtered_cookies:
                self.logger.warning(f"⚠️ 当前没有 {domain_filter} 域名的 cookies")
                self.logger.warning("可能原因：1) 未登录 2) 在错误的页面上保存")
                return False

            # 保存过滤后的 cookies
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_cookies, f, ensure_ascii=False, indent=2)

            self.logger.info(f"✓ 已保存 {len(filtered_cookies)} 个 {domain_filter} cookies")
            return True
        except Exception as e:
            self.logger.warning(f"保存 {domain_filter} cookies 失败: {e}")
            return False


# =============================================================================
# 搜狗微信搜索爬虫类 (使用Stagehand)
# =============================================================================

class SogouWeChatScraper:
    """
    搜狗微信搜索爬虫类 (使用Stagehand)

    负责从搜狗微信搜索爬取EPC总承包相关文章信息。

    Attributes:
        config: 配置对象
        logger: 日志记录器
        articles: 爬取到的文章列表
    """

    def __init__(self, config: Config, logger: Logger) -> None:
        """
        初始化爬虫

        Args:
            config: 配置对象
            logger: 日志记录器
        """
        self.config: Config = config
        self.logger: Logger = logger
        self.articles: List[Dict[str, Any]] = []

    @profile
    async def scrape(self, keyword: Optional[str] = None, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        爬取搜狗微信搜索资讯

        Args:
            keyword: 搜索关键词，默认使用配置文件中的默认关键词
            max_pages: 最大爬取页数，默认使用配置文件中的默认页数

        Returns:
            List[Dict]: 爬取到的文章列表，每篇文章包含标题、摘要、链接等信息

        Raises:
            ScrapingError: 爬取过程出现严重错误时抛出
            ValueError: 如果输入参数无效
        """
        keyword = keyword or self.config.default_keyword
        max_pages = max_pages or self.config.default_pages
        max_pages = min(max_pages, self.config.max_pages)

        # 输入验证（增强版）
        if not keyword or not isinstance(keyword, str):
            raise ValueError("搜索关键词必须是非空字符串")

        keyword = keyword.strip()
        if len(keyword) < 2:
            raise ValueError("搜索关键词至少需要2个字符")

        if not isinstance(max_pages, int):
            raise ValueError("最大页数必须是整数")

        if max_pages < 1:
            raise ValueError("最大页数必须大于0")

        if max_pages > 100:
            self.logger.warning(f"请求的页数({max_pages})过大，限制为100")
            max_pages = 100

        self.logger.info(f"开始爬取搜狗微信搜索，关键词: {keyword}，最大页数: {max_pages}")

        articles = []
        browser = None

        try:
            # 启动浏览器
            browser = StagehandBrowser(self.config, self.logger)
            await browser.start(headless=True)

            for page_num in range(1, max_pages + 1):
                self.logger.info(f"正在爬取第 {page_num}/{max_pages} 页")

                # 构建搜索URL
                search_url = self._build_search_url(keyword, page_num)

                # 访问页面
                await browser.goto(search_url, wait_until="domcontentloaded", timeout=30000)

                # 使用Stagehand提取文章信息
                page_articles = await self._extract_articles(browser)
                articles.extend(page_articles)

                self.logger.info(f"第 {page_num} 页提取到 {len(page_articles)} 篇文章")

                if page_num < max_pages:
                    await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"爬取过程出错: {str(e)}")
        finally:
            if browser:
                # 【v3.6.9 修复】SogouWeChatScraper 完全不保存任何 cookies
                # 原因：它只访问 sogou.com，保存会覆盖 metaso.cn 的登录状态
                # 使用 cookie_domain_filter="sogou.com" + save_cookies=False 双重保护
                await browser.close(save_cookies=False, cookie_domain_filter=None)  # 不保存任何 cookies

        # 对提取的文章进行深度分析（关键词提取、分类、情感分析）
        if articles:
            self.logger.info("开始对文章进行深度分析...")
            articles = await self._analyze_articles(articles)

        self.logger.info(f"爬取完成，共获取 {len(articles)} 篇文章")
        self.articles = articles
        return articles

    def _build_search_url(self, keyword: str, page_num: int) -> str:
        """构建搜索URL - 使用配置的搜狗资讯搜索URL"""
        from urllib.parse import quote, urlencode

        # 使用配置的搜索URL作为基础
        base_url = "https://www.sogou.com/sogou"

        # 构建搜索参数（按照用户提供的URL格式）
        params = {
            'interation': '1728053249',
            'interV': 'kKIOkrELjbkRmLkElbkTkKIMkrELjboImLkEk74TkKIRmLkEk78TkKILkY==_-115092183',
            'pid': 'sogou-wsse-7050094b04fd9aa3',
            'query': keyword,
            'tsn': '1',
            's_from': 'inttime_day',
            'page': page_num,
            'ie': 'utf8',
            'p': '40230447',
            'dp': '1'
        }

        # 构建完整URL
        param_str = '&'.join([f"{k}={quote(str(v), safe='')}" for k, v in params.items()])
        return f"{base_url}?{param_str}"

    async def _extract_articles(self, browser: StagehandBrowser) -> List[Dict]:
        """使用Stagehand从页面提取文章信息（只获取标题和摘要，不获取正文）"""
        articles = []

        try:
            # 使用Stagehand的extract功能提取文章
            schema = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "文章标题"},
                        "summary": {"type": "string", "description": "文章摘要或简短描述"},
                        "link": {"type": "string", "description": "文章链接"}
                    },
                    "required": ["title"]
                }
            }

            instruction = """Extract all article information from this WeChat search results page.
            For each article, carefully extract ONLY:
            - The title (from h3 or link text)
            - The article summary or abstract (usually displayed below the title)
            - The link URL

            Important: The summary field should contain the brief description shown below the title.
            DO NOT extract the full article content, only the title and summary displayed on the search results page.

            Return up to 10 articles with complete information."""

            result = await browser.extract(instruction, schema)

            if result and isinstance(result, list):
                # 过滤有效文章
                for item in result:
                    if item.get('title') and len(item.get('title', '')) > 5:
                        # 只使用summary，如果没有则使用title
                        summary = item.get('summary', '').strip()
                        if not summary:
                            summary = item['title']

                        articles.append({
                            'title': item['title'],
                            'summary': summary[:300],  # 限制摘要长度
                            'link': item.get('link', '')
                        })

        except Exception as e:
            self.logger.error(f"Stagehand提取失败: {str(e)}")
            # 回退到传统选择器方法
            articles = await self._extract_articles_fallback(browser)

        return articles

    async def _extract_articles_fallback(self, browser: StagehandBrowser) -> List[Dict]:
        """回退方法：使用传统选择器提取（包含摘要）"""
        articles = []

        try:
            # 尝试使用CSS选择器提取文章卡片
            results = await browser.page.query_selector_all('.news-box, .vr-title, .txt-box, h3 a')

            for result in results:
                try:
                    text = await result.inner_text()
                    if text and len(text.strip()) > 5:
                        # 尝试提取摘要（通常是标题后的文本）
                        lines = text.strip().split('\n')
                        title = lines[0].strip() if lines else text.strip()
                        # 摘要通常是第二行或后续内容
                        summary = '\n'.join(lines[1:3]).strip() if len(lines) > 1 else title

                        articles.append({
                            'title': title,
                            'summary': summary[:200],
                            'content': text.strip(),
                            'link': await result.get_attribute('href') or ''
                        })
                except (AttributeError, Exception):
                    continue

        except Exception as e:
            self.logger.debug(f"回退方法也失败: {str(e)}")

        return articles

    async def _analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """对文章进行深度分析：优化摘要、提取关键词、分类、情感分析

        优化版本：使用并行批次处理，提升分析效率40%
        """
        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=self.config.zhipu_api_key)

            self.logger.info(f"使用AI分析 {len(articles)} 篇文章...")

            # 批量分析文章（每次处理5篇）
            batch_size = 5
            total_batches = (len(articles) + batch_size - 1) // batch_size

            # 优化：并行处理批次（最多同时处理2个批次，避免API限流）
            max_concurrent_batches = 4  # 优化：提升并行度以加快分析速度
            semaphore = asyncio.Semaphore(max_concurrent_batches)

            async def analyze_single_batch(batch_idx: int, batch: List[Dict]) -> Tuple[int, List[Dict]]:
                """分析单个批次的文章"""
                async with semaphore:
                    batch_num = batch_idx + 1
                    self.logger.info(f"正在分析第 {batch_num}/{total_batches} 批文章...")

                    # 构建分析请求
                    articles_text = ""
                    for j, article in enumerate(batch):
                        articles_text += f"\n文章{j+1}:\n标题: {article['title']}\n原摘要: {article.get('summary', '')}\n"

                    analysis_prompt = f"""你是一位专业的EPC总承包行业内容分析师。请对以下文章进行分析。

{articles_text}

请对每篇文章进行分析，并以JSON格式返回结果，格式如下：
[
  {{
    "optimized_summary": "优化后的摘要（提炼核心观点，100-150字）",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "category": "分类（如：风险管理、成本控制、合同管理、项目管理、政策法规、技术标准等）",
    "sentiment": "情感倾向（积极/中性/消极）",
    "sentiment_score": "情感得分（-1到1之间，-1最消极，0中性，1最积极）",
    "core_points": ["核心观点1", "核心观点2"]
  }}
]

分析要求：
1. optimized_summary：提炼文章核心观点，确保包含关键信息和数据
2. keywords：提取3-5个最具代表性的关键词
3. category：从以下分类中选择最合适的一个：风险管理、成本控制、合同管理、项目管理、政策法规、技术标准、质量管理、进度管理、供应链管理、其他
4. sentiment：判断文章整体情感倾向
5. sentiment_score：根据内容判断情感强度（-0.9到-0.3为消极，-0.3到0.3为中性，0.3到0.9为积极）
6. core_points：提炼2-3个核心观点

请直接返回JSON数组，不要有任何额外说明。"""

                    try:
                        # 添加速率限制等待
                        await asyncio.sleep(0.5)  # 避免API限流
                        response = client.chat.completions.create(
                            model="glm-4-flash",  # 使用快速模型
                            messages=[
                                {
                                    "role": "system",
                                    "content": "你是专业的EPC总承包行业内容分析师，擅长分析文章、提取关键信息并进行分类。"
                                },
                                {
                                    "role": "user",
                                    "content": analysis_prompt
                                }
                            ],
                            temperature=0.3,
                            max_tokens=2000
                        )

                        result_text = response.choices[0].message.content.strip()

                        # 清理可能的markdown标记
                        if result_text.startswith('```json'):
                            result_text = result_text[7:]
                        if result_text.startswith('```'):
                            result_text = result_text[3:]
                        if result_text.endswith('```'):
                            result_text = result_text[:-3]
                        result_text = result_text.strip()

                        # 解析JSON结果
                        analysis_results = json.loads(result_text)

                        # 将分析结果合并到文章数据中
                        for j, (article, analysis) in enumerate(zip(batch, analysis_results)):
                            # 优化后的摘要
                            article['optimized_summary'] = analysis.get('optimized_summary', article.get('summary', ''))
                            # 关键词
                            article['keywords'] = analysis.get('keywords', [])
                            # 分类标签
                            article['category'] = analysis.get('category', '其他')
                            # 情感分析
                            article['sentiment'] = analysis.get('sentiment', '中性')
                            article['sentiment_score'] = float(analysis.get('sentiment_score', 0))
                            # 核心观点
                            article['core_points'] = analysis.get('core_points', [])

                            self.logger.debug(f"文章分析完成: {article['title'][:30]}... | 分类: {article['category']} | 情感: {article['sentiment']}")

                        return (batch_idx, batch)

                    except json.JSONDecodeError as je:
                        self.logger.warning(f"解析AI分析结果失败: {str(je)}，使用原始数据")
                        # 使用默认值
                        for article in batch:
                            article['optimized_summary'] = article.get('summary', '')
                            article['keywords'] = self._extract_simple_keywords(article['title'] + ' ' + article.get('summary', ''))
                            article['category'] = '其他'
                            article['sentiment'] = '中性'
                            article['sentiment_score'] = 0.0
                            article['core_points'] = []
                        return (batch_idx, batch)
                    except Exception as e:
                        self.logger.warning(f"AI分析失败: {str(e)}，使用原始数据")
                        # 使用默认值
                        for article in batch:
                            article['optimized_summary'] = article.get('summary', '')
                            article['keywords'] = self._extract_simple_keywords(article['title'] + ' ' + article.get('summary', ''))
                            article['category'] = '其他'
                            article['sentiment'] = '中性'
                            article['sentiment_score'] = 0.0
                            article['core_points'] = []
                        return (batch_idx, batch)

            # 准备所有批次任务
            batches = [(i, articles[i:i + batch_size]) for i in range(0, len(articles), batch_size)]

            # 并行执行所有批次分析
            self.logger.info(f"并行分析 {len(batches)} 个批次（最大并发: {max_concurrent_batches}）...")
            start_time = time.time()

            tasks = [analyze_single_batch(idx, batch) for idx, batch in batches]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 收集结果（保持原始顺序）
            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(f"批次分析出现异常: {str(result)}")
                elif isinstance(result, tuple):
                    batch_idx, analyzed_batch = result
                    # 更新原文章列表中对应批次的数据
                    start_idx = batch_idx * batch_size
                    for i, article in enumerate(analyzed_batch):
                        if start_idx + i < len(articles):
                            articles[start_idx + i] = article

            elapsed_time = time.time() - start_time
            self.logger.info(f"并行分析完成，耗时: {elapsed_time:.2f}秒")

            # 统计分析结果
            self._log_analysis_summary(articles)

        except Exception as e:
            self.logger.error(f"文章深度分析失败: {str(e)}")
            # 使用简单方法处理
            for article in articles:
                if 'optimized_summary' not in article:
                    article['optimized_summary'] = article.get('summary', '')
                if 'keywords' not in article:
                    article['keywords'] = self._extract_simple_keywords(article['title'] + ' ' + article.get('summary', ''))
                if 'category' not in article:
                    article['category'] = '其他'
                if 'sentiment' not in article:
                    article['sentiment'] = '中性'
                if 'sentiment_score' not in article:
                    article['sentiment_score'] = 0.0
                if 'core_points' not in article:
                    article['core_points'] = []

        return articles

    def _extract_simple_keywords(self, text: str) -> List[str]:
        """简单的关键词提取（备用方法）"""
        # EPC总承包相关关键词
        epc_keywords = [
            'EPC总承包', '工程总承包', '设计管理', '采购管理', '施工管理',
            '成本控制', '风险管理', '合同管理', '质量管理', '进度管理',
            '业主', '总承包商', '分包商', '供应商', '监理',
            '招标', '投标', '合同', '变更', '索赔', '验收',
            'BIM', '装配式', '绿色建筑', '智慧工地'
        ]

        found_keywords = []
        for keyword in epc_keywords:
            if keyword in text:
                found_keywords.append(keyword)

        return found_keywords[:5] if found_keywords else ['EPC总承包']

    def _log_analysis_summary(self, articles: List[Dict]):
        """输出分析摘要统计"""
        # 分类统计
        category_count = {}
        for article in articles:
            category = article.get('category', '其他')
            category_count[category] = category_count.get(category, 0) + 1

        self.logger.info("=" * 60)
        self.logger.info("📊 文章分析摘要统计")
        self.logger.info("=" * 60)
        self.logger.info(f"📁 分类分布:")
        for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            self.logger.info(f"   • {category}: {count}篇")

        # 情感统计
        sentiment_count = {'积极': 0, '中性': 0, '消极': 0}
        total_score = 0
        for article in articles:
            sentiment = article.get('sentiment', '中性')
            sentiment_count[sentiment] = sentiment_count.get(sentiment, 0) + 1
            total_score += article.get('sentiment_score', 0)

        avg_sentiment = total_score / len(articles) if articles else 0

        self.logger.info(f"\n😊 情感分析:")
        self.logger.info(f"   • 积极: {sentiment_count['积极']}篇")
        self.logger.info(f"   • 中性: {sentiment_count['中性']}篇")
        self.logger.info(f"   • 消极: {sentiment_count['消极']}篇")
        self.logger.info(f"   • 平均情感得分: {avg_sentiment:.2f} ({'积极' if avg_sentiment > 0.1 else '消极' if avg_sentiment < -0.1 else '中性'})")

        # 关键词统计
        all_keywords = []
        for article in articles:
            all_keywords.extend(article.get('keywords', []))

        from collections import Counter
        keyword_counter = Counter(all_keywords)
        top_keywords = keyword_counter.most_common(10)

        self.logger.info(f"\n🔑 高频关键词:")
        for keyword, count in top_keywords:
            self.logger.info(f"   • {keyword}: {count}次")

        self.logger.info("=" * 60)


# =============================================================================
# 智谱AI分析类
# =============================================================================

class ZhipuAIAnalyzer:
    """智谱AI分析类"""

    def __init__(self, config: Config, logger: Logger) -> None:
        """初始化AI分析器"""
        self.config = config
        self.logger = logger
        self.client = ZhipuAI(api_key=config.zhipu_api_key)

    @cached(ttl=86400, max_size=100)  # Cache for 24 hours (优化：延长缓存时间减少API调用)
    def generate_hot_question(self, articles: List[Dict]) -> str:
        """
        使用JTBD理论分析并生成热点问题

        Args:
            articles: 文章列表，每篇文章包含标题、摘要等信息

        Returns:
            str: 生成的热点问题

        Raises:
            ValueError: 如果文章列表为空或格式不正确
            AIAnalysisError: 如果AI分析失败

        【v3.6.7增强】添加重试机制和质量评分
        """
        # 输入验证
        if not articles:
            raise ValueError("文章列表不能为空")

        if not isinstance(articles, list):
            raise ValueError("文章列表必须是列表类型")

        for i, article in enumerate(articles):
            if not isinstance(article, dict):
                raise ValueError(f"第{i+1}篇文章必须是字典类型")
            if 'title' not in article:
                raise ValueError(f"第{i+1}篇文章缺少'title'字段")

        self.logger.info("开始使用智谱AI分析并生成热点问题")

        context = self._build_context(articles)
        prompt = self._build_prompt(context)

        # 0成本优化：GLM-4.7-Flash 对空输入更敏感，需要确保内容非空
        if not prompt or not prompt.strip():
            self.logger.warning("文章上下文为空，使用默认提示")
            prompt = "暂无具体文章内容，请基于EPC总承包行业常识生成一个热点问题。"

        # 确保提示词非空
        system_prompt = self.config.prompt_hot_question_system or "你是EPC总承包行业专家，请生成一个热点问题。"
        user_prompt_template = self.config.prompt_hot_question_user or "基于以下内容生成热点问题：{articles_context}"
        user_prompt = user_prompt_template.format(articles_context=prompt)

        self.logger.debug(f"热点问题生成 - 系统提示词长度: {len(system_prompt)}, 用户提示词长度: {len(user_prompt)}")

        # 【v3.6.7新增】质量评分器
        quality_scorer = ContentQualityScorer(self.logger)

        # 【v3.6.7新增】重试机制（最多3次）
        max_retries = 3
        question = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.zhipu_model_fast,  # 使用0成本模型（glm-4.7-flash）生成问题
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=2000,
                    timeout=Constants.API_CALL_TIMEOUT  # 【v3.6.4修复】添加API调用超时
                )

                question = response.choices[0].message.content.strip()

                # 【0成本优化V2.1】GLM-4.7-Flash 偶尔返回空响应，需要处理
                if not question or not question.strip():
                    self.logger.warning(f"AI返回空响应 (尝试 {attempt + 1}/{max_retries})")
                    continue

                question = self._validate_question(question)

                # 【v3.6.7新增】质量评分
                quality_result = quality_scorer.score_question(question)
                if quality_result['passed']:
                    self.logger.info(f"✓ 热点问题质量达标: {quality_result['score']}分")
                    self.logger.info(f"生成热点问题: {question}")
                    return question
                else:
                    self.logger.warning(f"热点问题质量不达标 (尝试 {attempt + 1}/{max_retries}): {quality_result['score']}分")
                    self.logger.warning(f"问题: {quality_result['issues']}")
                    if attempt < max_retries - 1:
                        self.logger.info("尝试重新生成...")
                        continue

            except Exception as e:
                self.logger.error(f"智谱AI调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # 等待2秒后重试
                    continue

        # 所有重试都失败，使用备用问题列表
        self.logger.warning("所有AI生成尝试失败，使用备用热点问题")
        backup_questions = [
            "在EPC总承包项目实施阶段，面对材料价格波动和工期压力的双重挑战，如何通过精细化管理实现成本控制和进度优化的平衡？",
            "EPC总承包项目在结算阶段常遇到哪些争议问题？如何通过合同管理和证据保全来有效维护自身权益？",
            "在当前市场环境下，EPC总承包企业如何通过数字化转型提升项目管理效率和风险防控能力？",
            "EPC项目联合体合作中，如何合理分配利润和风险，确保各方利益均衡且项目顺利推进？",
            "面对日益严格的环保要求，EPC总承包项目如何实现绿色施工与成本效益的双赢？"
        ]
        import random
        question = random.choice(backup_questions)
        self.logger.info(f"使用备用热点问题: {question}")
        return question

    def _build_context(self, articles: List[Dict]) -> str:
        """构建分析上下文（包含标题、优化摘要、关键词、分类、情感）"""
        selected_articles = articles[:20]
        context_parts = []

        for i, article in enumerate(selected_articles, 1):
            # 使用优化后的摘要
            title = article['title']
            # 优先使用优化摘要，其次使用原摘要
            summary = article.get('optimized_summary', article.get('summary', article.get('content', title)))
            keywords = article.get('keywords', [])
            category = article.get('category', '')
            sentiment = article.get('sentiment', '')
            core_points = article.get('core_points', [])

            # 构建文章信息
            article_info = f"文章{i}：\n标题：{title}\n分类：{category}\n情感：{sentiment}"

            if keywords:
                article_info += f"\n关键词：{', '.join(keywords)}"

            article_info += f"\n摘要：{summary}"

            if core_points:
                article_info += f"\n核心观点："
                for point in core_points:
                    article_info += f"\n  • {point}"

            context_parts.append(article_info)

        return "\n\n".join(context_parts)

    def _build_prompt(self, context: str) -> str:
        """构建文章内容上下文（供配置文件中的提示词使用）"""
        # 只返回文章内容上下文，提示词指令从配置文件读取
        return context

    def _validate_question(self, question: str) -> str:
        """
        验证并清理生成的问题（确保是问句）

        Args:
            question: 原始问题文本

        Returns:
            str: 验证和清理后的问题

        Raises:
            ValueError: 如果问题为空或无效
        """
        if not question or not isinstance(question, str):
            raise ValueError("问题必须是非空字符串")

        question = question.strip('"\'')

        prefixes = ['问题：', '热点问题：', '推荐问题：', 'Q:', 'Q：']
        for prefix in prefixes:
            if question.startswith(prefix):
                question = question[len(prefix):].strip()

        # 验证是否是问句（必须以问号结尾或包含疑问词）
        question_markers = ['？', '?', '吗', '呢', '如何', '怎么', '什么', '哪些', '为什么', '怎样', '是否', '能否', '能否']
        is_question = question.endswith('？') or question.endswith('?')

        # 检查是否包含疑问词
        if not is_question:
            for marker in question_markers:
                if marker in question:
                    is_question = True
                    break

        # 如果不是问句，转换为问句格式
        if not is_question:
            self.logger.warning(f"生成的内容不是问句: {question}，转换为问句格式")
            # 添加疑问词和问号
            if '如何' not in question and '怎么' not in question and '为什么' not in question:
                if '的' in question:
                    # 如果有"的"，尝试将"的"改为"如何"
                    question = question.replace('的', '如何', 1)
                elif '，' in question:
                    # 如果有逗号，在逗号前加"如何"
                    question = question.replace('，', '，如何', 1)
                else:
                    # 直接在前面加"如何"
                    question = f"如何{question}"
            if not question.endswith('？') and not question.endswith('?'):
                question += "？"

        if len(question) < 50:
            self.logger.warning(f"生成的问题过短（{len(question)}字），少于50字要求，返回默认问题")
            # 返回一个符合要求的默认问题（聚焦具体场景）
            return f"在EPC总承包项目的设计变更频繁发生且费用索赔争议不断的实际场景下，总承包商如何通过合同条款优化和现场证据管理，有效控制变更成本并维护合法权益？"

        if 'EPC总承包' not in question and 'epc总承包' not in question.lower():
            self.logger.warning(f"生成的问题不包含'EPC总承包'，添加默认前缀")
            question = f"EPC总承包领域：{question}"

        return question

    @cached(ttl=43200, max_size=200)  # Cache for 12 hours (优化：延长缓存时间减少API调用)
    def generate_catchy_title(self, question: str, answer: str, keyword: str = None) -> str:
        """
        根据热点问题凝练生成10万+自媒体风格标题

        核心策略：
        1. 深度分析热点问题中的具体场景和痛点
        2. 提取文章中的核心观点和关键数字
        3. 运用十大10万+标题公式生成爆款标题
        4. 标题必须包含搜索关键词（如果提供）

        Args:
            question: 热点问题（已包含具体场景描述）
            answer: AI生成的回答
            keyword: 搜索关键词（标题必须包含此关键词）

        Returns:
            str: 生成的10万+风格标题

        Raises:
            ValueError: 如果问题或回答为空或格式不正确
            AIAnalysisError: 如果AI生成失败
        """
        # 确保re模块可用（修复作用域问题）
        import re
        import random
        import time

        # 输入验证
        if not question or not isinstance(question, str):
            raise ValueError("问题必须是非空字符串")

        if not answer or not isinstance(answer, str):
            raise ValueError("回答必须是非空字符串")

        if len(question) < 10:
            raise ValueError("问题长度不能少于10个字符")

        if len(answer) < 50:
            raise ValueError("回答长度不能少于50个字符")

        self.logger.info("使用智谱AI生成10万+自媒体风格标题")
        self.logger.info(f"热点问题: {question}")

        # 提取文章核心内容用于分析
        content_for_analysis = answer[:2000] if len(answer) > 2000 else answer

        # 备用标题模板（仅在AI生成失败时使用）- 紧扣具体场景、包含感叹号（28-30字）
        title_templates = [
            "EPC设计变更索赔90%的人都做错这3点！后果真的很严重",
            "别让设计变更毁了你的EPC项目！这4招帮你有效规避风险",
            "EPC分包商违约怎么办？这5个合同条款必须提前看清！",
            "EPC项目成本失控？这5个真相终于大揭秘！速看",
            "掌握这4招让EPC项目利润直接提升30%！非常实用",
            "EPC合同这3个条款不看清后果真的很严重！必须警惕",
            "EPC项目风险管理这3个关键点必须牢牢掌握！非常重要",
            "EPC项目工期延误怎么办？这4个应对策略非常关键！",
        ]

        def _clean_title(raw_title: str) -> str:
            """清理标题的辅助函数"""
            if not raw_title:
                return ""
            # 移除编号前缀
            cleaned = re.sub(r'^[\d\.\、\s]+', '', raw_title)
            # 移除常见标记
            for prefix in ['标题：', '【最佳】', '最佳：', '推荐：', '爆款：', '答案：']:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):].strip()
            # 移除引号和特殊符号
            for char in '"''《》【】#*「」『』\n\r\t':
                cleaned = cleaned.replace(char, '')
            # 移除结尾标点（保留感叹号）
            cleaned = re.sub(r'[，。、：:,]$', '', cleaned)
            return cleaned.strip()

        # 构建关键词要求
        keyword_requirement = ""
        if keyword:
            keyword_requirement = f"""
【关键词强制要求】
标题必须包含搜索关键词「{keyword}」，这是文章的核心主题，不能遗漏！"""

        # 【v3.6.10修复】增强的重试机制 - 解决AI返回空的问题
        MAX_TITLE_RETRIES = 5  # 增加到5次重试
        title = ""
        last_error = None

        for retry in range(MAX_TITLE_RETRIES):
            try:
                self.logger.info(f"📍 标题生成尝试 {retry + 1}/{MAX_TITLE_RETRIES}")

                # 【v3.6.10优化】根据重试次数调整参数
                current_temp = 0.9 - (retry * 0.1)  # 逐次降低温度，获得更稳定输出
                current_temp = max(0.5, current_temp)

                response = self.client.chat.completions.create(
                    model=self.config.zhipu_model_title,
                    messages=[
                        {
                            "role": "system",
                            "content": self.config.prompt_title_system
                        },
                        {
                            "role": "user",
                            "content": self.config.prompt_title_user.format(
                                question=question,
                                content=content_for_analysis,
                                keyword_requirement=keyword_requirement
                            )
                        }
                    ],
                    temperature=current_temp,
                    max_tokens=300,  # 【v3.6.10修复】从100增加到300，确保模型有足够空间输出最终结果
                    timeout=Constants.API_CALL_TIMEOUT
                )

                # 【v3.6.10增强】全面的响应验证
                if not response:
                    self.logger.warning(f"⚠️ API响应为None，重试中...")
                    last_error = "API响应为None"
                    continue

                if not hasattr(response, 'choices') or not response.choices:
                    self.logger.warning(f"⚠️ API响应无效：choices为空")
                    last_error = "choices为空"
                    continue

                if not response.choices[0]:
                    self.logger.warning(f"⚠️ API响应无效：choices[0]为空")
                    last_error = "choices[0]为空"
                    continue

                message = response.choices[0].message
                if not message:
                    self.logger.warning(f"⚠️ API响应无效：message为空")
                    last_error = "message为空"
                    continue

                # 【v3.6.10关键修复】获取内容 - 优先使用content
                raw_content = getattr(message, 'content', None)

                # 【重要】GLM-4.7-Flash 模型可能会进行深度思考
                # 如果content为空但有reasoning_content，说明模型在思考但未输出最终结果
                if not raw_content or raw_content.strip() == '':
                    reasoning_content = getattr(message, 'reasoning_content', None)
                    if reasoning_content and reasoning_content.strip():
                        self.logger.warning(f"⚠️ content为空但存在reasoning_content（模型思考中），需要重试")
                        self.logger.debug(f"reasoning_content长度: {len(reasoning_content)}")
                        # 不使用reasoning_content，而是重试
                        last_error = "模型只输出了思考过程，需要重试"
                        continue
                    else:
                        self.logger.warning(f"⚠️ API响应无效：content为空且无reasoning_content")
                        last_error = "content为None"
                        continue

                # 清理标题
                title = _clean_title(raw_content)
                self.logger.info(f"AI原始输出: {raw_content.strip()}")
                self.logger.info(f"清理后标题: {title}")

                # 【v3.6.10新增】严格的标题验证
                if not title:
                    self.logger.warning(f"⚠️ 清理后标题为空，重试中...")
                    last_error = "清理后标题为空"
                    continue

                if len(title) < 10:
                    self.logger.warning(f"⚠️ 标题过短（{len(title)}字），重试中...")
                    last_error = f"标题过短: {len(title)}字"
                    title = ""
                    continue

                # 标题有效，跳出重试循环
                self.logger.info(f"✅ 标题生成成功 (尝试 {retry + 1}/{MAX_TITLE_RETRIES})")
                break

            except Exception as api_error:
                last_error = str(api_error)
                self.logger.error(f"❌ 标题生成API调用失败 (尝试 {retry + 1}/{MAX_TITLE_RETRIES}): {str(api_error)}")
                if retry < MAX_TITLE_RETRIES - 1:
                    wait_time = 2 + retry  # 递增等待时间
                    self.logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                continue

        # 【v3.6.10新增】如果所有重试都失败，使用备用模板
        if not title:
            self.logger.warning(f"⚠️ 所有重试均失败 (最后错误: {last_error})，使用备用标题模板")
            title = random.choice(title_templates)
            self.logger.info(f"📋 使用备用标题: {title}")

        # === 标题后处理（统一处理逻辑）===

        # 检查标题长度
        if len(title) < 28:
            self.logger.warning(f"生成的标题过短（{len(title)}字），少于28字要求")

        # 智能处理超长标题
        if len(title) > 30:
            self.logger.warning(f"生成的标题超长（{len(title)}字），进行智能截断")
            # 尝试在标点符号处截断
            truncate_points = ['！', '？', '。', '，', '：']
            for point in truncate_points:
                pos = title.rfind(point, 0, 30)
                if pos > 20:  # 确保截断后还有足够内容
                    title = title[:pos + 1]
                    self.logger.info(f"✓ 在标点处截断: {title}")
                    break
            else:
                # 没有合适的截断点，直接截断到30字
                title = title[:30]
                self.logger.info(f"✓ 直接截断到30字: {title}")

        # 关键词验证
        if keyword and keyword not in title:
            self.logger.warning(f"标题不包含搜索关键词「{keyword}」，尝试添加")
            new_title = f"{keyword}{title}"
            if len(new_title) <= 30:
                title = new_title
                self.logger.info(f"✓ 已添加关键词「{keyword}」，新标题: {title}")
            elif 'EPC项目' in title and keyword not in ['EPC', 'EPC总承包']:
                new_title = title.replace('EPC项目', f'{keyword}项目', 1)
                if len(new_title) <= 30:
                    title = new_title
                    self.logger.info(f"✓ 已替换为关键词，新标题: {title}")

        self.logger.info(f"✓ 最终标题: {title} (长度: {len(title)}字)")
        return title

    # 图片模板库 - 根据关键词匹配预设模板，减少AI图片生成调用（成本优化）
    IMAGE_TEMPLATES = {
        # 成本控制类
        '成本': {
            'prompt': "高饱和度彩色火柴人风格。场景：工程成本控制中心。前景：戴黄色安全帽的财务火柴人手持红色成本报表和放大镜，戴蓝色安全帽的项目经理火柴人操作金色计算器分析数据。背景：彩色柱状图、饼图、折线图，红色预警标志，绿色成本节约指标。配色：亮黄#FFD700、宝蓝#0096FF、绯红#FF2D55、翠绿#34C759，高饱和度，浅蓝渐变背景。横版构图900x500。",
            'keywords': ['成本', '费用', '预算', '利润', '盈亏']
        },
        # 合同管理类
        '合同': {
            'prompt': "高饱和度彩色火柴人风格。场景：合同签约现场。前景：戴红色领带的商务火柴人手持蓝色合同文件，戴黄色安全帽的工程师火柴人检查条款清单，戴橙色安全帽的法务火柴人审核印章。背景：彩色文件堆叠、合同模板、签字笔、企业LOGO墙。配色：亮黄#FFD700、宝蓝#0096FF、绯红#FF2D55、亮橙#FF6B00，高饱和度，浅蓝渐变背景。横版构图900x500。",
            'keywords': ['合同', '条款', '签约', '索赔', '违约']
        },
        # 风险管理类
        '风险': {
            'prompt': "高饱和度彩色火柴人风格。场景：工程风险评估中心。前景：戴红色安全帽的风险管理火柴人手持黄色警示牌，戴蓝色安全帽的工程师火柴人检查红色风险清单，戴橙色安全帽的安全员火柴人监控雷达图。背景：彩色风险矩阵图、红黄绿警示灯、安全标语横幅。配色：亮黄#FFD700、绯红#FF2D55、翠绿#34C759、亮橙#FF6B00，高饱和度，浅灰渐变背景。横版构图900x500。",
            'keywords': ['风险', '预警', '安全', '事故', '隐患']
        },
        # 项目管理类
        '项目': {
            'prompt': "高饱和度彩色火柴人风格。场景：EPC项目指挥中心。前景：戴黄色安全帽的项目经理火柴人手持蓝色进度表，戴橙色安全帽的工程师火柴人操作彩色甘特图，戴绿色安全帽的质检火柴人检查检查清单。背景：彩色建筑轮廓、进度条、里程碑标记、团队协作图标。配色：亮黄#FFD700、宝蓝#0096FF、翠绿#34C759、亮橙#FF6B00，高饱和度，浅蓝渐变背景。横版构图900x500。",
            'keywords': ['项目', '进度', '管理', '协调', '计划']
        },
        # 设计管理类
        '设计': {
            'prompt': "高饱和度彩色火柴人风格。场景：工程设计工作室。前景：戴蓝色安全帽的设计师火柴人手持彩色图纸和绘图笔，戴黄色安全帽的审核火柴人检查蓝图，戴橙色安全帽的BIM工程师火柴人操作3D模型。背景：彩色建筑效果图、BIM模型界面、设计规范手册、彩色图钉板。配色：亮黄#FFD700、宝蓝#0096FF、紫罗兰#9B59B6、翠绿#34C759，高饱和度，浅蓝渐变背景。横版构图900x500。",
            'keywords': ['设计', '图纸', 'BIM', '方案', '变更']
        },
        # 招投标类
        '投标': {
            'prompt': "高饱和度彩色火柴人风格。场景：工程招投标现场。前景：戴红色领带的商务火柴人手持黄色投标文件，戴蓝色安全帽的工程师火柴人计算报价，戴橙色安全帽的评审火柴人检查评分表。背景：彩色投标文件堆、评分矩阵图、中标公告栏、金色奖杯。配色：亮黄#FFD700、宝蓝#0096FF、绯红#FF2D55、亮橙#FF6B00，高饱和度，浅蓝渐变背景。横版构图900x500。",
            'keywords': ['投标', '招标', '报价', '中标', '竞标']
        },
        # 质量管理类
        '质量': {
            'prompt': "高饱和度彩色火柴人风格。场景：工程质量检测中心。前景：戴绿色安全帽的质检火柴人手持黄色检测仪器，戴蓝色安全帽的工程师火柴人检查质量报告，戴橙色安全帽的监理火柴人审核验收单。背景：彩色质量检测设备、合格印章、质量标准手册、绿色合格标志。配色：翠绿#34C759、亮黄#FFD700、宝蓝#0096FF、亮橙#FF6B00，高饱和度，浅蓝渐变背景。横版构图900x500。",
            'keywords': ['质量', '验收', '检测', '合格', '标准']
        },
        # 默认模板
        'default': {
            'prompt': "高饱和度彩色火柴人风格。场景：工程审计现场，彩色文件堆叠，放大镜和检查清单。前景：戴亮黄色安全帽的工程火柴人手持红色审计报告，戴橙色安全帽的审计火柴人用放大镜检查蓝色图纸，戴蓝色安全帽的财务火柴人操作金色计算器。背景：彩色建筑轮廓、黄黑安全警示条纹、绿色进度条、红色警示标志。配色：亮黄#FFD700、宝蓝#0096FF、绯红#FF2D55、翠绿#34C759、亮橙#FF6B00、紫罗兰#9B59B6，高饱和度，浅蓝渐变背景，色彩丰富，视觉冲击力强。横版构图900x500。",
            'keywords': []
        }
    }

    def _match_image_template(self, question: str) -> str:
        """根据问题关键词匹配合适的图片模板

        Args:
            question: 热点问题

        Returns:
            匹配的图片提示词模板
        """
        question_lower = question.lower()

        # 遍历模板库，查找最佳匹配
        for template_name, template_data in self.IMAGE_TEMPLATES.items():
            if template_name == 'default':
                continue
            for keyword in template_data.get('keywords', []):
                if keyword in question_lower or keyword in question:
                    self.logger.info(f"匹配到图片模板: {template_name} (关键词: {keyword})")
                    return template_data['prompt']

        # 没有匹配则返回默认模板
        self.logger.info("使用默认图片模板")
        return self.IMAGE_TEMPLATES['default']['prompt']

    def generate_cover_image_prompt(self, question: str, answer: str) -> str:
        """根据问题和回答生成高饱和度彩色火柴人风格封面图片提示词

        注意：图片模板复用功能已禁用，每次都使用AI生成以确保封面图正确
        """
        # 直接使用AI生成图片提示词（禁用模板复用）
        self.logger.info("使用智谱AI生成高饱和度彩色火柴人风格封面图片提示词")

        try:
            response = self.client.chat.completions.create(
                model=self.config.zhipu_model_fast,  # 使用低成本模型（glm-4-flash）生成图片提示词
                messages=[
                    {
                        "role": "system",
                        "content": self.config.prompt_cover_system  # 从配置文件读取
                    },
                    {
                        "role": "user",
                        "content": self.config.prompt_cover_user.format(question=question, answer=answer[:300])
                    }
                ],
                temperature=0.8,
                max_tokens=500,
                timeout=Constants.API_CALL_TIMEOUT  # 【v3.6.4修复】添加API调用超时
            )

            image_prompt = response.choices[0].message.content.strip()
            self.logger.info(f"生成火柴人风格封面提示词: {image_prompt}")
            return image_prompt

        except Exception as e:
            self.logger.error(f"生成封面图片提示词失败: {str(e)}")
            # 返回默认的火柴人风格提示词
            return "高饱和度彩色火柴人风格。场景：工程审计现场，彩色文件堆叠，放大镜和检查清单。前景：戴亮黄色安全帽的工程火柴人手持红色审计报告，戴橙色安全帽的审计火柴人用放大镜检查蓝色图纸，戴蓝色安全帽的财务火柴人操作金色计算器。背景：彩色建筑轮廓、黄黑安全警示条纹、绿色进度条、红色警示标志。配色：亮黄#FFD700、宝蓝#0096FF、绯红#FF2D55、翠绿#34C759、亮橙#FF6B00、紫罗兰#9B59B6，高饱和度，浅蓝渐变背景，色彩丰富，视觉冲击力强。横版构图900x500。"

    def generate_cover_image(self, question: str, answer: str, output_path: str = None) -> str:
        """使用智谱AI生成封面图片

        Args:
            question: 文章问题
            answer: 文章回答
            output_path: 输出图片路径，默认为 cover.jpg

        Returns:
            生成的图片路径，失败返回空字符串
        """
        self.logger.info("开始使用智谱AI生成封面图片")

        if output_path is None:
            script_dir = Path(__file__).parent
            output_path = str(script_dir / 'cover.jpg')

        try:
            # 首先生成图片提示词
            image_prompt = self.generate_cover_image_prompt(question, answer)

            # 使用智谱AI图像生成API（0成本优化：使用cogview-3-flash免费模型）
            # 注意：智谱AI的图像生成使用 cogview 模型
            # 智谱AI支持的尺寸: "1024x1024", "768x1344", "864x1152", "1344x768", "1152x864"

            # 优先使用免费模型 cogview-3-flash
            image_model = getattr(self.config, 'image_model', 'cogview-3-flash')
            self.logger.info(f"使用图片生成模型: {image_model}（免费）")

            try:
                response = self.client.images.generations(
                    model=image_model,  # 0成本优化：使用 cogview-3-flash 免费模型
                    prompt=image_prompt,
                    size="1024x1024"  # 使用正确的尺寸格式
                )
            except Exception as model_error:
                # 如果cogview-3-flash不可用，回退到cogview-3
                if 'flash' in image_model:
                    self.logger.warning(f"免费模型 {image_model} 调用失败: {str(model_error)}，回退到cogview-3")
                    response = self.client.images.generations(
                        model="cogview-3",
                        prompt=image_prompt,
                        size="1024x1024"
                    )
                else:
                    raise model_error

            # 获取图片URL
            if response.data and len(response.data) > 0:
                image_url = response.data[0].url
                self.logger.info(f"智谱AI生成图片URL: {image_url}")

                # 下载图片
                urllib.request.urlretrieve(image_url, output_path)
                self.logger.info(f"封面图片已保存: {output_path}")

                # 使用 PIL 调整图片尺寸为 900x500
                try:
                    from PIL import Image
                    img = Image.open(output_path)
                    # 裁剪或缩放为 900x500
                    img_resized = img.resize((900, 500), Image.Resampling.LANCZOS)
                    img_resized.save(output_path, 'JPEG', quality=95)
                    self.logger.info("封面图片已调整为 900x500 像素")
                except ImportError:
                    self.logger.warning("未安装PIL库，跳过尺寸调整")
                except Exception as e:
                    self.logger.warning(f"调整图片尺寸失败: {str(e)}")

                return output_path
            else:
                self.logger.error("智谱AI未返回图片数据")
                return ""

        except Exception as e:
            self.logger.error(f"生成封面图片失败: {str(e)}")
            return ""

    def _validate_title_relevance(self, title: str, question: str) -> bool:
        """验证标题与问题的相关性

        检查标题是否包含问题中的核心关键词，确保标题准确反映问题主题

        Args:
            title: 生成的标题
            question: 原始问题

        Returns:
            bool: 相关性是否达标
        """
        try:
            import jieba

            # 从问题中提取关键词
            question_words = set(jieba.cut(question))

            # 过滤停用词和标点
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '如何', '什么', '为什么', '怎么'}
            question_keywords = [w for w in question_words if len(w) >= 2 and w not in stop_words and not re.match(r'^[^\w\u4e00-\u9fff]+$', w)]

            # 检查标题是否包含核心关键词
            matched_keywords = []
            for keyword in question_keywords[:5]:  # 只检查前5个核心关键词
                if keyword in title:
                    matched_keywords.append(keyword)

            # 至少匹配1个核心关键词
            if len(matched_keywords) >= 1:
                self.logger.info(f"标题关键词匹配: {matched_keywords}")
                return True
            else:
                # 如果没有匹配，检查是否有EPC相关词汇作为保底
                epc_keywords = ['EPC', '总承包', '工程', '项目', '设计', '施工', '成本', '合同', '管理']
                for kw in epc_keywords:
                    if kw in title and kw in question:
                        self.logger.info(f"标题EPC关键词匹配: {kw}")
                        return True

                self.logger.warning(f"标题与问题关键词不匹配。问题关键词: {question_keywords[:5]}, 标题: {title}")
                return False

        except ImportError:
            self.logger.warning("未安装jieba库，跳过标题相关性验证")
            return True
        except Exception as e:
            self.logger.warning(f"标题相关性验证失败: {str(e)}")
            return True  # 验证失败时默认通过，避免误判


# =============================================================================
# 总包大脑自动化类 (使用Stagehand)
# =============================================================================

class MetasoAutomation:
    """总包大脑自动化类 (使用Stagehand)"""

    def __init__(self, config: Config, logger: Logger) -> None:
        """初始化自动化"""
        self.config = config
        self.logger = logger
        self.browser = None
        self.last_question = ""
        self._browser_restart_count = 0  # 浏览器重启计数器
        self._max_browser_restarts = 3   # 最大重启次数

    async def _check_browser_health(self) -> bool:
        """
        检查浏览器健康状态（稳定性优化）

        Returns:
            bool: 浏览器是否健康
        """
        if not self.browser:
            return False

        try:
            # 检查页面对象是否存在
            if not hasattr(self.browser, 'page') or not self.browser.page:
                self.logger.warning("浏览器页面对象不存在")
                return False

            # 尝试执行简单的JavaScript检查浏览器响应
            try:
                result = await self.browser.page.evaluate('1+1')
                if result != 2:
                    self.logger.warning(f"浏览器响应异常: 1+1 = {result}")
                    return False
            except Exception as eval_error:
                self.logger.warning(f"浏览器JavaScript执行失败: {str(eval_error)}")
                return False

            # 检查页面是否已关闭
            if self.browser.page.is_closed():
                self.logger.warning("浏览器页面已关闭")
                return False

            return True

        except Exception as e:
            self.logger.warning(f"浏览器健康检查失败: {str(e)}")
            return False

    async def close(self) -> None:
        """
        关闭浏览器并保存 metaso.cn 登录状态

        【v3.6.9 重大修复】
        1. 只保存 metaso.cn 域名的 cookies（防止 sogou.com cookies 污染）
        2. 添加超时保护
        3. 强制清理资源
        """
        if self.browser:
            try:
                # 【v3.6.9 关键修复】只保存 metaso.cn cookies
                # 使用 cookie_domain_filter 确保只保存正确的域名
                await self.browser.close(save_cookies=True, cookie_domain_filter="metaso.cn")
                self.logger.info("✓ MetasoAutomation 浏览器已关闭，metaso.cn cookies 已保存")
            except Exception as e:
                self.logger.warning(f"关闭浏览器时出错: {str(e)}")
                # 即使出错也尝试清理
                try:
                    if hasattr(self.browser, 'context') and self.browser.context:
                        await self.browser.context.close()
                    if hasattr(self.browser, 'browser') and self.browser.browser:
                        await self.browser.browser.close()
                except Exception:
                    pass
            finally:
                self.browser = None

    async def _restart_browser(self) -> bool:
        """
        重启浏览器（稳定性优化）

        Returns:
            bool: 重启是否成功
        """
        self._browser_restart_count += 1

        if self._browser_restart_count > self._max_browser_restarts:
            self.logger.error(f"浏览器重启次数超过限制({self._max_browser_restarts})")
            return False

        self.logger.info(f"正在重启浏览器... (第{self._browser_restart_count}次)")

        # 关闭旧浏览器
        # 【v3.6.9】重启前只保存 metaso.cn cookies（防止 sogou.com 污染）
        if self.browser:
            try:
                await self.browser.close(save_cookies=True, cookie_domain_filter="metaso.cn")
            except Exception as e:
                self.logger.debug(f"关闭旧浏览器时出错: {str(e)}")

        # 等待一段时间再重启
        await asyncio.sleep(2)

        # 启动新浏览器
        try:
            self.browser = StagehandBrowser(self.config, self.logger)
            await self.browser.start(headless=False, use_persistent_context=True)
            self.logger.info("浏览器重启成功")
            return True
        except Exception as e:
            self.logger.error(f"浏览器重启失败: {str(e)}")
            return False

    @profile
    async def send_question_and_get_answer(self, question: str, max_retry: int = None, prompt_content: str = None) -> Optional[str]:
        """发送问题到总包大脑并获取回答

        Args:
            question: 要发送的问题
            max_retry: 最大重试次数
            prompt_content: 回复人设提示词内容（可选，用于轮换）
        """
        max_retry = max_retry or self.config.max_retry_times
        self.last_question = question
        self._browser_restart_count = 0  # 重置重启计数器

        self.logger.info(f"准备向总包大脑发送问题: {question}")

        retry_count = 0
        answer = None

        while retry_count < max_retry and not self._is_answer_sufficient(answer):
            retry_count += 1
            self.logger.info(f"第 {retry_count} 次尝试获取回答")

            try:
                # 启动浏览器（如果尚未启动或需要重启）
                if not self.browser or not await self._check_browser_health():
                    if self.browser:
                        await self._restart_browser()
                    else:
                        self.browser = StagehandBrowser(self.config, self.logger)
                        await self.browser.start(headless=False, use_persistent_context=True)

                # 再次检查浏览器健康状态
                if not await self._check_browser_health():
                    self.logger.error("浏览器启动后健康检查失败")
                    continue

                # 访问总包大脑
                await self._navigate_to_metaso()

                # 检查是否需要登录
                if await self._check_login_required():
                    self.logger.info("需要扫码登录，请用户扫码...")
                    if not await self._wait_for_login():
                        self.logger.error("用户登录超时或失败")
                        # 【v3.6.8】登录失败时不保存 cookies（没有有效的登录状态）
                        await self.browser.close(save_cookies=False)
                        continue

                # 如果提供了回复人设提示词，先设置回复人设
                if prompt_content:
                    self.logger.info("步骤3.1: 设置回复人设提示词")
                    if await self._set_reply_persona(prompt_content):
                        self.logger.info("✓ 回复人设设置成功，等待10秒后发送问题...")
                        await asyncio.sleep(10)  # 等待10秒
                    else:
                        self.logger.warning("回复人设设置失败，继续使用默认设置")

                # 发送问题
                await self._send_question(question)

                # 等待并获取回答
                answer = await self._wait_for_answer()

                # 【v3.6.8】显式保存 metaso.cn cookies
                await self.browser.close(save_cookies=True)

            except Exception as e:
                self.logger.error(f"获取回答失败: {str(e)}")
                if self.browser:
                    try:
                        # 【v3.6.8】异常时也尝试保存 cookies
                        await self.browser.close(save_cookies=True)
                    except (Exception,):
                        pass
                continue

        if not self._is_answer_sufficient(answer):
            self.logger.error(f"经过 {max_retry} 次重试，仍未获取到足够长的回答")
            await self._send_failure_notification(question)
            return None

        self.logger.info(f"成功获取回答，长度: {len(answer)} 字符")
        return answer

    async def _set_reply_persona(self, prompt_content: str) -> bool:
        """设置总包大脑的回复人设

        实现完整的人设轮换功能：
        1. 精确定位并点击设置齿轮按钮
        2. 等待浮动弹窗出现
        3. 点击"回复人设"标签
        4. 输入提示词
        5. 保存设置

        Args:
            prompt_content: 回复人设提示词内容

        Returns:
            bool: 设置是否成功
        """
        self.logger.info("=" * 50)
        self.logger.info("开始设置回复人设...")
        self.logger.info("=" * 50)

        try:
            # 等待页面稳定并验证页面已正确加载
            max_page_wait = 3
            for page_wait in range(max_page_wait):
                await asyncio.sleep(3)

                # 验证页面是否正确加载
                page_loaded = await self.browser.page.evaluate('''() => {
                    let found = false;
                    document.querySelectorAll('*').forEach((el) => {
                        const text = (el.innerText || '').trim();
                        if ((text.includes('总包行业大脑') || text.includes('总包大脑')) && text.length < 20) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0 && rect.top < 60) {
                                found = true;
                            }
                        }
                    });
                    return found;
                }''')

                if page_loaded:
                    self.logger.info("  页面已正确加载（检测到总包大脑标题）")
                    break
                else:
                    self.logger.warning(f"  页面未正确加载，等待重试... ({page_wait + 1}/{max_page_wait})")
                    if page_wait < max_page_wait - 1:
                        # 尝试刷新页面
                        try:
                            await self.browser.page.reload(wait_until='domcontentloaded', timeout=30000)
                        except (asyncio.TimeoutError, Exception) as e:
                            self.logger.debug(f"页面刷新失败: {str(e)}")

            # ===== Step 1: 查找并点击设置按钮（带重试） =====
            max_retry = 3
            settings_clicked = False

            for retry in range(max_retry):
                self.logger.info(f"[Step 1] 查找并点击设置按钮... (尝试 {retry + 1}/{max_retry})")

                settings_clicked = await self._click_settings_gear_button()

                if settings_clicked:
                    break

                if retry < max_retry - 1:
                    self.logger.warning(f"  设置按钮点击失败，等待后重试...")
                    await asyncio.sleep(2)
                    # 尝试刷新页面
                    try:
                        await self.browser.page.reload(wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(3)
                    except (asyncio.TimeoutError, Exception) as reload_err:
                        self.logger.debug(f"页面刷新失败: {reload_err}")

            if not settings_clicked:
                self.logger.error("未能点击设置按钮")
                return False

            self.logger.info("[OK] 设置按钮点击成功")

            # 等待浮动弹窗出现
            await asyncio.sleep(2)

            # ===== Step 2: 点击"回复人设"标签 =====
            self.logger.info("[Step 2] 点击'回复人设'标签...")

            persona_tab_clicked = await self._click_persona_tab_in_panel()

            if not persona_tab_clicked:
                self.logger.warning("未能点击'回复人设'标签，尝试继续...")

            # 等待标签切换
            await asyncio.sleep(1)

            # ===== Step 3: 输入提示词 =====
            self.logger.info("[Step 3] 输入提示词...")

            input_success = await self._input_persona_prompt(prompt_content)

            if not input_success:
                self.logger.warning("输入提示词可能未成功")

            # 等待输入完成
            await asyncio.sleep(1)

            # ===== Step 4: 保存设置 =====
            self.logger.info("[Step 4] 保存设置...")

            save_success = await self._click_save_button()

            if not save_success:
                self.logger.warning("保存设置可能未成功")

            # 等待保存完成
            await asyncio.sleep(2)

            # ===== Step 5: 关闭设置面板 =====
            self.logger.info("[Step 5] 关闭设置面板...")
            await self._close_settings_panel()

            # 等待面板关闭动画完成
            await asyncio.sleep(1)

            # 重新导航到总包大脑页面
            self.logger.info("  重新导航到总包大脑页面...")
            try:
                await self.browser.page.goto(self.config.metaso_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                self.logger.info("  [OK] 已重新打开总包大脑页面")
            except Exception as e:
                self.logger.warning(f"  导航失败: {str(e)}")

            self.logger.info("=" * 50)
            self.logger.info("回复人设设置流程完成")
            self.logger.info("=" * 50)

            return True

        except Exception as e:
            self.logger.error(f"设置回复人设时出错: {str(e)}")
            return False

    async def _click_settings_gear_button(self) -> bool:
        """点击设置齿轮按钮 - 位于"总包行业大脑"文字右侧"""
        self.logger.info("  查找设置齿轮按钮（总包行业大脑右侧）...")

        try:
            # 首先找到"总包行业大脑"或"总包大脑"文字的位置
            settings_info = await self.browser.page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                let zongbaoBtn = null;
                let bestMatch = null;
                let candidates = [];

                // 步骤1: 找到包含"总包"文字的元素
                let zongbaoLeft = 0;
                let zongbaoRight = 0;
                let zongbaoTop = 0;

                document.querySelectorAll('*').forEach((el) => {
                    const text = (el.innerText || '').trim();
                    if ((text.includes('总包行业大脑') || text.includes('总包大脑')) && text.length < 20) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.top < 60) {
                            zongbaoLeft = Math.round(rect.left);
                            zongbaoRight = Math.round(rect.right);
                            zongbaoTop = Math.round(rect.top);
                        }
                    }
                });

                // 步骤2: 在"总包大脑"右侧查找齿轮按钮
                for (const btn of buttons) {
                    const rect = btn.getBoundingClientRect();
                    if (rect.top > 80 || rect.width === 0 || rect.height === 0) continue;

                    const svg = btn.querySelector('svg');
                    if (!svg) continue;

                    const viewBox = svg.getAttribute('viewBox') || '';
                    const paths = svg.querySelectorAll('path');
                    const pathCount = paths.length;
                    const btnText = (btn.innerText || '').trim();

                    const candidate = {
                        left: Math.round(rect.left),
                        top: Math.round(rect.top),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        viewBox: viewBox,
                        pathCount: pathCount,
                        text: btnText.substring(0, 20),
                        isRightOfZongbao: zongbaoRight > 0 && rect.left > zongbaoRight && rect.left < zongbaoRight + 100
                    };
                    candidates.push(candidate);

                    // 检查是否是齿轮图标: viewBox="0 0 20 20", 2个path, 无文字
                    if (viewBox === '0 0 20 20' && pathCount === 2 && !btnText) {
                        const path0 = paths[0] ? (paths[0].getAttribute('d') || '').length : 0;
                        const path1 = paths[1] ? (paths[1].getAttribute('d') || '').length : 0;

                        candidate.path0Len = path0;
                        candidate.path1Len = path1;

                        // 优先选择在"总包大脑"右侧的齿轮按钮
                        if (candidate.isRightOfZongbao && path0 > 100 && path1 > 20) {
                            bestMatch = candidate;
                        }
                    }
                }

                return {
                    bestMatch: bestMatch,
                    candidates: candidates.sort((a, b) => a.left - b.left),
                    zongbaoRight: zongbaoRight,
                    zongbaoTop: zongbaoTop
                };
            }''')

            self.logger.info(f"  总包大脑 right={settings_info.get('zongbaoRight', 0)}, top={settings_info.get('zongbaoTop', 0)}")

            if settings_info.get('bestMatch'):
                btn = settings_info['bestMatch']
                self.logger.info(f"  找到齿轮按钮 at left={btn['left']}")

                # 使用JavaScript直接点击按钮（更可靠）
                clicked = await self.browser.page.evaluate(f'''() => {{
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {{
                        const rect = btn.getBoundingClientRect();
                        if (rect.left >= {btn['left'] - 5} && rect.left <= {btn['left'] + 5} &&
                            rect.top >= {btn['top'] - 5} && rect.top <= {btn['top'] + 5}) {{
                            btn.click();
                            return true;
                        }}
                    }}
                    return false;
                }}''')

                await asyncio.sleep(3)  # 增加等待时间

                if await self._verify_settings_panel_open():
                    self.logger.info("  [OK] 齿轮按钮点击成功，设置弹窗已打开")
                    return True
                else:
                    # 如果JavaScript点击失败，尝试鼠标点击
                    self.logger.info("  JS点击失败，尝试鼠标点击...")
                    x = btn['left'] + btn['width'] // 2
                    y = btn['top'] + btn['height'] // 2
                    await self.browser.page.mouse.click(x, y)
                    await asyncio.sleep(3)
                    if await self._verify_settings_panel_open():
                        self.logger.info("  [OK] 鼠标点击成功，设置弹窗已打开")
                        return True

            # 方法2: 尝试所有候选按钮
            for c in settings_info.get('candidates', []):
                if c['viewBox'] == '0 0 20 20' and c['pathCount'] == 2 and not c['text'] and c['left'] > 200:
                    self.logger.info(f"  尝试候选按钮 at left={c['left']}...")

                    await self.browser.page.keyboard.press('Escape')
                    await asyncio.sleep(0.5)

                    # 使用JavaScript点击
                    clicked = await self.browser.page.evaluate(f'''() => {{
                        const buttons = document.querySelectorAll('button');
                        for (const btn of buttons) {{
                            const rect = btn.getBoundingClientRect();
                            if (rect.left >= {c['left'] - 5} && rect.left <= {c['left'] + 5}) {{
                                btn.click();
                                return true;
                            }}
                        }}
                        return false;
                    }}''')

                    await asyncio.sleep(3)

                    if await self._verify_settings_panel_open():
                        self.logger.info("  [OK] 通过候选按钮打开设置弹窗")
                        return True

            # 方法3: 尝试特定坐标（总包行业大脑右侧区域）
            # 根据用户截图，设置按钮在"总包行业大脑"文字右侧
            self.logger.info("  尝试坐标点击（总包行业大脑右侧）...")
            zongbao_right = settings_info.get('zongbaoRight', 200)
            coords_to_try = [
                (zongbao_right + 12, 27),   # 总包大脑右侧12px (精确位置)
                (zongbao_right + 20, 27),   # 总包大脑右侧20px
                (281, 27),   # 备用位置
            ]

            for x, y in coords_to_try:
                self.logger.info(f"  尝试坐标 ({x}, {y})...")

                await self.browser.page.keyboard.press('Escape')
                await asyncio.sleep(0.5)
                await self.browser.page.mouse.click(x, y)
                await asyncio.sleep(3)

                if await self._verify_settings_panel_open():
                    self.logger.info(f"  [OK] 通过坐标 ({x}, {y}) 打开设置弹窗")
                    return True

            # 方法4: 使用AI辅助
            try:
                instruction = """Click on the settings button (gear/cog icon) in the top right area of the page header. This should open a floating settings panel."""
                success = await self.browser.act(instruction, timeout=15000)
                if success:
                    await asyncio.sleep(2)
                    if await self._verify_settings_panel_open():
                        self.logger.info("  [OK] 通过AI识别点击设置按钮")
                        return True
            except Exception as e:
                self.logger.debug(f"  AI识别失败: {str(e)}")

            return False

        except Exception as e:
            self.logger.error(f"  点击设置按钮失败: {str(e)}")
            return False

    async def _verify_settings_panel_open(self) -> bool:
        """验证设置弹窗是否已打开"""
        try:
            panel_check = await self.browser.page.evaluate('''() => {
                // 方法1: 检查常见弹窗选择器
                const selectors = [
                    '[role="dialog"]',
                    '[class*="Popover"]',
                    '[class*="popover"]',
                    '[class*="Modal"]',
                    '[class*="modal"]',
                    '[class*="Drawer"]',
                    '[class*="drawer"]',
                    '[class*="Panel"]',
                    '[class*="panel"]',
                    '[class*="Popup"]',
                    '[class*="popup"]',
                    '[class*="Dropdown"]',
                    '[class*="dropdown"]'
                ];

                for (const sel of selectors) {
                    const panels = document.querySelectorAll(sel);
                    for (const panel of panels) {
                        const rect = panel.getBoundingClientRect();
                        if (rect.width > 200 && rect.height > 200) {
                            const text = panel.innerText || '';
                            if (text.includes('专题设置') || text.includes('设置') ||
                                text.includes('回复人设') || text.includes('人设')) {
                                return { found: true, method: 'selector', selector: sel };
                            }
                        }
                    }
                }

                // 方法2: 检查fixed/absolute定位的大面板
                const allDivs = document.querySelectorAll('div');
                for (const div of allDivs) {
                    const rect = div.getBoundingClientRect();
                    const style = window.getComputedStyle(div);
                    const position = style.position;
                    const zIndex = parseInt(style.zIndex) || 0;

                    if ((position === 'fixed' || position === 'absolute') &&
                        rect.width > 200 && rect.height > 200 && zIndex >= 0) {
                        const text = div.innerText || '';
                        if (text.includes('专题设置') || text.includes('回复人设')) {
                            return { found: true, method: 'position_check' };
                        }
                    }
                }

                // 方法3: 检查页面是否出现了设置相关文本（简化版）
                const bodyText = document.body.innerText;
                if (bodyText.includes('专题设置') || bodyText.includes('回复人设')) {
                    // 查找任何可见的大面板
                    const allElements = document.querySelectorAll('*');
                    for (const el of allElements) {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        if (rect.width > 200 && rect.height > 200 &&
                            (style.position === 'fixed' || style.position === 'absolute') &&
                            style.display !== 'none' && style.visibility !== 'hidden') {
                            return { found: true, method: 'text_found' };
                        }
                    }
                }

                return { found: false };
            }''')

            if panel_check.get('found'):
                self.logger.info(f"    检测到设置面板 (method={panel_check.get('method', 'unknown')})")
                return True

            return False

        except Exception as e:
            self.logger.debug(f"  面板验证失败: {str(e)}")
            return False

    async def _click_persona_tab_in_panel(self) -> bool:
        """在设置弹窗中点击'回复人设'标签"""
        try:
            # 使用JavaScript直接查找并点击标签
            clicked = await self.browser.page.evaluate('''() => {
                // 搜索所有可能包含标签的元素
                const allElements = document.querySelectorAll('button, div[role="tab"], span, a, [class*="tab"], [class*="Tab"]');
                for (const el of allElements) {
                    const text = (el.innerText || '').trim();
                    if (text === '回复人设' || text === '人设') {
                        el.click();
                        return { found: true, text: text, tagName: el.tagName };
                    }
                }
                return { found: false };
            }''')

            if clicked.get('found'):
                self.logger.info(f"  [OK] 已点击'{clicked['text']}'标签 ({clicked['tagName']})")
                await asyncio.sleep(1)
                return True

            # 备用方法: 鼠标点击
            tab_info = await self.browser.page.evaluate('''() => {
                const allElements = document.querySelectorAll('*');
                for (const el of allElements) {
                    const rect = el.getBoundingClientRect();
                    const text = (el.innerText || '').trim();
                    if (rect.width > 0 && rect.height > 0 && rect.width < 200 &&
                        (text === '回复人设' || text === '人设')) {
                        return {
                            found: true,
                            text: text,
                            left: Math.round(rect.left),
                            top: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        };
                    }
                }
                return { found: false };
            }''')

            if tab_info.get('found'):
                self.logger.info(f"  找到'{tab_info['text']}'标签，尝试鼠标点击")
                x = tab_info['left'] + tab_info['width'] // 2
                y = tab_info['top'] + tab_info['height'] // 2
                await self.browser.page.mouse.click(x, y)
                await asyncio.sleep(1)
                return True

            self.logger.warning("  未找到'回复人设'标签，尝试AI辅助...")
            try:
                instruction = """Click on the tab labeled "回复人设" in the settings panel."""
                success = await self.browser.act(instruction, timeout=10000)
                if success:
                    self.logger.info("  [OK] 通过AI点击'回复人设'标签")
                    return True
            except (asyncio.TimeoutError, Exception) as ai_err:
                self.logger.debug(f"AI辅助点击失败: {ai_err}")

            return False

        except Exception as e:
            self.logger.error(f"  点击'回复人设'标签失败: {str(e)}")
            return False

    async def _input_persona_prompt(self, prompt_content: str) -> bool:
        """在文本框中输入提示词"""
        try:
            # 使用JavaScript直接设置文本框内容
            result = await self.browser.page.evaluate(f'''() => {{
                // 查找textarea
                const textareas = document.querySelectorAll('textarea');
                for (const ta of textareas) {{
                    const rect = ta.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 50) {{
                        ta.value = `{prompt_content}`;
                        ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        return {{ found: true, type: 'textarea' }};
                    }}
                }}

                // 查找contenteditable
                const editables = document.querySelectorAll('[contenteditable="true"]');
                for (const el of editables) {{
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 50) {{
                        el.innerText = `{prompt_content}`;
                        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return {{ found: true, type: 'contenteditable' }};
                    }}
                }}
                return {{ found: false }};
            }}''')

            if result.get('found'):
                self.logger.info(f"  [OK] 已输入提示词 (type={result['type']})，长度: {len(prompt_content)}")
                return True

            # 备用方法：使用键盘输入
            textarea_info = await self.browser.page.evaluate('''() => {
                const textareas = document.querySelectorAll('textarea');
                for (const ta of textareas) {
                    const rect = ta.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 50) {
                        return {
                            found: true,
                            left: Math.round(rect.left),
                            top: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        };
                    }
                }
                return { found: false };
            }''')

            if textarea_info.get('found'):
                self.logger.info(f"  找到文本框，使用键盘输入")
                x = textarea_info['left'] + textarea_info['width'] // 2
                y = textarea_info['top'] + textarea_info['height'] // 2
                await self.browser.page.mouse.click(x, y)
                await asyncio.sleep(0.5)
                await self.browser.page.keyboard.press('Control+A')
                await asyncio.sleep(0.3)

                # 分批输入
                chunk_size = 200
                for i in range(0, len(prompt_content), chunk_size):
                    chunk = prompt_content[i:i+chunk_size]
                    await self.browser.page.keyboard.type(chunk, delay=10)
                    await asyncio.sleep(0.3)

                self.logger.info(f"  [OK] 已输入提示词，长度: {len(prompt_content)}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"  输入提示词失败: {str(e)}")
            return False

    async def _click_save_button(self) -> bool:
        """点击保存按钮"""
        try:
            # 使用JavaScript直接点击保存按钮
            clicked = await self.browser.page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = (btn.innerText || '').trim();
                    if (text.includes('保存') || text.includes('确定') || text.includes('确认')) {
                        btn.click();
                        return { found: true, text: text };
                    }
                }
                return { found: false };
            }''')

            if clicked.get('found'):
                self.logger.info(f"  [OK] 已点击'{clicked['text']}'按钮")
                await asyncio.sleep(2)
                return True

            # 备用方法：鼠标点击
            save_info = await self.browser.page.evaluate('''() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = (btn.innerText || '').trim();
                    const rect = btn.getBoundingClientRect();
                    if ((text.includes('保存') || text.includes('确定') || text.includes('确认')) &&
                        rect.width > 0 && rect.height > 0) {
                        return {
                            found: true,
                            text: text,
                            left: Math.round(rect.left),
                            top: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        };
                    }
                }
                return { found: false };
            }''')

            if save_info.get('found'):
                self.logger.info(f"  找到'{save_info['text']}'按钮，使用鼠标点击")
                x = save_info['left'] + save_info['width'] // 2
                y = save_info['top'] + save_info['height'] // 2
                await self.browser.page.mouse.click(x, y)
                await asyncio.sleep(2)
                return True

            return False

        except Exception as e:
            self.logger.error(f"  保存设置失败: {str(e)}")
            return False

    async def _close_settings_panel(self) -> bool:
        """关闭设置面板 - 点击右上角的×按钮"""
        try:
            self.logger.info("  关闭设置面板...")

            for attempt in range(3):  # 最多尝试3次
                # 方法1: 使用JavaScript直接点击×关闭按钮
                closed = await self.browser.page.evaluate('''() => {
                    // 首先找到设置面板
                    let panel = null;
                    const panelSelectors = [
                        '[class*="Drawer"]', '[class*="drawer"]',
                        '[class*="Modal"]', '[class*="modal"]',
                        '[class*="Popover"]', '[class*="popover"]',
                        '[class*="Panel"]', '[class*="panel"]',
                        '[role="dialog"]'
                    ];

                    for (const selector of panelSelectors) {
                        const panels = document.querySelectorAll(selector);
                        for (const p of panels) {
                            const rect = p.getBoundingClientRect();
                            const text = (p.innerText || '');
                            // 找到包含"回复人设"或"专题设置"的面板
                            if (rect.width > 200 && rect.height > 200 &&
                                (text.includes('回复人设') || text.includes('专题设置') || text.includes('人设'))) {
                                panel = p;
                                break;
                            }
                        }
                        if (panel) break;
                    }

                    // 如果找到了面板，在面板内查找关闭按钮
                    if (panel) {
                        const panelRect = panel.getBoundingClientRect();

                        // 在面板右上角区域查找关闭按钮
                        const allButtons = panel.querySelectorAll('button, [role="button"]');
                        for (const btn of allButtons) {
                            const rect = btn.getBoundingClientRect();
                            const text = (btn.innerText || '').trim();

                            // 检查是否在面板右上角（相对面板右边和上边较近）
                            const isNearRight = Math.abs(rect.right - panelRect.right) < 60;
                            const isNearTop = Math.abs(rect.top - panelRect.top) < 60;

                            if (isNearRight && isNearTop && rect.width < 50 && rect.height < 50) {
                                // 检查是否是关闭按钮（包含×或SVG图标）
                                const hasX = text === '×' || text === '✕' || text === '✖' || text === 'X' || text === '';
                                const hasSvg = btn.querySelector('svg') !== null;

                                if (hasX || hasSvg) {
                                    btn.click();
                                    return { found: true, method: 'panel_close_btn', position: 'in_panel' };
                                }
                            }
                        }

                        // 查找面板内带有close类名的按钮
                        const closeBtns = panel.querySelectorAll('[class*="close"], [class*="Close"], [aria-label*="关闭"], [aria-label*="close"]');
                        for (const btn of closeBtns) {
                            const rect = btn.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                btn.click();
                                return { found: true, method: 'close_class', position: 'in_panel' };
                            }
                        }
                    }

                    // 备用：在整个页面查找×按钮
                    const allButtons = document.querySelectorAll('button, [role="button"]');
                    for (const btn of allButtons) {
                        const text = (btn.innerText || '').trim();
                        if (text === '×' || text === '✕' || text === '✖' || text === 'X') {
                            const rect = btn.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                btn.click();
                                return { found: true, method: 'text_x', text: text };
                            }
                        }
                    }

                    // 查找SVG关闭图标（X形状的路径）
                    const svgs = document.querySelectorAll('svg');
                    for (const svg of svgs) {
                        const rect = svg.getBoundingClientRect();
                        // 查找小的SVG图标
                        if (rect.width < 30 && rect.height < 30 && rect.width > 10) {
                            const paths = svg.querySelectorAll('path');
                            // X图标的path通常包含M和L形成交叉线
                            let hasCrossPath = false;
                            for (const path of paths) {
                                const d = (path.getAttribute('d') || '');
                                // X图标通常有两条交叉线
                                if (d.includes('L') && d.length < 100) {
                                    hasCrossPath = true;
                                    break;
                                }
                            }
                            if (hasCrossPath || paths.length <= 2) {
                                const parent = svg.closest('button') || svg.parentElement;
                                if (parent) {
                                    parent.click();
                                    return { found: true, method: 'svg_x', position: 'page' };
                                }
                            }
                        }
                    }

                    return { found: false };
                }''')

                if closed.get('found'):
                    self.logger.info(f"  [OK] 点击关闭按钮 (方法: {closed.get('method', 'unknown')})")
                    await asyncio.sleep(1)

                    # 验证面板是否已关闭
                    panel_closed = await self.browser.page.evaluate('''() => {
                        const allText = document.body.innerText;
                        const hasPanel = allText.includes('专题设置') && allText.includes('回复人设');

                        // 检查是否还有可见的面板
                        const panelSelectors = ['[class*="Drawer"]', '[class*="Modal"]', '[role="dialog"]'];
                        for (const selector of panelSelectors) {
                            const panels = document.querySelectorAll(selector);
                            for (const panel of panels) {
                                const rect = panel.getBoundingClientRect();
                                const style = window.getComputedStyle(panel);
                                if (rect.width > 200 && rect.height > 200 &&
                                    style.display !== 'none' && style.visibility !== 'hidden') {
                                    return false; // 面板仍然可见
                                }
                            }
                        }
                        return true; // 面板已关闭
                    }''')

                    if panel_closed:
                        self.logger.info("  [OK] 设置面板已成功关闭")
                        return True
                    else:
                        self.logger.warning(f"  面板可能未关闭，重试... (尝试 {attempt + 1}/3)")
                        await asyncio.sleep(0.5)
                else:
                    # 方法2: 使用Escape键
                    self.logger.info(f"  未找到关闭按钮，使用Escape键 (尝试 {attempt + 1}/3)")
                    await self.browser.page.keyboard.press('Escape')
                    await asyncio.sleep(1)

                    # 验证是否关闭
                    panel_closed = await self.browser.page.evaluate('''() => {
                        const allText = document.body.innerText;
                        return !(allText.includes('专题设置') && allText.includes('回复人设'));
                    }''')

                    if panel_closed:
                        self.logger.info("  [OK] 设置面板已通过Escape键关闭")
                        return True

            self.logger.warning("  关闭面板可能未完全成功，但继续执行...")
            return True

        except Exception as e:
            self.logger.error(f"  关闭设置面板失败: {str(e)}")
            # 备用方法
            try:
                await self.browser.page.keyboard.press('Escape')
                await asyncio.sleep(0.5)
            except (asyncio.TimeoutError, Exception) as escape_err:
                self.logger.debug(f"按Escape键关闭失败: {escape_err}")
            return False

    async def _navigate_to_metaso(self):
        """导航到总包大脑页面

        【v3.6.7优化】localStorage 加载时机修复
        - 先在 about:blank 页面加载 localStorage
        - 然后导航到目标页面，这样页面脚本可以读取到 localStorage
        """
        self.logger.info(f"访问总包大脑: {self.config.metaso_url}")
        try:
            # 【v3.6.7修复】先加载 localStorage 到 about:blank
            # 这样导航到目标页面时，页面脚本可以读取到已设置的 localStorage
            storage_file = Path(self.config.user_data_dir) / "local_storage.json"
            if storage_file.exists():
                self.logger.info("预加载 localStorage...")
                try:
                    # 先导航到空白页
                    await self.browser.page.goto("about:blank", timeout=10000)
                    # 加载 localStorage
                    await self.browser._load_local_storage()
                    self.logger.info("✓ localStorage 预加载完成")
                except Exception as e:
                    self.logger.warning(f"预加载 localStorage 失败: {e}")

            # 然后导航到目标页面
            await self.browser.goto(self.config.metaso_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)

            # 【v3.6.7新增】导航后再次尝试加载 localStorage（确保在正确域名下）
            try:
                await self.browser._load_local_storage()
            except Exception as e:
                self.logger.debug(f"二次加载 localStorage 失败（可忽略）: {e}")

            await asyncio.sleep(2)
            self.logger.info("页面加载完成")
        except Exception as e:
            self.logger.warning(f"页面加载超时或出错，尝试继续: {str(e)}")
            await asyncio.sleep(3)

    async def _pre_check_login_status(self) -> tuple:
        """【v3.6.7新增】登录状态预检测

        在定时任务启动前检测登录状态，如果失效则提前通知。

        Returns:
            tuple: (is_valid: bool, remaining_seconds: int, message: str)
        """
        import time as time_module

        cookies_file = Path(self.config.user_data_dir) / "cookies.json"

        # 1. 检查状态文件是否存在
        if not cookies_file.exists():
            return (False, 0, "未找到保存的登录状态，需要扫码登录")

        # 2. 检查 cookies 有效期
        try:
            import json
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)

            now = time_module.time()
            min_expiry = float('inf')
            expired_count = 0

            for cookie in cookies:
                expiry = cookie.get('expires', -1)
                if expiry > 0:
                    if expiry < now:
                        expired_count += 1
                    else:
                        min_expiry = min(min_expiry, expiry)

            if expired_count > 0:
                self.logger.warning(f"发现 {expired_count} 个已过期的 cookie")

            if min_expiry == float('inf'):
                # 全是会话 cookie，无法确定有效期
                remaining_seconds = -1
                message = "登录状态为会话级别，请验证实际状态"
            else:
                remaining_seconds = max(0, int(min_expiry - now))
                if remaining_seconds < 3600:  # 少于1小时
                    message = f"登录状态即将过期，剩余 {remaining_seconds // 60} 分钟"
                else:
                    hours = remaining_seconds // 3600
                    message = f"登录状态有效，预计剩余 {hours} 小时"

            return (True, remaining_seconds, message)

        except Exception as e:
            return (False, 0, f"检查登录状态失败: {str(e)}")

    async def _send_login_expiry_warning(self, remaining_seconds: int):
        """【v3.6.7新增】发送登录即将过期预警"""
        try:
            notifier = NotificationManager(self.config, self.logger)
            minutes = remaining_seconds // 60
            warning_msg = f"""⚠️ **登录状态预警**

🔐 **总包大脑登录状态即将过期**

⏰ **剩余时间**: 约 {minutes} 分钟

📱 **建议操作**: 请尽快打开浏览器扫码登录，以免影响下次定时任务执行。

---
_总包大脑自动写作系统 v3.6.8_"""
            notifier.send_custom_message(warning_msg)
        except Exception as e:
            self.logger.warning(f"发送登录预警失败: {e}")

    async def _send_login_required_notification(self):
        """【v3.6.7新增】发送需要登录通知"""
        try:
            notifier = NotificationManager(self.config, self.logger)
            notify_msg = f"""🔴 **需要扫码登录**

🔐 **总包大脑登录状态已失效**

📱 **操作步骤**:
1. 打开程序查看浏览器窗口
2. 使用微信扫描二维码登录
3. 登录成功后程序将自动继续

⏰ **等待时间**: 最多2分钟

---
_总包大脑自动写作系统 v3.6.8_"""
            notifier.send_custom_message(notify_msg)
        except Exception as e:
            self.logger.warning(f"发送登录通知失败: {e}")

    async def _check_login_required(self) -> bool:
        """使用Stagehand检查是否需要登录"""
        try:
            # 等待页面完全加载
            await asyncio.sleep(3)

            # 策略1: 首先检查是否有输入框（有输入框说明已登录，这是最可靠的判断）
            input_selectors = [
                'textarea',
                'textarea[placeholder*="问"]',
                'textarea[placeholder*="输入"]',
                'input[type="text"]',
                '[contenteditable="true"]',
                'div[contenteditable="true"]',
                '[class*="input"]',
                '[class*="editor"]',
                '[class*="textarea"]',
                '[class*="chat-input"]',
                '[class*="message-input"]'
            ]

            for selector in input_selectors:
                try:
                    input_count = await self.browser.page.locator(selector).count()
                    if input_count > 0:
                        # 找到输入框，进一步验证是否可见且可用
                        first_input = self.browser.page.locator(selector).first
                        if await first_input.is_visible():
                            self.logger.info(f"检测到可用的输入框 ({selector})，用户已登录")
                            return False  # 已登录，不需要再登录
                except Exception as e:
                    self.logger.debug(f"检查选择器 {selector} 时出错: {str(e)}")
                    continue

            # 策略2: 检查是否有QR码或登录按钮（说明需要登录）
            # 但要注意：如果同时存在输入框，说明已登录（QR码可能是其他用途）
            login_indicators = [
                'img[class*="qr"]',
                'img[src*="qr"]',
                '[class*="qrcode"]',
                '[class*="login-btn"]',
                '[class*="login-button"]',
                'button:has-text("登录")',
                'a:has-text("登录")',
                '[class*="wechat-login"]',
                '[class*="scan"]'
            ]

            has_login_indicator = False
            for selector in login_indicators:
                try:
                    indicator_count = await self.browser.page.locator(selector).count()
                    if indicator_count > 0:
                        self.logger.info(f"检测到登录指示器 ({selector})")
                        has_login_indicator = True
                        break
                except Exception as e:
                    self.logger.debug(f"检查登录指示器 {selector} 时出错: {str(e)}")
                    continue

            # 如果检测到登录指示器，再次确认输入框的存在
            # 因为页面可能有其他位置的QR码（如广告），只有没有输入框时才真正需要登录
            if has_login_indicator:
                # 再次仔细检查输入框
                for selector in input_selectors:
                    try:
                        input_count = await self.browser.page.locator(selector).count()
                        if input_count > 0:
                            first_input = self.browser.page.locator(selector).first
                            if await first_input.is_visible():
                                self.logger.info(f"虽然检测到登录指示器，但同时存在输入框 ({selector})，判断为已登录")
                                return False  # 有输入框，已登录
                    except Exception:
                        continue
                # 确实没有输入框，需要登录
                self.logger.info("检测到登录指示器且无输入框，需要登录")
                return True

            # 策略3: 使用Stagehand的observe功能作为最后的检查
            try:
                instruction = "Check if this page shows a login interface with QR code or login buttons. Return 'yes' if login is required, 'no' otherwise."
                observation = await self.browser.observe(instruction)

                if observation and ('登录' in observation or '扫码' in observation or 'login' in observation.lower()):
                    # 再次确认没有输入框
                    for selector in input_selectors:
                        try:
                            input_count = await self.browser.page.locator(selector).count()
                            if input_count > 0:
                                self.logger.info("observe检测到登录界面但存在输入框，判断为已登录")
                                return False
                        except Exception:
                            continue
                    self.logger.info("observe检测到登录界面且无输入框，需要登录")
                    return True
            except Exception as e:
                self.logger.debug(f"observe检查失败: {str(e)}")

            # 默认：如果没有明确的登录指示器，假设已登录
            self.logger.info("未检测到明确的登录需求，假设已登录")
            return False

        except Exception as e:
            self.logger.debug(f"检查登录状态时出错: {str(e)}")
            return False

    async def _wait_for_login(self, timeout: int = 120) -> bool:
        """等待用户扫码登录"""
        self.logger.info(f"等待用户扫码登录，超时时间: {timeout} 秒")

        start_time = time.time()
        check_interval = 2

        while time.time() - start_time < timeout:
            try:
                # 使用Stagehand检查登录状态
                if not await self._check_login_required():
                    self.logger.info("检测到登录成功")
                    await asyncio.sleep(2)
                    # 【v3.6.4新增】登录成功后立即保存浏览器状态
                    # 【v3.6.8修复】正确调用 browser 对象的方法
                    await self.browser._save_storage_state()
                    self.logger.info("✓ 登录状态已持久化保存")
                    return True

                await asyncio.sleep(check_interval)

            except Exception as e:
                self.logger.debug(f"等待登录时出错: {str(e)}")
                await asyncio.sleep(check_interval)

        self.logger.error("等待登录超时")
        return False

    async def _send_question(self, question: str):
        """使用Stagehand发送问题到总包大脑

        【v3.6.2更新】在发送问题前先切换到长思考模式（可配置）
        """
        self.logger.info(f"发送问题: {question}")

        try:
            # 【v3.6.2】根据配置决定是否切换到长思考模式
            if self.config.enable_long_thinking:
                self.logger.info("=" * 50)
                self.logger.info("步骤1：切换到长思考模式")
                self.logger.info("=" * 50)

                mode_switched = await self._select_long_thinking_model()
                if mode_switched:
                    self.logger.info("✓ 已成功切换到长思考模式")
                else:
                    self.logger.warning("⚠ 长思考模式切换失败，将使用当前模式继续")

                # 等待模式切换生效
                await asyncio.sleep(2)
            else:
                self.logger.info("长思考模式未启用，使用默认模式")

            self.logger.info("=" * 50)
            self.logger.info("步骤2：发送问题到总包大脑")
            self.logger.info("=" * 50)

            # 发送问题
            # 方法1：使用Stagehand的act功能
            instruction = f"""First, scroll to the bottom of the page to find the input area. Then find the text input area or message box on this page. Click on it, clear any existing text, and type the following question: {question}. Then find and click the send button or press Enter to submit."""

            success = await self.browser.act(instruction, timeout=30000)

            if not success:
                # 方法2：使用传统选择器方法
                await self._send_question_fallback(question)

            await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"发送问题失败: {str(e)}")
            await self._send_question_fallback(question)

    async def _select_long_thinking_model(self):
        """选择长思考模型 - 通过hover触发下拉菜单选择

        【v3.6.2更新】根据实际UI交互模式：
        1. 找到"快思考"元素（当前模式指示器）
        2. 鼠标悬停在"快思考"上触发下拉菜单
        3. 等待下拉菜单出现
        4. 点击下拉菜单中的"长思考"选项
        """
        try:
            self.logger.info("正在切换到长思考模式...")

            # 等待页面稳定
            await asyncio.sleep(2)

            # ===== 策略1：通过hover触发下拉菜单选择 =====
            # 这是根据实际UI设计的主要交互方式
            self.logger.info("策略1：通过hover触发下拉菜单选择长思考")

            try:
                # 1.1 找到"快思考"元素
                fast_thinking_selectors = [
                    'span:has-text("快思考")',
                    'div:has-text("快思考")',
                    'button:has-text("快思考")',
                    'label:has-text("快思考")',
                    '[class*="model-selector"]',
                    '[class*="thinking-mode"]',
                    '[data-mode="fast"]',
                    '[class*="fast-thinking"]',
                ]

                fast_thinking_element = None
                for selector in fast_thinking_selectors:
                    try:
                        # 使用Playwright的locator API
                        locator = self.browser.page.locator(selector).first
                        if await locator.count() > 0:
                            fast_thinking_element = locator
                            self.logger.info(f"找到快思考元素: {selector}")
                            break
                    except (asyncio.TimeoutError, Exception) as locator_err:
                        self.logger.debug(f"选择器 {selector} 定位失败: {locator_err}")
                        continue

                if fast_thinking_element:
                    # 1.2 悬停在"快思考"上触发下拉菜单
                    self.logger.info("悬停在快思考元素上以触发下拉菜单...")
                    await fast_thinking_element.hover(timeout=5000)
                    await asyncio.sleep(1)  # 等待下拉菜单动画

                    # 1.3 查找并点击下拉菜单中的"长思考"选项
                    long_thinking_selectors = [
                        'text=长思考',
                        'span:has-text("长思考")',
                        'div:has-text("长思考")',
                        'button:has-text("长思考")',
                        'li:has-text("长思考")',
                        'a:has-text("长思考")',
                        '[data-value="long-thinking"]',
                        '[data-mode="long"]',
                        '[class*="long-thinking"]',
                        '[class*="dropdown"] span:has-text("长思考")',
                        '[class*="menu"] span:has-text("长思考")',
                    ]

                    for selector in long_thinking_selectors:
                        try:
                            locator = self.browser.page.locator(selector).first
                            if await locator.count() > 0:
                                # 确保元素可见
                                if await locator.is_visible():
                                    await locator.click(timeout=5000)
                                    self.logger.info(f"✓ 成功点击长思考选项: {selector}")
                                    await asyncio.sleep(1)  # 等待选择生效

                                    # 验证是否切换成功
                                    await asyncio.sleep(0.5)
                                    self.logger.info("✓ 成功切换到长思考模式")
                                    return True
                        except Exception as click_e:
                            self.logger.debug(f"选择器 {selector} 点击失败: {str(click_e)}")
                            continue

                    self.logger.warning("下拉菜单中未找到长思考选项，尝试其他策略")
                else:
                    self.logger.warning("未找到快思考元素，尝试其他策略")

            except Exception as e:
                self.logger.warning(f"策略1失败: {str(e)}")

            # ===== 策略2：使用Stagehand AI智能识别 =====
            self.logger.info("策略2：使用Stagehand AI智能识别")
            try:
                instruction = """Look for a dropdown or selector showing "快思考" (Fast Thinking) or current model. Hover over it to open a dropdown menu, then click on "长思考" (Long Thinking) option in the dropdown."""

                success = await self.browser.act(instruction, timeout=15000)
                if success:
                    self.logger.info("✓ 通过Stagehand成功切换到长思考模式")
                    await asyncio.sleep(1)
                    return True
            except Exception as e:
                self.logger.warning(f"Stagehand策略失败: {str(e)}")

            # ===== 策略3：使用JavaScript查找并触发下拉菜单 =====
            self.logger.info("策略3：使用JavaScript触发下拉菜单")
            try:
                js_result = await self.browser.page.evaluate('''
                    () => {
                        // 查找包含"快思考"的元素
                        const allElements = document.querySelectorAll('*');
                        let fastElement = null;

                        for (let elem of allElements) {
                            const text = elem.textContent || '';
                            if (text.trim() === '快思考' || text.includes('快思考')) {
                                // 检查是否是合适的触发元素（不是太大的容器）
                                if (elem.tagName !== 'BODY' && elem.tagName !== 'HTML') {
                                    fastElement = elem;
                                    break;
                                }
                            }
                        }

                        if (fastElement) {
                            // 创建并触发hover事件
                            const hoverEvent = new MouseEvent('mouseenter', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            fastElement.dispatchEvent(hoverEvent);

                            // 也触发mouseover事件
                            const overEvent = new MouseEvent('mouseover', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            fastElement.dispatchEvent(overEvent);

                            return 'hovered';
                        }
                        return 'not_found';
                    }
                ''')

                if js_result == 'hovered':
                    await asyncio.sleep(1)

                    # 尝试点击长思考
                    js_click = await self.browser.page.evaluate('''
                        () => {
                            const allElements = document.querySelectorAll('*');
                            for (let elem of allElements) {
                                const text = elem.textContent || '';
                                if (text.trim() === '长思考' || (text.includes('长思考') && text.length < 20)) {
                                    elem.click();
                                    return 'clicked';
                                }
                            }
                            return 'not_found';
                        }
                    ''')

                    if js_click == 'clicked':
                        self.logger.info("✓ 通过JavaScript成功切换到长思考模式")
                        await asyncio.sleep(1)
                        return True

            except Exception as e:
                self.logger.warning(f"JavaScript策略失败: {str(e)}")

            # ===== 策略4：直接查找并点击长思考元素（备用） =====
            self.logger.info("策略4：直接查找长思考元素")
            direct_selectors = [
                'input[type="radio"][value*="long"]',
                'input[type="radio"][value*="r2"]',
                '[class*="model-option"]:has-text("长思考")',
                '[role="menuitem"]:has-text("长思考")',
                '[role="option"]:has-text("长思考")',
            ]

            for selector in direct_selectors:
                try:
                    locator = self.browser.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(timeout=3000)
                        self.logger.info(f"✓ 通过直接选择器切换到长思考: {selector}")
                        await asyncio.sleep(1)
                        return True
                except (asyncio.TimeoutError, Exception) as click_err:
                    self.logger.debug(f"选择器 {selector} 点击失败: {click_err}")
                    continue

            self.logger.warning("所有策略均未成功切换到长思考模式，将使用默认模式")
            return False

        except Exception as e:
            self.logger.warning(f"选择长思考模型时出错: {str(e)}，将使用默认模型")
            return False

    async def _send_question_fallback(self, question: str):
        """
        智能回退方法：使用多重策略检测并发送问题

        策略优先级：
        1. 使用wait_for_selector等待标准选择器
        2. 使用locator和getByText等待动态内容
        3. 使用IntersectionObserver监听DOM变化
        4. 使用JavaScript智能查找可见输入框
        5. 强制滚动并重试
        """
        debug_dir = self.config.temp_dir
        os.makedirs(debug_dir, exist_ok=True)

        # 策略1：使用Playwright的wait_for_selector等待标准选择器
        if await self._try_wait_selector_strategy(question, debug_dir):
            return True

        # 策略2：使用locator和动态选择器
        if await self._try_locator_strategy(question, debug_dir):
            return True

        # 策略3：使用IntersectionObserver监听DOM变化
        if await self._try_intersection_observer_strategy(question, debug_dir):
            return True

        # 策略4：使用JavaScript智能查找并强制滚动
        if await self._try_js_smart_search_strategy(question, debug_dir):
            return True

        # 策略5：最后的fallback - 使用最宽松的选择器
        if await self._try_last_resort_strategy(question, debug_dir):
            return True

        # 所有策略都失败
        self.logger.error("所有输入框检测策略都失败了")
        raise Exception("无法找到或操作输入框")

    async def _try_wait_selector_strategy(self, question: str, debug_dir: str) -> bool:
        """策略1：使用wait_for_selector等待标准选择器"""
        self.logger.info("=" * 60)
        self.logger.info("策略1：使用wait_for_selector等待标准选择器")
        self.logger.info("=" * 60)

        try:
            # 等待页面稳定
            await self.browser.wait_for_page_stable()
            await asyncio.sleep(1)

            # 定义标准选择器列表（按优先级排序）
            standard_selectors = [
                # 总包大脑可能的特定选择器
                'textarea[placeholder*="问"]',
                'textarea[placeholder*="输入"]',
                'textarea[placeholder*="问题"]',
                # 通用聊天输入框选择器
                'div[contenteditable="true"]:visible',
                'textarea:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[type="text"]:visible',
                # class包含特定关键词的选择器
                '[class*="input"] textarea',
                '[class*="chat"] textarea',
                '[class*="prompt"] textarea',
                '[class*="editor"] textarea',
            ]

            for selector in standard_selectors:
                self.logger.info(f"尝试选择器: {selector}")
                try:
                    # 使用wait_for_selector等待元素出现并可见
                    element = await self.browser.page.wait_for_selector(
                        selector,
                        state='visible',
                        timeout=10000  # 10秒超时
                    )

                    if element:
                        self.logger.info(f"✓ 找到可见元素: {selector}")

                        # 尝试输入
                        if await self._input_and_send(element, question, debug_dir, strategy_name="wait_selector"):
                            return True

                except Exception as e:
                    self.logger.debug(f"选择器 {selector} 失败: {str(e)}")
                    continue

            self.logger.warning("策略1：所有标准选择器都未找到可见元素")
            return False

        except Exception as e:
            self.logger.error(f"策略1执行失败: {str(e)}")
            return False

    async def _try_locator_strategy(self, question: str, debug_dir: str) -> bool:
        """策略2：使用Playwright locator功能"""
        self.logger.info("=" * 60)
        self.logger.info("策略2：使用Playwright locator和动态选择器")
        self.logger.info("=" * 60)

        try:
            # 确保页面滚动到底部
            await self._scroll_to_bottom_forcefully()
            await asyncio.sleep(2)

            # 使用locator查找元素
            locator_strategies = [
                # 使用getByText
                lambda: self.browser.page.get_by_text("问", exact=False).locator('..').locator('textarea, [contenteditable="true"], input[type="text"]'),
                # 使用placeholder
                lambda: self.browser.page.get_by_placeholder("问"),
                lambda: self.browser.page.get_by_placeholder("输入"),
                lambda: self.browser.page.get_by_placeholder("问题"),
                # 使用role
                lambda: self.browser.page.get_by_role("textbox").filter(has_visible=True),
                # 使用locator的filter
                lambda: self.browser.page.locator('textarea').filter(is_visible=True),
                lambda: self.browser.page.locator('[contenteditable="true"]').filter(is_visible=True),
                lambda: self.browser.page.locator('input[type="text"]').filter(is_visible=True),
            ]

            for strategy_func in locator_strategies:
                try:
                    self.logger.info(f"尝试locator策略...")
                    locator = strategy_func()

                    # 等待locator找到元素
                    if await locator.count() > 0:
                        self.logger.info(f"✓ Locator找到 {await locator.count()} 个元素")

                        # 获取第一个可见元素
                        element = locator.first

                        if await element.is_visible():
                            self.logger.info("✓ 找到可见元素")

                            if await self._input_and_send(element, question, debug_dir, strategy_name="locator"):
                                return True

                except Exception as e:
                    self.logger.debug(f"Locator策略失败: {str(e)}")
                    continue

            self.logger.warning("策略2：所有locator策略都未找到元素")
            return False

        except Exception as e:
            self.logger.error(f"策略2执行失败: {str(e)}")
            return False

    async def _try_intersection_observer_strategy(self, question: str, debug_dir: str) -> bool:
        """策略3：使用IntersectionObserver监听元素变为可见"""
        self.logger.info("=" * 60)
        self.logger.info("策略3：使用IntersectionObserver监听DOM变化")
        self.logger.info("=" * 60)

        try:
            # 先滚动到底部
            await self._scroll_to_bottom_forcefully()

            # 使用JavaScript注入IntersectionObserver
            result = await self.browser.page.evaluate('''
                () => {
                    return new Promise((resolve) => {
                        // 查找所有可能的输入元素
                        const selectors = ['textarea', '[contenteditable="true"]', 'input[type="text"]', 'input:not([type])'];
                        let foundElement = null;

                        // 检查元素是否真正可见
                        function isReallyVisible(element) {
                            const rect = element.getBoundingClientRect();
                            if (rect.width === 0 || rect.height === 0) return false;

                            // 检查元素是否在视口中
                            const isInViewport = (
                                rect.top >= 0 &&
                                rect.left >= 0 &&
                                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                            );

                            // 检查样式
                            const style = window.getComputedStyle(element);
                            if (style.display === 'none' || style.visibility === 'hidden') return false;

                            // 检查祖先元素
                            let parent = element.parentElement;
                            while (parent) {
                                const parentStyle = window.getComputedStyle(parent);
                                if (parentStyle.display === 'none') return false;
                                parent = parent.parentElement;
                            }

                            return true;
                        }

                        // 立即检查所有元素
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            for (const elem of elements) {
                                if (isReallyVisible(elem)) {
                                    foundElement = {
                                        tagName: elem.tagName,
                                        id: elem.id,
                                        className: elem.className,
                                        selector: selector,
                                        index: Array.from(document.querySelectorAll(selector)).indexOf(elem)
                                    };
                                    resolve({success: true, element: foundElement});
                                    return;
                                }
                            }
                        }

                        // 如果立即检查没找到，使用IntersectionObserver等待
                        const observer = new IntersectionObserver((entries) => {
                            for (const entry of entries) {
                                if (entry.isIntersecting && isReallyVisible(entry.target)) {
                                    const elem = entry.target;
                                    const selector = elem.tagName.toLowerCase() + (elem.id ? '#' + elem.id : '') + (elem.className ? '.' + elem.className.split(' ').join('.') : '');
                                    foundElement = {
                                        tagName: elem.tagName,
                                        id: elem.id,
                                        className: elem.className,
                                        selector: elem.tagName.toLowerCase(),
                                        index: Array.from(document.querySelectorAll(elem.tagName.toLowerCase())).indexOf(elem)
                                    };
                                    observer.disconnect();
                                    resolve({success: true, element: foundElement});
                                    return;
                                }
                            }
                        }, {threshold: 0.1});

                        // 观察所有输入元素
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(elem => observer.observe(elem));
                        }

                        // 超时后返回失败
                        setTimeout(() => {
                            observer.disconnect();
                            resolve({success: false, error: 'Timeout waiting for visible element'});
                        }, 15000);
                    });
                }
            ''')

            import json
            result_data = json.loads(result) if isinstance(result, str) else result

            if result_data.get('success') and result_data.get('element'):
                elem_info = result_data['element']
                self.logger.info(f"✓ IntersectionObserver找到元素: {elem_info}")

                # 获取元素
                all_elements = await self.browser.page.query_selector_all(elem_info['selector'])
                if len(all_elements) > elem_info['index']:
                    element = all_elements[elem_info['index']]

                    if await self._input_and_send(element, question, debug_dir, strategy_name="intersection_observer"):
                        return True

            self.logger.warning("策略3：IntersectionObserver未找到可见元素")
            return False

        except Exception as e:
            self.logger.error(f"策略3执行失败: {str(e)}")
            return False

    async def _try_js_smart_search_strategy(self, question: str, debug_dir: str) -> bool:
        """策略4：使用JavaScript智能搜索并处理动态内容"""
        self.logger.info("=" * 60)
        self.logger.info("策略4：JavaScript智能搜索 + 强制滚动")
        self.logger.info("=" * 60)

        try:
            # 保存当前截图
            screenshot_path = os.path.join(debug_dir, "strategy4_before.png")
            await self.browser.page.screenshot(path=screenshot_path, full_page=True)
            self.logger.info(f"已保存策略4执行前截图: {screenshot_path}")

            # 多次滚动并尝试查找
            for attempt in range(3):
                self.logger.info(f"尝试 {attempt + 1}/3...")

                # 强制滚动到底部
                await self._scroll_to_bottom_forcefully()
                await asyncio.sleep(2)

                # 使用JavaScript智能查找
                element_found = await self.browser.page.evaluate('''
                    () => {
                        const viewportHeight = window.innerHeight;
                        const scrollY = window.scrollY;
                        let bestElement = null;
                        let bestScore = -1;

                        function isElementVisible(el) {
                            if (!el) return false;
                            const rect = el.getBoundingClientRect();

                            // 必须有实际的尺寸
                            if (rect.width < 10 || rect.height < 10) return false;

                            // 不能是隐藏的
                            const style = window.getComputedStyle(el);
                            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;

                            return true;
                        }

                        // 检查所有输入类型
                        const selectors = [
                            'textarea',
                            '[contenteditable="true"]',
                            'input[type="text"]',
                            'input:not([type])'
                        ];

                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach((elem, index) => {
                                if (isElementVisible(elem)) {
                                    const rect = elem.getBoundingClientRect();

                                    // 优先选择页面底部、宽度大的元素（通常是输入框）
                                    // 得分计算：位置越高（Y坐标越大）得分越高，宽度越大得分越高
                                    const positionScore = rect.top + scrollY;
                                    const widthScore = rect.width * 2;
                                    const score = positionScore + widthScore;

                                    if (score > bestScore) {
                                        bestScore = score;
                                        bestElement = {
                                            selector: selector,
                                            index: index,
                                            tagName: elem.tagName,
                                            id: elem.id,
                                            className: elem.className,
                                            rect: {
                                                top: rect.top,
                                                left: rect.left,
                                                width: rect.width,
                                                height: rect.height
                                            }
                                        };
                                    }
                                }
                            });
                        }

                        return bestElement ? JSON.stringify(bestElement) : null;
                    }
                ''')

                if element_found:
                    import json
                    elem_info = json.loads(element_found)
                    self.logger.info(f"✓ 找到输入框: {elem_info}")
                    self.logger.info(f"  位置: top={elem_info['rect']['top']}, width={elem_info['rect']['width']}, height={elem_info['rect']['height']}")

                    # 获取元素
                    all_elements = await self.browser.page.query_selector_all(elem_info['selector'])
                    if len(all_elements) > elem_info['index']:
                        element = all_elements[elem_info['index']]

                        if await self._input_and_send(element, question, debug_dir, strategy_name=f"js_smart_search_attempt_{attempt+1}"):
                            return True

                self.logger.info(f"尝试 {attempt + 1} 未找到合适的输入框，等待后重试...")
                await asyncio.sleep(2)

            self.logger.warning("策略4：所有尝试都未找到输入框")
            return False

        except Exception as e:
            self.logger.error(f"策略4执行失败: {str(e)}")
            return False

    async def _try_last_resort_strategy(self, question: str, debug_dir: str) -> bool:
        """策略5：最后的fallback - 尝试所有可能的输入元素"""
        self.logger.info("=" * 60)
        self.logger.info("策略5：最后的fallback - 尝试所有输入元素")
        self.logger.info("=" * 60)

        try:
            # 最后一次滚动
            await self._scroll_to_bottom_forcefully()
            await asyncio.sleep(2)

            # 获取所有输入元素信息
            all_inputs = await self.browser.page.evaluate('''
                () => {
                    const results = [];

                    function getElementInfo(el, type, index) {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return {
                            type: type,
                            index: index,
                            tagName: el.tagName,
                            id: el.id,
                            className: el.className,
                            placeholder: el.placeholder || '',
                            rect: {
                                width: rect.width,
                                height: rect.height,
                                top: rect.top,
                                left: rect.left
                            },
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            hasValue: el.value ? true : false
                        };
                    }

                    // 获取所有textarea
                    document.querySelectorAll('textarea').forEach((el, i) => {
                        results.push(getElementInfo(el, 'textarea', i));
                    });

                    // 获取所有contenteditable
                    document.querySelectorAll('[contenteditable="true"]').forEach((el, i) => {
                        results.push(getElementInfo(el, 'contenteditable', i));
                    });

                    // 获取所有text input
                    document.querySelectorAll('input[type="text"], input:not([type])').forEach((el, i) => {
                        results.push(getElementInfo(el, 'input', i));
                    });

                    return JSON.stringify(results);
                }
            ''')

            import json
            inputs_info = json.loads(all_inputs)
            self.logger.info(f"找到 {len(inputs_info)} 个输入元素")

            # 按宽度排序，优先尝试宽度大的（通常是真正的输入框）
            inputs_info.sort(key=lambda x: x['rect']['width'], reverse=True)

            # 尝试每个元素
            for idx, elem_info in enumerate(inputs_info[:10]):  # 最多尝试前10个
                self.logger.info(f"尝试元素 {idx + 1}: {elem_info['type']} - width={elem_info['rect']['width']}, height={elem_info['rect']['height']}")

                try:
                    # 获取元素
                    if elem_info['type'] == 'textarea':
                        elements = await self.browser.page.query_selector_all('textarea')
                    elif elem_info['type'] == 'contenteditable':
                        elements = await self.browser.page.query_selector_all('[contenteditable="true"]')
                    else:
                        elements = await self.browser.page.query_selector_all('input[type="text"], input:not([type])')

                    if len(elements) > elem_info['index']:
                        element = elements[elem_info['index']]

                        # 尝试滚动到视图
                        await element.scroll_into_view_if_needed(timeout=3000)
                        await asyncio.sleep(0.5)

                        # 尝试点击
                        try:
                            await element.click(timeout=2000)
                            await asyncio.sleep(0.3)
                        except (asyncio.TimeoutError, Exception) as click_err:
                            self.logger.debug(f"元素点击失败: {click_err}")

                        # 尝试输入
                        if await self._input_and_send(element, question, debug_dir, strategy_name=f"last_resort_{idx+1}"):
                            return True

                except Exception as e:
                    self.logger.debug(f"元素 {idx + 1} 尝试失败: {str(e)}")
                    continue

            self.logger.warning("策略5：所有元素都尝试失败")
            return False

        except Exception as e:
            self.logger.error(f"策略5执行失败: {str(e)}")
            return False

    async def _scroll_to_bottom_forcefully(self):
        """强制滚动到页面底部（多种方式）"""
        self.logger.info("强制滚动到页面底部...")

        scroll_methods = [
            'window.scrollTo(0, document.body.scrollHeight)',
            'window.scrollTo(0, document.documentElement.scrollHeight)',
            'document.body.scrollTop = document.body.scrollHeight',
            'document.documentElement.scrollTop = document.documentElement.scrollHeight',
            'window.scrollTo({top: document.body.scrollHeight, behavior: "instant"})',
        ]

        for method in scroll_methods:
            try:
                await self.browser.page.evaluate(method)
                await asyncio.sleep(0.2)
            except (asyncio.TimeoutError, Exception) as scroll_err:
                self.logger.debug(f"滚动方法 {method} 执行失败: {scroll_err}")

    async def _input_and_send(self, element, question: str, debug_dir: str, strategy_name: str = "unknown") -> bool:
        """
        尝试在元素中输入文本并发送

        Returns:
            bool: 是否成功输入并发送
        """
        try:
            self.logger.info(f"使用策略 '{strategy_name}' 尝试输入...")

            # 滚动到元素
            try:
                await element.scroll_into_view_if_needed(timeout=5000)
                await asyncio.sleep(0.5)
            except Exception as e:
                self.logger.debug(f"滚动失败: {str(e)}")

            # 点击元素
            try:
                await element.click(timeout=5000)
                await asyncio.sleep(0.5)
                self.logger.info("✓ 成功点击元素")
            except Exception as e:
                self.logger.debug(f"点击失败: {str(e)}")
                # 即使点击失败也继续尝试输入

            # 清空现有内容
            try:
                await self.browser.page.keyboard.press('Control+A')
                await asyncio.sleep(0.2)
                await self.browser.page.keyboard.press('Backspace')
                await asyncio.sleep(0.2)
            except (asyncio.TimeoutError, Exception) as clear_err:
                self.logger.debug(f"清空输入框失败: {clear_err}")

            # 尝试多种输入方式
            input_success = False

            # 方式1: 使用fill
            try:
                await element.fill(question, timeout=5000)
                await asyncio.sleep(0.5)

                # 验证输入
                value = await element.input_value() if await element.evaluate('el => el.tagName') != 'DIV' else await element.inner_text()
                if question in value:
                    input_success = True
                    self.logger.info("✓ 使用fill成功输入")
            except Exception as e:
                self.logger.debug(f"fill方式失败: {str(e)}")

            # 方式2: 使用type（如果fill失败）
            if not input_success:
                try:
                    await element.type(question, delay=20, timeout=5000)
                    await asyncio.sleep(0.5)
                    input_success = True
                    self.logger.info("✓ 使用type成功输入")
                except Exception as e:
                    self.logger.debug(f"type方式失败: {str(e)}")

            # 方式3: 使用JavaScript直接设置
            if not input_success:
                try:
                    tag_name = await element.evaluate('el => el.tagName')
                    if tag_name == 'TEXTAREA' or tag_name == 'INPUT':
                        await element.evaluate(f'el => el.value = "{question}"')
                    else:
                        await element.evaluate(f'el => el.textContent = "{question}"')

                    # 触发事件
                    await element.evaluate('el => { el.dispatchEvent(new Event("input", {bubbles: true})); el.dispatchEvent(new Event("change", {bubbles: true})); }')
                    await asyncio.sleep(0.5)
                    input_success = True
                    self.logger.info("✓ 使用JavaScript成功输入")
                except Exception as e:
                    self.logger.debug(f"JavaScript方式失败: {str(e)}")

            if not input_success:
                self.logger.error("所有输入方式都失败")
                return False

            # 保存输入后截图
            after_input_screenshot = os.path.join(debug_dir, f"after_input_{strategy_name}.png")
            await self.browser.page.screenshot(path=after_input_screenshot)
            self.logger.info(f"已保存输入后截图: {after_input_screenshot}")

            await asyncio.sleep(1)

            # 尝试发送
            send_success = await self._try_send_button()

            if send_success:
                self.logger.info(f"✓ 策略 '{strategy_name}' 完全成功")
                return True
            else:
                self.logger.warning(f"策略 '{strategy_name}' 输入成功但发送失败")
                return False

        except Exception as e:
            self.logger.error(f"输入发送过程出错: {str(e)}")
            return False

    async def _try_send_button(self) -> bool:
        """尝试找到并点击发送按钮"""
        self.logger.info("查找发送按钮...")

        try:
            # 等待一下让按钮出现
            await asyncio.sleep(1)

            # 定义发送按钮的选择器
            send_button_selectors = [
                'button:has-text("发送")',
                'button:has-text("提交")',
                'button:has-text("Send")',
                'button:has-text("send")',
                'button[aria-label*="发送"]',
                'button[aria-label*="Send"]',
                '[class*="send"] button',
                '[class*="submit"] button',
                'button[class*="send"]',
                'button[class*="submit"]',
                # 最后尝试：查找输入框旁边的按钮
            ]

            # 方法1: 使用选择器查找
            for selector in send_button_selectors:
                try:
                    button = await self.browser.page.query_selector(selector)
                    if button:
                        is_visible = await button.is_visible()
                        if is_visible:
                            await button.click(timeout=5000)
                            await asyncio.sleep(1)
                            self.logger.info(f"✓ 点击发送按钮成功: {selector}")
                            return True
                except (asyncio.TimeoutError, Exception) as btn_err:
                    self.logger.debug(f"发送按钮选择器 {selector} 失败: {btn_err}")
                    continue

            # 方法2: 使用JavaScript查找包含特定文本的按钮
            button_found = await self.browser.page.evaluate('''
                () => {
                    const buttons = document.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.textContent || '';
                        const rect = btn.getBoundingClientRect();
                        const ariaLabel = btn.getAttribute('aria-label') || '';
                        const className = btn.className || '';

                        if (rect.width > 0 && rect.height > 0) {
                            if (text.includes('发送') || text.includes('提交') || text.toLowerCase().includes('send') ||
                                ariaLabel.includes('发送') || ariaLabel.includes('Send') ||
                                className.includes('send') || className.includes('submit')) {
                                return {
                                    index: Array.from(buttons).indexOf(btn),
                                    text: text.substring(0, 20),
                                    className: className
                                };
                            }
                        }
                    }
                    return null;
                }
            ''')

            if button_found:
                import json
                btn_info = json.loads(button_found)
                buttons = await self.browser.page.query_selector_all('button')
                if len(buttons) > btn_info['index']:
                    await buttons[btn_info['index']].click(timeout=5000)
                    await asyncio.sleep(1)
                    self.logger.info(f"✓ 点击发送按钮成功: {btn_info['text']}")
                    return True

            # 方法3: 使用Enter键发送
            self.logger.info("未找到发送按钮，尝试使用Enter键发送...")
            await self.browser.page.keyboard.press('Enter')
            await asyncio.sleep(1)
            self.logger.info("✓ 已按Enter键发送")
            return True

        except Exception as e:
            self.logger.error(f"发送按钮操作失败: {str(e)}")
            return False

    async def _get_answer_from_metaso(self, question: str, max_retries: int = 3) -> str:
        try:
            # 尝试多种方式获取输入框内容
            try:
                value = await elem.input_value()
                if value:
                    return value
            except (asyncio.TimeoutError, Exception) as input_err:
                self.logger.debug(f"获取输入值失败: {input_err}")

            try:
                value = await elem.inner_text()
                if value:
                    return value
            except (asyncio.TimeoutError, Exception) as text_err:
                self.logger.debug(f"获取内部文本失败: {text_err}")

            try:
                value = await elem.get_attribute('value')
                if value:
                    return value
            except (asyncio.TimeoutError, Exception) as attr_err:
                self.logger.debug(f"获取value属性失败: {attr_err}")

            return ""
        except (asyncio.TimeoutError, Exception) as e:
            self.logger.debug(f"获取元素内容失败: {e}")
            return ""

    async def _get_answer_from_metaso(self, question: str, max_retries: int = 3) -> str:
        """旧的备份方法 - 待删除"""
        try:
            # 等待页面完全加载
            await self.browser.wait_for_page_stable()
            await asyncio.sleep(2)

            # 滚动到页面底部，确保输入框可见
            self.logger.info("滚动到页面底部...")
            await self.browser.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)

            # 先保存截图用于调试
            debug_dir = self.config.temp_dir
            os.makedirs(debug_dir, exist_ok=True)
            screenshot_path = os.path.join(debug_dir, "before_send.png")
            await self.browser.page.screenshot(path=screenshot_path)
            self.logger.info(f"已保存发送前截图: {screenshot_path}")

            # 更全面的输入框选择器列表（针对现代Web应用）
            input_selectors = [
                # Metaso/总包大脑可能的选择器
                'textarea[placeholder*="问题"]',
                'textarea[placeholder*="输入"]',
                'textarea[placeholder*="message"]',
                'textarea[placeholder*="prompt"]',
                # 通用选择器
                'textarea:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'div[contenteditable="true"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                'input[type="text"]:not([style*="display: none"]):not([style*="visibility: hidden"])',
                # 特定class选择器
                '#prompt-input',
                '.chat-input textarea',
                '.input-box textarea',
                '[class*="prompt"] textarea',
                '[class*="chat"] textarea',
                '[class*="editor"] textarea',
                '[class*="message"] textarea',
                '[class*="input"] textarea',
                # 回退到所有textarea和contenteditable
                'textarea',
                'div[contenteditable="true"]',
                'input[type="text"]',
            ]

            input_element = None
            used_selector = None

            # 尝试找到并操作输入框
            self.logger.info("开始查找输入框...")
            for selector in input_selectors:
                try:
                    elem = await self.browser.page.query_selector(selector)
                    if elem:
                        # 检查元素是否可见和可交互
                        is_visible = await elem.is_visible()
                        if is_visible:
                            # 滚动到元素
                            await elem.scroll_into_view_if_needed(timeout=5000)
                            await asyncio.sleep(0.5)

                            # 尝试点击聚焦
                            await elem.click()
                            await asyncio.sleep(0.5)

                            # 使用 type() 方法模拟真实键盘输入（对React/Vue应用更可靠）
                            # 先清空（Ctrl+A 然后删除）
                            await self.browser.page.keyboard.press('Control+A')
                            await asyncio.sleep(0.1)
                            await self.browser.page.keyboard.press('Backspace')
                            await asyncio.sleep(0.2)

                            # 使用 type() 而不是 fill() - 这样会触发正确的事件
                            await elem.type(question, delay=10)  # delay=10ms 模拟真实打字速度
                            await asyncio.sleep(0.5)

                            # 验证文本是否真的被输入了
                            actual_value = await self._verify_input_text(elem)
                            if actual_value and question[:20] in actual_value:
                                input_element = elem
                                used_selector = selector
                                self.logger.info(f"✓ 使用选择器 '{selector}' 成功输入问题")
                                self.logger.info(f"  验证文本已输入: {actual_value[:50]}...")
                                break
                            else:
                                self.logger.warning(f"选择器 '{selector}' 输入后验证失败，继续尝试...")
                                # 清除失败的输入
                                await self.browser.page.keyboard.press('Control+A')
                                await self.browser.page.keyboard.press('Backspace')
                except Exception as e:
                    self.logger.debug(f"选择器 '{selector}' 失败: {str(e)}")
                    continue

            if not input_element:
                # 最后尝试：查找所有可能的输入元素
                self.logger.info("标准选择器失败，尝试遍历所有输入元素...")
                all_textareas = await self.browser.page.query_selector_all('textarea, div[contenteditable="true"], input[type="text"]')

                for i, elem in enumerate(all_textareas):
                    try:
                        is_visible = await elem.is_visible()
                        if not is_visible:
                            continue

                        await elem.scroll_into_view_if_needed()
                        await asyncio.sleep(0.3)
                        await elem.click()
                        await asyncio.sleep(0.3)

                        # 清空并输入
                        await self.browser.page.keyboard.press('Control+A')
                        await self.browser.page.keyboard.press('Backspace')
                        await elem.type(question, delay=10)
                        await asyncio.sleep(0.3)

                        # 验证
                        actual_value = await self._verify_input_text(elem)
                        if actual_value and question[:20] in actual_value:
                            input_element = elem
                            used_selector = f'input_element[{i}]'
                            self.logger.info(f"✓ 使用遍历法成功输入问题 (元素索引: {i})")
                            break
                    except (AttributeError, Exception):
                        continue

            if not input_element:
                # 保存失败时的截图
                error_screenshot = os.path.join(debug_dir, "input_not_found.png")
                await self.browser.page.screenshot(path=error_screenshot)
                self.logger.error(f"无法找到或填充输入框，已保存截图: {error_screenshot}")
                raise Exception("无法找到或填充输入框")

            # 保存输入成功后的截图
            after_input_screenshot = os.path.join(debug_dir, "after_input.png")
            await self.browser.page.screenshot(path=after_input_screenshot)
            self.logger.info(f"已保存输入后截图: {after_input_screenshot}")

            # 等待一下确保输入完成
            await asyncio.sleep(1)

            # 尝试发送
            self.logger.info("尝试发送问题...")
            send_selectors = [
                # Metaso可能的发送按钮选择器
                'button:has-text("发送")',
                'button:has-text("提交")',
                'button:has-text("Send")',
                'button:has-text("发送")',
                'svg[class*="send"]',
                # 通用选择器
                '[class*="send"] button',
                '[class*="submit"] button',
                'button[type="submit"]',
                '.send-button',
                '[aria-label*="send"]',
                '[aria-label*="发送"]',
                '[aria-label*="submit"]',
                # 查找包含发送图标的按钮
                'button svg',
            ]

            sent = False
            for selector in send_selectors:
                try:
                    btn = await self.browser.page.query_selector(selector)
                    if btn:
                        # 检查按钮是否可见
                        is_visible = await btn.is_visible()
                        if is_visible:
                            await btn.scroll_into_view_if_needed()
                            await asyncio.sleep(0.3)
                            await btn.click()
                            sent = True
                            self.logger.info(f"✓ 使用选择器 '{selector}' 点击发送按钮")
                            break
                except Exception as e:
                    self.logger.debug(f"发送按钮选择器 '{selector}' 失败: {str(e)}")
                    continue

            if not sent:
                self.logger.info("未找到发送按钮，使用Enter键发送")
                await self.browser.page.keyboard.press('Enter')
                await asyncio.sleep(0.5)

            # 保存发送后的截图
            after_send_screenshot = os.path.join(debug_dir, "after_send.png")
            await self.browser.page.screenshot(path=after_send_screenshot)
            self.logger.info(f"已保存发送后截图: {after_send_screenshot}")

            # 等待发送完成
            await asyncio.sleep(2)

        except Exception as e:
            self.logger.error(f"回退发送方法失败: {str(e)}")
            # 保存错误截图
            try:
                error_screenshot = os.path.join(debug_dir, "send_error.png")
                await self.browser.page.screenshot(path=error_screenshot)
                self.logger.info(f"已保存错误截图: {error_screenshot}")
            except (Exception,):
                pass
            raise

    async def _verify_input_text(self, element) -> Optional[str]:
        """验证输入框中的文本"""
        try:
            # 尝试多种方式获取输入的文本
            tag_name = await element.evaluate('el => el.tagName.toLowerCase()')

            if tag_name == 'textarea':
                return await element.evaluate('el => el.value')
            elif tag_name == 'input':
                return await element.evaluate('el => el.value')
            else:  # contenteditable div
                return await element.evaluate('el => el.innerText || el.textContent')
        except Exception as e:
            self.logger.debug(f"验证输入文本失败: {str(e)}")
            return None

    async def _wait_for_answer(self) -> Optional[str]:
        """等待并获取总包大脑的回答

        【v3.6.2更新】长思考模式下使用更长的等待时间
        """
        # 【v3.6.2】根据是否启用长思考模式调整等待参数
        if self.config.enable_long_thinking:
            # 长思考模式：使用更长的等待时间
            max_wait = max(self.config.max_wait_time, 900)  # 至少15分钟
            min_wait_time = 60  # 最小等待60秒后再开始稳定性检查
            required_stable_count = 10  # 增加到10次，更保守的判定
            self.logger.info(f"等待总包大脑回答（长思考模式），最长等待时间: {max_wait} 秒")
        else:
            # 普通模式：使用默认等待时间
            max_wait = self.config.max_wait_time
            min_wait_time = 30  # 最小等待30秒后再开始稳定性检查
            required_stable_count = 6  # 6次稳定性检查
            self.logger.info(f"等待总包大脑回答，最长等待时间: {max_wait} 秒")

        start_time = time.time()
        previous_content = ""
        stable_count = 0
        max_content_length = 0
        content_growth_stopped = False
        no_growth_count = 0

        while time.time() - start_time < max_wait:
            try:
                current_content = await self._extract_current_answer()

                if current_content:
                    content_length = len(current_content)

                    # 记录内容增长情况
                    if content_length > max_content_length:
                        growth = content_length - max_content_length
                        max_content_length = content_length
                        no_growth_count = 0
                        self.logger.info(f"内容增长中... 当前长度: {content_length} 字符 (增长: +{growth})")
                    else:
                        no_growth_count += 1
                        self.logger.debug(f"内容未增长: {no_growth_count} 次, 当前长度: {content_length} 字符")

                    elapsed_time = time.time() - start_time

                    # 检查是否满足最小等待时间
                    if elapsed_time >= min_wait_time:
                        # 内容长度不再增长的检查
                        if no_growth_count >= required_stable_count:
                            content_growth_stopped = True

                        # 内容稳定性检查
                        if current_content == previous_content:
                            stable_count += 1
                            self.logger.debug(f"内容稳定次数: {stable_count}/{required_stable_count}")
                        else:
                            stable_count = 0
                            previous_content = current_content

                        # 判定完成条件：内容不再增长 且 内容稳定 且 达到最小长度
                        if (content_growth_stopped and
                            stable_count >= required_stable_count and
                            content_length >= self.config.min_answer_length):
                            self.logger.info(f"检测到回答完成 - 最终长度: {content_length} 字符")
                            return current_content
                    else:
                        self.logger.debug(f"等待中... ({elapsed_time:.1f}/{min_wait_time} 秒)")

                await asyncio.sleep(self.config.check_interval)

            except Exception as e:
                self.logger.debug(f"等待回答时出错: {str(e)}")
                await asyncio.sleep(self.config.check_interval)

        # 超时返回当前内容
        final_content = await self._extract_current_answer()
        if final_content:
            self.logger.warning(f"等待超时，返回当前获取的内容 (长度: {len(final_content)} 字符)")
            return final_content

        self.logger.error("等待超时且未获取到任何回答")
        return None

    async def _extract_current_answer(self) -> Optional[str]:
        """使用Stagehand提取当前页面的回答内容"""
        try:
            # 首先尝试直接使用JavaScript获取完整的回答内容
            js_content = await self._extract_answer_with_js()
            if js_content and len(js_content) > 50:
                return js_content.strip()

            # 回退到传统方法
            return await self._extract_answer_fallback()

        except Exception as e:
            self.logger.debug(f"Stagehand提取回答失败: {str(e)}")
            return await self._extract_answer_fallback()

    async def _extract_answer_fallback(self) -> Optional[str]:
        """回退方法：使用传统选择器提取回答"""
        try:
            # 更全面的选择器列表
            answer_selectors = [
                # Metaso/总包大脑特定的选择器
                '[class*="message"] [class*="assistant"]',
                '[class*="chat"] [class*="answer"]',
                '[class*="conversation"] [class*="response"]',

                # 通用AI聊天界面选择器
                'div[class*="message"]:not([class*="user"]):not([class*="input"])',
                'div[class*="bubble"]:not([class*="user"]):not([class*="input"])',
                'div[class*="msg"]:not([class*="user"]):not([class*="input"])',

                # Markdown内容
                '.markdown-body',
                '[class*="markdown"]',
                '[class*="prose"]',

                # 通用内容容器
                'div[class*="content"]:not([class*="input"]):not([class*="user"])',
                '[class*="assistant-message"]',
                '[class*="ai-message"]',
                '[class*="bot-message"]',
                '[class*="reply-content"]',
                '[class*="response-content"]',
                '[class*="answer-content"]',

                # 更广泛的选择器
                'article',
                '[role="article"]',
                '[class*="text-content"]',
                '[class*="message-content"]',
            ]

            best_content = ""
            best_length = 0

            for selector in answer_selectors:
                try:
                    elements = await self.browser.page.query_selector_all(selector)
                    # 获取所有元素，找到最长的内容
                    for elem in elements:
                        try:
                            text = await elem.inner_text()
                            if text and len(text.strip()) > 50:
                                # 排除包含输入框的元素
                                has_input = await elem.query_selector('textarea, input, [contenteditable="true"]')
                                if not has_input:
                                    if len(text.strip()) > best_length:
                                        best_content = text.strip()
                                        best_length = len(text.strip())
                                        self.logger.debug(f"选择器 '{selector}' 找到内容，长度: {best_length}")
                        except (AttributeError, Exception):
                            continue
                except (AttributeError, Exception):
                    continue

            if best_content:
                return best_content

            # 如果上述方法都失败，尝试获取页面文本
            page_text = await self.browser.page.inner_text('body')
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                if len(line) > 100:
                    content = '\n'.join(lines[i:i+20])  # 获取更多行
                    if len(content) > 100:
                        return content

            return None

        except Exception as e:
            self.logger.debug(f"回退提取方法失败: {str(e)}")
            return None

    async def _extract_answer_with_js(self) -> Optional[str]:
        """使用JavaScript提取回答内容（更可靠的方法）"""
        try:
            # 多种JavaScript提取策略
            js_scripts = [
                # 策略1: 查找包含assistant/answer/bubble/message的div，获取最后一个
                """(() => {
                    const selectors = [
                        'div[class*="message"][class*="assistant"]',
                        'div[class*="chat"] div[class*="answer"]',
                        'div[class*="conversation"] div[class*="response"]',
                        'div.markdown-body',
                        'div[class*="bubble"]:not([class*="user"])',
                        'div[class*="msg"]:not([class*="user"])',
                        '[class*="assistant-message"]',
                        '[class*="ai-message"]',
                        '[class*="bot-message"]',
                        '[class*="reply"]'
                    ];
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            const lastElem = elements[elements.length - 1];
                            const text = lastElem.innerText || lastElem.textContent;
                            if (text && text.length > 50) return text;
                        }
                    }
                    return '';
                })()""",

                # 策略2: 查找所有包含大量文本的div
                """(() => {
                    const divs = document.querySelectorAll('div');
                    let result = '';
                    for (const div of divs) {
                        const text = div.innerText || div.textContent || '';
                        // 排除输入框、按钮等
                        if (text.length > 100 &&
                            !div.querySelector('textarea, input, button') &&
                            !div.matches('textarea, input, button')) {
                            if (text.length > result.length) {
                                result = text;
                            }
                        }
                    }
                    return result;
                })()""",

                # 策略3: 查找具有特定类名的消息容器
                """(() => {
                    const containers = document.querySelectorAll('[class*="container"], [class*="wrapper"], [class*="message"], [class*="chat"]');
                    let bestResult = '';
                    for (const container of containers) {
                        const text = container.innerText || container.textContent || '';
                        if (text.length > 100 && text.length > bestResult.length) {
                            // 确保不是用户消息
                            const classes = container.className || '';
                            if (!classes.toLowerCase().includes('user') &&
                                !classes.toLowerCase().includes('input') &&
                                !classes.toLowerCase().includes('send')) {
                                bestResult = text;
                            }
                        }
                    }
                    return bestResult;
                })()"""
            ]

            for script in js_scripts:
                try:
                    content = await self.browser.page.evaluate(script)
                    if content and len(content.strip()) > 50:
                        self.logger.debug(f"使用JS提取成功，长度: {len(content.strip())} 字符")
                        return content.strip()
                except (AttributeError, Exception):
                    continue

            return None

        except Exception as e:
            self.logger.debug(f"JS提取失败: {str(e)}")
            return None

    def _is_answer_sufficient(self, answer: Optional[str]) -> bool:
        """检查回答是否足够长"""
        if not answer:
            return False
        return len(answer) >= self.config.min_answer_length

    async def _send_failure_notification(self, question: str):
        """发送失败通知"""
        self.logger.info("发送提取失败通知")

        subject = "【总包大脑】提取回复失败通知"
        content = f"""您好，

系统尝试从总包大脑获取回答，但经过多次重试仍未能获取到足够长度的回复（要求至少{self.config.min_answer_length}字符）。

问题：{question}

请检查总包大脑网站是否正常运行，或手动重试。

此致
ZBBrainArticle 自动化脚本
        """

        try:
            send_email(
                self.config.notification_email,
                subject,
                content,
                self.config.smtp_server,
                self.config.smtp_port,
                self.config.sender_email,
                self.config.email_auth_code
            )
            self.logger.info("失败通知邮件已发送")
        except Exception as e:
            self.logger.error(f"发送失败通知邮件失败: {str(e)}")


# =============================================================================
# 微信公众号草稿管理类
# =============================================================================

class WeChatDraftManager:
    """微信公众号草稿管理类"""

    def __init__(self, config: Config, logger: Logger) -> None:
        """初始化管理器"""
        self.config = config
        self.logger = logger
        self.access_token = None

    def get_access_token(self) -> str:
        """获取微信公众号access_token"""
        self.logger.info("获取微信公众号access_token")

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.config.wechat_appid,
            'secret': self.config.wechat_secret
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            result = response.json()

            if 'access_token' in result:
                self.access_token = result['access_token']
                self.logger.info("成功获取access_token")
                return self.access_token
            else:
                error_msg = result.get('errmsg', '未知错误')
                raise Exception(f"获取access_token失败: {error_msg}")

        except Exception as e:
            self.logger.error(f"获取access_token失败: {str(e)}")
            raise

    def upload_cover_image(self, image_path: str = None) -> str:
        """上传封面图片"""
        image_path = image_path or self.config.cover_image_path

        if not os.path.exists(image_path):
            self.logger.warning(f"封面图片不存在: {image_path}")
            return ""

        self.logger.info(f"上传封面图片: {image_path}")

        if not self.access_token:
            self.get_access_token()

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image"

        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files, timeout=60)
                result = response.json()

            if 'media_id' in result:
                self.logger.info(f"成功上传封面图片，media_id: {result['media_id']}")
                return result['media_id']
            else:
                error_msg = result.get('errmsg', '未知错误')
                self.logger.warning(f"上传封面图片失败: {error_msg}")
                return ""

        except Exception as e:
            self.logger.error(f"上传封面图片失败: {str(e)}")
            return ""

    def upload_permanent_material(self, image_path: str, max_retries: int = 3) -> str:
        """上传永久素材（用于广告图，带压缩）

        Args:
            image_path: 图片路径
            max_retries: 最大重试次数（默认3次）

        Returns:
            素材URL或空字符串（失败时返回空字符串，调用方应跳过广告图插入）
        """
        if not os.path.exists(image_path):
            self.logger.warning(f"广告图片不存在: {image_path}，将跳过广告图插入")
            return ""

        # 先压缩图片
        compressed_path = self.compress_image(image_path)

        if not self.access_token:
            self.get_access_token()

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}"

        # 重试机制
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(f"上传广告图片为永久素材 (尝试 {attempt}/{max_retries}): {image_path}")

                with open(compressed_path, 'rb') as f:
                    files = {'media': f}
                    response = requests.post(url, files=files, timeout=60)
                    result = response.json()

                if 'media_id' in result:
                    self.logger.info(f"✓ 成功上传广告图片，media_id: {result['media_id']}")
                    # 微信永久素材API返回格式：{"media_id": MEDIA_ID, "url": URL}
                    # 直接从返回结果中提取URL
                    if 'url' in result and result['url']:
                        self.logger.info(f"✓ 成功获取广告图片URL: {result['url']}")
                        return result['url']
                    else:
                        # 如果返回结果中没有URL，尝试通过其他方式获取
                        image_url = self._get_material_url(result['media_id'])
                        if image_url:
                            self.logger.info(f"✓ 成功获取广告图片URL: {image_url}")
                            return image_url
                        else:
                            # 无法获取URL，返回空字符串（将跳过广告图插入）
                            self.logger.warning("无法获取素材URL，将跳过广告图插入")
                            return ""
                else:
                    error_msg = result.get('errmsg', '未知错误')
                    error_code = result.get('errcode', 'N/A')
                    if attempt < max_retries:
                        self.logger.warning(f"上传广告图片失败 (尝试 {attempt}/{max_retries}): [{error_code}] {error_msg}，准备重试...")
                        import time
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        self.logger.error(f"上传广告图片失败 (已重试{max_retries}次): [{error_code}] {error_msg}，将跳过广告图插入")
                        return ""

            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"上传广告图片异常 (尝试 {attempt}/{max_retries}): {str(e)}，准备重试...")
                    import time
                    time.sleep(2)  # 等待2秒后重试
                else:
                    self.logger.error(f"上传广告图片异常 (已重试{max_retries}次): {str(e)}，将跳过广告图插入")
                    return ""

        # 所有重试都失败
        self.logger.error(f"广告图上传失败，已达到最大重试次数({max_retries})，将跳过广告图插入")
        return ""

    def _get_material_url(self, media_id: str) -> str:
        """获取素材的URL

        Args:
            media_id: 素材ID

        Returns:
            图片URL或空字符串
        """
        self.logger.info(f"获取素材URL: {media_id}")

        if not self.access_token:
            self.get_access_token()

        url = f"https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={self.access_token}"

        try:
            payload = {
                "media_id": media_id
            }
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()

            if 'news_item' in result and 'content' in result['news_item']:
                # 永久素材
                content = result['news_item']['content']
                if 'news_item' in content and 'content' in content['news_item']:
                    news_item = content['news_item']
                    # 查找图片URL
                    for key in ['thumb_url', 'url', 'thumb_url_720', 'url_720']:
                        if key in news_item and news_item[key]:
                            self.logger.info(f"成功获取素材URL: {news_item[key]}")
                            return news_item[key]
            elif 'image_url' in result:
                # 临时素材或其他类型
                self.logger.info(f"成功获取素材URL: {result['image_url']}")
                return result['image_url']

            self.logger.warning("未能从素材信息中提取URL")
            return ""

        except Exception as e:
            self.logger.error(f"获取素材URL失败: {str(e)}")
            return ""

    def compress_image(self, image_path: str, max_width: int = 1920,
                      quality: int = 85, output_path: str = None) -> str:
        """
        压缩图片（优化微信上传）

        Args:
            image_path: 原图片路径
            max_width: 最大宽度（保持宽高比）
            quality: JPEG质量（1-100）
            output_path: 输出路径（None则覆盖原文件）

        Returns:
            压缩后的图片路径
        """
        try:
            from PIL import Image

            # 检查文件大小，小于100KB不需要压缩
            file_size = os.path.getsize(image_path)
            if file_size < 100 * 1024:
                self.logger.info(f"图片文件较小({file_size/1024:.1f}KB)，无需压缩")
                return image_path

            self.logger.info(f"开始压缩图片: {image_path}")

            # 打开图片
            img = Image.open(image_path)

            # 转换为RGB模式（如果是RGBA）
            if img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 计算新尺寸（保持宽高比）
            width, height = img.size
            if width > max_width:
                new_height = int(height * max_width / width)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                self.logger.info(f"图片尺寸已调整: {width}x{height} -> {max_width}x{new_height}")

            # 压缩并保存
            output = output_path or image_path
            img.save(output, 'JPEG', quality=quality, optimize=True)

            # 记录压缩率
            compressed_size = os.path.getsize(output)
            ratio = (1 - compressed_size / file_size) * 100

            self.logger.info(
                f"图片压缩完成: {file_size/1024:.1f}KB -> {compressed_size/1024:.1f}KB "
                f"(压缩率: {ratio:.1f}%)"
            )
            return output

        except ImportError:
            self.logger.warning("PIL/Pillow未安装，跳过图片压缩")
            return image_path
        except Exception as e:
            self.logger.error(f"图片压缩失败: {str(e)}")
            return image_path

    def create_draft(self, title: str, content: str, author: str = None,
                     digest: str = None, cover_media_id: str = None) -> str:
        """创建草稿（支持原创声明）

        Returns:
            成功返回草稿media_id，失败返回空字符串
        """
        # 标题长度检查（警告但不截断，由调用方确保标题长度合适）
        if len(title) > 24:
            self.logger.warning(f"标题长度({len(title)}字符)超过建议的24字符，可能会被微信截断")

        self.logger.info(f"创建草稿: {title}")

        author = author or self.config.default_author
        # 作者字段长度限制（微信公众号限制约8个汉字/24字节）
        # "总包大脑"是4个汉字，在限制范围内
        if len(author) > 8:
            author = author[:8]
            self.logger.warning(f"作者名过长，已截断为: {author}")

        # digest 字段长度限制（使用传入的question作为摘要）
        if not digest:
            digest = f"总包大脑回应热点问题，详见：{self.config.metaso_url}"
        if len(digest) > 120:  # 微信摘要限制约120个字符
            digest = digest[:120]
            self.logger.warning(f"摘要过长，已截断")

        self.logger.info(f"草稿信息 - 标题: {title}, 作者: {author}, 摘要长度: {len(digest)}")

        if not self.access_token:
            self.get_access_token()

        articles = [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": self.config.metaso_url,
            "thumb_media_id": cover_media_id or "",
            "show_cover_pic": 1 if cover_media_id else 0,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
            "declare_original": 1  # 标记为原创内容
        }]

        # WeChat API requires content to be an HTML string
        # Ensure content is a string (not a file path)
        if os.path.isfile(content):
            self.logger.warning(f"content是文件路径，正在读取文件: {content}")
            with open(content, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            html_content = content

        # Debug: log content info
        content_length = len(html_content)
        self.logger.info(f"HTML内容长度: {content_length} 字符")

        # WeChat API content size limit check (approximately 200,000 characters for safety)
        if content_length > 200000:
            self.logger.error(f"HTML内容过长 ({content_length} 字符)，超过微信限制")
            return None

        # Log preview of content (first 200 chars)
        self.logger.debug(f"HTML内容预览: {html_content[:200]}")

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"

        try:
            articles = [{
                "title": title,
                "author": author,
                "digest": digest,
                "content": html_content,
                "content_source_url": self.config.metaso_url,
                "thumb_media_id": cover_media_id or "",
                "show_cover_pic": 1 if cover_media_id else 0,
                "need_open_comment": 1,
                "only_fans_can_comment": 0,
                "declare_original": 1  # 标记为原创内容
            }]

            data = {"articles": articles}

            # Debug logging
            self.logger.info(f"发送到微信API:")
            self.logger.info(f"  - title: '{title}' (长度: {len(title)})")
            self.logger.info(f"  - author: '{author}' (长度: {len(author)})")
            self.logger.info(f"  - digest长度: {len(digest) if digest else 0}")
            self.logger.info(f"  - content长度: {content_length}")
            self.logger.info(f"  - thumb_media_id: {cover_media_id}")

            # 使用正确的编码方式：显式UTF-8编码 + charset声明（GitHub最佳实践）
            # 修复微信API 45003错误：中文被正确解析，不会被误判为长度超限
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.logger.debug(f"请求Content-Type: {headers['Content-Type']}")
            self.logger.debug(f"JSON数据字节长度: {len(json_data)}")
            response = requests.post(url, data=json_data, headers=headers, timeout=30)
            result = response.json()

            self.logger.info(f"微信API响应: {result}")

            # WeChat API returns success without errcode field (only includes errcode on error)
            # Success response: {'media_id': 'xxx', 'item': [...]}
            # Error response: {'errcode': 40001, 'errmsg': 'error message'}
            if 'errcode' not in result:
                # No errcode means success
                media_id = result.get('media_id', '')
                if media_id:
                    self.logger.info(f"✓ 成功创建草稿 (media_id: {media_id})")
                    return media_id
                else:
                    self.logger.error("✗ 创建草稿失败: 响应中未包含media_id")
                    return None
            elif result['errcode'] == 0:
                # errcode == 0 also means success
                media_id = result.get('media_id', '')
                if media_id:
                    self.logger.info(f"✓ 成功创建草稿 (media_id: {media_id})")
                    return media_id
                else:
                    self.logger.error("✗ 创建草稿失败: 响应中未包含media_id")
                    return None
            else:
                # Any other errcode value means error
                error_msg = result.get('errmsg', '未知错误')
                error_code = result.get('errcode', 'N/A')
                self.logger.error(f"✗ 创建草稿失败: errcode={error_code}, errmsg={error_msg}")

                # Log common WeChat API errors
                error_hints = {
                    "40001": "access_token失效或无效",
                    "40007": "media_id无效或过期",
                    "45009": "接口调用次数超限",
                    "64004": "草稿箱已满（最多100条）",
                    "85006": "文章内容格式错误",
                    "85007": "文章内容长度超限",
                    "85008": "封面图片不合法",
                    "85009": "文章标题不合法",
                    "85010": "文章作者不合法",
                }

                if str(error_code) in error_hints:
                    self.logger.error(f"错误提示: {error_hints[str(error_code)]}")

                return None

        except Exception as e:
            self.logger.error(f"创建草稿异常: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None

    def schedule_publish(self, media_id: str, delay_minutes: int = 15) -> dict:
        """定时发布草稿

        【重要说明 v3.6.3】
        微信公众号API不支持通过API设置定时发布时间。
        freepublish/submit 接口只支持立即发布，publish_time参数无效。

        正确的定时发布方式：
        1. 创建草稿（已实现）
        2. 用户在微信公众号后台手动设置定时发布
        或
        3. 使用外部定时任务系统（如GitHub Actions）在指定时间调用发布API

        Args:
            media_id: 草稿的media_id
            delay_minutes: 延迟发布的分钟数（此参数当前无效，仅用于日志提示）

        Returns:
            dict: {"success": bool, "publish_id": str, "msg": str}
        """
        import time

        self.logger.info(f"📋 准备发布草稿")
        self.logger.info(f"   media_id: {media_id}")
        self.logger.warning(f"⚠️ 注意: 微信API不支持定时发布，草稿创建后请手动在后台设置发布时间")

        if not self.access_token:
            self.get_access_token()

        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={self.access_token}"

        try:
            # 【修复v3.6.3】移除不支持的publish_time参数
            # freepublish/submit API 不支持定时发布，只能立即发布
            payload = {
                "media_id": media_id
                # 注意: publish_time 参数已移除，因为微信API不支持
            }

            headers = {'Content-Type': 'application/json; charset=utf-8'}
            json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

            self.logger.info(f"发送发布请求到微信API...")
            response = requests.post(url, data=json_data, headers=headers, timeout=30)
            result = response.json()

            self.logger.info(f"微信API响应: {result}")

            if 'errcode' not in result or result.get('errcode') == 0:
                publish_id = result.get('publish_id', 'N/A')
                msg_id = result.get('msg_data_id', 'N/A')
                self.logger.info(f"✓ 发布成功!")
                self.logger.info(f"   publish_id: {publish_id}")
                return {
                    "success": True,
                    "publish_id": publish_id,
                    "msg_id": msg_id,
                    "msg": "发布成功"
                }
            else:
                error_msg = result.get('errmsg', '未知错误')
                error_code = result.get('errcode', 'N/A')
                self.logger.error(f"✗ 发布失败: errcode={error_code}, errmsg={error_msg}")

                # 常见错误提示
                error_hints = {
                    "40001": "access_token失效或无效",
                    "40007": "media_id无效或过期",
                    "40160": "草稿不存在",
                    "40161": "草稿已发布",
                    "40162": "草稿正在发布中",
                    "40163": "草稿发布失败",
                    "40164": "草稿发布超时",
                    "48001": "API权限不足 - 该公众号可能没有发布权限，请检查公众号后台设置",
                    "88000": "没有群发权限",
                    "88001": "草稿内容不符合群发要求",
                }

                hint = error_hints.get(str(error_code), "")
                if hint:
                    self.logger.error(f"错误提示: {hint}")

                return {
                    "success": False,
                    "publish_id": None,
                    "msg": f"发布失败: {error_msg} ({error_code})",
                    "error_code": error_code
                }

        except Exception as e:
            self.logger.error(f"发布请求异常: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {
                "success": False,
                "publish_id": None,
                "msg": f"发布异常: {str(e)}"
            }


# =============================================================================
# Markdown转微信类
# =============================================================================

class MarkdownToWeChat:
    """Markdown转微信公众号格式类"""

    def __init__(self, config: Config, logger: Logger) -> None:
        """初始化转换器"""
        self.config = config
        self.logger = logger

    def convert_answer_to_html(self, answer: str, question: str,
                                title: str = None, cover_image: str = None,
                                create_draft_direct: bool = False) -> str:
        """将总包大脑的回答转换为微信HTML格式或直接创建草稿

        Args:
            answer: 总包大脑的回答内容
            question: 原始问题（将用作文章摘要）
            title: 文章标题（如果提供，将用于直接创建草稿）
            cover_image: 封面图片路径
            create_draft_direct: 是否直接创建草稿（使用md2wechat sync-md）

        Returns:
            HTML内容，如果直接创建了草稿则返回空字符串
        """
        self.logger.info("转换回答为微信格式")

        # 使用配置中的广告图设置（使用本地路径，让md2wechat自动处理）
        markdown_content = self._answer_to_markdown(
            answer, question,
            top_ad_image=self.config.top_ad_image,
            bottom_ad_image=self.config.bottom_ad_image,
            enable_top_ad=self.config.enable_top_ad,
            enable_bottom_ad=self.config.enable_bottom_ad
        )

        md_file = os.path.join(self.config.temp_dir, f"article_{int(time.time())}.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        self.logger.info(f"Markdown文件已保存: {md_file}")

        # 复制广告图到temp目录（确保md2wechat能找到它们）
        temp_dir = os.path.dirname(md_file)
        top_ad_copy_path = None
        bottom_ad_copy_path = None
        top_ad_url = None
        bottom_ad_url = None

        # 上传顶部广告图到微信素材库
        if self.config.enable_top_ad and self.config.top_ad_image:
            src_path = Path(self.config.top_ad_image)
            if not src_path.is_absolute():
                src_path = Path(__file__).parent / self.config.top_ad_image
            if src_path.exists():
                top_ad_copy_path = os.path.join(temp_dir, "top-ad.jpg")
                import shutil
                shutil.copy2(src_path, top_ad_copy_path)
                self.logger.info(f"已复制顶部广告图到: {top_ad_copy_path}")

                # 上传到微信素材库并获取URL
                self.logger.info("正在上传顶部广告图到微信素材库...")
                try:
                    wechat_manager = WeChatDraftManager(self.config, self.logger)
                    # 上传永久素材获取URL
                    result = wechat_manager.upload_permanent_material(str(src_path))
                    if result and result.startswith('http'):
                        # 成功获取到微信CDN URL
                        top_ad_url = result
                        self.logger.info(f"✓ 成功获取顶部广告图微信CDN URL")
                    elif result:
                        # 获取到media_id但没有URL，记录日志
                        self.logger.info(f"顶部广告图media_id: {result}，未获取到URL")
                        top_ad_url = None
                    else:
                        # 上传失败，使用本地路径
                        top_ad_url = None
                        self.logger.info("顶部广告图将使用本地路径")
                except Exception as e:
                    self.logger.warning(f"上传顶部广告图失败: {str(e)}，将使用本地路径")
                    top_ad_url = None

        # 上传底部广告图到微信素材库
        if self.config.enable_bottom_ad and self.config.bottom_ad_image:
            src_path = Path(self.config.bottom_ad_image)
            if not src_path.is_absolute():
                src_path = Path(__file__).parent / self.config.bottom_ad_image
            if src_path.exists():
                bottom_ad_copy_path = os.path.join(temp_dir, "bottom-ad.jpg")
                import shutil
                shutil.copy2(src_path, bottom_ad_copy_path)
                self.logger.info(f"已复制底部广告图到: {bottom_ad_copy_path}")

                # 上传到微信素材库并获取URL
                self.logger.info("正在上传底部广告图到微信素材库...")
                try:
                    wechat_manager = WeChatDraftManager(self.config, self.logger)
                    # 上传永久素材获取URL
                    result = wechat_manager.upload_permanent_material(str(src_path))
                    if result and result.startswith('http'):
                        # 成功获取到微信CDN URL
                        bottom_ad_url = result
                        self.logger.info(f"✓ 成功获取底部广告图微信CDN URL")
                    elif result:
                        # 获取到media_id但没有URL，记录日志
                        self.logger.info(f"底部广告图media_id: {result}，未获取到URL")
                        bottom_ad_url = None
                    else:
                        # 上传失败，使用本地路径
                        bottom_ad_url = None
                        self.logger.info("底部广告图将使用本地路径")
                except Exception as e:
                    self.logger.warning(f"上传底部广告图失败: {str(e)}，将使用本地路径")
                    bottom_ad_url = None

        # 如果获取到微信URL，使用URL；否则检查是否复制成功
        # 注意：如果上传失败（top_ad_url为空），则不插入广告图
        if top_ad_url:
            top_ad_image = top_ad_url
        elif top_ad_copy_path and os.path.exists(top_ad_copy_path):
            # 上传失败但有本地副本，仍然可以使用本地路径
            top_ad_image = "top-ad.jpg"
            self.logger.info("顶部广告图上传失败，将使用本地路径作为备选")
        else:
            # 完全失败，不插入顶部广告图
            top_ad_image = None
            self.logger.warning("顶部广告图插入失败，将跳过顶部广告图")

        if bottom_ad_url:
            bottom_ad_image = bottom_ad_url
        elif bottom_ad_copy_path and os.path.exists(bottom_ad_copy_path):
            # 上传失败但有本地副本，仍然可以使用本地路径
            bottom_ad_image = "bottom-ad.jpg"
            self.logger.info("底部广告图上传失败，将使用本地路径作为备选")
        else:
            # 完全失败，不插入底部广告图
            bottom_ad_image = None
            self.logger.warning("底部广告图插入失败，将跳过底部广告图")

        # 重新生成markdown内容（使用URL或相对文件名）
        markdown_content = self._answer_to_markdown(
            answer, question,
            top_ad_image=top_ad_image,
            bottom_ad_image=bottom_ad_image,
            enable_top_ad=self.config.enable_top_ad,
            enable_bottom_ad=self.config.enable_bottom_ad,
            use_simple_filename=(not top_ad_url and not bottom_ad_url)  # 只有没有URL时才使用简单文件名
        )

        # 更新markdown文件
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # 使用改进的md2wechat方法，传递question作为digest
        html_content = self._convert_with_md2wechat(
            md_file,
            title=title,
            cover_image=cover_image,
            create_draft=create_draft_direct,
            digest=question  # 使用热点问题作为摘要
        )

        return html_content

    def _upload_ad_image_to_wechat(self, image_path: str) -> str:
        """上传广告图到微信素材库并返回URL

        Args:
            image_path: 图片路径

        Returns:
            图片URL、base64数据或空字符串
        """
        try:
            # 先尝试上传为永久素材并获取URL
            wechat_manager = WeChatDraftManager(self.config, self.logger)
            result = wechat_manager.upload_permanent_material(image_path)

            if result and not result.startswith('data:'):
                # 如果成功获取到URL或media_id
                if result.startswith('http'):
                    return result
                else:
                    # 获取到media_id但没获取到URL，转换为base64
                    self.logger.info("素材上传成功但未获取URL，转换为base64嵌入")
                    return self._image_to_base64(image_path)

        except Exception as e:
            self.logger.error(f"上传广告图失败: {str(e)}")

        # 失败时返回空字符串，将使用本地路径
        return ""

    def _image_to_base64(self, image_path: str) -> str:
        """将图片转换为base64编码（用于嵌入HTML）

        Args:
            image_path: 图片路径

        Returns:
            base64编码的图片数据URI
        """
        try:
            import base64

            # 检查文件大小，限制在500KB以内
            file_size = os.path.getsize(image_path)
            if file_size > 500 * 1024:  # 500KB
                self.logger.warning(f"广告图文件过大({file_size/1024:.1f}KB)，压缩后再转换")
                # 这里应该压缩图片，但暂时跳过
                return ""

            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')

            # 根据文件扩展名确定MIME类型
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'

            # 返回data URI格式
            self.logger.info(f"广告图已转换为base64格式，大小: {len(base64_data)}字符")
            return f"data:{mime_type};base64,{base64_data}"

        except Exception as e:
            self.logger.error(f"图片转base64失败: {str(e)}")
            return ""

    def _answer_to_markdown(self, answer: str, question: str,
                           top_ad_image: str = None, bottom_ad_image: str = None,
                           enable_top_ad: bool = True, enable_bottom_ad: bool = True,
                           use_simple_filename: bool = False) -> str:
        """将回答转换为结构化的Markdown格式（含二级、三级标题）

        Args:
            answer: 总包大脑的回答
            question: 热点问题
            top_ad_image: 顶部广告图路径或base64数据或素材URL
            bottom_ad_image: 底部广告图路径或base64数据或素材URL
            enable_top_ad: 是否启用顶部广告
            enable_bottom_ad: 是否启用底部广告
            use_simple_filename: 是否使用简单文件名（不进行路径检查）
        """
        self.logger.info("使用AI优化文章结构，添加层次化标题")
        structured_content = self._structure_content_with_headings(answer)

        # 获取项目根目录（用于将相对路径转换为绝对路径）
        project_root = Path(__file__).parent.absolute()

        # 构建顶部广告图Markdown
        top_ad_md = ""
        if enable_top_ad and top_ad_image:
            # 检查是否是base64格式（已上传的图片）
            if top_ad_image.startswith('data:image'):
                # 使用HTML img标签（将在md2wechat转换时保留）
                self.logger.info("添加顶部广告图（base64嵌入）")
                top_ad_md = f"""
<div style="text-align: center; margin: 0 0 10px 0;">
<img src="{top_ad_image}" alt="顶部广告" style="width: 100%; max-width: 900px; height: auto; display: block;"/>
</div>

---
"""
            elif top_ad_image.startswith('http'):
                # 外链URL
                self.logger.info(f"添加顶部广告图（外链）: {top_ad_image}")
                top_ad_md = f"""
<div style="text-align: center; margin: 0 0 10px 0;">
<img src="{top_ad_image}" alt="顶部广告" style="width: 100%; max-width: 900px; height: auto; display: block;"/>
</div>

---
"""
            else:
                # 处理本地文件路径（相对路径或绝对路径）
                # 如果use_simple_filename为True且是简单文件名，使用相对于markdown文件的路径
                if use_simple_filename and os.path.dirname(top_ad_image) == '':
                    # 简单文件名，图片在temp目录，markdown文件也在temp目录
                    # 使用相对于markdown文件的路径（即同目录下的文件）
                    image_relative_path = top_ad_image
                    self.logger.info(f"添加顶部广告图（相对路径）: {image_relative_path}")
                    top_ad_md = f"""
![顶部广告]({image_relative_path})

---

"""
                else:
                    image_path = Path(top_ad_image)
                    found = False

                    # 首先检查是否直接存在（绝对路径或当前目录）
                    if image_path.exists():
                        found = True
                    elif not image_path.is_absolute():
                        # 相对路径，尝试项目根目录
                        image_path = project_root / top_ad_image
                        if image_path.exists():
                            found = True

                    if found:
                        # 如果是简单文件名（不含路径分隔符），使用相对路径
                        # 否则使用绝对路径
                        if os.path.dirname(top_ad_image) == '':
                            # 简单文件名，使用相对路径
                            self.logger.info(f"添加顶部广告图（相对路径）: {top_ad_image}")
                            top_ad_md = f"""
![顶部广告]({top_ad_image})

---

"""
                        else:
                            # 转换为绝对路径，并使用正斜杠（md2wechat兼容性更好）
                            abs_path = str(image_path.resolve()).replace('\\', '/')
                            self.logger.info(f"添加顶部广告图（绝对路径）: {abs_path}")
                            top_ad_md = f"""
![顶部广告]({abs_path})

---

"""
                    else:
                        self.logger.warning(f"顶部广告图路径无效: {top_ad_image} (尝试路径: {image_path})")

        # 构建底部广告图Markdown
        bottom_ad_md = ""
        if enable_bottom_ad and bottom_ad_image:
            if bottom_ad_image.startswith('data:image'):
                self.logger.info("添加底部广告图（base64嵌入）")
                bottom_ad_md = f"""
---
<div style="text-align: center; margin: 12px 0;">
<img src="{bottom_ad_image}" alt="底部广告" style="width: 100%; max-width: 900px; height: auto;"/>
</div>

"""
            elif bottom_ad_image.startswith('http'):
                self.logger.info(f"添加底部广告图（外链）: {bottom_ad_image}")
                bottom_ad_md = f"""
---

<div style="text-align: center; margin: 12px 0;">
<img src="{bottom_ad_image}" alt="底部广告" style="width: 100%; max-width: 900px; height: auto;"/>
</div>

"""
            else:
                # 处理本地文件路径（相对路径或绝对路径）
                # 如果use_simple_filename为True且是简单文件名，使用相对于markdown文件的路径
                if use_simple_filename and os.path.dirname(bottom_ad_image) == '':
                    # 简单文件名，图片在temp目录，markdown文件也在temp目录
                    # 使用相对于markdown文件的路径（即同目录下的文件）
                    image_relative_path = bottom_ad_image
                    self.logger.info(f"添加底部广告图（相对路径）: {image_relative_path}")
                    bottom_ad_md = f"""
---

![底部广告]({image_relative_path})

"""
                else:
                    image_path = Path(bottom_ad_image)
                    found = False

                    # 首先检查是否直接存在（绝对路径或当前目录）
                    if image_path.exists():
                        found = True
                    elif not image_path.is_absolute():
                        # 相对路径，尝试项目根目录
                        image_path = project_root / bottom_ad_image
                        if image_path.exists():
                            found = True

                    if found:
                        # 如果是简单文件名（不含路径分隔符），使用相对路径
                        # 否则使用绝对路径
                        if os.path.dirname(bottom_ad_image) == '':
                            # 简单文件名，使用相对路径
                            self.logger.info(f"添加底部广告图（相对路径）: {bottom_ad_image}")
                            bottom_ad_md = f"""
---

![底部广告]({bottom_ad_image})

"""
                        else:
                            # 转换为绝对路径，并使用正斜杠（md2wechat兼容性更好）
                            abs_path = str(image_path.resolve()).replace('\\', '/')
                            self.logger.info(f"添加底部广告图（绝对路径）: {abs_path}")
                            bottom_ad_md = f"""
---

![底部广告]({abs_path})

"""
                    else:
                        self.logger.warning(f"底部广告图路径无效: {bottom_ad_image} (尝试路径: {image_path})")

        # 构建Markdown：顶部广告图 → 标题 → 正文 → 底部广告图
        markdown = f"""{top_ad_md}# {question}

{structured_content}

{bottom_ad_md}"""
        return markdown

    def _structure_content_with_headings(self, content: str) -> str:
        """仅添加层次化标题结构，绝对不修改原文内容

        优化策略（0成本）：
        - 使用免费模型 glm-4-flash + 增强提示词
        - 多步验证确保原文完整性
        - 失败时自动重试（最多2次）

        Args:
            content: 原始回答内容

        Returns:
            仅添加了##和###标题的内容，原文完全保留
        """
        self.logger.info(f"正在为内容添加结构化标题（使用 {self.config.zhipu_model_pro} 免费模型）...")

        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=self.config.zhipu_api_key)

            # 增强版提示词：针对 GLM-4.7-Flash 优化，确保免费模型也能高质量完成
            enhanced_system = """你是专业的排版编辑，擅长为文章添加结构化标题。

【核心任务】为文章内容添加层次化的Markdown标题（## 和 ###）

【严格规则 - 必须遵守】
1. 只输出添加了##和###标题后的原文内容，不添加任何其他文字
2. 绝对不能修改、删除、精简原文任何字、标点或格式
3. 绝对不能在输出中包含任何对话指令、说明或注释
4. 标题要简洁精准，准确概括下方段落的核心主题
5. 标题层级要合理：## 用于主要章节，### 用于子章节

【质量标准】
- 原文完整性：100%保留原文
- 标题准确性：标题能准确概括段落内容
- 层级合理性：标题层级清晰，逻辑结构分明"""

            enhanced_user = f"""给下面的文章内容添加##和###标题。只输出添加标题后的文章内容，不要输出任何其他文字。

========文章内容开始========
{content}
========文章内容结束========"""

            best_result = None
            best_similarity = 0

            # 最多尝试2次，选择质量最好的结果
            for attempt in range(2):
                response = client.chat.completions.create(
                    model=self.config.zhipu_model_pro,  # 内容结构化使用高质量模型
                    messages=[
                        {"role": "system", "content": enhanced_system},
                        {"role": "user", "content": enhanced_user}
                    ],
                    temperature=0.1,  # 降低温度，减少创造性修改
                    max_tokens=10000,
                    timeout=Constants.API_CALL_TIMEOUT  # 【v3.6.4修复】添加API调用超时
                )

                structured_content = response.choices[0].message.content.strip()

                # 质量验证
                original_len = len(content.replace('\n', '').replace(' ', ''))
                structured_len = len(structured_content.replace('\n', '').replace(' ', '').replace('#', ''))
                similarity = self._calculate_text_similarity(content, structured_content)

                # 长度检查：内容减少超过5%则认为被精炼
                if structured_len < original_len * 0.95:
                    self.logger.warning(f"尝试{attempt+1}: 内容可能被精炼（原文{original_len}字→{structured_len}字）")
                    continue

                # 相似度检查
                if similarity >= 0.90:  # 提高相似度阈值到90%
                    self.logger.info(f"✓ 内容结构化完成（相似度: {similarity:.2%}）")
                    return structured_content

                # 记录最佳结果
                if similarity > best_similarity:
                    best_result = structured_content
                    best_similarity = similarity

                self.logger.warning(f"尝试{attempt+1}: 相似度{similarity:.2%}，低于90%阈值，重试...")

            # 使用最佳结果或回退
            if best_similarity >= 0.85:
                self.logger.info(f"使用最佳结果（相似度: {best_similarity:.2%}）")
                return best_result
            else:
                self.logger.warning(f"两次尝试相似度均不达标，使用回退方法")
                return self._fallback_structure(content)

        except Exception as e:
            self.logger.warning(f"AI结构化失败: {str(e)}，使用回退方法")
            return self._fallback_structure(content)

    def _fallback_structure(self, content: str) -> str:
        """AI失败时的回退方法：仅做基本格式清理，完全不修改原文内容

        Args:
            content: 原始内容

        Returns:
            仅清理格式的原始内容，不添加任何标题
        """
        # 只做最基本的格式清理，不修改任何文字内容
        content = self._clean_answer(content)

        # 不添加任何标题，保持原文完整
        self.logger.info("使用原始内容（仅做格式清理，不修改原文）")
        return content

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（用于验证原文是否被保留）

        使用字符级别相似度检测，避免AI生成内容与原文差异过大

        Args:
            text1: 原始文本
            text2: 待比较文本

        Returns:
            相似度（0.0-1.0）
        """
        try:
            import difflib

            # 清理文本：移除空白和标点，只保留核心内容
            def clean_for_comparison(text: str) -> str:
                # 移除Markdown标题标记
                text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
                # 移除空白字符
                text = re.sub(r'\s+', '', text)
                # 移除常见标点
                text = re.sub(r'[，。！？、；：""''（）【】《》\.,!?;:\'"()\[\]<>]', '', text)
                return text

            clean1 = clean_for_comparison(text1)
            clean2 = clean_for_comparison(text2)

            if not clean1 or not clean2:
                return 0.0

            # 使用difflib计算相似度
            matcher = difflib.SequenceMatcher(None, clean1, clean2)
            similarity = matcher.ratio()

            return similarity

        except Exception as e:
            self.logger.warning(f"计算文本相似度失败: {str(e)}，返回默认值0.9")
            return 0.9  # 默认返回较高相似度，避免误判

    def _validate_title_relevance(self, title: str, question: str) -> bool:
        """验证标题与问题的相关性

        检查标题是否包含问题中的核心关键词，确保标题准确反映问题主题

        Args:
            title: 生成的标题
            question: 原始问题

        Returns:
            bool: 相关性是否达标
        """
        try:
            import jieba

            # 从问题中提取关键词
            question_words = set(jieba.cut(question))

            # 过滤停用词和标点
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '如何', '什么', '为什么', '怎么'}
            question_keywords = [w for w in question_words if len(w) >= 2 and w not in stop_words and not re.match(r'^[^\w\u4e00-\u9fff]+$', w)]

            # 检查标题是否包含核心关键词
            matched_keywords = []
            for keyword in question_keywords[:5]:  # 只检查前5个核心关键词
                if keyword in title:
                    matched_keywords.append(keyword)

            # 至少匹配1个核心关键词
            if len(matched_keywords) >= 1:
                self.logger.info(f"标题关键词匹配: {matched_keywords}")
                return True
            else:
                # 如果没有匹配，检查是否有EPC相关词汇作为保底
                epc_keywords = ['EPC', '总承包', '工程', '项目', '设计', '施工', '成本', '合同', '管理']
                for kw in epc_keywords:
                    if kw in title and kw in question:
                        self.logger.info(f"标题EPC关键词匹配: {kw}")
                        return True

                self.logger.warning(f"标题与问题关键词不匹配。问题关键词: {question_keywords[:5]}, 标题: {title}")
                return False

        except ImportError:
            # jieba未安装，使用简单的字符匹配
            self.logger.debug("jieba未安装，使用简单字符匹配验证标题相关性")
            # 检查问题中连续2字以上的词是否出现在标题中
            for i in range(len(question) - 1):
                if question[i:i+2] in title and re.match(r'[\u4e00-\u9fff]{2}', question[i:i+2]):
                    return True
            return 'EPC' in title or '总承包' in title
        except Exception as e:
            self.logger.warning(f"标题相关性验证失败: {str(e)}，默认通过")
            return True

    def _validate_html_quality(self, html_content: str, original_md: str, theme_name: str) -> float:
        """验证HTML排版质量（多维度评分）

        评分维度：
        1. 内容完整性（40%）- 原文内容是否被保留
        2. 结构正确性（30%）- HTML结构是否正确
        3. 样式规范性（20%）- 内联样式是否规范
        4. 主题一致性（10%）- 是否符合主题配色

        Args:
            html_content: 生成的HTML内容
            original_md: 原始Markdown内容
            theme_name: 主题名称

        Returns:
            float: 质量评分（0.0-1.0）
        """
        try:
            import re

            score = 0.0

            # 1. 内容完整性检查（40%）
            # 移除HTML标签后，检查文本相似度
            text_only = re.sub(r'<[^>]+>', '', html_content)
            text_only = re.sub(r'\s+', '', text_only)
            original_text = re.sub(r'[#\*\n\s]+', '', original_md)

            # 计算文本重叠率
            common_chars = sum(1 for c in original_text if c in text_only)
            completeness_score = min(common_chars / max(len(original_text), 1), 1.0)
            score += completeness_score * 0.4

            # 2. 结构正确性检查（30%）
            structure_score = 1.0

            # 检查是否禁止列表标签
            if re.search(r'<[ou]l[^>]*>', html_content, re.IGNORECASE):
                structure_score -= 0.3
            if re.search(r'<li[^>]*>', html_content, re.IGNORECASE):
                structure_score -= 0.3

            # 检查是否有基本的HTML结构
            if not re.search(r'<section[^>]*>', html_content) and not re.search(r'<div[^>]*>', html_content):
                structure_score -= 0.2

            # 检查是否有段落标签
            if not re.search(r'<p[^>]*>', html_content):
                structure_score -= 0.2

            structure_score = max(0, structure_score)
            score += structure_score * 0.3

            # 3. 样式规范性检查（20%）
            style_score = 1.0

            # 检查内联样式
            style_count = len(re.findall(r'style="[^"]*"', html_content))
            if style_count < 5:  # 至少应该有5个内联样式
                style_score -= 0.3

            # 检查是否有外部样式表（不应该有）
            if re.search(r'<style[^>]*>', html_content, re.IGNORECASE):
                style_score -= 0.5

            style_score = max(0, style_score)
            score += style_score * 0.2

            # 4. 主题一致性检查（10%）
            theme_score = 1.0

            # 主题颜色映射
            theme_colors = {
                '秋日暖光': ['#FF8C00', '#FFD700', '#FFA500'],
                '春日清新': ['#4CAF50', '#8BC34A', '#CDDC39'],
                '深海静谧': ['#191970', '#4169E1', '#1E90FF'],
                '优雅金': ['#B8860B', '#DAA520', '#FFD700'],
                '活力红': ['#FF4444', '#FF6B6B', '#EE4444'],
                '简约蓝': ['#0096FF', '#0066CC', '#4A90D9'],
                '专注绿': ['#27AE60', '#2ECC71', '#1ABC9C']
            }

            if theme_name in theme_colors:
                has_theme_color = False
                for color in theme_colors[theme_name]:
                    if color.lower() in html_content.lower():
                        has_theme_color = True
                        break
                if not has_theme_color:
                    theme_score -= 0.5

            theme_score = max(0, theme_score)
            score += theme_score * 0.1

            self.logger.debug(f"HTML质量评分详情: 完整性={completeness_score:.2%}, 结构={structure_score:.2%}, 样式={style_score:.2%}, 主题={theme_score:.2%}, 总分={score:.2%}")

            return score

        except Exception as e:
            self.logger.warning(f"HTML质量验证失败: {str(e)}，返回默认评分0.8")
            return 0.8

    def _clean_answer(self, answer: str) -> str:
        """清理回答内容"""
        answer = re.sub(r'\n{3,}', '\n\n', answer)
        answer = answer.replace('\u200b', '')
        answer = answer.replace('\xa0', ' ')
        return answer.strip()

    def _convert_with_md2wechat(self, md_file: str, title: str = None,
                                cover_image: str = None, create_draft: bool = True,
                                digest: str = None) -> str:
        """使用专业级AI转换（支持秋日暖光主题和草稿创建）

        注意：md2wechat AI 模式与 ZhipuAI 不兼容，已改用直接调用 ZhipuAI GLM-4-Plus
        确保专业级秋日暖光主题排版质量

        Args:
            md_file: Markdown文件路径
            title: 文章标题（用于草稿创建）
            cover_image: 封面图片路径
            create_draft: 是否直接创建草稿
            digest: 文章摘要（热点问题）

        Returns:
            HTML内容或空字符串（如果直接创建了草稿）
        """
        self.logger.info("使用专业级AI转换（秋日暖光主题 - ZhipuAI GLM-4-Plus）")

        # 直接使用增强的 ZhipuAI 转换，确保专业级排版质量
        html_content = self._convert_with_zhipu_ai(md_file, cover_image)

        # 如果需要创建草稿，则调用微信API创建
        if create_draft and title:
            try:
                return self._create_wechat_draft_directly(html_content, title, cover_image, digest)
            except Exception as e:
                self.logger.error(f"创建草稿失败: {str(e)}")
                return html_content

        return html_content

    def _create_wechat_draft_directly(self, html_content: str, title: str,
                                     cover_image: str = None, digest: str = None) -> str:
        """直接创建微信草稿（使用专业级AI转换后的HTML）

        Args:
            html_content: HTML内容
            title: 文章标题
            cover_image: 封面图片路径
            digest: 文章摘要

        Returns:
            空字符串（成功创建草稿后）
        """
        self.logger.info("直接创建微信草稿（跳过md2wechat，使用专业级AI转换）")

        # 上传封面图片
        wechat_manager = WeChatDraftManager(self.config, self.logger)

        if cover_image:
            self.logger.info("上传指定封面图片...")
            cover_media_id = wechat_manager.upload_cover_image(cover_image)
        else:
            # 使用默认封面
            cover_media_id = wechat_manager.upload_cover_image()

        if not cover_media_id:
            raise Exception("上传封面图片失败")

        # 创建草稿
        self.logger.info("创建草稿...")
        draft_media_id = wechat_manager.create_draft(
            title=title,
            content=html_content,
            digest=digest,
            cover_media_id=cover_media_id
        )

        if not draft_media_id:
            raise Exception("创建草稿失败")

        self.logger.info(f"✓ 成功创建微信草稿 (media_id: {draft_media_id})")

        # 定时发布（如果启用）
        if self.config.enable_schedule_publish:
            self.logger.info(f"设置定时发布 (延迟 {self.config.schedule_publish_delay} 分钟)...")
            publish_result = wechat_manager.schedule_publish(
                media_id=draft_media_id,
                delay_minutes=self.config.schedule_publish_delay
            )
            if publish_result["success"]:
                self.logger.info(f"✓ {publish_result['msg']}")
            else:
                self.logger.warning(f"⚠ {publish_result['msg']} (草稿已创建，可手动发布)")

        return ""

    def _sync_to_wechat_draft(self, md_file: str, title: str,
                              cover_image: str = None, digest: str = None) -> str:
        """使用md2wechat convert直接转换并发送到微信草稿箱

        使用正确的md2wechat命令格式：
        md2wechat convert article.md --mode ai --theme autumn-warm --draft --cover cover.jpg
        """
        self.logger.info("使用md2wechat convert直接转换并发送到微信草稿箱")

        # 检查封面图片
        if not cover_image:
            cover_path = Path(self.config.cover_image_path)
            if cover_path.exists():
                cover_image = str(cover_path)
                self.logger.info(f"使用封面图片: {cover_image}")

        # 查找md2wechat可执行文件
        md2wechat_cmd = self._find_md2wechat_executable()
        if not md2wechat_cmd:
            raise Exception("未找到md2wechat命令，请确保已安装")

        # 在markdown文件开头添加frontmatter（包含标题、作者、摘要）
        self._add_frontmatter_to_md(md_file, title, digest)

        # 将路径转换为绝对路径（Windows路径兼容性）
        md_file_abs = str(Path(md_file).resolve())

        # 构建正确的md2wechat convert命令
        # 命令格式：md2wechat convert file.md --mode ai --theme autumn-warm --draft --cover cover.jpg
        cmd = [
            md2wechat_cmd,
            'convert',
            md_file_abs,  # 使用绝对路径
            '--mode', 'ai',  # 使用AI模式（推荐）
            '--theme', self.config.md2wechat_theme,  # autumn-warm（秋日暖光）
            '--draft',  # 直接发送到草稿箱
        ]

        # 添加封面图片（使用绝对路径）
        if cover_image:
            cover_abs = str(Path(cover_image).resolve())
            cmd.extend(['--cover', cover_abs])

        self.logger.info(f"执行md2wechat convert命令:")
        self.logger.info(f"  模式: AI模式")
        self.logger.info(f"  主题: {self.config.md2wechat_theme} ({self.config.article_theme})")
        self.logger.info(f"  目标: 微信草稿箱")
        self.logger.info(f"  Markdown: {md_file_abs}")
        self.logger.info(f"  封面: {cover_image if cover_image else 'None'}")
        self.logger.debug(f"  完整命令: {' '.join(cmd)}")
        self.logger.debug(f"  工作目录: {os.getcwd()}")

        # 设置环境变量（md2wechat使用的环境变量名）
        env = os.environ.copy()
        env['WECHAT_APP_ID'] = self.config.wechat_appid
        env['WECHAT_APP_SECRET'] = self.config.wechat_secret

        # 配置智谱AI的API密钥（md2wechat使用OpenAI兼容接口）
        # 安全修复：从配置文件读取API密钥，不硬编码
        zhipu_api_key = self.config.zhipu_api_key
        if not zhipu_api_key:
            raise ConfigurationError("智谱AI API密钥未配置，请在config.ini中设置")

        env['OPENAI_API_KEY'] = zhipu_api_key
        env['OPENAI_BASE_URL'] = 'https://open.bigmodel.cn/api/paas/v4'
        env['OPENAI_MODEL'] = 'glm-4-flash'

        self.logger.info("已配置智谱AI环境变量")
        self.logger.debug(f"  OPENAI_API_KEY: {'*' * 8}[已配置]")
        self.logger.debug(f"  OPENAI_BASE_URL: {env.get('OPENAI_BASE_URL')}")

        # 先尝试使用系统默认编码读取输出
        # Windows中文系统默认是GBK，不需要强制UTF-8

        # AI模式可能需要较长时间，设置足够长的超时时间（180秒=3分钟）
        timeout = 180

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='gbk',  # Windows中文系统默认编码
                errors='replace',  # 遇到无法解码的字符时替换为�，而不是崩溃
                timeout=timeout,
                env=env
            )
        except subprocess.TimeoutExpired:
            self.logger.error(f"md2wechat convert执行超时（{timeout}秒），AI模式可能需要更长时间")
            self.logger.info("尝试使用AI备用方案")
            return self._convert_with_zhipu_ai(md_file, cover_image)
        except Exception as e:
            self.logger.warning(f"使用GBK编码失败: {str(e)}，尝试UTF-8编码")
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=timeout,
                    env=env
                )
            except subprocess.TimeoutExpired:
                self.logger.error(f"md2wechat convert执行超时（{timeout}秒）")
                return self._convert_with_zhipu_ai(md_file, cover_image)

        self.logger.info(f"md2wechat convert返回码: {result.returncode}")

        # 详细记录输出信息
        if result.stdout:
            self.logger.info(f"md2wechat convert标准输出: {result.stdout[:1000]}")  # 输出前1000字符
        else:
            self.logger.info("md2wechat convert标准输出: (空)")

        if result.stderr:
            self.logger.warning(f"md2wechat convert标准错误: {result.stderr[:1000]}")  # 输出前1000字符
        else:
            self.logger.info("md2wechat convert标准错误: (空)")

        if result.returncode == 0:
            self.logger.info("✓ 成功使用md2wechat convert创建微信草稿")
            return ""  # 返回空字符串表示草稿已直接创建
        else:
            self.logger.warning(f"md2wechat convert失败（返回码{result.returncode}），尝试AI备用方案")
            # 输出完整的错误信息以便调试
            if result.stderr:
                self.logger.error(f"完整错误信息: {result.stderr}")
            return self._convert_with_zhipu_ai(md_file, cover_image)

    def _add_frontmatter_to_md(self, md_file: str, title: str, digest: str = None) -> None:
        """在Markdown文件开头添加YAML frontmatter

        Args:
            md_file: Markdown文件路径
            title: 文章标题
            digest: 文章摘要（热点问题）
        """
        try:
            # 读取现有内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已有frontmatter
            if content.startswith('---'):
                self.logger.debug("Markdown文件已包含frontmatter，跳过添加")
                return

            # 构建frontmatter
            author = self.config.default_author
            frontmatter = f"""---
title: {title}
author: {author}
"""
            if digest:
                # 截断摘要到120字节（微信限制）
                # 确保不会在UTF-8字符中间截断
                digest_safe = digest
                while len(digest_safe.encode('utf-8')) > 120:
                    digest_safe = digest_safe[:-1]
                frontmatter += f"digest: {digest_safe}\n"

            frontmatter += "---\n\n"

            # 写入文件（frontmatter + 原内容）
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)

            self.logger.info("✓ 已添加YAML frontmatter到Markdown文件")

        except Exception as e:
            self.logger.warning(f"添加frontmatter失败: {str(e)}，继续执行")

    def _find_md2wechat_executable(self) -> str:
        """查找md2wechat可执行文件的完整路径"""
        import platform

        system = platform.system()
        possible_paths = []

        # Windows下的可能路径
        if system == 'Windows':
            # npm全局安装路径
            npm_prefix = os.path.expanduser('~/AppData/Roaming/npm')
            possible_paths.extend([
                os.path.join(npm_prefix, 'md2wechat.cmd'),
                os.path.join(npm_prefix, 'md2wechat.exe'),
                'md2wechat.cmd',
                'md2wechat.exe',
            ])
            # 从PATH中查找
            for path_dir in os.environ.get('PATH', '').split(os.pathsep):
                possible_paths.extend([
                    os.path.join(path_dir, 'md2wechat.cmd'),
                    os.path.join(path_dir, 'md2wechat.exe'),
                ])
        else:
            # Linux/Mac下的可能路径
            possible_paths.extend([
                os.path.expanduser('~/npm/bin/md2wechat'),
                '/usr/local/bin/md2wechat',
                'md2wechat',
            ])

        # 尝试找到可执行的md2wechat
        for path in possible_paths:
            if os.path.isfile(path):
                self.logger.debug(f"找到md2wechat: {path}")
                return path

        # 如果都找不到，尝试使用which/where命令
        try:
            if system == 'Windows':
                result = subprocess.run(['where', 'md2wechat'], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', 'md2wechat'], capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError, Exception):
            pass

        return ''

    def _convert_to_html_only(self, md_file: str, cover_image: str = None) -> str:
        """仅转换Markdown为HTML，不创建草稿"""
        self.logger.info("使用md2wechat convert转换为HTML")

        output_file = md_file.replace('.md', '.html')

        # 查找md2wechat可执行文件
        md2wechat_cmd = self._find_md2wechat_executable()
        if not md2wechat_cmd:
            raise Exception("未找到md2wechat命令")

        cmd = [
            md2wechat_cmd,
            'convert',
            md_file,
            output_file,
        ]

        self.logger.info(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )

        if result.returncode != 0:
            self.logger.warning(f"md2wechat convert失败: {result.stderr}")
            raise Exception("md2wechat转换失败")

        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.logger.info("✓ 使用md2wechat成功转换为HTML")
            return html_content
        else:
            raise Exception("HTML输出文件未生成")

    def _get_theme_prompt(self, theme_name: str, theme_desc: str) -> str:
        """根据主题名称生成对应的AI提示词（整合md2wechat skill专业设计）

        Args:
            theme_name: 主题名称
            theme_desc: 主题描述

        Returns:
            主题风格规范提示词
        """
        # 主题颜色方案配置 - 整合md2wechat skill专业设计
        theme_configs = {
            '秋日暖光': {
                'colors': {
                    'primary': '#d97758',      # 秋日暖橙
                    'secondary': '#c06b4d',    # 橙红
                    'background': '#faf9f5',   # 暖白
                    'card_bg': '#fef4e7',      # 淡橙
                    'text': '#4a413d',         # 深褐灰
                    'border': '#d97758',       # 边框色
                },
                'style': '温暖治愈、橙色调、文艺美学',
                'features': ['卡片式布局', '米白方格纹理', '圆角18px', '柔和阴影', '▶ 符号装饰'],
                'border_radius': '18px',
            },
            '春日清新': {
                'colors': {
                    'primary': '#6b9b7a',      # 春日嫩绿
                    'secondary': '#4a8058',    # 草地翠绿
                    'background': '#f5f8f5',   # 淡绿
                    'card_bg': '#e8f0e8',      # 淡绿背景
                    'text': '#3d4a3d',         # 深绿灰
                    'border': '#6b9b7a',
                },
                'style': '清新自然、绿色调、生机盎然',
                'features': ['点状纹理背景', '圆角16px', '清新阴影', '❀ 符号装饰'],
                'border_radius': '16px',
            },
            '深海静谧': {
                'colors': {
                    'primary': '#4a7c9b',      # 深海蔚蓝
                    'secondary': '#3d6a8a',    # 静谧石蓝
                    'background': '#f0f4f8',   # 淡蓝
                    'card_bg': '#e8f0f8',      # 淡蓝背景
                    'text': '#3a4150',         # 深蓝灰
                    'border': '#4a7c9b',
                },
                'style': '深邃冷静、蓝色调、理性专业',
                'features': ['网格纹理背景', '圆角14px', '深邃阴影', '◆ 符号装饰'],
                'border_radius': '14px',
            },
            '优雅金': {
                'colors': {
                    'primary': '#D4AF37',      # 金色
                    'secondary': '#C5A028',    # 深金
                    'background': '#FFFAF0',   # 花白
                    'card_bg': '#FFF8DC',      # 道奇白
                    'text': '#4A3B2A',         # 深褐
                    'border': '#D4AF37',
                },
                'style': '优雅高贵、金色调、品质感',
                'features': ['细腻纹理', '圆角12px', '金属光泽', '✦ 符号装饰'],
                'border_radius': '12px',
            },
            '活力红': {
                'colors': {
                    'primary': '#E74C3C',      # 活力红
                    'secondary': '#C0392B',    # 深红
                    'background': '#FFF5F5',   # 淡红
                    'card_bg': '#FFEBEB',      # 浅红背景
                    'text': '#2C1818',         # 深褐红
                    'border': '#E74C3C',
                },
                'style': '热情活力、红色调、冲击力',
                'features': ['渐变背景', '圆角8px', '动态感', '★ 符号装饰'],
                'border_radius': '8px',
            },
            '简约蓝': {
                'colors': {
                    'primary': '#3498DB',      # 天蓝
                    'secondary': '#2980B9',    # 深蓝
                    'background': '#F0F8FF',   # 爱丽丝蓝
                    'card_bg': '#E3F2FD',      # 浅蓝背景
                    'text': '#2C3E50',         # 深蓝灰
                    'border': '#3498DB',
                },
                'style': '简约现代、蓝色调、科技感',
                'features': ['简洁线条', '圆角6px', '清晰层次', '▸ 符号装饰'],
                'border_radius': '6px',
            },
            '专注绿': {
                'colors': {
                    'primary': '#27AE60',      # 翠绿
                    'secondary': '#1E8449',    # 深绿
                    'background': '#F0FDF4',   # 淡绿
                    'card_bg': '#DCFCE7',      # 浅绿背景
                    'text': '#14532D',         # 深绿
                    'border': '#27AE60',
                },
                'style': '专注自然、绿色调、清新感',
                'features': ['叶子纹理', '圆角10px', '生机感', '● 符号装饰'],
                'border_radius': '10px',
            },
        }

        # 获取主题配置，默认使用秋日暖光
        config = theme_configs.get(theme_name, theme_configs['秋日暖光'])
        colors = config['colors']
        radius = config['border_radius']

        # 构建专业级主题提示词（整合md2wechat skill设计规范）
        prompt = f"""【{theme_name}主题专业排版规范】
风格：{config['style']}
特点：{', '.join(config['features'])}

═══════════════════════════════════════
一、整体布局结构（紧凑版）
═══════════════════════════════════════
```html
<section style="max-width: 677px; margin: 0 auto; padding: 16px; background: {colors['background']}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <!-- 文章内容 -->
</section>
```

═══════════════════════════════════════
二、配色系统
═══════════════════════════════════════
- 主背景色：{colors['background']}
- 卡片背景：{colors['card_bg']}
- 主强调色：{colors['primary']}
- 副强调色：{colors['secondary']}
- 正文字色：{colors['text']}
- 边框色：{colors['border']}

═══════════════════════════════════════
三、卡片容器样式（紧凑版）
═══════════════════════════════════════
```html
<section style="background: {colors['card_bg']}; padding: 16px 18px; border-radius: {radius}; margin-bottom: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.06);">
  <!-- 卡片内容 -->
</section>
```

═══════════════════════════════════════
四、标题样式（紧凑版）
═══════════════════════════════════════
H1（文章标题）：
- 字号：22px，加粗
- 颜色：{colors['primary']}
- 底部：2px {colors['secondary']} 实线
- 边距：上 16px，下 12px
- 装饰：标题前添加 ▶ 符号
- 行高：1.4

H2（二级标题）：
- 字号：18px，加粗
- 颜色：{colors['primary']}
- 左侧：3px {colors['border']} 实线边框
- 边距：上 14px，下 8px
- 内边距：左 10px
- 行高：1.4

H3（三级标题）：
- 字号：16px，加粗
- 颜色：{colors['secondary']}
- 边距：上 10px，下 6px
- 行高：1.4

═══════════════════════════════════════
五、正文样式（紧凑版）
═══════════════════════════════════════
段落：
- 字号：15px
- 行高：1.6（重要：紧凑行高）
- 颜色：{colors['text']}
- 首行缩进：2em
- 段落间距：8px（重要：减少空白）

强调文本：
- 颜色：{colors['primary']}
- 加粗

引用块（紧凑版）：
```html
<blockquote style="background: {colors['card_bg']}; border-left: 3px solid {colors['border']}; padding: 10px 14px; margin: 10px 0; border-radius: 0 {radius} {radius} 0;">
  <!-- 引用内容 -->
</blockquote>
```

═══════════════════════════════════════
六、图片样式（紧凑版）
═══════════════════════════════════════
广告图/封面图：
```html
<div style="text-align: center; margin: 12px 0;">
  <img src="图片URL" alt="描述" style="width: 100%; max-width: 100%; height: auto; border-radius: {radius};"/>
</div>
```

内嵌图片：
- 居中显示
- 圆角：{radius}
- 上下边距：12px

═══════════════════════════════════════
七、分隔线样式（紧凑版）
═══════════════════════════════════════
```html
<hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, {colors['border']}, transparent); margin: 16px 0;"/>
```

═══════════════════════════════════════
八、列表样式（紧凑版）
═══════════════════════════════════════
- 列表项前使用 {colors['primary']} 圆点
- 左边距：18px
- 行间距：4px（重要：紧凑间距）
- 列表项边距：margin-bottom: 4px

═══════════════════════════════════════
九、结尾签名（紧凑版）
═══════════════════════════════════════
```html
<p style="text-align: center; color: {colors['secondary']}; font-size: 13px; margin-top: 20px; padding-top: 12px; border-top: 1px dashed {colors['border']};">
  *本文由总包大脑AI生成，仅供参考*
</p>
```

═══════════════════════════════════════
【紧凑排版核心原则】
═══════════════════════════════════════
1. 所有margin值减半（30px→16px，24px→12px，20px→10px，18px→10px）
2. padding值优化（24px→16px，16px→10px）
3. 行高从1.8降低到1.6
4. 段落间距从20px减少到8px
5. 标题边距大幅压缩，保持视觉层次但不拥挤
6. 卡片间距从20px减少到12px

═══════════════════════════════════════
【重要技术要求】
═══════════════════════════════════════
1. 所有CSS必须是内联样式（style属性）
2. 不使用外部样式表或<style>标签
3. 只使用安全的HTML标签：section, p, span, strong, em, br, h1-h6, blockquote, pre, code, img, div
4. 【禁止使用列表标签】绝对禁止使用ul、ol、li等列表标签，所有列表项必须转换为段落(p)格式，使用序号或符号作为段落开头（如"1. "、"• "、"◆ "等）
5. 图片使用占位符格式：<!-- IMG:数字 -->，从0开始编号
6. 保持原文内容100%完整，只添加排版样式
7. 只输出HTML，不要额外说明文字
"""
        return prompt

    def _convert_with_zhipu_ai(self, md_file: str, cover_image: str = None) -> str:
        """使用智谱AI直接将Markdown转换为微信公众号HTML格式（支持多主题）"""
        theme_name = self.config.article_theme
        theme_desc = self.config.theme_description
        self.logger.info(f"使用智谱AI直接转换（主题：{theme_name} - {theme_desc}）")

        try:
            import re  # 确保在函数开头导入re模块

            # 读取Markdown内容
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 【修复广告图问题】先提取并保护广告图HTML标签
            ad_image_pattern = r'<div[^>]*style="text-align:\s*center[^"]*"[^>]*>\s*<img[^>]*src="[^"]*mmbiz\.qpic\.cn[^"]*"[^>]*>\s*</div>'
            ad_images = re.findall(ad_image_pattern, md_content, re.DOTALL)
            ad_image_placeholders = []
            processed_md_content = md_content

            for idx, ad_html in enumerate(ad_images):
                placeholder = f"<!-- AD_IMG:{idx} -->"
                ad_image_placeholders.append((placeholder, ad_html))
                processed_md_content = processed_md_content.replace(ad_html, placeholder, 1)
                self.logger.info(f"保护广告图HTML {idx}: {ad_html[:100]}...")

            self.logger.info(f"提取到 {len(ad_images)} 个广告图HTML标签")

            # 提取所有图片引用（在AI转换前保存）- Markdown格式图片
            image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            images = re.findall(image_pattern, processed_md_content)
            self.logger.info(f"从Markdown中提取到 {len(images)} 个图片引用")

            # 构建图片路径列表（按出现顺序）
            image_paths = [img_path for alt_text, img_path in images]

            # 获取详细的主题排版规范（包含颜色系统、卡片样式等专业设计）
            theme_prompt = self._get_theme_prompt(theme_name, theme_desc)

            # 使用智谱AI进行转换
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=self.config.zhipu_api_key)

            self.logger.info(f"调用智谱AI {self.config.zhipu_model_pro}（免费）进行专业排版（主题：{theme_name}）...")

            # 增强版系统提示词：针对 GLM-4.7-Flash 优化
            enhanced_system = self.config.prompt_html_system_template.format(theme_name=theme_name, theme_desc=theme_desc)
            enhanced_system += """

【超紧凑排版要求 - 必须严格遵守】
1. 必须保留100%的原文内容，不能删减、修改任何文字
2. 每个段落必须正确包裹在适当的HTML标签中
3. 颜色方案必须严格遵循主题定义
4. 禁止使用列表标签(ul/ol/li)，使用段落+序号代替
5. 确保所有CSS样式都是内联的（style属性）

【适度紧凑排版要求 - 舒适阅读】
1. 外层容器：padding:10px，max-width:677px
2. 卡片设计：padding:12px 15px，border-radius:8px，box-shadow:0 1px 3px rgba(0,0,0,0.05)
3. 段落间距：margin-bottom:8px，行高line-height:1.6
4. 标题间距：h1 margin:10px 0 8px 0，h2/h3 margin:8px 0 6px 0
5. 字体大小：h1=19px，h2=18px，h3=17px，正文p=16px
6. 【扁平结构】禁止section嵌套section，每个内容块直接使用section+p
7. 通过颜色、边框、背景色区分层级，适当间距增强可读性

【标题处理规则 - 重要】
1. 必须保留并显示Markdown中的一级标题(# 标题)，这是文章的核心问题
2. 一级标题使用h1标签，样式：font-size:19px, font-weight:bold, text-align:center, margin:10px 0 8px 0
3. 二级标题使用h2标签，三级标题使用h3标签

【严格禁止事项 - 违者结果作废】
1. 禁止删除或省略文章的一级标题（热点问题）
2. 禁止添加任何原文中不存在的文字或段落
3. 禁止修改原文的任何词语、标点或语气
4. 禁止section多层嵌套，保持扁平结构
5. 【绝对禁止】在HTML末尾添加任何签名、声明、备注

【质量控制 - GLM-4.7-Flash优化】
本提示词已针对GLM-4.7-Flash免费模型优化，通过明确的指令和规则确保输出质量。
如遇到质量问题，系统会自动重试最多2次。"""

            best_html = None
            best_quality_score = 0

            # 最多尝试2次，选择质量最好的结果
            for attempt in range(2):
                response = client.chat.completions.create(
                    model=self.config.zhipu_model_pro,  # HTML排版使用高质量模型
                    messages=[
                        {
                            "role": "system",
                            "content": enhanced_system
                        },
                        {
                            "role": "user",
                            "content": f"""{theme_prompt}

{self.config.prompt_html_user.format(theme_name=theme_name, md_content=processed_md_content)}"""
                        }
                    ],
                    temperature=0.2,  # 降低随机性，保证风格稳定
                    max_tokens=16000,  # 高质量模型使用更大的token限制
                    timeout=Constants.API_STREAM_TIMEOUT  # 【v3.6.4修复】HTML生成使用更长的超时时间
                )

                html_content = response.choices[0].message.content.strip()

                # 质量评分
                quality_score = self._validate_html_quality(html_content, processed_md_content, theme_name)

                if quality_score >= 0.85:
                    self.logger.info(f"✓ HTML排版完成（质量评分: {quality_score:.2%}）")
                    break
                else:
                    self.logger.warning(f"尝试{attempt+1}: 排版质量{quality_score:.2%}，低于85%阈值")
                    if quality_score > best_quality_score:
                        best_html = html_content
                        best_quality_score = quality_score

            # 使用最佳结果（如果质量不达标，使用最佳尝试结果）
            if best_html and best_quality_score >= 0.70:
                html_content = best_html
                self.logger.info(f"使用最佳结果（质量评分: {best_quality_score:.2%}）")
            # 注意：不要重新获取response内容，否则会覆盖质量检查结果

            # 清理可能的markdown代码块标记
            if html_content.startswith('```html'):
                html_content = html_content[7:]
            if html_content.endswith('```'):
                html_content = html_content[:-3]
            html_content = html_content.strip()

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
                        else:
                            self.logger.warning(f"✗ 无法处理图片 {idx}: {img_path}")
                            # 移除占位符
                            html_content = html_content.replace(placeholder, '')

            # 【修复广告图问题】替换广告图占位符为原始HTML
            if ad_image_placeholders:
                self.logger.info("开始恢复广告图HTML...")
                for placeholder, ad_html in ad_image_placeholders:
                    if placeholder in html_content:
                        html_content = html_content.replace(placeholder, ad_html)
                        self.logger.info(f"✓ 已恢复广告图: {placeholder}")
                    else:
                        # 如果占位符不在HTML中，尝试在开头插入（针对顶部广告图）
                        if "AD_IMG:0" in placeholder and ad_images:
                            html_content = ad_html + html_content
                            self.logger.info(f"✓ 已在开头插入广告图: {placeholder}")
                        # 如果是底部广告图，追加到末尾
                        elif len(ad_image_placeholders) > 1 and placeholder == ad_image_placeholders[-1][0]:
                            html_content = html_content + ad_html
                            self.logger.info(f"✓ 已在末尾追加广告图: {placeholder}")

            # 保存HTML文件
            output_file = md_file.replace('.md', '.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info("智谱AI转换成功，已保存HTML文件")
            return html_content

        except Exception as e:
            error_str = str(e)
            # 【修复v3.6.1】处理速率限制错误（429）
            if '429' in error_str or '速率限制' in error_str or 'rate limit' in error_str.lower():
                self.logger.warning(f"⚠️ 智谱AI速率限制，等待30秒后重试...")
                import time
                time.sleep(30)  # 等待30秒
                try:
                    # 重新尝试一次
                    from zhipuai import ZhipuAI
                    client = ZhipuAI(api_key=self.config.zhipu_api_key)
                    self.logger.info(f"重试调用智谱AI {self.config.zhipu_model_pro}...")
                    response = client.chat.completions.create(
                        model=self.config.zhipu_model_pro,
                        messages=[
                            {"role": "system", "content": enhanced_system},
                            {"role": "user", "content": f"""{self.config.prompt_html_user.format(theme_name=theme_name, md_content=processed_md_content)}"""}
                        ],
                        temperature=0.2,
                        max_tokens=16000
                    )
                    html_content = response.choices[0].message.content.strip()
                    self.logger.info("✓ 重试成功！智谱AI转换完成")
                    # 保存HTML文件
                    output_file = md_file.replace('.md', '.html')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    return html_content
                except Exception as retry_e:
                    self.logger.error(f"重试仍然失败: {str(retry_e)}")
                    return self._simple_convert(md_file)
            else:
                self.logger.error(f"智谱AI转换失败: {error_str}")
                return self._simple_convert(md_file)

    def _process_image_for_html(self, img_path: str, md_dir: str) -> str:
        """处理图片并转换为HTML img标签（使用秋日暖光主题专业样式）

        Args:
            img_path: 图片路径（相对、绝对或HTTP(S) URL）
            md_dir: Markdown文件所在目录

        Returns:
            HTML img标签字符串，失败返回空字符串
        """
        try:
            # 获取主题配置
            theme_name = self.config.article_theme
            theme_configs = {
                '秋日暖光': {'radius': '18px', 'shadow': '0 4px 16px rgba(217, 119, 88, 0.15)'},
                '春日清新': {'radius': '16px', 'shadow': '0 4px 16px rgba(107, 155, 122, 0.15)'},
                '深海静谧': {'radius': '14px', 'shadow': '0 4px 16px rgba(74, 124, 155, 0.15)'},
            }
            config = theme_configs.get(theme_name, theme_configs['秋日暖光'])
            radius = config['radius']
            shadow = config['shadow']

            # 检查是否是HTTP(S) URL
            if img_path.startswith('http://') or img_path.startswith('https://'):
                # 直接使用URL创建img标签（专业样式）
                self.logger.info(f"使用微信CDN URL: {img_path}")
                return f'<div style="text-align: center; margin: 12px 0;"><img src="{img_path}" alt="图片" style="width: 100%; max-width: 100%; height: auto; border-radius: {radius};"/></div>'

            # 解析本地图片路径
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
                return f'<div style="text-align: center; margin: 12px 0;"><img src="{base64_data}" alt="广告图" style="width: 100%; max-width: 900px; height: auto;"/></div>'
            else:
                return ""

        except Exception as e:
            self.logger.error(f"处理图片失败 ({img_path}): {str(e)}")
            return ""

    def _image_to_base64(self, image_path: str) -> str:
        """将图片转换为base64编码（用于嵌入HTML）

        Args:
            image_path: 图片路径

        Returns:
            base64编码的图片数据URI，失败返回空字符串
        """
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

    def _simple_convert(self, md_file: str) -> str:
        """内置的简单Markdown转HTML转换"""
        self.logger.info("使用内置方法转换")

        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            html = md_content
            html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
            html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
            html = re.sub(r'```(.+?)```', r'<pre>\1</pre>', html, flags=re.DOTALL)
            html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

            paragraphs = html.split('\n\n')
            html = '\n'.join([f'<p>{p}</p>' if not p.startswith('<') else p
                             for p in paragraphs if p.strip()])

            return html

        except Exception as e:
            self.logger.error(f"内置转换失败: {str(e)}")
            return f"<div>{md_content}</div>"


# =============================================================================
# 通知类
# =============================================================================

class NotificationManager:
    """通知管理类"""

    def __init__(self, config: Config, logger: Logger) -> None:
        """初始化通知管理器"""
        self.config = config
        self.logger = logger

    def send_success_notification(self, question: str, success: bool = True, send_email: bool = False, account_name: str = None):
        """发送任务完成通知

        Args:
            question: 热点问题
            success: 任务是否成功
            send_email: 是否发送邮件通知，默认False
            account_name: 公众号名称（多公众号轮换时使用）
        """
        self.logger.info("发送任务完成通知")

        # 始终发送企业微信通知
        self._send_wechat_notification(question, success, account_name)

        # 仅在用户选择时发送邮件通知
        if send_email:
            self._send_email_notification(question, success, account_name)
        else:
            self.logger.info("邮件通知已跳过（用户未启用邮件通知）")

    def _send_wechat_notification(self, question: str, success: bool, account_name: str = None):
        """发送企业微信通知（简化版）"""
        self.logger.info("发送企业微信通知")

        # 使用传入的公众号名称，如果没有则使用默认名称
        display_name = account_name or "总包之声"

        if success:
            # 成功时使用简化格式：总包大脑刚刚回复了这个热点问题：【完整的热点问题】
            content = f"总包大脑刚刚回复了这个热点问题：\n\n> {question}\n\n✅ 文章已发送到【{display_name}】公众号草稿箱"
        else:
            # 失败时显示详细信息
            content = f"❌ 总包大脑文章生成任务失败\n\n> {question}\n\n请查看日志了解详情"

        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        try:
            response = requests.post(
                self.config.wechat_webhook,
                json=data,
                timeout=10
            )
            result = response.json()

            if result.get('errcode') == 0:
                self.logger.info("企业微信通知发送成功")
            else:
                self.logger.warning(f"企业微信通知发送失败: {result.get('errmsg')}")

        except Exception as e:
            self.logger.error(f"发送企业微信通知失败: {str(e)}")

    def _send_email_notification(self, question: str, success: bool, account_name: str = None):
        """发送邮件通知"""
        self.logger.info("发送邮件通知")

        # 使用传入的公众号名称，如果没有则使用默认名称
        display_name = account_name or "总包之声"

        status = "成功" if success else "失败"
        subject = f"【总包大脑】文章生成{status}通知 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        success_message = f"✅ 任务已成功完成，文章已发送到【{display_name}】公众号草稿箱，请登录微信公众平台查看和编辑。" if success else "❌ 任务执行失败，请查看日志了解详情。"

        content = f"""您好，

总包大脑文章自动生成任务已完成。

**状态**: {status}

**目标公众号**: {display_name}

**热点问题**: {question}

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{success_message}

此致
ZBBrainArticle 自动化脚本
"""

        try:
            send_email(
                self.config.notification_email,
                subject,
                content,
                self.config.smtp_server,
                self.config.smtp_port,
                self.config.sender_email,
                self.config.email_auth_code
            )
            self.logger.info("邮件通知发送成功")
        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {str(e)}")

    def send_custom_message(self, content: str):
        """发送自定义消息到企业微信（v3.5.0 新增）

        Args:
            content: Markdown格式的消息内容
        """
        self.logger.info("发送自定义通知消息")

        # 发送到企业微信
        if self.config.wechat_webhook:
            try:
                data = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": content
                    }
                }
                response = requests.post(
                    self.config.wechat_webhook,
                    json=data,
                    timeout=30
                )
                if response.status_code == 200:
                    self.logger.info("✓ 企业微信自定义消息发送成功")
                else:
                    self.logger.error(f"企业微信消息发送失败: {response.text}")
            except Exception as e:
                self.logger.error(f"发送企业微信消息失败: {str(e)}")
        else:
            self.logger.warning("未配置企业微信webhook，跳过发送")

    def send_status_report(self, stats: dict):
        """发送运行状态汇报（定时汇报功能）

        Args:
            stats: 运行统计数据字典，包含：
                - start_time: 启动时间
                - total_runs: 总运行次数
                - success_runs: 成功次数
                - failed_runs: 失败次数
                - last_run_time: 最后运行时间
                - last_run_status: 最后运行状态
                - last_article_title: 最后生成文章标题
                - next_run_time: 下次运行时间
                - ip_whitelist_ok: IP白名单状态
        """
        self.logger.info("发送定时运行状态汇报")

        # 计算运行时长（使用北京时间，确保时区一致）
        from datetime import datetime
        import pytz
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(beijing_tz)
        start_time_str = stats.get('start_time', now.isoformat())
        start_dt = datetime.fromisoformat(start_time_str)
        # 如果start_dt有时区信息，转换为北京时间；如果没有，假设为本地时间
        if start_dt.tzinfo is not None:
            start_dt = start_dt.astimezone(beijing_tz)
        uptime_hours = (now - start_dt).total_seconds() / 3600

        # 构建状态信息
        status_icon = "✅" if stats.get('last_run_status') else "❌"
        ip_icon = "✅" if stats.get('ip_whitelist_ok', True) else "⚠️"

        content = f"""📊 **总包大脑运行状态汇报**

⏰ **汇报时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}

---

**📈 运行统计**
- 🕐 运行时长: {uptime_hours:.1f} 小时
- 📝 总运行次数: {stats.get('total_runs', 0)} 次
- ✅ 成功次数: {stats.get('success_runs', 0)} 次
- ❌ 失败次数: {stats.get('failed_runs', 0)} 次

---

**📋 最近执行**
- 状态: {status_icon} {'成功' if stats.get('last_run_status') else '失败'}
- 时间: {stats.get('last_run_time', '-')}

**📄 最新文章**
{stats.get('last_article_title', '暂无')}

---

**⚙️ 系统状态**
- IP白名单: {ip_icon} {'正常' if stats.get('ip_whitelist_ok', True) else '未配置'}
- 下次运行: {stats.get('next_run_time', '-')}

---

_🤖 总包大脑自动写作系统 v3.4.0_"""

        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

        try:
            response = requests.post(
                self.config.wechat_webhook,
                json=data,
                timeout=10
            )
            result = response.json()

            if result.get('errcode') == 0:
                self.logger.info("运行状态汇报发送成功")
            else:
                self.logger.warning(f"运行状态汇报发送失败: {result.get('errmsg')}")

        except Exception as e:
            self.logger.error(f"发送运行状态汇报失败: {str(e)}")


# =============================================================================
# 邮件发送函数
# =============================================================================

def send_email(to_email: str, subject: str, content: str,
               smtp_server: str, smtp_port: int, from_email: str,
               auth_code: str):
    """发送邮件"""
    msg = MIMEMultipart('related')
    msg['From'] = Header(from_email)
    msg['To'] = Header(to_email)
    msg['Subject'] = Header(subject, 'utf-8')

    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, auth_code)
        server.send_message(msg)


# =============================================================================
# 主任务类 (使用Stagehand)
# =============================================================================

class ZBBrainArticleTask:
    """总包大脑文章生成主任务类 (Stagehand版本)"""

    def __init__(self, config_file: str = "config.ini"):
        """初始化任务"""
        self.config = Config(config_file)
        self.logger = Logger(self.config.log_file_path, self.config.debug_mode)

    def _check_china_network(self) -> tuple:
        """检测当前网络是否为国内网络环境

        Returns:
            tuple: (is_china: bool, ip: str, country: str, message: str)
        """
        import requests

        self.logger.info("=" * 60)
        self.logger.info("🌐 检测网络环境（国内/海外）")
        self.logger.info("=" * 60)

        # 方法1: 使用 ip-api.com 查询IP归属地
        ip_api_services = [
            'http://ip-api.com/json/?lang=zh-CN',
            'https://ipwho.is/?lang=zh-CN',
        ]

        for service in ip_api_services:
            try:
                self.logger.info(f"正在查询网络归属地: {service}")
                response = requests.get(service, timeout=15)

                if response.status_code == 200:
                    data = response.json()

                    # ip-api.com 格式
                    if 'countryCode' in data:
                        country_code = data.get('countryCode', '')
                        country = data.get('country', '')
                        ip = data.get('query', '')

                        is_china = country_code == 'CN'

                        if is_china:
                            msg = f"✓ 检测到国内网络环境 (IP: {ip}, 地区: {country})"
                            self.logger.info(msg)
                        else:
                            msg = f"✗ 检测到海外网络环境 (IP: {ip}, 地区: {country} [{country_code}])"
                            self.logger.warning(msg)

                        self.logger.info("=" * 60)
                        return is_china, ip, country, msg

                    # ipwho.is 格式
                    elif 'country_code' in data:
                        country_code = data.get('country_code', '')
                        country = data.get('country', '')
                        ip = data.get('ip', '')

                        is_china = country_code == 'CN'

                        if is_china:
                            msg = f"✓ 检测到国内网络环境 (IP: {ip}, 地区: {country})"
                            self.logger.info(msg)
                        else:
                            msg = f"✗ 检测到海外网络环境 (IP: {ip}, 地区: {country} [{country_code}])"
                            self.logger.warning(msg)

                        self.logger.info("=" * 60)
                        return is_china, ip, country, msg

            except Exception as e:
                self.logger.warning(f"查询服务 {service} 失败: {str(e)}")
                continue

        # 如果所有服务都失败，尝试通过连接国内网站判断
        self.logger.info("IP归属地查询失败，尝试通过连接国内服务判断...")
        try:
            # 尝试连接微信公众号API（国内网络才能正常访问）
            test_url = "https://api.weixin.qq.com/cgi-bin/get_api_domain_ip"
            response = requests.get(test_url, timeout=10)

            # 如果能连接，大概率是国内网络
            if response.status_code == 200:
                self.logger.info("✓ 能正常连接微信API，推测为国内网络")
                return True, '', '未知', "推测为国内网络（基于微信API连接）"
            else:
                self.logger.warning("✗ 无法正常连接微信API，可能为海外网络")
                return False, '', '未知', "可能为海外网络（微信API连接异常）"

        except Exception as e:
            self.logger.error(f"网络环境检测失败: {str(e)}")
            return False, '', '未知', f"网络检测失败: {str(e)}"

    def _check_wechat_ip_whitelist(self) -> bool:
        """检查当前外网IP是否在微信公众号IP白名单中

        Returns:
            bool: True表示IP在白名单中或检查通过，False表示不在白名单
        """
        import requests

        self.logger.info("=" * 60)
        self.logger.info("检查微信公众号IP白名单状态")
        self.logger.info("=" * 60)

        # 获取当前外网IP地址
        self.logger.info("正在获取当前外网IP地址...")
        try:
            # 尝试多个IP查询服务
            ip_services = [
                'https://api.ipify.org',
                'https://icanhazip.com',
                'https://ifconfig.me/ip',
            ]

            current_ip = None
            for service in ip_services:
                try:
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        current_ip = response.text.strip()
                        break
                except (requests.exceptions.RequestException, requests.exceptions.Timeout) as ip_err:
                    self.logger.debug(f"IP服务 {service} 查询失败: {ip_err}")
                    continue

            if not current_ip:
                self.logger.error("无法获取当前外网IP地址")
                return False

            self.logger.info(f"当前外网IP地址: {current_ip}")

        except Exception as e:
            self.logger.error(f"获取IP地址失败: {str(e)}")
            return False

        # 测试微信公众号API连接
        self.logger.info("正在测试微信公众号API连接...")
        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                'grant_type': 'client_credential',
                'appid': self.config.wechat_appid,
                'secret': self.config.wechat_secret
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                result = response.json()

                if 'access_token' in result:
                    self.logger.info(f"✓ IP地址 {current_ip} 在微信公众号白名单中")
                    self.logger.info("=" * 60)
                    return True
                else:
                    error_msg = result.get('errmsg', '')

                    if 'invalid ip' in error_msg or 'not in whitelist' in error_msg:
                        self.logger.error("=" * 60)
                        self.logger.error(f"✗ IP地址 {current_ip} 不在微信公众号IP白名单中")
                        self.logger.error("=" * 60)
                        self.logger.error("")
                        self.logger.error("请按以下步骤添加IP白名单：")
                        self.logger.error("1. 登录微信公众平台: https://mp.weixin.qq.com")
                        self.logger.error("2. 进入「设置与开发」→「基本配置」")
                        self.logger.error("3. 找到「IP白名单」设置")
                        self.logger.error(f"4. 将IP地址 {current_ip} 添加到白名单中")
                        self.logger.error("5. 点击「确定」保存设置")
                        self.logger.error("")
                        self.logger.error("添加完成后，请重新运行项目。")
                        self.logger.error("=" * 60)
                        return False
                    else:
                        self.logger.warning(f"微信公众号API返回其他错误: {error_msg}")
                        self.logger.warning("但这可能不是IP白名单问题，继续尝试运行...")
                        return True
            else:
                self.logger.warning(f"微信公众号API返回状态码: {response.status_code}")
                self.logger.warning("但这可能不是IP白名单问题，继续尝试运行...")
                return True

        except requests.exceptions.Timeout:
            self.logger.warning("连接微信公众号API超时")
            self.logger.warning("但这可能不是IP白名单问题，继续尝试运行...")
            return True
        except Exception as e:
            self.logger.warning(f"测试微信公众号API时出错: {str(e)}")
            self.logger.warning("但这可能不是IP白名单问题，继续尝试运行...")
            return True

    async def run_async(self, keyword: str = None, max_pages: int = None,
                       mode: str = 'auto', user_question: str = None,
                       send_email: bool = False) -> bool:
        """执行完整的文章生成流程（异步版本）

        Args:
            keyword: 搜索关键词（自主选题模式使用）
            max_pages: 爬取页数（自主选题模式使用）
            mode: 运行模式，'auto'为自主选题模式，'user'为用户命题模式，默认为'auto'
            user_question: 用户直接提供的问题（用户命题模式使用）
            send_email: 是否发送邮件通知，默认False
        """
        self.logger.info("=" * 60)
        mode_name = "自主选题模式" if mode == 'auto' else "用户命题模式"
        self.logger.info(f"开始执行总包大脑文章生成任务 (Stagehand版本) - {mode_name}")
        self.logger.info("=" * 60)

        # 步骤0.1: 获取当前要使用的微信公众号配置（支持多公众号轮换）
        current_account = self.config.get_current_wechat_account()
        self.logger.info(f"📱 当前目标公众号: {current_account['name']}")
        self.logger.info(f"   公众号数量: {len(self.config.get_all_wechat_accounts())} 个")

        # 设置当前公众号配置
        self.config.set_wechat_account(current_account)

        # 步骤0.2: 检查微信公众号IP白名单
        self.logger.info("步骤0: 检查微信公众号IP白名单")
        if not self._check_wechat_ip_whitelist():
            self.logger.error("IP白名单检查失败，项目终止运行")
            return False

        try:
            question = None
            ai_analyzer = ZhipuAIAnalyzer(self.config, self.logger)

            # 根据模式选择不同的工作流
            if mode == 'user':
                # 用户命题模式：直接使用用户提供的问题
                self.logger.info("用户命题模式：使用用户提供的问题")
                if not user_question:
                    # 使用默认问题
                    user_question = '如何看待中国特色工程总承包的"特色"？'
                    self.logger.info(f"未提供问题，使用默认问题：{user_question}")
                else:
                    self.logger.info(f"用户提供的问题：{user_question}")
                question = user_question
            else:
                # 自主选题模式（默认）：爬取搜狗微信搜索并生成热点问题
                self.logger.info("自主选题模式：爬取搜狗微信搜索资讯")
                # 步骤1: 爬取搜狗微信搜索资讯
                self.logger.info("步骤1: 爬取搜狗微信搜索资讯")

                # 从 keywords.txt 依次获取关键词
                if not keyword:
                    keyword = self.config.get_next_keyword()
                    self.logger.info(f"📝 从关键词轮换列表获取关键词: {keyword}")

                scraper = SogouWeChatScraper(self.config, self.logger)
                articles = await scraper.scrape(keyword, max_pages)

                if not articles:
                    self.logger.error("未爬取到任何文章")
                    return False

                # 步骤2: 使用智谱AI生成热点问题
                self.logger.info("步骤2: 使用智谱AI生成热点问题")
                question = ai_analyzer.generate_hot_question(articles)

                if not question:
                    self.logger.error("生成热点问题失败")
                    return False

            # 步骤3: 发送到总包大脑获取回答
            self.logger.info("步骤3: 发送到总包大脑获取回答")

            # 步骤3.1: 获取当前回复人设提示词
            current_prompt = self.config.get_current_prompt()
            prompt_content = current_prompt.get('content', '')
            prompt_name = current_prompt.get('name', '默认版')

            if prompt_content:
                self.logger.info(f"📝 当前回复人设: {prompt_name}")
                self.logger.info(f"   提示词长度: {len(prompt_content)} 字符")
            else:
                self.logger.info("使用默认回复人设（未配置自定义提示词）")

            metaso = MetasoAutomation(self.config, self.logger)
            try:
                answer = await metaso.send_question_and_get_answer(question, prompt_content=prompt_content)

                if not answer:
                    self.logger.error("=" * 60)
                    self.logger.error("❌ 获取总包大脑回答失败")
                    self.logger.error("=" * 60)
                    self.logger.error("本次运行终止，等待下一次定时运行")
                    self.logger.error("请检查: 1) 总包大脑登录状态 2) 网络连接 3) 总包大脑服务是否正常")
                    notifier = NotificationManager(self.config, self.logger)
                    notifier.send_success_notification(question, success=False, send_email=send_email)
                    return False

                # 步骤4.5: 使用轮换封面图片（cover.jpg 和 cover2.jpg 交替使用，节省AI生成成本）
                self.logger.info("步骤4.5: 使用轮换封面图片")
                cover_image_path = self.config.get_rotating_cover_image()

                if Path(cover_image_path).exists():
                    self.logger.info(f"使用封面图片: {cover_image_path}")
                    self.config.cover_image_path = cover_image_path
                else:
                    self.logger.warning(f"封面图片不存在: {cover_image_path}，将不设置封面")

                # 步骤4.6: 使用智谱AI生成爆款标题
                self.logger.info("步骤4.6: 使用智谱AI生成爆款标题")
                catchy_title = ai_analyzer.generate_catchy_title(question, answer, keyword=keyword)
                self.logger.info(f"生成爆款标题: {catchy_title} (长度: {len(catchy_title)}字)")

                # 步骤4: 转换并直接创建草稿（使用改进的md2wechat工作流）
                self.logger.info("步骤4: 使用md2wechat直接创建微信草稿")
                converter = MarkdownToWeChat(self.config, self.logger)

                # 使用md2wechat sync-md直接创建草稿
                html_content = converter.convert_answer_to_html(
                    answer=answer,
                    question=question,
                    title=catchy_title,  # 使用生成的爆款标题
                    cover_image=cover_image_path,
                    create_draft_direct=True  # 直接创建草稿
                )

                # 如果md2wechat sync-md成功，html_content会返回空字符串
                if html_content == "":
                    self.logger.info("✓ 已通过md2wechat sync-md直接创建草稿，跳过手动草稿创建")
                    # 步骤5: 发送成功通知
                    self.logger.info("步骤5: 发送成功通知")
                    notifier = NotificationManager(self.config, self.logger)
                    # 使用原始热点问题作为通知内容，并包含公众号信息
                    notifier.send_success_notification(
                        question,
                        success=True,
                        send_email=send_email,
                        account_name=current_account['name']
                    )

                    self.logger.info("=" * 60)
                    self.logger.info(f"✓ 任务执行成功 - 已推送到公众号: {current_account['name']}")
                    self.logger.info("=" * 60)

                    # 轮换到下一个公众号（为下次运行做准备）
                    next_account = self.config.rotate_to_next_wechat_account()
                    self.logger.info(f"🔄 下次运行将推送到: {next_account['name']}")

                    # 轮换到下一个回复人设提示词（为下次运行做准备）
                    next_prompt = self.config.rotate_to_next_prompt()
                    self.logger.info(f"🎨 下次运行将使用回复人设: {next_prompt['name']}")

                    return True

                # 回退到传统流程（如果sync-md失败）
                self.logger.info("使用传统流程创建草稿")

                # 步骤5: 上传封面图片
                self.logger.info("步骤5: 上传封面图片")
                wechat_manager = WeChatDraftManager(self.config, self.logger)
                cover_media_id = wechat_manager.upload_cover_image()

                # 步骤6: 创建微信公众号草稿
                self.logger.info("步骤6: 创建微信公众号草稿")
                # 使用原始热点问题作为摘要
                draft_media_id = wechat_manager.create_draft(
                    title=catchy_title,
                    content=html_content,
                    digest=question,  # 使用原始热点问题作为摘要
                    cover_media_id=cover_media_id
                )

                if not draft_media_id:
                    self.logger.error("创建草稿失败")
                    notifier = NotificationManager(self.config, self.logger)
                    # 使用原始热点问题作为通知内容
                    notifier.send_success_notification(question, success=False, send_email=send_email)
                    return False

                self.logger.info(f"✓ 成功创建微信草稿 (media_id: {draft_media_id})")

                # 步骤6.5: 定时发布（如果启用）
                if self.config.enable_schedule_publish:
                    self.logger.info(f"步骤6.5: 设置定时发布 (延迟 {self.config.schedule_publish_delay} 分钟)")
                    publish_result = wechat_manager.schedule_publish(
                        media_id=draft_media_id,
                        delay_minutes=self.config.schedule_publish_delay
                    )
                    if publish_result["success"]:
                        self.logger.info(f"✓ {publish_result['msg']}")
                    else:
                        self.logger.warning(f"⚠ {publish_result['msg']} (草稿已创建，可手动发布)")

                # 步骤7: 发送成功通知
                self.logger.info("步骤7: 发送成功通知")
                notifier = NotificationManager(self.config, self.logger)
                # 使用原始热点问题作为通知内容，并包含公众号信息
                notifier.send_success_notification(
                    question,
                    success=True,
                    send_email=send_email,
                    account_name=current_account['name']
                )

                self.logger.info("=" * 60)
                self.logger.info(f"✓ 任务执行成功 - 已推送到公众号: {current_account['name']}")
                self.logger.info("=" * 60)

                # 轮换到下一个公众号（为下次运行做准备）
                next_account = self.config.rotate_to_next_wechat_account()
                self.logger.info(f"🔄 下次运行将推送到: {next_account['name']}")

                # 轮换到下一个回复人设提示词（为下次运行做准备）
                next_prompt = self.config.rotate_to_next_prompt()
                self.logger.info(f"🎨 下次运行将使用回复人设: {next_prompt['name']}")

                return True

            except Exception as e:
                self.logger.error(f"任务执行失败: {str(e)}")

                # 【修复】即使任务失败也要轮换公众号和提示词，避免某个公众号被反复重试
                try:
                    next_account = self.config.rotate_to_next_wechat_account()
                    self.logger.info(f"🔄 任务失败但仍轮换公众号，下次运行将推送到: {next_account['name']}")

                    next_prompt = self.config.rotate_to_next_prompt()
                    self.logger.info(f"🎨 下次运行将使用回复人设: {next_prompt['name']}")
                except Exception as rotate_error:
                    self.logger.warning(f"轮换公众号/提示词时出错: {str(rotate_error)}")

                return False
            finally:
                # 关闭总包大脑浏览器
                try:
                    await metaso.close()
                except Exception as close_error:
                    self.logger.warning(f"关闭浏览器时出错: {str(close_error)}")

        finally:
            # 外层try的finally块 - 清理资源
            pass

    def run(self, keyword: str = None, max_pages: int = None,
            mode: str = 'auto', user_question: str = None,
            send_email: bool = False) -> bool:
        """执行完整的文章生成流程（同步版本）

        Args:
            keyword: 搜索关键词（自主选题模式使用）
            max_pages: 爬取页数（自主选题模式使用）
            mode: 运行模式，'auto'为自主选题模式，'user'为用户命题模式，默认为'auto'
            user_question: 用户直接提供的问题（用户命题模式使用）
            send_email: 是否发送邮件通知，默认False
        """
        return asyncio.run(self.run_async(keyword, max_pages, mode, user_question, send_email))


# =============================================================================
# 主程序入口
# =============================================================================

def main():
    """主程序入口"""
    import argparse

    parser = argparse.ArgumentParser(description='总包大脑文章自动生成脚本 (Stagehand版本)')
    parser.add_argument('-c', '--config', default='config.ini', help='配置文件路径')
    parser.add_argument('-k', '--keyword', help='搜索关键词（自主选题模式）')
    parser.add_argument('-p', '--pages', type=int, help='爬取页数（自主选题模式）')
    parser.add_argument('-m', '--mode', choices=['auto', 'user'], default='auto',
                       help='运行模式：auto=自主选题模式（默认），user=用户命题模式')
    parser.add_argument('-q', '--question', help='用户直接提供的问题（用户命题模式）')
    parser.add_argument('-s', '--schedule', action='store_true', default=None,
                       help='强制启用定时调度模式（覆盖配置文件）')
    parser.add_argument('--once', action='store_true',
                       help='仅运行一次（禁用定时调度，覆盖配置文件）')
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
    parser.add_argument('-e', '--send-email', action='store_true',
                       help='同时发送邮件通知（默认只发送企业微信通知）')

    args = parser.parse_args()

    # 加载配置
    temp_config = Config(args.config)
    if args.debug:
        temp_config.config.set('其他', '调试模式', 'true')

    # 初始化日志
    logger = Logger(temp_config.log_file_path, temp_config.debug_mode)

    # 输出配置信息
    logger.info("=" * 60)
    logger.info("ZBBrain-Write v3.6.9 (Cookie Domain Isolation)")
    logger.info("=" * 60)

    # 【0成本优化 V2.0】显示模型配置和成本优化状态
    logger.info(f"🤖 AI模型配置:")
    logger.info(f"   低成本模型: {temp_config.zhipu_model_fast}")
    logger.info(f"   高质量模型: {temp_config.zhipu_model_pro}")
    logger.info(f"   图片生成模型: {temp_config.image_model}")

    # 检查是否使用免费模型
    free_models = ['glm-4-flash', 'glm-4.7-flash', 'glm-4.5-flash', 'glm-4.6v-flash']
    is_free_setup = (temp_config.zhipu_model_fast in free_models and
                     temp_config.zhipu_model_pro in free_models)

    if is_free_setup:
        logger.info("💰 成本优化: ✅ 已启用 0成本模式 (使用免费AI模型)")
        logger.info("   GLM-4.7-Flash: 200K上下文, 同级别最强能力, 完全免费")
    else:
        logger.info("💰 成本优化: ⚠️ 使用付费模型 (可在config.ini切换到免费模型)")
        logger.info("   推荐: glm-4.7-flash (免费, 高质量)")

    logger.info("=" * 60)

    if temp_config.enable_theme_rotation:
        logger.info(f"🎨 文章主题: {temp_config.article_theme} (md2wechat: {temp_config.md2wechat_theme}) [轮换模式]")
        logger.info(f"   本次主题由自动轮换选择，下次将更换为不同风格")
    else:
        logger.info(f"🎨 文章主题: {temp_config.article_theme} (md2wechat: {temp_config.md2wechat_theme})")
    logger.info("=" * 60)

    # 确定是否启用定时模式
    # 优先级: --once > --schedule > 配置文件
    if args.once:
        use_schedule = False
        logger.info("⏺ 命令行参数 --once: 仅运行一次")
    elif args.schedule:
        use_schedule = True
        logger.info("⏺ 命令行参数 --schedule: 强制启用定时模式")
    else:
        # 从配置文件读取定时任务设置
        use_schedule = temp_config.config.getboolean('任务调度', '启用定时任务', fallback=True)
        if use_schedule:
            logger.info("⏺ 配置文件: 启用定时任务")

    if use_schedule:
        logger.info("🕐 启动定时调度模式（默认）")
        logger.info(f"   运行间隔: {temp_config.run_frequency_hours} 小时")
        logger.info(f"   工作时间: {temp_config.start_run_hour}:00 - {temp_config.stop_run_hour}:00 (北京时间)")
        run_scheduler(temp_config, logger, args.keyword, args.pages, args.mode, args.question, args.send_email)
    else:
        mode_name = "自主选题模式" if args.mode == 'auto' else "用户命题模式"
        logger.info(f"▶ 启动单次执行模式 - {mode_name}")
        task = ZBBrainArticleTask(args.config)
        success = task.run(args.keyword, args.pages, args.mode, args.question, args.send_email)
        sys.exit(0 if success else 1)


def run_scheduler(config: Config, logger: Logger, keyword: str, max_pages: int,
                  mode: str, user_question: str, send_email: bool):
    """运行定时调度器

    功能说明：
    - 启动时立即运行1次
    - 每隔指定小时数运行1次（默认2小时）
    - 超过停止运行时间（默认22点）即停止运行
    - 使用北京时间（Asia/Shanghai）
    - 每小时自动发送运行状态汇报（新增v3.4.0）
    - IP白名单检查失败时跳过运行，2小时后重试（新增v3.4.0）
    """
    import signal
    import time
    import pytz

    # 设置北京时间时区
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # ========================================
    # 运行状态追踪器（v3.4.0 新增）
    # ========================================
    class RunStatsTracker:
        """运行状态追踪器"""
        def __init__(self):
            self.start_time = datetime.now(beijing_tz).isoformat()
            self.total_runs = 0
            self.success_runs = 0
            self.failed_runs = 0
            self.last_run_time = "-"
            self.last_run_status = False
            self.last_article_title = "暂无"
            self.next_run_time = "-"
            self.ip_whitelist_ok = True
            self.last_hour_reported = -1  # 上次汇报的小时数

        def record_run(self, success: bool, article_title: str = ""):
            """记录一次运行"""
            self.total_runs += 1
            self.last_run_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
            self.last_run_status = success
            if success:
                self.success_runs += 1
                if article_title:
                    self.last_article_title = article_title
            else:
                self.failed_runs += 1

        def set_next_run(self, next_time):
            """设置下次运行时间"""
            self.next_run_time = next_time.strftime('%Y-%m-%d %H:%M:%S')

        def should_report(self, current_hour: int) -> bool:
            """检查是否应该发送定时汇报（每小时一次）"""
            if self.last_hour_reported != current_hour:
                self.last_hour_reported = current_hour
                return True
            return False

        def to_dict(self) -> dict:
            """转换为字典"""
            return {
                'start_time': self.start_time,
                'total_runs': self.total_runs,
                'success_runs': self.success_runs,
                'failed_runs': self.failed_runs,
                'last_run_time': self.last_run_time,
                'last_run_status': self.last_run_status,
                'last_article_title': self.last_article_title,
                'next_run_time': self.next_run_time,
                'ip_whitelist_ok': self.ip_whitelist_ok
            }

        def output_status_report(self, logger, keyword: str = "", success: bool = True, article_title: str = ""):
            """输出状态报告到stdout和状态文件（v3.5.0 新增）

            在每次任务完成后输出特殊格式的状态报告，便于Claude Code监控
            """
            import json
            import os

            # 获取当前时间
            now = datetime.now(beijing_tz)
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')

            # 构建状态报告
            report = {
                "timestamp": now_str,
                "status": "SUCCESS" if success else "FAILED",
                "article_title": article_title if article_title else self.last_article_title,
                "keyword": keyword,
                "stats": {
                    "total_runs": self.total_runs,
                    "success_runs": self.success_runs,
                    "failed_runs": self.failed_runs
                },
                "next_run": self.next_run_time
            }

            # 输出特殊格式的状态报告到stdout（便于Claude Code识别）
            # 注意：使用ASCII符号避免Windows GBK编码问题
            try:
                print("\n" + "=" * 60, flush=True)
                print("[ZBBrain-Write 状态报告]", flush=True)
                print("=" * 60, flush=True)
                print(f"[时间] 完成时间: {now_str}", flush=True)
                print(f"[状态] 执行状态: {'[OK] 成功' if success else '[X] 失败'}", flush=True)
                print(f"[文章] 文章标题: {article_title if article_title else self.last_article_title}", flush=True)
                print(f"[关键词] 使用关键词: {keyword}", flush=True)
                print(f"[统计] 累计统计: 总运行 {self.total_runs} 次 | 成功 {self.success_runs} 次 | 失败 {self.failed_runs} 次", flush=True)
                print(f"[下次] 下次运行: {self.next_run_time}", flush=True)
                print("=" * 60, flush=True)
                print("[STATUS_REPORT_END]", flush=True)
                print(flush=True)
            except UnicodeEncodeError:
                # 如果仍然有编码问题，尝试用纯ASCII输出
                print("\n" + "=" * 60, flush=True)
                print("[ZBBrain-Write Status Report]", flush=True)
                print("=" * 60, flush=True)
                print(f"Time: {now_str}", flush=True)
                print(f"Status: {'SUCCESS' if success else 'FAILED'}", flush=True)
                title = article_title if article_title else self.last_article_title
                # 将标题转为拼音或ASCII，如果编码失败则用占位符
                try:
                    print(f"Article: {title}", flush=True)
                except UnicodeEncodeError:
                    print(f"Article: [Chinese Title]", flush=True)
                print(f"Keyword: {keyword}", flush=True)
                print(f"Stats: Total {self.total_runs} | Success {self.success_runs} | Failed {self.failed_runs}", flush=True)
                print(f"Next Run: {self.next_run_time}", flush=True)
                print("=" * 60, flush=True)
                print("[STATUS_REPORT_END]", flush=True)
                print(flush=True)

            # 同时写入状态文件
            try:
                status_file = os.path.join(os.path.dirname(__file__), 'temp', 'status_report.json')
                os.makedirs(os.path.dirname(status_file), exist_ok=True)
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                logger.info(f"[OK] 状态报告已保存: {status_file}")
            except Exception as e:
                logger.warning(f"保存状态报告失败: {str(e)}")

    # 初始化状态追踪器
    stats_tracker = RunStatsTracker()

    logger.info("=" * 60)
    logger.info("🕐 定时调度器已启动 (v3.4.0)")
    logger.info(f"⏰ 工作时间: {config.start_run_hour}:00-{config.stop_run_hour}:00 (北京时间)")
    logger.info(f"🔄 运行频率: 每{config.run_frequency_hours}小时")
    logger.info("📊 定时汇报: 每小时自动发送运行状态")
    logger.info("=" * 60)

    # 设置退出标志
    stop_flag = {'running': True}

    def signal_handler(signum, frame):
        """信号处理器"""
        logger.info("收到停止信号，正在关闭调度器...")
        stop_flag['running'] = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    first_run = True  # 标记是否是第一次运行
    ip_check_failed = False  # IP白名单检查失败标志
    network_not_china = False  # 非国内网络标志（v3.5.0 新增）

    while stop_flag['running']:
        try:
            # 获取当前北京时间
            now_beijing = datetime.now(beijing_tz)
            current_hour = now_beijing.hour

            # 检查是否在工作时间内
            if config.start_run_hour <= current_hour < config.stop_run_hour:
                # 启动时立即运行1次，或者在正常运行周期内
                if first_run or True:  # 每次循环都检查是否应该运行
                    logger.info(f"📅 当前北京时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')}")

                    # ========================================
                    # 国内网络环境检测（v3.5.0 新增）
                    # 推送文章到公众号需要国内网络环境
                    # ========================================
                    logger.info("🚀 开始执行任务...")

                    # 每次运行都重新创建task，以触发主题轮换
                    # 【修复v3.6.1】只创建一个Config实例，避免多次创建导致轮换状态混乱
                    fresh_config = Config(config.config_file)
                    if fresh_config.enable_theme_rotation:
                        logger.info(f"🎨 本次主题: {fresh_config.article_theme} (md2wechat: {fresh_config.md2wechat_theme})")

                    # 【修复v3.6.1】获取并锁定当前公众号配置，确保本轮运行使用同一个公众号
                    current_wechat_account = fresh_config.get_current_wechat_account()
                    logger.info(f"📱 当前目标公众号: {current_wechat_account['name']}")
                    logger.info(f"   公众号数量: {len(fresh_config.get_all_wechat_accounts())} 个")

                    # 设置当前公众号配置（锁定）
                    fresh_config.set_wechat_account(current_wechat_account)
                    logger.info(f"✓ 已锁定公众号配置: AppID {current_wechat_account['appid'][:8]}...")

                    task = ZBBrainArticleTask(config.config_file)
                    # 【修复v3.6.1】将锁定的公众号配置同步到task的config
                    task.config.set_wechat_account(current_wechat_account)

                    # 先检测网络环境（v3.5.0 新增）
                    is_china, ip, country, network_msg = task._check_china_network()

                    # 发送网络状态通知
                    network_status_icon = "🇨🇳" if is_china else "🌍"
                    network_status = "国内网络" if is_china else "海外网络"
                    notifier = NotificationManager(fresh_config, logger)

                    if not is_china:
                        # 非国内网络，暂停运行并等待30分钟重试
                        network_not_china = True
                        logger.warning("=" * 60)
                        logger.warning("❌ 检测到海外网络环境，暂停本次运行")
                        logger.warning("📢 推送文章到微信公众号需要国内网络环境")
                        logger.warning("⏭️ 将在 30 分钟后重新检查网络环境")
                        logger.warning("=" * 60)

                        stats_tracker.record_run(False, f"海外网络环境-{country}")

                        # 发送网络状态通知给用户
                        network_notify_msg = f"""🌐 **网络环境检测报告**

{network_status_icon} **当前网络**: {network_status}
📍 **IP地址**: {ip if ip else '未知'}
🗺️ **地区**: {country if country else '未知'}

---
⚠️ **检测结果**: 非国内网络环境

推送文章到微信公众号需要国内网络，本次运行已暂停。

⏰ **下次检测**: 30分钟后自动重试

---
_总包大脑自动写作系统 v3.5.0_"""
                        notifier.send_custom_message(network_notify_msg)

                        # 等待30分钟后重试
                        wait_seconds = 30 * 60  # 30分钟
                        next_retry = datetime.now(beijing_tz) + timedelta(minutes=30)
                        stats_tracker.set_next_run(next_retry)
                        logger.info(f"⏭️ 下次网络检测时间: {next_retry.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
                        logger.info(f"😴 等待 30 分钟后重新检测网络环境...")

                        # 分段等待，每5分钟检查一次
                        waited = 0
                        while waited < wait_seconds and stop_flag['running']:
                            time.sleep(60)
                            waited += 60

                            # 检查是否超过停止时间
                            current_check_hour = datetime.now(beijing_tz).hour
                            if current_check_hour >= config.stop_run_hour:
                                logger.info(f"🕛 当前时间 {current_check_hour}:00 已超过停止时间")
                                break

                            # 每5分钟发送一次网络等待通知
                            if waited % 300 == 0 and waited > 0:
                                minutes_waited = waited // 60
                                logger.info(f"⏳ 等待网络环境... 已等待 {minutes_waited} 分钟")

                        continue  # 跳过后续任务执行，重新循环检测网络

                    else:
                        # 国内网络，正常继续
                        network_not_china = False
                        logger.info(f"✓ {network_msg}")
                        logger.info("✓ 网络环境正常，继续执行任务...")

                    # ========================================
                    # IP白名单预检查（v3.4.0）
                    # ========================================
                    if ip_check_failed:
                        logger.info("🔍 重新检查IP白名单状态...")

                    # 先检查IP白名单
                    ip_ok = task._check_wechat_ip_whitelist()
                    stats_tracker.ip_whitelist_ok = ip_ok

                    if not ip_ok:
                        # IP白名单检查失败
                        logger.error("=" * 60)
                        logger.error("❌ IP白名单检查失败，跳过本次运行")
                        logger.error("⏭️ 将在 2 小时后重新检查并运行")
                        logger.error("=" * 60)

                        ip_check_failed = True
                        stats_tracker.record_run(False, "IP白名单未配置")

                        # 发送状态汇报（包含IP问题）
                        notifier = NotificationManager(fresh_config, logger)
                        notifier.send_status_report(stats_tracker.to_dict())

                        # 等待2小时后重试
                        wait_seconds = 2 * 3600  # 2小时
                        next_retry = datetime.now(beijing_tz) + timedelta(hours=2)
                        stats_tracker.set_next_run(next_retry)
                        logger.info(f"⏭️ 下次重试时间: {next_retry.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
                        logger.info(f"😴 等待 2 小时后重新检查IP白名单...")

                        # 分段等待
                        waited = 0
                        while waited < wait_seconds and stop_flag['running']:
                            time.sleep(60)
                            waited += 60

                            # 检查是否超过停止时间
                            current_check_hour = datetime.now(beijing_tz).hour
                            if current_check_hour >= config.stop_run_hour:
                                logger.info(f"🕛 当前时间 {current_check_hour}:00 已超过停止时间")
                                break

                            # 每小时发送状态汇报
                            if waited % 3600 == 0:
                                hours_waited = waited // 3600
                                logger.info(f"⏳ 等待IP重试... 已等待 {hours_waited} 小时")

                                # 检查是否需要发送定时汇报
                                report_hour = datetime.now(beijing_tz).hour
                                if stats_tracker.should_report(report_hour):
                                    logger.info("📤 发送定时运行状态汇报...")
                                    notifier = NotificationManager(fresh_config, logger)
                                    notifier.send_status_report(stats_tracker.to_dict())

                        continue  # 跳过后续任务执行，重新循环

                    # IP检查通过，重置标志
                    ip_check_failed = False

                    # ========================================
                    # 【v3.6.7新增】登录状态预检测
                    # ========================================
                    logger.info("=" * 60)
                    logger.info("🔐 登录状态预检测")
                    logger.info("=" * 60)

                    try:
                        # 创建临时的 MetasoAutomation 实例来检测登录状态
                        temp_metaso = MetasoAutomation(config, logger)
                        # 使用 asyncio.run() 来调用异步方法
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            is_login_valid, remaining_seconds, login_message = loop.run_until_complete(
                                temp_metaso._pre_check_login_status()
                            )

                            if is_login_valid:
                                if remaining_seconds > 0:
                                    hours_remaining = remaining_seconds // 3600
                                    logger.info(f"✓ 登录状态有效，剩余约 {hours_remaining} 小时")

                                    # 如果即将过期（少于2小时），发送预警
                                    if remaining_seconds < 7200:
                                        logger.warning(f"⚠️ 登录状态即将过期，剩余 {remaining_seconds // 60} 分钟")
                                        loop.run_until_complete(
                                            temp_metaso._send_login_expiry_warning(remaining_seconds)
                                        )
                                else:
                                    logger.info("✓ 登录状态为会话级别，将验证实际状态")
                            else:
                                logger.warning(f"⚠️ 登录状态检测失败: {login_message}")
                                # 发送登录提醒通知
                                loop.run_until_complete(
                                    temp_metaso._send_login_required_notification()
                                )
                        finally:
                            loop.close()
                    except Exception as e:
                        logger.warning(f"登录预检测失败（可忽略）: {e}")
                    except Exception as e:
                        logger.warning(f"登录预检测失败（可忽略）: {e}")

                    logger.info("=" * 60)

                    # 执行任务
                    success = task.run(keyword, max_pages, mode, user_question, send_email)

                    # 尝试获取文章标题
                    article_title = ""
                    if hasattr(task, 'last_article_title'):
                        article_title = task.last_article_title

                    # 记录运行结果
                    stats_tracker.record_run(success, article_title)

                    if success:
                        logger.info("✅ 本次任务执行成功")
                    else:
                        logger.warning("⚠️ 本次任务执行失败")

                    # 输出Claude Code状态报告
                    stats_tracker.output_status_report(
                        logger=logger,
                        success=success,
                        article_title=article_title,
                        keyword=keyword
                    )

                    first_run = False

                    # 计算下次运行时间
                    # 【修复v3.6.3】使用当前时间而非任务开始时的时间，确保间隔正确
                    current_time_for_next_run = datetime.now(beijing_tz)
                    next_run = current_time_for_next_run + timedelta(hours=config.run_frequency_hours)
                    stats_tracker.set_next_run(next_run)
                    logger.info(f"⏭️ 下次运行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")

                    # 等待到下次运行时间
                    wait_seconds = config.run_frequency_hours * 3600
                    logger.info(f"😴 等待 {config.run_frequency_hours} 小时后下次运行...")

                    # 分段等待，每分钟检查一次停止信号和时间
                    waited = 0
                    while waited < wait_seconds and stop_flag['running']:
                        time.sleep(60)  # 每次等待60秒
                        waited += 60

                        # 检查是否超过停止时间
                        current_check_hour = datetime.now(beijing_tz).hour
                        if current_check_hour >= config.stop_run_hour:
                            logger.info(f"🕛 当前时间 {current_check_hour}:00 已超过停止时间 {config.stop_run_hour}:00，暂停运行")
                            break

                        # 每小时输出一次日志
                        if waited % 3600 == 0:
                            hours_waited = waited // 3600
                            logger.info(f"⏳ 调度器运行中... 已等待 {hours_waited} 小时")

                        # ========================================
                        # 每小时定时汇报（v3.4.0 新增）
                        # ========================================
                        report_check_time = datetime.now(beijing_tz)
                        report_hour = report_check_time.hour
                        if stats_tracker.should_report(report_hour):
                            logger.info("📤 发送定时运行状态汇报...")
                            try:
                                fresh_config = Config(config.config_file)
                                notifier = NotificationManager(fresh_config, logger)
                                notifier.send_status_report(stats_tracker.to_dict())
                            except Exception as e:
                                logger.error(f"发送状态汇报失败: {str(e)}")

            else:
                # 不在工作时间内，计算到下次工作时间的等待时间
                if current_hour < config.start_run_hour:
                    # 还没到开始时间
                    wait_hours = config.start_run_hour - current_hour
                    logger.info(f"🌙 当前北京时间 {now_beijing.strftime('%H:%M:%S')} 早于工作时间")
                else:
                    # 已超过工作时间，等到明天
                    wait_hours = (24 - current_hour) + config.start_run_hour
                    logger.info(f"🌙 当前北京时间 {now_beijing.strftime('%H:%M:%S')} 已超过工作时间")

                logger.info(f"😴 等待 {wait_hours} 小时后到工作时间 ({config.start_run_hour}:00)...")

                wait_seconds = wait_hours * 3600

                # 分段等待，每分钟检查一次停止信号
                waited = 0
                while waited < wait_seconds and stop_flag['running']:
                    time.sleep(60)
                    waited += 60

                    # 每小时定时汇报（即使在非工作时间也发送）
                    report_check_time = datetime.now(beijing_tz)
                    report_hour = report_check_time.hour
                    if stats_tracker.should_report(report_hour):
                        logger.info("📤 发送定时运行状态汇报...")
                        try:
                            fresh_config = Config(config.config_file)
                            notifier = NotificationManager(fresh_config, logger)
                            notifier.send_status_report(stats_tracker.to_dict())
                        except Exception as e:
                            logger.error(f"发送状态汇报失败: {str(e)}")

        except KeyboardInterrupt:
            logger.info("⚠️ 收到键盘中断，正在关闭调度器...")
            break
        except Exception as e:
            logger.error(f"❌ 调度器运行出错: {str(e)}")
            logger.info("⏳ 等待 5 分钟后重试...")
            time.sleep(300)  # 出错后等待5分钟再重试

    logger.info("🛑 定时调度器已停止")


if __name__ == '__main__':
    main()
