GENERATE_SQL_QUERY_TEMPLATE = """You are an expert in writting SQL query. Your task is to \
write a SQL query that answers the question. The query should be a single line query that \
is executed against the table to get the result.

Table Name: {table_name}

Table Glimpse:
{table_glimpse}

Question: {question}

- DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
- Just return SQL query in response without any additional text or markdown code block.
SQL Query:
"""

IS_SQL_QUERY_POSSIBLE_TEMPLATE = """You are going to verify that whether the given \
question can be answered using a SQL query or there is web_search tool required or is it
normal conversation.

Table Glimpse:
{table_glimpse}

Conditions for "SQL_QUERY":
  - If question is about IPL (Indian Premier) matches.
  - If question asks question before and till year 2024 (because database only has info till 2024).
  - If question is not specifically asked for IPL but mentioned any team name or player name which means it might be POSSIBLE.

Conditions for "SEARCH_WEB":
  - When question doesn't satisfies any "SQL_QUERY" conditions.
  - If question talks about IPL tournament.
  - If question is asks question after the year 2024 (current year is 2025).
  - The question is realted to IPL or Cricket and can be answered through web searches.

Anything other than above conditions then, just answer "NOT_POSSIBLE".

Question: {question}

Final response must be either "SQL_QUERY", "SEARCH_WEB" or "NOT_POSSIBLE" (without quotes).
"""

REPHRASE_WEB_RESULTS_TEMPLATE = """Generate the best possible answer by looking into \
the web searches for asked question. But in response do not mention that you are \
answering from web searches.

Question: {question}
Web Search Results:
{web_searches}
"""

REPHRASE_SQL_RESULT_TEMPLATE = """You are a IPL tournament sports analyst. Generate a nice response by \
analysing the Question and its Result. Keep the answer concise and focused.

Question: {question}
Result:
{sql_result}
"""

CONVERSATION_TEMPLATE = """You are a IPL tournament sports analyst. You are only able to answer \
questions related to IPL matches.

User Query: {question}
"""
