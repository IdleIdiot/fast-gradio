import requests


def inference(
    api_host,
    api_port,
    image_path: str = "",
    max_new_tokens=80,
):
    result = requests.get(
        f"http://{api_host}:{api_port}/api/v1/llm/image/to/text/blip",
        json={
            "source_path": image_path,
            "max_new_tokens": max_new_tokens,
        },
        headers={"content-type": "application/json"},
    ).json()
    return result["message"]
