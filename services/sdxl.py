import gradio as gr
import requests


def inference(
    api_host,
    api_port,
    message,
    attach,
):
    if not message:
        raise gr.Error("请至少输入对图片的描述！")

    if attach:
        result = requests.get(
            f"http://{api_host}:{api_port}/api/v1/llm/text/to/image/sdxl",
            json={
                "message": message,
                "source_img": attach,
            },
            headers={"content-type": "application/json"},
        ).json()
    else:

        result = requests.get(
            f"http://{api_host}:{api_port}/api/v1/llm/text/to/image/sdxl",
            json={
                "message": message,
            },
            headers={"content-type": "application/json"},
        ).json()

    return result["dest_img"]
