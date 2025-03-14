import polars as pl
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Modify str output of polars.Dataframe for LLM prompts
(
    pl.Config.set_tbl_formatting("MARKDOWN")
    .set_tbl_cols(10)  # limit to 10 cols
    .set_tbl_hide_dataframe_shape()
    .set_tbl_hide_column_data_types()
    .set_fmt_str_lengths(60)
)


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        env_file_encoding="utf-8",
    )

    MODEL_NAME: str = Field(
        min_length=1,
        description="Default model fallback name.",
    )
    IPL_MATCHES_DATA_URL: HttpUrl = Field(
        description="URL to fetch IPL matches data.",
    )
    MATCHES_TABLE_NAME: str = Field(
        description="Table name to register the dataframe with duckdb and query.",
    )
    WEB_SEARCH_MAX_RESULTS: int = Field(
        ge=3,
        le=10,
        description="Number of results fetch from search tool.",
    )
    FETCH_FULL_CONTENT: bool = Field(
        description="Whether to fetch full content from searched url.",
    )


settings = _Settings()  # type: ignore[reportCallIssue]
