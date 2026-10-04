from src.core.state import SalesState


def question_classifier_node(state: SalesState) -> dict:
    question = state["question"]

    # 复杂问题的关键词
    complex_keywords = ["Top","排名","趋势","哪个最好"]

    # 检查问题里有没有这些词
    need_review = False
    for keyword in complex_keywords:
        if keyword in question:
            need_review = True
            break

    return {"need_review": need_review}