import streamlit as st
import os

st.set_page_config(page_title="SQLite Streamlit App", layout="wide")

st.sidebar.title("Navigation")

# Reset button in sidebar
if st.sidebar.button("Reset Application"):
    if "conn" in st.session_state and st.session_state.conn:
        st.session_state.conn.close()
    db_path = st.session_state.get("db_filename")
    if db_path and os.path.exists(db_path):
        os.remove(db_path)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

page = st.sidebar.radio("Go to", ["Upload Existing DB", "Build DB from CSV"])

if page == "Upload Existing DB":
    import upload_db
    upload_db.app()
elif page == "Build DB from CSV":
    import build_db
    build_db.app()
