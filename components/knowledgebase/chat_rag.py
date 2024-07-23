import json
import time
import copy
import requests

import gradio as gr


from openai import OpenAI
from requests import Response

from components.templates.template import template_factory

settings = None
with open("settings.json") as f:
    settings = json.loads(f.read())

# rag
proto = settings["rag"]["proto"]
api_host = settings["rag"]["api_host"]
api_port = settings["rag"]["api_port"]
api_server = f"{proto}://{api_host}:{api_port}"
# default_prompt_type = settings["rag"]["default_prompt_type"]

# openai
client = OpenAI(api_key="anystr", base_url=f"{api_server}/v1")


def clear_history():
    return [], []


def update_prompt_show(prompt):
    return template_factory[prompt], [], []


def get_server_models() -> Response:
    resp = requests.get(f"{api_server}/v1/models")
    if resp.status_code in [200, 201]:
        return resp.json()["data"]
    else:
        print(resp.text)
        raise


def chat_callback(
    message,
    history,
    llm_model: str,
    sys_prompt: str,
    history_conversations: int,
    max_tokens: int,
    presence_penalty: float,
    frequency_penalty: float,
    temperature: float,
    top_p: float,
    stream: bool,
    embedding_model: str,
):

    if message is None or message == "":
        # print(history + [("", "`检测到您的输入为空，请重新输入您的问题！`")])
        yield (
            None,
            history + [(None, "`检测到您的输入为空，请重新输入您的问题！`")],
            history,
        )
    else:
        # sys prompt
        ## 使用后端的 prompt 接口返回内容
        messages = [
            {"role": "system", "content": template_factory[sys_prompt]},
        ]
        # history
        if history_conversations != 0:
            for record in history[-history_conversations:]:
                if record[0] is None:
                    record[0] = ""
                if record[1] is None:
                    record[1] = ""
                messages.append({"role": "user", "content": record[0]})
                messages.append({"role": "assistant", "content": record[1]})

        # message
        messages.append({"role": "user", "content": message})

        print(messages)

        stream = bool(stream)
        start_time = time.time()
        resp = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            stream=stream,
            top_p=top_p,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
        )

        result = ""
        for chunk in resp:
            # TODO: finish_reason="length" 消息截断，设置提醒
            content = chunk.choices[0].delta.content
            if content:
                result += content
                yield None, history + [(message, result)], history

        end_time = time.time()
        elapse_time = round(end_time - start_time, 2)
        # history.append((message, result + f"`本次响应用时：{elapse_time}`"))
        resp_with_time = copy.deepcopy(history)
        resp_with_time.append((message, result + f"\n`本次响应用时：{elapse_time}`"))
        history.append((message, result))

        yield None, resp_with_time, history


def setup(
    enable_conf: bool = True,
):
    custom_css = """
        #custom-textbox textarea {
            resize: none;
        }
    """

    # update_server_prompt(prompt_type=default_prompt_type)
    with gr.Blocks(css=custom_css) as app:
        history = gr.State([])

        chatbot = gr.Chatbot(
            height=600,
            label="对话框",
            show_copy_button=True,
            bubble_full_width=False,
        )
        with gr.Row():
            chatbox = gr.Textbox(
                show_label=False,
                label="用户输入",
                placeholder="对话输入",
                scale=8,
                container=False,
                elem_id="custom-textbox",
            )

            submit_btn = gr.Button(
                "提交",
                scale=2,
            )

        clear_button = gr.Button("清除历史记录")

        with gr.Accordion("超参数"):
            options_prompt = list(template_factory.keys())
            sys_prompt = gr.Dropdown(
                options_prompt,
                value=options_prompt[0],
                label="LLM Model Prompt",
                visible=enable_conf,
            )
            sys_prompt_show = gr.Textbox(
                value=template_factory[options_prompt[0]],
                lines=1,
                max_lines=6,
                interactive=False,
                container=False,
                elem_id="custom-textbox",
            )
            extra_inputs = []
            llm_models = []
            embedding_models = []
            server_models = get_server_models()
            for server_model in server_models:
                if server_model["model_type"] == "LLM":
                    llm_models.append(server_model["id"])
                elif server_model["model_type"] == "embedding":
                    embedding_models.append(server_model["id"])
            llm_model = gr.Dropdown(
                llm_models,
                label="模型",
                value=llm_models[0],
                visible=enable_conf,
            )
            embedding_model = gr.Dropdown(
                embedding_models,
                label="嵌入模型",
                value=embedding_models[0],
                visible=enable_conf,
            )

            history_conversations = gr.Slider(
                0,
                10,
                value=5,
                step=1.0,
                label="保留历史对话次数",
                interactive=True,
                visible=enable_conf,
            )

            max_tokens = gr.Slider(
                20,
                2048,
                value=512,
                step=1.0,
                label="Maximum Tokens Length",
                interactive=True,
                visible=enable_conf,
            )

            presence_penalty = gr.Slider(
                -2.0,
                2.0,
                value=1.05,
                step=0.01,
                label="Presence Penalty",
                interactive=True,
                visible=enable_conf,
            )
            frequency_penalty = gr.Slider(
                -2.0,
                2.0,
                value=1.2,
                step=0.01,
                label="Frequency Penalty",
                interactive=True,
                visible=enable_conf,
            )

            temperature = gr.Slider(
                0.1,
                2,
                value=0.2,
                step=0.01,
                label="Temperature",
                interactive=True,
                visible=enable_conf,
            )

            top_p = gr.Slider(
                0.01,
                1,
                value=0.8,
                step=0.01,
                label="Top P",
                interactive=True,
                visible=enable_conf,
            )

            stream = gr.Textbox(
                True,
                label="Enable Stream",
                lines=1,
                max_lines=1,
                visible=False,
            )

            extra_inputs.append(llm_model)
            extra_inputs.append(sys_prompt)
            extra_inputs.append(history_conversations)
            extra_inputs.append(max_tokens)
            extra_inputs.append(presence_penalty)
            extra_inputs.append(frequency_penalty)
            extra_inputs.append(temperature)
            extra_inputs.append(top_p)
            extra_inputs.append(stream)
            extra_inputs.append(embedding_model)

            all_inputs = [chatbox, history]
            all_inputs.extend(extra_inputs)

            submit_btn.click(
                chat_callback,
                inputs=all_inputs,
                outputs=[chatbox, chatbot, history],
                # scroll_to_output=True,
            )

            clear_button.click(
                clear_history,
                inputs=[],
                outputs=[chatbot, history],
            )

            sys_prompt.change(
                update_prompt_show,
                inputs=[sys_prompt],
                outputs=[sys_prompt_show, chatbot, history],
            )
    return app


if __name__ == "__main__":
    app = setup()
    app.launch()
