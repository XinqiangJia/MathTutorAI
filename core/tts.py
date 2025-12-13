# core/tts.py

import os
import subprocess
from config.settings import TTS_ENABLED

def speak(text: str):
    if not TTS_ENABLED:
        return
    try:
        # 使用 macOS 内置 say 命令
        subprocess.run(["say", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[TTS 错误] {e}")