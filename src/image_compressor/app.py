import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import os
import io
from PIL import Image

# ----------------------------------------------------------------------------
# 核心压缩算法 (从之前的脚本移植过来，并稍作修改以适应GUI)
# ----------------------------------------------------------------------------
def smart_compress_image(input_path, output_path, target_kb, update_status_callback,
                         initial_quality=75, min_width=600):
    try:
        target_bytes = target_kb * 1024
        
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            original_width, original_height = img.size
            current_width = original_width
            
            # --- 阶段一：寻找最佳尺寸 ---
            update_status_callback(f"阶段一: 寻找最佳尺寸 (固定质量: {initial_quality})...")
            final_img = None
            while current_width >= min_width:
                aspect_ratio = original_height / original_width
                current_height = int(current_width * aspect_ratio)
                
                resized_img = img.resize((current_width, current_height), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                resized_img.save(buffer, format='JPEG', quality=initial_quality, optimize=True)
                current_size = buffer.tell()
                
                update_status_callback(f"尝试宽度: {current_width}px, 大小: {current_size / 1024:.1f} KB")

                if current_size <= target_bytes:
                    final_img = resized_img
                    break
                
                step = max(50, int(current_width * 0.05))
                current_width -= step
            
            if not final_img:
                raise ValueError("即使在最小尺寸下也无法压缩到目标大小")

            # --- 阶段二：优化质量 ---
            update_status_callback(f"阶段二: 优化质量 (固定宽度: {final_img.width}px)...")
            best_quality_buffer = io.BytesIO()
            final_img.save(best_quality_buffer, format='JPEG', quality=initial_quality, optimize=True)

            for quality in range(initial_quality + 1, 96):
                buffer = io.BytesIO()
                final_img.save(buffer, format='JPEG', quality=quality, optimize=True)
                
                if buffer.tell() <= target_bytes:
                    best_quality_buffer = buffer
                else:
                    break
            
            with open(output_path, 'wb') as f:
                f.write(best_quality_buffer.getvalue())

            return True, f"压缩成功! 文件大小: {os.path.getsize(output_path) / 1024:.1f} KB"

    except Exception as e:
        return False, f"错误: {e}"

# ----------------------------------------------------------------------------
# 图形界面 (GUI) 主程序
# ----------------------------------------------------------------------------
class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片压缩神器 V1.0")
        self.root.geometry("500x300")
        
        self.input_path = tk.StringVar()
        self.target_size_kb = tk.IntVar(value=200)

        # --- UI 组件 ---
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=BOTH, expand=YES)

        # 文件选择
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=X, pady=5)
        ttk.Label(file_frame, text="选择图片:").pack(side=LEFT, padx=5)
        ttk.Entry(file_frame, textvariable=self.input_path, state="readonly").pack(side=LEFT, fill=X, expand=YES)
        ttk.Button(file_frame, text="浏览...", command=self.select_file, bootstyle="outline").pack(side=LEFT, padx=5)

        # 目标大小
        size_frame = ttk.Frame(frame)
        size_frame.pack(fill=X, pady=10)
        ttk.Label(size_frame, text="目标大小 (KB):").pack(side=LEFT, padx=5)
        ttk.Spinbox(size_frame, from_=10, to=1000, textvariable=self.target_size_kb, width=10).pack(side=LEFT)

        # 开始按钮
        ttk.Button(frame, text="开始压缩", command=self.start_compression_thread, bootstyle="success").pack(pady=20, ipady=10, fill=X)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(frame, textvariable=self.status_var, font=("", 9)).pack(side=BOTTOM, fill=X)

    def select_file(self):
        path = filedialog.askopenfilename(
            title="请选择一个图片文件",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")]
        )
        if path:
            self.input_path.set(path)
            self.status_var.set(f"已选择: {os.path.basename(path)}")
            
    def update_status(self, message):
        self.status_var.set(message)

    def start_compression_thread(self):
        if not self.input_path.get():
            messagebox.showerror("错误", "请先选择一个图片文件！")
            return
            
        # 使用线程来运行压缩，避免UI卡死
        thread = threading.Thread(target=self.run_compression)
        thread.daemon = True # 确保主窗口关闭时线程也退出
        thread.start()

    def run_compression(self):
        self.update_status("正在压缩，请稍候...")
        
        in_path = self.input_path.get()
        target_kb = self.target_size_kb.get()
        
        path_parts = os.path.splitext(in_path)
        out_path = f"{path_parts[0]}_compressed.jpg"

        success, message = smart_compress_image(in_path, out_path, target_kb, self.update_status)

        if success:
            self.update_status(message)
            messagebox.showinfo("成功", f"图片压缩成功!\n文件已保存为:\n{out_path}")
        else:
            self.update_status("操作失败")
            messagebox.showerror("失败", message)


