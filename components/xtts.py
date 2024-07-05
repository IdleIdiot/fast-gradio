import gradio as gr

# import soundfile as sf
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts


# def inference(
#     message,
#     model_path: str = "/data/wanghui01/models/XTTS-v2/",
#     source_path: str = "",
# ):
#     output_path = "/tmp/gradio/output.wav"
#     config = XttsConfig()
#     config.load_json(f"{model_path}/config.json")
#     model = Xtts.init_from_config(config)
#     model.load_checkpoint(config, checkpoint_dir=model_path, eval=True)
#     model.cuda()

#     outputs = model.synthesize(
#         message,
#         config,
#         speaker_wav=source_path,
#         gpt_cond_len=3,
#         language="zh-cn",
#     )
#     outputs = outputs["wav"]

#     sample_rate = 22050  # 或者根据你的模型实际采样率进行调整

#     # 保存为 WAV 文件
#     sf.write(output_path, outputs, sample_rate)
#     return output_path


def clear(output):
    if output != None:
        return None, output
    return None, None


# def dispatcher(
#     message,
#     history,
#     model="",
#     system_prompt=None,
#     temperature=0.2,
#     max_new_tokens=512,
#     top_p=0.9,
#     top_k=40,
#     host="",
#     port="",
# ):
#     if system_prompt == None:
#         raise gr.Error("请先放入音源！")

#     output_path = inference(message, source_path=system_prompt)
#     return output_path


def setup_xtts(
    interface_func: object,
    api_host,
    api_port,
):

    with gr.Blocks() as app:
        source = gr.Audio(label="音源", type="filepath")

        with gr.Row():

            content = gr.Textbox(
                lines=2,
                max_lines=5,
                show_label=False,
                placeholder="放入音源文件后，在这里输入要转化的内容, 仅支持中文，暂不支持语种选择：",
                scale=5,
            )

            upload = gr.Button("文字转语音", scale=1)

        output = gr.Audio(
            label="音频输出", visible=True, show_label=True, interactive=False
        )

        model = gr.Textbox(
            "XTTS",
            label="Model",
            lines=1,
            max_lines=1,
            visible=False,
        )

        host = gr.Textbox(
            api_host,
            label="Api Host",
            lines=1,
            max_lines=1,
            visible=False,
        )

        port = gr.Textbox(
            api_port,
            label="Port",
            lines=1,
            max_lines=1,
            visible=False,
        )

        upload.click(
            interface_func,
            [content, output, model, source, host, port],
            [output],
        ).then(clear, output, [content, output])

    return app


# if __name__ == "__main__":
#     app = setup_xtts(dispatcher)
#     app.launch(
#         share=False,
#         server_port=9528,
#         server_name="0.0.0.0",
#         ssl_keyfile="../ssl/cert.key",
#         ssl_certfile="../ssl/cert.pem",
#         ssl_verify=False,
#         show_api=False,
#     )
