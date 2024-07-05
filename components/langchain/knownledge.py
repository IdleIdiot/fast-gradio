import gradio as gr


def clear(output):
    if output != None:
        return None, output
    return None, None


def upload_file_to_vec(files: str):
    for file_ in files:
        print(file_)


def setup_knownledge():

    with gr.Blocks() as app:
        with gr.Row():
            gr.Textbox(
                placeholder="输入知识库名称",
                container=False,
                show_label=False,
                scale=6,
                max_lines=1,
            )
            create_bt = gr.Button(value="新建知识库", scale=1)
        gr.Markdown("---")
        with gr.Row():
            collection = gr.Dropdown(
                label="知识库",
                choices=["知识库测试一", "知识库测试二", "知识库测试三"],
                scale=12,
            )
            with gr.Column():
                index_bt = gr.Button(value="查看知识库")

                delete_bt = gr.Button(value="删除知识库")
        files = gr.Files(label="上传文档至知识库")
        upload = gr.Button(value="上传")

        upload.click(
            upload_file_to_vec,
            [files],
            None,
        )

    return app


if __name__ == "__main__":
    app = setup_knownledge()
    app.launch(
        share=False,
        server_port=9528,
        server_name="0.0.0.0",
        show_api=False,
    )
