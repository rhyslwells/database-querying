import streamlit as st
import sqlite3
import pandas as pd
import io

st.title("Build & Query SQLite DB from CSVs and Schema")

def get_connection():
    conn = sqlite3.connect(':memory:')  # Use in-memory for fresh DB each run; change to filename for persistence
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def execute_schema(conn, schema_sql):
    cursor = conn.cursor()
    try:
        cursor.executescript(schema_sql)
        st.success("Schema executed successfully.")
    except Exception as e:
        st.error(f"Schema error: {e}")
        return False
    return True

def insert_csv_to_table(conn, csv_file, table_name):
    try:
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        st.success(f"Inserted {len(df)} rows into '{table_name}'")
    except Exception as e:
        st.error(f"Error inserting into {table_name}: {e}")

conn = get_connection()

st.header("Step 1: Upload Schema SQL")
schema_sql = st.text_area("Paste SQL schema (CREATE TABLE statements):", height=150)

if st.button("Create Database from Schema"):
    if schema_sql.strip() == "":
        st.warning("Please provide a valid SQL schema.")
    else:
        success = execute_schema(conn, schema_sql)
        if success:
            st.session_state['db_created'] = True
        else:
            st.session_state['db_created'] = False

if st.session_state.get('db_created', False):
    st.header("Step 2: Upload CSV files to populate tables")
    uploaded_files = st.file_uploader(
        "Upload CSV files (name must match table name exactly):",
        accept_multiple_files=True,
        type=['csv']
    )
    
    if uploaded_files:
        for csv_file in uploaded_files:
            # Use filename without extension as table name
            table_name = csv_file.name.rsplit('.', 1)[0]
            insert_csv_to_table(conn, csv_file, table_name)

    st.header("Step 3: Query the database")
    default_query = "SELECT name FROM sqlite_master WHERE type='table';"
    query = st.text_area("Enter your SQL query:", default_query, height=150)

    if st.button("Run Query"):
        try:
            df = pd.read_sql_query(query, conn)
            st.dataframe(df)
            st.success(f"Query executed successfully, {len(df)} rows returned.")
        except Exception as e:
            st.error(f"Error executing query: {e}")
