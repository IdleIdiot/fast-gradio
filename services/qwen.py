import json
import requests


def inference(
    message,
    system_prompt,
    temperature,
    max_new_tokens,
    top_p,
    top_k,
    api_host,
    api_port,
):

    with requests.get(
        # f"http://{api_host}:{api_port}/model/qwen",
        f"http://{api_host}:{api_port}/api/v1/llm/chat/stream/qwen",
        json={
            "message": message,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "top_p": top_p,
            "top_k": top_k,
        },
        stream=True,
        headers={"content-type": "application/json"},
    ) as response:
        try:
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                if "result" in chunk:
                    result = json.loads(chunk.split(":", maxsplit=1)[1].strip())[
                        "result"
                    ]
                    if result:
                        yield result

                else:
                    pass
        except requests.exceptions.HTTPError as e:
            raise e


if __name__ == "__main__":
    inference(
        message="Hello.",
        system_prompt="You are a helpful assistent.",
        temperature=1.0,
        max_new_tokens=512,
        top_p=0.9,
        top_k=5,
        api_host="10.121.177.161",
        api_port=8000,
    )
