import os
import shutil
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import time
import threading
from collections import deque
import json


# 定义备份应用程序类
class BackupApp:
    # 初始化方法
    def __init__(self, root):
        """
        初始化BackupApp类的实例。

        :param root: Tkinter根窗口对象。
        """
        self.root = root
        self.root.title("文件夹备份工具")  # 设置窗口标题
        self.root.geometry("800x600")  # 设置窗口初始大小
        self.root.minsize(700, 500)  # 设置窗口最小大小

        # 初始化设置
        self.settings = {
            'auto_clean': False,  # 是否自动清理旧备份
            'clean_days': 30,  # 自动清理的天数
            'default_save_path': os.path.expanduser('~'),  # 默认备份保存路径
            'exclude_extensions': ['.tmp', '.log', '.cache']  # 默认排除的文件扩展名
        }

        # 备份历史记录
        self.backup_history = deque(maxlen=50)  # 使用双端队列存储备份历史记录，最大长度为50

        # 当前备份任务
        self.current_backup_thread = None  # 当前备份线程
        self.backup_running = False  # 标记是否正在执行备份任务

        # 创建界面
        self.create_widgets()

        # 加载数据
        self.load_backup_history()  # 加载备份历史记录
        self.load_settings()  # 加载设置

    # 创建界面组件
    def create_widgets(self):
        """
        创建应用程序的界面组件。
        """
        # 主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 备份选项卡
        self.backup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.backup_tab, text="备份")
        self.setup_backup_tab()

        # 历史记录选项卡
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="历史记录")
        self.setup_history_tab()

        # 设置选项卡
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="设置")
        self.setup_settings_tab()

    # 设置备份选项卡
    def setup_backup_tab(self):
        """
        设置备份选项卡的界面组件。
        """
        # 源文件夹选择
        source_frame = ttk.LabelFrame(self.backup_tab, text="源文件夹", padding=10)
        source_frame.pack(fill=tk.X, padx=5, pady=5)

        self.source_var = tk.StringVar()
        ttk.Label(source_frame, text="选择要备份的文件夹:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(source_frame, textvariable=self.source_var, width=50).grid(row=1, column=0, padx=(0, 5))
        ttk.Button(source_frame, text="浏览...", command=self.browse_source).grid(row=1, column=1)

        # 目标位置选择
        dest_frame = ttk.LabelFrame(self.backup_tab, text="备份位置", padding=10)
        dest_frame.pack(fill=tk.X, padx=5, pady=5)

        self.dest_var = tk.StringVar()
        ttk.Label(dest_frame, text="选择备份保存位置:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(dest_frame, textvariable=self.dest_var, width=50).grid(row=1, column=0, padx=(0, 5))
        ttk.Button(dest_frame, text="浏览...", command=self.browse_dest).grid(row=1, column=1)

        # 备份选项
        options_frame = ttk.LabelFrame(self.backup_tab, text="备份选项", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # 压缩选项
        self.compress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="压缩备份 (ZIP格式)", variable=self.compress_var).grid(row=0, column=0,
                                                                                                   sticky=tk.W)

        # 排除选项
        ttk.Label(options_frame, text="排除文件扩展名 (逗号分隔):").grid(row=1, column=0, sticky=tk.W)
        self.exclude_var = tk.StringVar(value=".tmp, .log, .cache")
        ttk.Entry(options_frame, textvariable=self.exclude_var, width=50).grid(row=1, column=1)

        # 计划选项
        schedule_frame = ttk.LabelFrame(self.backup_tab, text="备份计划", padding=10)
        schedule_frame.pack(fill=tk.X, padx=5, pady=5)

        self.schedule_var = tk.StringVar(value="now")
        ttk.Radiobutton(schedule_frame, text="立即执行", variable=self.schedule_var, value="now").grid(row=0, column=0,
                                                                                                       sticky=tk.W)
        ttk.Radiobutton(schedule_frame, text="每日", variable=self.schedule_var, value="daily").grid(row=0, column=1,
                                                                                                     sticky=tk.W)
        ttk.Radiobutton(schedule_frame, text="每周", variable=self.schedule_var, value="weekly").grid(row=0, column=2,
                                                                                                      sticky=tk.W)

        # 时间选择
        self.time_frame = ttk.Frame(schedule_frame)
        self.time_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        ttk.Label(self.time_frame, text="时间:").pack(side=tk.LEFT)
        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        ttk.Spinbox(self.time_frame, from_=0, to=23, textvariable=self.hour_var, width=3).pack(side=tk.LEFT)
        ttk.Label(self.time_frame, text=":").pack(side=tk.LEFT)
        ttk.Spinbox(self.time_frame, from_=0, to=59, textvariable=self.minute_var, width=3).pack(side=tk.LEFT)

        # 每周选择
        self.weekly_frame = ttk.Frame(schedule_frame)
        ttk.Label(self.weekly_frame, text="每周:").pack(side=tk.LEFT)
        self.day_var = tk.StringVar(value="Monday")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ttk.OptionMenu(self.weekly_frame, self.day_var, "Monday", *days).pack(side=tk.LEFT)

        # 更新UI显示
        self.schedule_var.trace_add('write', self.update_schedule_ui)
        self.update_schedule_ui()

        # 备份按钮
        button_frame = ttk.Frame(self.backup_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        ttk.Button(button_frame, text="开始备份", command=self.start_backup).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_backup).pack(side=tk.RIGHT)

        # 日志区域
        log_frame = ttk.LabelFrame(self.backup_tab, text="备份日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    # 设置历史记录选项卡
    def setup_history_tab(self):
        """
        设置历史记录选项卡的界面组件。
        """
        # 历史记录列表
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 树状视图
        columns = ("id", "date", "source", "destination", "status", "size")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", selectmode="browse")

        # 设置列
        for col in columns:
            self.history_tree.heading(col, text=col.capitalize())

        # 设置列宽
        self.history_tree.column("id", width=40, anchor=tk.CENTER)
        self.history_tree.column("date", width=120)
        self.history_tree.column("source", width=150)
        self.history_tree.column("destination", width=150)
        self.history_tree.column("status", width=80, anchor=tk.CENTER)
        self.history_tree.column("size", width=80, anchor=tk.CENTER)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        # 按钮框架
        button_frame = ttk.Frame(self.history_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="查看详情", command=self.show_history_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="恢复备份", command=self.restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除记录", command=self.delete_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除历史", command=self.clear_history).pack(side=tk.RIGHT, padx=5)

    # 设置设置选项卡
    def setup_settings_tab(self):
        """
        设置设置选项卡的界面组件。
        """
        # 常规设置
        general_frame = ttk.LabelFrame(self.settings_tab, text="常规设置", padding=10)
        general_frame.pack(fill=tk.X, padx=5, pady=5)

        # 自动清理
        self.auto_clean_var = tk.BooleanVar(value=self.settings['auto_clean'])
        ttk.Checkbutton(general_frame, text="自动清理旧备份", variable=self.auto_clean_var).grid(row=0, column=0,
                                                                                                 sticky=tk.W)

        # 清理天数
        ttk.Label(general_frame, text="清理超过多少天的备份:").grid(row=1, column=0, sticky=tk.W)
        self.clean_days_var = tk.StringVar(value=str(self.settings['clean_days']))
        ttk.Spinbox(general_frame, from_=1, to=365, textvariable=self.clean_days_var, width=5).grid(row=1, column=1,
                                                                                                    sticky=tk.W)

        # 默认保存路径
        ttk.Label(general_frame, text="默认备份保存路径:").grid(row=2, column=0, sticky=tk.W)
        self.default_path_var = tk.StringVar(value=self.settings['default_save_path'])
        ttk.Entry(general_frame, textvariable=self.default_path_var, width=40).grid(row=2, column=1, sticky=tk.W)
        ttk.Button(general_frame, text="浏览...", command=self.browse_default_path).grid(row=2, column=2)

        # 排除设置
        exclude_frame = ttk.LabelFrame(self.settings_tab, text="排除设置", padding=10)
        exclude_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(exclude_frame, text="默认排除的文件扩展名 (每行一个):").grid(row=0, column=0, sticky=tk.W)
        self.exclude_list = tk.Text(exclude_frame, width=30, height=5)
        self.exclude_list.grid(row=1, column=0, sticky=tk.W)

        # 加载排除列表
        for ext in self.settings['exclude_extensions']:
            self.exclude_list.insert(tk.END, ext + "\n")

        # 保存按钮
        button_frame = ttk.Frame(self.settings_tab)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="保存设置", command=self.save_settings).pack(side=tk.RIGHT)

    # 浏览源文件夹
    def browse_source(self):
        """
        打开文件夹选择对话框，选择源文件夹。
        """
        folder = filedialog.askdirectory(initialdir=self.source_var.get() or os.path.expanduser('~'))
        if folder:
            self.source_var.set(folder)

    # 浏览目标位置
    def browse_dest(self):
        """
        打开文件夹选择对话框，选择备份目标位置。
        """
        folder = filedialog.askdirectory(initialdir=self.dest_var.get() or self.settings['default_save_path'])
        if folder:
            self.dest_var.set(folder)

    # 浏览默认保存路径
    def browse_default_path(self):
        """
        打开文件夹选择对话框，选择默认备份保存路径。
        """
        folder = filedialog.askdirectory(initialdir=self.default_path_var.get())
        if folder:
            self.default_path_var.set(folder)

    # 更新计划选项UI
    def update_schedule_ui(self, *args):
        """
        根据选择的计划选项更新UI显示。
        """
        schedule = self.schedule_var.get()
        self.time_frame.grid_remove()
        self.weekly_frame.grid_remove()

        if schedule == "daily":
            self.time_frame.grid()
        elif schedule == "weekly":
            self.time_frame.grid()
            self.weekly_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

    # 开始备份
    def start_backup(self):
        """
        开始备份操作。
        """
        source = self.source_var.get()
        dest = self.dest_var.get()

        if not source or not os.path.isdir(source):
            messagebox.showerror("错误", "请选择有效的源文件夹")
            return

        if not dest:
            messagebox.showerror("错误", "请选择备份目标位置")
            return

        compress = self.compress_var.get()
        schedule = self.schedule_var.get()
        exclude_exts = [ext.strip() for ext in self.exclude_var.get().split(",")]

        if schedule == "now":
            self.log_text.insert(tk.END, f"开始备份: {source} 到 {dest}\n")
            self.log_text.see(tk.END)

            self.backup_running = True
            self.current_backup_thread = threading.Thread(
                target=self.run_backup,
                args=(source, dest, compress, exclude_exts),
                daemon=True
            )
            self.current_backup_thread.start()
        else:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            if schedule == "weekly":
                day = self.day_var.get()
                self.log_text.insert(tk.END, f"已计划每周{day} {hour:02d}:{minute:02d} 执行备份\n")
            else:
                self.log_text.insert(tk.END, f"已计划每天 {hour:02d}:{minute:02d} 执行备份\n")
            self.log_text.see(tk.END)

    # 执行备份操作
    def run_backup(self, source, dest, compress, exclude_exts):
        """
        执行备份操作。

        :param source: 源文件夹路径
        :param dest: 备份目标位置
        :param compress: 是否压缩备份
        :param exclude_exts: 排除的文件扩展名列表
        """
        try:
            start_time = time.time()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{os.path.basename(source)}_{timestamp}"
            backup_path = os.path.join(dest, backup_name)

            self.add_log(f"备份开始: {backup_name}")

            if not os.path.exists(dest):
                os.makedirs(dest)

            if compress:
                backup_path += ".zip"
                self.add_log("创建ZIP压缩备份...")
                self.create_zip_backup(source, backup_path, exclude_exts)
            else:
                os.makedirs(backup_path)
                self.add_log("创建文件夹备份...")
                self.copy_folder(source, backup_path, exclude_exts)

            backup_size = self.get_folder_size(backup_path) if not compress else os.path.getsize(backup_path)
            size_str = self.format_size(backup_size)

            elapsed = time.time() - start_time
            self.add_log(f"备份完成! 用时: {elapsed:.2f}秒, 大小: {size_str}")

            backup_record = {
                'id': len(self.backup_history) + 1,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': source,
                'destination': backup_path,
                'status': "成功",
                'size': size_str,
                'elapsed': f"{elapsed:.2f}秒",
                'compress': "是" if compress else "否",
                'exclude': ", ".join(exclude_exts)
            }

            self.backup_history.append(backup_record)
            self.update_history_tree()
            self.save_backup_history()

        except Exception as e:
            self.add_log(f"备份失败: {str(e)}")
        finally:
            self.backup_running = False

    # 创建ZIP压缩备份
    def create_zip_backup(self, source, zip_path, exclude_exts):
        """
        创建ZIP压缩备份。

        :param source: 源文件夹路径
        :param zip_path: ZIP文件路径
        :param exclude_exts: 排除的文件扩展名列表
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, source)

                    _, ext = os.path.splitext(file)
                    if ext.lower() in exclude_exts:
                        self.add_log(f"排除: {rel_path}")
                        continue

                    zipf.write(file_path, rel_path)
                    self.add_log(f"添加: {rel_path}")

                    if not self.backup_running:
                        self.add_log("备份已取消")
                        if os.path.exists(zip_path):
                            os.remove(zip_path)
                        return

    # 复制文件夹
    def copy_folder(self, source, dest, exclude_exts):
        """
        复制文件夹。

        :param source: 源文件夹路径
        :param dest: 目标文件夹路径
        :param exclude_exts: 排除的文件扩展名列表
        """
        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(dest, item)

            if os.path.isdir(s):
                shutil.copytree(s, d)
                self.add_log(f"复制文件夹: {item}")
            else:
                _, ext = os.path.splitext(item)
                if ext.lower() in exclude_exts:
                    self.add_log(f"排除: {item}")
                    continue

                shutil.copy2(s, d)
                self.add_log(f"复制文件: {item}")

            if not self.backup_running:
                self.add_log("备份已取消")
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                return

    # 获取文件夹大小
    def get_folder_size(self, path):
        """
        获取文件夹大小。

        :param path: 文件夹路径
        :return: 文件夹大小
        """
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total

    # 格式化文件大小
    def format_size(self, size):
        """
        格式化文件大小。

        :param size: 文件大小
        :return: 格式化后的文件大小
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    # 添加日志
    def add_log(self, message):
        """
        添加日志信息。

        :param message: 日志信息
        """
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert(tk.END, timestamp + message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    # 取消备份
    def cancel_backup(self):
        """
        取消正在进行的备份操作。
        """
        if self.backup_running:
            self.backup_running = False
            self.add_log("正在取消备份...")
        else:
            self.add_log("没有正在运行的备份任务")

    # 更新历史记录树
    def update_history_tree(self):
        """
        更新历史记录树。
        """
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        sorted_history = sorted(self.backup_history, key=lambda x: x['date'], reverse=True)

        for record in sorted_history:
            self.history_tree.insert("", tk.END, values=(
                record['id'],
                record['date'],
                record['source'],
                record['destination'],
                record['status'],
                record['size']
            ))

    # 显示历史记录详情
    def show_history_details(self):
        """
        显示选中的历史记录详情。
        """
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一条备份记录")
            return

        item = self.history_tree.item(selected[0])
        record_id = item['values'][0]

        record = None
        for r in self.backup_history:
            if r['id'] == record_id:
                record = r
                break

        if not record:
            messagebox.showerror("错误", "找不到选定的备份记录")
            return

        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"备份详情 - ID: {record_id}")
        detail_win.geometry("500x400")

        text = tk.Text(detail_win, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info = f"""备份详情 - ID: {record['id']}

日期时间: {record['date']}
源文件夹: {record['source']}
目标位置: {record['destination']}
状态: {record['status']}
大小: {record['size']}
用时: {record['elapsed']}
压缩: {record['compress']}
排除的文件: {record['exclude']}
"""
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)

        ttk.Button(detail_win, text="关闭", command=detail_win.destroy).pack(pady=10)

    # 恢复备份
    def restore_backup(self):
        """
        恢复选中的备份。
        """
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一条备份记录")
            return

        item = self.history_tree.item(selected[0])
        record_id = item['values'][0]

        record = None
        for r in self.backup_history:
            if r['id'] == record_id:
                record = r
                break

        if not record:
            messagebox.showerror("错误", "找不到选定的备份记录")
            return

        restore_path = filedialog.askdirectory(
            title="选择恢复位置",
            initialdir=os.path.dirname(record['source']))

        if not restore_path:
            return

        if not messagebox.askyesno("确认", f"确定要将备份恢复到 {restore_path} 吗？"):
            return

        try:
            self.add_log(f"开始恢复备份 {record_id} 到 {restore_path}")

            if record['destination'].endswith('.zip'):
                with zipfile.ZipFile(record['destination'], 'r') as zipf:
                    zipf.extractall(restore_path)
            else:
                if os.path.exists(restore_path):
                    shutil.rmtree(restore_path)
                shutil.copytree(record['destination'], restore_path)

            self.add_log("恢复完成!")
            messagebox.showinfo("成功", "备份恢复完成")
        except Exception as e:
            self.add_log(f"恢复失败: {str(e)}")
            messagebox.showerror("错误", f"恢复失败: {str(e)}")

    # 删除历史记录
    def delete_history(self):
        """
        删除选中的历史记录。
        """
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一条备份记录")
            return

        item = self.history_tree.item(selected[0])
        record_id = item['values'][0]

        if not messagebox.askyesno("确认", "确定要删除此备份记录吗？"):
            return

        for i, record in enumerate(self.backup_history):
            if record['id'] == record_id:
                if record['destination'].endswith('.zip') and os.path.exists(record['destination']):
                    try:
                        os.remove(record['destination'])
                    except Exception as e:
                        messagebox.showwarning("警告", f"无法删除备份文件: {str(e)}")

                del self.backup_history[i]
                break

        self.update_history_tree()
        self.save_backup_history()
        messagebox.showinfo("成功", "备份记录已删除")

    # 清除历史记录
    def clear_history(self):
        """
        清除所有历史记录。
        """
        if not messagebox.askyesno("确认", "确定要清除所有备份历史记录吗？"):
            return

        self.backup_history.clear()
        self.update_history_tree()
        self.save_backup_history()
        messagebox.showinfo("成功", "备份历史已清除")

    # 加载备份历史记录
    def load_backup_history(self):
        """
        加载备份历史记录。
        """
        try:
            if os.path.exists('backup_history.json'):
                with open('backup_history.json', 'r') as f:
                    history = json.load(f)
                    self.backup_history = deque(history, maxlen=50)
        except Exception as e:
            self.add_log(f"加载备份历史失败: {str(e)}")

    # 保存备份历史记录
    def save_backup_history(self):
        """
        保存备份历史记录。
        """
        try:
            with open('backup_history.json', 'w') as f:
                json.dump(list(self.backup_history), f)
        except Exception as e:
            self.add_log(f"保存备份历史失败: {str(e)}")

    # 加载设置
    def load_settings(self):
        """
        加载设置。
        """
        try:
            if os.path.exists('backup_settings.json'):
                with open('backup_settings.json', 'r') as f:
                    self.settings.update(json.load(f))

                self.auto_clean_var.set(self.settings['auto_clean'])
                self.clean_days_var.set(str(self.settings['clean_days']))
                self.default_path_var.set(self.settings['default_save_path'])

                self.exclude_list.delete('1.0', tk.END)
                for ext in self.settings['exclude_extensions']:
                    self.exclude_list.insert(tk.END, ext + "\n")
        except Exception as e:
            self.add_log(f"加载设置失败: {str(e)}")

    # 保存设置
    def save_settings(self):
        """
        保存设置。
        """
        self.settings['auto_clean'] = self.auto_clean_var.get()
        try:
            self.settings['clean_days'] = int(self.clean_days_var.get())
        except ValueError:
            self.settings['clean_days'] = 30

        self.settings['default_save_path'] = self.default_path_var.get()

        exclude_text = self.exclude_list.get("1.0", tk.END)
        self.settings['exclude_extensions'] = [
            ext.strip() for ext in exclude_text.split("\n") if ext.strip()
        ]

        try:
            with open('backup_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=4)

            messagebox.showinfo("成功", "设置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()