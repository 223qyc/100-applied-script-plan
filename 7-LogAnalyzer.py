import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import os

# 尝试导入 tkinterdnd2 以实现拖放功能
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES

    DND_SUPPORT = True
except ImportError:
    DND_SUPPORT = False
    print("警告: tkinterdnd2 未安装，拖放功能不可用")


class SimpleLogAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("macOS 日志分析工具")
        self.root.geometry("900x600")

        # 初始化变量
        self.log_file_path = ""
        self.log_data = []
        self.error_lines = []
        self.error_stats = defaultdict(int)
        self.error_keywords = ["error", "exception", "fail", "critical", "warning"]

        # 创建UI
        self.create_widgets()

        # 如果支持拖放，设置拖放功能
        if DND_SUPPORT:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def create_widgets(self):
        # 顶部框架 - 文件选择和配置
        top_frame = ttk.LabelFrame(self.root, text="日志配置", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # 文件选择区域
        file_frame = ttk.Frame(top_frame)
        file_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file_frame, text="日志文件:").pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(file_frame, width=60)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="浏览...", command=self.browse_file).pack(side=tk.LEFT)

        # 拖拽提示（仅在支持拖放时显示）
        if DND_SUPPORT:
            ttk.Label(top_frame, text="或直接拖拽日志文件到窗口", foreground="gray").pack()
        else:
            ttk.Label(top_frame, text="安装 tkinterdnd2 以获得拖放功能 (pip install tkinterdnd2)",
                      foreground="gray").pack()

        # 分析配置区域
        config_frame = ttk.Frame(top_frame)
        config_frame.pack(fill=tk.X, pady=5)

        # 错误关键词配置
        ttk.Label(config_frame, text="错误关键词(逗号分隔):").pack(side=tk.LEFT)
        self.keywords_entry = ttk.Entry(config_frame, width=40)
        self.keywords_entry.pack(side=tk.LEFT, padx=5)
        self.keywords_entry.insert(0, ", ".join(self.error_keywords))

        # 分析按钮
        ttk.Button(top_frame, text="分析日志", command=self.analyze_log).pack(pady=5)

        # 中间框架 - 结果显示
        middle_frame = ttk.LabelFrame(self.root, text="分析结果", padding=10)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 错误统计表格
        self.stats_tree = ttk.Treeview(middle_frame, columns=("type", "count"), show="headings")
        self.stats_tree.heading("type", text="错误类型")
        self.stats_tree.heading("count", text="数量")
        self.stats_tree.column("type", width=300)
        self.stats_tree.column("count", width=100)
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 右侧详细信息
        detail_frame = ttk.Frame(middle_frame)
        detail_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        ttk.Label(detail_frame, text="错误详情:").pack()
        self.detail_text = tk.Text(detail_frame, width=50, height=15, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        # 底部框架 - 日志预览
        bottom_frame = ttk.LabelFrame(self.root, text="日志预览", padding=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 日志内容显示
        self.log_text = tk.Text(bottom_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # 绑定事件
        self.stats_tree.bind("<<TreeviewSelect>>", self.show_error_detail)

    def handle_drop(self, event):
        # 处理拖拽文件
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.log_file_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.analyze_log()

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")])
        if file_path:
            self.log_file_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def analyze_log(self):
        if not self.log_file_path:
            messagebox.showerror("错误", "请先选择日志文件")
            return

        # 获取用户定义的关键词
        keywords = self.keywords_entry.get().strip()
        if keywords:
            self.error_keywords = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

        try:
            # 读取日志文件
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                self.log_data = f.readlines()

            # 清空之前的结果
            self.error_lines = []
            self.error_stats = defaultdict(int)
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            self.log_text.delete(1.0, tk.END)
            self.detail_text.delete(1.0, tk.END)

            # 分析日志
            for line in self.log_data:
                # 检查错误关键词
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in self.error_keywords):
                    self.error_lines.append(line)

                    # 确定错误类型
                    error_type = "其他错误"
                    for kw in self.error_keywords:
                        if kw in line_lower:
                            error_type = kw.capitalize() + " 错误"
                            break

                    self.error_stats[error_type] += 1

            # 显示统计结果
            for error_type, count in sorted(self.error_stats.items(), key=lambda x: x[1], reverse=True):
                self.stats_tree.insert("", tk.END, values=(error_type, count))

            # 显示日志预览
            self.log_text.insert(tk.END, "".join(self.log_data[:500]))  # 只显示前500行避免卡顿

            messagebox.showinfo("完成", f"日志分析完成，共找到 {len(self.error_lines)} 条错误信息")

        except Exception as e:
            messagebox.showerror("错误", f"分析日志时出错: {str(e)}")

    def show_error_detail(self, event):
        selected_item = self.stats_tree.selection()
        if not selected_item:
            return

        error_type = self.stats_tree.item(selected_item, "values")[0]
        self.detail_text.delete(1.0, tk.END)

        # 显示该类型的所有错误
        for line in self.error_lines:
            line_lower = line.lower()
            for kw in self.error_keywords:
                if kw in line_lower and error_type.lower().startswith(kw):
                    self.detail_text.insert(tk.END, line)
                    break


if __name__ == "__main__":
    # 根据是否支持拖放功能选择不同的 Tk 类
    if DND_SUPPORT:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = SimpleLogAnalyzer(root)
    root.mainloop()