import re
import os
import json
import time
import copy
import requests

import gradio as gr

from typing import Dict
from pathlib import Path

from openai import OpenAI

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


def get_knowledge_base() -> Dict:
    resp = requests.get(f"{api_server}/knowledge_base/list_knowledge_bases")
    if resp.status_code in [200, 201]:
        return resp.json()["data"]
    else:
        print(resp.text)
        raise


def upload_file_to_kb(
    kb_name,
    tag,
    files,
    override,
    zh_title_enhance,
    chunk_size,
    chunk_overlap,
):
    def convert_file(file):
        file = Path(file).absolute().open("rb")
        filename = os.path.split(file.name)[-1]
        return filename, file

    files = [convert_file(file) for file in files]
    print(type(files))
    print(files)

    data = {
        "knowledge_base_name": kb_name,
        "tag": tag,
        "override": override,
        "to_vector_store": True,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "zh_title_enhance": zh_title_enhance,
        "docs": None,
        "not_refresh_vs_cache": False,
    }

    response = requests.post(
        f"{api_server}/knowledge_base/upload_docs",
        data=data,
        files=[("files", (filename, file)) for filename, file in files],
    )

    print(response.status_code)
    return None


def setup(
    enable_conf: bool = True,
):
    # update_server_prompt(prompt_type=default_prompt_type)

    total_kb = []
    knowledge_base_list = get_knowledge_base()
    for knowledge_base in knowledge_base_list:
        total_kb.append(knowledge_base["kb_name"])

    default_kb = total_kb[0]

    with gr.Blocks() as app:

        current_kb = gr.Dropdown(
            total_kb,
            value=default_kb,
            label="知识库",
        )

        upload_file = gr.File(file_count="multiple", label=False)

        upload_kb_btn = gr.Button("上传至知识库", scale=4)

        with gr.Accordion("超参数"):
            extra_inputs = []
            tag = gr.Textbox(
                label="标签",
                placeholder="为文件标记标签",
                max_lines=1,
            )
            override = gr.Dropdown(
                [False, True],
                label="覆盖已有文件",
                value=False,
                visible=enable_conf,
            )
            zh_title_enhance = gr.Dropdown(
                [False, True],
                label="是否开启中文标题加强",
                value=False,
                visible=enable_conf,
            )

            chunk_size = gr.Slider(
                20,
                2048,
                value=256,
                step=1.0,
                label="知识库中单段文本最大长度",
                interactive=True,
                visible=enable_conf,
            )

            chunk_overlap = gr.Slider(
                20,
                128,
                value=64,
                step=1.0,
                label="知识库中相邻文本重合长度",
                interactive=True,
                visible=enable_conf,
            )

            extra_inputs.append(override)
            extra_inputs.append(zh_title_enhance)
            extra_inputs.append(chunk_size)
            extra_inputs.append(chunk_overlap)

        all_inputs = [current_kb, tag, upload_file]
        all_inputs.extend(extra_inputs)

        upload_kb_btn.click(
            upload_file_to_kb,
            all_inputs,
            [upload_file],
        )

    return app


if __name__ == "__main__":
    app = setup()
    app.launch(
        share=True,
        inbrowser=False,
        server_name="0.0.0.0",
        show_api=False,
    )
