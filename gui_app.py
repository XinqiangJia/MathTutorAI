# gui_app.py
import threading
import flet as ft
from core.agent import MathTutorAgent
from core.tts import speak


agent = MathTutorAgent()

def main(page: ft.Page):
    page.title = "小学数学 AI 老师"
    page.window.width = 600
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.LIGHT

    chat_area = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    # Step 1: 先定义 conversation_history（闭包变量）
    conversation_history = ""

    # Step 2: 定义辅助函数
    def copy_to_clipboard(text: str):
        page.set_clipboard(text)
        snack = ft.SnackBar(content=ft.Text("✅ 已复制到剪贴板！"), duration=1000)
        page.snack_bar = snack
        snack.open = True
        page.update()

    # Step 3: ✅ 先定义 send_message
    def send_message(e):
        nonlocal conversation_history
        question = user_input.value.strip()
        if not question:
            return

        # === 显示用户消息 ===
        full_user_text = f"你：{question}"
        user_copy_btn = ft.IconButton(
            icon="content_copy",
            tooltip="复制",
            on_click=lambda _: copy_to_clipboard(full_user_text),
            icon_color="grey600",
            icon_size = 14
        )
        user_row = ft.Row([ft.Text(full_user_text, color="blue", expand=True), user_copy_btn])
        chat_area.controls.append(user_row)

        # === 显示“正在思考...” ===
        thinking_text = ft.Text("老师：🤔 正在思考...", color="orange")
        thinking_row = ft.Row([thinking_text])
        chat_area.controls.append(thinking_row)
        user_input.value = ""
        page.update()

        def _get_ai_reply():
            nonlocal conversation_history, question, thinking_row
            try:
                reply = agent.generate_response(question, context=conversation_history)
            except Exception:
                reply = "❌ 老师暂时无法回答，请检查 Ollama 是否运行。"

            full_reply_text = reply.strip()
            copy_btn = ft.IconButton(
                icon="content_copy",
                tooltip="复制",
                on_click=lambda _: copy_to_clipboard(full_reply_text),
                icon_color="grey600",
                icon_size = 14
            )
            real_reply_row = ft.Row([ft.Text(full_reply_text, color="green", expand=True), copy_btn])

            chat_area.controls.remove(thinking_row)
            chat_area.controls.append(real_reply_row)
            page.update()

            speak(reply)

            conversation_history += f"\n学生：{question}\n老师：{reply}"
            if len(conversation_history) > 1200:
                conversation_history = conversation_history[-1000:]

        threading.Thread(target=_get_ai_reply, daemon=True).start()

    # Step 4: ✅ 现在 send_message 已定义，可以安全引用
    user_input = ft.TextField(
        label="输入你的问题...",
        expand=True,
        on_submit=send_message  # ← 安全！
    )

    # Step 5: 创建发送按钮
    send_btn = ft.ElevatedButton("发送", on_click=send_message)

    input_row = ft.Row([user_input, send_btn], alignment=ft.MainAxisAlignment.END)

    page.add(
        ft.Text("🧠 小学数学 AI 老师", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Container(chat_area, expand=True, padding=10, border=ft.border.all(1, "grey300")),
        input_row
    )

if __name__ == "__main__":
    ft.app(target=main)