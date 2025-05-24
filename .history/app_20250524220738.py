import streamlit as st
import sqlite3
from db_utils import create_connection, execute_schema, insert_dataframe
from file_uploads import upload_sql_schema, upload_csv_files, upload_sqlite_db
from schema_utils import generate_schema_from_csv, get_table_columns
from visualization import render_er_diagram
import os
import pandas as pd

st.set_page_config(page_title="SQLite Streamlit App", layout="wide")

# Session state for DB connection
if "conn" not in st.session_state:
    st.session_state.conn = None

st.title("SQLite Database Builder and Query Interface")

# Step 1: Upload or generate schema
st.header("1. Upload or Generate Schema")

uploaded_db = upload_sqlite_db()
if uploaded_db:
    st.success("Database loaded from uploaded .db file")
    st.session_state.conn = create_connection('uploaded_database.db')

elif st.session_state.conn is None:
    schema_sql = upload_sql_schema()
    if schema_sql:
        conn = create_connection('my_database.db')
        if execute_schema(conn, schema_sql):
            st.success("Schema executed and database created")
            st.session_state.conn = conn

# Step 2: Upload CSV files to populate tables or generate schema
if st.session_state.conn:
    st.header("2. Upload CSV Files")
    uploaded_csvs = upload_csv_files()

    if uploaded_csvs:
        for file in uploaded_csvs:
            table_name = file.name.rsplit('.', 1)[0]
            df = file.read()
            df = pd.read_csv(file)
            # Preview
            st.subheader(f"Preview of `{file.name}`")
            st.dataframe(df.head())

            # Validate columns
            expected_cols = get_table_columns(st.session_state.conn, table_name)
            missing = set(expected_cols) - set(df.columns)
            extra = set(df.columns) - set(expected_cols)

            if missing:
                st.error(f"Missing columns for table '{table_name}': {missing}")
            if extra:
                st.warning(f"Extra columns in CSV for table '{table_name}': {extra}")

            # Insert data button
            if st.button(f"Insert data into `{table_name}`"):
                inserted = insert_dataframe(st.session_state.conn, table_name, df)
                if inserted:
                    st.success(f"Inserted {len(df)} rows into {table_name}")

    # Step 3: Query interface
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
    st.header("4. Download Database")
    if st.button("Download current database"):
        with open('my_database.db', 'rb') as f:
            data = f.read()
        st.download_button(label="Download SQLite DB", data=data, file_name="my_database.db", mime="application/x-sqlite3")

    # Step 5: ER Diagram
    st.header("5. ER Diagram")
    er_image = render_er_diagram('my_database.db')
    if er_image:
        st.image(er_image, caption="ER Diagram")

    # Step 6: Reset app
    if st.button("Reset Application"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()
