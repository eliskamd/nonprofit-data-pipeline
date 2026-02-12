"""Infer schema and produce a safe, anonymized summary for LLM context.

No PII is included in the output; only structure and anonymized samples.
"""

from pathlib import Path
from typing import Any

import pandas as pd


# Column names (case-insensitive) that suggest PII - values will be redacted in samples.
PII_PATTERNS = (
    "email", "phone", "name", "first_name", "last_name", "address",
    "city", "state", "zip", "donor_id", "narrative", "salutation",
)


def _looks_like_pii(column_name: str) -> bool:
    """Return True if the column name suggests PII (for redaction)."""
    lower = column_name.lower().strip()
    return any(p in lower for p in PII_PATTERNS)


def infer_schema(df: pd.DataFrame, sample_rows: int = 5) -> dict[str, Any]:
    """Infer schema and a safe sample from a DataFrame.

    No PII is included; string columns that look like PII are replaced
    with a placeholder in the sample.

    Args:
        df: Input DataFrame (e.g. from CSV upload).
        sample_rows: Number of rows to include in the anonymized sample (default 5).

    Returns:
        Dict with keys: columns (list of {name, dtype, non_null_count}),
        shape (rows, cols), sample (list of dicts, PII redacted).
    """
    rows, cols = df.shape
    columns = []
    for c in df.columns:
        ser = df[c]
        columns.append({
            "name": str(c),
            "dtype": str(ser.dtype),
            "non_null_count": int(ser.notna().sum()),
        })

    # Build anonymized sample: first N rows with PII-like columns redacted.
    sample_df = df.head(sample_rows)
    sample: list[dict[str, Any]] = []
    for _, row in sample_df.iterrows():
        safe_row: dict[str, Any] = {}
        for k in df.columns:
            v = row[k]
            if pd.isna(v):
                safe_row[k] = None
            elif _looks_like_pii(k) and isinstance(v, str):
                safe_row[k] = "[REDACTED]"
            elif _looks_like_pii(k) and getattr(v, "__class__", None) and "int" in str(type(v)):
                safe_row[k] = "[REDACTED]"
            else:
                safe_row[k] = v
        sample.append(safe_row)

    return {
        "columns": columns,
        "shape": {"rows": rows, "cols": cols},
        "sample": sample,
    }


def format_schema_for_prompt(schema: dict[str, Any]) -> str:
    """Format the schema dict as a string suitable for an LLM system prompt."""
    lines = [
        "## Ingested data schema",
        f"- Rows: {schema['shape']['rows']}, Columns: {schema['shape']['cols']}",
        "",
        "### Columns",
    ]
    for col in schema["columns"]:
        lines.append(f"- {col['name']}: {col['dtype']} (non-null: {col['non_null_count']})")
    lines.append("")
    lines.append("### Sample rows (PII redacted)")
    for i, row in enumerate(schema["sample"], 1):
        lines.append(f"Row {i}: {row}")
    return "\n".join(lines)
