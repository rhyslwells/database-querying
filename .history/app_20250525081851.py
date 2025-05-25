import streamlit as st
import os

st.set_page_config(page_title="SQLite Streamlit App", layout="wide")

if st.sidebar.button("Reset Application", key="reset_sidebar"):
    db_path = st.session_state.get("db_filename")

    # Try to delete the DB file (if exists)
    if db_path:
        try:
            os.remove(db_path)
        except PermissionError:
            st.warning(
                f"Could not delete {db_path} — it may still be in use. "
                "Please manually refresh the page to fully reset the app."
            )

    # Always clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Attempt to rerun
    try:
        st.rerun()
    except:
        st.warning("Please manually refresh the page to complete the reset.")


st.sidebar.title("Navigation")

page = st.sidebar.radio("Go to", ["Upload Existing DB", "Build DB from CSV"])

if page == "Upload Existing DB":
    import upload_db
    upload_db.app()
elif page == "Build DB from CSV":
    import build_db
    build_db.app()
