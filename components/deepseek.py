import gradio as gr


def setup_deepseek(
    interface_func: object,
    config_enable: bool,
    api_host: str,
    api_port: str,
):
    chatbot = gr.Chatbot(height=450, label="对话框")

    chatbox = gr.Textbox(
        container=False,
        show_label=False,
        label="用户输入",
        placeholder="该模型能够进行代码协助编写。请输入您想实现的功能 ...",
        scale=7,
        autofocus=True,
    )

    max_new_tokens = gr.Slider(
        0,
        4096,
        value=1024,
        step=1.0,
        label="Maximum New Tokens Length",
        interactive=True,
        visible=config_enable,
    )

    top_p = gr.Slider(
        0,
        1,
        value=0.95,
        step=0.01,
        label="Top P",
        interactive=True,
        visible=config_enable,
    )

    top_k = gr.Slider(
        1,
        60,
        value=50,
        step=1,
        label="Top K",
        interactive=True,
        visible=config_enable,
    )

    model = gr.Textbox(
        "Deepseek-Model",
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

    # event list
    # model.select(model_on_select, None, outputs=system_prompt)

    # app
    deepseek_mainboard = gr.ChatInterface(
        interface_func,
        chatbot=chatbot,
        textbox=chatbox,
        retry_btn="重试",
        undo_btn="撤销",
        clear_btn="清除",
        submit_btn="提交",
        stop_btn="停止",
        additional_inputs=[
            model,
            max_new_tokens,
            top_p,
            top_k,
            host,
            port,
        ],
        additional_inputs_accordion="超参数",
    )

    return deepseek_mainboard
