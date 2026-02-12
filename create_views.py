"""
Create/refresh Postgres analytics views used by the dashboard.

Run:
  uv run python create_views.py

This reads connection settings from environment variables (optionally from .env):
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _load_env() -> None:
    load_dotenv(_project_root() / ".env")


def _build_db_config() -> dict[str, object]:
    cfg: dict[str, object] = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "donorcrm_db"),
        "user": os.getenv("DB_USER", "postgres"),
    }
    password = os.getenv("DB_PASSWORD", "").strip()
    if password:
        cfg["password"] = password
    return cfg


def main() -> int:
    _load_env()
    sql_path = _project_root() / "sql" / "views.sql"
    if not sql_path.is_file():
        print(f"Missing SQL file: {sql_path}")
        return 1

    sql_text = sql_path.read_text(encoding="utf-8")

    try:
        with psycopg2.connect(**_build_db_config()) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_text)
        print("Views created/refreshed successfully.")
        return 0
    except Exception as e:
        print(f"Error creating views: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

