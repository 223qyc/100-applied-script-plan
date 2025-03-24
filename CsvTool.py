import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from functools import reduce


class CSV_Merger:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV 文件合并工具 - 增强版")
        self.root.geometry("800x500")

        # 主题美化
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10), padding=5)
        self.style.configure("TLabel", font=("Arial", 11))
        self.style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.files = []
        self.dfs = []

        # 顶部区域
        frame_top = ttk.Frame(root)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        self.label = ttk.Label(frame_top, text="选择要合并的 CSV 文件:")
        self.label.pack(side=tk.LEFT, padx=5)

        self.add_button = ttk.Button(frame_top, text="添加文件", command=self.add_files)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = ttk.Button(frame_top, text="移除选中", command=self.remove_files)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.info_button = ttk.Button(frame_top, text="文件信息", command=self.show_file_info)
        self.info_button.pack(side=tk.LEFT, padx=5)

        # 文件列表区域
        frame_list = ttk.Frame(root)
        frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame_list, columns=("文件名", "大小 (KB)", "行数", "列数"), show="headings")
        self.tree.heading("文件名", text="文件名")
        self.tree.heading("大小 (KB)", text="大小 (KB)")
        self.tree.heading("行数", text="行数")
        self.tree.heading("列数", text="列数")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 选项区域
        frame_options = ttk.Frame(root)
        frame_options.pack(fill=tk.X, padx=10, pady=5)

        self.search_button = ttk.Button(frame_options, text="数据检索", command=self.search_data)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.preview_button = ttk.Button(frame_options, text="预览文件", command=self.preview_file)
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.merge_button = ttk.Button(frame_options, text="合并文件", command=self.merge_files)
        self.merge_button.pack(side=tk.LEFT, padx=5)

        # 合并方式
        frame_merge = ttk.Frame(root)
        frame_merge.pack(fill=tk.X, padx=10, pady=5)

        self.merge_mode = tk.StringVar(value="row")
        ttk.Label(frame_merge, text="合并方式:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_merge, text="按行合并", variable=self.merge_mode, value="row").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_merge, text="按列合并", variable=self.merge_mode, value="col").pack(side=tk.LEFT, padx=5)

        self.fill_na_var = tk.IntVar()
        self.fill_na_check = ttk.Checkbutton(frame_merge, text="填充缺失值", variable=self.fill_na_var)
        self.fill_na_check.pack(side=tk.LEFT, padx=10)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        for file in files:
            if file not in self.files:
                self.files.append(file)
                df = pd.read_csv(file)
                self.dfs.append(df)
                file_size = round(os.path.getsize(file) / 1024, 2)
                self.tree.insert("", tk.END, values=(os.path.basename(file), file_size, len(df), len(df.columns)))

    def remove_files(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            index = self.tree.index(item)
            self.tree.delete(item)
            del self.files[index]
            del self.dfs[index]

    def show_file_info(self):
        if not self.files:
            messagebox.showwarning("警告", "请先添加 CSV 文件！")
            return

        info_window = tk.Toplevel(self.root)
        info_window.title("文件信息")
        info_text = tk.Text(info_window, wrap=tk.NONE, width=80, height=20)
        info_text.pack(padx=10, pady=10)

        for i, file in enumerate(self.files):
            df = self.dfs[i]
            info_text.insert(tk.END, f"文件: {os.path.basename(file)}\n")
            info_text.insert(tk.END, f"大小: {os.path.getsize(file) / 1024:.2f} KB\n")
            info_text.insert(tk.END, f"行数: {len(df)}\n")
            info_text.insert(tk.END, f"列数: {len(df.columns)}\n")
            info_text.insert(tk.END, f"列名: {', '.join(df.columns)}\n")
            info_text.insert(tk.END, "-" * 50 + "\n")

    def search_data(self):
        if not self.files:
            messagebox.showwarning("警告", "请先添加 CSV 文件！")
            return

        search_window = tk.Toplevel(self.root)
        search_window.title("数据检索")
        search_label = ttk.Label(search_window, text="输入检索关键词:")
        search_label.pack(pady=5)

        search_entry = ttk.Entry(search_window, width=50)
        search_entry.pack(pady=5)

        def perform_search():
            keyword = search_entry.get()
            if not keyword:
                messagebox.showwarning("警告", "请输入检索关键词！")
                return

            result = []
            for df in self.dfs:
                matches = df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
                if matches.any():
                    result.append(df[matches])

            if result:
                result_df = pd.concat(result, ignore_index=True)
                messagebox.showinfo("提示", f"找到 {len(result_df)} 条匹配数据。")
            else:
                messagebox.showinfo("提示", "未找到匹配的数据。")

        search_button = ttk.Button(search_window, text="检索", command=perform_search)
        search_button.pack(pady=5)

    def preview_file(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择一个文件进行预览！")
            return

        index = self.tree.index(selected_item[0])
        df = self.dfs[index]
        messagebox.showinfo("文件预览", df.head(10).to_string(index=False))

    def merge_files(self):
        if not self.files:
            messagebox.showwarning("警告", "请先添加 CSV 文件！")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not output_path:
            return

        merged_df = pd.concat(self.dfs, ignore_index=True) if self.merge_mode.get() == "row" else reduce(lambda left, right: pd.merge(left, right, how="outer"), self.dfs)
        if self.fill_na_var.get():
            merged_df = merged_df.fillna("N/A")

        merged_df.to_csv(output_path, index=False)
        messagebox.showinfo("成功", f"合并成功！保存至: {output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSV_Merger(root)
    root.mainloop()
