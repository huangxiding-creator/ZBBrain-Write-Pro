#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
总包大脑自动写作系统 - GUI配置工具
By 总包君

极简科技风深色主题配置界面
"""

import sys
import os
import configparser
from pathlib import Path

# ============================================================================
# 配色方案 - 极简科技风
# ============================================================================
COLORS = {
    'bg_dark': '#0d1117',           # 深空背景
    'bg_card': '#161b22',           # 卡片背景
    'bg_input': '#0d1117',          # 输入框背景
    'accent_blue': '#58a6ff',       # 科技蓝
    'accent_cyan': '#39d353',       # 霓虹绿
    'accent_purple': '#a371f7',     # 赛博紫
    'accent_orange': '#f78166',     # 警告橙
    'text_primary': '#e6edf3',      # 主文本
    'text_secondary': '#8b949e',    # 次要文本
    'border': '#30363d',            # 边框
    'border_focus': '#58a6ff',      # 聚焦边框
}

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QCheckBox,
        QGroupBox, QScrollArea, QFrame, QMessageBox, QGridLayout,
        QSizePolicy, QSpacerItem
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QColor, QPalette
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False
    print("PyQt5 未安装，请运行: pip install PyQt5")
    sys.exit(1)


# ============================================================================
# 主窗口
# ============================================================================
class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.config_path = Path(__file__).parent / 'config.ini'
        self.config = configparser.ConfigParser()
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("总包大脑自动写作系统 By 总包君")
        self.setGeometry(100, 50, 1100, 900)
        self.setMinimumSize(1000, 800)

        # 全局样式 - 18px及以上字体
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_dark']};
            }}
            QWidget {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                font-family: 'Microsoft YaHei UI', 'Segoe UI', sans-serif;
                font-size: 18px;
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_card']};
                width: 14px;
                border-radius: 7px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 7px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['accent_blue']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QGroupBox {{
                font-size: 20px;
                font-weight: bold;
                color: {COLORS['accent_blue']};
                border: 2px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px;
                padding-top: 30px;
                background-color: {COLORS['bg_card']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 25px;
                padding: 0 12px;
                background-color: {COLORS['bg_card']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background: transparent;
                font-size: 18px;
            }}
            QLabel#section_title {{
                font-size: 24px;
                font-weight: bold;
                color: {COLORS['accent_blue']};
                padding: 12px 0;
            }}
            QLabel#label {{
                color: {COLORS['text_secondary']};
                font-size: 18px;
            }}
        """)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)

        # 标题栏
        self.create_header(main_layout)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea {{ background: transparent; }}")

        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 10, 5, 10)
        scroll_layout.setSpacing(20)

        # 创建各配置区域
        self.create_search_section(scroll_layout)
        self.create_ai_section(scroll_layout)
        self.create_wechat_section(scroll_layout)
        self.create_theme_section(scroll_layout)
        self.create_schedule_section(scroll_layout)
        self.create_notify_section(scroll_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # 底部按钮栏
        self.create_footer(main_layout)

    def create_header(self, layout):
        """创建标题栏"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1f2e, stop:0.5 #252d3d, stop:1 #1a1f2e);
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # 左侧图标和标题
        left_layout = QHBoxLayout()

        icon_label = QLabel("🧠")
        icon_label.setStyleSheet("font-size: 32px; background: transparent;")
        left_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_main = QLabel("总包大脑自动写作系统")
        title_main.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        title_layout.addWidget(title_main)

        title_sub = QLabel("EPC总承包微信公众号自动化文章生成工具")
        title_sub.setStyleSheet(f"""
            font-size: 18px;
            color: {COLORS['text_secondary']};
            background: transparent;
        """)
        title_layout.addWidget(title_sub)

        left_layout.addLayout(title_layout)
        header_layout.addLayout(left_layout)
        header_layout.addStretch()

        # 右侧版本信息
        version_label = QLabel("v1.0\nBy 总包君")
        version_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        version_label.setStyleSheet(f"""
            font-size: 18px;
            color: {COLORS['accent_blue']};
            background: transparent;
        """)
        header_layout.addWidget(version_label)

        layout.addWidget(header)

    def create_input(self, placeholder="", password=False):
        """创建输入框"""
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        if password:
            edit.setEchoMode(QLineEdit.Password)
        edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 15px;
                color: {COLORS['text_primary']};
                font-family: 'Consolas', 'Microsoft YaHei UI', monospace;
                font-size: 18px;
                min-height: 28px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_blue']};
            }}
            QLineEdit:hover {{
                border-color: {COLORS['border_focus']};
            }}
            QLineEdit::placeholder {{
                color: {COLORS['text_secondary']};
                font-size: 16px;
            }}
        """)
        return edit

    def create_spinbox(self, min_val=0, max_val=100, suffix=""):
        """创建数字输入框"""
        spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        if suffix:
            spin.setSuffix(suffix)
        spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_input']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
                font-family: 'Consolas', monospace;
                font-size: 18px;
                min-width: 120px;
                min-height: 28px;
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent_blue']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLORS['bg_card']};
                border: none;
                width: 28px;
                border-radius: 4px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {COLORS['accent_blue']};
            }}
            QSpinBox::up-arrow {{
                color: {COLORS['text_secondary']};
                width: 16px;
            }}
            QSpinBox::down-arrow {{
                color: {COLORS['text_secondary']};
                width: 16px;
            }}
        """)
        return spin

    def create_combo(self, items):
        """创建下拉框"""
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_input']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 15px;
                color: {COLORS['text_primary']};
                font-size: 18px;
                min-width: 180px;
                min-height: 28px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['accent_blue']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
            QComboBox::down-arrow {{
                color: {COLORS['text_secondary']};
                width: 18px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                border: 2px solid {COLORS['accent_blue']};
                selection-background-color: {COLORS['accent_blue']};
                color: {COLORS['text_primary']};
                padding: 8px;
                font-size: 18px;
            }}
        """)
        return combo

    def create_checkbox(self, text, checked=True):
        """创建复选框"""
        cb = QCheckBox(text)
        cb.setChecked(checked)
        cb.setStyleSheet(f"""
            QCheckBox {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 24px;
                height: 24px;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                background-color: {COLORS['bg_input']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent_blue']};
                border-color: {COLORS['accent_blue']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['accent_blue']};
            }}
        """)
        return cb

    def create_section_label(self, text):
        """创建区域标题"""
        label = QLabel(text)
        label.setObjectName("section_title")
        label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['accent_blue']};
            padding: 12px 0;
        """)
        return label

    def create_sub_label(self, text):
        """创建子标题"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['accent_blue']};
            font-size: 20px;
            font-weight: bold;
            margin-top: 15px;
        """)
        return label

    def create_row(self, label_text, widget, widget2=None):
        """创建一行配置"""
        layout = QHBoxLayout()
        layout.setSpacing(20)

        label = QLabel(label_text)
        label.setFixedWidth(160)
        label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        layout.addWidget(label)

        layout.addWidget(widget, 1)

        if widget2:
            layout.addWidget(widget2, 1)

        return layout

    def create_search_section(self, layout):
        """搜索配置区域"""
        group = QGroupBox("🔍 搜狗微信搜索配置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)

        # 关键词
        self.keyword_edit = self.create_input("输入搜索关键词")
        group_layout.addLayout(self.create_row("默认搜索关键词:", self.keyword_edit))

        # 翻页设置
        page_layout = QHBoxLayout()
        page_label = QLabel("翻页页数:")
        page_label.setFixedWidth(160)
        page_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        page_layout.addWidget(page_label)

        page_label2 = QLabel("默认:")
        page_label2.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        page_layout.addWidget(page_label2)
        self.page_spin = self.create_spinbox(1, 20, " 页")
        page_layout.addWidget(self.page_spin)

        page_layout.addSpacing(20)

        max_label = QLabel("最大:")
        max_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        page_layout.addWidget(max_label)
        self.max_page_spin = self.create_spinbox(1, 50, " 页")
        page_layout.addWidget(self.max_page_spin)
        page_layout.addStretch()

        group_layout.addLayout(page_layout)

        # 网址
        self.search_url_edit = self.create_input("搜狗微信搜索网址")
        group_layout.addLayout(self.create_row("搜索网址:", self.search_url_edit))

        layout.addWidget(group)

    def create_ai_section(self, layout):
        """AI配置区域"""
        group = QGroupBox("🤖 智谱AI配置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)

        # API配置
        self.api_key_edit = self.create_input("智谱AI API Key", password=True)
        group_layout.addLayout(self.create_row("API Key:", self.api_key_edit))

        self.api_url_edit = self.create_input("API地址")
        group_layout.addLayout(self.create_row("API 地址:", self.api_url_edit))

        # 模型配置
        model_layout = QHBoxLayout()
        model_label = QLabel("模型配置:")
        model_label.setFixedWidth(160)
        model_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        model_layout.addWidget(model_label)

        low_label = QLabel("低成本:")
        low_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        model_layout.addWidget(low_label)
        self.low_cost_model_edit = self.create_input()
        self.low_cost_model_edit.setPlaceholderText("glm-4-flash")
        model_layout.addWidget(self.low_cost_model_edit)

        high_label = QLabel("高质量:")
        high_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        model_layout.addWidget(high_label)
        self.high_quality_model_edit = self.create_input()
        self.high_quality_model_edit.setPlaceholderText("glm-4-plus")
        model_layout.addWidget(self.high_quality_model_edit)

        group_layout.addLayout(model_layout)

        # 图片模型
        self.image_model_edit = self.create_input("图片生成模型")
        self.image_model_edit.setPlaceholderText("cogview-3-flash")
        group_layout.addLayout(self.create_row("图片生成模型:", self.image_model_edit))

        # 字符数限制
        char_layout = QHBoxLayout()
        char_label = QLabel("字符限制:")
        char_label.setFixedWidth(160)
        char_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        char_layout.addWidget(char_label)

        q_label = QLabel("问题最小:")
        q_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        char_layout.addWidget(q_label)
        self.min_question_spin = self.create_spinbox(10, 200, " 字")
        char_layout.addWidget(self.min_question_spin)

        char_layout.addSpacing(20)

        r_label = QLabel("回复最小:")
        r_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        char_layout.addWidget(r_label)
        self.min_reply_spin = self.create_spinbox(100, 2000, " 字")
        char_layout.addWidget(self.min_reply_spin)
        char_layout.addStretch()

        group_layout.addLayout(char_layout)

        layout.addWidget(group)

    def create_wechat_section(self, layout):
        """微信公众号配置区域"""
        group = QGroupBox("📱 微信公众号配置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)

        # 总包之声
        zb_label = QLabel("总包之声公众号")
        zb_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 20px; font-weight: bold;")
        group_layout.addWidget(zb_label)

        self.appid_edit = self.create_input("AppID")
        group_layout.addLayout(self.create_row("AppID:", self.appid_edit))

        self.appsecret_edit = self.create_input("AppSecret", password=True)
        group_layout.addLayout(self.create_row("AppSecret:", self.appsecret_edit))

        self.author_edit = self.create_input("默认作者名称")
        group_layout.addLayout(self.create_row("默认作者:", self.author_edit))

        # 复选框
        check_layout = QHBoxLayout()
        check_layout.setSpacing(30)
        self.original_check = self.create_checkbox("声明原创")
        self.comment_check = self.create_checkbox("开启评论")
        check_layout.addWidget(self.original_check)
        check_layout.addWidget(self.comment_check)
        check_layout.addStretch()
        group_layout.addLayout(check_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 10px 0;")
        group_layout.addWidget(line)

        # 其他公众号
        other_label = QLabel("其他公众号（可选）")
        other_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        group_layout.addWidget(other_label)

        # 工程豹
        gcb_layout = QHBoxLayout()
        gcb_label = QLabel("工程豹:")
        gcb_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        gcb_label.setFixedWidth(70)
        gcb_layout.addWidget(gcb_label)
        self.gcb_appid_edit = self.create_input("AppID")
        gcb_layout.addWidget(self.gcb_appid_edit)
        self.gcb_secret_edit = self.create_input("Secret", password=True)
        gcb_layout.addWidget(self.gcb_secret_edit)
        group_layout.addLayout(gcb_layout)

        # 总包说
        zbs_layout = QHBoxLayout()
        zbs_label = QLabel("总包说:")
        zbs_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        zbs_label.setFixedWidth(70)
        zbs_layout.addWidget(zbs_label)
        self.zbs_appid_edit = self.create_input("AppID")
        zbs_layout.addWidget(self.zbs_appid_edit)
        self.zbs_secret_edit = self.create_input("Secret", password=True)
        zbs_layout.addWidget(self.zbs_secret_edit)
        group_layout.addLayout(zbs_layout)

        layout.addWidget(group)

    def create_theme_section(self, layout):
        """主题配置区域"""
        group = QGroupBox("🎨 文章主题配置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)

        # 默认主题
        theme_layout = QHBoxLayout()
        theme_label = QLabel("默认主题:")
        theme_label.setFixedWidth(160)
        theme_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        theme_layout.addWidget(theme_label)

        self.theme_combo = self.create_combo([
            "秋日暖光", "春日清新", "深海静谧",
            "优雅金", "活力红", "简约蓝", "专注绿"
        ])
        theme_layout.addWidget(self.theme_combo)

        # 主题描述
        desc_label = QLabel("(橙/绿/蓝/金/红/蓝/绿)")
        desc_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        theme_layout.addWidget(desc_label)
        theme_layout.addStretch()

        group_layout.addLayout(theme_layout)

        # 主题轮换
        self.theme_rotation_check = self.create_checkbox("启用主题轮换（每次运行自动更换主题）")
        group_layout.addWidget(self.theme_rotation_check)

        # 广告图设置
        ad_label = QLabel("广告图设置")
        ad_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 20px; font-weight: bold; margin-top: 10px;")
        group_layout.addWidget(ad_label)

        ad_layout = QHBoxLayout()
        self.show_top_ad_check = self.create_checkbox("顶部广告图")
        self.show_bottom_ad_check = self.create_checkbox("底部广告图")
        ad_layout.addWidget(self.show_top_ad_check)
        ad_layout.addWidget(self.show_bottom_ad_check)
        ad_layout.addStretch()
        group_layout.addLayout(ad_layout)

        # 广告图路径
        self.top_ad_edit = self.create_input("顶部广告图路径")
        group_layout.addLayout(self.create_row("顶部广告图:", self.top_ad_edit))

        self.bottom_ad_edit = self.create_input("底部广告图路径")
        group_layout.addLayout(self.create_row("底部广告图:", self.bottom_ad_edit))

        layout.addWidget(group)

    def create_schedule_section(self, layout):
        """调度配置区域"""
        group = QGroupBox("⏰ 任务调度配置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)

        # 启用定时
        self.enable_schedule_check = self.create_checkbox("启用定时任务")
        group_layout.addWidget(self.enable_schedule_check)

        # 运行频率
        freq_layout = QHBoxLayout()
        freq_label = QLabel("运行频率:")
        freq_label.setFixedWidth(160)
        freq_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        freq_layout.addWidget(freq_label)

        self.frequency_spin = self.create_spinbox(1, 24, " 小时")
        freq_layout.addWidget(self.frequency_spin)
        freq_layout.addStretch()
        group_layout.addLayout(freq_layout)

        # 运行时间
        time_layout = QHBoxLayout()
        time_label = QLabel("工作时间:")
        time_label.setFixedWidth(160)
        time_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        time_layout.addWidget(time_label)

        start_label = QLabel("从")
        start_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        time_layout.addWidget(start_label)
        self.start_hour_spin = self.create_spinbox(0, 23, " 点")
        time_layout.addWidget(self.start_hour_spin)

        end_label = QLabel("到")
        end_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        time_layout.addWidget(end_label)
        self.stop_hour_spin = self.create_spinbox(0, 23, " 点")
        time_layout.addWidget(self.stop_hour_spin)
        time_layout.addStretch()
        group_layout.addLayout(time_layout)

        # 其他配置
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 10px 0;")
        group_layout.addWidget(line)

        other_label = QLabel("其他配置")
        other_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 20px; font-weight: bold;")
        group_layout.addWidget(other_label)

        self.debug_check = self.create_checkbox("调试模式")
        group_layout.addWidget(self.debug_check)

        retry_layout = QHBoxLayout()
        retry_label = QLabel("最多重试次数:")
        retry_label.setFixedWidth(160)
        retry_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        retry_layout.addWidget(retry_label)
        self.retry_spin = self.create_spinbox(1, 20, " 次")
        retry_layout.addWidget(self.retry_spin)
        retry_layout.addStretch()
        group_layout.addLayout(retry_layout)

        layout.addWidget(group)

    def create_notify_section(self, layout):
        """通知配置区域"""
        group = QGroupBox("📢 通知配置")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(15)

        # 企业微信
        wecom_label = QLabel("企业微信通知")
        wecom_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 20px; font-weight: bold;")
        group_layout.addWidget(wecom_label)

        self.wecom_webhook_edit = self.create_input("企业微信机器人Webhook地址")
        group_layout.addLayout(self.create_row("Webhook地址:", self.wecom_webhook_edit))

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 10px 0;")
        group_layout.addWidget(line)

        # 邮件通知
        email_label = QLabel("邮件通知（可选）")
        email_label.setStyleSheet(f"color: {COLORS['accent_blue']}; font-size: 20px; font-weight: bold;")
        group_layout.addWidget(email_label)

        self.receive_email_edit = self.create_input("接收通知的邮箱地址")
        group_layout.addLayout(self.create_row("接收邮箱:", self.receive_email_edit))

        smtp_layout = QHBoxLayout()
        smtp_label = QLabel("SMTP服务器:")
        smtp_label.setFixedWidth(160)
        smtp_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 18px;")
        smtp_layout.addWidget(smtp_label)
        self.smtp_server_edit = self.create_input("smtp.example.com")
        smtp_layout.addWidget(self.smtp_server_edit)
        self.smtp_port_spin = self.create_spinbox(1, 65535)
        self.smtp_port_spin.setValue(587)
        smtp_layout.addWidget(self.smtp_port_spin)
        group_layout.addLayout(smtp_layout)

        self.send_email_edit = self.create_input("发件邮箱地址")
        group_layout.addLayout(self.create_row("发件邮箱:", self.send_email_edit))

        self.email_auth_edit = self.create_input("邮箱授权码", password=True)
        group_layout.addLayout(self.create_row("授权码:", self.email_auth_edit))

        layout.addWidget(group)

    def create_footer(self, layout):
        """创建底部按钮栏"""
        footer = QFrame()
        footer.setFixedHeight(80)
        footer.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.setSpacing(15)

        # 状态标签
        self.status_label = QLabel("✅ 就绪")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            font-size: 18px;
            padding: 8px 15px;
            background-color: {COLORS['bg_input']};
            border-radius: 6px;
        """)
        footer_layout.addWidget(self.status_label)

        footer_layout.addStretch()

        # 重置按钮
        btn_reset = QPushButton("🔄 重置")
        btn_reset.setFixedSize(120, 45)
        btn_reset.setCursor(Qt.PointingHandCursor)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text_secondary']};
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_blue']};
                color: {COLORS['accent_blue']};
            }}
        """)
        btn_reset.clicked.connect(self.reset_config)
        footer_layout.addWidget(btn_reset)

        # 保存按钮
        btn_save = QPushButton("💾 保存配置")
        btn_save.setFixedSize(140, 45)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_blue']};
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #79b8ff;
            }}
        """)
        btn_save.clicked.connect(self.save_config)
        footer_layout.addWidget(btn_save)

        # 启动按钮
        btn_run = QPushButton("▶️ 启动运行")
        btn_run.setFixedSize(140, 45)
        btn_run.setCursor(Qt.PointingHandCursor)
        btn_run.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_cyan']};
                border: none;
                border-radius: 8px;
                color: #0d1117;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #46e670;
            }}
        """)
        btn_run.clicked.connect(self.run_script)
        footer_layout.addWidget(btn_run)

        layout.addWidget(footer)

    # ========================================================================
    # 配置加载/保存
    # ========================================================================
    def load_config(self):
        """加载配置文件"""
        try:
            self.config.read(self.config_path, encoding='utf-8')

            # 搜索配置
            self.keyword_edit.setText(
                self.config.get('搜狗微信搜索', '默认搜索关键词', fallback='EPC总承包'))
            self.page_spin.setValue(
                int(self.config.get('搜狗微信搜索', '默认翻页页数', fallback='5')))
            self.max_page_spin.setValue(
                int(self.config.get('搜狗微信搜索', '最大翻页页数', fallback='10')))
            self.search_url_edit.setText(
                self.config.get('搜狗微信搜索', '搜狗微信搜索网址', fallback=''))

            # AI配置
            self.api_key_edit.setText(
                self.config.get('智谱AI', 'api key', fallback=''))
            self.api_url_edit.setText(
                self.config.get('智谱AI', 'api 地址', fallback=''))
            self.low_cost_model_edit.setText(
                self.config.get('智谱AI', '低成本模型名称', fallback='glm-4-plus'))
            self.high_quality_model_edit.setText(
                self.config.get('智谱AI', '高质量模型名称', fallback='glm-4-plus'))
            self.image_model_edit.setText(
                self.config.get('智谱AI', '图片生成模型', fallback='cogview-3-flash'))
            self.min_question_spin.setValue(
                int(self.config.get('智谱AI', '问题最小字符数', fallback='50')))
            self.min_reply_spin.setValue(
                int(self.config.get('智谱AI', '回复最小字符数', fallback='500')))

            # 微信公众号
            self.appid_edit.setText(
                self.config.get('微信公众号', 'appid', fallback=''))
            self.appsecret_edit.setText(
                self.config.get('微信公众号', 'appsecret', fallback=''))
            self.author_edit.setText(
                self.config.get('微信公众号', '默认作者', fallback='总包大脑'))
            self.original_check.setChecked(
                self.config.get('微信公众号', '声明原创', fallback='1') == '1')
            self.comment_check.setChecked(
                self.config.get('微信公众号', '开启评论', fallback='1') == '1')

            self.gcb_appid_edit.setText(
                self.config.get('工程豹公众号', 'appid', fallback=''))
            self.gcb_secret_edit.setText(
                self.config.get('工程豹公众号', 'secret', fallback=''))
            self.zbs_appid_edit.setText(
                self.config.get('总包说公众号', 'appid', fallback=''))
            self.zbs_secret_edit.setText(
                self.config.get('总包说公众号', 'secret', fallback=''))

            # 主题
            theme = self.config.get('文章主题', '默认主题', fallback='秋日暖光')
            index = self.theme_combo.findText(theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
            self.theme_rotation_check.setChecked(
                self.config.get('文章主题', '启用主题轮换', fallback='true') == 'true')

            # 广告图
            self.show_top_ad_check.setChecked(
                self.config.get('广告图设置', '显示顶部广告图', fallback='true') == 'true')
            self.top_ad_edit.setText(
                self.config.get('广告图设置', '顶部广告图路径', fallback='./image/top-ad.jpg'))
            self.show_bottom_ad_check.setChecked(
                self.config.get('广告图设置', '显示底部广告图', fallback='true') == 'true')
            self.bottom_ad_edit.setText(
                self.config.get('广告图设置', '底部广告图路径', fallback='./image/bottom-image.jpg'))

            # 调度
            self.enable_schedule_check.setChecked(
                self.config.get('任务调度', '启用定时任务', fallback='true') == 'true')
            self.frequency_spin.setValue(
                int(self.config.get('任务调度', '运行频率小时', fallback='2')))
            self.start_hour_spin.setValue(
                int(self.config.get('任务调度', '开始运行小时', fallback='6')))
            self.stop_hour_spin.setValue(
                int(self.config.get('任务调度', '停止运行小时', fallback='22')))

            # 其他
            self.debug_check.setChecked(
                self.config.get('其他', '调试模式', fallback='false') == 'true')
            self.retry_spin.setValue(
                int(self.config.get('其他', '最多重试次数', fallback='5')))

            # 通知
            self.wecom_webhook_edit.setText(
                self.config.get('企业微信通知', 'Webhook地址', fallback=''))
            self.receive_email_edit.setText(
                self.config.get('邮件通知', '接收邮箱', fallback=''))
            self.smtp_server_edit.setText(
                self.config.get('邮件通知', 'SMTP服务器', fallback=''))
            self.smtp_port_spin.setValue(
                int(self.config.get('邮件通知', 'SMTP端口', fallback='587')))
            self.send_email_edit.setText(
                self.config.get('邮件通知', '发件邮箱', fallback=''))
            self.email_auth_edit.setText(
                self.config.get('邮件通知', '授权码', fallback=''))

            self.status_label.setText("✅ 配置已加载")
            self.status_label.setStyleSheet(f"""
                color: {COLORS['accent_cyan']};
                font-size: 18px;
                padding: 8px 15px;
                background-color: {COLORS['bg_input']};
                border-radius: 6px;
            """)

        except Exception as e:
            self.status_label.setText(f"⚠️ 加载失败")
            print(f"加载配置失败: {e}")

    def save_config(self):
        """保存配置文件"""
        try:
            # 搜索配置
            self.config.set('搜狗微信搜索', '默认搜索关键词', self.keyword_edit.text())
            self.config.set('搜狗微信搜索', '默认翻页页数', str(self.page_spin.value()))
            self.config.set('搜狗微信搜索', '最大翻页页数', str(self.max_page_spin.value()))
            self.config.set('搜狗微信搜索', '搜狗微信搜索网址', self.search_url_edit.text())

            # AI配置
            self.config.set('智谱AI', 'api key', self.api_key_edit.text())
            self.config.set('智谱AI', 'api 地址', self.api_url_edit.text())
            self.config.set('智谱AI', '低成本模型名称', self.low_cost_model_edit.text())
            self.config.set('智谱AI', '高质量模型名称', self.high_quality_model_edit.text())
            self.config.set('智谱AI', '图片生成模型', self.image_model_edit.text())
            self.config.set('智谱AI', '问题最小字符数', str(self.min_question_spin.value()))
            self.config.set('智谱AI', '回复最小字符数', str(self.min_reply_spin.value()))

            # 微信公众号
            self.config.set('微信公众号', 'appid', self.appid_edit.text())
            self.config.set('微信公众号', 'appsecret', self.appsecret_edit.text())
            self.config.set('微信公众号', '默认作者', self.author_edit.text())
            self.config.set('微信公众号', '声明原创', '1' if self.original_check.isChecked() else '0')
            self.config.set('微信公众号', '开启评论', '1' if self.comment_check.isChecked() else '0')

            self.config.set('工程豹公众号', 'appid', self.gcb_appid_edit.text())
            self.config.set('工程豹公众号', 'secret', self.gcb_secret_edit.text())
            self.config.set('总包说公众号', 'appid', self.zbs_appid_edit.text())
            self.config.set('总包说公众号', 'secret', self.zbs_secret_edit.text())

            # 主题
            self.config.set('文章主题', '默认主题', self.theme_combo.currentText())
            self.config.set('文章主题', '启用主题轮换', 'true' if self.theme_rotation_check.isChecked() else 'false')

            # 广告图
            self.config.set('广告图设置', '显示顶部广告图', 'true' if self.show_top_ad_check.isChecked() else 'false')
            self.config.set('广告图设置', '顶部广告图路径', self.top_ad_edit.text())
            self.config.set('广告图设置', '显示底部广告图', 'true' if self.show_bottom_ad_check.isChecked() else 'false')
            self.config.set('广告图设置', '底部广告图路径', self.bottom_ad_edit.text())

            # 调度
            self.config.set('任务调度', '启用定时任务', 'true' if self.enable_schedule_check.isChecked() else 'false')
            self.config.set('任务调度', '运行频率小时', str(self.frequency_spin.value()))
            self.config.set('任务调度', '开始运行小时', str(self.start_hour_spin.value()))
            self.config.set('任务调度', '停止运行小时', str(self.stop_hour_spin.value()))

            # 其他
            self.config.set('其他', '调试模式', 'true' if self.debug_check.isChecked() else 'false')
            self.config.set('其他', '最多重试次数', str(self.retry_spin.value()))

            # 通知
            self.config.set('企业微信通知', 'Webhook地址', self.wecom_webhook_edit.text())
            self.config.set('邮件通知', '接收邮箱', self.receive_email_edit.text())
            self.config.set('邮件通知', 'SMTP服务器', self.smtp_server_edit.text())
            self.config.set('邮件通知', 'SMTP端口', str(self.smtp_port_spin.value()))
            self.config.set('邮件通知', '发件邮箱', self.send_email_edit.text())
            self.config.set('邮件通知', '授权码', self.email_auth_edit.text())

            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)

            self.status_label.setText("✅ 保存成功")
            QMessageBox.information(self, "成功", "配置已成功保存！")

        except Exception as e:
            self.status_label.setText("❌ 保存失败")
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}")

    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, '确认', '确定要重新加载配置吗？\n未保存的修改将丢失。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.load_config()

    def run_script(self):
        """启动脚本运行"""
        self.save_config()
        script_path = Path(__file__).parent / 'ZBBrainArticle.py'
        os.system(f'start cmd /k "cd /d {script_path.parent} && python ZBBrainArticle.py"')
        self.status_label.setText("▶️ 脚本已启动")


# ============================================================================
# 主程序入口
# ============================================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 设置字体
    font = QFont('Microsoft YaHei UI', 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
