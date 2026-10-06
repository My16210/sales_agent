from langchain_openai import ChatOpenAI
from config.settings import settings
from src.core.state import SalesState
from src.utils.logger import setup_logger
logger = setup_logger()


def analyst_node(state: SalesState) -> dict:
    logger.info(f"开始分析: {state['question']}")
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
    logger.info("DeepSeek生成代码成功")
    return {"generated_code": response.content}
