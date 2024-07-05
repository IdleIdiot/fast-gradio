import json
import requests


def inference(
    message,
    max_new_tokens,
    top_p,
    top_k,
    api_host,
    api_port,
):
    begin = False
    with requests.get(
        # f"http://{api_host}:{api_port}/model/deepseek",
        f"http://{api_host}:{api_port}/api/v1/llm/chat/stream/deepseek",
        json={
            "message": message,
            "max_new_tokens": max_new_tokens,
            "top_p": top_p,
            "top_k": top_k,
        },
        stream=True,
        headers={"content-type": "application/json"},
    ) as response:
        # try:
        #     response.raise_for_status()

        #     for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
        #         if "result" in chunk:
        #             if "begin▁of▁sentence" in chunk:
        #                 begin = True
        #                 continue

        #             if begin:
        #                 result = json.loads(chunk.split(":", maxsplit=1)[1].strip())[
        #                     "result"
        #                 ]
        #                 if result:
        #                     if "<|EOT|>" != result.strip():
        #                         yield result

        #         else:
        #             pass
        # except requests.exceptions.HTTPError as e:
        #     print(e)
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
            print(e)


if __name__ == "__main__":
    inference(
        '''优化如下代码：location_value = ""
name_value = ""
manu_value = ""
sn_value = ""
model_value = ""
rev_value = ""
max_value = ""
status_value = ""
plug_value = ""''',
        512,
        0.95,
        50,
        "10.121.177.161",
        "8000",
    )
