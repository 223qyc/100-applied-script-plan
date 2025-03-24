import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
import re
import json

class TextSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("一个文本文件搜索工具")
        self.root.geometry("1000x800")

        # 初始化变量
        self.file_path = tk.StringVar()
        self.search_keyword = tk.StringVar()
        self.case_sensitive = tk.BooleanVar()
        self.use_regex = tk.BooleanVar()
        self.whole_word = tk.BooleanVar()
        self.current_page = 1
        self.matches = []

        # 创建界面
        self.create_widgets()

    

    def create_widgets(self):
        # 文件选择区域
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, fill=tk.X)

        tk.Label(file_frame, text="文件路径：").pack(side=tk.LEFT, padx=5)
        self.entry_file = tk.Entry(file_frame, textvariable=self.file_path, width=70)
        self.entry_file.pack(side=tk.LEFT, padx=5)
        self.entry_file.drop_target_register(DND_FILES)
        self.entry_file.dnd_bind('<<Drop>>', self.on_file_drop)

        tk.Button(file_frame, text="选择文件", command=self.open_file_dialog).pack(side=tk.LEFT, padx=5)

        # 搜索关键词输入
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, fill=tk.X)

        tk.Label(search_frame, text="搜索关键词：").pack(side=tk.LEFT, padx=5)
        self.entry_keyword = tk.Entry(search_frame, textvariable=self.search_keyword, width=70)
        self.entry_keyword.pack(side=tk.LEFT, padx=5)

        # 搜索选项
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=10, fill=tk.X)

        tk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(options_frame, text="使用正则表达式", variable=self.use_regex).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(options_frame, text="全词匹配", variable=self.whole_word).pack(side=tk.LEFT, padx=5)

        # 搜索按钮
        tk.Button(self.root, text="搜索", command=self.perform_search).pack(pady=10)

        # 文件内容预览
        tk.Label(self.root, text="文件内容预览：").pack(pady=5)
        self.preview_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=10, width=100)
        self.preview_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 搜索结果区域
        tk.Label(self.root, text="搜索结果：").pack(pady=5)
        self.result_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, width=100)
        self.result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 分页控制
        page_frame = tk.Frame(self.root)
        page_frame.pack(pady=10)

        self.prev_button = tk.Button(page_frame, text="上一页", command=self.prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = tk.Button(page_frame, text="下一页", command=self.next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # 清空按钮
        tk.Button(self.root, text="清空结果", command=self.clear_results).pack(pady=10)
    
    def on_file_drop(self, event):
        """用于处理文件的拖拽的事件"""
        self.file_path.set(event.data.strip('{}'))  # 去除拖拽路径中的多余字符
        self.load_file_preview()
    
    def open_file_dialog(self):
        """用于打开文件的选择框进行选择"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json"), ("Markdown Files", "*.md")]
        )

        if file_path:
            self.file_path.set(file_path)
            self.load_file_preview()


    def load_file_preview(self):
        """用于加载文件预览部分"""
        file_path=self.file_path.get()
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content= file.read()
            
            if file_path.endswith(".json"):
                try:
                    content = json.dumps(json.loads(content), indent=2)
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "文件不是有效的 JSON 格式！")
                    return
                
            elif file_path.endswith(".md"):
                try:
                    content = self.format_markdown(content)  # 格式化 Markdown
                except Exception as e:
                    messagebox.showerror("错误", f"格式化 Markdown 时发生了错误：{e}")
                    return
                
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, content)

        except FileNotFoundError:
            messagebox.showerror("错误", f"文件 '{file_path}' 没有找到")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件时发生了错误：{e}")        
    

    def format_markdown(self, content):
        return content
    
    def perform_search(self):
        """执行搜索操作"""
        self.result_text.delete(1.0, tk.END)  # 清空之前的结果
        self.matches = []
        self.current_page = 1


        file_path = self.file_path.get()
        keyword = self.search_keyword.get()
        case_sensitive = self.case_sensitive.get()
        use_regex = self.use_regex.get()
        whole_word = self.whole_word.get()

        if not file_path or not keyword:
            messagebox.showwarning("警告", "文件路径和关键词不能为空！")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if file_path.endswith(".json"):
                try:
                    content = json.dumps(json.loads(content), indent=2)
                except json.JSONDecodeError:
                    messagebox.showerror("错误", "文件不是有效的 JSON 格式！")
                    return
                
            elif file_path.endswith(".md"):
                try:
                    content = self.format_markdown(content)  # 格式化 Markdown
                except Exception as e:
                    messagebox.showerror("错误", f"格式化 Markdown 时发生了错误：{e}")
                    return

            flags = 0 if case_sensitive else re.IGNORECASE

            if use_regex:
                try:
                    pattern = re.compile(keyword, flags)
                except re.error:
                    messagebox.showerror("错误", "无效的正则表达式！")
                    return
            else:
                if whole_word:
                    keyword = r'\b' + re.escape(keyword) + r'\b'
                pattern = re.compile(keyword, flags)

            # 搜索并记录匹配结果
            for line_number, line in enumerate(content.splitlines(), 1):
                if pattern.search(line):
                    self.matches.append((line_number, line))


            if self.matches:
                self.update_results()
            else:
                self.result_text.insert(tk.END, "未找到匹配的关键词。")
        except FileNotFoundError:
            messagebox.showerror("错误", f"文件 '{file_path}' 未找到！")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误：{e}")

        
    
    def update_results(self):
        """更新搜索结果显示"""
        self.result_text.delete(1.0, tk.END)
        start = (self.current_page - 1) * 10
        end = start + 10
        for line_number, line in self.matches[start:end]:
            self.result_text.insert(tk.END, f"行 {line_number}: {line}\n")

        # 更新分页按钮状态
        self.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if end < len(self.matches) else tk.DISABLED)



    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_results()

    
    def next_page(self):
        """下一页"""
        if self.current_page * 10 < len(self.matches):
            self.current_page += 1
            self.update_results()
        
    
    def clear_results(self):
        """清空搜索结果"""
        self.result_text.delete(1.0, tk.END)
        self.matches = []
        self.current_page = 1
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
    

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = TextSearchApp(root)
    root.mainloop()