import streamlit as st
import os

st.set_page_config(page_title="SQLite Streamlit App", layout="wide")

if st.sidebar.button("Reset Application", key="reset_sidebar"):
    # Remove DB file
    db_path = st.session_state.get("db_filename")
    if db_path and os.path.exists(db_path):
        os.remove(db_path)
    # Clear all session state keys (including any connection objects)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Rerun app from clean state
    st.rerun()

st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Upload Existing DB", "Build DB from CSV"])

if page == "Upload Existing DB":
    import upload_db
    upload_db.app()
elif page == "Build DB from CSV":
    import build_db
    build_db.app()
