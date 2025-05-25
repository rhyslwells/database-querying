import streamlit as st
import datetime
import os
import pandas as pd
from db_utils import create_connection, execute_schema, insert_dataframe
from file_uploads import upload_csv_files, upload_sql_schema
from schema_utils import get_table_columns
from visualization import generate_mermaid_er
import streamlit_mermaid


def get_timestamped_db_name():
    return f"db_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def app():
    st.title("Build SQLite DB from Schema and CSV Files")

    # --- Session State Initialization ---
    if "conn" not in st.session_state:
        st.session_state.conn = None
    if "schema_executed" not in st.session_state:
        st.session_state.schema_executed = False
    if "db_filename" not in st.session_state:
        st.session_state.db_filename = None
    if "schema_sql" not in st.session_state:
        st.session_state.schema_sql = ""

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

        if st.session_state.schema_sql and not st.session_state.schema_executed:
            # Close old connection if exists
            if st.session_state.conn:
                st.session_state.conn.close()

            # Create new connection
            db_filename = get_timestamped_db_name()
            conn = create_connection(db_filename)

            if conn is None:
                st.error("Failed to create database connection.")
                return

            if execute_schema(conn, st.session_state.schema_sql):
                st.session_state.conn = conn
                st.session_state.db_filename = db_filename
                st.session_state.schema_executed = True
                st.success("Schema executed and database created.")
            else:
                st.error("Failed to execute schema.")

    else:
        st.text_area("Schema Preview (Executed)", st.session_state.schema_sql, height=150, disabled=True)

    # --- Optional ER Diagram Viewer ---
    if st.session_state.conn and st.session_state.schema_executed:
        # st.subheader("Show ER Diagram")
        if st.button("Show ER Diagram", key="show_er"):
            try:
                mermaid_code = generate_mermaid_er(st.session_state.conn)
                streamlit_mermaid.st_mermaid(mermaid_code)
            except Exception as e:
                st.error(f"Could not generate ER diagram: {e}")


    # --- Step 3: CSV Upload ---
    if st.session_state.schema_executed:
        st.header("3. Upload CSV Files to Populate Tables")
        uploaded_csvs = upload_csv_files()

        if uploaded_csvs:
            for file in uploaded_csvs:
                table_name = file.name.rsplit('.', 1)[0]
                df = pd.read_csv(file)
                st.subheader(f"Preview of `{file.name}`")
                st.dataframe(df.head())

                expected_cols = get_table_columns(st.session_state.conn, table_name)
                missing = set(expected_cols) - set(df.columns)
                extra = set(df.columns) - set(expected_cols)

                if missing:
                    st.error(f"Missing columns for table '{table_name}': {missing}")
                if extra:
                    st.warning(f"Extra columns in CSV for table '{table_name}': {extra}")

                if st.button(f"Insert data into `{table_name}`", key=f"insert_{table_name}"):
                    inserted = insert_dataframe(st.session_state.conn, table_name, df)
                    if inserted:
                        st.success(f"Inserted {len(df)} rows into {table_name}")

    # --- Step 4: Query Interface ---
    if st.session_state.conn and st.session_state.schema_executed:
        st.header("4. Query the Database")
        query = st.text_area("Enter SQL query", "SELECT name FROM sqlite_master WHERE type='table';", height=100)

        if st.button("Run Query", key="run_query_build_db"):
            try:
                df = pd.read_sql_query(query, st.session_state.conn)
                st.dataframe(df)
                st.success(f"Returned {len(df)} rows")
            except Exception as e:
                st.error(f"Query error: {e}")

    # --- Step 5: Download DB ---
    if st.session_state.db_filename:
        st.header("5. Download Database File")
        if st.button("Download current database", key="download_db_build_db"):
            if os.path.exists(st.session_state.db_filename):
                with open(st.session_state.db_filename, 'rb') as f:
                    data = f.read()
                st.download_button(
                    label="Download SQLite DB",
                    data=data,
                    file_name=os.path.basename(st.session_state.db_filename),
                    mime="application/x-sqlite3"
                )
            else:
                st.error("Database file not found.")
