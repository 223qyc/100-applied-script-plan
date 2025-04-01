import requests
import random
import threading
from tkinter import *
from tkinter import ttk, messagebox
import json
import os
from urllib.parse import urlparse


class ProxyPool:
    def __init__(self, filename="proxy_pool.json"):
        self.filename = filename
        self.proxies = []
        self.load_proxies()

    def load_proxies(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    self.proxies = json.load(f)
                except json.JSONDecodeError:
                    self.proxies = []
        else:
            self.proxies = []

    def save_proxies(self):
        with open(self.filename, 'w') as f:
            json.dump(self.proxies, f, indent=2)

    def add_proxy(self, proxy, protocol='http', test_url='http://www.baidu.com'):
        """添加代理并测试其可用性"""
        if not proxy.strip():
            return False, "代理地址不能为空"

        # 标准化代理格式
        if '://' not in proxy:
            proxy = f"{protocol}://{proxy}"

        # 检查是否已存在
        for p in self.proxies:
            if p['proxy'] == proxy:
                return False, "该代理已存在"

        # 测试代理
        is_ok, speed = self.test_proxy(proxy, test_url)

        if is_ok:
            self.proxies.append({
                'proxy': proxy,
                'protocol': protocol,
                'is_working': is_ok,
                'speed': speed,
                'test_url': test_url
            })
            self.save_proxies()
            return True, f"代理添加成功，响应时间: {speed:.2f}s"
        else:
            return False, "代理测试失败"

    def remove_proxy(self, proxy):
        """移除代理"""
        for i, p in enumerate(self.proxies):
            if p['proxy'] == proxy:
                self.proxies.pop(i)
                self.save_proxies()
                return True
        return False

    def test_proxy(self, proxy, test_url='http://www.baidu.com', timeout=5):
        """测试代理是否可用"""
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            start = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            end = time.time()
            if response.status_code == 200:
                return True, end - start
        except Exception as e:
            pass
        return False, 0

    def test_all_proxies(self, test_url='http://www.baidu.com'):
        """测试所有代理"""
        for proxy in self.proxies:
            is_ok, speed = self.test_proxy(proxy['proxy'], test_url)
            proxy['is_working'] = is_ok
            proxy['speed'] = speed if is_ok else 0
            proxy['test_url'] = test_url
        self.save_proxies()

    def get_random_proxy(self, protocol=None, working_only=True):
        """随机获取一个代理"""
        candidates = []
        for p in self.proxies:
            if working_only and not p['is_working']:
                continue
            if protocol and p['protocol'] != protocol:
                continue
            candidates.append(p['proxy'])

        if candidates:
            return random.choice(candidates)
        return None

    def get_all_proxies(self):
        """获取所有代理"""
        return self.proxies.copy()


class ProxyPoolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("简单代理池工具 v1.0")
        self.root.geometry("800x600")

        self.proxy_pool = ProxyPool()

        self.create_widgets()
        self.update_proxy_list()

    def create_widgets(self):
        # 顶部框架 - 添加代理
        top_frame = LabelFrame(self.root, text="添加代理", padx=5, pady=5)
        top_frame.pack(fill=X, padx=10, pady=5)

        Label(top_frame, text="代理地址:").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.proxy_entry = Entry(top_frame, width=40)
        self.proxy_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(top_frame, text="协议类型:").grid(row=0, column=2, padx=5, pady=5, sticky=E)
        self.protocol_var = StringVar(value="http")
        protocol_options = ["http", "https", "socks4", "socks5"]
        self.protocol_menu = OptionMenu(top_frame, self.protocol_var, *protocol_options)
        self.protocol_menu.grid(row=0, column=3, padx=5, pady=5)

        Label(top_frame, text="测试URL:").grid(row=1, column=0, padx=5, pady=5, sticky=E)
        self.test_url_entry = Entry(top_frame, width=40)
        self.test_url_entry.insert(0, "http://www.baidu.com")
        self.test_url_entry.grid(row=1, column=1, padx=5, pady=5)

        self.add_btn = Button(top_frame, text="添加并测试", command=self.add_proxy)
        self.add_btn.grid(row=1, column=3, padx=5, pady=5)

        # 中间框架 - 代理列表
        mid_frame = LabelFrame(self.root, text="代理列表", padx=5, pady=5)
        mid_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        columns = ("proxy", "protocol", "status", "speed", "test_url")
        self.proxy_tree = ttk.Treeview(mid_frame, columns=columns, show="headings")

        self.proxy_tree.heading("proxy", text="代理地址")
        self.proxy_tree.heading("protocol", text="协议")
        self.proxy_tree.heading("status", text="状态")
        self.proxy_tree.heading("speed", text="响应时间(s)")
        self.proxy_tree.heading("test_url", text="测试URL")

        self.proxy_tree.column("proxy", width=200)
        self.proxy_tree.column("protocol", width=80)
        self.proxy_tree.column("status", width=80)
        self.proxy_tree.column("speed", width=100)
        self.proxy_tree.column("test_url", width=200)

        self.proxy_tree.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # 绑定右键菜单
        self.proxy_tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="测试选中代理", command=self.test_selected_proxy)
        self.context_menu.add_command(label="删除选中代理", command=self.remove_selected_proxy)
        self.context_menu.add_command(label="复制代理地址", command=self.copy_selected_proxy)

        # 底部框架 - 操作按钮
        bottom_frame = Frame(self.root)
        bottom_frame.pack(fill=X, padx=10, pady=5)

        self.test_all_btn = Button(bottom_frame, text="测试所有代理", command=self.test_all_proxies)
        self.test_all_btn.pack(side=LEFT, padx=5)

        self.get_random_btn = Button(bottom_frame, text="获取随机代理", command=self.get_random_proxy)
        self.get_random_btn.pack(side=LEFT, padx=5)

        self.clear_btn = Button(bottom_frame, text="清空代理池", command=self.clear_proxy_pool)
        self.clear_btn.pack(side=RIGHT, padx=5)

        # 状态栏
        self.status_var = StringVar()
        self.status_var.set("就绪")
        self.status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(fill=X, padx=10, pady=5)

    def update_proxy_list(self):
        """更新代理列表显示"""
        self.proxy_tree.delete(*self.proxy_tree.get_children())
        for proxy in self.proxy_pool.get_all_proxies():
            status = "可用" if proxy['is_working'] else "不可用"
            speed = f"{proxy['speed']:.2f}" if proxy['is_working'] else "N/A"
            self.proxy_tree.insert("", "end", values=(
                proxy['proxy'],
                proxy['protocol'],
                status,
                speed,
                proxy['test_url']
            ))

    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.proxy_tree.identify_row(event.y)
        if item:
            self.proxy_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def add_proxy(self):
        """添加代理"""
        proxy = self.proxy_entry.get().strip()
        protocol = self.protocol_var.get()
        test_url = self.test_url_entry.get().strip()

        if not proxy:
            messagebox.showerror("错误", "代理地址不能为空")
            return

        self.status_var.set("正在测试代理...")
        self.root.update()

        # 在新线程中添加代理，避免界面冻结
        def add_proxy_thread():
            try:
                success, msg = self.proxy_pool.add_proxy(proxy, protocol, test_url)
                self.root.after(0, lambda: messagebox.showinfo("结果", msg) if success else messagebox.showerror("错误",
                                                                                                                 msg))
                self.root.after(0, self.update_proxy_list)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"添加代理失败: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("就绪"))

        threading.Thread(target=add_proxy_thread, daemon=True).start()

    def test_selected_proxy(self):
        """测试选中的代理"""
        selected = self.proxy_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个代理")
            return

        item = selected[0]
        values = self.proxy_tree.item(item, 'values')
        proxy = values[0]
        test_url = self.test_url_entry.get().strip()

        self.status_var.set(f"正在测试代理 {proxy}...")
        self.root.update()

        def test_proxy_thread():
            try:
                is_ok, speed = self.proxy_pool.test_proxy(proxy, test_url)

                # 更新代理状态
                for p in self.proxy_pool.proxies:
                    if p['proxy'] == proxy:
                        p['is_working'] = is_ok
                        p['speed'] = speed if is_ok else 0
                        p['test_url'] = test_url
                        break

                self.proxy_pool.save_proxies()

                msg = f"代理测试 {'成功' if is_ok else '失败'}"
                if is_ok:
                    msg += f"，响应时间: {speed:.2f}s"

                self.root.after(0, lambda: messagebox.showinfo("测试结果", msg))
                self.root.after(0, self.update_proxy_list)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"测试代理失败: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("就绪"))

        threading.Thread(target=test_proxy_thread, daemon=True).start()

    def remove_selected_proxy(self):
        """删除选中的代理"""
        selected = self.proxy_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个代理")
            return

        item = selected[0]
        values = self.proxy_tree.item(item, 'values')
        proxy = values[0]

        if messagebox.askyesno("确认", f"确定要删除代理 {proxy} 吗？"):
            if self.proxy_pool.remove_proxy(proxy):
                self.update_proxy_list()
                messagebox.showinfo("成功", "代理已删除")
            else:
                messagebox.showerror("错误", "删除代理失败")

    def copy_selected_proxy(self):
        """复制选中的代理地址"""
        selected = self.proxy_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个代理")
            return

        item = selected[0]
        values = self.proxy_tree.item(item, 'values')
        proxy = values[0]

        self.root.clipboard_clear()
        self.root.clipboard_append(proxy)
        self.status_var.set(f"已复制代理地址: {proxy}")

    def test_all_proxies(self):
        """测试所有代理"""
        if not self.proxy_pool.proxies:
            messagebox.showwarning("警告", "代理池为空")
            return

        test_url = self.test_url_entry.get().strip()

        self.status_var.set("正在测试所有代理，请稍候...")
        self.test_all_btn.config(state=DISABLED)
        self.root.update()

        def test_all_thread():
            try:
                self.proxy_pool.test_all_proxies(test_url)
                self.root.after(0, self.update_proxy_list)
                self.root.after(0, lambda: messagebox.showinfo("完成", "所有代理测试完成"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"测试代理失败: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("就绪"))
                self.root.after(0, lambda: self.test_all_btn.config(state=NORMAL))

        threading.Thread(target=test_all_thread, daemon=True).start()

    def get_random_proxy(self):
        """获取随机代理"""
        protocol = self.protocol_var.get()
        proxy = self.proxy_pool.get_random_proxy(protocol)

        if proxy:
            self.root.clipboard_clear()
            self.root.clipboard_append(proxy)
            messagebox.showinfo("随机代理", f"已选择并复制代理:\n{proxy}")
            self.status_var.set(f"已复制随机代理: {proxy}")
        else:
            messagebox.showwarning("警告", "没有可用的代理")

    def clear_proxy_pool(self):
        """清空代理池"""
        if not self.proxy_pool.proxies:
            messagebox.showwarning("警告", "代理池已为空")
            return

        if messagebox.askyesno("确认", "确定要清空代理池吗？"):
            self.proxy_pool.proxies = []
            self.proxy_pool.save_proxies()
            self.update_proxy_list()
            messagebox.showinfo("成功", "代理池已清空")


if __name__ == "__main__":
    import time

    root = Tk()
    app = ProxyPoolGUI(root)
    root.mainloop()