from PIL import Image
import os

src = "pomodoro.png"
dst = "pomodoro.ico"

try:
    if os.path.exists(src):
        img = Image.open(src)
        # Check if it needs resizing or just saving
        img.save(dst, format='ICO', sizes=[(128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"Successfully converted {src} to {dst}")
    else:
        print(f"Source file {src} does not exist.")
except Exception as e:
    print(f"Error converting icon: {e}")
