"""Streamlit UI for the DataBridge data intake assistant.

Run with: uv run streamlit run streamlit_app.py
Then open http://localhost:8501 in your browser.
"""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

from src.ai_assistant import chat_with_context, explain_data
from src.schema_inference import infer_schema

load_dotenv()

st.set_page_config(
    page_title="DataBridge – Data Intake Assistant",
    page_icon="📊",
    layout="wide",
)


def _build_db_config() -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "donorcrm_db"),
        "user": os.getenv("DB_USER", "postgres"),
    }
    password = os.getenv("DB_PASSWORD", "").strip()
    if password:
        cfg["password"] = password
    return cfg


def _has_db_config() -> bool:
    return bool(os.getenv("DB_HOST") or os.getenv("DB_NAME") or os.getenv("DB_USER") or os.getenv("DB_PASSWORD"))


@st.cache_data(ttl=60)
def _query_df(sql: str) -> pd.DataFrame:
    """Run a SQL query and return a DataFrame (cached)."""
    with psycopg2.connect(**_build_db_config()) as conn:
        return pd.read_sql_query(sql, conn)


def render_dashboard() -> None:
    st.title("DataBridge – Dashboard (Mock Data)")
    st.caption("Reads from Postgres views: vw_monthly_giving, vw_campaign_performance, vw_donor_ltv.")

    if not _has_db_config():
        st.warning(
            "Database environment variables are not set. Create a `.env` from `.env.example` and fill in DB_* values."
        )
        return

    try:
        monthly = _query_df("SELECT * FROM vw_monthly_giving;")
        campaigns = _query_df("SELECT * FROM vw_campaign_performance;")
        top_donors = _query_df(
            """
            SELECT *
            FROM vw_donor_ltv
            WHERE donation_count > 0
            ORDER BY total_given DESC
            LIMIT 25;
            """
        )
    except Exception as e:
        st.error(f"Could not query the database/views: {e!s}")
        st.info("Tip: run `uv run python create_views.py` after loading data.")
        return

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total raised", f"${monthly['total_amount'].sum():,.2f}")
    with kpi2:
        st.metric("Donations", f"{int(monthly['donation_count'].sum()):,}")
    with kpi3:
        st.metric("Unique donors (monthly sum)", f"{int(monthly['unique_donors'].sum()):,}")
    with kpi4:
        st.metric("Avg donation (overall)", f"${(monthly['total_amount'].sum() / max(monthly['donation_count'].sum(), 1)) :,.2f}")

    st.subheader("Monthly giving trend")
    st.line_chart(monthly.set_index("month")["total_amount"])

    st.divider()
    tab1, tab2 = st.tabs(["Campaigns", "Top donors"])

    with tab1:
        st.subheader("Campaign performance")
        st.dataframe(
            campaigns[[
                "campaign_name",
                "campaign_type",
                "goal_amount",
                "total_raised",
                "raised_minus_goal",
                "donation_count",
                "unique_donors",
            ]],
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        st.subheader("Top donors by total given")
        st.dataframe(
            top_donors[[
                "donor_id",
                "first_name",
                "last_name",
                "donation_count",
                "total_given",
                "first_gift_date",
                "last_gift_date",
            ]],
            use_container_width=True,
            hide_index=True,
        )


def render_intake_assistant() -> None:
    # Session state: current schema (from last upload), chat history
    if "schema" not in st.session_state:
        st.session_state.schema = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "explanation" not in st.session_state:
        st.session_state.explanation = None

    st.title("DataBridge – Data Intake Assistant")
    st.caption("Upload a CSV to understand its structure and map it to our donor schema. Ask questions in context.")

    # --- File upload ---
    uploaded_file = st.file_uploader(
        "Upload a CSV", type=["csv"], help="Upload donor or gift data to inspect and discuss."
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.schema = infer_schema(df)
            st.session_state.explanation = None  # Reset so user can request a fresh explanation
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
            st.session_state.schema = None

    # --- Current data summary ---
    if st.session_state.schema:
        s = st.session_state.schema
        st.subheader("Current dataset")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", s["shape"]["rows"])
        with col2:
            st.metric("Columns", s["shape"]["cols"])
        with col3:
            st.metric("Sample rows (for AI)", len(s["sample"]))

        with st.expander("Column summary", expanded=True):
            summary = pd.DataFrame([
                {"Column": c["name"], "Type": c["dtype"], "Non-null": c["non_null_count"]}
                for c in s["columns"]
            ])
            st.dataframe(summary, use_container_width=True, hide_index=True)

        with st.expander("Sample rows (PII redacted for AI context)"):
            st.dataframe(pd.DataFrame(s["sample"]), use_container_width=True, hide_index=True)

        # --- Explain this data ---
        st.subheader("Explain this data")
        if st.button("Get AI explanation", type="primary"):
            with st.spinner("Asking the assistant..."):
                st.session_state.explanation = explain_data(st.session_state.schema)
        if st.session_state.explanation:
            st.markdown(st.session_state.explanation)
    else:
        st.info(
            "Upload a CSV above to see its schema and get an AI explanation. You can still ask about our target schema or integrations in the chat below."
        )

    # --- Chat with context ---
    st.divider()
    st.subheader("Chat with context")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about this data, mappings to DataBridge, or our integration docs...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat_with_context(
                    prompt,
                    st.session_state.chat_history[:-1],
                    st.session_state.schema,
                )
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()


# --- Navigation ---
st.sidebar.title("DataBridge")
page = st.sidebar.radio("Go to", ["Dashboard", "Data intake assistant"], index=0)

if page == "Dashboard":
    render_dashboard()
else:
    render_intake_assistant()
