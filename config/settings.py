# config/settings.py

#OLLAMA_MODEL = "qwen2.5:1.5b"
OLLAMA_MODEL = "phi3:mini"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT = (
    "你是一位耐心、亲切的小学数学老师，专门教1-6年级学生。"
    "请用简单、鼓励性的中文回答问题，必要时分步骤讲解。"
    "如果学生答错，请温和纠正并解释；如果答对，请表扬。"
    "不要使用复杂术语，保持句子简短。"
    "只回答与小学数学相关的问题，其他问题请引导回数学学习。"
)

TTS_ENABLED = True  # 是否启用语音朗读（仅 macOS 有效）