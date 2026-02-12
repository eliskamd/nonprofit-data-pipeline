"""AI assistant for data intake: load docs, build context, call LLM.

Uses OpenAI API (key from OPENAI_API_KEY). No PII is sent to the model.
"""

import os
from pathlib import Path
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv

from src.schema_inference import format_schema_for_prompt

# Project root: parent of src/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DOCS_DIR = _PROJECT_ROOT / "docs"
_INTEGRATIONS_DIR = _DOCS_DIR / "integrations"

# Load environment variables from .env if present (safe no-op if missing).
load_dotenv(_PROJECT_ROOT / ".env")


def _read_file(path: Path) -> str:
    """Read file contents; return empty string if missing or not a file."""
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def load_data_dictionary() -> str:
    """Load docs/DATA_DICTIONARY.md for LLM context."""
    return _read_file(_DOCS_DIR / "DATA_DICTIONARY.md")


def load_integration_docs() -> dict[str, str]:
    """Load all docs/integrations/*.md; return dict of filename -> content."""
    out: dict[str, str] = {}
    if not _INTEGRATIONS_DIR.is_dir():
        return out
    for p in _INTEGRATIONS_DIR.glob("*.md"):
        out[p.stem] = _read_file(p)
    return out


def build_system_context(
    schema_text: str,
    data_dictionary: str = "",
    integration_docs: dict[str, str] | None = None,
) -> str:
    """Build the system prompt context: schema + data dictionary + integration docs."""
    parts = [
        "You are a data intake assistant for a nonprofit donor data pipeline (DataBridge).",
        "You help users understand uploaded or connected data: its structure, what fields mean,",
        "and how they might map to the DataBridge schema (donors, campaigns, donations).",
        "Answer in clear, concise language. If the user's data does not match our schema,",
        "suggest mappings or transformations where possible.",
        "",
        "---",
        "",
        schema_text,
    ]
    if data_dictionary:
        parts.extend(["", "---", "", "## DataBridge data dictionary (target schema)", "", data_dictionary])
    if integration_docs:
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append("## Integration reference docs (source systems)")
        for name, content in integration_docs.items():
            if content:
                parts.append(f"### {name}")
                parts.append(content)
                parts.append("")
    return "\n".join(parts)


def get_client() -> OpenAI | None:
    """Return OpenAI client if OPENAI_API_KEY is set; else None."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    return OpenAI(api_key=key)


def explain_data(schema: dict[str, Any]) -> str:
    """One-shot: ask the LLM to explain the ingested data structure and suggest mappings.

    Returns the model's response text, or an error message if API key missing or call fails.
    """
    schema_text = format_schema_for_prompt(schema)
    data_dictionary = load_data_dictionary()
    integration_docs = load_integration_docs()
    system = build_system_context(schema_text, data_dictionary, integration_docs)

    client = get_client()
    if not client:
        return "OpenAI API key is not set. Add OPENAI_API_KEY to your environment or .env to use the assistant."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": "Summarize this dataset: what it contains, what each column likely represents, and how it could map to our DataBridge schema (donors, campaigns, donations). Be concise."},
            ],
            max_tokens=1024,
        )
        msg = response.choices[0].message
        return (msg.content or "").strip()
    except Exception as e:
        return f"Error calling the assistant: {e!s}"


def chat_with_context(
    user_message: str,
    history: list[dict[str, str]],
    schema: dict[str, Any] | None,
) -> str:
    """Send user message with full context (schema + docs) and return assistant reply.

    history: list of {"role": "user"|"assistant", "content": "..."}.
    schema: current ingested schema (or None if no data loaded). If None, context is docs only.
    """
    schema_text = format_schema_for_prompt(schema) if schema else "No dataset is currently loaded. The user may ask about the target schema or integrations."
    data_dictionary = load_data_dictionary()
    integration_docs = load_integration_docs()
    system = build_system_context(schema_text, data_dictionary, integration_docs)

    client = get_client()
    if not client:
        return "OpenAI API key is not set. Add OPENAI_API_KEY to your environment or .env to use the assistant."

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1024,
        )
        msg = response.choices[0].message
        return (msg.content or "").strip()
    except Exception as e:
        return f"Error calling the assistant: {e!s}"
