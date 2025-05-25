import streamlit as st
import tempfile
import os
import datetime
import pandas as pd
from db_utils import create_connection
from visualization import generate_mermaid_er
import streamlit_mermaid

def get_timestamped_db_name():
    return f"db_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

def app():
    st.title("Upload and Query Existing SQLite Database")

    uploaded_db = st.file_uploader("Upload SQLite DB file (.db)", type=['db'])
    if uploaded_db:
        uploaded_path = os.path.join(tempfile.gettempdir(), get_timestamped_db_name())
        with open(uploaded_path, "wb") as f:
            f.write(uploaded_db.getbuffer())

        conn = create_connection(uploaded_path)
        st.success("Database loaded successfully")

        query = st.text_area("Enter SQL query", "SELECT name FROM sqlite_master WHERE type='table';", height=100)
        if st.button("Run Query", key="run_query_upload_db"):
            try:
                df = pd.read_sql_query(query, conn)
                st.dataframe(df)
                st.success(f"Returned {len(df)} rows")
            except Exception as e:
                st.error(f"Query error: {e}")

        if st.button("Show ER Diagram", key="show_er_upload_db"):
            mermaid_code = generate_mermaid_er(conn)
            streamlit_mermaid.st_mermaid(mermaid_code)

        if st.button("Download DB file", key="download_db_upload_db"):
            with open(uploaded_path, 'rb') as f:
                data = f.read()
            st.download_button("Download SQLite DB", data=data, file_name=os.path.basename(uploaded_path), mime="application/x-sqlite3")
