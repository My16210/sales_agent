from langchain_openai import ChatOpenAI

from config import settings
from src.core.state import SalesState


def reviewer_node(state: SalesState) -> dict:
    # 1.初始化Qwen模型
    llm = ChatOpenAI(**settings.get_llm_kwargs("qwen"))

    # 2. 写prompt，让Qwen审查代码
    prompt = f"""你是一个代码审查员。
    用户的问题是：{state['question']}
    数据列名有：{state['columns']}

    DeepSeek写的pandas代码是：
    {state['generated_code']}

    执行结果是：
    {state['exec_result']}

    请检查：
    1. 列名有没有写错
    2. 计算逻辑对不对
    3. 排序方向对不对

    只回答"正确"或"错误：xxx问题"。
    """

    # 3. 调模型
    response = llm.invoke(prompt)

    # 4. 返回审查结果
    return {
        "review_result": response.content,
        "review_comment": response.content
    }
