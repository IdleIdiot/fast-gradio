import json

import gradio as gr


def debug():
    return "/tmp/debug_file_in_server"


def setup_resource_chart():
    with gr.Blocks() as app:

        show_button = gr.Button("history")

        file_exporter = gr.components.File(label="download")

        show_button.click(
            fn=debug,
            inputs=[],
            outputs=[
                file_exporter,
            ],
        )

    return app


if __name__ == "__main__":
    with open("settings.json") as f:
        settings = json.loads(f.read())
    app = setup_resource_chart()
    app.launch(
        share=True,
        inbrowser=False,
        server_name="0.0.0.0",
        server_port=9528,
        show_api=False,
        ssl_keyfile=settings["pages"]["ssl"]["key"],
        ssl_certfile=settings["pages"]["ssl"]["pem"],
        ssl_verify=False,
        debug=True,
    )
