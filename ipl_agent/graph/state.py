from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class StateInput(TypedDict):
    question: str


class StateOutput(TypedDict):
    final_answer: str
    sql_query: str
    sql_result: str
    web_searches: str


class WorkflowState(TypedDict):
    # TODO: Currently messages contains dummy Meassages. Need to implement it
    # or remove it completely.
    messages: Annotated[list[str], add_messages]
    question: str
    table_glimpse: str
    final_answer: str
    sql_query: str
    sql_result: str
    web_searches: str
