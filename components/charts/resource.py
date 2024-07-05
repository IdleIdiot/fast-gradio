import time
import json
import random
import warnings

import numpy as np
import pandas as pd
import gradio as gr

import matplotlib.pyplot as plt

from datetime import datetime, timedelta

from elasticsearch import Elasticsearch, ElasticsearchWarning
from matplotlib.dates import DateFormatter, SecondLocator, MinuteLocator


settings = None
with open("settings.json") as f:
    settings = json.loads(f.read())

es = Elasticsearch(settings["database"]["elk"]["url"])
warnings.filterwarnings("ignore", category=ElasticsearchWarning)


# def auto_refresh_plt():
#     end_time = datetime.now()
#     start_time = end_time - timedelta(minutes=10)
#     start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
#     end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
#     agent_times, all_exists_resource_info = get_resource_data_by_es(
#         "10.121.177.161", start_time, end_time
#     )

#     plt = painter(agent_times, all_exists_resource_info)

#     return plt.gcf()


# 假设这是你的数据获取方法
def get_resource_data_by_es(ip_address, start_time, end_time):
    # 初始化Elasticsearch客户端
    all_exists_resource_info = {}
    # 设置查询参数
    index_name = "resource"

    # 构建查询语句
    query = {
        "sort": [
            "agent_time",
        ],
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "host_id": ip_address,
                        }
                    },
                    {
                        "match": {
                            "item_id": 0,
                        }
                    },
                    {
                        "range": {
                            "agent_time": {
                                "gte": start_time,
                                "lt": end_time,
                            }
                        }
                    },
                ]
            }
        },
    }

    query["query"]["bool"]["must"][1]["match"]["item_id"] = "1001"
    results = es.search(index=index_name, body=query)["hits"]["hits"]
    agent_times = [result["_source"]["agent_time"] for result in results]

    for item_id in range(1001, 1010):
        # 执行查询
        query["query"]["bool"]["must"][1]["match"]["item_id"] = item_id
        results = es.search(index=index_name, body=query)["hits"]["hits"]
        if results:
            for result in results:
                resource_info = result["_source"]
                if resource_info["alias"] not in all_exists_resource_info.keys():
                    all_exists_resource_info[resource_info["alias"]] = []
                all_exists_resource_info[resource_info["alias"]].append(
                    resource_info["value1"]
                )

    for item_id in range(2001, 2050):
        # 执行查询
        query["query"]["bool"]["must"][1]["match"]["item_id"] = item_id
        results = es.search(index=index_name, body=query)["hits"]["hits"]
        if results:
            for result in results:
                resource_info = result["_source"]
                if resource_info["alias"] not in all_exists_resource_info.keys():
                    all_exists_resource_info[resource_info["alias"]] = []
                all_exists_resource_info[resource_info["alias"]].append(
                    resource_info["value1"]
                )

    # print(f"DEBUG: {agent_times} , {all_exists_resource_info}")
    if not agent_times:
        raise gr.Error("指定IP未部署代理程序！")

    agent_times = pd.to_datetime(agent_times)
    # agent_times_sorted = np.sort(agent_times)
    return agent_times, all_exists_resource_info


def painter(agent_times, all_exists_resource_info, by=[1, 0, 0]):

    # 设置绘制图标大小
    plt.figure(figsize=(32, 18))

    # 设置x轴日期格式

    if by[0] == 1:
        plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
        plt.gca().xaxis.set_major_locator(SecondLocator(bysecond=range(0, 60, 30)))
    elif by[1] == 1:
        plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M"))
        plt.gca().xaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 2)))
    elif by[2] == 1:
        plt.gca().xaxis.set_major_formatter(DateFormatter("%H:%M"))
        plt.gca().xaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 20)))
    plt.xlim(agent_times[0], agent_times[-1])
    # x轴自动旋转日期标记
    plt.gcf().autofmt_xdate()
    plt.xticks(fontsize=16)

    # 绘制
    number_of_resource = 0
    last_style = ":"
    style_choices = ["-", "--"]
    for k, v in all_exists_resource_info.items():
        # if point:
        #     plt.plot(agent_times, v, "-o", label=k)
        # else:

        linestyle = random.choice(style_choices)
        style_choices.remove(linestyle)
        style_choices.append(last_style)
        last_style = linestyle

        if linestyle == "--":
            linewidth = 3.5
        elif linestyle == ":":
            linewidth = 5
        else:
            linewidth = 2
        plt.plot(agent_times, v, label=k, linestyle=linestyle, linewidth=linewidth)
        number_of_resource += 1

    # y轴
    plt.yticks(
        [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"],
        fontsize=20,
    )
    plt.ylim(-5, 100 + number_of_resource * 4)

    # 添加图例
    plt.legend(loc=2, fontsize=16)
    return plt


def write_to_excel(
    agent_times,
    all_exists_resource_info,
):
    cache = {}
    timestamp = str(time.time()).replace(".", "")
    tmp_file_path = f"/tmp/result-{timestamp}.xlsx"
    cache["agent_time"] = agent_times
    for item_k, item_v in all_exists_resource_info.items():
        cache[item_k] = item_v

    data = pd.DataFrame(cache)
    data.to_excel(tmp_file_path, sheet_name="监控数据", index=False)
    return tmp_file_path


# 创建一个函数来更新图表
def update_plot(sys_ip, end_delta, start_delta, item_selected):

    if not sys_ip:
        raise gr.Error("请先指定要查询的系统IP！")

    if start_delta <= end_delta:
        raise gr.Error("监控结束时间过早，请设置结束时间晚于开始时间！")

    # 获取当前时间
    end_time = datetime.now() - timedelta(minutes=end_delta)
    start_time = datetime.now() - timedelta(minutes=start_delta)
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    min_delta = start_delta - end_delta

    agent_times, all_exists_resource_info = get_resource_data_by_es(
        sys_ip, start_time, end_time
    )

    # 筛选条件，保存所有已监控的项
    all_choices = [key for key, _ in all_exists_resource_info.items()]

    # 根据已选择的监控项，有选择的展示视图
    if item_selected:
        new_seleced = item_selected
        wait_to_delete = [
            key for key, _ in all_exists_resource_info.items() if key not in new_seleced
        ]
        for resource in wait_to_delete:
            del all_exists_resource_info[resource]

    else:
        new_seleced = list(all_exists_resource_info.keys())[0]
        wait_to_delete = [
            key for key, _ in all_exists_resource_info.items() if key not in new_seleced
        ]
        for resource in wait_to_delete:
            del all_exists_resource_info[resource]

    try:
        tmp_file_path = write_to_excel(agent_times, all_exists_resource_info)

        # agent_times = [cpu_value["agent_time"] for cpu_value in cpu_values]

        if min_delta <= 10:
            plt = painter(agent_times, all_exists_resource_info, by=[1, 0, 0])
        elif min_delta <= 90:
            plt = painter(agent_times, all_exists_resource_info, by=[0, 1, 0])
        else:
            plt = painter(agent_times, all_exists_resource_info, by=[0, 0, 1])
    except ValueError as ve:
        raise gr.Error("数据过大，返回数据内容检查不一致，请重试！")

    return (
        gr.update(choices=all_choices, value=new_seleced),
        plt.gcf(),
        tmp_file_path,
    )  # 返回当前的figure对象


def clean_last_selected(item_selected):
    if item_selected:
        return gr.update(choices=[], value=[])


# 使用Gradio Blocks构建应用
def setup_resource_chart():
    with gr.Blocks(
        css="footer {visibility: hidden}",
    ) as app:

        sys_ip = gr.Textbox(
            placeholder="输入查询的IP地址，需要先部署代理程序：",
            show_label=True,
            value="10.121.177.161",
            max_lines=1,
            label="服务器 IP",
        )

        gr.Markdown(
            value="[代理程序](http://10.121.176.191:8280/automation/sys-agent)",
            show_label=False,
        )

        end_delta = gr.Slider(
            minimum=0,
            maximum=720,
            value=0,
            step=1,
            label="监控结束时间偏移量(分钟)",
        )

        start_delta = gr.Slider(
            minimum=1,
            maximum=720,
            value=5,
            step=1,
            label="监控开始时间偏移量(分钟)",
        )

        item_selected = gr.Dropdown(
            choices=[],
            label="监控项",
            multiselect=True,
            interactive=True,
            allow_custom_value=True,
            filterable=True,
        )

        # 创建按钮，当点击时生成图表
        show_button = gr.Button("历史资源占用情况")

        sys_ip.change(
            fn=clean_last_selected, inputs=item_selected, outputs=item_selected
        )

        chart = gr.Plot(label="系统资源占用")
        file_exporter = gr.components.File(label="下载文件")

        show_button.click(
            fn=update_plot,
            inputs=[sys_ip, end_delta, start_delta, item_selected],
            outputs=[
                item_selected,
                chart,
                file_exporter,
            ],
        )
        # item_selected.select(
        #     fn=update_plot,
        #     inputs=[sys_ip, end_delta, start_delta, item_selected],
        #     outputs=[
        #         item_selected,
        #         chart,
        #         file_exporter,
        #     ],
        # )

        # gr.Plot(label="当前机器资源占用", value=auto_refresh_plt, every=10)

    return app


if __name__ == "__main__":
    with open("settings.json") as f:
        settings = json.loads(f.read())
    app = setup_resource_chart()
    app.launch(
        share=True,
        inbrowser=False,
        server_name="0.0.0.0",
        server_port=9528,
        show_api=False,
        ssl_keyfile=settings["pages"]["ssl"]["key"],
        ssl_certfile=settings["pages"]["ssl"]["pem"],
        ssl_verify=False,
    )
