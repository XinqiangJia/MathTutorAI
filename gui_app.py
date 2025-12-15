import flet as ft
import threading
import tempfile
import os
from paddleocr import PaddleOCR
from core.agent import MathTutorAgent

# 初始化 OCR
print("正在加载中文 OCR 模型...")
ocr_engine = PaddleOCR(lang="ch")
print("✅ OCR 模型加载完成！")

# 初始化 AI 老师代理
agent = MathTutorAgent()


def main(page: ft.Page):
    page.title = "小学数学 AI 老师"
    page.window.width = 650
    page.window.height = 750
    page.theme_mode = "light"

    # ========================
    # 全局变量
    # ========================
    conversation_history = []  # 存储对话历史

    # ========================
    # 创建聊天区域
    # ========================
    chat_area = ft.Column(scroll="adaptive", expand=True)

    # 创建输入组件
    user_input = ft.TextField(
        label="输入你的问题...",
        expand=True
    )

    # ========================
    # 工具函数
    # ========================
    def copy_to_clipboard(text: str):
        page.set_clipboard(text)
        page.snack_bar = ft.SnackBar(
            content=ft.Text("✅ 已复制到剪贴板！"),
            duration=1000
        )
        page.snack_bar.open = True
        page.update()

    def show_snackbar(message: str):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            duration=2000
        )
        page.snack_bar.open = True
        page.update()

    def add_conversation(role: str, content: str):
        """添加对话到历史记录"""
        conversation_history.append({"role": role, "content": content})
        # 保持历史记录长度
        if len(conversation_history) > 20:  # 保留最近20轮对话
            conversation_history.pop(0)

    def get_context_string():
        """将对话历史转换为字符串上下文"""
        context = ""
        for conv in conversation_history[-10:]:  # 只使用最近10轮对话作为上下文
            if conv["role"] == "student":
                context += f"学生：{conv['content']}\n"
            elif conv["role"] == "teacher":
                context += f"老师：{conv['content']}\n"
        return context

    # ========================
    # 最简单的UI更新方式
    # ========================
    def safe_update():
        """安全更新UI"""
        try:
            page.update()
        except:
            pass

    # ========================
    # 发送消息函数
    # ========================
    def send_message(e):
        question = user_input.value.strip()
        if not question:
            show_snackbar("请输入问题")
            return

        # 添加用户对话记录
        add_conversation("student", question)

        # 显示用户消息
        full_user_text = f"你：{question}"
        user_copy_btn = ft.IconButton(
            icon="content_copy",
            tooltip="复制",
            on_click=lambda _: copy_to_clipboard(full_user_text),
            icon_color="grey600",
            icon_size=14
        )
        user_row = ft.Row([ft.Text(full_user_text, color="blue", expand=True), user_copy_btn])
        chat_area.controls.append(user_row)

        # 显示"正在思考..."
        thinking_row = ft.Row([ft.Text("老师：🤔 正在思考...", color="orange")])
        chat_area.controls.append(thinking_row)
        user_input.value = ""
        safe_update()

        # 创建AI回复线程
        def ai_thread():
            try:
                # 获取上下文
                context = get_context_string()
                reply = agent.generate_response(question, context=context)
            except Exception as ex:
                reply = "❌ 老师暂时无法回答，请检查 Ollama 是否正在运行。"

            # 添加老师对话记录
            add_conversation("teacher", reply)

            full_reply_text = f"老师：{reply.strip()}"
            copy_btn = ft.IconButton(
                icon="content_copy",
                tooltip="复制",
                on_click=lambda _: copy_to_clipboard(full_reply_text),
                icon_color="grey600",
                icon_size=14
            )
            real_reply_row = ft.Row([ft.Text(full_reply_text, color="green", expand=True), copy_btn])

            # 直接更新UI - Flet 通常能处理线程安全
            try:
                # 移除思考中的消息
                if thinking_row in chat_area.controls:
                    chat_area.controls.remove(thinking_row)
                # 添加AI回复
                chat_area.controls.append(real_reply_row)
                safe_update()
            except Exception as e:
                print(f"更新UI时出错: {e}")

        # 启动AI线程
        thread = threading.Thread(target=ai_thread, daemon=True)
        thread.start()

    # 设置输入框的提交事件
    user_input.on_submit = send_message

    # ========================
    # 文件选择器回调
    # ========================
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            handle_uploaded_file(e.files[0])
        else:
            show_snackbar("❌ 未选择文件")

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)
    safe_update()

    # ========================
    # 处理上传的图片文件
    # ========================
    def handle_uploaded_file(file_info):
        """处理上传的文件"""
        print(f"📌 开始处理文件: {file_info.name}")

        # 显示处理中的消息
        thinking_row = ft.Row([ft.Text("📷 正在处理图片...", color="orange")])
        chat_area.controls.append(thinking_row)
        safe_update()

        def process_file_thread():
            question = ""

            try:
                file_name = file_info.name
                file_size = file_info.size

                # 尝试获取文件内容
                if hasattr(file_picker, 'get_file_content') and hasattr(file_info, 'id'):
                    try:
                        file_data = file_picker.get_file_content(file_info.id)
                        if file_data:
                            # 保存为临时文件
                            suffix = os.path.splitext(file_name)[1] if '.' in file_name else '.png'
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                                tmp.write(file_data)
                                tmp_path = tmp.name

                            # 使用 OCR 处理
                            result = ocr_engine.ocr(tmp_path, cls=True)
                            if result and result[0]:
                                text = " ".join([word_info[1][0] for line in result for word_info in line])
                                question = text.strip() or "（图片识别无文字）"
                            else:
                                question = "（图片识别失败）"

                            # 清理临时文件
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                        else:
                            question = f"文件：{file_name} ({file_size / 1024:.1f} KB)"
                    except Exception as read_ex:
                        print(f"📌 读取文件失败: {read_ex}")
                        question = f"文件：{file_name} ({file_size / 1024:.1f} KB)"
                else:
                    question = f"文件：{file_name} ({file_size / 1024:.1f} KB)"

            except Exception as ex:
                question = f"（处理失败：{str(ex)[:50]}）"
                print(f"📌 处理文件时出错: {ex}")

            # 直接更新UI
            try:
                # 移除处理中的消息
                if thinking_row in chat_area.controls:
                    chat_area.controls.remove(thinking_row)

                # 显示识别结果
                full_user_text = f"你（图片）：{question}"
                user_copy_btn = ft.IconButton(
                    icon="content_copy",
                    tooltip="复制",
                    on_click=lambda _: copy_to_clipboard(full_user_text),
                    icon_color="grey600",
                    icon_size=14
                )
                user_row = ft.Row([ft.Text(full_user_text, color="blue", expand=True), user_copy_btn])
                chat_area.controls.append(user_row)

                # 添加对话记录
                add_conversation("student", f"[图片] {question}")

                # 如果识别成功，自动请求AI回答
                if question and "（" not in question and "文件：" not in question:
                    # 显示思考中
                    thinking_row2 = ft.Row([ft.Text("老师：🤔 正在思考...", color="orange")])
                    chat_area.controls.append(thinking_row2)

                    # 启动AI回复线程
                    def ai_reply_thread():
                        try:
                            context = get_context_string()
                            reply = agent.generate_response(question, context=context)
                        except Exception:
                            reply = "❌ 老师暂时无法回答。"

                        # 添加老师对话记录
                        add_conversation("teacher", reply)

                        full_reply_text = f"老师：{reply.strip()}"
                        copy_btn = ft.IconButton(
                            icon="content_copy",
                            tooltip="复制",
                            on_click=lambda _: copy_to_clipboard(full_reply_text),
                            icon_color="grey600",
                            icon_size=14
                        )
                        reply_row = ft.Row([ft.Text(full_reply_text, color="green", expand=True), copy_btn])

                        # 直接更新UI
                        try:
                            if thinking_row2 in chat_area.controls:
                                chat_area.controls.remove(thinking_row2)
                            chat_area.controls.append(reply_row)
                            safe_update()
                        except Exception as e:
                            print(f"更新UI2时出错: {e}")

                    # 启动AI回复线程
                    ai_thread = threading.Thread(target=ai_reply_thread, daemon=True)
                    ai_thread.start()
                else:
                    # 提供手动输入选项
                    manual_btn = ft.ElevatedButton(
                        "📝 手动输入题目内容",
                        on_click=lambda e: open_manual_input_dialog(
                            file_info.name if hasattr(file_info, 'name') else "图片"),
                        height=30
                    )
                    chat_area.controls.append(manual_btn)

                safe_update()

            except Exception as e:
                print(f"更新UI时出错: {e}")

        # 启动文件处理线程
        thread = threading.Thread(target=process_file_thread, daemon=True)
        thread.start()

    # ========================
    # 手动输入对话框
    # ========================
    def open_manual_input_dialog(file_name):
        manual_input = ft.TextField(
            label=f"请输入 '{file_name}' 的内容",
            multiline=True,
            min_lines=3,
            max_lines=6,
            expand=True
        )

        def submit_manual_input(e):
            question = manual_input.value.strip()
            if not question:
                show_snackbar("请输入内容")
                return

            # 关闭对话框
            page.dialog.open = False

            # 显示用户输入
            full_user_text = f"你（图片/手动输入）：{question}"
            user_copy_btn = ft.IconButton(
                icon="content_copy",
                tooltip="复制",
                on_click=lambda _: copy_to_clipboard(full_user_text),
                icon_color="grey600",
                icon_size=14
            )
            user_row = ft.Row([ft.Text(full_user_text, color="blue", expand=True), user_copy_btn])
            chat_area.controls.append(user_row)

            # 添加对话记录
            add_conversation("student", f"[图片/手动] {question}")

            # 显示思考中
            thinking_row = ft.Row([ft.Text("老师：🤔 正在思考...", color="orange")])
            chat_area.controls.append(thinking_row)
            safe_update()

            # 获取AI回答线程
            def get_reply_thread():
                try:
                    context = get_context_string()
                    reply = agent.generate_response(question, context=context)
                except Exception:
                    reply = "❌ 老师暂时无法回答。"

                # 添加老师对话记录
                add_conversation("teacher", reply)

                full_reply_text = f"老师：{reply.strip()}"
                copy_btn = ft.IconButton(
                    icon="content_copy",
                    tooltip="复制",
                    on_click=lambda _: copy_to_clipboard(full_reply_text),
                    icon_color="grey600",
                    icon_size=14
                )
                reply_row = ft.Row([ft.Text(full_reply_text, color="green", expand=True), copy_btn])

                # 直接更新UI
                try:
                    if thinking_row in chat_area.controls:
                        chat_area.controls.remove(thinking_row)
                    chat_area.controls.append(reply_row)
                    safe_update()
                except Exception as e:
                    print(f"更新对话框UI时出错: {e}")

            # 启动AI回复线程
            thread = threading.Thread(target=get_reply_thread, daemon=True)
            thread.start()

        page.dialog = ft.AlertDialog(
            title=ft.Text("手动输入题目内容"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"文件: {file_name}"),
                    manual_input
                ]),
                width=400,
                height=200
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda e: setattr(page.dialog, 'open', False)),
                ft.TextButton("确定", on_click=submit_manual_input),
            ]
        )
        page.dialog.open = True
        safe_update()

    # ========================
    # 打开文件选择器
    # ========================
    def open_file_picker(e):
        file_picker.pick_files(
            allowed_extensions=["png", "jpg", "jpeg"],
            file_type=ft.FilePickerFileType.CUSTOM,
            allow_multiple=False
        )

    # ========================
    # 创建界面组件
    # ========================
    upload_btn = ft.IconButton(
        icon="attach_file",
        tooltip="上传题目图片（PNG/JPG）",
        on_click=open_file_picker
    )

    send_btn = ft.ElevatedButton("发送", on_click=send_message)

    input_row = ft.Row(
        [user_input, upload_btn, send_btn],
        alignment="end",
        spacing=10
    )

    # ========================
    # 页面布局
    # ========================
    page.add(
        ft.Text("🧠 小学数学 AI 老师", size=24, weight="bold"),
        ft.Divider(),
        ft.Container(
            content=chat_area,
            expand=True,
            padding=10,
            border=ft.border.all(1, "#CCCCCC"),
            border_radius=5
        ),
        ft.Text("📝 提示：点击📎按钮上传题目图片，或直接输入问题", size=12, color="#666666"),
        input_row
    )


# 启动应用
if __name__ == "__main__":
    print("🚀 启动小学数学 AI 老师应用...")
    #ft.app(target=main)
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)