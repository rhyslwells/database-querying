import streamlit as st
import sqlite3
import datetime
import pandas as pd
from visualization import generate_mermaid_er
import streamlit_mermaid

def get_timestamped_db_name():
    return f"db_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def app():
    st.title("Upload and Query SQLite DB in Memory")

    # Initialize in-memory connection once per session
    if "conn" not in st.session_state:
        st.session_state.conn = None

    uploaded_db = st.file_uploader("Upload SQLite DB file (.db)", type=['db'])
    if uploaded_db:
        # Load uploaded DB into memory
        uploaded_bytes = uploaded_db.read()

        # Create in-memory DB
        mem_conn = sqlite3.connect(':memory:')
        # Load uploaded DB into this in-memory DB
        disk_conn = sqlite3.connect(':memory:')
        # Actually, better: open temporary disk DB and then copy to memory

        # We'll do a workaround by creating a temp disk DB, then copying to memory
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
            tmp_file.write(uploaded_bytes)
            tmp_filename = tmp_file.name

        disk_conn = sqlite3.connect(tmp_filename)
        mem_conn = sqlite3.connect(':memory:')

        # Backup disk DB into memory DB
        disk_conn.backup(mem_conn)
        disk_conn.close()
        os.remove(tmp_filename)

        st.session_state.conn = mem_conn
        st.success("Database loaded into memory successfully")

    if st.session_state.conn:
        query = st.text_area("Enter SQL query", "SELECT name FROM sqlite_master WHERE type='table';", height=100)
        if st.button("Run Query", key="run_query"):
            try:
                df = pd.read_sql_query(query, st.session_state.conn)
                st.dataframe(df)
                st.success(f"Returned {len(df)} rows")
            except Exception as e:
                st.error(f"Query error: {e}")

        if st.button("Show ER Diagram", key="show_er"):
            mermaid_code = generate_mermaid_er(st.session_state.conn)
            streamlit_mermaid.st_mermaid(mermaid_code)

        if st.button("Download Database", key="download_db"):
            # Save in-memory DB to a file with timestamped name
            filename = get_timestamped_db_name()
            disk_conn = sqlite3.connect(filename)
            st.session_state.conn.backup(disk_conn)
            disk_conn.close()

            with open(filename, "rb") as f:
                data = f.read()
            st.download_button("Download SQLite DB", data=data, file_name=filename, mime="application/x-sqlite3")

            # Optional: Delete the file after download button click, or leave it to user
            os.remove(filename)
