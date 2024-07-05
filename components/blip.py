import gradio as gr


# import os
# import sys

# # 获取当前文件的目录
# current_dir = os.path.dirname(__file__)
# # 获取上一级目录
# parent_dir = os.path.dirname(current_dir)
# print(parent_dir)
# # 将上一级目录添加到 sys.path
# sys.path.append(parent_dir)
# print(sys.path)


def setup_img2text(
    interface_func: object,
    api_host,
    api_port,
):
    with gr.Blocks() as app:
        chatbot = gr.Chatbot(
            # [],
            # elem_id="chatbot",
            bubble_full_width=False,
            height=375,
            label="对话框",
        )

        image = gr.Image(sources=["upload", "clipboard"], type="filepath")

        upload = gr.Button("描述图片")

        model = gr.Textbox(
            "BLIP",
            label="Model",
            lines=1,
            max_lines=1,
            visible=False,
        )

        host = gr.Textbox(
            api_host,
            label="Api Host",
            lines=1,
            max_lines=1,
            visible=False,
        )

        port = gr.Textbox(
            api_port,
            label="Port",
            lines=1,
            max_lines=1,
            visible=False,
        )

        upload.click(
            interface_func,
            [image, chatbot, model, host, port],
            [image, chatbot],
        )

        # app

    return app


# if __name__ == "__main__":

#     setup_img2text(dispatcher).launch(
#         inbrowser=False, server_name="0.0.0.0", server_port=9528
#     )
