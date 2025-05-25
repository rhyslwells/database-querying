import streamlit as st

st.set_page_config(page_title="SQLite Streamlit App", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload Existing DB", "Build DB from CSV"])

if page == "Upload Existing DB":
    import upload_db
    upload_db.app()
elif page == "Build DB from CSV":
    import build_db
    build_db.app()
