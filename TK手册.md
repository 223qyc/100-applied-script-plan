## **1. Tkinter 基础**
### **1.1 创建主窗口**
- **`tk.Tk()`**：创建一个主窗口。
  ```python
  import tkinter as tk
  root = tk.Tk()  # 创建主窗口
  root.mainloop()  # 进入主事件循环
  ```

### **1.2 设置窗口标题**
- **`root.title("标题")`**：设置窗口的标题。
  ```python
  root.title("我的应用程序")
  ```

### **1.3 设置窗口大小**
- **`root.geometry("宽度x高度")`**：设置窗口的初始大小。
  ```python
  root.geometry("400x300")  # 宽度400像素，高度300像素
  ```

---

## **2. Frame（框架）**
- **`tk.Frame`**：用于将多个组件分组，方便布局。
  ```python
  frame = tk.Frame(root)  # 创建一个Frame
  frame.pack()  # 将Frame添加到窗口中
  ```

---

## **3. Label（标签）**
- **`tk.Label`**：用于显示文本或图片。
  ```python
  label = tk.Label(root, text="这是一个标签")  # 创建标签
  label.pack()  # 将标签添加到窗口中
  ```

### **3.1 设置标签属性**
- **`label.config(text="新文本")`**：动态修改标签的文本。
  ```python
  label.config(text="更新后的文本")
  ```

---

## **4. Entry（输入框）**
- **`tk.Entry`**：用于接收用户输入的单行文本。
  ```python
  entry = tk.Entry(root, width=30)  # 创建输入框
  entry.pack()
  ```

### **4.1 获取输入框内容**
- **`entry.get()`**：获取输入框中的内容。
  ```python
  content = entry.get()
  ```

### **4.2 清空输入框**
- **`entry.delete(起始位置, 结束位置)`**：删除输入框中的内容。
  ```python
  entry.delete(0, tk.END)  # 清空输入框
  ```

### **4.3 插入内容**
- **`entry.insert(位置, 内容)`**：在指定位置插入内容。
  ```python
  entry.insert(0, "默认文本")  # 在输入框开头插入文本
  ```

---

## **5. Checkbutton（复选框）**
- **`tk.Checkbutton`**：用于创建复选框，用户可以选择或取消选择。
  ```python
  var = tk.BooleanVar()  # 创建一个布尔变量，用于追踪复选框状态
  checkbutton = tk.Checkbutton(root, text="选择我", variable=var)  # 创建复选框
  checkbutton.pack()
  ```

### **5.1 获取复选框状态**
- **`var.get()`**：获取复选框的状态（`True` 或 `False`）。
  ```python
  is_checked = var.get()
  ```

---

## **6. ScrolledText（带滚动条的文本框）**
- **`tk.scrolledtext.ScrolledText`**：用于显示多行文本，并带有滚动条。
  ```python
  text_area = scrolledtext.ScrolledText(root, width=40, height=10)  # 创建文本框
  text_area.pack()
  ```

### **6.1 插入文本**
- **`text_area.insert(位置, 内容)`**：在指定位置插入文本。
  ```python
  text_area.insert(tk.END, "这是插入的文本")  # 在文本框末尾插入文本
  ```

### **6.2 清空文本框**
- **`text_area.delete(起始位置, 结束位置)`**：删除文本框中的内容。
  ```python
  text_area.delete(1.0, tk.END)  # 清空文本框
  ```

### **6.3 获取文本框内容**
- **`text_area.get(起始位置, 结束位置)`**：获取文本框中的内容。
  ```python
  content = text_area.get(1.0, tk.END)  # 获取全部内容
  ```

---

## **7. Button（按钮）**
- **`tk.Button`**：用于创建按钮，用户可以点击触发事件。
  ```python
  button = tk.Button(root, text="点击我", command=回调函数)  # 创建按钮
  button.pack()
  ```

### **7.1 绑定事件**
- **`command=回调函数`**：按钮点击时执行的函数。
  ```python
  def on_button_click():
      print("按钮被点击了")
  button = tk.Button(root, text="点击我", command=on_button_click)
  ```

---

## **8. Pack 布局管理器**
- **`pack()`**：将组件添加到窗口中，默认从上到下排列。
  ```python
  label.pack()  # 将标签添加到窗口中
  ```

### **8.1 常用参数**
- **`side`**：设置组件的位置（`tk.LEFT`、`tk.RIGHT`、`tk.TOP`、`tk.BOTTOM`）。
  ```python
  label.pack(side=tk.LEFT)  # 将标签放在左侧
  ```
- **`padx` 和 `pady`**：设置组件的外边距。
  ```python
  label.pack(padx=10, pady=10)  # 设置外边距
  ```
- **`fill`**：设置组件填充方式（`tk.X`、`tk.Y`、`tk.BOTH`）。
  ```python
  label.pack(fill=tk.X)  # 水平填充
  ```
- **`expand`**：设置组件是否扩展以填充额外空间。
  ```python
  label.pack(expand=True)  # 允许扩展
  ```

---

## **9. Config（配置组件属性）**
- **`config()`**：动态修改组件的属性。
  ```python
  label.config(text="新文本", fg="red")  # 修改标签文本和前景色
  ```

---

## **10. 其他常用操作**
### **10.1 `tk.END`**
- **`tk.END`**：表示文本框或输入框的末尾位置。
  ```python
  text_area.insert(tk.END, "在末尾插入文本")
  ```

### **10.2 消息框**
- **`messagebox.showinfo()`**：显示信息提示框。
  ```python
  from tkinter import messagebox
  messagebox.showinfo("提示", "操作成功")
  ```

- **`messagebox.showerror()`**：显示错误提示框。
  ```python
  messagebox.showerror("错误", "操作失败")
  ```

---

## **11. 完整示例**
```python
import tkinter as tk
from tkinter import scrolledtext, messagebox

def on_button_click():
    content = entry.get()
    text_area.insert(tk.END, f"输入的内容: {content}\n")
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("示例程序")
root.geometry("400x300")

# 创建Frame
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# 创建Label
label = tk.Label(frame, text="请输入内容:")
label.pack(side=tk.LEFT)

# 创建Entry
entry = tk.Entry(frame, width=30)
entry.pack(side=tk.LEFT, padx=10)

# 创建Button
button = tk.Button(root, text="提交", command=on_button_click)
button.pack(pady=10)

# 创建ScrolledText
text_area = scrolledtext.ScrolledText(root, width=40, height=10)
text_area.pack(padx=10, pady=10)

root.mainloop()
```


