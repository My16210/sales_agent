import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from langchain_openai import ChatOpenAI
from config.settings import settings
from src.core.state import SalesState


def report_writer_node(state: SalesState) -> dict:
    # 1. 画图：各地区销售额柱状图
    csv_path = Path(__file__).parent.parent.parent / "data" / "raw" / "sales.csv"
    df = pd.read_csv(csv_path)
    region_sales = df.groupby("地区")["金额"].sum().sort_values(ascending=False)

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(8, 5))
    region_sales.plot(kind="bar", ax=ax, color="#4472C4")
    ax.set_title("各地区销售额")
    ax.set_xlabel("地区")
    ax.set_ylabel("销售额（元）")
    plt.xticks(rotation=0)

    output_dir = Path(__file__).parent.parent.parent / "data" / "output"
    output_dir.mkdir(exist_ok=True)
    chart_path = output_dir / "chart.png"
    plt.tight_layout()
    plt.savefig(chart_path, dpi=100)
    plt.close()

    # 2. 调DeepSeek写报告
    llm = ChatOpenAI(**settings.get_llm_kwargs("deepseek"))
    prompt = f"""用户问的是：{state['question']}
数据分析结果是：{state['exec_result']}
本次分析共消耗{state.get('total_tokens', 0)}个token。

请把这个结果写成一段简洁的中文结论，不要超过3句话，最后提一下本次token消耗。
"""
    response = llm.invoke(prompt)

    # 3. 返回报告 + 图片路径 + 更新对话历史
    return {
        "final_report": response.content,
        "chart_path": str(chart_path),
        "messages": state.get("messages", []) + [
            {"role": "用户", "content": state["question"]},
            {"role": "助手", "content": response.content}
        ]
    }
