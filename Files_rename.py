import os
import tkinter as tk
from tkinter import filedialog,messagebox

def rename_files(folder_path,prefix,start_number):
    try:
        files=os.listdir(folder_path)
        files.sort()
        for i,filename in enumerate(files):# 重要函数，将列表配置索引
            file_path=os.path.join(folder_path,filename)
            if os.path.isfile(file_path):
                file_extension=os.path.splitext(file_path)[1]# 获取文件的拓展名
                new_name=f"{prefix}_{start_number+i}_{file_extension}"
                new_path=os.path.join(folder_path,new_name)
                os.rename(file_path,new_path)
        messagebox.showinfo("成功","文件重命名完成！")  # messagebox展示消息
    except Exception as e:
        messagebox.showerror("错误",f"发生了错误：{e}")


def rename_folder(folder_path,new_name):
    try:
        parent_folder=os.path.dirname(folder_path)
        new_floader_path=os.path.join(parent_folder,new_name)
        os.rename(folder_path,new_floader_path)
        messagebox.showinfo("成功","文件重命名完成！")
        return new_floader_path
    except Exception as e:
        messagebox.showerror("错误",f"发生了错误{e}")
        return folder_path



def select_folder():
    folder_path = filedialog.askdirectory()    # 打开文件夹提供选择
    if folder_path:
        folder_entry.delete(0,tk.END)  # 清空文件夹路径输入框
        folder_entry.insert(0,folder_path)# 将选择的文件夹路径插入到输入框中

def start_rename():
    folder_path = folder_entry.get()
    prefix = prefix_entry.get()
    start_number = int(start_number_entry.get())
    new_folder_name = folder_name_entry.get()

    if not folder_path:
        messagebox.showwarning("警告","请选择一个文件夹")
        return

    if new_folder_name:
        folder_path = rename_folder(folder_path, new_folder_name)
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)  # 更新文件夹路径显示


    if prefix:
        rename_files(folder_path,prefix,start_number)
    else:
        messagebox.showwarning("警告","请输入文件名前缀")

# 创建Tkinter主窗口
root = tk.Tk()
root.title("文件批量重命名工具")

# 创建一个标签，显示“文件夹路径：”
tk.Label(root, text="文件夹路径:").grid(row=0, column=0, padx=5, pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="选择文件夹", command=select_folder).grid(row=0, column=2, padx=5, pady=5)

# 创建一个标签，显示“新文件夹名称：”
tk.Label(root, text="新文件夹名称:").grid(row=1, column=0, padx=5, pady=5)
folder_name_entry = tk.Entry(root, width=50)
folder_name_entry.grid(row=1, column=1, padx=5, pady=5)

# 创建一个标签，显示“文件名前缀：”
tk.Label(root, text="文件名前缀:").grid(row=2, column=0, padx=5, pady=5)
prefix_entry = tk.Entry(root, width=50)
prefix_entry.grid(row=2, column=1, padx=5, pady=5)

# 创建一个标签，显示“起始编号：”
tk.Label(root, text="起始编号:").grid(row=3, column=0, padx=5, pady=5)
start_number_entry = tk.Entry(root, width=50)
start_number_entry.grid(row=3, column=1, padx=5, pady=5)
start_number_entry.insert(0, "1")

tk.Button(root, text="开始重命名", command=start_rename).grid(row=4, column=1, padx=5, pady=20)

# 进入Tkinter主循环，显示窗口
root.mainloop()

