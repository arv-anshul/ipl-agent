import re

import httpx
from bs4 import BeautifulSoup

_sql_markdown_re = re.compile(r"```(sql)?(.*)", re.DOTALL)


def strip_reasoning_block(text: str) -> str:
    """Strip `^<think>` block from llm response using regex, if exists."""
    cleaned_text = re.sub(r"^<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()


def extract_sql_code_block(text: str) -> str:
    """Extracts the SQL code block from llm response."""
    match_ = _sql_markdown_re.search(text)

    # If no match found, assume the entire string is a SQL string
    # Else, use the content within the backticks
    sql_str = match_.group(2) if match_ else text
    sql_str = sql_str.strip(" \n\r\t`")
    return sql_str


def fetch_full_content(url: str) -> str | None:
    """Fetches text content from given url."""
    response = httpx.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, "lxml")
    return soup.get_text(strip=True)
