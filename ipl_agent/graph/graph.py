from langgraph.graph import StateGraph

from . import edges, nodes
from .state import StateInput, StateOutput, WorkflowState


def build_graph() -> StateGraph:
    builder = StateGraph(
        WorkflowState,
        input=StateInput,
        output=StateOutput,
    )

    # nodes
    builder.add_node(nodes.get_table_glimpse)
    builder.add_node(nodes.search_web)
    builder.add_node(nodes.generate_sql_query)
    builder.add_node(nodes.sql_query_executor)
    builder.add_node(nodes.rephrase_answer)

    # edges
    builder.add_conditional_edges("get_table_glimpse", edges.is_sql_query_possible)
    builder.add_edge("search_web", "rephrase_answer")
    builder.add_edge("generate_sql_query", "sql_query_executor")
    builder.add_conditional_edges("sql_query_executor", edges.is_sql_result_fine)

    # entry and finish
    builder.set_entry_point("get_table_glimpse")
    builder.set_finish_point("rephrase_answer")

    return builder


# Graph instance for langraph studio
graph = build_graph().compile()
