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

    shown = len(dataframe)
    hidden = total_rows - shown
    rows = "row" if hidden == 1 else "rows"
    return (
        f"Warning: only the first {shown:,} of {total_rows:,} rows are shown. "
        "They are in internal node ID order: not sorted by score, not a random sample. "
        f"The {hidden:,} {rows} not shown may contain the most important results. "
        "Do not rank, estimate, generalise or pick examples from these rows. "
        "For the full result, run the algorithm in mutate mode and query the property with Cypher "
        "(gds.graph.nodeProperties.stream with WHERE, ORDER BY and LIMIT)."
    )


def dataframe_limit_reminder(dataframe) -> str | None:
    total_rows = dataframe.attrs.get(SOURCE_ROW_COUNT_ATTR)
    if total_rows is None:
        return None

    hidden = total_rows - len(dataframe)
    rows = "row" if hidden == 1 else "rows"
    return f"[{hidden:,} more {rows} not shown. This list is incomplete.]"


def limit_text(text: str) -> str:
    char_limit = max_result_chars()
    if len(text) <= char_limit:
        return text

    missing = len(text) - char_limit
    percent = round(missing * 100 / len(text))
    return (
        f"Warning: this output was cut at {char_limit:,} characters. "
        f"{missing:,} characters ({percent}%) are missing, so the text below is incomplete. "
        "Do not count, list, summarise or pick examples from it as if it were the full result. "
        "For the full result, run the algorithm in mutate mode and query the result with Cypher.\n\n"
        f"{text[:char_limit]}\n\n"
        f"[truncated {missing} characters]"
    )
