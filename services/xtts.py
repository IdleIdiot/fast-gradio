import requests


def inference(
    api_host,
    api_port,
    message,
    source_path: str = "",
):
    result = requests.get(
        f"http://{api_host}:{api_port}/api/v1/llm/audio/to/audio/xtts",
        json={
            "message": message,
            "source_path": source_path,
        },
        headers={"content-type": "application/json"},
    ).json()

    return result["dest_path"]
