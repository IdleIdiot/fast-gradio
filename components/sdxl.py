import gradio as gr


def test(message, history, model, api_host, api_port, attach):
    if not message:
        raise gr.Error("Prompt 参数不足！")

    if message and attach:
        print(attach)
    else:
        print(message)


# def toggle_input(selected_input):
#     """根据选中的输入方式，显示指定的组件"""
#     if selected_input == "文本输入":
#         i = gr.update(visible=False)
#     elif selected_input == "附加参考":
#         i = gr.update(visible=True)
#     return i


def setup_2_img(
    interface_func: object,
    api_host,
    api_port,
):

    with gr.Blocks() as app:
        with gr.Row():
            text_input = gr.Textbox(
                placeholder="用英文短句输入要生成的图片内容",
                visible=True,
                lines=1,
                max_lines=5,
                show_label=False,
            )

        with gr.Row():
            image_upload = gr.Image(
                label="附加参考图",
                visible=True,
                type="filepath",
            )

        upload = gr.Button("生成图片")

        model = gr.Textbox(
            "SDXL",
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
            [text_input, image_upload, model, host, port],
            gr.Image(),
        )

        # app

    return app


if __name__ == "__main__":

    setup_2_img(
        test,
        "10.121.177.161",
        "8000",
    ).launch(
        inbrowser=False,
        server_name="0.0.0.0",
        server_port=9528,
    )
