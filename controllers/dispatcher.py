import gradio as gr
from templates import template
from services import tgi, blip, xtts, deepseek, sdxl, llama3, qwen


# *args 不同模型传进来的参数名称相似而不相同
def dispatcher(
    message,
    history,
    model="",
    *args,
    # system_prompt=None,
    # temperature=0.2,
    # max_new_tokens=512,
    # top_p=0.9,
    # top_k=40,
    # host="",
    # port="",
):
    # if not message.endswith("</s>"):
    #     message = system_prompt + message + "</s><s>"
    response = ""
    if model == "DISC-Model":
        ## 不确定多轮对话Prompt
        # if len(history) < 3:
        #     history_fmt = "".join(
        #         ["<s>" + q + "</s></INST>" + a + "<INST>" for q, a in history]
        #     )
        # else:
        #     history_fmt = "".join(
        #         [q + "</INST>" + a + "<INST>" for q, a in history[-2:]]
        #     )
        # message = history_fmt + message
        system_prompt = args[0]
        temperature = args[1]
        max_new_tokens = args[2]
        top_p = args[3]
        top_k = args[4]
        host = args[5]
        port = args[6]

        message = template.DISC_SYSPROMPT_TEMPLATE.replace(
            "system_prompt", system_prompt
        ).replace("message", message)
        # print(message)
        # message = LLAMA2_SYSPROMPT.replace("system_prompt", system_prompt).replace(
        #     "message", message
        # )
        next_tokens = tgi.chat_with_tgi(
            message,
            temperature,
            max_new_tokens,
            top_p,
            top_k,
            host,
            port,
        )
        try:
            while next_token := next(next_tokens):
                response += next_token
                yield response
        except StopIteration:
            if response == "":
                yield "我暂时无法回答问题"

    elif model == "LLaMa2":
        system_prompt = args[0]
        temperature = args[1]
        max_new_tokens = args[2]
        top_p = args[3]
        top_k = args[4]
        host = args[5]
        port = args[6]

        if len(history) < 3:
            history_fmt = "".join(
                [q + "[/INST]" + a + "</s><s><INST>" for q, a in history]
            )
        else:
            history_fmt = "".join(
                [q + "[/INST]" + a + "</s><s><INST>" for q, a in history[-2:]]
            )
        message = history_fmt + message
        message = template.LLAMA2_SYSPROMPT_TEMPLATE.replace(
            "system_prompt", system_prompt
        ).replace("message", message)
        next_tokens = tgi.chat_with_tgi(
            message,
            temperature,
            max_new_tokens,
            top_p,
            top_k,
            host,
            port,
        )
        try:
            while next_token := next(next_tokens):
                response += next_token
                yield response
        except StopIteration:
            if response == "":
                yield "我暂时无法回答问题"

    elif model == "Deepseek-Model":
        # message = LLAMA2_SYSPROMPT.replace("system_prompt", system_prompt).replace(
        #     "message", message
        # )
        max_new_tokens = args[0]
        top_p = args[1]
        top_k = args[2]
        host = args[3]
        port = args[4]

        next_tokens = deepseek.inference(
            message, max_new_tokens, top_p, top_k, host, port
        )
        try:
            while next_token := next(next_tokens):
                response += next_token
                yield response
        except StopIteration:
            if response == "":
                yield "我暂时无法回答问题"

    elif model == "BLIP":
        api_host = args[0]
        api_port = args[1]
        output = blip.inference(
            api_host,
            api_port,
            image_path=message,
        )

        history.append(
            (
                (message,),
                output,
            )
        )
        yield None, history

    elif model == "XTTS":
        audio_source = args[0]
        api_host = args[1]
        api_port = args[2]
        if audio_source == None:
            raise gr.Error("请先放入音源！")

        if message == "":
            raise gr.Error("文字内容不能为空！")

        output_path = xtts.inference(
            api_host,
            api_port,
            message,
            source_path=audio_source,
        )
        yield output_path

    elif model == "SDXL":
        api_host = args[0]
        api_port = args[1]
        output_path = sdxl.inference(
            api_host,
            api_port,
            message=message,
            attach=history,
        )

        yield output_path

    elif model == "LLaMa3":
        system_prompt = args[0]
        temperature = args[1]
        max_new_tokens = args[2]
        top_p = args[3]
        top_k = args[4]
        host = args[5]
        port = args[6]

        next_tokens = llama3.inference(
            message,
            system_prompt,
            temperature,
            max_new_tokens,
            top_p,
            top_k,
            host,
            port,
        )
        try:
            while next_token := next(next_tokens):
                response += next_token
                yield response
        except StopIteration:
            if response == "":
                yield "我暂时无法回答问题"

    elif model == "Qwen":
        system_prompt = args[0]
        temperature = args[1]
        max_new_tokens = args[2]
        top_p = args[3]
        top_k = args[4]
        host = args[5]
        port = args[6]

        next_tokens = qwen.inference(
            message,
            system_prompt,
            temperature,
            max_new_tokens,
            top_p,
            top_k,
            host,
            port,
        )
        try:
            while next_token := next(next_tokens):
                response += next_token
                yield response
        except StopIteration:
            if response == "":
                yield "我暂时无法回答问题"
