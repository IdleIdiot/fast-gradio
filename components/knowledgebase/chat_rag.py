import re
import json
import time
import copy
import requests

import gradio as gr


from openai import OpenAI
from requests import Response
from typing import Dict
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
client = OpenAI(api_key="anystr", base_url=f"{api_server}/thtf")


permit_tools = [
    "calculate",
    "search_local_knowledgebase",
    "weather_check",
    "gitlab_projects",
]


def clear_history():
    return [], []


def update_prompt_show(prompt):
    return template_factory[prompt], [], []


def get_server_models() -> Dict:
    resp = requests.get(f"{api_server}/v1/models")
    if resp.status_code in [200, 201]:
        return resp.json()["data"]
    else:
        print(resp.text)
        raise


def get_server_tools() -> Dict:
    resp = requests.get(f"{api_server}/tools")
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
    is_tools_enable: bool,
    tools_choice: list,
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
        # tmp

        result = ""

        if bool(is_tools_enable):
            tools_filter = {}
            tools = get_server_tools()
            for k, v in tools.items():
                if v["title"] in tools_choice:
                    tools_filter.update({k: v})

            resp = client.chat.completions.create(
                model=llm_model,
                messages=messages,
                stream=stream,
                top_p=top_p,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                max_tokens=max_tokens,
                tools=tools_filter,
            )
            for chunk in resp:
                # TODO: finish_reason="length" 消息截断，设置提醒
                content = chunk.choices[0].delta.content
                if (
                    content
                    and not content.startswith("Thought")
                    and "Final Answer" in content
                ):
                    print(content)
                    content = re.match(".*Final Answer: (.*)", content, re.S).group(1)
                    for c in content:
                        result += c
                        time.sleep(0.005)
                        yield None, history + [(message, result)], history
                    if not result:
                        yield None, history + [
                            (message, "```接口平台未返回信息！```")
                        ], history
                    else:
                        yield None, history + [
                            (
                                message,
                                result := result + "\n`本次回答根据知识库资料生成`",
                            )
                        ], history

                else:
                    if content and not result and not content.startswith("Thought"):
                        for c in content:
                            result += c
                            time.sleep(0.01)
                            yield None, history + [(message, result)], history
        else:
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

            for chunk in resp:
                # TODO: finish_reason="length" 消息截断，设置提醒
                content = chunk.choices[0].delta.content
                if content:
                    result += content
                    yield None, history + [(message, result)], history
                if not result:
                    yield None, history + [
                        (message, "```接口平台未返回信息！```")
                    ], history

        end_time = time.time()
        elapse_time = round(end_time - start_time, 2)
        # history.append((message, result + f"`本次响应用时：{elapse_time}`"))
        resp_with_time = copy.deepcopy(history)
        resp_with_time.append((message, result + f"\n`响应用时：{elapse_time}`"))
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

    # python写前端，知道javascript语言怎么写，都不知道怎么往里加 淦
    custom_js = """
    function handleKeyboardEvent(e) {
        console.log('User pressed:', e.key);
        if (e.key === 'Enter') { // 示例：当用户按下回车键时执行某些操作
            document.getElementById("commit_btn").click();
        }
    }

    document.addEventListener('keydown', handleKeyboardEvent);
    """

    # update_server_prompt(prompt_type=default_prompt_type)
    with gr.Blocks(
        css=custom_css,
        # js=custom_js,
    ) as app:
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
                placeholder="对话输入（shift+enter换行）",
                scale=8,
                container=False,
                elem_id="custom-textbox",
                autofocus=True,
            )

            submit_btn = gr.Button(
                "提交",
                scale=2,
                elem_id="commit_btn",
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
            # embedding_model = gr.Dropdown(
            #     embedding_models,
            #     label="嵌入模型",
            #     value=embedding_models[0],
            #     visible=enable_conf,
            # )
            is_tools_enable = gr.Dropdown(
                [False, True],
                value=False,
                label="是否让模型使用工具",
                visible=enable_conf,
            )
            tools = get_server_tools()
            tools_can_be_used = []
            for k, v in tools.items():
                if k in permit_tools:
                    tools_can_be_used.append(v["title"])

            tools_choice = gr.Dropdown(
                tools_can_be_used,
                value=tools_can_be_used,
                multiselect=True,
                max_choices=5,
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
            extra_inputs.append(is_tools_enable)
            extra_inputs.append(tools_choice)
            # extra_inputs.append(embedding_model)

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
    app.launch(
        share=True,
        inbrowser=False,
        server_name="0.0.0.0",
        show_api=False,
        server_port=7866,
    )
