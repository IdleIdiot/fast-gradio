import json
import requests

import gradio as gr


from openai import OpenAI
from typing import Dict

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


kb_header_mapping = {
    "No": "序号",
    "file_name": "文件名",
    "file_ext": "文件后缀",
    "create_time": "创建时间",
    "tag": "标签",
    "docs_count": "切分文档数量",
    "file_size": "文件大小",
    "document_loader": "文档加载器",
    "text_splitter": "文档分词器",
    "file_version": "文件版本",
    "in_folder": "本地文件存储",
    "in_db": "数据库存储",
    "custom_docs": "自定义文档",
}


# def update_prompt_show(prompt):
#     return template_factory[prompt], [], []


# def get_server_models() -> Dict:
#     resp = requests.get(f"{api_server}/v1/models")
#     if resp.status_code in [200, 201]:
#         return resp.json()["data"]
#     else:
#         print(resp.text)
#         raise


# def get_server_tools() -> Dict:
#     resp = requests.get(f"{api_server}/tools")
#     if resp.status_code in [200, 201]:
#         return resp.json()["data"]
#     else:
#         print(resp.text)
#         raise


def get_knowledge_base() -> Dict:
    resp = requests.get(f"{api_server}/knowledge_base/list_knowledge_bases")
    if resp.status_code in [200, 201]:
        return resp.json()["data"]
    else:
        print(resp.text)
        raise


def get_kb_files(kb_name) -> Dict:
    resp = requests.get(
        f"{api_server}/knowledge_base/list_files",
        params={"knowledge_base_name": kb_name},
    )
    if resp.status_code in [200, 201]:
        return resp.json()["data"]
    else:
        print(resp.text)
        raise


def list_data_frame(
    kb_name,
    number_condition=None,
    file_condition=None,
    tag_condition=None,
):
    total_file = []
    kb_file_list = get_kb_files(kb_name)
    headers = list(kb_header_mapping.values())
    for kb_file_meta in kb_file_list:
        row = []
        try:
            for k, _ in kb_header_mapping.items():
                if k not in kb_file_meta.keys():
                    kb_file_meta[k] = ""
                row.append(kb_file_meta[k])
            if number_condition and int(number_condition) != int(kb_file_meta["No"]):
                continue
            if file_condition and file_condition not in kb_file_meta["file_name"]:
                continue
            if tag_condition and tag_condition != kb_file_meta["tag"]:
                continue
            total_file.append(row)
        except Exception as e:
            print(kb_file_meta)
    return gr.Dataframe(
        value=total_file,
        headers=headers,
        interactive=False,
    )


def filter_data(kb_name, number_condition, file_condition, tag_condition):
    return list_data_frame(kb_name, number_condition, file_condition, tag_condition)


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

        with gr.Row():
            number_condition = gr.Textbox(
                placeholder="请输入文件编号（精准）",
                label="编号",
                max_lines=1,
                visible=False,
            )

            file_condition = gr.Textbox(
                placeholder="请输入文件名称（模糊）",
                label="文件名",
                max_lines=1,
            )

            tag_condition = gr.Textbox(
                placeholder="请输入文件标签(精准)",
                max_lines=1,
                label="文件标签",
            )
            search_btn = gr.Button("搜索")

        data_frame = list_data_frame(default_kb)

        search_btn.click(
            filter_data,
            [current_kb, number_condition, file_condition, tag_condition],
            [data_frame],
        )

        # upload_file.upload(reset_tips, [], [tips_textbox])

    return app


if __name__ == "__main__":
    app = setup()
    app.launch(
        share=True,
        inbrowser=False,
        server_name="0.0.0.0",
        show_api=False,
    )
