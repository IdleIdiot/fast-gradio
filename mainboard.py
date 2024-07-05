import json
import gradio as gr

from templates import template
from controllers.dispatcher import dispatcher

from components.charts import resource
from components.langchain import knownledge
from components import (
    blip,
    deepseek,
    disc,
    llama2,
    xtts,
    sdxl,
    llama3,
    qwen,
)


settings = None
with open("settings.json") as f:
    settings = json.loads(f.read())


def setup():
    website = []
    labels = []
    for next_deploy in settings["pages"]["deployment"]:
        if next_deploy == "llama2":
            website.append(
                llama2.setup_llama2(
                    system_prompt=template.DEFAULT_LLAMA_SYS,
                    config_enable=settings["pages"]["show_params"],
                    api_host=settings["models"]["llama2"]["api_host"],
                    api_port=settings["models"]["llama2"]["api_port"],
                    interface_func=dispatcher,
                )
            )
        elif next_deploy == "disc":
            website.append(
                disc.setup_disc(
                    system_prompt=template.DEFAULT_DISC_SYS,
                    config_enable=settings["pages"]["show_params"],
                    api_host=settings["models"]["disc"]["api_host"],
                    api_port=settings["models"]["disc"]["api_port"],
                    interface_func=dispatcher,
                )
            )
        elif next_deploy == "blip":
            website.append(
                blip.setup_img2text(
                    interface_func=dispatcher,
                    api_host=settings["models"]["blip"]["api_host"],
                    api_port=settings["models"]["blip"]["api_port"],
                )
            )
        elif next_deploy == "xtts":
            website.append(
                xtts.setup_xtts(
                    interface_func=dispatcher,
                    api_host=settings["models"]["xtts"]["api_host"],
                    api_port=settings["models"]["xtts"]["api_port"],
                )
            )
        elif next_deploy == "deepseek":
            website.append(
                deepseek.setup_deepseek(
                    interface_func=dispatcher,
                    config_enable=settings["pages"]["show_params"],
                    api_host=settings["models"]["deepseek"]["api_host"],
                    api_port=settings["models"]["deepseek"]["api_port"],
                )
            )
        elif next_deploy == "sdxl":
            website.append(
                sdxl.setup_2_img(
                    interface_func=dispatcher,
                    api_host=settings["models"]["sdxl"]["api_host"],
                    api_port=settings["models"]["sdxl"]["api_port"],
                )
            )
        elif next_deploy == "llama3":
            website.append(
                llama3.setup_llama3(
                    system_prompt=template.DEFAULT_LLAMA_SYS,
                    config_enable=settings["pages"]["show_params"],
                    api_host=settings["models"]["llama3"]["api_host"],
                    api_port=settings["models"]["llama3"]["api_port"],
                    interface_func=dispatcher,
                )
            )
        elif next_deploy == "qwen":
            website.append(
                qwen.setup_qwen(
                    system_prompt=template.DEFAULT_QWEN_SYS,
                    config_enable=settings["pages"]["show_params"],
                    api_host=settings["models"]["qwen"]["api_host"],
                    api_port=settings["models"]["qwen"]["api_port"],
                    interface_func=dispatcher,
                )
            )
        elif next_deploy == "monitor":
            website.append(resource.setup_resource_chart())
            labels.append("资源监控")
            continue

        elif next_deploy == "knownledge":
            website.append(knownledge.setup_knownledge())
            labels.append("知识库管理")
            continue

        else:
            continue

        labels.append(settings["models"][next_deploy]["title"])

    return gr.TabbedInterface(
        website,
        labels,
        css="footer {visibility: hidden}",
        # title="test",
        # js=js_btn,
    )


if __name__ == "__main__":
    app = setup()
    app.title = settings["pages"]["application"]
    app.launch(
        share=True,
        inbrowser=False,
        server_name="0.0.0.0",
        server_port=settings["pages"]["port"],
        show_api=False,
        ssl_keyfile=settings["pages"]["ssl"]["key"],
        ssl_certfile=settings["pages"]["ssl"]["pem"],
        ssl_verify=False,
        favicon_path=settings["pages"]["icon"],
    )
