# main.py

from core.agent import MathTutorAgent
from core.tts import speak

def main():
    print("🚀 启动小学数学 AI 老师（命令行版）...")
    agent = MathTutorAgent()
    conversation = ""

    print("👋 你好！我是你的数学小助手，有什么我可以帮你的吗？输入 '退出' 结束。")
    while True:
        user_input = input("\n你：").strip()
        if not user_input or user_input.lower() in ["退出", "exit", "bye"]:
            print("再见！记得多练习哦～")
            break

        reply = agent.generate_response(user_input, context=conversation)
        print(f"\n🤖 老师：{reply}")
        speak(reply)  # 语音朗读

        # 更新上下文（限制长度）
        conversation += f"\n学生：{user_input}\n老师：{reply}"
        if len(conversation) > 1200:
            conversation = conversation[-1000:]

if __name__ == "__main__":
    main()