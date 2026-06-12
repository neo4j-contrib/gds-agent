import os

DEFAULT_MAX_RESULT_ROWS = 500
DEFAULT_MAX_RESULT_CHARS = 100_000
DEFAULT_MAX_CELL_CHARS = 200

MAX_RESULT_ROWS_ENV = "GDS_AGENT_MAX_RESULT_ROWS"
MAX_RESULT_CHARS_ENV = "GDS_AGENT_MAX_RESULT_CHARS"
MAX_CELL_CHARS_ENV = "GDS_AGENT_MAX_CELL_CHARS"

SOURCE_ROW_COUNT_ATTR = "gds_agent_source_row_count"


def _env_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, default))
    except ValueError:
        return default
    return value if value > 0 else default


def max_result_rows() -> int:
    return _env_int(MAX_RESULT_ROWS_ENV, DEFAULT_MAX_RESULT_ROWS)


def max_result_chars() -> int:
    return _env_int(MAX_RESULT_CHARS_ENV, DEFAULT_MAX_RESULT_CHARS)


def max_cell_chars() -> int:
    return _env_int(MAX_CELL_CHARS_ENV, DEFAULT_MAX_CELL_CHARS)


def limit_dataframe_rows(dataframe):
    row_limit = max_result_rows()
    total_rows = len(dataframe)
    if total_rows <= row_limit:
        return dataframe

    limited = dataframe.head(row_limit).copy()
    limited.attrs[SOURCE_ROW_COUNT_ATTR] = total_rows
    return limited


def dataframe_limit_warning(dataframe) -> str | None:
    total_rows = dataframe.attrs.get(SOURCE_ROW_COUNT_ATTR)
    if total_rows is None:
        return None

    return (
        f"Warning: output truncated to the first {len(dataframe)} of {total_rows} rows "
        "to keep the MCP server responsive. For full graph-scale results, prefer running "
        "algorithms in mutate mode and inspect the projected graph with "
        "stream_node_properties, stream_relationship_properties, stream_relationships, "
        "or narrower filters."
    )


def limit_text(text: str) -> str:
    char_limit = max_result_chars()
    if len(text) <= char_limit:
        return text

    return (
        f"Warning: output truncated to {char_limit} characters to keep the MCP server "
        "responsive. Use narrower filters, mutate mode plus graph accessor tools, or "
        "request a smaller result.\n\n"
        f"{text[:char_limit]}\n\n"
        f"[truncated {len(text) - char_limit} characters]"
    )
