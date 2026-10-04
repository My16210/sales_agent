from typing import TypedDict, List, Optional


class SalesState(TypedDict):
    question: str
    columns: List[str]
    data_sample: str
    generated_code: str
    exec_result: str
    exec_error: Optional[str]
    retry_count: int
    review_result: str
    review_comment: str
    review_round: int
    need_review: bool
    chart_path: str
    final_report: str
