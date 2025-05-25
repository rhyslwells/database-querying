import streamlit as st
import sqlite3
import datetime
import os
import tempfile
import pandas as pd

from utils.db_utils import execute_schema, insert_dataframe
from utils.file_uploads import upload_csv_files, upload_sql_schema
from utils.schema_utils import get_table_columns
from utils.visualization import generate_mermaid_er


import streamlit_mermaid


def get_timestamped_db_name():
    return f"db_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"


def load_memory_connection(db_bytes: bytes) -> sqlite3.Connection:
    """Create a fresh in-memory SQLite connection from raw bytes."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
        tmp_file.write(db_bytes)
        tmp_path = tmp_file.name

    disk_conn = sqlite3.connect(tmp_path)
    mem_conn = sqlite3.connect(":memory:")
    disk_conn.backup(mem_conn)
    disk_conn.close()
    os.remove(tmp_path)
    return mem_conn


def app():
    st.title("Build In-Memory SQLite DB from Schema and CSV Files")

    if "schema_executed" not in st.session_state:
        st.session_state.schema_executed = False
    if "schema_sql" not in st.session_state:
        st.session_state.schema_sql = ""
    if "db_bytes" not in st.session_state:
        st.session_state.db_bytes = None

    # --- Step 1: Schema Input ---
    st.header("1. Provide Schema (Upload .sql or Type It)")
    if not st.session_state.schema_executed:
        schema_input_mode = st.radio("Choose how to provide your schema:", ["Upload SQL file", "Type SQL schema"])

        if schema_input_mode == "Upload SQL file":
            uploaded_sql = upload_sql_schema()
            if uploaded_sql:
                st.session_state.schema_sql = uploaded_sql
        elif schema_input_mode == "Type SQL schema":
            st.session_state.schema_sql = st.text_area(
                "Enter your SQL schema here:",
                st.session_state.schema_sql,
                height=200
            )

        if st.session_state.schema_sql:
            st.text_area("Schema Preview", st.session_state.schema_sql, height=150, disabled=True)

        if st.session_state.schema_sql:
            conn = sqlite3.connect(":memory:")
            if execute_schema(conn, st.session_state.schema_sql):
                # Save DB bytes
                with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
                    tmp_path = tmp_file.name
                disk_conn = sqlite3.connect(tmp_path)
                conn.backup(disk_conn)
                disk_conn.close()
                with open(tmp_path, "rb") as f:
                    st.session_state.db_bytes = f.read()
                os.remove(tmp_path)

                st.session_state.schema_executed = True
                st.success("Schema executed and in-memory database created.")
            else:
                st.error("Failed to execute schema.")
            conn.close()
    else:
        st.text_area("Schema Preview (Executed)", st.session_state.schema_sql, height=150, disabled=True)

    # ---  ER Diagram Viewer ---
    if st.session_state.schema_executed and st.session_state.db_bytes:
        if st.button("Show ER Diagram", key="show_er"):
            try:
                conn = load_memory_connection(st.session_state.db_bytes)
                mermaid_code = generate_mermaid_er(conn)
                conn.close()
                streamlit_mermaid.st_mermaid(mermaid_code)
            except Exception as e:
                st.error(f"Could not generate ER diagram: {e}")

    # --- Step 2: CSV Upload ---
    if st.session_state.schema_executed and st.session_state.db_bytes:
        st.header("2. Upload CSV Files to Populate Tables")
        uploaded_csvs = upload_csv_files()

        if uploaded_csvs:
            for file in uploaded_csvs:
                table_name = file.name.rsplit('.', 1)[0]
                df = pd.read_csv(file)
                st.subheader(f"Preview of `{file.name}`")
                st.dataframe(df.head())

                conn = load_memory_connection(st.session_state.db_bytes)
                expected_cols = get_table_columns(conn, table_name)
                conn.close()

                missing = set(expected_cols) - set(df.columns)
                extra = set(df.columns) - set(expected_cols)

                if missing:
                    st.error(f"Missing columns for table '{table_name}': {missing}")
                if extra:
                    st.warning(f"Extra columns in CSV for table '{table_name}': {extra}")

                if st.button(f"Insert data into `{table_name}`", key=f"insert_{table_name}"):
                    conn = load_memory_connection(st.session_state.db_bytes)
                    success = insert_dataframe(conn, table_name, df)

                    if success:
                        # Save updated DB
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
                            tmp_path = tmp_file.name
                        disk_conn = sqlite3.connect(tmp_path)
                        conn.backup(disk_conn)
                        disk_conn.close()
                        with open(tmp_path, "rb") as f:
                            st.session_state.db_bytes = f.read()
                        os.remove(tmp_path)
                        st.success(f"Inserted {len(df)} rows into {table_name}")
                    else:
                        st.error(f"Failed to insert data into {table_name}")
                    conn.close()

    # --- Step 3: Query Interface ---
    if st.session_state.schema_executed and st.session_state.db_bytes:
        st.header("3. Query the Database")
        query = st.text_area("Enter SQL query", "SELECT name FROM sqlite_master WHERE type='table';", height=100)

        if st.button("Run Query", key="run_query_build_db"):
            try:
                conn = load_memory_connection(st.session_state.db_bytes)
                df = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(df)
                st.success(f"Returned {len(df)} rows")
            except Exception as e:
                st.error(f"Query error: {e}")

    # --- Step 4: Download DB ---
    if st.session_state.db_bytes:
        st.header("4. Download In-Memory Database")
        if st.button("Download current database", key="download_db_build_db"):
            st.download_button(
                label="Download SQLite DB",
                data=st.session_state.db_bytes,
                file_name=get_timestamped_db_name(),
                mime="application/x-sqlite3"
            )
