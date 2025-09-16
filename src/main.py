import ttkbootstrap as ttk
from image_compressor import ImageCompressorApp


# 使用 ttkbootstrap 创建一个带主题的窗口
app_root = ttk.Window(themename="litera")
app = ImageCompressorApp(app_root)
app_root.mainloop()    

