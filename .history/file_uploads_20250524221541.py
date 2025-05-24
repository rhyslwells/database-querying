import streamlit as st
import pandas as pd

def upload_csv_files():
    uploaded_files = st.file_uploader("Upload CSV files", type=['csv'], accept_multiple_files=True)
    return uploaded_files

def upload_sqlite_db():
    uploaded_db = st.file_uploader("Upload SQLite DB file (.db)", type=['db'])
    if uploaded_db:
        with open('uploaded_database.db', 'wb') as f:
            f.write(uploaded_db.read())
        return 'uploaded_database.db'
    else:
        return None
