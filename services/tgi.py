import json
import requests


def _post_http_request(
    api_url: str,
    inputs: str,
    top_p: float = 0.9,
    top_k: int = 40,
    temperature: float = 0.2,
    max_new_tokens: int = 512,
):
    """
    Base on TGI inference.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        "inputs": inputs,
        "parameters": {
            "top_p": top_p,
            "top_k": top_k,
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
        },
    }
    try:
        print(api_url)
        print(payload)
        resp = requests.post(api_url, headers=headers, json=payload, stream=True)
        resp.raise_for_status()

        for chunk in resp.iter_lines():
            # 忽略可能存在的空行
            if chunk:
                chunk = chunk.decode("utf-8").split(":", maxsplit=1)[1]
                chunk = json.loads(chunk)
                print(f"DEBUG: {chunk}")
                if "error" in chunk:
                    yield chunk["error"]
                    break

                chunk = chunk["token"]
                if chunk["special"]:
                    print(f"SKIP: {chunk}")
                    break
                yield chunk
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")


def chat_with_tgi(
    message,
    temperature,
    max_new_tokens,
    top_p,
    top_k,
    host,
    port,
):
    api_url = f"http://{host}:{port}/generate_stream"
    tokens_stream = _post_http_request(
        api_url,
        message,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        top_p=top_p,
        top_k=top_k,
    )

    for next_token in tokens_stream:
        if "text" in next_token:
            yield next_token["text"]
        elif type(next_token) == str:
            yield next_token
