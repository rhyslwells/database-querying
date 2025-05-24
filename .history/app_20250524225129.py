import streamlit as st
import sqlite3
import os
import pandas as pd
import datetime

from db_utils import create_connection, execute_schema, insert_dataframe
from file_uploads import upload_csv_files, upload_sqlite_db, upload_sql_schema
from schema_utils import generate_schema_from_csv, get_table_columns
from visualization import render_er_diagram

st.set_page_config(page_title="SQLite Streamlit App", layout="wide")

def get_timestamped_db_name():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"db_{timestamp}.db"

# Initialize session state variables
if "conn" not in st.session_state:
    st.session_state.conn = None
if "schema_executed" not in st.session_state:
    st.session_state.schema_executed = False
if "db_filename" not in st.session_state:
    st.session_state.db_filename = None

st.title("SQLite Database Builder and Query Interface")

# Step 1: Upload or generate schema
st.header("1. Provide Schema (Upload .sql or Type It)")

uploaded_db = upload_sqlite_db()
if uploaded_db:
    # Close previous connection if any
    if st.session_state.conn:
        st.session_state.conn.close()
    uploaded_path = 'uploaded_database.db'
    with open(uploaded_path, 'wb') as f:
        f.write(uploaded_db.getbuffer())
    st.session_state.conn = create_connection(uploaded_path)
    st.session_state.db_filename = uploaded_path
    st.session_state.schema_executed = True
    st.success("Database loaded from uploaded .db file")

elif st.session_state.conn is None or not st.session_state.schema_executed:
    schema_input_mode = st.radio("Choose how to provide your schema:", ["Upload SQL file", "Type SQL schema"])
    schema_sql = None

    if schema_input_mode == "Upload SQL file":
        schema_sql = upload_sql_schema()
        if schema_sql:
            st.text_area("Schema Preview", schema_sql, height=150)
    elif schema_input_mode == "Type SQL schema":
        schema_sql = st.text_area("Enter your SQL schema here:", height=200)

    if schema_sql and not st.session_state.schema_executed:
        # Close previous connection if exists
        if st.session_state.conn:
            st.session_state.conn.close()
        # Generate timestamped DB filename
        db_filename = get_timestamped_db_name()
        conn = create_connection(db_filename)
        if execute_schema(conn, schema_sql):
            st.session_state.conn = conn
            st.session_state.db_filename = db_filename
            st.session_state.schema_executed = True
            st.success("Schema executed and database created")
        else:
            st.error("Failed to execute schema.")

# Step 2: Upload CSV files to populate tables
if st.session_state.conn and st.session_state.schema_executed:
    st.header("2. Upload CSV Files")
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

            if st.button(f"Insert data into `{table_name}`"):
                inserted = insert_dataframe(st.session_state.conn, table_name, df)
                if inserted:
                    st.success(f"Inserted {len(df)} rows into {table_name}")

# Step 3: Query interface
if st.session_state.conn and st.session_state.schema_executed:
    st.header("3. Query the Database")
    query = st.text_area("Enter SQL query", "SELECT name FROM sqlite_master WHERE type='table';", height=100)

    if st.button("Run Query"):
        try:
            df = pd.read_sql_query(query, st.session_state.conn)
            st.dataframe(df)
            st.success(f"Returned {len(df)} rows")
        except Exception as e:
            st.error(f"Query error: {e}")

# Step 4: Download DB file
if st.session_state.db_filename:
    st.header("4. Download Database")
    if st.button("Download current database"):
        if os.path.exists(st.session_state.db_filename):
            with open(st.session_state.db_filename, 'rb') as f:
                data = f.read()
            st.download_button(label="Download SQLite DB", data=data, file_name=st.session_state.db_filename, mime="application/x-sqlite3")
        else:
            st.error("Database file not found.")

# Step 5: ER Diagram with a button toggle
if st.session_state.db_filename:
    st.header("5. ER Diagram")

    if "show_er_diagram" not in st.session_state:
        st.session_state.show_er_diagram = False

    if st.button("Show ER Diagram"):
        st.session_state.show_er_diagram = True

    if st.session_state.show_er_diagram:
        er_image = render_er_diagram(st.session_state.db_filename)
        if er_image:
            st.image(er_image, caption="ER Diagram")
        else:
            st.error("Failed to generate ER diagram.")


# Step 6: Reset app
if st.button("Reset Application"):
    # Close DB connection
    if st.session_state.conn:
        st.session_state.conn.close()
    # Delete DB file
    db_path = st.session_state.db_filename
    if db_path and os.path.exists(db_path):
        os.remove(db_path)
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
