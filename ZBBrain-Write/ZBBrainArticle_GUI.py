#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZBBrainArticle - 总包大脑文章自动生成脚本 (GUI版本)

功能描述：
1. 图形化界面操作，更直观易用
2. 支持自主选题和用户命题两种模式
3. 实时显示运行日志和进度
4. 现代科技感配色方案
5. 可视化配置管理

作者：AI助手
版本：2.1.0 (GUI Edition - Config Sync)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import sys
import configparser
import os
import shutil
from datetime import datetime
from pathlib import Path

# 导入主程序模块
from ZBBrainArticle import ZBBrainArticleTask


class TextHandler:
    """处理日志输出到GUI的处理器"""

    def __init__(self, queue_obj):
        self.queue = queue_obj

    def write(self, text):
        if text.strip():
            self.queue.put(text)

    def flush(self):
        pass


class StatusIndicator:
    """状态指示器"""

    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=16, height=16,
                               bg="#0A0E27", highlightthickness=0)
        self.status = "idle"
        self.circle = self.canvas.create_oval(0, 0, 16, 16,
                                             fill="#2A2F4A", outline="")
        self.update_status("idle")

    def update_status(self, status):
        colors = {
            "idle": "#2A2F4A",
            "running": "#FFA500",
            "success": "#00FF88",
            "error": "#FF4444"
        }
        self.canvas.itemconfig(self.circle, fill=colors.get(status, "#2A2F4A"))

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)


class ModernButton(tk.Button):
    """现代风格按钮"""

    def __init__(self, parent, text, command, **kwargs):
        defaults = {
            "font": ("Microsoft YaHei UI", 10),
            "bg": "#00F0FF",
            "fg": "#0A0E27",
            "activebackground": "#00D0E0",
            "activeforeground": "#0A0E27",
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "pady": 8
        }
        defaults.update(kwargs)
        super().__init__(parent, text=text, command=command, **defaults)


class IconButton(tk.Button):
    """图标按钮"""

    COLORS = {
        "bg_panel": "#121830",
        "text_dim": "#8A92A8",
        "border": "#1E2542",
        "accent": "#00F0FF",
    }

    def __init__(self, parent, text, command, icon_size=16, **kwargs):
        defaults = {
            "font": ("Segoe UI Symbol", icon_size),
            "bg": self.COLORS["bg_panel"],
            "fg": self.COLORS["text_dim"],
            "activebackground": self.COLORS["border"],
            "activeforeground": self.COLORS["accent"],
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "pady": 5,
            "padx": 10
        }
        defaults.update(kwargs)
        super().__init__(parent, text=text, command=command, **defaults)


class SettingsWindow:
    """设置窗口"""

    COLORS = {
        "bg_main": "#0A0E27",
        "bg_panel": "#121830",
        "bg_input": "#0A0E27",
        "accent": "#00F0FF",
        "text_main": "#E0E6ED",
        "text_dim": "#8A92A8",
        "border": "#1E2542",
    }

    def __init__(self, parent, config_file="config.ini", save_callback=None):
        self.config_file = config_file
        self.save_callback = save_callback
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

        # 创建窗口
        self.window = tk.Toplevel(parent)
        self.window.title("系统配置")
        self.window.geometry("800x600")
        self.window.configure(bg=self.COLORS["bg_main"])
        self.window.transient(parent)
        self.window.grab_set()

        # 居中显示
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.window.geometry(f"800x600+{x}+{y}")

        # 创建界面
        self.create_widgets()
        self.load_current_config()

    def create_widgets(self):
        """创建界面组件"""
        # 标题栏
        header = tk.Frame(self.window, bg=self.COLORS["bg_panel"], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="⚙ 系统配置",
            font=("Microsoft YaHei UI", 16, "bold"),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["accent"]
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)

        # 主内容区
        main = tk.Frame(self.window, bg=self.COLORS["bg_main"])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建Notebook
        self.notebook = ttk.Notebook(main, style="Settings.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 配置样式
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Settings.TNotebook", background=self.COLORS["bg_main"],
                        borderwidth=0)
        style.configure("Settings.TNotebook.Tab",
                        background=self.COLORS["bg_panel"],
                        foreground=self.COLORS["text_dim"],
                        padding=[20, 10],
                        borderwidth=0)
        style.map("Settings.TNotebook.Tab",
                  background=[("selected", self.COLORS["accent"])],
                  foreground=[("selected", self.COLORS["bg_main"])])

        # 创建各个配置页
        self.create_sogou_tab()
        self.create_metaso_tab()
        self.create_zhipuai_tab()
        self.create_wechat_tab()
        self.create_workwx_tab()
        self.create_email_tab()
        self.create_schedule_tab()
        self.create_other_tab()

        # 底部按钮栏
        button_frame = tk.Frame(self.window, bg=self.COLORS["bg_panel"], height=60)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        button_frame.pack_propagate(False)

        btn_container = tk.Frame(button_frame, bg=self.COLORS["bg_panel"])
        btn_container.pack(side=tk.RIGHT, padx=20, pady=15)

        # 重置按钮
        reset_btn = ModernButton(
            btn_container,
            text="↺ 重置默认",
            command=self.reset_to_default,
            bg=self.COLORS["text_dim"],
            fg=self.COLORS["bg_main"],
            activebackground=self.COLORS["text_main"]
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮
        cancel_btn = ModernButton(
            btn_container,
            text="✕ 取消",
            command=self.window.destroy,
            bg=self.COLORS["text_dim"],
            fg=self.COLORS["bg_main"],
            activebackground=self.COLORS["text_main"]
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # 保存按钮
        save_btn = ModernButton(
            btn_container,
            text="✓ 保存配置",
            command=self.save_config
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # 应用按钮
        apply_btn = ModernButton(
            btn_container,
            text="► 应用",
            command=self.apply_config,
            bg=self.COLORS["success"],
            activebackground="#00E078"
        )
        apply_btn.pack(side=tk.LEFT, padx=5)

    def create_config_page(self, parent, title, fields):
        """创建配置页面"""
        frame = tk.Frame(parent, bg=self.COLORS["bg_panel"])
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 滚动容器
        canvas = tk.Canvas(frame, bg=self.COLORS["bg_panel"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS["bg_panel"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置项容器
        self.config_fields = {}

        current_group = None
        group_frame = None

        for field in fields:
            if field.get("type") == "group":
                # 创建分组
                if group_frame:
                    group_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

                group_frame = tk.Frame(scrollable_frame, bg=self.COLORS["bg_main"])
                group_title = tk.Label(
                    group_frame,
                    text=field["label"],
                    font=("Microsoft YaHei UI", 11, "bold"),
                    bg=self.COLORS["bg_main"],
                    fg=self.COLORS["accent"]
                )
                group_title.pack(anchor=tk.W, padx=10, pady=(10, 5))
                current_group = field["key"]
            else:
                # 创建配置项
                item_frame = tk.Frame(group_frame if group_frame else scrollable_frame,
                                     bg=self.COLORS["bg_main"])
                item_frame.pack(fill=tk.X, padx=10, pady=5)

                # 标签
                label = tk.Label(
                    item_frame,
                    text=field["label"],
                    font=("Microsoft YaHei UI", 9),
                    bg=self.COLORS["bg_main"],
                    fg=self.COLORS["text_dim"],
                    width=20,
                    anchor=tk.W
                )
                label.pack(side=tk.LEFT)

                # 输入控件
                field_key = f"{current_group}_{field['key']}" if current_group else field['key']

                if field.get("type") == "password":
                    entry = tk.Entry(
                        item_frame,
                        font=("Consolas", 9),
                        bg=self.COLORS["bg_input"],
                        fg=self.COLORS["text_main"],
                        insertbackground=self.COLORS["accent"],
                        relief=tk.FLAT,
                        highlightthickness=1,
                        highlightbackground=self.COLORS["border"],
                        highlightcolor=self.COLORS["accent"],
                        show="•"
                    )
                elif field.get("type") == "number":
                    entry = tk.Spinbox(
                        item_frame,
                        from_=field.get("min", 0),
                        to=field.get("max", 100),
                        font=("Consolas", 9),
                        bg=self.COLORS["bg_input"],
                        fg=self.COLORS["text_main"],
                        buttonbackground=self.COLORS["border"],
                        relief=tk.FLAT,
                        highlightthickness=1,
                        highlightbackground=self.COLORS["border"],
                        highlightcolor=self.COLORS["accent"]
                    )
                elif field.get("type") == "boolean":
                    var = tk.BooleanVar()
                    entry = tk.Checkbutton(
                        item_frame,
                        variable=var,
                        font=("Microsoft YaHei UI", 9),
                        bg=self.COLORS["bg_main"],
                        fg=self.COLORS["text_main"],
                        selectcolor=self.COLORS["bg_input"],
                        activebackground=self.COLORS["bg_main"]
                    )
                    self.config_fields[field_key] = ("boolean", var)
                else:
                    entry = tk.Entry(
                        item_frame,
                        font=("Consolas", 9),
                        bg=self.COLORS["bg_input"],
                        fg=self.COLORS["text_main"],
                        insertbackground=self.COLORS["accent"],
                        relief=tk.FLAT,
                        highlightthickness=1,
                        highlightbackground=self.COLORS["border"],
                        highlightcolor=self.COLORS["accent"]
                    )

                if field.get("type") != "boolean":
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
                    if field.get("type") != "number":
                        self.config_fields[field_key] = ("entry", entry)
                    else:
                        self.config_fields[field_key] = ("spinbox", entry)

        if group_frame:
            group_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        return frame

    def create_sogou_tab(self):
        """创建搜狗微信搜索配置页"""
        fields = [
            {"type": "group", "label": "🔍 搜狗微信搜索", "key": "sogou"},
            {"key": "搜狗微信搜索网址", "label": "搜索网址:", "type": "text"},
            {"key": "默认搜索关键词", "label": "默认关键词:", "type": "text"},
            {"key": "默认翻页页数", "label": "默认页数:", "type": "number", "min": 1, "max": 20},
            {"key": "最大翻页页数", "label": "最大页数:", "type": "number", "min": 1, "max": 50},
        ]
        frame = self.create_config_page(self.notebook, "搜狗搜索", fields)
        self.notebook.add(frame, text="  搜狗搜索  ")

    def create_metaso_tab(self):
        """创建总包大脑配置页"""
        fields = [
            {"type": "group", "label": "🧠 总包大脑", "key": "metaso"},
            {"key": "总包大脑网址", "label": "网址:", "type": "text"},
            {"key": "用户数据目录", "label": "数据目录:", "type": "text"},
            {"key": "最大等待回复时间", "label": "等待超时(秒):", "type": "number", "min": 60, "max": 3600},
            {"key": "回复检查间隔", "label": "检查间隔(秒):", "type": "number", "min": 1, "max": 60},
        ]
        frame = self.create_config_page(self.notebook, "总包大脑", fields)
        self.notebook.add(frame, text="  总包大脑  ")

    def create_zhipuai_tab(self):
        """创建智谱AI配置页"""
        fields = [
            {"type": "group", "label": "🤖 智谱AI", "key": "zhipuai"},
            {"key": "api key", "label": "API Key:", "type": "password"},
            {"key": "api 地址", "label": "API地址:", "type": "text"},
            {"key": "模型名称", "label": "模型名称:", "type": "text"},
            {"key": "问题最小字符数", "label": "问题最小字符:", "type": "number", "min": 10, "max": 200},
            {"key": "回复最小字符数", "label": "回复最小字符:", "type": "number", "min": 100, "max": 5000},
        ]
        frame = self.create_config_page(self.notebook, "智谱AI", fields)
        self.notebook.add(frame, text="  智谱AI  ")

    def create_wechat_tab(self):
        """创建微信公众号配置页"""
        fields = [
            {"type": "group", "label": "📱 微信公众号", "key": "wechat"},
            {"key": "公众号配置文件", "label": "多公众号配置:", "type": "text"},
            {"key": "appid", "label": "AppID:", "type": "text"},
            {"key": "appsecret", "label": "AppSecret:", "type": "password"},
            {"key": "封面图片路径", "label": "封面图片路径:", "type": "text"},
            {"key": "默认作者", "label": "默认作者:", "type": "text"},
        ]
        frame = self.create_config_page(self.notebook, "微信公众号", fields)

        # 添加多公众号配置说明
        info_frame = tk.Frame(frame, bg=self.COLORS["bg_panel"])
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        info_label = tk.Label(
            info_frame,
            text="💡 提示: 多公众号轮换功能已启用，请在 wechat_accounts.json 中配置所有公众号\n"
                 "     每次运行将自动轮换到下一个公众号进行推送",
            font=("Microsoft YaHei UI", 9),
            fg=self.COLORS["text_secondary"],
            bg=self.COLORS["bg_panel"],
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W)

        self.notebook.add(frame, text="  微信公众号  ")

    def create_workwx_tab(self):
        """创建企业微信配置页"""
        fields = [
            {"type": "group", "label": "💼 企业微信", "key": "workwx"},
            {"key": "webhook地址", "label": "Webhook地址:", "type": "password"},
        ]
        frame = self.create_config_page(self.notebook, "企业微信", fields)
        self.notebook.add(frame, text="  企业微信  ")

    def create_email_tab(self):
        """创建邮件通知配置页"""
        fields = [
            {"type": "group", "label": "📧 邮件通知", "key": "email"},
            {"key": "接收邮箱", "label": "接收邮箱:", "type": "text"},
            {"key": "smtp服务器", "label": "SMTP服务器:", "type": "text"},
            {"key": "smtp端口", "label": "SMTP端口:", "type": "number", "min": 1, "max": 65535},
            {"key": "发件邮箱", "label": "发件邮箱:", "type": "text"},
            {"key": "授权码", "label": "授权码:", "type": "password"},
        ]
        frame = self.create_config_page(self.notebook, "邮件通知", fields)
        self.notebook.add(frame, text="  邮件通知  ")

    def create_schedule_tab(self):
        """创建任务调度配置页"""
        fields = [
            {"type": "group", "label": "⏰ 任务调度", "key": "schedule"},
            {"key": "运行频率小时", "label": "运行频率(小时):", "type": "number", "min": 1, "max": 24},
            {"key": "开始运行小时", "label": "开始时间(小时):", "type": "number", "min": 0, "max": 23},
            {"key": "停止运行小时", "label": "停止时间(小时):", "type": "number", "min": 0, "max": 23},
        ]
        frame = self.create_config_page(self.notebook, "任务调度", fields)
        self.notebook.add(frame, text="  任务调度  ")

    def create_other_tab(self):
        """创建其他配置页"""
        fields = [
            {"type": "group", "label": "🔧 其他设置", "key": "other"},
            {"key": "日志文件路径", "label": "日志文件路径:", "type": "text"},
            {"key": "临时文件目录", "label": "临时文件目录:", "type": "text"},
            {"key": "调试模式", "label": "调试模式:", "type": "boolean"},
            {"key": "最多重试次数", "label": "最多重试次数:", "type": "number", "min": 1, "max": 20},
        ]
        frame = self.create_config_page(self.notebook, "其他", fields)
        self.notebook.add(frame, text="  其他  ")

    def load_current_config(self):
        """加载当前配置"""
        for key, (field_type, widget) in self.config_fields.items():
            # 解析key (section_option)
            parts = key.split('_', 1)
            if len(parts) != 2:
                continue

            section_map = {
                'sogou': '搜狗微信搜索',
                'metaso': '总包大脑',
                'zhipuai': '智谱AI',
                'wechat': '微信公众号',
                'workwx': '企业微信',
                'email': '邮件通知',
                'schedule': '任务调度',
                'other': '其他'
            }

            section = section_map.get(parts[0])
            option = parts[1]

            if not section or not self.config.has_option(section, option):
                continue

            value = self.config.get(section, option)

            if field_type == "entry":
                widget.delete(0, tk.END)
                widget.insert(0, value)
            elif field_type == "spinbox":
                widget.delete(0, tk.END)
                widget.insert(0, value)
            elif field_type == "boolean":
                widget.set(value.lower() == 'true')

    def save_config(self):
        """保存配置到文件"""
        try:
            # 更新配置
            for key, (field_type, widget) in self.config_fields.items():
                parts = key.split('_', 1)
                if len(parts) != 2:
                    continue

                section_map = {
                    'sogou': '搜狗微信搜索',
                    'metaso': '总包大脑',
                    'zhipuai': '智谱AI',
                    'wechat': '微信公众号',
                    'workwx': '企业微信',
                    'email': '邮件通知',
                    'schedule': '任务调度',
                    'other': '其他'
                }

                section = section_map.get(parts[0])
                option = parts[1]

                if not section:
                    continue

                if field_type == "entry" or field_type == "spinbox":
                    value = widget.get()
                elif field_type == "boolean":
                    value = 'true' if widget.get() else 'false'
                else:
                    continue

                self.config.set(section, option, value)

            # 备份原配置
            backup_file = self.config_file + '.backup'
            if os.path.exists(self.config_file):
                import shutil
                shutil.copy2(self.config_file, backup_file)

            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)

            messagebox.showinfo("成功", f"配置已保存到 {self.config_file}\n备份文件: {backup_file}")

            # 调用保存回调
            if self.save_callback:
                self.save_callback()

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")

    def apply_config(self):
        """应用配置（不保存到文件）"""
        messagebox.showinfo("提示", "配置已应用，将在下次运行时生效")

    def reset_to_default(self):
        """重置为默认配置"""
        if messagebox.askyesno("确认", "确定要重置所有配置为默认值吗？"):
            messagebox.showinfo("提示", "请手动删除配置文件后重启程序以恢复默认配置")


class ZBBrainArticleGUI:
    """总包大脑文章生成GUI主类"""

    # 配色方案
    COLORS = {
        "bg_main": "#0A0E27",
        "bg_panel": "#121830",
        "bg_input": "#0A0E27",
        "accent": "#00F0FF",
        "accent_hover": "#00D0E0",
        "text_main": "#E0E6ED",
        "text_dim": "#8A92A8",
        "border": "#1E2542",
        "success": "#00FF88",
        "error": "#FF4444",
        "warning": "#FFA500",
        "progress_bg": "#1A1F3A",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("总包大脑文章自动生成系统")
        self.root.geometry("950x720")
        self.root.configure(bg=self.COLORS["bg_main"])
        self.root.resizable(False, False)

        # 初始化变量
        self.running = False
        self.log_queue = queue.Queue()
        self.task_thread = None
        self.task = None
        self.mode_var = tk.StringVar(value="auto")
        self.email_var = tk.BooleanVar(value=False)
        self.config_file = "config.ini"
        self.settings_window = None

        # 配置管理器
        self.config = configparser.ConfigParser()
        self.config_modified = False  # 配置是否已修改

        # 创建界面
        self.create_header()
        self.create_main_area()
        self.create_footer()

        # 配置日志文本颜色标签
        self._setup_log_tags()

        # 启动日志处理
        self.process_log_queue()

        # 更新时间戳
        self.update_timestamp()

        # 加载配置文件参数到GUI
        self.load_config_to_gui()

    def _setup_log_tags(self):
        """配置日志文本标签"""
        self.log_text.tag_config("info", foreground=self.COLORS["text_main"])
        self.log_text.tag_config("warning", foreground=self.COLORS["warning"])
        self.log_text.tag_config("error", foreground=self.COLORS["error"])
        self.log_text.tag_config("success", foreground=self.COLORS["success"])
        self.log_text.tag_config("accent", foreground=self.COLORS["accent"])
        self.log_text.tag_config("timestamp", foreground=self.COLORS["text_dim"])
        self.log_text.tag_config("header", foreground=self.COLORS["accent"],
                                font=("Consolas", 9, "bold"))

    def create_header(self):
        """创建顶部标题栏"""
        header = tk.Frame(self.root, bg=self.COLORS["bg_main"], height=70)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # 标题容器
        title_container = tk.Frame(header, bg=self.COLORS["bg_main"])
        title_container.pack(side=tk.LEFT, padx=30, pady=15)

        # 主标题
        title = tk.Label(
            title_container,
            text="总包大脑文章自动生成系统",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["accent"]
        )
        title.pack(anchor=tk.W)

        # 版本标签
        version = tk.Label(
            title_container,
            text="v2.1 GUI Config Sync",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["text_dim"]
        )
        version.pack(anchor=tk.W, pady=(2, 0))

        # 右侧按钮容器
        right_container = tk.Frame(header, bg=self.COLORS["bg_main"])
        right_container.pack(side=tk.RIGHT, padx=30, pady=20)

        # 配置按钮组容器
        config_buttons_frame = tk.Frame(right_container, bg=self.COLORS["bg_main"])
        config_buttons_frame.pack(side=tk.RIGHT)

        # 重新加载配置按钮
        reload_btn = tk.Button(
            config_buttons_frame,
            text="↻ 重载",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"],
            activebackground=self.COLORS["border"],
            activeforeground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            pady=5,
            padx=8,
            command=self.reload_config_from_file
        )
        reload_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 保存配置按钮
        save_btn = tk.Button(
            config_buttons_frame,
            text="💾 保存",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"],
            activebackground=self.COLORS["border"],
            activeforeground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            pady=5,
            padx=8,
            command=self.save_gui_to_config
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 配置状态指示器
        self.config_status_dot = tk.Label(
            config_buttons_frame,
            text="●",
            font=("Microsoft YaHei UI", 12),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["success"]
        )
        self.config_status_dot.pack(side=tk.LEFT)

        # 设置按钮
        settings_btn = tk.Button(
            right_container,
            text="⚙ 配置",
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"],
            activebackground=self.COLORS["border"],
            activeforeground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            pady=5,
            padx=12,
            command=self.open_settings
        )
        settings_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 状态指示器
        self.status_indicator = StatusIndicator(right_container)
        self.status_indicator.pack(side=tk.RIGHT)

        # 状态标签
        self.state_label = tk.Label(
            right_container,
            text="就绪",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["text_dim"]
        )
        self.state_label.pack(side=tk.RIGHT, padx=(0, 10))

        # 底部分隔线
        separator = tk.Frame(self.root, bg=self.COLORS["accent"], height=2)
        separator.pack(fill=tk.X)

    def create_main_area(self):
        """创建主内容区域"""
        main = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        # 创建左侧控制面板
        self.create_control_panel(main)

        # 创建右侧日志面板
        self.create_log_panel(main)

    def create_control_panel(self, parent):
        """创建左侧控制面板"""
        panel = tk.Frame(parent, bg=self.COLORS["bg_panel"], width=320)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        panel.pack_propagate(False)

        # 面板标题
        title = tk.Label(
            panel,
            text="控制面板",
            font=("Microsoft YaHei UI", 13, "bold"),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_main"]
        )
        title.pack(pady=(18, 15), padx=18, anchor=tk.W)

        # ===== 运行模式选择 =====
        mode_label = tk.Label(
            panel,
            text="运行模式",
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"]
        )
        mode_label.pack(anchor=tk.W, padx=18, pady=(5, 8))

        # 单选按钮容器
        radio_frame = tk.Frame(panel, bg=self.COLORS["bg_panel"])
        radio_frame.pack(fill=tk.X, padx=18, pady=(0, 15))

        # 自主选题模式
        auto_radio = tk.Radiobutton(
            radio_frame,
            text="自主选题",
            variable=self.mode_var,
            value="auto",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_main"],
            selectcolor=self.COLORS["bg_main"],
            activebackground=self.COLORS["bg_panel"],
            activeforeground=self.COLORS["accent"],
            indicatoron=True,
            command=self.on_mode_change
        )
        auto_radio.pack(anchor=tk.W, pady=2)

        # 用户命题模式
        user_radio = tk.Radiobutton(
            radio_frame,
            text="用户命题",
            variable=self.mode_var,
            value="user",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_main"],
            selectcolor=self.COLORS["bg_main"],
            activebackground=self.COLORS["bg_panel"],
            activeforeground=self.COLORS["accent"],
            indicatoron=True,
            command=self.on_mode_change
        )
        user_radio.pack(anchor=tk.W, pady=2)

        # ===== 自主选题模式输入框 =====
        self.auto_inputs_frame = tk.Frame(panel, bg=self.COLORS["bg_panel"])
        self.auto_inputs_frame.pack(fill=tk.X, padx=18)

        # 搜索关键词
        keyword_label = tk.Label(
            self.auto_inputs_frame,
            text="搜索关键词",
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"]
        )
        keyword_label.pack(anchor=tk.W, pady=(5, 6))

        self.keyword_entry = tk.Entry(
            self.auto_inputs_frame,
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_input"],
            fg=self.COLORS["text_main"],
            insertbackground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["accent"]
        )
        self.keyword_entry.pack(fill=tk.X, pady=(0, 12))
        # 绑定配置修改事件
        self.keyword_entry.bind('<KeyRelease>', self.on_config_modified)

        # 爬取页数
        pages_label = tk.Label(
            self.auto_inputs_frame,
            text="爬取页数",
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"]
        )
        pages_label.pack(anchor=tk.W, pady=(0, 6))

        self.pages_entry = tk.Entry(
            self.auto_inputs_frame,
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_input"],
            fg=self.COLORS["text_main"],
            insertbackground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["accent"],
            width=15
        )
        self.pages_entry.pack(anchor=tk.W, pady=(0, 12))
        # 绑定配置修改事件
        self.pages_entry.bind('<KeyRelease>', self.on_config_modified)

        # ===== 用户命题模式输入框 =====
        self.user_inputs_frame = tk.Frame(panel, bg=self.COLORS["bg_panel"])

        question_label = tk.Label(
            self.user_inputs_frame,
            text="用户问题",
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"]
        )
        question_label.pack(anchor=tk.W, padx=18, pady=(5, 6))

        self.question_text = scrolledtext.ScrolledText(
            self.user_inputs_frame,
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_input"],
            fg=self.COLORS["text_main"],
            insertbackground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["accent"],
            height=5,
            wrap=tk.WORD,
            padx=8,
            pady=6
        )
        self.question_text.pack(fill=tk.X, padx=18, pady=(0, 12))

        # ===== 选项复选框 =====
        options_frame = tk.Frame(panel, bg=self.COLORS["bg_panel"])
        options_frame.pack(fill=tk.X, padx=18, pady=(0, 18))

        email_check = tk.Checkbutton(
            options_frame,
            text="同时发送邮件通知",
            variable=self.email_var,
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_main"],
            selectcolor=self.COLORS["bg_main"],
            activebackground=self.COLORS["bg_panel"],
            activeforeground=self.COLORS["accent"]
        )
        email_check.pack(anchor=tk.W, pady=2)

        # 分隔线
        separator = tk.Frame(panel, bg=self.COLORS["border"], height=1)
        separator.pack(fill=tk.X, padx=18, pady=(10, 18))

        # ===== 进度条 =====
        progress_label = tk.Label(
            panel,
            text="执行进度",
            font=("Microsoft YaHei UI", 10),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"]
        )
        progress_label.pack(anchor=tk.W, padx=18, pady=(0, 8))

        # 进度条画布
        self.progress_canvas = tk.Canvas(
            panel,
            width=284,
            height=8,
            bg=self.COLORS["bg_panel"],
            highlightthickness=0
        )
        self.progress_canvas.pack(padx=18, pady=(0, 6))

        # 进度条背景
        self.progress_canvas.create_rectangle(
            0, 0, 284, 8,
            fill=self.COLORS["progress_bg"],
            outline=""
        )

        # 进度条前景
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 8,
            fill=self.COLORS["accent"],
            outline=""
        )

        # 进度文本
        self.progress_text = tk.Label(
            panel,
            text="就绪",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["accent"]
        )
        self.progress_text.pack(anchor=tk.W, padx=18, pady=(0, 18))

        # ===== 控制按钮 =====
        button_frame = tk.Frame(panel, bg=self.COLORS["bg_panel"])
        button_frame.pack(fill=tk.X, padx=18, pady=(0, 18))

        # 开始运行按钮
        self.run_btn = ModernButton(
            button_frame,
            text="开始运行",
            command=self.start_task,
            width=284
        )
        self.run_btn.pack(fill=tk.X, pady=(0, 10))

        # 停止运行按钮
        self.stop_btn = ModernButton(
            button_frame,
            text="停止运行",
            command=self.stop_task,
            width=284,
            bg="#FF4444",
            fg="#0A0E27",
            activebackground="#E04040",
            activeforeground="#0A0E27"
        )
        self.stop_btn.pack(fill=tk.X, pady=(0, 10))

        # 清空日志按钮
        self.clear_btn = ModernButton(
            button_frame,
            text="清空日志",
            command=self.clear_log,
            width=284,
            bg=self.COLORS["text_dim"],
            fg="#0A0E27",
            activebackground=self.COLORS["text_main"],
            activeforeground="#0A0E27"
        )
        self.clear_btn.pack(fill=tk.X)

    def create_log_panel(self, parent):
        """创建右侧日志面板"""
        panel = tk.Frame(parent, bg=self.COLORS["bg_panel"])
        panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 标题栏
        header = tk.Frame(panel, bg=self.COLORS["bg_panel"], height=45)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # 标题
        title = tk.Label(
            header,
            text="运行日志",
            font=("Microsoft YaHei UI", 13, "bold"),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_main"]
        )
        title.pack(side=tk.LEFT, padx=18, pady=12)

        # 时间戳
        self.timestamp_label = tk.Label(
            header,
            text="",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"]
        )
        self.timestamp_label.pack(side=tk.RIGHT, padx=18, pady=12)

        # 分隔线
        separator = tk.Frame(panel, bg=self.COLORS["border"], height=1)
        separator.pack(fill=tk.X)

        # 日志文本区域
        log_frame = tk.Frame(panel, bg=self.COLORS["bg_main"])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg=self.COLORS["bg_main"],
            fg=self.COLORS["text_main"],
            insertbackground=self.COLORS["accent"],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["accent"],
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=10,
            pady=8
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def create_footer(self):
        """创建底部状态栏"""
        footer = tk.Frame(self.root, bg=self.COLORS["bg_panel"], height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        # 配置文件信息
        config_info = tk.Label(
            footer,
            text=f"配置文件: {self.config_file}",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"],
            anchor=tk.W
        )
        config_info.pack(side=tk.LEFT, padx=18, pady=8)

        # 状态信息
        self.status_text = tk.Label(
            footer,
            text="就绪",
            font=("Microsoft YaHei UI", 9),
            bg=self.COLORS["bg_panel"],
            fg=self.COLORS["text_dim"],
            anchor=tk.E
        )
        self.status_text.pack(side=tk.RIGHT, padx=18, pady=8)

        # 顶部分隔线
        separator = tk.Frame(self.root, bg=self.COLORS["accent"], height=2)
        separator.pack(fill=tk.X, side=tk.BOTTOM)

    def open_settings(self):
        """打开设置窗口"""
        if self.settings_window is None or not self.settings_window.window.winfo_exists():
            self.settings_window = SettingsWindow(
                self.root,
                self.config_file,
                save_callback=self.on_config_saved
            )

    def on_config_saved(self):
        """配置保存回调"""
        self.add_log("配置已更新，将在下次运行时生效", "info")

    def on_mode_change(self):
        """模式切换事件"""
        mode = self.mode_var.get()
        if mode == "auto":
            self.auto_inputs_frame.pack(fill=tk.X, padx=18, after=self.mode_var.master)
            self.user_inputs_frame.pack_forget()
        else:
            self.auto_inputs_frame.pack_forget()
            self.user_inputs_frame.pack(fill=tk.X, padx=18, after=self.mode_var.master)

    def add_log(self, message, level="info"):
        """添加日志"""
        if "ERROR" in message or level == "error":
            tag = "error"
        elif "WARNING" in message or level == "warning":
            tag = "warning"
        elif "SUCCESS" in message or "✓" in message or "✅" in message:
            tag = "success"
        elif any(x in message for x in ["步骤", "=====", "INFO -"]):
            tag = "accent"
        else:
            tag = "info"

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def process_log_queue(self):
        """处理日志队列"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.add_log(message)
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)

    def update_progress(self, value, text=""):
        """更新进度条"""
        value = max(0, min(100, value))
        bar_width = int(284 * value / 100)
        self.progress_canvas.coords(self.progress_bar, 0, 0, bar_width, 8)
        if text:
            self.progress_text.config(text=text)

    def update_status(self, status, text=""):
        """更新状态"""
        self.status_indicator.update_status(status)
        if text:
            self.state_label.config(text=text)
            self.status_text.config(text=text)

    def update_timestamp(self):
        """更新时间戳"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timestamp_label.config(text=now)
        self.root.after(1000, self.update_timestamp)

    def start_task(self):
        """启动任务"""
        if self.running:
            messagebox.showwarning("警告", "任务正在运行中！")
            return

        # 获取参数
        mode = self.mode_var.get()

        if mode == "auto":
            keyword = self.keyword_entry.get().strip()
            pages = self.pages_entry.get().strip()
            question = None

            if not keyword:
                messagebox.showerror("错误", "请输入搜索关键词！")
                return

            try:
                pages = int(pages)
            except ValueError:
                messagebox.showerror("错误", "页数必须是数字！")
                return
        else:
            keyword = None
            pages = None
            question = self.question_text.get("1.0", tk.END).strip()

            if not question:
                messagebox.showerror("错误", "请输入用户问题！")
                return

        send_email = self.email_var.get()

        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        # 开始任务
        self.running = True
        self.update_status("running", "运行中")
        self.update_progress(0, "准备中...")

        # 启动任务线程
        self.task_thread = threading.Thread(
            target=self.run_task,
            args=(mode, keyword, pages, question, send_email),
            daemon=True
        )
        self.task_thread.start()

    def run_task(self, mode, keyword, pages, question, send_email):
        """运行任务"""
        try:
            # 重定向日志
            handler = TextHandler(self.log_queue)
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = handler
            sys.stderr = handler

            # 创建任务
            self.task = ZBBrainArticleTask(self.config_file)

            # 执行任务
            result = self.task.run(
                keyword=keyword,
                max_pages=pages,
                mode=mode,
                user_question=question,
                send_email=send_email
            )

            # 恢复标准输出
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            if result:
                self.root.after(0, lambda: self.update_status("success", "成功"))
                self.root.after(0, lambda: self.update_progress(100, "完成"))
                self.root.after(0, lambda: messagebox.showinfo("成功", "任务执行成功！"))
            else:
                self.root.after(0, lambda: self.update_status("error", "失败"))
                self.root.after(0, lambda: messagebox.showerror("失败", "任务执行失败！"))

        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.root.after(0, lambda: self.update_status("error", "错误"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"执行出错：{str(e)}"))

        finally:
            self.running = False
            if not self.task_thread.is_alive():
                self.root.after(0, lambda: self.update_status("idle", "就绪"))

    def stop_task(self):
        """停止任务"""
        if not self.running:
            return

        if messagebox.askyesno("确认", "确定要停止任务吗？"):
            self.running = False
            self.update_status("idle", "已停止")
            self.update_progress(0, "已停止")

    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def load_config_to_gui(self):
        """从配置文件加载参数到GUI界面"""
        try:
            if not os.path.exists(self.config_file):
                return

            self.config.read(self.config_file, encoding='utf-8')

            # 加载搜狗微信搜索配置
            if '搜狗微信搜索' in self.config:
                default_keyword = self.config.get('搜狗微信搜索', '默认搜索关键词', fallback='')
                default_pages = self.config.get('搜狗微信搜索', '默认翻页页数', fallback='5')

                # 更新GUI输入框
                self.keyword_entry.delete(0, tk.END)
                self.keyword_entry.insert(0, default_keyword)

                self.pages_entry.delete(0, tk.END)
                self.pages_entry.insert(0, default_pages)

            # 重置修改标志
            self.config_modified = False
            self._update_config_status()

        except Exception as e:
            messagebox.showerror("配置加载错误", f"加载配置文件失败：{str(e)}")

    def reload_config_from_file(self):
        """从文件重新加载配置"""
        if self.config_modified:
            result = messagebox.askyesnocancel(
                "重新加载配置",
                "检测到未保存的配置更改，是否保存后重新加载？\n\n是：保存更改并重新加载\n否：放弃更改并重新加载\n取消：取消操作"
            )
            if result is None:  # 用户点击取消
                return
            elif result:  # 用户点击是 - 保存后重新加载
                self.save_gui_to_config()

        # 重新加载配置
        self.load_config_to_gui()
        messagebox.showinfo("配置已重新加载", "配置文件已成功重新加载到界面！")

    def save_gui_to_config(self):
        """将GUI界面的参数保存到配置文件"""
        try:
            # 读取现有配置
            if not os.path.exists(self.config_file):
                messagebox.showerror("配置文件错误", "配置文件不存在！")
                return False

            # 创建备份
            backup_file = self.config_file + '.backup'
            if os.path.exists(self.config_file):
                shutil.copy2(self.config_file, backup_file)

            self.config.read(self.config_file, encoding='utf-8')

            # 确保搜狗微信搜索部分存在
            if '搜狗微信搜索' not in self.config:
                self.config.add_section('搜狗微信搜索')

            # 保存GUI输入框的值
            keyword = self.keyword_entry.get().strip()
            pages = self.pages_entry.get().strip()

            self.config.set('搜狗微信搜索', '默认搜索关键词', keyword)
            self.config.set('搜狗微信搜索', '默认翻页页数', pages)

            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)

            # 重置修改标志
            self.config_modified = False
            self._update_config_status()

            messagebox.showinfo("配置已保存", f"配置已成功保存到 {self.config_file}")
            return True

        except Exception as e:
            messagebox.showerror("配置保存错误", f"保存配置文件失败：{str(e)}")
            # 尝试恢复备份
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, self.config_file)
            return False

    def _update_config_status(self):
        """更新配置状态指示器"""
        if self.config_modified:
            self.config_status_dot.config(fg=self.COLORS["warning"])  # 黄色表示已修改
        else:
            self.config_status_dot.config(fg=self.COLORS["success"])  # 绿色表示已同步

    def on_config_modified(self, event=None):
        """配置被修改时的回调"""
        self.config_modified = True
        self._update_config_status()

    def on_closing(self):
        """窗口关闭事件"""
        # 检查是否有未保存的配置更改
        if self.config_modified:
            result = messagebox.askyesnocancel(
                "退出确认",
                "检测到未保存的配置更改，是否保存后退出？\n\n是：保存更改并退出\n否：放弃更改并退出\n取消：取消退出"
            )
            if result is None:  # 用户点击取消
                return
            elif result:  # 用户点击是 - 保存后退出
                if not self.save_gui_to_config():
                    return  # 保存失败，不退出

        # 检查任务是否在运行
        if self.running:
            if messagebox.askyesno("确认退出", "任务正在运行，确定退出吗？"):
                self.running = False
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = ZBBrainArticleGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
