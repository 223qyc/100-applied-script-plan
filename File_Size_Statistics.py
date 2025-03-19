import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
# 分别是用于打开文件选择对话框，显示消息框，创建带滚动条的文本框

class FileSizeStatisticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件大小统计工具")
        self.directories = []  # 用于存储选择的目录
        self.file_types = [".txt", ".pdf", ".jpg", ".png", ".doc", ".docx", ".html", ".xlsx", ".mp3", ".mp4"]  # 支持的文件类型
        self.selected_file_types = []  # 实际选择的文件类型

        self.create_widgets()  # 创建界面

    def create_widgets(self):
        """用来创建整个界面的组件"""

        # 选择目录，一个Frame容器可以用来放置一些相关组件
        directory_frame = tk.Frame(self.root)
        directory_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(directory_frame, text="选择目录:").pack(side=tk.LEFT, padx=5)
        self.directory_entry = tk.Entry(directory_frame, width=50)
        self.directory_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(directory_frame, text="浏览", command=self.browse_directory).pack(side=tk.LEFT, padx=5)

        # 文件类型的过滤
        file_type_frame = tk.Frame(self.root)
        file_type_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Label(file_type_frame, text="文件类型:").pack(side=tk.LEFT, padx=5)
        for file_type in self.file_types:
            var = tk.BooleanVar()  # 创建布尔变量追踪复选框的状态
            tk.Checkbutton(file_type_frame, text=file_type, variable=var, onvalue=True, offvalue=False).pack(
                side=tk.LEFT, padx=2)
            self.selected_file_types.append((file_type, var))    # 将文件类型和对应的布尔变量作为一个元组添加到列表中

        # 计算大小的按钮
        tk.Button(self.root, text="计算大小", command=self.calculate_size).pack(pady=10)

        # 用于结果显示
        self.result_text = scrolledtext.ScrolledText(self.root, width=80, height=20, state=tk.DISABLED)
        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 保存结果按钮
        tk.Button(self.root, text="保存结果", command=self.save_results).pack(pady=10)

    def browse_directory(self):
        """用于打开目录选择对话框"""
        directory = filedialog.askdirectory()
        if directory:
            self.directories.append(directory)
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, ", ".join(self.directories))

    def calculate_size(self):
        """计算目录大小并显示结果"""
        if not self.directories:
            messagebox.showerror("错误", "请选择一个目录")
            return

        # 获取用户选择的文件类型
        selected_types = [file_type for file_type, var in self.selected_file_types if var.get()]

        # 清空结果显示区域
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        total_size = 0
        total_files = 0

        for directory in self.directories:
            self.result_text.insert(tk.END, f"目录: {directory}\n")
            dir_total_size = 0
            dir_file_count = 0

            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    file_extension = os.path.splitext(filename)[1].lower()

                    # 如果选择了文件类型，则只统计符合条件的文件
                    if selected_types and file_extension not in selected_types:
                        continue

                    file_size = os.path.getsize(file_path)
                    dir_total_size += file_size
                    dir_file_count += 1
                    self.result_text.insert(tk.END, f"{filename}: {file_size / 1024:.2f} KB\n")

            total_size += dir_total_size
            total_files += dir_file_count
            self.result_text.insert(tk.END, f"\n文件数量: {dir_file_count}\n")
            self.result_text.insert(tk.END, f"目录大小: {dir_total_size / 1024 / 1024:.2f} MB\n\n")

        self.result_text.insert(tk.END, f"总文件数量: {total_files}\n")
        self.result_text.insert(tk.END, f"总大小: {total_size / 1024 / 1024:.2f} MB\n")
        self.result_text.config(state=tk.DISABLED)

    def save_results(self):
        """将结果保存到文件"""
        if not self.result_text.get(1.0, tk.END).strip():
            messagebox.showerror("错误", "没有可保存的结果")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.result_text.get(1.0, tk.END))
            messagebox.showinfo("成功", f"结果已保存到 {save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileSizeStatisticsApp(root)
    root.mainloop()