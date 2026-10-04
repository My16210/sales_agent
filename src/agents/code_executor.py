import pandas as pd

from pathlib import Path
from src.core.state import SalesState


def code_executor_node(state: SalesState) -> dict:
    #1.再次读取csv文件
    csv_path = Path(__file__).parent.parent.parent / "data" / "raw" / "sales.csv"
    df = pd.read_csv(csv_path)

    #2.拿DeepSeek写的代码，清理markdown标记
    code = state["generated_code"]
    code = code.replace("```python", "").replace("```", "").strip()

    #3.准备执行环境
    local_vars = {"df":df}

    print(f"\n--- 执行代码 ---\n{code}\n--- 执行结束 ---\n")
    try:
        #4.执行代码
        exec(code, {}, local_vars)
        #5.从local_vars里取result
        result = local_vars.get("result","没有返回结果")
        print(f"--- 执行成功，结果: {result} ---")
        return {
            "exec_result": str(result),
            "exec_error": None
        }
    except Exception as e:
        print(f"--- 执行失败: {e} ---")
        return{"exec_result":"","exec_error":str(e)}

