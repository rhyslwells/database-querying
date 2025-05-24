import streamlit as st
import pandas as pd

def upload_sql_schema():
    uploaded_file = st.file_uploader("Upload SQL Schema file (.sql)", type=['sql'])
    if uploaded_file:
        schema_text = uploaded_file.read().decode('utf-8')
        st.text_area("Schema SQL", schema_text, height=150)
        return schema_text
    else:
        return None

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
