from langchain_openai import ChatOpenAI
from config.settings import settings
from src.core.state import SalesState


def analyst_node(state: SalesState) -> dict:
    # 1.初始化DeepSeek模型
    llm = ChatOpenAI(**settings.get_llm_kwargs("deepseek"))

    #2。写prompt,告诉模型数据有哪些列、用户问什么
    prompt = f"""你是一个数据分析助手。
    这是一个销售数据表，列名有：{state['columns']}
    前5行数据：{state['data_sample']}

    用户的问题是：{state['question']}

    请写一段pandas代码来回答这个问题。
    要求：用df表示数据，结果存在result变量里。只输出代码。"""

    # 3. 调模型
    response = llm.invoke(prompt)

    # 4. 返回代码
    print(f"\n--- DeepSeek写的代码 ---\n{response.content}\n--- 代码结束 ---\n")
    return {"generated_code": response.content}


