from langchain_openai import ChatOpenAI
from config.settings import settings
from src.core.state import SalesState


def self_corrector_node(state: SalesState) -> dict:
    # 1. 初始化DeepSeek
    llm = ChatOpenAI(**settings.get_llm_kwargs("deepseek"))

    # 2. 写纠错prompt
    prompt = f"""你之前写的pandas代码报错了。
    用户问题：{state['question']}
    数据列名：{state['columns']}
    你之前写的代码：
    {state['generated_code']}

    错误信息：{state['exec_error']}

    请修正代码，只输出修正后的pandas代码，结果存在result变量里。"""

    # 3. 调模型
    response = llm.invoke(prompt)

    # 4. 返回新代码 + 重试次数+1 + 清除错误
    return {
        "generated_code": response.content,
        "retry_count": state.get("retry_count", 0) + 1,
        "exec_error": None
    }
