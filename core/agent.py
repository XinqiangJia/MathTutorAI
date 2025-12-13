# core/agent.py

import requests
from config.settings import OLLAMA_API_URL, OLLAMA_MODEL, SYSTEM_PROMPT
from utils.logger import log

class MathTutorAgent:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.url = OLLAMA_API_URL
        self.system_prompt = SYSTEM_PROMPT

    def generate_response(self, user_input: str, context: str = "") -> str:
        prompt = f"{context}\n学生：{user_input}\n老师："
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": self.system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        try:
            response = requests.post(self.url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                reply = result.get("response", "").strip()
                log(f"AI 回复: {reply}")
                return reply
            else:
                error_msg = f"Ollama 返回错误: {response.status_code}"
                log(error_msg)
                return "老师现在有点忙，稍后再试试吧～"
        except Exception as e:
            error_msg = f"请求失败: {e}"
            log(error_msg)
            return "哎呀，网络出问题了，请检查 Ollama 是否运行！"