import streamlit as st

def app():
    st.title("Welcome to the SQLite Streamlit App")

    st.markdown("""
    This app allows you to interact with SQLite databases efficiently:

    - **Upload Existing DB**: Upload a `.db` SQLite file, query it in-memory, visualize its schema, and download it back.
    - **Build DB from CSV**: Upload CSV files and an SQL schema to create an in-memory SQLite database, query and manipulate data without saving permanently.
    
    Use the sidebar navigation to get started.
    """)
