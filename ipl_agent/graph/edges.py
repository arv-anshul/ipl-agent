from typing import Literal

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from loguru import logger

from ipl_agent import utils
from ipl_agent.settings import settings

from ..core.prompts import IS_SQL_QUERY_POSSIBLE_TEMPLATE
from .state import WorkflowState


def is_sql_query_possible(
    state: WorkflowState,
) -> Literal["generate_sql_query", "search_web", "rephrase_answer"]:
    """
    A conditional node which check if the question can be answered using a SQL query or not.
    """
    llm = ChatOllama(model=settings.MODEL_NAME, temperature=0)
    prompt = ChatPromptTemplate.from_template(IS_SQL_QUERY_POSSIBLE_TEMPLATE)
    chain = prompt | llm | StrOutputParser() | utils.strip_reasoning_block

    response = chain.invoke(dict(state))
    logger.debug("Asked question can be answered with sql query: {}", response)

    node_mapping = {
        "SQL_QUERY": "generate_sql_query",
        "SEARCH_WEB": "search_web",
    }
    return node_mapping.get(response, "rephrase_answer")  # type: ignore


def is_sql_result_fine(
    state: WorkflowState,
) -> Literal["generate_sql_query", "rephrase_answer"]:
    """A conditional node which check if the SQL query result is fine or not."""
    # TODO: add some logic which reflect the error
    return (
        "generate_sql_query"
        if state["sql_result"].startswith("Error:")
        else "rephrase_answer"
    )
