import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.graph import build_graph
from src.core.state import SalesState


if __name__ == "__main__":
    app = build_graph()
    question = input("请输入你要分析的问题: ")
    print("=" * 60)

    result = app.invoke({
        "question": question,
        "columns": [],
        "data_sample": "",
        "generated_code": "",
        "exec_result": "",
        "exec_error": None,
        "retry_count": 0,
        "review_result": "",
        "review_comment": "",
        "review_round": 0,
        "need_review": True,
        "chart_path": "",
        "final_report": "",
    })

    print("\n" + "=" * 60)
    print(result["final_report"] if result["final_report"] else "（报告还没写）")
