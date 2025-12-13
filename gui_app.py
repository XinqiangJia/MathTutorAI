# gui_app.py

import flet as ft
from core.agent import MathTutorAgent
from core.tts import speak

agent = MathTutorAgent()
conversation_history = ""


def main(page: ft.Page):
    page.title = "小学数学 AI 老师"
    page.window.width = 600
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.LIGHT

    chat_area = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    user_input = ft.TextField(label="输入你的问题...", expand=True)

    def copy_to_clipboard(text: str):
        """兼容旧版 Flet 的复制 + Snackbar 提示"""
        page.set_clipboard(text)
        snack = ft.SnackBar(
            content=ft.Text("✅ 已复制到剪贴板！"),
            duration=1000
        )
        page.snack_bar = snack
        snack.open = True
        page.update()

    def send_message(e):
        global conversation_history
        question = user_input.value.strip()
        if not question:
            return

        # 用户消息
        chat_area.controls.append(
            ft.Row([ft.Text(f"你：{question}", color="blue", expand=True)])
        )
        user_input.value = ""
        page.update()

        # AI 回复
        reply = agent.generate_response(question, context=conversation_history)
        full_reply_text = f"老师：{reply}"

        # 复制按钮（使用字符串图标）
        copy_btn = ft.IconButton(
            icon="content_copy",
            tooltip="复制",
            on_click=lambda _: copy_to_clipboard(full_reply_text),
            icon_color="grey600"
        )
        reply_row = ft.Row(
            [
                ft.Text(full_reply_text, color="green", expand=True),
                copy_btn
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
        chat_area.controls.append(reply_row)
        page.update()

        speak(reply)

        conversation_history += f"\n学生：{question}\n老师：{reply}"
        if len(conversation_history) > 1200:
            conversation_history = conversation_history[-1000:]

    send_btn = ft.ElevatedButton("发送", on_click=send_message)
    input_row = ft.Row([user_input, send_btn], alignment=ft.MainAxisAlignment.END)

    page.add(
        ft.Text("🧠 小学数学 AI 老师", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Container(
            chat_area,
            expand=True,
            padding=10,
            border=ft.border.all(1, "grey300")
        ),
        input_row
    )


if __name__ == "__main__":
    ft.app(target=main)