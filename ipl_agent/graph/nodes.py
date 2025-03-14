import json

import duckdb
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from loguru import logger

from ipl_agent import utils
from ipl_agent.settings import settings

from ..core.df import load_dataframe
from ..core.prompts import (
    CONVERSATION_TEMPLATE,
    GENERATE_SQL_QUERY_TEMPLATE,
    REPHRASE_SQL_RESULT_TEMPLATE,
    REPHRASE_WEB_RESULTS_TEMPLATE,
)
from .state import WorkflowState

# load ipl matches csv as polars.DataFrame
# Now we can automatically query the dataframe using duckdb
ipl_matches = load_dataframe()
# Register ipl_matches df into duckdb
conn = duckdb.register(settings.MATCHES_TABLE_NAME, ipl_matches)


def get_table_schema(_state: WorkflowState):
    query = "SELECT column_name, column_type FROM (DESC SELECT * FROM %s LIMIT 5);"
    table_schema = conn.execute(query % settings.MATCHES_TABLE_NAME).pl()
    return {"table_schema": str(table_schema)}


def get_table_glimpse(_state: WorkflowState):
    return {"table_glimpse": str(ipl_matches.sample(5, seed=42))}


def search_web(state: WorkflowState):
    search = (
        DuckDuckGoSearchResults(
            num_results=settings.WEB_SEARCH_MAX_RESULTS,
            output_format="string",
            results_separator="\n\n",
            keys_to_include=["snippet", "link"],
        )
        | StrOutputParser()
    )
    # TODO: use settings.FETCH_FULL_CONTENT and integrate it into prompt.
    results = search.invoke(state["question"])
    logger.debug(results)

    return {
        "web_searches": results,
        "messages": [
            HumanMessage(state["question"]),
            AIMessage("Given question cannot be answer through SQL statement."),
            HumanMessage(results),
        ],
    }


def generate_sql_query(state: WorkflowState):
    llm = ChatOllama(
        model=settings.MODEL_NAME,
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_template(GENERATE_SQL_QUERY_TEMPLATE)
    chain = (
        prompt
        | llm
        | StrOutputParser()
        | utils.strip_reasoning_block
        | utils.extract_sql_code_block
    )

    sql_query = chain.invoke({**state, "table_name": settings.MATCHES_TABLE_NAME})
    return {
        "sql_query": sql_query,
        "messages": [
            HumanMessage(state["question"]),
            AIMessage("Given question can be answer through SQL statement."),
            AIMessage(sql_query),
        ],
    }


def sql_query_executor(state: WorkflowState):
    try:
        result = conn.sql(state["sql_query"]).pl()
        result = (
            str(result.item())
            if result.height == 1 and result.width == 1  # when result is scalar
            else str(result)
            if result.height <= 10  # when result is under certain rows
            else json.dumps(result.to_dicts())  # when result is more than 7 rows
        )
    except duckdb.Error as e:
        result = f"Error: {e}"

    return {"sql_result": result, "messages": [AIMessage(result)]}


def rephrase_answer(state: WorkflowState):
    llm = ChatOllama(
        model=settings.MODEL_NAME,
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_template(
        REPHRASE_SQL_RESULT_TEMPLATE
        if "sql_result" in state
        else REPHRASE_WEB_RESULTS_TEMPLATE
        if "web_searches" in state
        else CONVERSATION_TEMPLATE,
    )
    chain = prompt | llm | StrOutputParser() | utils.strip_reasoning_block

    response = chain.invoke(dict(state))
    return {"final_answer": response, "messages": [HumanMessage(response)]}
