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

    if "uploaded_db_path" not in st.session_state:
        st.session_state.uploaded_db_path = None
    if "conn" not in st.session_state:
        st.session_state.conn = None

    uploaded_db = st.file_uploader("Upload SQLite DB file (.db)", type=['db'])
    if uploaded_db:
        # If previous uploaded file exists, close conn and remove file
        if st.session_state.conn:
            st.session_state.conn.close()
        if st.session_state.uploaded_db_path and os.path.exists(st.session_state.uploaded_db_path):
            os.remove(st.session_state.uploaded_db_path)

        # Save uploaded file to a temp file that persists during session
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_file.write(uploaded_db.getbuffer())
        temp_file.close()

        st.session_state.uploaded_db_path = temp_file.name
        st.session_state.conn = create_connection(st.session_state.uploaded_db_path)
        st.success("Database loaded successfully")

    if st.session_state.conn:
        query = st.text_area("Enter SQL query", "SELECT name FROM sqlite_master WHERE type='table';", height=100)
        if st.button("Run Query", key="run_query_upload_db"):
            try:
                df = pd.read_sql_query(query, st.session_state.conn)
                st.dataframe(df)
                st.success(f"Returned {len(df)} rows")
            except Exception as e:
                st.error(f"Query error: {e}")

        if st.button("Show ER Diagram", key="show_er_upload_db"):
            mermaid_code = generate_mermaid_er(st.session_state.conn)
            streamlit_mermaid.st_mermaid(mermaid_code)

        if st.session_state.uploaded_db_path and os.path.exists(st.session_state.uploaded_db_path):
            # Use download_button directly, no need for separate button click to read file
            with open(st.session_state.uploaded_db_path, 'rb') as f:
                data = f.read()
            st.download_button(
                label="Download SQLite DB",
                data=data,
                file_name=os.path.basename(st.session_state.uploaded_db_path),
                mime="application/x-sqlite3"
            )

    # Cleanup: You could add a callback or mechanism to delete the temp file on app close,
    # but Streamlit does not provide a direct hook.
