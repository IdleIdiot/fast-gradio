import gradio as gr


def setup_qwen(
    system_prompt: str,
    config_enable: bool,
    api_host: str,
    api_port: str,
    interface_func: object,
):
    chatbot = gr.Chatbot(height=450, label="对话框")

    chatbox = gr.Textbox(
        container=False,
        show_label=False,
        label="用户输入",
        placeholder="对话输入",
        scale=7,
        autofocus=True,
    )

    # model = gr.Dropdown(
    #     ["DISC-Model", "Baichuan2-13B", "LLaMa2", "THTF-Model", "ChatGLM3"],
    #     value="DISC-Model",
    #     label="Text Generation Model",
    # )

    system_prompt = gr.Textbox(
        system_prompt,
        label="System Prompt",
        lines=3,
        max_lines=20,
        visible=config_enable,
    )

    max_new_tokens = gr.Slider(
        0,
        2048,
        value=1024,
        step=1.0,
        label="Maximum New Tokens Length",
        interactive=True,
        visible=config_enable,
    )

    top_p = gr.Slider(
        0,
        1,
        value=0.9,
        step=0.01,
        label="Top P",
        interactive=True,
        visible=config_enable,
    )

    temperature = gr.Slider(
        0,
        1,
        value=0.2,
        step=0.01,
        label="Temperature",
        interactive=True,
        visible=config_enable,
    )

    top_k = gr.Slider(
        1,
        40,
        value=40,
        step=1,
        label="Top K",
        interactive=True,
        visible=config_enable,
    )

    model = gr.Textbox(
        "Qwen",
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
    qwen_mainboard = gr.ChatInterface(
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
            system_prompt,
            temperature,
            max_new_tokens,
            top_p,
            top_k,
            host,
            port,
        ],
        additional_inputs_accordion="超参数",
    )
    return qwen_mainboard
