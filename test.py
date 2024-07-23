import requests

base_url = "http://10.121.177.161:7865/v1"
data = {
    "model": "qwen1.5-14B-chat-awq-rag",
    "messages": [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，我是人工智能大模型"},
        {"role": "user", "content": "写一个长篇小说"},
    ],
    "stream": True,
    "temperature": 0.7,
}


data = {
    "model": "qwen2-instruct",
    "messages": [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，我是人工智能大模型"},
        {"role": "user", "content": "如何高质量提问？"},
    ],
    "stream": True,
    "temperature": 0.7,
    "extra_body": {
        "top_k": 3,
        "score_threshold": 2.0,
        "return_direct": True,
    },
}

a = [1, 2, 4]
b = [2, 4, 5]
a.extend(b)
print(a)
# response = requests.post(f"{base_url}/chat/completions", json=data, stream=True)
# for line in response.iter_content(None, decode_unicode=True):
#     print(line, end="", flush=True)
