import json
import gradio as gr

from components.charts import resource
from components.knowledgebase import chat_rag

settings = None
with open("settings.json") as f:
    settings = json.loads(f.read())


def setup():
    website = []
    labels = []
    for next_deploy in settings["pages"]["deployment"]:
        if next_deploy == "monitor":
            website.append(resource.setup_resource_chart())
            labels.append("资源监控")
            continue

        # elif next_deploy == "knownledge":
        #     website.append(knownledge.setup_knownledge())
        #     labels.append("知识库管理")
        #     continue
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
