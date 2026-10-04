from langgraph.graph import StateGraph, END
from src.core.state import SalesState
from src.agents.data_loader import data_loader_node
from src.agents.question_classifier import question_classifier_node
from src.agents.analyst import analyst_node
from src.agents.code_executor import code_executor_node
from src.agents.self_corrector import self_corrector_node
from src.agents.reviewer import reviewer_node
from src.agents.report_writer import report_writer_node


def build_graph():
    workflow = StateGraph(SalesState)

    workflow.add_node("load_data", data_loader_node)
    workflow.add_node("classify", question_classifier_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("execute", code_executor_node)
    workflow.add_node("self_correct", self_corrector_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("report", report_writer_node)

    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "classify")
    workflow.add_edge("classify", "analyst")
    workflow.add_edge("analyst", "execute")

    def after_execute(state: SalesState) -> str:
        if state.get("exec_error") and state.get("retry_count", 0) < 3:
            return "self_correct"
        return "reviewer"

    workflow.add_conditional_edges("execute", after_execute, {
        "self_correct": "self_correct",
        "reviewer": "reviewer",
    })
    workflow.add_edge("self_correct", "execute")
    workflow.add_edge("reviewer", "report")
    workflow.add_edge("report", END)

    return workflow.compile()
