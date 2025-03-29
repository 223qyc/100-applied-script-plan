import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os


class ExcelDataExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel 数据提取工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # 初始化变量
        self.file_path = None
        self.df = None
        self.columns = []

        # 创建界面元素
        self.create_widgets()

        # 添加状态栏
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status("准备就绪")

    def create_widgets(self):
        # 使用ttk样式美化界面
        style = ttk.Style()
        style.configure("TFrame", padding=5)
        style.configure("TButton", padding=5)
        style.configure("TLabel", padding=5)

        # 文件选择部分
        self.file_frame = ttk.LabelFrame(self.root, text="1. 选择 Excel 文件", padding=10)
        self.file_frame.pack(fill=tk.X, padx=10, pady=5, expand=False)

        # 文件路径显示和浏览按钮
        self.file_label = ttk.Label(self.file_frame, text="未选择文件", width=50)
        self.file_label.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.browse_button = ttk.Button(self.file_frame, text="浏览...", command=self.browse_file)
        self.browse_button.pack(side=tk.RIGHT, padx=5)

        # 列选择部分
        self.column_frame = ttk.LabelFrame(self.root, text="2. 选择要提取的列 (可多选)", padding=10)
        self.column_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.column_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.column_listbox = tk.Listbox(
            self.column_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            bg='white',
            relief=tk.FLAT,
            highlightthickness=1
        )
        self.column_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.column_listbox.yview)

        # 添加全选/取消全选按钮
        self.select_buttons_frame = ttk.Frame(self.column_frame)
        self.select_buttons_frame.pack(fill=tk.X, pady=(0, 5))

        self.select_all_button = ttk.Button(
            self.select_buttons_frame,
            text="全选",
            command=lambda: self.toggle_select_all(True),
            width=10
        )
        self.select_all_button.pack(side=tk.LEFT, padx=5)

        self.deselect_all_button = ttk.Button(
            self.select_buttons_frame,
            text="取消全选",
            command=lambda: self.toggle_select_all(False),
            width=10
        )
        self.deselect_all_button.pack(side=tk.LEFT, padx=5)

        # 保存部分
        self.save_frame = ttk.LabelFrame(self.root, text="3. 保存提取的数据", padding=10)
        self.save_frame.pack(fill=tk.X, padx=10, pady=5, expand=False)

        self.save_button = ttk.Button(
            self.save_frame,
            text="保存为 Excel 文件...",
            command=self.save_data,
            state=tk.DISABLED
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)

        # 进度条
        self.progress = ttk.Progressbar(
            self.save_frame,
            orient=tk.HORIZONTAL,
            length=200,
            mode='determinate'
        )
        self.progress.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def toggle_select_all(self, select):
        if not self.columns:
            return

        self.column_listbox.selection_clear(0, tk.END)
        if select:
            for i in range(len(self.columns)):
                self.column_listbox.selection_set(i)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Excel 文件", "*.xlsx *.xls"),
                ("CSV 文件", "*.csv"),
                ("所有文件", "*.*")
            ],
            title="选择Excel文件"
        )

        if file_path:
            self.file_path = file_path
            self.file_label.config(text=self.file_path)
            self.load_excel_file()

    def load_excel_file(self):
        if not self.file_path:
            return

        self.update_status("正在加载文件...")
        self.root.update_idletasks()

        try:
            # 根据文件扩展名选择读取方式
            if self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith('.xlsx'):
                self.df = pd.read_excel(self.file_path, engine='openpyxl')
            elif self.file_path.endswith('.xls'):
                try:
                    self.df = pd.read_excel(self.file_path, engine='xlrd')
                except ImportError:
                    messagebox.showerror(
                        "缺少依赖",
                        "读取.xls文件需要xlrd库，请执行: pip install xlrd",
                        parent=self.root
                    )
                    return
            else:
                messagebox.showerror(
                    "不支持的格式",
                    "只支持.csv, .xlsx和.xls文件",
                    parent=self.root
                )
                return

            self.columns = self.df.columns.tolist()
            self.update_column_listbox()
            self.save_button.config(state=tk.NORMAL)
            self.update_status(f"成功加载文件: {len(self.columns)}列, {len(self.df)}行数据")

        except Exception as e:
            error_msg = f"无法读取文件: {str(e)}"
            self.update_status(error_msg, is_error=True)
            messagebox.showerror(
                "文件读取错误",
                f"读取文件时出错:\n\n{error_msg}\n\n请确认文件格式正确且未被其他程序占用。",
                parent=self.root
            )
            self.reset_ui()

    def reset_ui(self):
        self.file_label.config(text="未选择文件")
        self.file_path = None
        self.df = None
        self.columns = []
        self.update_column_listbox()
        self.save_button.config(state=tk.DISABLED)

    def update_column_listbox(self):
        self.column_listbox.delete(0, tk.END)

        if not self.columns:
            self.column_listbox.insert(tk.END, "没有可用的列")
            self.column_listbox.config(state=tk.DISABLED)
            self.select_all_button.config(state=tk.DISABLED)
            self.deselect_all_button.config(state=tk.DISABLED)
        else:
            self.column_listbox.config(state=tk.NORMAL)
            self.select_all_button.config(state=tk.NORMAL)
            self.deselect_all_button.config(state=tk.NORMAL)

            for i, column in enumerate(self.columns):
                dtype = str(self.df[column].dtype)
                display_text = f"{column} ({dtype})"
                self.column_listbox.insert(tk.END, display_text)

    def save_data(self):
        if not self.file_path or self.df is None:
            messagebox.showwarning("警告", "请先选择有效的Excel文件", parent=self.root)
            return

        selected_columns = self.column_listbox.curselection()
        if not selected_columns:
            messagebox.showwarning("警告", "请选择至少一列", parent=self.root)
            return

        columns_to_extract = [self.columns[i] for i in selected_columns]

        try:
            extracted_df = self.df[columns_to_extract]
        except Exception as e:
            messagebox.showerror("错误", f"提取数据时出错: {e}", parent=self.root)
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel 文件", "*.xlsx"),
                ("CSV 文件", "*.csv"),
                ("所有文件", "*.*")
            ],
            title="保存提取的数据"
        )

        if not save_path:
            self.update_status("取消保存操作")
            return

        self.update_status("正在保存文件...")
        self.progress["value"] = 0
        self.root.update_idletasks()

        try:
            for i in range(5):
                self.progress["value"] = i * 20
                self.root.update_idletasks()
                self.root.after(100)

            if save_path.endswith('.csv'):
                extracted_df.to_csv(save_path, index=False, encoding='utf-8-sig')
            elif save_path.endswith('.xlsx'):
                extracted_df.to_excel(save_path, index=False, engine='openpyxl')
            elif save_path.endswith('.xls'):
                extracted_df.to_excel(save_path, index=False, engine='xlrd')
            else:
                extracted_df.to_excel(save_path, index=False)

            self.progress["value"] = 100
            self.update_status(f"数据已成功保存到: {save_path}")
            messagebox.showinfo(
                "保存成功",
                f"已成功保存 {len(extracted_df.columns)}列, {len(extracted_df)}行数据到:\n\n{save_path}",
                parent=self.root
            )

        except Exception as e:
            self.progress["value"] = 0
            error_msg = f"保存文件时出错: {str(e)}"
            self.update_status(error_msg, is_error=True)
            messagebox.showerror(
                "保存错误",
                f"无法保存文件:\n\n{error_msg}\n\n请确认有写入权限且文件未被其他程序占用。",
                parent=self.root
            )

    def update_status(self, message, is_error=False):
        self.status_var.set(message)
        if is_error:
            self.status_bar.config(fg='red')
        else:
            self.status_bar.config(fg='black')


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    app = ExcelDataExtractor(root)
    root.mainloop()